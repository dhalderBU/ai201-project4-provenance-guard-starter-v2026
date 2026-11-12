"""Five Unit 7 criteria, fixed inputs, and explicit targets for Unit 8.

Fixtures are frozen in eval_samples/samples.json. Own writing is preserved
verbatim; supplemental HC3 texts retain their dataset labels and provenance.
No scenario is selected by its score in this evaluation.
"""
import json
from pathlib import Path

SAMPLES = {item['id']: item for item in json.loads(
    (Path(__file__).parent / 'eval_samples/samples.json').read_text(encoding='utf-8'))}
HUMAN_IDS = ['own_1', 'own_2', 'human_00000000_02', 'human_00000051_02', 'human_00000362_02']
AI_IDS = ['ai_00000113_00', 'ai_00000318_00', 'ai_00000552_00', 'ai_00001008_00', 'ai_00001495_00']


def text_case(sample_id, expected_label=None):
    sample = SAMPLES[sample_id]
    return {'id': sample_id, 'body': {'text': sample['text']},
            'authorship': sample['label'],
            'expected_label': expected_label or sample['label']}


SCENARIOS = [
    {'criterion': 1, 'name': 'False positive rate', 'target': 'At most 2/5 human pieces labelled AI',
     'cases': [text_case(key) for key in HUMAN_IDS]},
    {'criterion': 2, 'name': 'AI minus human mean score', 'target': 'Mean gap >= 0.30 (5 AI + 5 human)',
     'cases': [text_case(key) for key in HUMAN_IDS + AI_IDS]},
    {'criterion': 3, 'name': 'Correct labels', 'target': 'At least 4/5 correct labels',
     'cases': [text_case(key) for key in ['own_1', 'coverage_1', 'coverage_2', 'coverage_3', 'demo_ai']]},
    {'criterion': 4, 'name': 'Appeal process', 'target': '5/5 appeals satisfy the recorded process',
     'cases': [text_case(key) for key in ['own_1', 'own_2', 'ai_00000113_00', 'ai_00001495_00', 'coverage_1']]},
    {'criterion': 5, 'name': 'Complete and accurate audit entries', 'target': '10/10 requests logged in the required format',
     'cases': [
         text_case('own_1'), text_case('ai_00000113_00'),
         {'id': 'empty_text', 'body': {'text': ''}},
         {'id': 'missing_text', 'body': {}},
         {'id': 'list_text', 'body': {'text': ['not', 'a', 'string']}},
         {'id': 'null_creator', 'body': {'text': '', 'creator_id': None}},
         {'id': 'empty_creator', 'body': {'text': '', 'creator_id': ''}},
         {'id': 'whitespace_creator', 'body': {'text': '', 'creator_id': '   '}},
         {'id': 'object_creator', 'body': {'text': '', 'creator_id': {'name': 'invalid'}}},
         {'id': 'missing_creator', 'body': {'text': ''}, 'omit_creator': True},
     ]},
]


def validate():
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
    return problems
