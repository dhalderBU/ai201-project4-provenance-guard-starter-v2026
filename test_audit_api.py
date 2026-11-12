"""Verify persisted submission decisions and rejections through GET /log."""

from datetime import datetime
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import config
import detector
from run_attacks import FLOOD_TEXT
import stylometry


REQUIRED_FIELDS = {
    "timestamp", "content_id", "creator_id", "guess", "model_score",
    "style_score", "combined_score", "label", "status",
}


class AuditApiTests(unittest.TestCase):
    def setUp(self):
        root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.enterContext(patch.object(config, "LOG_DIR", root))
        self.enterContext(patch.object(config, "AUDIT_LOG", root / "audit.jsonl"))
        self.enterContext(patch.object(config, "SUBMISSIONS_FILE", root / "submissions.jsonl"))
        self.enterContext(patch.object(config, "RATE_LIMITING_ENABLED", True))
        self.model = self.enterContext(patch("detector.model_signal", return_value=0.8))
        self.binoculars = self.enterContext(patch("binoculars_signal.binoculars_signal", return_value=0.6))
        self.style = self.enterContext(patch("stylometry.style_signal", return_value=0.4))
        spec = importlib.util.spec_from_file_location(
            "audit_test_app", Path(__file__).with_name("app.py")
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        module.app.testing = True
        self.client = module.app.test_client()

    def entries(self):
        response = self.client.get("/log")
        self.assertEqual(response.status_code, 200)
        body = response.get_json()
        disk = [json.loads(line) for line in config.AUDIT_LOG.read_text().splitlines()]
        self.assertEqual(body, {"count": len(disk), "entries": disk})
        for entry in disk:
            self.assertTrue(REQUIRED_FIELDS <= entry.keys())
            self.assertIsNotNone(datetime.fromisoformat(entry["timestamp"]).tzinfo)
        return body["entries"]

    def test_three_decisions_round_trip_with_scores_labels_and_current_status(self):
        responses = []
        for index in range(3):
            response = self.client.post("/submit", json={
                "creator_id": "audit_writer", "text": FLOOD_TEXT + f" Draft {index}.",
            })
            self.assertEqual(response.status_code, 200)
            responses.append(response.get_json())
        entries = self.entries()
        self.assertEqual(len(entries), 3)
        for body, entry in zip(responses, entries):
            for field in ("content_id", "guess", "model_score", "style_score", "combined_score", "label"):
                self.assertEqual(entry[field], body[field])
            self.assertEqual(entry["creator_id"], "audit_writer")
            self.assertEqual(entry["status"], "decided")
            status = self.client.get(f"/content/{body['content_id']}").get_json()
            self.assertEqual(status["status"], entry["status"])
        self.assertEqual(self.client.get("/log?limit=2").get_json()["entries"], entries[-2:])
        self.assertEqual(
            self.client.get("/log", query_string={"content_id": entries[0]["content_id"]}).get_json()["entries"],
            entries[:1],
        )

    def test_invalid_json_and_non_objects_are_logged_before_scoring(self):
        for raw in ("{", "", "[]", '"text"', "null", "123"):
            response = self.client.post("/submit", data=raw, content_type="application/json")
            self.assertEqual(response.status_code, 400)
        entries = self.entries()
        self.assertEqual(len(entries), 6)
        for entry in entries:
            self.assertEqual(entry["reason"], "invalid_json_object")
            self.assertEqual(entry["creator_id"], "unknown")
            self.assertEqual(entry["http_status"], 400)
            for field in ("content_id", "guess", "model_score", "style_score", "combined_score", "label"):
                self.assertIsNone(entry[field])
        self.model.assert_not_called()
        self.assertFalse(config.SUBMISSIONS_FILE.exists())

    def test_missing_empty_or_non_string_text_is_logged(self):
        bodies = [{}, {"text": None}, {"text": ""}, {"text": "  "}, {"text": 12}, {"text": []}]
        for body in bodies:
            response = self.client.post("/submit", json={"creator_id": "invalid_text_writer", **body})
            self.assertEqual(response.status_code, 400)
        entries = self.entries()
        self.assertEqual(len(entries), len(bodies))
        for entry in entries:
            self.assertEqual(entry["reason"], "missing_or_invalid_text")
            self.assertEqual(entry["creator_id"], "invalid_text_writer")
            self.assertEqual(entry["status"], "rejected")
        self.model.assert_not_called()

    def test_insufficient_inputs_record_the_stage_and_any_available_score(self):
        self.model.side_effect = detector.TextTooShortError("Too few model tokens.")
        first = self.client.post("/submit", json={"text": "Hi", "creator_id": "model_short"})
        self.assertEqual(first.status_code, 400)
        self.model.side_effect = None
        self.style.side_effect = stylometry.TextTooShortError("Too few style sentences.")
        second = self.client.post("/submit", json={"text": FLOOD_TEXT, "creator_id": "style_short"})
        self.assertEqual(second.status_code, 400)
        first, second = self.entries()
        self.assertEqual(first["reason"], "insufficient_model_input")
        self.assertIsNone(first["model_score"])
        self.assertEqual(second["reason"], "insufficient_style_input")
        self.assertEqual(second["model_score"], 0.8)
        self.assertIsNone(second["combined_score"])
        self.assertFalse(config.SUBMISSIONS_FILE.exists())

    def test_flood_logs_each_decision_and_each_rejection_without_extra_inference(self):
        responses = [self.client.post("/submit", json={
            "text": FLOOD_TEXT, "creator_id": "audit_flood",
        }) for _ in range(15)]
        self.assertEqual([response.status_code for response in responses], [200] * 9 + [429] * 6)
        entries = self.entries()
        self.assertEqual(len(entries), 15)
        self.assertEqual([entry["status"] for entry in entries], ["decided"] * 9 + ["rejected"] * 6)
        for entry in entries[9:]:
            self.assertEqual(entry["reason"], "rate_limited")
            self.assertEqual(entry["http_status"], 429)
            self.assertIsNone(entry["model_score"])
            self.assertEqual(entry["ip_address"], "127.0.0.1")
            self.assertEqual(entry["rate_limit_key"], "127.0.0.1")
            self.assertEqual(entry["rate_limit_key_type"], "ip_address")
        self.assertEqual(self.model.call_count, 9)
        self.assertEqual(self.binoculars.call_count, 9)
        self.assertEqual(self.style.call_count, 9)

    def test_ip_limit_is_persisted_for_invalid_creators_and_malformed_bodies(self):
        bodies = [
            {"text": FLOOD_TEXT},
            *({"text": FLOOD_TEXT, "creator_id": creator}
              for creator in (None, "", "   ", 123, ["writer"])),
            ["not an object"],
            "{",
        ]
        for index, body in enumerate(bodies, 1):
            address = f"192.0.2.{index}"
            with self.subTest(body=body):
                options = {
                    "environ_overrides": {"REMOTE_ADDR": address},
                    "headers": {"X-Forwarded-For": "203.0.113.99"},
                }
                if isinstance(body, str):
                    options.update(data=body, content_type="application/json")
                else:
                    options["json"] = body
                expected = 200 if isinstance(body, dict) else 400
                for _ in range(config.RATE_LIMIT_PER_MINUTE):
                    self.assertEqual(self.client.post("/submit", **options).status_code, expected)
                self.assertEqual(self.client.post("/submit", **options).status_code, 429)
                entry = self.entries()[-1]
                self.assertEqual(entry["reason"], "rate_limited")
                self.assertEqual(entry["ip_address"], address)
                self.assertEqual(entry["rate_limit_key"], address)
                self.assertEqual(entry["rate_limit_key_type"], "ip_address")

    def test_creator_breach_is_logged_when_ip_still_has_capacity(self):
        for index in range(config.RATE_LIMIT_PER_MINUTE):
            response = self.client.post("/submit", json={
                "text": FLOOD_TEXT, "creator_id": "travelling_writer",
            }, environ_overrides={"REMOTE_ADDR": f"192.0.2.{index + 1}"})
            self.assertEqual(response.status_code, 200)
        response = self.client.post("/submit", json={
            "text": FLOOD_TEXT, "creator_id": "travelling_writer",
        }, environ_overrides={"REMOTE_ADDR": "192.0.2.100"})
        self.assertEqual(response.status_code, 429)
        entry = self.entries()[-1]
        self.assertEqual(entry["creator_id"], "travelling_writer")
        self.assertEqual(entry["ip_address"], "192.0.2.100")
        self.assertEqual(entry["rate_limit_key"], "travelling_writer")
        self.assertEqual(entry["rate_limit_key_type"], "creator_id")

    def test_unavailable_detector_leaves_evidence_without_changing_error_behavior(self):
        self.model.side_effect = detector.DetectorUnavailable("Model unavailable for this test.")
        with self.assertRaises(detector.DetectorUnavailable):
            self.client.post("/submit", json={"text": FLOOD_TEXT, "creator_id": "unavailable_test"})
        entry, = self.entries()
        self.assertEqual(entry["reason"], "detector_unavailable")
        self.assertEqual(entry["http_status"], 500)
        self.assertIsNone(entry["combined_score"])


class FloodFixtureTests(unittest.TestCase):
    def test_flood_text_meets_existing_style_requirements(self):
        self.assertGreaterEqual(len(stylometry.sentences(FLOOD_TEXT)), stylometry.MIN_STYLE_SENTENCES)
        self.assertGreaterEqual(len(stylometry.words(FLOOD_TEXT)), stylometry.MIN_STYLE_WORDS)


if __name__ == "__main__":
    unittest.main()
