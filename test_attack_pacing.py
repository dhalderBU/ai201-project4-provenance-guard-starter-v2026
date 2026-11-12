"""Check that normal inputs reach the route while the flood remains a burst."""

import contextlib
import io
import unittest

from run_paced_attacks import AttackPacer


class AttackPacingTests(unittest.TestCase):
    def setUp(self):
        self.now = 0.0
        self.sleeps = []
        self.pacer = AttackPacer(9, clock=lambda: self.now, sleep=self.sleep)
        self.enterContext(contextlib.redirect_stdout(io.StringIO()))

    def sleep(self, seconds):
        self.sleeps.append(seconds)
        self.now += seconds

    def test_normal_tenth_request_waits_for_new_minute(self):
        for _ in range(9):
            self.assertEqual(self.pacer.before_request("evasion"), 0)
        self.assertEqual(self.pacer.before_request("false_positive"), 61)
        self.assertEqual(self.now, 61)
        self.assertEqual(self.pacer.count, 1)
        self.assertTrue(all(seconds <= 30 for seconds in self.sleeps))

    def test_flood_starts_fresh_then_all_twelve_rows_run_without_delay(self):
        self.pacer.before_request("malformed")
        self.now = 10
        self.assertEqual(self.pacer.before_request("flood_same_creator"), 51)
        for _ in range(11):
            self.assertEqual(self.pacer.before_request("flood_same_creator"), 0)
        self.assertEqual(self.pacer.count, 12)
        self.assertEqual(self.now, 61)

    def test_elapsed_time_does_not_add_an_unnecessary_wait(self):
        for _ in range(9):
            self.pacer.before_request("malformed")
        self.now = 70
        self.assertEqual(self.pacer.before_request("evasion"), 0)
        self.assertEqual(self.sleeps, [])
        self.assertEqual(self.pacer.count, 1)


if __name__ == "__main__":
    unittest.main()
