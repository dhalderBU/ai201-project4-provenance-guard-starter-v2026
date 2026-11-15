"""Five Unit 7 criteria, fixed inputs, and explicit targets for Unit 8.

Fixtures are frozen in eval_samples/samples.json. Own writing is preserved
verbatim; supplemental HC3 texts retain their dataset labels and provenance.
No scenario is selected by its score in this evaluation.

run_eval.py submits these cases and checks each criterion in three trials.
Expected labels describe the test inputs; they are not changed to match a
service response. The original acceptance targets remain in criteria.md.
"""
import json
from pathlib import Path

SAMPLES = {item['id']: item for item in json.loads(
    (Path(__file__).parent / 'eval_samples/samples.json').read_text(encoding='utf-8'))}
# These two samples are my own writing. The other three human samples retain
# the HC3 dataset's human labels; they are not presented as my own work.
OWN_WRITING_IDS = ['own_1', 'own_2']
HC3_HUMAN_IDS = ['human_00000000_02', 'human_00000051_02', 'human_00000362_02']
HUMAN_IDS = OWN_WRITING_IDS + HC3_HUMAN_IDS
AI_IDS = ['ai_00000113_00', 'ai_00000318_00', 'ai_00000552_00', 'ai_00001008_00', 'ai_00001495_00']


def text_case(sample_id, expected_label=None):
    """Build a POST /submit case using the retained, unedited sample text."""
    sample = SAMPLES[sample_id]
    return {'id': sample_id, 'body': {'text': sample['text']},
            'authorship': sample['label'],
            'expected_label': expected_label or sample['label']}


SCENARIOS = [
    # 1. Submit five human texts, including my own writing. Count AI labels;
    # human and unsure avoid a false AI accusation. All five must be scored.
    {
        'criterion': 1,
        'name': 'False positive rate',
        'target': 'At most 2/5 human pieces labelled AI',
        'cases': [text_case(key) for key in HUMAN_IDS],
    },

    # 2. Submit five texts from each authorship group. Compare the mean
    # combined scores: mean(AI) - mean(human) must be at least 0.30.
    {
        'criterion': 2,
        'name': 'AI minus human mean score',
        'target': 'Mean gap >= 0.30 (5 AI + 5 human)',
        'cases': [text_case(key) for key in HUMAN_IDS + AI_IDS],
    },

    # 3. Include intended human, unsure, and AI examples. A case passes only
    # when its returned label matches both the expected label below and the
    # original criteria.md score bands (human <= 0.45, AI >= 0.60).
    # coverage_3 remains an intended unsure case even if the service misses it.
    {
        'criterion': 3,
        'name': 'Correct labels',
        'target': 'At least 4/5 correct labels',
        'cases': [
            text_case('own_1', expected_label='human'),
            text_case('coverage_1', expected_label='ai'),
            text_case('coverage_2', expected_label='human'),
            text_case('coverage_3', expected_label='unsure'),
            text_case('demo_ai', expected_label='ai'),
        ],
    },

    # 4. Each submission supplies a real content_id for a nonempty appeal.
    # run_eval.py checks the appeal log, under_review status, original text
    # and both sentence-removal variants, 60/40 model/style weights, majority
    # label, and the corresponding message. Every one of the five must pass.
    {
        'criterion': 4,
        'name': 'Appeal process',
        'target': '5/5 appeals satisfy the recorded process',
        'cases': [text_case(key) for key in [
            'own_1', 'own_2', 'ai_00000113_00', 'ai_00001495_00', 'coverage_1',
        ]],
    },

    # 5. Read GET /log before and after each request. Successful decisions
    # must include the required fields, match the response, and have
    # confidence == combined_score and status == decided. Invalid text must
    # receive a logged 400 rejection; missing/invalid creator IDs must be unknown.
    {
        'criterion': 5,
        'name': 'Complete and accurate audit entries',
        'target': '10/10 requests logged in the required format',
        'cases': [
            # Two scored decisions: one human source and one AI source.
            text_case('own_1'),
            text_case('ai_00000113_00'),
            # Three rejection paths with an ordinary creator ID added by the runner.
            {'id': 'empty_text', 'body': {'text': ''}},
            {'id': 'missing_text', 'body': {}},
            {'id': 'list_text', 'body': {'text': ['not', 'a', 'string']}},
            # Four supplied but invalid creator IDs, plus a missing creator ID.
            {'id': 'null_creator', 'body': {'text': '', 'creator_id': None}},
            {'id': 'empty_creator', 'body': {'text': '', 'creator_id': ''}},
            {'id': 'whitespace_creator', 'body': {'text': '', 'creator_id': '   '}},
            {'id': 'object_creator', 'body': {'text': '', 'creator_id': {'name': 'invalid'}}},
            {'id': 'missing_creator', 'body': {'text': ''}, 'omit_creator': True},
        ],
    },
]


def validate():
    """Reject incomplete coverage before the runner sends any requests."""
    problems = []
    if [s.get('criterion') for s in SCENARIOS] != [1, 2, 3, 4, 5]:
        problems.append('Exactly five criteria, numbered 1 through 5, are required.')
    for scenario, count in zip(SCENARIOS, [5, 10, 5, 5, 10]):
        if len(scenario.get('cases', [])) != count:
            problems.append(f"Criterion {scenario['criterion']} requires {count} cases.")
        ids = [c['id'] for c in scenario['cases']]
        if len(set(ids)) != len(ids):
            problems.append(f"Criterion {scenario['criterion']} has duplicate case IDs.")
        for case in scenario['cases']:
            if not isinstance(case.get('body'), dict):
                problems.append(f"{case['id']}: body must be a dictionary.")
            elif scenario['criterion'] in (1, 2, 3, 4):
                text = case['body'].get('text')
                if not isinstance(text, str) or not text.strip():
                    problems.append(f"{case['id']}: a nonblank sample text is required.")

        if scenario['criterion'] == 1:
            if any(case.get('authorship') != 'human' for case in scenario['cases']):
                problems.append('Criterion 1 requires only human-authored samples.')
            if not set(OWN_WRITING_IDS).issubset(ids):
                problems.append('Criterion 1 must include both pieces of my own writing.')
        elif scenario['criterion'] == 2:
            authors = [case.get('authorship') for case in scenario['cases']]
            if authors.count('human') != 5 or authors.count('ai') != 5:
                problems.append('Criterion 2 requires five human and five AI samples.')
        elif scenario['criterion'] == 3:
            labels = {case.get('expected_label') for case in scenario['cases']}
            if labels != {'human', 'unsure', 'ai'}:
                problems.append('Criterion 3 must cover human, unsure, and AI expected labels.')
    return problems
