"""Check active MATTR scoring and the supplied whole-text TTR fallback."""

import json
import math
import re
import statistics
import unittest
from pathlib import Path
from unittest.mock import patch

import stylometry


def text_with_lengths(lengths, unique=False):
    """Build prose with known counts; use letters only to match the tokenizer."""
    tokens = []
    index = 0
    for length in lengths:
        sentence = []
        for _ in range(length):
            token = "word" + chr(97 + index // 26) + chr(97 + index % 26) if unique else "word"
            sentence.append(token)
            index += 1
        tokens.append(" ".join(sentence) + ".")
    return " ".join(tokens)


def supplied_reference_score(text):
    """User-supplied acceptance oracle, independent of the refactored methods."""
    sentences = [s for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s]
    words = re.findall(r"[A-Za-z']+", text)
    n_words = len(words)
    if len(sentences) < 3 or n_words < 40:
        return None
    lengths = [len(re.findall(r"[A-Za-z']+", s)) for s in sentences]
    cv = statistics.pstdev(lengths) / statistics.mean(lengths)
    spread_ai = max(0.0, min(1.0, (0.60 - cv) / (0.60 - 0.25)))
    density = len(re.findall(r"[,;:\u2014\u2013()]", text)) / n_words
    punct_ai = max(0.0, min(1.0, (density - 0.06) / (0.14 - 0.06)))
    ttr = len(set(w.lower() for w in words)) / n_words
    ttr_ai = max(0.0, min(1.0, (0.80 - ttr) / (0.80 - 0.62)))
    return 0.50 * spread_ai + 0.20 * punct_ai + 0.30 * ttr_ai


class MeasurementTests(unittest.TestCase):
    def test_tokenizer_matches_sample_case_apostrophes_and_digits(self):
        self.assertEqual(
            stylometry.words("Don't DON'T 123 alpha2beta rock'n'roll"),
            ["don't", "don't", "alpha", "beta", "rock'n'roll"],
        )

    def test_sentence_splitter_matches_sample(self):
        self.assertEqual(
            stylometry.sentences("  One! \nTwo? Three.  "),
            ["One!", "Two?", "Three."],
        )
        self.assertEqual(stylometry.sentences(""), [])

    def test_spread_uses_population_deviation(self):
        # Counts 2, 4, 6: population variance 8/3 and mean 4.
        self.assertAlmostEqual(
            stylometry.sentence_length_spread(text_with_lengths([2, 4, 6])),
            math.sqrt(8 / 3) / 4,
        )

    def test_spread_is_relative_to_sentence_length(self):
        self.assertAlmostEqual(
            stylometry.sentence_length_spread(text_with_lengths([2, 4, 6])),
            stylometry.sentence_length_spread(text_with_lengths([4, 8, 12])),
        )

    def test_wordless_sentence_fragments_match_sample_distribution(self):
        self.assertAlmostEqual(
            stylometry.sentence_length_spread("!!! One two. Three four."),
            math.sqrt(0.5),
        )

    def test_empty_and_uniform_inputs_have_zero_spread(self):
        for text in ("", " \t\n", "!!! ???", "One sentence.", "One two. Three four."):
            with self.subTest(text=text):
                self.assertEqual(stylometry.sentence_length_spread(text), 0.0)

    def test_ttr_counts_lowercase_unique_tokens_over_all_tokens(self):
        self.assertEqual(stylometry.type_token_ratio("The cat sleeps. THE dog sleeps."), 4 / 6)
        self.assertEqual(stylometry.type_token_ratio("Don't don't stop."), 2 / 3)
        self.assertEqual(stylometry.type_token_ratio(""), 0.0)

    def test_mattr_averages_every_overlapping_window(self):
        # [a,a,b], [a,b,c], [b,c,b] have TTRs 2/3, 1, 2/3.
        self.assertAlmostEqual(stylometry.moving_average_ttr("A a b c B", 3), 7 / 9)

    def test_mattr_short_input_and_first_sliding_window(self):
        self.assertEqual(stylometry.moving_average_ttr("", 50), 0.0)
        self.assertAlmostEqual(
            stylometry.moving_average_ttr(" ".join(["a"] * 25 + ["b"] * 24), 50), 2 / 49
        )
        self.assertEqual(
            stylometry.moving_average_ttr(" ".join(["a"] * 25 + ["b"] * 25), 50), 2 / 50
        )
        # At 51 tokens there are two windows, with two and three types.
        self.assertAlmostEqual(
            stylometry.moving_average_ttr(" ".join(["a"] * 25 + ["b"] * 25 + ["c"]), 50),
            0.05,
        )

    def test_punctuation_counts_only_seven_structural_marks(self):
        self.assertEqual(stylometry.punctuation_density("One two ,;:—–()"), 7 / 2)
        self.assertEqual(stylometry.punctuation_density("One. Two! Three? \"Four\" - 'five'"), 0.0)

    def test_punctuation_is_per_word_and_ignores_word_length_and_whitespace(self):
        self.assertEqual(stylometry.punctuation_density("a, b."), 0.5)
        self.assertEqual(stylometry.punctuation_density("extraordinary,\tword.\n"), 0.5)
        self.assertEqual(stylometry.punctuation_density(",;:—–()"), 0.0)


class StyleScoreTests(unittest.TestCase):
    def test_clamp_handles_both_extremes_and_preserves_middle(self):
        for value, expected in ((-3, 0.0), (0, 0.0), (0.42, 0.42), (1, 1.0), (3, 1.0)):
            self.assertEqual(stylometry.clamp01(value), expected)

    def test_both_minimums_are_required(self):
        for text in ("", "!!! ???", text_with_lengths([20, 20]), text_with_lengths([13, 13, 13])):
            with self.subTest(text=text):
                self.assertIsNone(stylometry.style_subscores(text))
                self.assertIsNone(stylometry.style_score(text))
                self.assertEqual(stylometry.style_classification(text), "INSUFFICIENT_DATA")
                with self.assertRaisesRegex(stylometry.TextTooShortError, "3 sentences and 40 words"):
                    stylometry.style_signal(text)

    def test_exactly_three_sentences_and_40_words_qualifies(self):
        text = text_with_lengths([14, 13, 13])
        self.assertAlmostEqual(stylometry.style_score(text), 0.8)
        self.assertEqual(stylometry.style_signal(text), stylometry.style_score(text))

    def test_spread_linear_anchors_and_clipping(self):
        text = text_with_lengths([14, 13, 13])
        for raw, expected in ((0, 1), (0.25, 1), (0.425, 0.5), (0.60, 0), (2, 0)):
            with self.subTest(raw=raw):
                with patch("stylometry.sentence_length_spread", return_value=raw):
                    self.assertAlmostEqual(stylometry.style_subscores(text)[0], expected)

    def test_punctuation_linear_anchors_and_clipping(self):
        text = text_with_lengths([14, 13, 13])
        for raw, expected in ((0, 0), (0.06, 0), (0.10, 0.5), (0.14, 1), (2, 1)):
            with self.subTest(raw=raw):
                with patch("stylometry.punctuation_density", return_value=raw):
                    self.assertAlmostEqual(stylometry.style_subscores(text)[1], expected)

    def test_whole_text_ttr_linear_anchors_and_clipping(self):
        text = text_with_lengths([14, 13, 13])
        for raw, expected in ((0, 1), (0.62, 1), (0.71, 0.5), (0.80, 0), (1, 0)):
            with self.subTest(raw=raw):
                with patch.object(stylometry, "TTR_WINDOW", 0), patch(
                    "stylometry.type_token_ratio", return_value=raw
                ):
                    self.assertAlmostEqual(stylometry.style_subscores(text)[2], expected)

    def test_mattr_linear_anchors_and_clipping(self):
        text = text_with_lengths([14, 13, 13])
        for raw, expected in ((0, 1), (0.68, 1), (0.75, 0.5), (0.82, 0), (1, 0)):
            with self.subTest(raw=raw), patch("stylometry.moving_average_ttr", return_value=raw):
                self.assertAlmostEqual(stylometry.style_subscores(text)[2], expected)

    def test_active_mattr_score_on_known_vocabulary(self):
        # Fifty tokens, thirty-eight distinct types: MATTR = 0.76.
        # Sentence lengths 20/15/15 saturate spread_ai at 1; punctuation_ai is 0.
        vocabulary = ["term" + chr(97 + i // 26) + chr(97 + i % 26) for i in range(38)]
        tokens = vocabulary + vocabulary[:12]
        text = ". ".join(" ".join(part) for part in (tokens[:20], tokens[20:35], tokens[35:])) + "."
        self.assertAlmostEqual(stylometry.ttr_measure(text)[0], 0.76)
        self.assertEqual(stylometry.ttr_measure(text)[1:], (0.68, 0.82))
        self.assertAlmostEqual(stylometry.style_score(text), 0.5 + 0.3 * (3 / 7))
        self.assertEqual(stylometry.style_classification(text), "Uncertain")

    def test_weights_match_the_supplied_rule(self):
        for subscores, expected in (
            ((1, 0, 0), 0.50), ((0, 1, 0), 0.20), ((0, 0, 1), 0.30),
            ((1, 1, 1), 1.0), ((0, 0, 0), 0.0),
        ):
            with self.subTest(subscores=subscores):
                with patch("stylometry.style_subscores", return_value=subscores):
                    self.assertEqual(stylometry.style_score("text"), expected)

    def test_all_three_labels_are_reachable_with_actual_text(self):
        for text, expected_score, expected_label in (
            (text_with_lengths([10, 15, 15]), 0.8, "Likely AI"),
            (text_with_lengths([10, 10, 10, 10], unique=True), 0.5, "Uncertain"),
            (text_with_lengths([2, 8, 30], unique=True), 0.0, "Likely Human"),
        ):
            with self.subTest(label=expected_label):
                self.assertAlmostEqual(stylometry.style_score(text), expected_score)
                self.assertEqual(stylometry.style_classification(text), expected_label)

    def test_decision_thresholds_use_unrounded_scores(self):
        for score, label in (
            (None, "INSUFFICIENT_DATA"), (0.0, "Likely Human"),
            (math.nextafter(0.40, 0.0), "Likely Human"), (0.40, "Uncertain"),
            (math.nextafter(0.65, 0.0), "Uncertain"), (0.65, "Likely AI"),
            (1.0, "Likely AI"),
        ):
            with self.subTest(score=score):
                self.assertEqual(stylometry.style_score_to_label(score), label)

    def test_thresholds_are_named_constants(self):
        with patch("stylometry.STYLE_AI_THRESHOLD", 0.70), patch(
            "stylometry.STYLE_UNCERTAIN_THRESHOLD", 0.45
        ):
            self.assertEqual(stylometry.style_score_to_label(0.68), "Uncertain")
            self.assertEqual(stylometry.style_score_to_label(0.42), "Likely Human")

    def test_invalid_scores_are_rejected(self):
        for score in (-0.1, 1.1, math.inf, -math.inf, math.nan):
            with self.subTest(score=score):
                with self.assertRaises(ValueError):
                    stylometry.style_score_to_label(score)

    @patch.object(stylometry, "TTR_WINDOW", 0)
    def test_whole_text_mode_matches_the_supplied_algorithm(self):
        samples = [
            "", text_with_lengths([20, 20]), text_with_lengths([13, 13, 13]),
            text_with_lengths([14, 13, 13]), text_with_lengths([2, 8, 30], unique=True),
            text_with_lengths([50] * 5), "!!! " + text_with_lengths([10, 15, 15]),
            text_with_lengths([10, 15, 15]) + " ,;:—–() \"123\"",
        ]
        for path in sorted((Path(__file__).parent / "samples").glob("*.json")):
            payload = json.loads(path.read_text())
            # Malformed API fixtures (missing text, lists, etc.) belong to
            # request-validation tests, not the string-scoring oracle.
            if isinstance(payload, dict) and isinstance(payload.get("text"), str):
                samples.append(payload["text"])
        for text in samples:
            with self.subTest(text=text[:80]):
                expected = supplied_reference_score(text)
                if expected is None:
                    self.assertIsNone(stylometry.style_score(text))
                else:
                    self.assertAlmostEqual(stylometry.style_score(text), expected, places=14)
                    self.assertAlmostEqual(stylometry.style_signal(text), expected, places=14)

    def test_scores_remain_finite_and_bounded_at_extremes(self):
        for text in (
            text_with_lengths([1, 1, 1000]),
            text_with_lengths([14, 13, 13]) + ",;" * 1000,
            text_with_lengths([100] * 3),
        ):
            with self.subTest(text=text[:60]):
                score = stylometry.style_score(text)
                self.assertTrue(math.isfinite(score))
                self.assertGreaterEqual(score, 0.0)
                self.assertLessEqual(score, 1.0)


if __name__ == "__main__":
    unittest.main()
