"""Check the evaluator does not count incomplete or incorrect evidence as a pass."""
import copy
import json
import tempfile
from pathlib import Path
import unittest
from unittest.mock import Mock, patch

from certification_data_requests import run_tests as runner


class RunnerTests(unittest.TestCase):
    def test_manifest_has_five_cases_for_each_of_five_criteria(self):
        fixtures, specs = runner.validate_pack()
        self.assertEqual(len(fixtures), 5)
        self.assertEqual([len(s['case_specs']) for s in specs], [5] * 5)
        failure_requests = [len(c['requests']) for c in specs[3]['case_specs']]
        self.assertEqual(failure_requests, [5, 2, 2, 3, 1])

    def test_empty_case_and_truthy_integer_do_not_pass(self):
        case = {'checks': {}}
        self.assertFalse(runner.case_passed(case))
        runner.checked(case, 'verified', 1, True)
        self.assertFalse(runner.case_passed(case))

    def test_http_200_with_wrong_verification_result_fails(self):
        sandbox = Mock()
        sandbox.request.return_value = {'curl_exit_code': 0, 'http_status': 200,
                                        'response': {'verified': False, 'status': 'verified'}}
        case = {'id': 'example', 'checks': {}}
        request = runner.read(runner.PACK / 'criterion_07/case_01.json')['requests'][0]
        runner.check_request(sandbox, case, request, '_check')
        self.assertFalse(runner.case_passed(case))

    def test_transport_error_cannot_pass_even_with_expected_response(self):
        sandbox = Mock()
        sandbox.request.return_value = {'curl_exit_code': 28, 'http_status': 200,
                                        'response': {'verified': True, 'status': 'verified'}}
        case = {'id': 'example', 'checks': {}}
        request = runner.read(runner.PACK / 'criterion_07/case_01.json')['requests'][0]
        runner.check_request(sandbox, case, request, '_check')
        self.assertFalse(runner.case_passed(case))

    def test_missing_trial_cannot_be_reported_passed(self):
        _, specs = runner.validate_pack()
        cases = [{'id': str(i), 'checks': {'check': {'passed': True}}} for i in range(5)]
        trials = [{'criterion': 6, 'run': 1, 'cases': cases}]
        with tempfile.TemporaryDirectory() as directory:
            runner.write_report(specs, trials, Path(directory))
            report = (Path(directory) / 'report.md').read_text()
        self.assertNotIn('**PASSED**', report)
        self.assertIn('| 5/5 | NOT RUN | NOT RUN | **INCOMPLETE** |', report)

    def test_one_failed_inner_check_counts_as_one_failed_case(self):
        _, specs = runner.validate_pack()
        trials = []
        for run in (1, 2, 3):
            cases = [{'id': str(i), 'checks': {'a': {'passed': True}}} for i in range(5)]
            if run == 2:
                cases[3]['checks']['another_request_failed'] = {'passed': False}
            trials.append({'criterion': 9, 'run': run, 'cases': cases})
        with tempfile.TemporaryDirectory() as directory:
            runner.write_report(specs, trials, Path(directory))
            report = (Path(directory) / 'report.md').read_text()
        self.assertIn('| 5/5 | 4/5 | 5/5 | **MISSED** |', report)
        self.assertIn('another_request_failed', report)

    def test_restart_record_change_fails_only_affected_case_without_retrying_approvals(self):
        fixtures, specs = runner.validate_pack()
        spec = specs[-1]
        seeds = {f['id']: {'content_id': f'c_{i}', 'request_id': f'vr_{i}'}
                 for i, f in enumerate(fixtures)}
        original = [{'event': 'human_verification_review',
                     'verification_request_id': seed['request_id'],
                     'content_id': seed['content_id'], 'credential': {'content_hash': 'original'}}
                    for seed in seeds.values()]
        damaged = copy.deepcopy(original)
        damaged[2]['credential']['content_hash'] = 'changed'
        def snapshot(certificates):
            return {runner.CERT_FILE: ''.join(json.dumps(r) + '\n' for r in certificates),
                    'audit.jsonl': ''.join(json.dumps(r) + '\n' for r in original),
                    'submissions.jsonl': ''}
        sandbox = Mock()
        sandbox.snapshot.side_effect = [snapshot(original), snapshot(damaged)]
        sandbox.history = [{'container_id': 'before'}, {'container_id': 'after'}]
        def response(endpoint, body, tag):
            verified = tag.endswith('_1')
            return {'curl_exit_code': 0, 'http_status': 200, 'response': {
                'verified': verified, 'status': 'verified' if verified else 'content_mismatch'}}
        sandbox.request.side_effect = response
        cases = [{'id': c['id'], 'checks': {}} for c in spec['case_specs']]
        with patch.object(runner, 'certify', side_effect=lambda sandbox, fixture, tag: seeds[fixture['id']]):
            runner.evaluate(sandbox, spec, fixtures, cases)
        self.assertEqual([runner.case_passed(c) for c in cases], [True, True, False, True, True])
        self.assertEqual(sandbox.request.call_count, 10)
        self.assertTrue(all(call.args[0] == '/verification/verify' for call in sandbox.request.call_args_list))
        sandbox.replace.assert_called_once()


if __name__ == '__main__':
    unittest.main()
