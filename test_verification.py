"""Exercise manual verification, reviewer decisions, and certificate persistence."""

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import uuid

from app import app
import audit
import config
import submissions
import verification


class VerificationTests(unittest.TestCase):
    def setUp(self):
        self.directory = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.enterContext(patch.object(config, "LOG_DIR", self.directory))
        self.enterContext(patch.object(config, "AUDIT_LOG", self.directory / "audit.jsonl"))
        self.enterContext(patch.object(config, "SUBMISSIONS_FILE", self.directory / "submissions.jsonl"))
        self.enterContext(patch.object(config, "VERIFIED_HUMAN_CERTIFICATION_LOG",
                                       self.directory / "verified_human_certification_log.jsonl"))
        self.enterContext(patch.dict(app.config, TESTING=True))
        self.automatic = self.enterContext(patch("appeals.reassess", side_effect=AssertionError(
            "Human verification must not run automatic scoring."
        )))
        self.client = app.test_client()
        self.submission = submissions.save_submission(
            "c_verify_test", "original_writer", "This is the original submission used by the test."
        )
        self.original = audit.log_decision(
            "c_verify_test", "original_writer", label="unsure", combined_score=0.5,
        )

    def request(self, **extra):
        return self.client.post("/appeal", json={
            "content_id": "c_verify_test", "review_type": "human_verification",
            "reasoning": "Please review my drafts.",
            "additional_text": "Earlier draft.\n\nI revised the ending.", **extra,
        })

    def review(self, status="certified", **extra):
        return self.client.post("/verification/review", json={
            "content_id": "c_verify_test", "status": status, **extra,
        })

    def certificates(self):
        path = config.VERIFIED_HUMAN_CERTIFICATION_LOG
        return [json.loads(line) for line in path.read_text().splitlines()] if path.exists() else []

    def test_human_request_preserves_evidence_and_cannot_supply_its_own_credential(self):
        response = self.request(creator_id="impostor", credential={"Certificate_id": "fake"},
                                status="certified")
        self.assertEqual(response.status_code, 202)
        body = response.get_json()
        self.assertRegex(body["verification_request_id"], r"^vr_[0-9a-f]{16}$")
        record = audit.entries_for("c_verify_test")[-1]
        self.assertEqual(record["creator_id"], "original_writer")
        self.assertEqual(record["additional_text"], "Earlier draft.\n\nI revised the ending.")
        self.assertEqual(record["status"], "under_review")
        self.assertNotIn("credential", record)
        self.assertEqual(self.certificates(), [])
        current = self.client.get("/content/c_verify_test").get_json()
        self.assertEqual(current["verification_status"], "pending")
        self.assertIsNone(current["credential"])
        self.assertEqual(audit.entries_for("c_verify_test")[0], self.original)
        self.automatic.assert_not_called()

    def test_request_validation_and_unknown_content_do_not_write_records(self):
        original = config.AUDIT_LOG.read_bytes()
        for invalid in (None, "", "  ", [], 7):
            with self.subTest(additional_text=invalid):
                self.assertEqual(self.request(additional_text=invalid).status_code, 400)
        for invalid in (None, "", "manual", [], 7):
            with self.subTest(review_type=invalid):
                self.assertEqual(self.request(review_type=invalid).status_code, 400)
        self.assertEqual(self.request(content_id="c_missing").status_code, 404)
        self.assertEqual(config.AUDIT_LOG.read_bytes(), original)
        self.assertEqual(self.certificates(), [])

    def test_automatic_mode_remains_the_default_and_accepts_explicit_selection(self):
        result = {"label": "unsure", "label_text": "Review requested.", "message": "Recorded.",
                  "votes": {"unsure": 3}, "evaluations": [], "weights": {"model": 0.6, "style": 0.4}}
        with patch("appeals.reassess", return_value=result) as reassess:
            for mode in ({}, {"review_type": "automatic"}):
                response = self.client.post("/appeal", json={
                    "content_id": "c_verify_test", "reasoning": "Please recheck.", **mode,
                })
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.get_json()["review_type"], "automatic")
                self.assertEqual(response.get_json()["status"], "under_review")
            self.assertEqual(reassess.call_count, 2)
            reassess.assert_called_with(self.submission["text"])
        self.assertEqual(self.certificates(), [])

    def test_review_accepts_only_content_id_and_status_without_authentication(self):
        self.request()
        response = self.client.post("/verification/review", json={
            "content_id": "c_verify_test", "status": "certified",
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["status"], "certified")
        self.assertEqual(self.certificates()[0]["reviewer"], "unspecified")
        self.assertEqual(audit.entries_for("c_verify_test")[-1]["status"], "certified")

    def test_certification_has_unique_id_utc_time_and_is_bound_to_the_reviewed_item(self):
        self.request()
        response = self.review(reviewer="Test reviewer", review_notes="Reviewed the test drafts.")
        self.assertEqual(response.status_code, 200)
        body = response.get_json()
        self.assertEqual(body["status"], "certified")
        credential = body["credential"]
        self.assertRegex(credential["Certificate_id"], r"^vh_[0-9a-f]{16}$")
        datetime.strptime(credential["verified_dt_time"], "%Y-%m-%d %H:%M:%S UTC")
        self.assertEqual(credential["type"], "verified_human")
        self.assertEqual(credential["method"], "draft_review")
        certificate = self.certificates()[0]
        self.assertEqual(certificate["creator_id"], "original_writer")
        self.assertEqual(certificate["credential"], credential)
        self.assertEqual(certificate["reviewer"], "Test reviewer")
        audit.log_decision("c_other", "original_writer")
        original = config.AUDIT_LOG.read_bytes()
        current = self.client.get("/content/c_verify_test").get_json()
        self.assertEqual(current["status"], "certified")
        self.assertEqual(current["credential"], credential)
        self.assertIsNone(self.client.get("/content/c_other").get_json()["credential"])
        self.assertEqual(config.AUDIT_LOG.read_bytes(), original)
        self.assertEqual(audit.entries_for("c_verify_test")[0], self.original)

    def test_repeating_decision_preserves_certificate_and_conflicting_decision_is_rejected(self):
        self.request()
        first = self.review().get_json()
        audit_bytes = config.AUDIT_LOG.read_bytes()
        cert_bytes = config.VERIFIED_HUMAN_CERTIFICATION_LOG.read_bytes()
        self.assertEqual(self.review().get_json(), first)
        self.assertEqual(self.review(status="not_certified").status_code, 409)
        self.assertEqual(self.request().status_code, 409)
        self.assertEqual(config.AUDIT_LOG.read_bytes(), audit_bytes)
        self.assertEqual(config.VERIFIED_HUMAN_CERTIFICATION_LOG.read_bytes(), cert_bytes)

    def test_not_certified_has_no_credential_and_allows_a_new_request(self):
        first = self.request().get_json()
        self.assertEqual(self.review(status="not_certified").status_code, 200)
        current = self.client.get("/content/c_verify_test").get_json()
        self.assertEqual(current["status"], "not_certified")
        self.assertEqual(current["verification_status"], "not_certified")
        self.assertIsNone(current["credential"])
        self.assertEqual(self.certificates(), [])
        new = self.request(additional_text="A more complete earlier draft.")
        self.assertEqual(new.status_code, 202)
        self.assertNotEqual(new.get_json()["verification_request_id"], first["verification_request_id"])
        self.assertEqual(self.client.get("/content/c_verify_test").get_json()["status"], "under_review")
        self.assertEqual(self.review().status_code, 200)

    def test_review_requires_a_request_and_valid_status(self):
        original = config.AUDIT_LOG.read_bytes()
        self.assertEqual(self.review().status_code, 409)
        self.assertEqual(self.review(content_id="c_missing").status_code, 404)
        for invalid in (None, "decided", "under_review", [], 7):
            self.assertEqual(self.review(status=invalid).status_code, 400)
        self.assertEqual(self.review(reviewer="  ").status_code, 400)
        self.assertEqual(self.review(review_notes=[]).status_code, 400)
        self.assertEqual(self.review(content_id=[]).status_code, 400)
        response = self.client.post("/verification/review", json=[])
        self.assertEqual(response.status_code, 400)
        self.assertEqual(config.AUDIT_LOG.read_bytes(), original)

    def test_certificate_is_read_from_disk_in_a_new_process(self):
        self.request()
        expected = self.review().get_json()["credential"]
        script = """
import json, sys
from pathlib import Path
import config, verification
config.LOG_DIR = Path(sys.argv[1])
config.AUDIT_LOG = config.LOG_DIR / 'audit.jsonl'
config.VERIFIED_HUMAN_CERTIFICATION_LOG = config.LOG_DIR / 'verified_human_certification_log.jsonl'
print(json.dumps(verification.content_status('c_verify_test')))
"""
        result = subprocess.run([sys.executable, "-B", "-c", script, str(self.directory)],
                                cwd=config.ROOT, capture_output=True, text=True, check=True)
        self.assertEqual(json.loads(result.stdout)["credential"], expected)

    def test_short_uuid_collision_is_regenerated(self):
        self.request()
        old_id = self.review().get_json()["credential"]["Certificate_id"]
        audit.log_decision("c_other", "another_writer")
        submissions.save_submission("c_other", "another_writer", "Another original submission.")
        self.request(content_id="c_other")
        fresh = uuid.uuid4()
        with patch("verification.uuid.uuid4", side_effect=[
            SimpleNamespace(hex=old_id.removeprefix("vh_") + "0" * 16), fresh,
        ]):
            response = self.review(content_id="c_other")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["credential"]["Certificate_id"], "vh_" + fresh.hex[:16])
        self.assertEqual(len(self.certificates()), 2)

    def test_saved_certificate_recovers_if_audit_append_fails(self):
        self.request()
        with patch("audit.log_verification", side_effect=OSError("Simulated audit failure")):
            with self.assertRaises(OSError):
                self.review()
        credential = self.certificates()[0]["credential"]
        self.assertEqual(self.client.get("/content/c_verify_test").get_json()["status"], "certified")
        response = self.review()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["credential"], credential)
        self.assertEqual(len(self.certificates()), 1)
        self.assertEqual(audit.entries_for("c_verify_test")[-1]["status"], "certified")

    def test_concurrent_duplicate_requests_create_only_one_pending_review(self):
        def submit(_):
            try:
                verification.request_review("c_verify_test", "Please review", "Earlier draft")
                return 202
            except verification.VerificationError as exc:
                return exc.status_code
        with ThreadPoolExecutor(max_workers=2) as pool:
            self.assertEqual(sorted(pool.map(submit, range(2))), [202, 409])
        self.assertEqual(len(audit.entries_for("c_verify_test")), 2)

    def test_reviewer_reads_separate_files_and_sees_the_saved_outcome(self):
        submissions.save_submission("c_other", "another_writer", "Unrelated text.")
        submission_bytes = config.SUBMISSIONS_FILE.read_bytes()
        requested = self.request().get_json()
        audit_bytes = config.AUDIT_LOG.read_bytes()
        response = self.client.get("/verification/review/c_verify_test")
        self.assertEqual(response.status_code, 200)
        details = response.get_json()
        self.assertEqual(details["submission"], self.submission)
        self.assertEqual(details["decision"], self.original)
        self.assertEqual(details["verification_request"]["verification_request_id"],
                         requested["verification_request_id"])
        self.assertEqual(details["verification_request"]["additional_text"],
                         "Earlier draft.\n\nI revised the ending.")
        self.assertIsNone(details["review"])
        self.assertEqual(config.AUDIT_LOG.read_bytes(), audit_bytes)
        certified = self.review().get_json()
        details = self.client.get("/verification/review/c_verify_test").get_json()
        self.assertEqual(details["review"]["status"], "certified")
        self.assertEqual(details["review"]["credential"], certified["credential"])
        self.assertEqual(details["review"], self.certificates()[0])
        self.assertEqual(details["submission"], self.submission)
        self.assertEqual(config.SUBMISSIONS_FILE.read_bytes(), submission_bytes)
        self.assertTrue(all("text" not in entry for entry in audit.read_entries()))

    def test_missing_original_cannot_be_certified_but_can_be_declined(self):
        self.request()
        config.SUBMISSIONS_FILE.unlink()
        audit_bytes = config.AUDIT_LOG.read_bytes()
        details = self.client.get("/verification/review/c_verify_test").get_json()
        self.assertIsNone(details["submission"])
        response = self.review()
        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.get_json()["error"], "original_text_unavailable")
        self.assertEqual(config.AUDIT_LOG.read_bytes(), audit_bytes)
        self.assertEqual(self.certificates(), [])
        self.assertEqual(self.review(status="not_certified").status_code, 200)

    def test_human_review_can_load_legacy_original_from_audit(self):
        audit.log_decision("c_legacy", "legacy_writer", text="Legacy original text.")
        self.assertEqual(self.request(content_id="c_legacy").status_code, 202)
        details = self.client.get("/verification/review/c_legacy").get_json()
        self.assertEqual(details["submission"]["text"], "Legacy original text.")
        self.assertEqual(details["submission"]["creator_id"], "legacy_writer")
        self.assertNotIn("text", details["decision"])
        self.assertEqual(self.review(content_id="c_legacy").status_code, 200)

    def test_review_details_require_a_known_item_and_human_request(self):
        audit_bytes = config.AUDIT_LOG.read_bytes()
        self.assertEqual(self.client.get("/verification/review/c_missing").status_code, 404)
        response = self.client.get("/verification/review/c_verify_test")
        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.get_json()["error"], "verification_required")
        self.assertEqual(config.AUDIT_LOG.read_bytes(), audit_bytes)

    def test_changed_submission_creator_blocks_human_review(self):
        self.request()
        altered = {**self.submission, "creator_id": "different_writer"}
        config.SUBMISSIONS_FILE.write_text(json.dumps(altered) + "\n")
        audit_bytes = config.AUDIT_LOG.read_bytes()
        self.assertEqual(self.client.get("/verification/review/c_verify_test").status_code, 409)
        response = self.review()
        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.get_json()["error"], "submission_mismatch")
        self.assertEqual(config.AUDIT_LOG.read_bytes(), audit_bytes)
        self.assertEqual(self.certificates(), [])


if __name__ == "__main__":
    unittest.main()
