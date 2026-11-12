"""Verify appeal voting, validation, text retention, and the append-only log."""

from datetime import datetime, timedelta
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from app import app
import appeals
import audit
import config
import detector
import scoring
import submissions
from test_stylometry import text_with_lengths


class AppealTests(unittest.TestCase):
    def setUp(self):
        directory = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.enterContext(patch.object(config, "LOG_DIR", directory))
        self.enterContext(patch.object(config, "AUDIT_LOG", directory / "audit.jsonl"))
        self.enterContext(patch.object(config, "SUBMISSIONS_FILE", directory / "submissions.jsonl"))
        self.enterContext(patch("binoculars_signal.binoculars_signal", return_value=0.5))
        self.client = app.test_client()
        self.text = (
            "First sentence introduces the topic.\n"
            "Second sentence offers some context.  "
            "Third sentence supplies more detail!\n\n"
            "Fourth sentence closes the passage."
        )

    def seed_decision(self, text=True):
        if text:
            submissions.save_submission("c_appeal_test", "original_writer", self.text)
        return audit.log_decision(
            content_id="c_appeal_test",
            creator_id="original_writer",
            model_score=0.9,
            style_score=0.7,
            combined_score=0.84,
            label="ai",
            guess="ai",
            confidence=0.84,
        )

    def post_appeal(self, **extra):
        return self.client.post("/appeal", json={
            "content_id": "c_appeal_test",
            "reasoning": "I wrote this and can provide earlier drafts.",
            **extra,
        })

    def test_majority_human_ai_unsure_and_three_way_tie(self):
        self.seed_decision()
        cases = [
            ([0.1, 0.1, 0.9], "human"),
            ([0.9, 0.9, 0.1], "ai"),
            ([0.5, 0.5, 0.9], "unsure"),
            ([0.1, 0.5, 0.9], "unsure"),
        ]
        for signals, expected in cases:
            with self.subTest(signals=signals):
                with patch("detector.model_signal", side_effect=signals), patch(
                    "stylometry.style_signal", side_effect=signals
                ):
                    response = self.post_appeal()
                self.assertEqual(response.status_code, 200)
                body = response.get_json()
                self.assertEqual(body["label"], expected)
                self.assertEqual(body["status"], "under_review")
                self.assertEqual(len(body["evaluations"]), 3)
                self.assertEqual(sum(body["votes"].values()), 3)
                if expected == "unsure":
                    self.assertEqual(body["message"], appeals.UNSURE_MESSAGE)
                elif expected == "ai":
                    self.assertIn(appeals.AI_REVIEW_MESSAGE, body["message"])
                else:
                    self.assertEqual(body["message"], appeals.CONFIRMATION)

    def test_appeal_weights_change_the_outcome_without_changing_submit_weights(self):
        self.seed_decision()
        with patch("detector.model_signal", return_value=0.9), patch(
            "stylometry.style_signal", return_value=0.1
        ):
            body = self.post_appeal().get_json()
        self.assertEqual(body["label"], "unsure")
        self.assertEqual(body["weights"], {"model": 0.6, "style": 0.4})
        for evaluation in body["evaluations"]:
            self.assertAlmostEqual(evaluation["combined_score"], 0.58)
        self.assertEqual(scoring.score_to_label(scoring.combine_signals(0.9, 0.1))[0], "ai")

    def test_both_signals_receive_the_exact_three_text_variants(self):
        self.seed_decision()
        with patch("detector.model_signal", return_value=0.5) as model, patch(
            "stylometry.style_signal", return_value=0.5
        ) as style:
            self.assertEqual(self.post_appeal().status_code, 200)
        expected_texts = [
            self.text,
            "Second sentence offers some context.  Third sentence supplies more detail!\n\nFourth sentence closes the passage.",
            "First sentence introduces the topic.\nSecond sentence offers some context.  Third sentence supplies more detail!",
        ]
        self.assertEqual([call.args[0] for call in model.call_args_list], expected_texts)
        self.assertEqual([call.args[0] for call in style.call_args_list], expected_texts)

    def test_appeal_is_logged_before_scoring_and_original_decision_is_preserved(self):
        original = self.seed_decision()
        original_bytes = config.AUDIT_LOG.read_bytes()

        def model_score(text):
            self.assertEqual(audit.entries_for("c_appeal_test")[-1]["event"], "appeal")
            self.assertEqual(audit.entries_for("c_appeal_test")[-1]["status"], "under_review")
            return 0.2

        with patch("detector.model_signal", side_effect=model_score), patch(
            "stylometry.style_signal", return_value=0.2
        ):
            response = self.post_appeal(creator_id="different_writer")
        body = response.get_json()
        self.assertTrue(config.AUDIT_LOG.read_bytes().startswith(original_bytes))
        records = audit.entries_for("c_appeal_test")
        self.assertEqual(len(records), 3)
        self.assertEqual(records[0], original)
        self.assertEqual(records[1]["reasoning"], "I wrote this and can provide earlier drafts.")
        for record in records[1:]:
            self.assertEqual(record["creator_id"], "original_writer")
            self.assertEqual(record["appeal_id"], body["appeal_id"])
            self.assertEqual(record["status"], "under_review")
        for key, value in body.items():
            self.assertEqual(records[2][key], value)

        audit.log_decision("c_unrelated", "other_writer")
        log_response = self.client.get("/log?content_id=c_appeal_test")
        self.assertEqual(log_response.get_json(), {"count": 3, "entries": records})
        latest = self.client.get("/log?content_id=c_appeal_test&limit=1").get_json()
        self.assertEqual(latest["entries"][0], records[-1])
        self.assertEqual(latest["entries"][0]["status"], "under_review")

    def test_invalid_payload_or_fields_return_400_without_creating_an_appeal(self):
        self.seed_decision()
        original_bytes = config.AUDIT_LOG.read_bytes()
        invalid = [
            [], "text", {}, {"content_id": "c_appeal_test"},
            {"content_id": None, "reasoning": "Please review"},
            {"content_id": 123, "reasoning": "Please review"},
            {"content_id": "   ", "reasoning": "Please review"},
            {"content_id": "c_appeal_test", "reasoning": "   "},
            {"content_id": "c_appeal_test", "reasoning": []},
        ]
        for payload in invalid:
            with self.subTest(payload=payload):
                response = self.client.post("/appeal", json=payload)
                self.assertEqual(response.status_code, 400)
        response = self.client.post("/appeal", data="{", content_type="application/json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(config.AUDIT_LOG.read_bytes(), original_bytes)

    def test_unknown_id_returns_404_without_inference(self):
        with patch("appeals.reassess") as reassess:
            response = self.post_appeal()
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.get_json()["error"], "not_found")
        self.assertEqual(audit.read_entries(), [])
        reassess.assert_not_called()

    def test_legacy_submission_without_text_is_still_recorded_for_review(self):
        self.seed_decision(text=False)
        with patch("detector.model_signal") as model, patch("stylometry.style_signal") as style:
            response = self.post_appeal()
        self.assertEqual(response.status_code, 200)
        body = response.get_json()
        self.assertEqual(body["label"], "unsure")
        self.assertEqual(body["status"], "under_review")
        for evaluation in body["evaluations"]:
            self.assertIsNone(evaluation["combined_score"])
            self.assertEqual(evaluation["reason"], "original_text_unavailable")
        self.assertEqual(len(audit.entries_for("c_appeal_test")), 3)
        model.assert_not_called()
        style.assert_not_called()

    def test_legacy_text_in_audit_can_still_be_appealed(self):
        audit.log_decision("c_appeal_test", "original_writer", text=self.text)
        with patch("appeals.reassess", wraps=appeals.reassess) as reassess, patch(
            "detector.model_signal", return_value=0.2
        ), patch("stylometry.style_signal", return_value=0.3):
            response = self.post_appeal()
        self.assertEqual(response.status_code, 200)
        reassess.assert_called_once_with(self.text)
        self.assertFalse(config.SUBMISSIONS_FILE.exists())

    def test_trimmed_text_too_short_votes_unsure_without_a_fabricated_score(self):
        self.text = text_with_lengths([14, 13, 13])
        self.seed_decision()
        with patch("detector.model_signal", return_value=0.5) as model:
            body = self.post_appeal().get_json()
        self.assertEqual(body["label"], "unsure")
        self.assertEqual(model.call_count, 1)
        self.assertEqual(body["evaluations"][0]["status"], "scored")
        for evaluation in body["evaluations"][1:]:
            self.assertEqual(evaluation["status"], "insufficient_data")
            self.assertEqual(evaluation["label"], "unsure")
            self.assertIsNone(evaluation["combined_score"])

    def test_model_unavailable_preserves_the_appeal_and_returns_unsure(self):
        self.seed_decision()
        with patch("detector.model_signal", side_effect=detector.DetectorUnavailable("unavailable")), patch(
            "stylometry.style_signal", return_value=0.5
        ):
            response = self.post_appeal()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["label"], "unsure")
        for evaluation in response.get_json()["evaluations"]:
            self.assertEqual(evaluation["reason"], "model_unavailable")
        self.assertEqual(audit.entries_for("c_appeal_test")[-1]["status"], "under_review")

    def test_submit_retains_original_text_for_a_later_appeal(self):
        text = "  " + text_with_lengths([14, 14, 14, 14]) + "\n\nCafé — original wording.  "
        with patch("detector.model_signal", return_value=0.2):
            submitted = self.client.post("/submit", json={"text": text, "creator_id": "saved_writer"})
        self.assertEqual(submitted.status_code, 200)
        body = submitted.get_json()
        decision = audit.entries_for(body["content_id"])[0]
        self.assertNotIn("text", decision)
        self.assertEqual(decision["guess"], body["guess"])
        saved = json.loads(config.SUBMISSIONS_FILE.read_text(encoding="utf-8"))
        self.assertEqual(set(saved), set(decision) | {"text"})
        for key, value in decision.items():
            if key != "timestamp":
                self.assertEqual(saved[key], value)
        self.assertEqual(saved["content_id"], body["content_id"])
        self.assertEqual(saved["creator_id"], "saved_writer")
        self.assertEqual(saved["text"], text)
        self.assertEqual(datetime.fromisoformat(saved["timestamp"]).utcoffset(), timedelta(0))
        submissions.save_submission("c_other", "other_writer", "A different submission.")
        submission_bytes = config.SUBMISSIONS_FILE.read_bytes()
        with patch("detector.model_signal", return_value=0.2) as model:
            appealed = self.client.post("/appeal", json={
                "content_id": body["content_id"], "reasoning": "Please review my work."
            })
        self.assertEqual(appealed.status_code, 200)
        self.assertEqual(model.call_count, 3)
        self.assertEqual(model.call_args_list[0].args[0], text)
        self.assertEqual(appealed.get_json()["status"], "under_review")
        self.assertEqual(config.SUBMISSIONS_FILE.read_bytes(), submission_bytes)
        self.assertTrue(all("text" not in entry for entry in audit.entries_for(body["content_id"])))

    def test_submission_storage_failure_does_not_record_a_decision(self):
        with patch.dict(app.config, TESTING=True), patch("detector.model_signal", return_value=0.2), patch(
            "stylometry.style_signal", return_value=0.3
        ), patch("submissions.save_submission", side_effect=OSError("Storage unavailable")), patch(
            "audit.log_decision"
        ) as log:
            with self.assertRaises(OSError):
                self.client.post("/submit", json={"text": self.text, "creator_id": "storage_failure_test"})
        log.assert_not_called()


if __name__ == "__main__":
    unittest.main()
