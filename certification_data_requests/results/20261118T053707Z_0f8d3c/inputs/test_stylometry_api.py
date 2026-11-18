"""Verify style integration using Flask's test client, with model and audit mocked."""

import unittest
from unittest.mock import patch

from app import app
import stylometry
from test_stylometry import text_with_lengths


class StyleApiTests(unittest.TestCase):
    def setUp(self):
        self.enterContext(patch("submissions.save_submission"))

    def test_insufficient_style_input_returns_400_without_a_decision(self):
        for text in (text_with_lengths([20, 20]), text_with_lengths([13, 13, 13])):
            with self.subTest(text=text):
                with patch("detector.model_signal", return_value=0.5), patch(
                    "audit.log_decision"
                ) as log:
                    response = app.test_client().post(
                        "/submit", json={"text": text, "creator_id": "style_test"}
                    )
                    self.assertEqual(response.status_code, 400)
                    self.assertEqual(response.get_json()["error"], "bad_request")
                    self.assertIn("3 sentences and 40 words", response.get_json()["message"])
                    log.assert_not_called()

    def test_valid_style_score_reaches_response_and_audit(self):
        text = text_with_lengths([14, 13, 13])
        expected = stylometry.style_signal(text)
        with patch("detector.model_signal", return_value=0.5), patch("audit.log_decision") as log:
            response = app.test_client().post(
                "/submit", json={"text": text, "creator_id": "style_test"}
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.get_json()["style_score"], expected)
            self.assertEqual(log.call_args.kwargs["style_score"], expected)


if __name__ == "__main__":
    unittest.main()
