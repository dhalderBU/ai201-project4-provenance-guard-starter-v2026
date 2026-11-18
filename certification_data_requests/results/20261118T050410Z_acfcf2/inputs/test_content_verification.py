"""Verify exact content binding, legacy behavior, and persisted certificate lookup."""

import copy
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from app import app
import audit
import config
import submissions
import verification


class ContentVerificationTests(unittest.TestCase):
    def setUp(self):
        self.directory = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.enterContext(patch.object(config, "LOG_DIR", self.directory))
        self.enterContext(patch.object(config, "AUDIT_LOG", self.directory / "audit.jsonl"))
        self.enterContext(patch.object(config, "SUBMISSIONS_FILE", self.directory / "submissions.jsonl"))
        self.enterContext(patch.object(config, "VERIFIED_HUMAN_CERTIFICATION_LOG",
                                       self.directory / "certificates.jsonl"))
        self.enterContext(patch.dict(app.config, TESTING=True))
        for target in ("detector._load", "binoculars_signal._load_performer", "appeals.reassess"):
            self.enterContext(patch(target, side_effect=AssertionError(
                "Certification and hash verification must not run model inference."
            )))
        self.client = app.test_client()
        self.text = "  My café draft.\nA second line with 日本語 and an emoji 🐈.\n"

    def certify(self, text=None, content_id="c_hash_test"):
        text = self.text if text is None else text
        submissions.save_submission(content_id, "writer", text)
        audit.log_decision(content_id, "writer", label="unsure", combined_score=0.5)
        requested = self.client.post("/appeal", json={
            "content_id": content_id, "review_type": "human_verification",
            "reasoning": "Please review this draft.", "additional_text": "Earlier supporting draft.",
        })
        self.assertEqual(requested.status_code, 202)
        reviewed = self.client.post("/verification/review", json={
            "content_id": content_id, "status": "certified", "reviewer": "Test reviewer",
        })
        self.assertEqual(reviewed.status_code, 200)
        return reviewed.get_json()["credential"]

    def verify(self, certificate_id, text=None):
        return self.client.post("/verification/verify", json={
            "certificate_id": certificate_id, "text": self.text if text is None else text,
        })

    def records(self):
        return [json.loads(line) for line in config.VERIFIED_HUMAN_CERTIFICATION_LOG.read_text().splitlines()]

    def save_records(self, records):
        config.VERIFIED_HUMAN_CERTIFICATION_LOG.write_text(
            "".join(json.dumps(record) + "\n" for record in records), encoding="utf-8"
        )

    def test_sha256_known_vector_is_saved_in_certificate_and_audit(self):
        credential = self.certify("abc")
        self.assertEqual(credential["hash_algorithm"], "sha256")
        self.assertEqual(credential["content_hash"],
                         "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad")
        self.assertEqual(credential["Certificate_id"], "f20015ad")
        self.assertEqual(self.records()[0]["credential"], credential)
        self.assertEqual(audit.entries_for("c_hash_test")[-1]["credential"], credential)

    def test_exact_unicode_match_is_verified_without_changing_records(self):
        credential = self.certify()
        before = {path: path.read_bytes() for path in (
            config.AUDIT_LOG, config.SUBMISSIONS_FILE, config.VERIFIED_HUMAN_CERTIFICATION_LOG)}
        response = self.verify(credential["Certificate_id"])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {
            "certificate_id": credential["Certificate_id"], "content_id": "c_hash_test",
            "verified": True, "status": "verified", "hash_algorithm": "sha256",
            "verified_dt_time": credential["verified_dt_time"],
            "latest_certification_at": self.records()[0]["timestamp"],
        })
        self.assertEqual(credential["content_hash"], hashlib.sha256(self.text.encode("utf-8")).hexdigest())
        for changed in (self.text.strip(), self.text + " ", self.text.replace(".", "!", 1),
                        self.text.replace("\n", "\r\n"), self.text.replace("é", "e\u0301")):
            with self.subTest(text=changed):
                mismatch = self.verify(credential["Certificate_id"], changed)
                self.assertEqual(mismatch.status_code, 200)
                self.assertFalse(mismatch.get_json()["verified"])
                self.assertEqual(mismatch.get_json()["status"], "content_mismatch")
                self.assertIsNone(mismatch.get_json()["verified_dt_time"])
                self.assertIsNone(mismatch.get_json()["latest_certification_at"])
        self.assertEqual(self.client.get("/content/c_hash_test").get_json()["status"], "certified")
        self.assertEqual(before, {path: path.read_bytes() for path in before})

    def test_text_beyond_model_token_limit_is_still_bound_to_the_certificate(self):
        text = "word " * (config.DETECTOR_MAX_TOKENS + 100) + "original ending"
        credential = self.certify(text)
        self.assertTrue(self.verify(credential["Certificate_id"], text).get_json()["verified"])
        changed = text.replace("original ending", "changed ending")
        self.assertFalse(self.verify(credential["Certificate_id"], changed).get_json()["verified"])

    def test_digest_cannot_be_borrowed_from_another_certificate(self):
        first = self.certify()
        second = self.certify("A different certified text.", "c_second")
        wrong = self.verify(second["Certificate_id"])
        self.assertEqual(wrong.status_code, 200)
        self.assertFalse(wrong.get_json()["verified"])
        self.assertTrue(self.verify(first["Certificate_id"]).get_json()["verified"])
        unknown = self.verify("vh_not_a_real_certificate")
        self.assertEqual(unknown.status_code, 404)
        self.assertFalse(unknown.get_json()["verified"])
        self.assertEqual(unknown.get_json()["error"], "certificate_not_found")

    def test_empty_store_returns_unknown_certificate(self):
        response = self.verify("vh_missing")
        self.assertEqual(response.status_code, 404)
        self.assertFalse(response.get_json()["verified"])
        self.assertFalse(config.VERIFIED_HUMAN_CERTIFICATION_LOG.exists())
        self.assertFalse(config.AUDIT_LOG.exists())

    def test_bad_json_and_field_types_return_400_without_writing_records(self):
        payloads = [None, [], "text", {}, {"certificate_id": "vh_x"},
                    {"text": self.text}, {"certificate_id": "vh_x", "text": "\ud800"}]
        for value in (None, "", " \n", 123, [], {}):
            payloads.append({"certificate_id": value, "text": self.text})
            payloads.append({"certificate_id": "vh_x", "text": value})
        for payload in payloads:
            with self.subTest(payload=payload):
                response = self.client.post("/verification/verify", data=json.dumps(payload),
                                            content_type="application/json")
                self.assertEqual(response.status_code, 400)
                self.assertFalse(response.get_json()["verified"])
        malformed = self.client.post("/verification/verify", data='{broken', content_type="application/json")
        self.assertEqual(malformed.status_code, 400)
        self.assertFalse(malformed.get_json()["verified"])
        self.assertFalse(config.VERIFIED_HUMAN_CERTIFICATION_LOG.exists())
        self.assertFalse(config.AUDIT_LOG.exists())

    def test_legacy_certificate_is_not_silently_upgraded_or_reported_verified(self):
        credential = self.certify()
        legacy = self.records()[0]
        del legacy["credential"]["hash_algorithm"]
        del legacy["credential"]["content_hash"]
        self.save_records([legacy])
        # A genuinely old certificate lacks the fields in both saved copies.
        entries = audit.read_entries()
        for entry in entries:
            if isinstance(entry.get("credential"), dict):
                entry["credential"].pop("hash_algorithm", None)
                entry["credential"].pop("content_hash", None)
        config.AUDIT_LOG.write_text("".join(json.dumps(entry) + "\n" for entry in entries))
        before = config.VERIFIED_HUMAN_CERTIFICATION_LOG.read_bytes()
        response = self.verify(credential["Certificate_id"])
        self.assertEqual(response.status_code, 409)
        self.assertFalse(response.get_json()["verified"])
        self.assertEqual(response.get_json()["error"], "certificate_unverifiable")
        existing = verification.review_content("c_hash_test", "certified", "Reviewer", "")
        self.assertEqual(existing["credential"], legacy["credential"])
        self.assertEqual(config.VERIFIED_HUMAN_CERTIFICATION_LOG.read_bytes(), before)
        self.assertEqual(self.client.get("/content/c_hash_test").get_json()["status"], "certified")

    def test_unsupported_algorithm_and_invalid_hash_cannot_verify(self):
        credential = self.certify()
        original = self.records()[0]
        for field, value in [("hash_algorithm", "md5"), ("content_hash", None),
                             ("content_hash", 123), ("content_hash", "a" * 63),
                             ("content_hash", "z" * 64)]:
            with self.subTest(field=field, value=value):
                invalid = copy.deepcopy(original)
                invalid["credential"][field] = value
                self.save_records([invalid])
                response = self.verify(credential["Certificate_id"])
                self.assertEqual(response.status_code, 409)
                self.assertFalse(response.get_json()["verified"])

    def test_replayed_identical_record_keeps_original_certification_activity(self):
        credential = self.certify()
        record = self.records()[0]
        self.save_records([record, record])
        response = self.verify(credential["Certificate_id"])
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.get_json()["verified"])
        self.assertEqual(response.get_json()["latest_certification_at"], record["timestamp"])

    def test_same_content_reuses_id_and_lookup_returns_latest_certification_by_time(self):
        first = self.certify(content_id="c_first")
        second = self.certify(content_id="c_second")
        self.assertEqual(first["Certificate_id"], second["Certificate_id"])
        records = self.records()
        # Deliberately order the file newest first, with two activities in the
        # same second. Selecting the last line or display string would be wrong.
        records[0]["timestamp"] = "2026-11-17T10:00:00.100000+00:00"
        records[1]["timestamp"] = "2026-11-17T10:00:00.900000+00:00"
        for record in records:
            record["credential"]["verified_dt_time"] = "2026-11-17 10:00:00 UTC"
        self.save_records(list(reversed(records)))
        before = config.VERIFIED_HUMAN_CERTIFICATION_LOG.read_bytes()
        for _ in range(2):
            response = self.verify(first["Certificate_id"])
            self.assertEqual(response.status_code, 200)
            body = response.get_json()
            self.assertTrue(body["verified"])
            self.assertEqual(body["content_id"], "c_second")
            self.assertEqual(body["verified_dt_time"], "2026-11-17 10:00:00 UTC")
            self.assertEqual(body["latest_certification_at"], records[1]["timestamp"])
        self.assertEqual(config.VERIFIED_HUMAN_CERTIFICATION_LOG.read_bytes(), before)
        # Lookup by content ID still reports that submission's own approval.
        self.assertEqual(self.client.get("/content/c_first").get_json()["credential"]["Certificate_id"], first["Certificate_id"])

    def test_real_suffix_collision_does_not_verify_uncertified_content(self):
        # These are genuine SHA-256 suffix collisions, not mocked hash outputs.
        first_text, second_text = "certificate-collision-2818", "certificate-collision-66974"
        first = self.certify(first_text, "c_collision_first")
        second_hash = hashlib.sha256(second_text.encode()).hexdigest()
        self.assertEqual(first["Certificate_id"], second_hash[-8:])
        self.assertNotEqual(first["content_hash"], second_hash)
        mismatch = self.verify(first["Certificate_id"], second_text)
        self.assertEqual(mismatch.status_code, 200)
        self.assertFalse(mismatch.get_json()["verified"])
        self.assertIsNone(mismatch.get_json()["latest_certification_at"])

    def test_collision_lookup_selects_latest_matching_full_hash_not_other_content(self):
        first_text, second_text = "certificate-collision-2818", "certificate-collision-66974"
        first = self.certify(first_text, "c_collision_first")
        self.certify(first_text, "c_collision_repeat")
        second = self.certify(second_text, "c_collision_second")
        self.assertEqual(first["Certificate_id"], second["Certificate_id"])
        records = self.records()
        for index, record in enumerate(records):
            record["timestamp"] = f"2026-11-17T10:00:0{index}+00:00"
            record["credential"]["verified_dt_time"] = f"2026-11-17 10:00:0{index} UTC"
        self.save_records(records)
        for text, expected in ((first_text, records[1]), (second_text, records[2])):
            body = self.verify(first["Certificate_id"], text).get_json()
            self.assertTrue(body["verified"])
            self.assertEqual(body["content_id"], expected["content_id"])
            self.assertEqual(body["latest_certification_at"], expected["timestamp"])
        unmatched = self.verify(first["Certificate_id"], "Neither certified text").get_json()
        self.assertFalse(unmatched["verified"])
        self.assertIsNone(unmatched["content_id"])
        self.assertIsNone(unmatched["verified_dt_time"])

    def test_conflicting_copies_of_one_activity_fail_closed(self):
        credential = self.certify()
        original = self.records()[0]
        conflicting = copy.deepcopy(original)
        conflicting["content_id"] = "c_conflicting"
        self.save_records([original, conflicting])
        response = self.verify(credential["Certificate_id"])
        self.assertEqual(response.status_code, 409)
        self.assertFalse(response.get_json()["verified"])

    def test_missing_invalid_naive_and_inconsistent_dates_are_unverifiable(self):
        credential = self.certify()
        original = self.records()[0]
        for timestamp in (None, "not-a-date", "2026-11-17T10:00:00", "2020-01-01T00:00:00+00:00"):
            with self.subTest(timestamp=timestamp):
                record = copy.deepcopy(original)
                record["timestamp"] = timestamp
                self.save_records([record])
                self.assertEqual(self.verify(credential["Certificate_id"]).status_code, 409)
        record = copy.deepcopy(original)
        record["credential"].pop("verified_dt_time")
        self.save_records([record])
        self.assertEqual(self.verify(credential["Certificate_id"]).status_code, 409)

    def test_previous_uuid_certificate_with_hash_remains_readable_without_rewrite(self):
        self.certify()
        record = self.records()[0]
        legacy_id = "vh_0123456789abcdef"
        record["credential"]["Certificate_id"] = legacy_id
        self.save_records([record])
        before = config.VERIFIED_HUMAN_CERTIFICATION_LOG.read_bytes()
        response = self.verify(legacy_id)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.get_json()["verified"])
        self.assertEqual(response.get_json()["verified_dt_time"], record["credential"]["verified_dt_time"])
        self.assertEqual(config.VERIFIED_HUMAN_CERTIFICATION_LOG.read_bytes(), before)

    def test_latest_certification_compares_instants_across_timezone_offsets(self):
        credential = self.certify(content_id="c_utc_later")
        self.certify(content_id="c_offset_earlier")
        records = self.records()
        records[0]["timestamp"] = "2026-11-17T10:01:00+00:00"
        records[0]["credential"]["verified_dt_time"] = "2026-11-17 10:01:00 UTC"
        records[1]["timestamp"] = "2026-11-17T13:00:00+03:00"
        records[1]["credential"]["verified_dt_time"] = "2026-11-17 10:00:00 UTC"
        self.save_records(records)
        body = self.verify(credential["Certificate_id"]).get_json()
        self.assertEqual(body["content_id"], "c_utc_later")
        self.assertEqual(body["latest_certification_at"], "2026-11-17T10:01:00+00:00")

    def test_retry_of_older_approval_does_not_refresh_or_replace_latest_activity(self):
        first = self.certify(content_id="c_old_approval")
        self.certify(content_id="c_new_approval")
        records = self.records()
        latest = records[-1]
        before = config.VERIFIED_HUMAN_CERTIFICATION_LOG.read_bytes()
        repeated = verification.review_content("c_old_approval", "certified", "Another reviewer", "")
        self.assertEqual(repeated["credential"], first)
        self.assertEqual(config.VERIFIED_HUMAN_CERTIFICATION_LOG.read_bytes(), before)
        body = self.verify(first["Certificate_id"]).get_json()
        self.assertEqual(body["content_id"], "c_new_approval")
        self.assertEqual(body["latest_certification_at"], latest["timestamp"])

    def test_short_id_must_agree_with_saved_full_hash(self):
        self.certify()
        record = self.records()[0]
        wrong_id = "00000000" if record["credential"]["Certificate_id"] != "00000000" else "11111111"
        record["credential"]["Certificate_id"] = wrong_id
        self.save_records([record])
        self.assertEqual(self.verify(wrong_id).status_code, 409)

    def test_concurrent_approvals_of_same_text_share_id_but_keep_distinct_history(self):
        for content_id in ("c_concurrent_a", "c_concurrent_b"):
            submissions.save_submission(content_id, "writer", self.text)
            audit.log_decision(content_id, "writer", label="unsure")
            verification.request_review(content_id, "Please review", "Earlier draft")
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(lambda content_id: verification.review_content(
                content_id, "certified", "Reviewer", ""), ("c_concurrent_a", "c_concurrent_b")))
        self.assertEqual(results[0]["credential"]["Certificate_id"], results[1]["credential"]["Certificate_id"])
        self.assertEqual(len(self.records()), 2)
        latest = max(self.records(), key=lambda record: datetime.fromisoformat(record["timestamp"]))
        body = self.verify(latest["credential"]["Certificate_id"]).get_json()
        self.assertEqual(body["content_id"], latest["content_id"])
        self.assertEqual(body["latest_certification_at"], latest["timestamp"])

    def test_unapproved_or_malformed_certificate_record_cannot_verify(self):
        credential = self.certify()
        original = self.records()[0]
        for field, value in [("status", "not_certified"), ("review_decision", "not_certified"),
                             ("content_id", None)]:
            with self.subTest(field=field):
                invalid = copy.deepcopy(original)
                invalid[field] = value
                self.save_records([invalid])
                response = self.verify(credential["Certificate_id"])
                self.assertEqual(response.status_code, 409)
                self.assertFalse(response.get_json()["verified"])

    def test_corrupt_or_unreadable_store_returns_503(self):
        for data in ('{broken\n', '[]\n', '{"credential": null}\n'):
            with self.subTest(data=data):
                config.VERIFIED_HUMAN_CERTIFICATION_LOG.write_text(data)
                response = self.verify("vh_any")
                self.assertEqual(response.status_code, 503)
                self.assertFalse(response.get_json()["verified"])
                self.assertEqual(response.get_json()["error"], "certificate_store_unavailable")
        with patch("verification._certificates", side_effect=OSError("Cannot read file")):
            self.assertEqual(self.verify("vh_any").status_code, 503)
        with patch("verification._locked", side_effect=OSError("Cannot open lock")):
            response = self.verify("vh_any")
            self.assertEqual(response.status_code, 503)
            self.assertFalse(response.get_json()["verified"])

    def test_repeat_approval_preserves_original_hash_even_if_submission_changes(self):
        credential = self.certify()
        saved = submissions.get_submission("c_hash_test")
        saved["text"] = "Changed after the original approval."
        config.SUBMISSIONS_FILE.write_text(json.dumps(saved) + "\n")
        repeated = verification.review_content("c_hash_test", "certified", "Another reviewer", "")
        self.assertEqual(repeated["credential"], credential)
        self.assertEqual(len(self.records()), 1)
        self.assertTrue(self.verify(credential["Certificate_id"]).get_json()["verified"])
        self.assertFalse(self.verify(credential["Certificate_id"], saved["text"]).get_json()["verified"])

    def test_saved_hash_verifies_after_process_restart_without_original_text(self):
        credential = self.certify()
        self.certify(content_id="c_latest_after_restart")
        latest = self.records()[-1]
        config.SUBMISSIONS_FILE.unlink()
        config.AUDIT_LOG.unlink()
        script = """
import json, sys
from pathlib import Path
import config, verification
config.LOG_DIR = Path(sys.argv[1])
config.VERIFIED_HUMAN_CERTIFICATION_LOG = config.LOG_DIR / 'certificates.jsonl'
print(json.dumps(verification.verify_content(sys.argv[2], sys.argv[3])))
"""
        completed = subprocess.run(
            [sys.executable, "-B", "-c", script, str(self.directory), credential["Certificate_id"], self.text],
            cwd=config.ROOT, text=True, capture_output=True, check=True,
        )
        result = json.loads(completed.stdout)
        self.assertTrue(result["verified"])
        self.assertEqual(result["content_id"], "c_latest_after_restart")
        self.assertEqual(result["latest_certification_at"], latest["timestamp"])


if __name__ == "__main__":
    unittest.main()
