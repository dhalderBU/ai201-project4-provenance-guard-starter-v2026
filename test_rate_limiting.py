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
    def test_week8_limiter_is_enabled_even_with_a_stale_environment_override(self):
        for value in (None, "0", "1"):
            with self.subTest(value=value), patch.dict(os.environ):
                if value is None:
                    os.environ.pop("AI201_RATE_LIMITS", None)
                else:
                    os.environ["AI201_RATE_LIMITS"] = value
                settings = runpy.run_path(str(Path(__file__).with_name("config.py")))
                self.assertIs(settings["RATE_LIMITING_ENABLED"], True)


class RateLimitTests(unittest.TestCase):
    def setUp(self):
        self.now = self.enterContext(patch("time.time", return_value=2_000_000_000.0))
        self.model = self.enterContext(patch("detector.model_signal", return_value=0.5))
        self.enterContext(patch("binoculars_signal.binoculars_signal", return_value=0.5))
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
            http_status=429,
            ip_address="127.0.0.1",
            rate_limit_key="127.0.0.1",
            rate_limit_key_type="ip_address",
        )

        self.now.return_value += 61
        self.assertEqual(self.submit(client).status_code, 200)

    def test_daily_ip_limit_survives_creator_changes_and_minute_resets(self):
        client = self.client()
        for index in range(config.RATE_LIMIT_PER_DAY):
            if index and index % config.RATE_LIMIT_PER_MINUTE == 0:
                self.now.return_value += 61
            self.assertEqual(self.submit(client, creator=f"writer-{index}").status_code, 200)

        self.now.return_value += 61
        response = self.submit(client)
        self.assertEqual(response.status_code, 429)
        self.assertIn("day", response.get_json()["limit"])
        self.assertGreater(int(response.headers["Retry-After"]), 60)
        self.assertEqual(self.model.call_count, config.RATE_LIMIT_PER_DAY)
        self.assertEqual(self.rejections.call_args.kwargs["rate_limit_key_type"], "ip_address")

        self.now.return_value = 2_000_000_000.0 + 86401
        self.assertEqual(self.submit(client).status_code, 200)

    def test_disabled_limiter_allows_more_than_daily_limit(self):
        client = self.client(enabled=False)
        for _ in range(config.RATE_LIMIT_PER_DAY + 1):
            self.assertEqual(self.submit(client).status_code, 200)
        self.rejections.assert_not_called()

    def test_new_creator_on_exhausted_ip_is_blocked_but_other_ip_has_capacity(self):
        client = self.client()
        for _ in range(config.RATE_LIMIT_PER_MINUTE):
            self.assertEqual(self.submit(client, creator="writer-a").status_code, 200)
        self.assertEqual(self.submit(client, creator="writer-a").status_code, 429)
        self.assertEqual(self.submit(client, creator="writer-b").status_code, 429)
        self.assertEqual(self.rejections.call_args.kwargs["rate_limit_key_type"], "ip_address")
        self.assertEqual(self.submit(client, creator="writer-b", address="192.0.2.1").status_code, 200)

    def test_rotating_creators_cannot_bypass_the_minute_ip_limit(self):
        client = self.client()
        for index in range(config.RATE_LIMIT_PER_MINUTE):
            self.assertEqual(self.submit(client, creator=f"writer-{index}").status_code, 200)
        self.assertEqual(self.submit(client, creator="another-writer").status_code, 429)
        self.assertEqual(self.rejections.call_args.kwargs["rate_limit_key_type"], "ip_address")
        self.assertEqual(self.rejections.call_args.kwargs["rate_limit_key"], "127.0.0.1")
        self.assertEqual(self.model.call_count, config.RATE_LIMIT_PER_MINUTE)

    def test_creator_limit_still_applies_across_different_ips(self):
        client = self.client()
        for index in range(config.RATE_LIMIT_PER_MINUTE):
            self.assertEqual(self.submit(client, address=f"192.0.2.{index + 1}").status_code, 200)
        self.assertEqual(self.submit(client, address="192.0.2.100").status_code, 429)
        self.assertEqual(self.rejections.call_args.kwargs["rate_limit_key_type"], "creator_id")
        self.assertEqual(self.rejections.call_args.kwargs["rate_limit_key"], "writer")
        self.assertEqual(self.submit(client, creator="other-writer", address="192.0.2.100").status_code, 200)

    def test_daily_creator_limit_applies_across_ips_and_minute_resets(self):
        client = self.client()
        for index in range(config.RATE_LIMIT_PER_DAY):
            if index and index % config.RATE_LIMIT_PER_MINUTE == 0:
                self.now.return_value += 61
            self.assertEqual(self.submit(client, address=f"2001:db8::{index + 1:x}").status_code, 200)
        self.now.return_value += 61
        response = self.submit(client, address="2001:db8::ffff")
        self.assertEqual(response.status_code, 429)
        self.assertIn("day", response.get_json()["limit"])
        self.assertEqual(self.rejections.call_args.kwargs["rate_limit_key_type"], "creator_id")
        self.now.return_value = 2_000_000_000.0 + 86401
        self.assertEqual(self.submit(client).status_code, 200)

    def test_creator_named_like_ip_does_not_double_count_the_same_bucket(self):
        client = self.client()
        for _ in range(config.RATE_LIMIT_PER_MINUTE):
            self.assertEqual(self.submit(client, creator="127.0.0.1").status_code, 200)
        self.assertEqual(self.submit(client, creator="127.0.0.1").status_code, 429)

    def test_missing_or_invalid_creator_uses_ip_address(self):
        client = self.client()
        for index in range(config.RATE_LIMIT_PER_MINUTE):
            creator = (None, "", "   ", 123, ["writer"])[index % 5]
            self.assertEqual(self.submit(client, creator=creator).status_code, 200)
        self.assertEqual(self.submit(client, creator=None).status_code, 429)
        self.assertEqual(self.rejections.call_args.kwargs["ip_address"], "127.0.0.1")
        self.assertEqual(self.rejections.call_args.kwargs["rate_limit_key"], "127.0.0.1")
        self.assertEqual(self.rejections.call_args.kwargs["rate_limit_key_type"], "ip_address")
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
        self.assertEqual(self.rejections.call_count, config.RATE_LIMIT_PER_MINUTE + 1)
        self.assertEqual(self.rejections.call_args.kwargs["reason"], "rate_limited")

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
