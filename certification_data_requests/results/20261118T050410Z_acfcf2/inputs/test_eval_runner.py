"""Verify the evaluation harness cannot silently turn failures into passes."""
import unittest
from unittest.mock import Mock

import run_eval as runner
import scenarios


class EvaluationTests(unittest.TestCase):
    def scored_case(self, label='human', score=.2, **extra):
        return {'id': 'fixture', 'submission': {'status': 200, 'error': None,
                'response': {'label': label, 'combined_score': score}}, **extra}

    def test_five_complete_scenarios(self):
        self.assertEqual(scenarios.validate(), [])
        self.assertEqual(sum(len(s['cases']) for s in scenarios.SCENARIOS), 35)
        self.assertEqual(len(set(scenarios.HUMAN_IDS)), 5)
        self.assertEqual(len(set(scenarios.AI_IDS)), 5)

    def test_rejected_human_is_not_a_successful_false_positive_trial(self):
        cases = [self.scored_case() for _ in range(5)]
        cases[0]['submission'] = {'status': 400, 'response': {'error': 'bad_request'}}
        self.assertEqual(runner.summarize({'criterion': 1}, cases)['verdict'], 'MISSED')

    def test_gap_uses_ai_minus_human_and_requires_five_each(self):
        cases = [self.scored_case(score=.2, authorship='human') for _ in range(5)]
        cases += [self.scored_case('ai', .6, authorship='ai') for _ in range(5)]
        result = runner.summarize({'criterion': 2}, cases)
        self.assertAlmostEqual(result['metrics']['gap'], .4)
        self.assertEqual(result['verdict'], 'MET')
        self.assertEqual(runner.summarize({'criterion': 2}, cases[:-1])['verdict'], 'MISSED')

    def test_labels_require_expected_authorship_and_original_thresholds(self):
        cases = [self.scored_case('unsure', .43, expected_label='unsure') for _ in range(5)]
        result = runner.summarize({'criterion': 3}, cases)
        self.assertEqual(result['metrics']['expected_label_matches'], 5)
        self.assertEqual(result['metrics']['criterion_band_matches'], 0)
        self.assertEqual(result['verdict'], 'MISSED')
        self.assertEqual(runner.criterion_label(.45), 'human')
        self.assertEqual(runner.criterion_label(.60), 'ai')

    def test_non_json_500_retains_real_status_and_body(self):
        session = Mock()
        session.request.return_value.status_code = 500
        session.request.return_value.text = '<html>crash</html>'
        session.request.return_value.json.side_effect = ValueError('not JSON')
        result = runner.request_json(session, 'POST', 'http://local/submit', 5, {})
        self.assertEqual(result['status'], 500)
        self.assertIn('ValueError', result['error'])
        self.assertEqual(result['response_text'], '<html>crash</html>')

    def test_invalid_creator_must_be_unknown_even_when_entry_exists(self):
        for creator in (None, '', '   ', {'name': 'invalid'}):
            record = {'request': {'text': '', 'creator_id': creator}, 'status': 400,
                      'response': {'error': 'bad_request'}}
            entry = {'timestamp': '2026-11-12T00:00:00Z', 'creator_id': creator,
                     'event': 'rejected', 'status': 'rejected', 'reason': 'invalid_text'}
            self.assertFalse(runner.audit_checks(record, [entry])['creator_id'])
            entry['creator_id'] = 'unknown'
            self.assertTrue(all(runner.audit_checks(record, [entry]).values()))
            self.assertFalse(runner.audit_checks(record, [])['one_entry'])
            self.assertFalse(runner.audit_checks(record, [entry, entry])['one_entry'])

    def test_matching_response_with_wrong_confidence_fails(self):
        response = dict(content_id='c_1', guess='human', model_score=.2, style_score=.4,
                        combined_score=.26, confidence=.9, label='human')
        entry = dict(response, timestamp='now', creator_id='writer', status='decided')
        record = {'request': {'creator_id': 'writer'}, 'status': 200, 'response': response}
        checks = runner.audit_checks(record, [entry])
        self.assertTrue(checks['response_matches'])
        self.assertFalse(checks['confidence_matches_combined'])

    def test_appeal_rejects_missing_variants_and_wrong_arithmetic(self):
        evaluations = [{'variant': variant, 'status': 'scored', 'model_score': .2,
                        'style_score': .4, 'combined_score': .28, 'label': 'human'}
                       for variant in ['original', 'without_first_sentence', 'without_last_sentence']]
        result = dict(status='under_review', appeal_id='a_1', label='human',
                      votes={'human': 3, 'unsure': 0, 'ai': 0}, evaluations=evaluations,
                      weights={'model': .6, 'style': .4}, message='Your appeal has been recorded.')
        appeal = {'status': 200, 'response': result, 'request': {'reasoning': 'Review this.'}}
        status = {'status': 200, 'response': {'status': 'under_review'}}
        entries = [{'event': 'appeal', 'status': 'under_review', 'reasoning': 'Review this.'},
                   dict(result, event='appeal_reassessment')]
        self.assertTrue(all(runner.appeal_checks(appeal, status, entries).values()))
        evaluations[0]['combined_score'] = .26
        self.assertFalse(runner.appeal_checks(appeal, status, entries)['scored_with_60_40'])
        evaluations.pop()
        self.assertFalse(runner.appeal_checks(appeal, status, entries)['three_variants'])


if __name__ == '__main__':
    unittest.main()
