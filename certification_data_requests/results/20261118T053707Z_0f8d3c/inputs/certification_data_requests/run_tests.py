#!/usr/bin/env python3
"""Run criteria 6–10 with curl, isolated Docker records, and three fixed trials.

Host dependencies: Python 3.9+, Docker and curl. Run from the project directory.
No application imports or changes to the running Compose service are required.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys
import time
import uuid

PACK = Path(__file__).resolve().parent
ROOT = PACK.parent
CERT_FILE = 'verified_human_certification_log.jsonl'
BUSINESS_FILES = ('submissions.jsonl', 'audit.jsonl', CERT_FILE)


class FixtureError(Exception):
    """Invalid test data must stop the run before application testing continues."""


def now():
    return datetime.now(timezone.utc).isoformat()


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def save(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def command(args, **kwargs):
    result = subprocess.run(args, text=True, capture_output=True, **kwargs)
    if result.returncode:
        raise RuntimeError(f'{shlex.join(args[:4])}: {result.stderr.strip() or result.stdout.strip()}')
    return result.stdout.strip()


def docker(*args, **kwargs):
    return command(['docker', *args], **kwargs)


def checked(case, name, actual, expected=True):
    case['checks'][name] = {'passed': type(actual) is type(expected) and actual == expected,
                            'expected': expected, 'actual': actual}


def case_passed(case):
    return bool(case['checks']) and all(v.get('passed') is True for v in case['checks'].values())


def validate_pack():
    manifest = read(PACK / 'manifest.json')
    fixtures = read(PACK / 'fixtures.json')
    specs = [read(PACK / name) for name in manifest['criteria']]
    if manifest['runs'] != 3 or manifest['cases_per_criterion'] != 5:
        raise ValueError('The plan must specify three runs and five cases per criterion.')
    if [s['number'] for s in specs] != list(range(6, 11)) or len(fixtures) != 5:
        raise ValueError('Expected criteria 6–10 and five fixtures.')
    for fixture in fixtures:
        text = read(PACK / fixture['submit_file'])['text']
        digest = hashlib.sha256(text.encode('utf-8')).hexdigest()
        if digest != fixture['sha256'] or digest[-8:] != fixture['certificate_id']:
            raise ValueError(f'Fixture hash changed: {fixture["id"]}')
        if len(text.split()) < 40 or len(re.findall(r'[.!?](?:\s|$)', text)) < 3:
            raise ValueError(f'Fixture too short: {fixture["id"]}')
    if len({f['certificate_id'] for f in fixtures}) != 5:
        raise ValueError('Wrong-pairing fixtures need five different short IDs.')
    for spec in specs:
        if len(spec['cases']) != 5:
            raise ValueError(f'Criterion {spec["number"]} must have exactly five cases.')
        spec['case_specs'] = [read(PACK / name) for name in spec['cases']]
        for case in spec['case_specs']:
            for req in case['requests']:
                read(PACK / req['json_file'])
        count = sum(r.get('repeat', 1) for c in spec['case_specs'] for r in c['requests'])
        if count != {6: 5, 7: 10, 8: 20, 9: 13, 10: 10}[spec['number']]:
            raise ValueError(f'Unexpected request count in criterion {spec["number"]}.')
    return fixtures, specs


class Sandbox:
    def __init__(self, image, cache, offline, output, readiness_timeout):
        self.image, self.cache, self.offline = image, cache, offline
        self.output, self.readiness_timeout = output, readiness_timeout
        self.name = 'certification-test-' + uuid.uuid4().hex[:12]
        self.volume = self.name + '-logs'
        self.base = None
        self.history = []
        self.requests = 0
        self.window_start, self.window_count = None, 0
        self.allowance = None
        self.output.mkdir(parents=True)

    def execute(self, code, data=None):
        return docker('exec', '-i', self.name, 'python', '-c', code,
                      input=json.dumps(data) if data is not None else '')

    def start(self):
        args = ['run', '-d', '--init', '--name', self.name, '--no-healthcheck',
                '-p', '127.0.0.1::5000', '-v', self.volume + ':/app/logs',
                '-v', self.cache + ':/models' + (':ro' if self.offline else '')]
        if self.offline:
            args += ['-e', 'HF_HUB_OFFLINE=1', '-e', 'TRANSFORMERS_OFFLINE=1']
        container_id = docker(*args, self.image)
        info = json.loads(docker('inspect', self.name))[0]
        self.base = 'http://127.0.0.1:' + info['NetworkSettings']['Ports']['5000/tcp'][0]['HostPort']
        self.history.append({'container_id': container_id, 'url': self.base, 'started_at': now(),
                             'log_volume': self.volume})
        deadline = time.monotonic() + self.readiness_timeout
        while time.monotonic() < deadline:
            result = subprocess.run(['curl', '-sS', '--max-time', '2', self.base + '/health'],
                                    text=True, capture_output=True)
            try:
                health = json.loads(result.stdout)
                if result.returncode == 0 and health.get('ok') and health.get('inference_ready'):
                    self.history[-1]['ready_health'] = health
                    break
            except ValueError:
                pass
            time.sleep(.5)
        else:
            raise RuntimeError('Models did not become ready; see container.log.')
        settings = json.loads(self.execute(
            'import config,json; print(json.dumps({"minute_limit":config.RATE_LIMIT_PER_MINUTE,'
            '"day_limit":config.RATE_LIMIT_PER_DAY,"timeout":config.REQUEST_TIMEOUT_SECONDS}))'))
        self.history[-1]['settings'] = settings
        self.allowance = settings['minute_limit']
        self.window_start, self.window_count = None, 0
        save(self.output / 'containers.json', self.history)

    def pace(self):
        current = time.monotonic()
        if self.window_start is not None and self.window_count >= self.allowance:
            delay = max(0, self.window_start + 61 - current)
            if delay:
                print(f'  Waiting {delay:.1f}s for the unchanged submit rate limit.', flush=True)
            while time.monotonic() < self.window_start + 61:
                time.sleep(min(10, self.window_start + 61 - time.monotonic()))
            self.window_start = None
        if self.window_start is None or time.monotonic() - self.window_start >= 61:
            self.window_start, self.window_count = time.monotonic(), 0
        self.window_count += 1

    def request(self, endpoint, body, tag):
        if endpoint == '/submit':
            self.pace()
        self.requests += 1
        stem = f'{self.requests:03}_{tag}'
        request_file = self.output / 'requests' / (stem + '.json')
        response_file = self.output / 'responses' / (stem + '.json')
        response_file.parent.mkdir(exist_ok=True)
        save(request_file, body)
        args = ['curl', '--silent', '--show-error', '--max-time', '30',
                '--request', 'POST', '--header', 'Content-Type: application/json',
                '--data-binary', '@' + str(request_file), '--output', str(response_file),
                '--write-out', '%{http_code}', self.base + endpoint]
        started = time.monotonic()
        record = {'tag': tag, 'sent_at_utc': now(), 'endpoint': endpoint,
                  'request_file': str(request_file.relative_to(ROOT)), 'request': body}
        result = subprocess.run(args, text=True, capture_output=True)
        record.update(duration_seconds=time.monotonic() - started, curl_exit_code=result.returncode,
                      http_status=int(result.stdout) if result.stdout.isdigit() else None,
                      stderr=result.stderr, received_at_utc=now())
        raw = response_file.read_text(encoding='utf-8') if response_file.exists() else ''
        try:
            record['response'] = json.loads(raw)
        except ValueError:
            record['response'] = None
            record['response_text'] = raw
        with (self.output / 'responses.jsonl').open('a', encoding='utf-8') as handle:
            handle.write(json.dumps(record, ensure_ascii=False) + '\n')
        # Recorded commands use parent-directory paths. These ports belong only
        # to the temporary container; re-running the harness creates fresh IDs.
        display = ['curl', '-sS', '-i', '-X', 'POST', '-H', 'Content-Type: application/json',
                   '--data-binary', '@' + str(request_file.relative_to(ROOT)), self.base + endpoint]
        with (self.output / 'curl_commands.sh').open('a', encoding='utf-8') as handle:
            handle.write(f'# {tag}\n' + shlex.join(display) + '\n')
        return record

    def snapshot(self, label):
        files = json.loads(self.execute(
            'import pathlib,json,sys; print(json.dumps({name: '
            '(pathlib.Path("/app/logs")/name).read_text(encoding="utf-8") '
            'if (pathlib.Path("/app/logs")/name).exists() else None for name in json.load(sys.stdin)}))',
            BUSINESS_FILES))
        folder = self.output / 'snapshots' / label
        folder.mkdir(parents=True, exist_ok=True)
        for name, value in files.items():
            if value is not None:
                (folder / name).write_text(value, encoding='utf-8')
        return files

    def append_certificates(self, text):
        # Only this object's randomly named test container can be targeted.
        self.execute('import pathlib,sys,json; p=pathlib.Path("/app/logs/' + CERT_FILE + '"); '
                     'p.open("a",encoding="utf-8").write(json.load(sys.stdin))', text)

    def replace(self):
        self.export('before-replacement')
        docker('rm', '-f', self.name)
        self.start()

    def export(self, label='final'):
        folder = self.output / label
        folder.mkdir(exist_ok=True)
        docker('cp', self.name + ':/app/logs', str(folder / 'logs'))
        logs = subprocess.run(['docker', 'logs', self.name], text=True, capture_output=True)
        (folder / 'container.log').write_text(logs.stdout + logs.stderr, encoding='utf-8')

    def close(self):
        try:
            self.export()
        finally:
            removed = subprocess.run(['docker', 'rm', '-f', self.name], capture_output=True, text=True)
            if removed.returncode and 'No such container' not in removed.stderr:
                raise RuntimeError(removed.stderr)
            docker('volume', 'rm', self.volume)


def body(record):
    return record.get('response') if isinstance(record.get('response'), dict) else {}


def require(record, status):
    if record['curl_exit_code'] or record['http_status'] != status or not isinstance(record['response'], dict):
        raise RuntimeError(f'{record["tag"]}: expected HTTP {status}; got {record["http_status"]}: '
                           f'{record.get("response_text", record["response"])}')
    return record['response']


def certify(sandbox, fixture, tag):
    submitted = require(sandbox.request('/submit', read(PACK / fixture['submit_file']), tag + '_submit'), 200)
    content_id = submitted['content_id']
    request = read(PACK / 'request_human_review.template.json')
    request['content_id'] = content_id
    require(sandbox.request('/appeal', request, tag + '_request_review'), 202)
    approval = read(PACK / 'approve_review.template.json')
    approval['content_id'] = content_id
    reviewed = require(sandbox.request('/verification/review', approval, tag + '_approve'), 200)
    return {'content_id': content_id, 'credential': reviewed['credential'], 'approval': approval,
            'request_id': reviewed['verification_request_id']}


def records(snapshot, filename):
    return [json.loads(line) for line in (snapshot[filename] or '').splitlines() if line.strip()]


def check_request(sandbox, case, spec, suffix=''):
    result = sandbox.request(spec['endpoint'], read(PACK / spec['json_file']), case['id'] + suffix)
    checked(case, suffix + '_curl_succeeded', result['curl_exit_code'], 0)
    checked(case, suffix + '_http_status', result['http_status'], spec['expected_status'])
    for key, expected in spec.get('expected_fields', {}).items():
        checked(case, suffix + '_' + key, body(result).get(key), expected)
    return result


def token_check(sandbox, fixtures):
    fixture = fixtures[-1]
    text = read(PACK / fixture['submit_file'])['text']
    changed = text.replace(fixture['word_edit_original'], fixture['word_edit_replacement'], 1)
    code = ('import json,sys; from transformers import AutoTokenizer; '
            'd=json.load(sys.stdin); t=AutoTokenizer.from_pretrained("gpt2",local_files_only=True); '
            'a=t(d["text"],truncation=False,return_offsets_mapping=True); '
            'b=t(d["changed"],truncation=False); p=d["text"].index(d["word"]); '
            'print(json.dumps({"tokens":len(a["input_ids"]),'
            '"tokens_before_edit":sum(end<=p for start,end in a["offset_mapping"]),'
            '"first_400_tokens_unchanged":a["input_ids"][:400]==b["input_ids"][:400]}))')
    result = json.loads(sandbox.execute(code, {'text': text, 'changed': changed,
                                              'word': fixture['word_edit_original']}))
    if result['tokens'] <= 400 or result['tokens_before_edit'] < 400 or not result['first_400_tokens_unchanged']:
        raise FixtureError(f'Long-text fixture does not test the required model boundary: {result}')
    return result


def evaluate(sandbox, spec, fixtures, cases):
    seeds = {f['id']: certify(sandbox, f, 'seed_' + f['id']) for f in fixtures}
    before = sandbox.snapshot('after-initial-approvals')
    if len(records(before, CERT_FILE)) != 5:
        raise RuntimeError('Initial setup did not create exactly five certificate records.')
    number = spec['number']
    for case, plan in zip(cases, spec['case_specs']):
        try:
            if number == 6:
                fixture = next(f for f in fixtures if f['id'] == plan['fixture_id'])
                seed = seeds[fixture['id']]
                digest = hashlib.sha256(read(PACK / fixture['submit_file'])['text'].encode('utf-8')).hexdigest()
                expected = {'Certificate_id': digest[-8:], 'content_hash': digest, 'hash_algorithm': 'sha256'}
                for field, value in expected.items():
                    checked(case, 'response_' + field, seed['credential'].get(field), value)
                for filename in (CERT_FILE, 'audit.jsonl'):
                    matches = [r for r in records(before, filename) if r.get('event') == 'human_verification_review'
                               and r.get('verification_request_id') == seed['request_id']]
                    checked(case, filename + '_one_approval', len(matches), 1)
                    for field, value in expected.items():
                        checked(case, filename + '_' + field,
                                matches[0].get('credential', {}).get(field) if matches else None, value)
            elif number == 7:
                fixture = next(f for f in fixtures if f['id'] == plan['fixture_id'])
                first = seeds[fixture['id']]
                second = certify(sandbox, fixture, case['id'] + '_second')
                checked(case, 'separate_submission', second['content_id'] != first['content_id'])
                saved = sandbox.snapshot(case['id'] + '-before-lookups')
                approvals = records(saved, CERT_FILE)
                latest = next(r for r in approvals if r['verification_request_id'] == second['request_id'])
                older = next(r for r in approvals if r['verification_request_id'] == first['request_id'])
                checked(case, 'second_is_later', datetime.fromisoformat(latest['timestamp']) >
                        datetime.fromisoformat(older['timestamp']))
                for index in (1, 2):
                    response = body(check_request(sandbox, case, plan['requests'][0], f'_lookup_{index}'))
                    for field, expected in {
                        'certificate_id': second['credential']['Certificate_id'],
                        'content_id': second['content_id'],
                        'verified_dt_time': second['credential']['verified_dt_time'],
                        'latest_certification_at': datetime.fromisoformat(latest['timestamp']).isoformat(),
                    }.items():
                        checked(case, f'lookup_{index}_{field}', response.get(field), expected)
                sandbox.snapshot(case['id'] + '-after-lookups')
            elif number in (8, 9):
                if 'seed_records_file' in plan:
                    sandbox.append_certificates(''.join(json.dumps(r) + '\n' for r in read(PACK / plan['seed_records_file'])))
                if 'append_to_certificate_store' in plan:
                    sandbox.append_certificates(plan['append_to_certificate_store'])
                for index, request in enumerate(plan['requests'], 1):
                    check_request(sandbox, case, request, f'_check_{index}')
            if number != 10:
                checked(case, 'completed', True)
        except (RuntimeError, KeyError, ValueError, OSError) as exc:
            checked(case, 'execution_error', str(exc), 'No error')
    if number == 10:
        sandbox.replace()
        after_restart = sandbox.snapshot('after-replacement')
        changed_container = sandbox.history[0]['container_id'] != sandbox.history[1]['container_id']
        for case, plan in zip(cases, spec['case_specs']):
            checked(case, 'actual_container_replacement', changed_container)
            seed = seeds[plan['fixture_id']]
            for filename in (CERT_FILE, 'audit.jsonl'):
                original = [r for r in records(before, filename)
                            if r.get('event') == 'human_verification_review'
                            and r.get('verification_request_id') == seed['request_id']]
                restored = [r for r in records(after_restart, filename)
                            if r.get('event') == 'human_verification_review'
                            and r.get('verification_request_id') == seed['request_id']]
                checked(case, filename + '_one_original_approval', len(original), 1)
                checked(case, filename + '_preserved', restored, original)
            checked(case, 'exactly_five_certificates', len(records(after_restart, CERT_FILE)), 5)
            for index, request in enumerate(plan['requests'], 1):
                check_request(sandbox, case, request, f'_after_restart_{index}')
            checked(case, 'completed', True)


def write_report(specs, trials, output):
    lines = ['# Certified-content integrity — criteria 6–10', '',
             'Five cases per criterion per run. A case passes only when every check passes.',
             'Three runs: 25 cases per run, 75 case executions. Setup requests are not extra cases.', '',
             '| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |',
             '|---|---|---|---|---|---|']
    for spec in specs:
        values, passed = [], []
        for trial in range(1, 4):
            row = next((r for r in trials if r['criterion'] == spec['number'] and r['run'] == trial), None)
            count = sum(case_passed(c) for c in row['cases']) if row else None
            values.append(f'{count}/5' if row else 'NOT RUN')
            passed.append(row is not None and len(row['cases']) == 5 and count == 5)
        verdict = 'PASSED' if all(passed) else ('INCOMPLETE' if 'NOT RUN' in values else 'MISSED')
        lines.append(f'| {spec["number"]}. {spec["name"]} | {spec["target"]} | ' +
                     ' | '.join(values) + f' | **{verdict}** |')
    lines += ['', '## Failed checks', '']
    failures = []
    for row in trials:
        for case in row['cases']:
            names = [name for name, value in case['checks'].items() if not value['passed']]
            if not case['checks']:
                names = ['Case was not executed']
            if names:
                failures.append(f'- Criterion {row["criterion"]}, Run {row["run"]}, {case["id"]}: ' + ', '.join(names))
    lines += failures or ['None in the completed cases.']
    lines += ['', 'See `results.json` for expected/actual checks, `metadata.json` for source/image identity,',
              'and each run directory for JSON requests, raw responses, recorded curl commands,',
              'business-record snapshots, operational logs and container logs.', '',
              'Fixture approvals are synthetic test actions; they do not establish human authorship.', '']
    (output / 'report.md').write_text('\n'.join(lines), encoding='utf-8')
    save(output / 'results.json', trials)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--image', default='provenance-guard:certification-tests')
    parser.add_argument('--skip-build', action='store_true', help='Use an existing image, recorded by immutable ID.')
    parser.add_argument('--model-cache', help='Existing Docker model-cache volume to mount read-only/offline.')
    parser.add_argument('--readiness-timeout', type=float, default=300)
    parser.add_argument('--validate-only', action='store_true', help='Validate local JSON files; no Docker or HTTP.')
    args = parser.parse_args()
    fixtures, specs = validate_pack()
    if args.validate_only:
        print('Valid JSON pack: five criteria, five cases each, three runs; fixture hashes match.')
        return 0
    for executable in ('docker', 'curl'):
        if not shutil.which(executable):
            parser.error(f'{executable} is required.')
    if args.readiness_timeout <= 0:
        parser.error('--readiness-timeout must be positive.')
    output = PACK / 'results' / (datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '_' + uuid.uuid4().hex[:6])
    output.mkdir(parents=True)
    print(f'Evidence directory: {output.relative_to(ROOT)}', flush=True)
    inputs = output / 'inputs'
    inputs.mkdir()
    source_hashes = {}
    for source in sorted([*ROOT.glob('*.py'), ROOT / 'criteria.md', ROOT / 'Dockerfile', ROOT / '.dockerignore', ROOT / 'requirements-docker.lock',
                          *[p for p in PACK.rglob('*') if p.is_file() and 'results' not in p.relative_to(PACK).parts
                            and '__pycache__' not in p.parts]]):
        relative = source.relative_to(ROOT)
        target = inputs / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        source_hashes[str(relative)] = hashlib.sha256(source.read_bytes()).hexdigest()
    if not args.skip_build:
        print('Building a separate test image; see build.log.', flush=True)
        with (output / 'build.log').open('w', encoding='utf-8') as log:
            subprocess.run(['docker', 'build', '-t', args.image, '.'], cwd=ROOT, stdout=log,
                           stderr=subprocess.STDOUT, check=True)
    image = json.loads(docker('image', 'inspect', args.image))[0]['Id']
    cache, owned_cache = args.model_cache, False
    if not cache:
        services = subprocess.run(['docker', 'compose', 'ps', '-q', 'app'], cwd=ROOT, text=True, capture_output=True)
        if services.returncode == 0 and services.stdout.strip():
            current = json.loads(docker('inspect', services.stdout.strip()))[0]
            cache = next((m['Name'] for m in current['Mounts'] if m['Destination'] == '/models' and m['Type'] == 'volume'), None)
    if cache:
        docker('volume', 'inspect', cache)
    else:
        cache = 'certification-models-' + uuid.uuid4().hex[:12]
        docker('volume', 'create', cache)
        owned_cache = True
        print('No existing model cache: the isolated service will download its CPU models.', flush=True)
    metadata = {'started_at_utc': now(), 'image_id': image, 'image_tag': args.image,
                'source_sha256': source_hashes, 'model_cache': cache, 'model_cache_read_only': not owned_cache,
                'runs': 3, 'cases_per_criterion_per_run': 5, 'http_client': 'curl',
                'pacing': 'At most the configured minute limit of submissions per 61-second window; no failed-request retries.',
                'settings': 'Application defaults; no timeout, circuit-breaker, scoring or rate-limit overrides.'}
    save(output / 'metadata.json', metadata)
    trials = []
    write_report(specs, trials, output)
    try:
        for trial in range(1, 4):
            for spec in specs:
                print(f'Run {trial}/3 — criterion {spec["number"]}: {spec["name"]}', flush=True)
                cases = [{'id': c['id'], 'name': c['name'], 'checks': {}} for c in spec['case_specs']]
                for case in cases:
                    checked(case, 'completed', False)
                row = {'run': trial, 'criterion': spec['number'], 'cases': cases}
                sandbox = Sandbox(image, cache, not owned_cache,
                                  output / f'run_{trial}' / f'criterion_{spec["number"]:02}', args.readiness_timeout)
                docker('volume', 'create', sandbox.volume)
                try:
                    sandbox.start()
                    if 'image_source_sha256' not in metadata:
                        names = [name for name in source_hashes if '/' not in name and name.endswith('.py')]
                        image_hashes = json.loads(sandbox.execute(
                            'import pathlib,hashlib,json,sys; print(json.dumps({name: '
                            'hashlib.sha256(pathlib.Path(name).read_bytes()).hexdigest() '
                            'for name in json.load(sys.stdin)}))', names))
                        metadata['image_source_sha256'] = image_hashes
                        metadata['image_matches_workspace_python'] = all(
                            image_hashes[name] == source_hashes[name] for name in names)
                        save(output / 'metadata.json', metadata)
                    if not metadata['image_matches_workspace_python']:
                        raise RuntimeError('Image Python source differs from the workspace. Rebuild the test image.')
                    if 'long_text_token_validation' not in metadata:
                        metadata['long_text_token_validation'] = token_check(sandbox, fixtures)
                        save(output / 'metadata.json', metadata)
                    evaluate(sandbox, spec, fixtures, cases)
                except FixtureError as exc:
                    for case in cases:
                        checked(case, 'invalid_fixture', str(exc), 'Valid fixture')
                    raise
                except (RuntimeError, KeyError, ValueError, OSError) as exc:
                    for case in cases:
                        checked(case, 'criterion_setup_or_execution', str(exc), 'No error')
                finally:
                    try:
                        sandbox.close()
                    except (RuntimeError, OSError) as exc:
                        row['cleanup_error'] = str(exc)
                        for case in cases:
                            checked(case, 'evidence_and_cleanup', str(exc), 'No error')
                    trials.append(row)
                    write_report(specs, trials, output)
                print(f'  {sum(case_passed(c) for c in cases)}/5 cases passed.', flush=True)
    finally:
        if owned_cache:
            docker('volume', 'rm', cache)
        metadata['finished_at_utc'] = now()
        metadata['source_unchanged'] = all(hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest
                                           for name, digest in source_hashes.items())
        save(output / 'metadata.json', metadata)
        if not metadata['source_unchanged']:
            for row in trials:
                for case in row['cases']:
                    checked(case, 'source_unchanged', False)
        write_report(specs, trials, output)
    print('\n' + (output / 'report.md').read_text(encoding='utf-8').split('## Failed checks')[0], flush=True)
    print(f'Report: {output.relative_to(ROOT)}/report.md', flush=True)
    return 0 if len(trials) == 15 and all(case_passed(c) for r in trials for c in r['cases']) else 1


if __name__ == '__main__':
    sys.exit(main())
