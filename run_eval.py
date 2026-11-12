#!/usr/bin/env python3
"""Run all five fixed criteria three times against the unchanged live service.

    .venv/bin/python run_eval.py --label before

Paces /submit against the shared IP allowance; keeps complete JSON responses,
HTTP statuses (including non-JSON errors), audit evidence, and source hashes.
No retry, threshold adjustment, or service restart occurs between trials.
"""
import argparse
from collections import Counter
from datetime import datetime
import hashlib
import json
import math
from pathlib import Path
import time
import uuid

import requests
import config
import scenarios
from run_paced_attacks import AttackPacer, utc_now

FROZEN_FILES = ('app.py', 'audit.py', 'config.py', 'detector.py',
                'binoculars_signal.py', 'scoring.py', 'stylometry.py',
                'appeals.py', 'submissions.py', 'verification.py', 'criteria.md',
                'scenarios.py', 'run_eval.py', 'run_paced_attacks.py',
                'eval_samples/samples.json')
UNSURE_MESSAGE = ('Based on revaluation we do not have enough evidence to determine '
                  'how this text was written. Your appeal has been recorded.')
DECISION_FIELDS = ('timestamp', 'content_id', 'creator_id', 'guess', 'model_score',
                   'style_score', 'combined_score', 'label', 'status', 'confidence')


def snapshot():
    return {name: hashlib.sha256((config.ROOT / name).read_bytes()).hexdigest()
            for name in FROZEN_FILES}


def request_json(session, method, url, timeout, body=None):
    record = {'method': method, 'url': url, 'request': body,
              'sent_at_utc': utc_now(), 'status': None, 'response': None, 'error': None}
    started = time.monotonic()
    try:
        kwargs = {'json': body} if method == 'POST' else {}
        response = session.request(method, url, timeout=timeout, **kwargs)
        record['status'] = response.status_code
        try:
            record['response'] = response.json()
        except ValueError as exc:
            record['error'] = f'{type(exc).__name__}: {exc}'
            record['response_text'] = response.text
    except requests.RequestException as exc:
        record['error'] = f'{type(exc).__name__}: {exc}'
    record['received_at_utc'] = utc_now()
    record['duration_seconds'] = time.monotonic() - started
    return record


def payload(record):
    value = record.get('response')
    return value if isinstance(value, dict) else {}


def successful(record):
    return record.get('status') == 200 and not record.get('error')


def numeric(value):
    return isinstance(value, (float, int)) and not isinstance(value, bool) and math.isfinite(value)


def criterion_label(score):
    # Independent oracle from criteria.md, deliberately not config.py.
    return 'ai' if score >= .60 else 'human' if score <= .45 else 'unsure'


def audit_checks(record, entries):
    body, response = record['request'], payload(record)
    creator = body.get('creator_id')
    expected_creator = creator if isinstance(creator, str) and creator.strip() else 'unknown'
    entry = entries[0] if len(entries) == 1 else {}
    checks = {'one_entry': len(entries) == 1,
              'timestamp': isinstance(entry.get('timestamp'), str) and bool(entry['timestamp']),
              'creator_id': entry.get('creator_id') == expected_creator}
    if successful(record):
        checks.update({
            'required_fields': all(key in entry for key in DECISION_FIELDS),
            'response_matches': all(key in response and entry.get(key) == response[key]
                for key in ('content_id', 'guess', 'model_score', 'style_score', 'combined_score', 'label', 'confidence')),
            'confidence_matches_combined': numeric(entry.get('combined_score')) and entry.get('confidence') == entry['combined_score'],
            'decided': entry.get('status') == 'decided',
        })
    else:
        checks.update({'controlled_rejection': record.get('status') == 400,
                       'rejection_format': entry.get('event') == 'rejected'
                           and entry.get('status') == 'rejected' and bool(entry.get('reason'))})
    return checks


def appeal_checks(appeal, status_record, entries):
    result = payload(appeal)
    evaluations = result.get('evaluations', [])
    votes = Counter(item.get('label') for item in evaluations)
    expected_votes = {label: votes[label] for label in ('human', 'unsure', 'ai')}
    majority = next((label for label, count in expected_votes.items() if count >= 2), 'unsure')
    accepted = [e for e in entries if e.get('event') == 'appeal']
    reassessed = [e for e in entries if e.get('event') == 'appeal_reassessment']
    message = result.get('message', '')
    if majority == 'unsure':
        message_ok = message == UNSURE_MESSAGE
    elif majority == 'ai':
        message_ok = all(phrase in message for phrase in
                        ('written by a human', 'human re-evaluation', 'earlier versions'))
    else:
        message_ok = 'Your appeal has been recorded.' in message
    arithmetic = len(evaluations) == 3 and all(
        item.get('status') == 'scored'
        and all(numeric(item.get(key)) for key in ('model_score', 'style_score', 'combined_score'))
        and math.isclose(item['combined_score'], .6 * item['model_score'] + .4 * item['style_score'], abs_tol=1e-12)
        for item in evaluations)
    return {
        'accepted': successful(appeal),
        'under_review': result.get('status') == 'under_review',
        'status_readback': successful(status_record) and payload(status_record).get('status') == 'under_review',
        'appeal_logged': len(accepted) == 1 and accepted[0].get('status') == 'under_review'
             and accepted[0].get('reasoning') == appeal['request']['reasoning'],
        'result_logged': len(reassessed) == 1 and reassessed[0].get('status') == 'under_review'
             and all(reassessed[0].get(key) == result.get(key) for key in
                     ('appeal_id', 'label', 'votes', 'evaluations', 'weights', 'message')),
        'three_variants': [e.get('variant') for e in evaluations] ==
             ['original', 'without_first_sentence', 'without_last_sentence'],
        'weights': result.get('weights') == {'model': .6, 'style': .4},
        'scored_with_60_40': arithmetic,
        'majority': result.get('votes') == expected_votes and result.get('label') == majority,
        'message': message_ok,
    }


def summarize(scenario, cases):
    number = scenario['criterion']
    results = [payload(case['submission']) for case in cases]
    all_scored = all(successful(case['submission']) and numeric(result.get('combined_score'))
                     for case, result in zip(cases, results))
    metrics = {'requests': len(cases), 'all_submissions_scored': all_scored}
    if number == 1:
        count = sum(result.get('label') == 'ai' for result in results)
        metrics.update(ai_labels=count, human_labels=sum(r.get('label') == 'human' for r in results),
                       unsure_labels=sum(r.get('label') == 'unsure' for r in results))
        met = all_scored and len(cases) == 5 and count <= 2
        display = f'{count}/5 AI' if all_scored else 'Incomplete scoring'
    elif number == 2:
        means = {}
        for label in ('human', 'ai'):
            scores = [r.get('combined_score') for c, r in zip(cases, results) if c['authorship'] == label]
            means[label] = sum(scores) / 5 if len(scores) == 5 and all(numeric(s) for s in scores) else None
        gap = means['ai'] - means['human'] if all(numeric(v) for v in means.values()) else None
        metrics.update(human_mean=means['human'], ai_mean=means['ai'], gap=gap)
        met = all_scored and gap is not None and gap >= .3
        display = f'{gap:.6f}' if gap is not None else 'Incomplete scoring'
    elif number == 3:
        for case, result in zip(cases, results):
            score = result.get('combined_score')
            case['checks'] = {
                'scored': successful(case['submission']) and numeric(score),
                'expected_label': result.get('label') == case['expected_label'],
                'criterion_band': numeric(score) and result.get('label') == criterion_label(score),
            }
        count = sum(all(c['checks'].values()) for c in cases)
        metrics.update(correct=count, labels_reached=sorted({r['label'] for r in results if 'label' in r}),
                       expected_label_matches=sum(c['checks']['expected_label'] for c in cases),
                       criterion_band_matches=sum(c['checks']['criterion_band'] for c in cases))
        met = len(cases) == 5 and count >= 4
        display = f'{count}/5'
    else:
        count = sum(all(case['checks'].values()) for case in cases)
        metrics.update(passed=count, failures=[{'case': c['id'], 'failed_checks': [k for k, v in c['checks'].items() if not v]}
                                             for c in cases if not all(c['checks'].values())])
        met = count == len(cases) == (5 if number == 4 else 10)
        display = f'{count}/{len(cases)}'
    return {'metrics': metrics, 'display': display, 'verdict': 'MET' if met else 'MISSED'}


def read_log(session, url, timeout):
    record = request_json(session, 'GET', url + '/log', timeout)
    if not successful(record) or not isinstance(payload(record).get('entries'), list):
        raise RuntimeError(f'Cannot verify audit log: {record}')
    return record


def run_case(session, url, timeout, pacer, scenario, case, trial, run_id):
    body = dict(case['body'])
    if 'creator_id' not in body and not case.get('omit_creator'):
        body['creator_id'] = f'eval_{run_id}_c{scenario["criterion"]}_t{trial}_{case["id"]}'
    pacer.before_request('evaluation')
    before = read_log(session, url, timeout) if scenario['criterion'] == 5 else None
    row = {key: case[key] for key in ('id', 'authorship', 'expected_label') if key in case}
    row['submission'] = request_json(session, 'POST', url + '/submit', timeout, body)
    if scenario['criterion'] == 5:
        after = read_log(session, url, timeout)
        offset = len(payload(before)['entries'])
        row['audit_entries'] = payload(after)['entries'][offset:]
        row['audit_count_before'] = offset
        row['audit_count_after'] = len(payload(after)['entries'])
        row['checks'] = audit_checks(row['submission'], row['audit_entries'])
    elif scenario['criterion'] == 4:
        content_id = payload(row['submission']).get('content_id')
        if not successful(row['submission']) or not content_id:
            row['checks'] = {'seed_submission': False}
            return row
        row['appeal'] = request_json(session, 'POST', url + '/appeal', timeout,
            {'content_id': content_id, 'reasoning': 'Please review this evaluation against the retained original and both sentence-removal variants.'})
        row['status_readback'] = request_json(session, 'GET', url + '/content/' + content_id, timeout)
        log = read_log(session, url, timeout)
        appeal_id = payload(row['appeal']).get('appeal_id')
        row['audit_entries'] = [e for e in payload(log)['entries'] if e.get('content_id') == content_id and e.get('appeal_id') == appeal_id]
        row['checks'] = appeal_checks(row['appeal'], row['status_readback'], row['audit_entries'])
    return row


def write_report(rows, output, label):
    lines = [f'# Five-criterion run — {label}', '',
             'Produced by `run_eval.py::main`, `run_case`, and `summarize`.', '',
             '| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |',
             '|---|---|---|---|---|---|']
    for row in rows:
        trials = row['trials']
        verdict = 'MET' if all(t['verdict'] == 'MET' for t in trials) else 'MISSED'
        lines.append(f"| {row['criterion']}. {row['name']} | {row['target']} | " +
                     ' | '.join(t['display'] for t in trials) + f' | {verdict} |')
    lines += ['', 'All raw requests, responses, checks, and trial metrics follow.', '']
    for row in rows:
        lines += [f"## {row['criterion']}. {row['name']}", '', '```json',
                  json.dumps(row, indent=2, ensure_ascii=False), '```', '']
    (output / 'report.md').write_text('\n'.join(lines), encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--label', default='before')
    parser.add_argument('--trials', type=int, default=3, choices=[3])
    parser.add_argument('--url', default=f'http://{config.HOST}:{config.PORT}')
    parser.add_argument('--timeout', type=float, default=90)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if problems := scenarios.validate():
        parser.error('; '.join(problems))
    output = args.output or config.RESULTS_DIR / f'run_{datetime.now():%Y-%m-%d_%H%M%S}_{args.label}'
    output.mkdir(parents=True, exist_ok=False)
    frozen = snapshot()
    for name in FROZEN_FILES:
        target = output / 'inputs' / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((config.ROOT / name).read_bytes())
    metadata = {'url': args.url, 'label': args.label, 'trials': 3, 'source_sha256': frozen,
                'submit_requests_planned': sum(len(s['cases']) for s in scenarios.SCENARIOS) * 3,
                'pacing': f'{config.RATE_LIMIT_PER_MINUTE} submissions per 61-second window; no retries',
                'run_id': uuid.uuid4().hex[:8]}
    session = requests.Session()
    health = request_json(session, 'GET', args.url + '/health', args.timeout)
    metadata['health_before'] = health
    if not successful(health) or payload(health).get('rate_limiting') is not True:
        parser.error('The live service must return JSON health with rate_limiting=true')
    (output / 'metadata.json').write_text(json.dumps(metadata, indent=2) + '\n')
    print('Health before:', json.dumps(payload(health)), flush=True)
    started = time.monotonic()
    time.sleep(10)
    metadata['health_wait_seconds'] = time.monotonic() - started
    metadata['started_at_utc'] = utc_now()
    pacer = AttackPacer(config.RATE_LIMIT_PER_MINUTE)
    rows = []
    for scenario in scenarios.SCENARIOS:
        row = {key: scenario[key] for key in ('criterion', 'name', 'target')}
        row['trials'] = []
        for trial in range(1, 4):
            cases = []
            for case in scenario['cases']:
                result = run_case(session, args.url, args.timeout, pacer, scenario, case, trial, metadata['run_id'])
                cases.append(result)
                with (output / 'responses.jsonl').open('a', encoding='utf-8') as handle:
                    handle.write(json.dumps({'criterion': scenario['criterion'], 'trial': trial, **result}, ensure_ascii=False) + '\n')
                print(f"C{scenario['criterion']} trial {trial} {case['id']}: HTTP {result['submission']['status']} {payload(result['submission']).get('label', '')}", flush=True)
            summary = summarize(scenario, cases)
            row['trials'].append({'trial': trial, **summary, 'cases': cases})
            print(f"C{scenario['criterion']} trial {trial}: {summary['display']} {summary['verdict']}", flush=True)
        rows.append(row)
        (output / 'results.json').write_text(json.dumps(rows, indent=2, ensure_ascii=False) + '\n')
    metadata['finished_at_utc'] = utc_now()
    metadata['health_after'] = request_json(session, 'GET', args.url + '/health', args.timeout)
    log = read_log(session, args.url, args.timeout)
    entries = payload(log)['entries'][payload(health)['log_entries']:]
    (output / 'audit_excerpt.jsonl').write_text(''.join(json.dumps(e, ensure_ascii=False) + '\n' for e in entries))
    metadata['audit_entries_captured'] = len(entries)
    metadata['source_sha256_after'] = snapshot()
    metadata['service_and_inputs_unchanged'] = metadata['source_sha256_after'] == frozen
    (output / 'metadata.json').write_text(json.dumps(metadata, indent=2) + '\n')
    write_report(rows, output, args.label)
    print('Health after:', json.dumps(payload(metadata['health_after'])), flush=True)
    print(f'Recorded all five criteria, three trials each: {output}', flush=True)
    if not metadata['service_and_inputs_unchanged']:
        raise SystemExit('Files changed during the run; these trials are not a stable baseline.')


if __name__ == '__main__':
    main()
