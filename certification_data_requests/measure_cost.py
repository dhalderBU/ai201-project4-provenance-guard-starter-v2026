#!/usr/bin/env python3
"""Measure ten warm assessments and ten certificate verifications in isolation.

CPU cost comes from the application's operational log, not wall time or pricing.
The fixed long-text fixture exercises both models. Setup and warm-up are excluded.
"""
import argparse
from collections import defaultdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import statistics
import uuid

import run_tests as runner


def percentile(values, fraction):
    ordered = sorted(values)
    position = (len(ordered) - 1) * fraction
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (position - lower)


def operational_records(sandbox):
    return json.loads(sandbox.execute(
        'import config,json; from pathlib import Path; '
        'p=config.LOG_DIR/config.OPERATIONAL_LOG_FILENAME; '
        'print(json.dumps([json.loads(line) for line in p.read_text().splitlines() if line.strip()]))'))


def summarize(rows):
    if len(rows) != 10 or not all(r['cpu_measurement_complete'] for r in rows):
        raise RuntimeError('A cost average requires ten complete CPU measurements.')
    cpu = [r['cpu_seconds'] for r in rows]
    server = [r['duration_seconds'] for r in rows]
    client = [r['client_duration_seconds'] for r in rows]
    if not all(isinstance(value, (int, float)) and value >= 0 for value in cpu):
        raise RuntimeError('Missing or invalid CPU measurements.')
    models = defaultdict(lambda: {'calls': 0, 'input_tokens': 0, 'output_tokens': 0})
    for row in rows:
        for model, values in row['models'].items():
            for key in models[model]:
                models[model][key] += values[key]
    return {'runs': 10, 'total_cpu_seconds': sum(cpu), 'mean_cpu_seconds': statistics.mean(cpu),
            'mean_server_seconds': statistics.mean(server), 'p50_server_seconds': percentile(server, .5),
            'p95_server_seconds': percentile(server, .95), 'mean_client_seconds': statistics.mean(client),
            'cpu_seconds_for_100_requests': statistics.mean(cpu) * 100,
            'models_total': dict(models)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--image', default='provenance-guard:local')
    parser.add_argument('--model-cache', required=True, help='Existing cached-model Docker volume; mounted read-only.')
    args = parser.parse_args()
    runner.docker('volume', 'inspect', args.model_cache)
    image = json.loads(runner.docker('image', 'inspect', args.image))[0]['Id']
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    output = runner.PACK / 'results' / f'cost_{stamp}_{uuid.uuid4().hex[:6]}'
    output.mkdir(parents=True)
    fixture = next(f for f in runner.read(runner.PACK / 'fixtures.json') if f['id'] == 'long_text')
    payload = runner.read(runner.PACK / fixture['submit_file'])
    runner.save(output / 'fixture.json', payload)
    shutil.copyfile(__file__, output / 'measurement_script.py')
    metadata = {'started_at_utc': runner.now(), 'image_id': image, 'fixture': fixture,
                'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                'warm_definition': 'Models loaded; one assessment and certificate approval completed before measurement.',
                'cost_metric': 'Operational cpu_time_seconds: handler thread CPU plus inference child-process CPU.',
                'excluded': ['model download/startup', 'warm-up', 'approval setup', 'human review effort',
                             'rate-limit waiting between calls', 'idle CPU', 'network transfer', 'storage and electricity cost'],
                'request_policy': 'Ten sequential requests per workload, unchanged application defaults, no retries.'}
    runner.save(output / 'metadata.json', metadata)
    sandbox = runner.Sandbox(image, args.model_cache, True, output / 'session', 120)
    runner.docker('volume', 'create', sandbox.volume)
    measurements = []
    print(f'Cost evidence: {output.relative_to(runner.ROOT)}', flush=True)
    try:
        sandbox.start()
        metadata['health'] = sandbox.history[-1]['ready_health']
        metadata['runtime'] = json.loads(sandbox.execute(
            'import platform,os,json,torch; print(json.dumps({"python":platform.python_version(),'
            '"architecture":platform.machine(),"visible_cpus":os.cpu_count(),'
            '"torch_threads":torch.get_num_threads()}))'))
        metadata['application_sha256'] = json.loads(sandbox.execute(
            'import pathlib,hashlib,json; print(json.dumps({n:hashlib.sha256(pathlib.Path(n).read_bytes()).hexdigest() '
            'for n in ["app.py","config.py","operations.py","inference_runtime.py","verification.py"]}))'))
        runner.save(output / 'metadata.json', metadata)
        approved = runner.certify(sandbox, fixture, 'excluded_warmup')
        cursor = len(operational_records(sandbox))

        def measured_request(workload, index, endpoint, request, expected_status):
            nonlocal cursor
            result = sandbox.request(endpoint, request, f'{workload}_{index:02}')
            response = runner.require(result, expected_status)
            all_records = operational_records(sandbox)
            new = [r for r in all_records[cursor:]
                   if r['event'] == 'request_completed' and r['path'] == endpoint]
            cursor = len(all_records)
            if len(new) != 1:
                raise RuntimeError('Could not identify one operational completion for the measured request.')
            event = new[0]
            row = {'timestamp': event['received_at'], 'workload': workload, 'run': index,
                   'request_id': event['request_id'], 'endpoint': endpoint,
                   'input': {'request_file': result['request_file'],
                             'text_sha256': hashlib.sha256(request['text'].encode('utf-8')).hexdigest()},
                   'output': response, 'http_status': event['http_status'],
                   'duration_seconds': event['duration_seconds'],
                   'client_duration_seconds': result['duration_seconds'],
                   'cpu_seconds': event['cpu_time_seconds'],
                   'cpu_measurement_complete': event['cpu_measurement_complete'], 'models': event['models']}
            if event['http_status'] != expected_status:
                raise RuntimeError('Operational status does not match HTTP status.')
            with (output / 'measurements.jsonl').open('a', encoding='utf-8') as handle:
                handle.write(json.dumps(row, ensure_ascii=False) + '\n')
            # Compact structured run record: full inputs/responses are retained
            # at the linked request file and in measurements.jsonl, respectively.
            compact = {'timestamp': row['timestamp'], 'run': index, 'endpoint': endpoint,
                       'input': row['input'],
                       'output': {k: response[k] for k in ('content_id', 'label', 'verified', 'error') if k in response},
                       'http_status': expected_status, 'duration_seconds': row['duration_seconds'],
                       'cpu_seconds': row['cpu_seconds']}
            with (output / 'run_log.jsonl').open('a', encoding='utf-8') as handle:
                handle.write(json.dumps(compact, ensure_ascii=False) + '\n')
            measurements.append(row)
            return row

        for index in range(1, 11):
            row = measured_request('assessment', index, '/submit', payload, 200)
            if set(row['models']) != {'gpt2', 'distilgpt2'}:
                raise RuntimeError('The assessment workload must exercise both configured models.')
        verify_request = {'certificate_id': approved['credential']['Certificate_id'], 'text': payload['text']}
        for index in range(1, 11):
            row = measured_request('verification', index, '/verification/verify', verify_request, 200)
            if row['output'].get('verified') is not True or row['models']:
                raise RuntimeError('Verification must match without model inference.')
        measured_request('failure', 1, '/verification/verify', {'certificate_id': '', 'text': payload['text']}, 400)
        summary = {name: summarize([r for r in measurements if r['workload'] == name])
                   for name in ('assessment', 'verification')}
        runner.save(output / 'summary.json', summary)
        print(json.dumps(summary, indent=2), flush=True)
        metadata['finished_at_utc'] = runner.now()
        metadata['measurement_rows'] = len(measurements)
        runner.save(output / 'metadata.json', metadata)
    finally:
        sandbox.close()
    print(f'Summary: {output.relative_to(runner.ROOT)}/summary.json', flush=True)


if __name__ == '__main__':
    main()
