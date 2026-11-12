"""Check final label boundaries and reader-facing messages in the submit API."""

import math
import unittest
from unittest.mock import patch

from app import app
import config
import calibrate_combined
import detector
import scoring
from test_stylometry import text_with_lengths


class LabelTests(unittest.TestCase):
    def setUp(self):
        self.enterContext(patch("submissions.save_submission"))

    def test_threshold_boundaries_cover_every_label(self):
        cases = [
            (0.0, "human"),
            (config.HUMAN_THRESHOLD, "human"),
            (math.nextafter(config.HUMAN_THRESHOLD, 1.0), "unsure"),
            (math.nextafter(config.AI_THRESHOLD, 0.0), "unsure"),
            (config.AI_THRESHOLD, "ai"),
            (1.0, "ai"),
        ]
        for score, expected in cases:
            with self.subTest(score=score):
                label, confidence = scoring.score_to_label(score)
                self.assertEqual(label, expected)
                self.assertEqual(confidence, score)
                self.assertIsInstance(confidence, float)

    def test_each_response_and_audit_record_include_matching_label_text(self):
        # Real stylometry yields 0.8 for this valid, repetitive passage.
        # Vary the model signal to exercise all three final labels.
        text = text_with_lengths([14, 13, 13])
        for model_score, expected in [(0.0, "human"), (0.5, "unsure"), (1.0, "ai")]:
            with self.subTest(label=expected):
                with patch("detector.model_signal", return_value=model_score), patch(
                    "audit.log_decision"
                ) as log:
                    response = app.test_client().post(
                        "/submit",
                        json={"text": text, "creator_id": f"label_test_{expected}"},
                    )
                self.assertEqual(response.status_code, 200)
                body = response.get_json()
                self.assertEqual(body["label"], expected)
                self.assertEqual(body["label_text"], scoring.LABEL_TEXT[expected])
                self.assertEqual(body["confidence"], body["combined_score"])
                self.assertIn("model_score", body)
                self.assertIn("style_score", body)
                log.assert_called_once()
                self.assertEqual(log.call_args.kwargs["label"], expected)
                self.assertEqual(log.call_args.kwargs["label_text"], body["label_text"])
                self.assertEqual(
                    log.call_args.kwargs["combined_score"], body["combined_score"]
                )


class ModelBlendTests(unittest.TestCase):
    def setUp(self):
        self.enterContext(patch.object(config, "BINOCULARS_ENABLED", True))
        self.saved = self.enterContext(patch("submissions.save_submission"))
        self.enterContext(patch("audit.log_decision"))
        self.perplexity = self.enterContext(patch("detector.model_signal", return_value=0.8))
        self.binoculars = self.enterContext(patch("binoculars_signal.binoculars_signal", return_value=0.2))
        self.enterContext(patch("stylometry.style_signal", return_value=0.4))

    def check_api_and_calibration(self, count, expected_model, binoculars_used):
        text = text_with_lengths([count - 28, 14, 14])
        self.assertEqual(len(text.split()), count)
        response = app.test_client().post("/submit", json={
            "text": text, "creator_id": f"blend_{self._testMethodName}_{count}",
        })
        self.assertEqual(response.status_code, 200)
        body = response.get_json()
        self.assertEqual(body["model_score"], expected_model)
        self.assertAlmostEqual(body["combined_score"], 0.7 * expected_model + 0.3 * 0.4)
        self.assertEqual(self.saved.call_args.kwargs["binoculars_used"], binoculars_used)
        row = calibrate_combined.score_all([("sample", "ai", text)])[0]
        self.assertEqual(row["model"], body["model_score"])
        self.assertEqual(calibrate_combined.combined(row, 0.7), body["combined_score"])

    def test_model_blend_starts_at_250_words(self):
        for count, expected, used in ((249, 0.8, False), (250, 0.62, True), (251, 0.62, True)):
            with self.subTest(words=count):
                self.check_api_and_calibration(count, expected, used)

    def test_unavailable_binoculars_uses_full_perplexity_score(self):
        self.binoculars.side_effect = detector.DetectorUnavailable("test unavailable")
        self.check_api_and_calibration(250, 0.8, False)

    def test_disabled_binoculars_skips_inference_for_every_length(self):
        with patch.object(config, "BINOCULARS_ENABLED", False):
            for count in (249, 250, 251):
                with self.subTest(words=count):
                    self.check_api_and_calibration(count, 0.8, False)
                    self.assertIsNone(self.saved.call_args.kwargs["binoculars_score"])
            self.assertFalse(app.test_client().get("/health").get_json()["binoculars_enabled"])
        self.binoculars.assert_not_called()

    def test_blend_weights_are_shared_configuration(self):
        with patch.object(config, "MODEL_WEIGHT_PERPLEXITY", 0.8), patch.object(
            config, "MODEL_WEIGHT_BINOCULARS", 0.2
        ):
            self.check_api_and_calibration(250, 0.68, True)

    def test_api_and_calibration_use_same_four_decimal_rounding(self):
        self.perplexity.return_value = 0.1234
        self.binoculars.return_value = 0.5678
        self.check_api_and_calibration(250, 0.2567, True)


if __name__ == "__main__":
    unittest.main()
