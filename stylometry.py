"""Measure writing style using the supplied linear-anchor scoring rule.

The three measurement functions return raw values. style_subscores normalizes
them into AI-oriented scores; style_score combines them, returning None for
insufficient text. style_signal preserves the service's float-returning API
by raising TextTooShortError when style_score cannot judge the input.

These heuristics measure form, not meaning or authorship. Their anchors are
experimental settings for short prose, not calibrated probabilities.

    python stylometry.py "some text to look at"
"""

import math
import re
import statistics


WORD_PATTERN = r"[A-Za-z']+"
STRUCTURAL_PUNCTUATION_PATTERN = r"[,;:—–()]"

MIN_STYLE_SENTENCES = 3
MIN_STYLE_WORDS = 40

SPREAD_AI_ANCHOR = 0.25
SPREAD_HUMAN_ANCHOR = 0.60
PUNCTUATION_HUMAN_ANCHOR = 0.06
PUNCTUATION_AI_ANCHOR = 0.14
TTR_AI_ANCHOR = 0.62
TTR_HUMAN_ANCHOR = 0.80

STYLE_WEIGHT_SPREAD = 0.50
STYLE_WEIGHT_PUNCTUATION = 0.20
STYLE_WEIGHT_TTR = 0.30

STYLE_AI_THRESHOLD = 0.65
STYLE_UNCERTAIN_THRESHOLD = 0.40


class TextTooShortError(ValueError):
    """The input has too few sentences or words for the style signal."""


def clamp01(x: float) -> float:
    """Clamp a normalized contribution to the inclusive interval [0, 1]."""
    return max(0.0, min(1.0, x))


def sentences(text: str) -> list[str]:
    """Split at whitespace following a period, exclamation mark, or question mark."""
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [part for part in parts if part]


def words(text: str) -> list[str]:
    """Return lowercase tokens using the sample's letters/apostrophes regex.

    Digits are excluded. Straight apostrophes stay within tokens, while curly
    apostrophes split tokens. This intentionally matches the supplied algorithm.
    """
    return [token.lower() for token in re.findall(WORD_PATTERN, text)]


# ── Raw measurements ────────────────────────────────────────────────────────

def sentence_length_spread(text: str) -> float:
    """Return population standard deviation / mean of sentence word counts.

    Use population deviation (pstdev), as in the sample. Sentence fragments
    with zero words remain in the distribution. Empty or wholly wordless text
    returns 0.0 to avoid division by zero; a single sentence also has zero spread.
    The combined scorer checks sample sufficiency before using these values.
    """
    lengths = [len(words(sentence)) for sentence in sentences(text)]
    if not lengths or not any(lengths):
        return 0.0
    return statistics.pstdev(lengths) / statistics.mean(lengths)


def type_token_ratio(text: str) -> float:
    """Return unique lowercase word tokens / total word tokens, or 0.0 if empty.

    Measure the whole input, without windows. TTR depends on text length;
    the supplied scoring anchors are intended for short prose under 200 words.
    """
    tokens = words(text)
    if not tokens:
        return 0.0
    return len(set(tokens)) / len(tokens)


def punctuation_density(text: str) -> float:
    """Return structural punctuation marks per word, or 0.0 without words.

    Count only commas, semicolons, colons, em/en dashes, and parentheses.
    Periods, question marks, exclamation marks, quotes, and hyphens do not count.
    This raw ratio can exceed 1.0; normalization clamps its contribution later.
    """
    word_count = len(words(text))
    if word_count == 0:
        return 0.0
    return len(re.findall(STRUCTURAL_PUNCTUATION_PATTERN, text)) / word_count


# ── Normalization and combination ───────────────────────────────────────────

def style_subscores(text: str) -> tuple[float, float, float] | None:
    """Return normalized (spread, punctuation, TTR) scores, or None if too short."""
    if len(sentences(text)) < MIN_STYLE_SENTENCES or len(words(text)) < MIN_STYLE_WORDS:
        return None

    spread_ai = clamp01(
        (SPREAD_HUMAN_ANCHOR - sentence_length_spread(text))
        / (SPREAD_HUMAN_ANCHOR - SPREAD_AI_ANCHOR)
    )
    punct_ai = clamp01(
        (punctuation_density(text) - PUNCTUATION_HUMAN_ANCHOR)
        / (PUNCTUATION_AI_ANCHOR - PUNCTUATION_HUMAN_ANCHOR)
    )
    ttr_ai = clamp01(
        (TTR_HUMAN_ANCHOR - type_token_ratio(text))
        / (TTR_HUMAN_ANCHOR - TTR_AI_ANCHOR)
    )
    return spread_ai, punct_ai, ttr_ai


def style_score(text: str) -> float | None:
    """Combine the three sub-scores, matching the supplied sample's None guard.

    Score = 0.50 * spread_ai + 0.20 * punct_ai + 0.30 * ttr_ai.
    Keep full precision for classification. The score is a heuristic, not a
    measured probability of AI authorship.
    """
    subscores = style_subscores(text)
    if subscores is None:
        return None
    spread_ai, punct_ai, ttr_ai = subscores
    score = clamp01(
        STYLE_WEIGHT_SPREAD * spread_ai
        + STYLE_WEIGHT_PUNCTUATION * punct_ai
        + STYLE_WEIGHT_TTR * ttr_ai
    )
    tokens = words(text)
    word_count = len(tokens)
    unique_count = len(set(tokens))
    punctuation_count = len(re.findall(STRUCTURAL_PUNCTUATION_PATTERN, text))
    density = punctuation_density(text)
    ttr = type_token_ratio(text)
    punctuation_unclamped = (
        (density - PUNCTUATION_HUMAN_ANCHOR)
        / (PUNCTUATION_AI_ANCHOR - PUNCTUATION_HUMAN_ANCHOR)
    )
    ttr_unclamped = (TTR_HUMAN_ANCHOR - ttr) / (TTR_HUMAN_ANCHOR - TTR_AI_ANCHOR)
    print(
        f"punctuation_density = structural_marks / words = "
        f"{punctuation_count} / {word_count} = {density:.6f}\n"
        f"punctuation_ai = clamp01(({density:.6f} - {PUNCTUATION_HUMAN_ANCHOR:g}) / "
        f"({PUNCTUATION_AI_ANCHOR:g} - {PUNCTUATION_HUMAN_ANCHOR:g})) "
        f"= clamp01({punctuation_unclamped:.6f}) = {punct_ai:.4f}\n"
        f"ttr = unique_lowercase_words / words = {unique_count} / {word_count} = {ttr:.6f}\n"
        f"ttr_ai = clamp01(({TTR_HUMAN_ANCHOR:g} - {ttr:.6f}) / "
        f"({TTR_HUMAN_ANCHOR:g} - {TTR_AI_ANCHOR:g})) "
        f"= clamp01({ttr_unclamped:.6f}) = {ttr_ai:.4f}\n"
        "style_score = (weight_spread * spread_ai) + "
        "(weight_punctuation * punctuation_ai) + (weight_ttr * ttr_ai)\n"
        f"            = ({STYLE_WEIGHT_SPREAD:.2f} * {spread_ai:.4f}) + "
        f"({STYLE_WEIGHT_PUNCTUATION:.2f} * {punct_ai:.4f}) + "
        f"({STYLE_WEIGHT_TTR:.2f} * {ttr_ai:.4f}) = {score:.4f}",
        flush=True,
    )
    return score


def style_signal(text: str) -> float:
    """Return the style score; raise TextTooShortError for the service's HTTP 400 handler."""
    score = style_score(text)
    if score is None:
        raise TextTooShortError(
            f"Text is too short for style analysis. Provide at least "
            f"{MIN_STYLE_SENTENCES} sentences and {MIN_STYLE_WORDS} words."
        )
    return score


def style_score_to_label(score: float | None) -> str:
    """Apply the supplied >= 0.65 AI, >= 0.40 uncertain, and < 0.40 human bands."""
    if score is None:
        return "INSUFFICIENT_DATA"
    if not math.isfinite(score) or not 0.0 <= score <= 1.0:
        raise ValueError("Style score must be finite and between 0.0 and 1.0.")
    if score >= STYLE_AI_THRESHOLD:
        return "Likely AI"
    if score >= STYLE_UNCERTAIN_THRESHOLD:
        return "Uncertain"
    return "Likely Human"


def style_classification(text: str) -> str:
    """Classify text without assigning authorship to an insufficient sample."""
    return style_score_to_label(style_score(text))


if __name__ == "__main__":
    import sys

    text = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else (
        "The system works well and supports a range of everyday tasks. "
        "It handles most cases correctly and provides useful results for users. "
        "People generally find the interface easy to understand, although some "
        "tasks require extra time and careful attention."
    )
    print(f"{len(sentences(text))} sentences, {len(words(text))} words\n")
    print(f"sentence_length_spread   {sentence_length_spread(text)}")
    print(f"punctuation_density      {punctuation_density(text)}   (marks per word)")
    print(f"type_token_ratio         {type_token_ratio(text)}")
    subscores = style_subscores(text)
    if subscores is not None:
        for name, value in zip(("spread_ai", "punctuation_ai", "ttr_ai"), subscores):
            print(f"{name:24}{value:.4f}")
    score = style_score(text)
    print(f"style_score              {score}")
    print(f"style_classification     {style_score_to_label(score)}")
    if score is None:
        print(f"Provide at least {MIN_STYLE_SENTENCES} sentences and {MIN_STYLE_WORDS} words.")
    print("Heuristic only; this score does not establish who wrote the text.")
