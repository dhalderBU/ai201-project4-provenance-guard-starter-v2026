"""Check content status lookup across decisions, appeals, and unknown IDs."""

from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from app import app
import audit
import config


class ContentTests(unittest.TestCase):
    def setUp(self):
        directory = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.enterContext(patch.object(config, "LOG_DIR", directory))
        self.enterContext(patch.object(config, "AUDIT_LOG", directory / "audit.jsonl"))
        self.enterContext(patch.object(config, "SUBMISSIONS_FILE", directory / "submissions.jsonl"))
        self.enterContext(patch.object(config, "VERIFIED_HUMAN_CERTIFICATION_LOG",
                                       directory / "verified_human_certification_log.jsonl"))
        self.client = app.test_client()

    def test_decided_item_returns_status_without_changing_the_log(self):
        audit.log_decision("c_content_test", "writer", label="ai", text="Saved text.")
        original = config.AUDIT_LOG.read_bytes()

        response = self.client.get("/content/c_content_test")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {
            "content_id": "c_content_test",
            "status": "decided",
            "credential": None,
        })
        self.assertEqual(config.AUDIT_LOG.read_bytes(), original)

    def test_appeal_changes_current_status_even_with_same_timestamp_and_other_items(self):
        # A legacy decision without saved text can still be appealed for review.
        with patch("audit._now", return_value="2026-11-11T12:00:00+00:00"):
            decision = audit.log_decision("c_content_test", "writer", label="ai")
            before = self.client.get("/content/c_content_test")
            self.assertEqual(before.get_json()["status"], "decided")

            appealed = self.client.post("/appeal", json={
                "content_id": "c_content_test",
                "reasoning": "Please review my original writing.",
            })
            self.assertEqual(appealed.status_code, 200)
            audit.log_decision("c_other", "other_writer")

        original = config.AUDIT_LOG.read_bytes()
        response = self.client.get("/content/c_content_test")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {
            "content_id": "c_content_test",
            "status": "under_review",
            "credential": None,
        })
        self.assertEqual(audit.entries_for("c_content_test")[0], decision)
        self.assertEqual(config.AUDIT_LOG.read_bytes(), original)

    def test_unknown_id_returns_json_404_without_creating_or_changing_records(self):
        for has_other_item in (False, True):
            with self.subTest(has_other_item=has_other_item):
                if has_other_item:
                    audit.log_decision("c_other", "other_writer")
                original = config.AUDIT_LOG.read_bytes() if config.AUDIT_LOG.exists() else None

                response = self.client.get("/content/c_missing")

                self.assertEqual(response.status_code, 404)
                self.assertEqual(response.get_json(), {
                    "error": "not_found",
                    "message": "No submission exists for that content_id.",
                })
                if original is None:
                    self.assertFalse(config.AUDIT_LOG.exists())
                else:
                    self.assertEqual(config.AUDIT_LOG.read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
