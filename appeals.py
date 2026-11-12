"""Reassess three versions of a submission using the appeal acceptance rule."""

from collections import Counter
import re

import config
import detector
import scoring
import stylometry


UNSURE_MESSAGE = (
    "Based on revaluation we do not have enough evidence to determine how this "
    "text was written. Your appeal has been recorded."
)
AI_REVIEW_MESSAGE = (
    "Due to the nature of the mathematical computation involved in arriving at "
    "the conclusion, it is possible that the text has been evaluated as "
    "AI-written even though it was written by a human. If that is the case, "
    "please request human re-evaluation and submit earlier versions of the work "
    "so it can be evaluated by a person."
)
CONFIRMATION = "Your appeal has been recorded. Your submission is marked for review."


def text_variants(text: str) -> list[tuple[str, str]]:
    """Remove boundary sentences using stylometry's sentence-splitting rule.

    Preserve whitespace inside the remaining text so only the intended
    sentence is removed, rather than also reformatting the passage.
    """
    stripped = text.strip()
    boundaries = list(re.finditer(r"(?<=[.!?])\s+", stripped))
    return [
        ("original", text),
        ("without_first_sentence", stripped[boundaries[0].end():] if boundaries else ""),
        ("without_last_sentence", stripped[:boundaries[-1].start()] if boundaries else ""),
    ]


def reassess(text: str | None) -> dict:
    """Return three evaluations and their majority label; ties are unsure.

    Unscorable variants vote unsure and retain null scores where no score was
    obtained. Missing historical text never becomes a fabricated human score.
    """
    source_available = isinstance(text, str) and bool(text.strip())
    variants = text_variants(text if source_available else "")
    evaluations = []
    for variant, variant_text in variants:
        evaluation = {
            "variant": variant,
            "status": "unavailable",
            "model_score": None,
            "style_score": None,
            "combined_score": None,
            "label": "unsure",
        }
        if not source_available:
            evaluation["reason"] = "original_text_unavailable"
        else:
            try:
                evaluation["style_score"] = stylometry.style_signal(variant_text)
                evaluation["model_score"] = detector.model_signal(variant_text)
                evaluation["combined_score"] = scoring.combine_appeal_signals(
                    evaluation["model_score"], evaluation["style_score"]
                )
                evaluation["label"], _ = scoring.score_to_label(evaluation["combined_score"])
                evaluation["status"] = "scored"
            except (detector.TextTooShortError, stylometry.TextTooShortError):
                evaluation["status"] = "insufficient_data"
                evaluation["reason"] = "text_too_short"
            except detector.DetectorUnavailable:
                evaluation["reason"] = "model_unavailable"
        evaluations.append(evaluation)

    counts = Counter(evaluation["label"] for evaluation in evaluations)
    votes = {label: counts[label] for label in ("human", "unsure", "ai")}
    label = next((label for label, count in votes.items() if count >= 2), "unsure")
    if label == "unsure":
        message = UNSURE_MESSAGE
    elif label == "ai":
        message = f"{CONFIRMATION} {AI_REVIEW_MESSAGE}"
    else:
        message = CONFIRMATION
    return {
        "label": label,
        "label_text": scoring.LABEL_TEXT[label],
        "message": message,
        "votes": votes,
        "evaluations": evaluations,
        "weights": {
            "model": config.APPEAL_WEIGHT_MODEL_SIGNAL,
            "style": config.APPEAL_WEIGHT_STYLE_SIGNAL,
        },
    }
