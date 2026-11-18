#!/usr/bin/env python3
"""Measure rejection of ambiguous certificate JSON; separate from criteria 6–10.

Run from the project root with an existing image and Docker model-cache volume:
python3 certification_data_requests/check_duplicate_fields.py \
    --image IMAGE --model-cache VOLUME --label before

Three variants × three trials. The target is HTTP 503, verified: false,
certificate_store_unavailable for every deliberately ambiguous record.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import uuid

import run_tests as runner


def variants(record):
    """Keep the valid value last, exposing ordinary json.loads last-value behavior."""
    original = json.dumps(record, ensure_ascii=False)
    fields = {'content_hash': '0' * 64, 'Certificate_id': 'wrong_id', 'status': 'not_certified'}
    for field, conflicting in fields.items():
        value = record['credential'][field] if field != 'status' else record[field]
        token = json.dumps(field) + ': ' + json.dumps(value)
        assert original.count(token) == 1
        replacement = json.dumps(field) + ': ' + json.dumps(conflicting) + ', ' + token
        yield field, original.replace(token, replacement, 1) + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--image', required=True)
    parser.add_argument('--model-cache', required=True)
    parser.add_argument('--label', choices=('before', 'after'), required=True)
    args = parser.parse_args()
    image = json.loads(runner.docker('image', 'inspect', args.image))[0]['Id']
    runner.docker('volume', 'inspect', args.model_cache)
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    output = runner.PACK / 'results' / f'duplicate_fields_{args.label}_{stamp}_{uuid.uuid4().hex[:6]}'
    output.mkdir(parents=True)
    shutil.copyfile(__file__, output / 'measurement_script.py')
    fixture = runner.read(runner.PACK / 'fixtures.json')[0]
    text = runner.read(runner.PACK / fixture['submit_file'])['text']
    runner.save(output / 'fixture.json', runner.read(runner.PACK / fixture['submit_file']))
    metadata = {'label': args.label, 'image_id': image, 'started_at_utc': runner.now(),
                'target': '3/3 ambiguous records rejected in each of three trials',
                'note': 'Supplemental diagnostic; formal criteria 6–10 are unchanged.',
                'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    rows = []
    runner.save(output / 'metadata.json', metadata)
    print(f'Diagnostic evidence: {output.relative_to(runner.ROOT)}', flush=True)
    try:
        for trial in (1, 2, 3):
            sandbox = runner.Sandbox(image, args.model_cache, True, output / f'run_{trial}', 120)
            runner.docker('volume', 'create', sandbox.volume)
            try:
                sandbox.start()
                if trial == 1:
                    source = sandbox.execute('from pathlib import Path; print(Path("verification.py").read_text())')
                    (output / 'verification.py').write_text(source + '\n', encoding='utf-8')
                    metadata['verification_sha256'] = sandbox.execute(
                        'import hashlib,pathlib; print(hashlib.sha256(pathlib.Path("verification.py").read_bytes()).hexdigest())')
                    runner.save(output / 'metadata.json', metadata)
                approved = runner.certify(sandbox, fixture, 'seed')
                snapshot = sandbox.snapshot('original')
                certificate = runner.records(snapshot, runner.CERT_FILE)[0]
                for field, raw in variants(certificate):
                    (sandbox.output / f'duplicate_{field}.jsonl').write_text(raw, encoding='utf-8')
                    sandbox.execute('import pathlib,sys,json; '
                                    'pathlib.Path("/app/logs/' + runner.CERT_FILE + '").write_text('
                                    'json.load(sys.stdin),encoding="utf-8")', raw)
                    result = sandbox.request('/verification/verify', {
                        'certificate_id': approved['credential']['Certificate_id'], 'text': text,
                    }, 'duplicate_' + field)
                    body = runner.body(result)
                    row = {'run': trial, 'duplicate_field': field,
                           'http_status': result['http_status'], 'response': result['response'],
                           'passed': result['curl_exit_code'] == 0 and result['http_status'] == 503
                           and body.get('verified') is False
                           and body.get('error') == 'certificate_store_unavailable'}
                    rows.append(row)
                    runner.save(output / 'results.json', rows)
                print(f'Run {trial}: {sum(r["passed"] for r in rows if r["run"] == trial)}/3 rejected.', flush=True)
            finally:
                sandbox.close()
    finally:
        metadata['finished_at_utc'] = runner.now()
        metadata['completed_checks'] = len(rows)
        metadata['rejected_correctly'] = sum(r['passed'] for r in rows)
        runner.save(output / 'metadata.json', metadata)
    lines = [f'# Duplicate-field diagnostic — {args.label}', '',
             '| Duplicate field | Run 1 | Run 2 | Run 3 | Verdict |', '|---|---|---|---|---|']
    for field in ('content_hash', 'Certificate_id', 'status'):
        group = [r for r in rows if r['duplicate_field'] == field]
        values = [f'{r["http_status"]}; verified={str(r["response"].get("verified")).lower()}' for r in group]
        verdict = 'MET' if len(group) == 3 and all(r['passed'] for r in group) else 'MISSED'
        lines.append(f'| {field} | ' + ' | '.join(values) + f' | {verdict} |')
    lines += ['', 'Target: each ambiguous record returns 503, verified: false, certificate_store_unavailable.',
              'Full requests, responses, intentionally corrupted files, logs and image identity are retained.', '']
    (output / 'report.md').write_text('\n'.join(lines), encoding='utf-8')
    print(f'Report: {output.relative_to(runner.ROOT)}/report.md', flush=True)
    return 0 if len(rows) == 9 and all(r['passed'] for r in rows) else 1


if __name__ == '__main__':
    raise SystemExit(main())
