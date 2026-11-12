"""Exercise submission rate limits without model inference or audit file writes."""

import importlib.util
import os
from pathlib import Path
import runpy
import sys
import unittest
from unittest.mock import patch

import config


class RateLimitConfigTests(unittest.TestCase):
    def test_environment_switch_matches_documented_default_and_overrides(self):
        for value, expected in ((None, True), ("0", False), ("1", True)):
            with self.subTest(value=value), patch.dict(os.environ):
                if value is None:
                    os.environ.pop("AI201_RATE_LIMITS", None)
                else:
                    os.environ["AI201_RATE_LIMITS"] = value
                settings = runpy.run_path(str(Path(__file__).with_name("config.py")))
                self.assertIs(settings["RATE_LIMITING_ENABLED"], expected)


class RateLimitTests(unittest.TestCase):
    def setUp(self):
        self.now = self.enterContext(patch("time.time", return_value=2_000_000_000.0))
        self.model = self.enterContext(patch("detector.model_signal", return_value=0.5))
        self.style = self.enterContext(patch("stylometry.style_signal", return_value=0.5))
        self.decisions = self.enterContext(patch("audit.log_decision"))
        self.enterContext(patch("submissions.save_submission"))
        self.rejections = self.enterContext(patch("audit.log_rejection"))

    def client(self, enabled=True):
        # Each test gets fresh Flask routes and in-memory counters, without
        # reloading the app module used by the other API tests.
        name = "rate_limit_test_app"
        spec = importlib.util.spec_from_file_location(
            name, Path(__file__).with_name("app.py")
        )
        module = importlib.util.module_from_spec(spec)
        with patch.object(config, "RATE_LIMITING_ENABLED", enabled), patch.dict(
            sys.modules, {name: module}
        ):
            spec.loader.exec_module(module)
        module.app.testing = True
        return module.app.test_client()

    def submit(self, client, creator="writer", address="127.0.0.1"):
        payload = {"text": "Example submission; model and style scoring are mocked."}
        if creator is not None:
            payload["creator_id"] = creator
        return client.post(
            "/submit", json=payload, environ_overrides={"REMOTE_ADDR": address}
        )

    def test_exceeding_minute_limit_returns_json_429_and_logs_rejection(self):
        client = self.client()
        for _ in range(config.RATE_LIMIT_PER_MINUTE):
            self.assertEqual(self.submit(client).status_code, 200)

        response = self.submit(client)
        self.assertEqual(response.status_code, 429)
        self.assertEqual(response.get_json()["error"], "rate_limited")
        self.assertIn("minute", response.get_json()["limit"])
        self.assertGreater(int(response.headers["Retry-After"]), 0)
        self.assertEqual(self.model.call_count, config.RATE_LIMIT_PER_MINUTE)
        self.assertEqual(self.style.call_count, config.RATE_LIMIT_PER_MINUTE)
        self.assertEqual(self.decisions.call_count, config.RATE_LIMIT_PER_MINUTE)
        self.rejections.assert_called_once_with(
            creator_id="writer",
            reason="rate_limited",
            limit=response.get_json()["limit"],
        )

        self.now.return_value += 61
        self.assertEqual(self.submit(client).status_code, 200)

    def test_daily_limit_survives_minute_resets_and_expires(self):
        client = self.client()
        for index in range(config.RATE_LIMIT_PER_DAY):
            if index and index % config.RATE_LIMIT_PER_MINUTE == 0:
                self.now.return_value += 61
            self.assertEqual(self.submit(client).status_code, 200)

        self.now.return_value += 61
        response = self.submit(client)
        self.assertEqual(response.status_code, 429)
        self.assertIn("day", response.get_json()["limit"])
        self.assertGreater(int(response.headers["Retry-After"]), 60)
        self.assertEqual(self.model.call_count, config.RATE_LIMIT_PER_DAY)

        self.now.return_value = 2_000_000_000.0 + 86401
        self.assertEqual(self.submit(client).status_code, 200)

    def test_disabled_limiter_allows_more_than_daily_limit(self):
        client = self.client(enabled=False)
        for _ in range(config.RATE_LIMIT_PER_DAY + 1):
            self.assertEqual(self.submit(client).status_code, 200)
        self.rejections.assert_not_called()

    def test_creator_ids_have_separate_allowances(self):
        client = self.client()
        for _ in range(config.RATE_LIMIT_PER_MINUTE):
            self.assertEqual(self.submit(client, creator="writer-a").status_code, 200)
        self.assertEqual(self.submit(client, creator="writer-a").status_code, 429)
        self.assertEqual(self.submit(client, creator="writer-b").status_code, 200)

    def test_missing_or_invalid_creator_uses_ip_address(self):
        client = self.client()
        for index in range(config.RATE_LIMIT_PER_MINUTE):
            creator = (None, "", "   ", 123, ["writer"])[index % 5]
            self.assertEqual(self.submit(client, creator=creator).status_code, 200)
        self.assertEqual(self.submit(client, creator=None).status_code, 429)
        self.assertEqual(
            self.submit(client, creator=None, address="192.0.2.1").status_code, 200
        )

    def test_malformed_requests_count_without_crashing(self):
        client = self.client()
        for index in range(config.RATE_LIMIT_PER_MINUTE):
            if index % 2:
                response = client.post("/submit", data="{", content_type="application/json")
            else:
                response = client.post("/submit", json=["not an object"])
            self.assertEqual(response.status_code, 400)
        response = client.post("/submit", json=["not an object"])
        self.assertEqual(response.status_code, 429)
        self.assertEqual(response.get_json()["error"], "rate_limited")
        self.model.assert_not_called()
        self.decisions.assert_not_called()
        self.rejections.assert_called_once()

    def test_ping_does_not_consume_submission_allowance(self):
        client = self.client()
        for _ in range(config.RATE_LIMIT_PER_MINUTE + 1):
            self.assertEqual(client.post("/ping", json={}).status_code, 200)
        for _ in range(config.RATE_LIMIT_PER_MINUTE):
            self.assertEqual(self.submit(client).status_code, 200)
        self.assertEqual(self.submit(client).status_code, 429)
        self.assertEqual(client.post("/ping", json={}).status_code, 200)


if __name__ == "__main__":
    unittest.main()
