"""
Binoculars signal — a drop-in companion to model_signal.

Binoculars (Hans et al., 2024) scores text with TWO models:

    observer   : how surprised is it by the actual tokens?  (log-perplexity)
    performer  : what would a machine have written next, at every position?

    cross-perplexity = at each position, the observer's expected surprise if the
                       next token were drawn from the performer's distribution
    B = log_perplexity / cross_perplexity          (low  ->  AI)

Dividing by cross-perplexity cancels out how predictable the *topic* is, which
is the main cause of the false positives named in model_signal's docstring:
plain human writing on an ordinary subject has low perplexity, but it also has
low cross-perplexity, so the ratio stays high.

Two modes, chosen by config:

    config.BINOCULARS_PERFORMER = "distilgpt2"   # true Binoculars (two models)
    config.BINOCULARS_PERFORMER = None           # single-model fallback

With no performer, the cross-perplexity collapses to the observer's own
entropy and B becomes NLL / entropy. Still useful, measurably weaker.

The observer is config.DETECTOR_MODEL, the same model model_signal uses, so
the two signals share one download.

    from binoculars_signal import binoculars_signal
    score = binoculars_signal("some text")     # 0.0 human-ish … 1.0 AI-ish
"""

import math

import config

# Your existing perplexity module: reuses its _load() and error classes.
# It's imported as `detector` in the starter; fall back to other common names.
try:
    import detector as ms
except ImportError:
    try:
        from detector import model_signal as ms   # detector/ package with model_signal.py inside
    except ImportError:
        import model_signal as ms                  # standalone model_signal.py
if not hasattr(ms, "_load"):
    raise ImportError(
        "Found a 'detector' module but it has no _load(); edit the import at the top of "
        "binoculars_signal.py to point at the file that defines perplexity()/model_signal()."
    )

# ---- config with defaults, so this works even if config.py hasn't been edited
PERFORMER = getattr(config, "BINOCULARS_PERFORMER", "distilgpt2")
MIDPOINT = getattr(config, "BINOCULARS_MIDPOINT", 0.90)    # B that maps to 0.5
STEEPNESS = getattr(config, "BINOCULARS_STEEPNESS", 12.0)

_performer = None


def _load_performer():
    """Load the second model once. Must share the observer's tokenizer."""
    global _performer
    if _performer is not None or PERFORMER is None:
        return _performer

    from transformers import AutoModelForCausalLM, AutoTokenizer

    try:
        _performer = AutoModelForCausalLM.from_pretrained(PERFORMER).eval()
        perf_tok = AutoTokenizer.from_pretrained(PERFORMER)
    except Exception as exc:  # noqa: BLE001
        raise ms.DetectorUnavailable(f"Couldn't load performer '{PERFORMER}': {exc}") from exc

    _, obs_tok = ms._load()
    if perf_tok.get_vocab() != obs_tok.get_vocab():
        raise ms.DetectorUnavailable(
            f"'{PERFORMER}' and '{config.DETECTOR_MODEL}' use different tokenizers. "
            f"Binoculars needs a pair from the same family (gpt2 / distilgpt2 / gpt2-medium)."
        )
    return _performer


def binoculars_score(text: str) -> dict:
    """
    Raw numbers. 'B' is the Binoculars ratio (lower = more likely AI).
    Also returns the pieces so you can log or plot them separately.
    """
    import torch
    import torch.nn.functional as F

    observer, tokenizer = ms._load()
    performer = _load_performer()

    encoded = tokenizer(text, return_tensors="pt", truncation=True,
                        max_length=config.DETECTOR_MAX_TOKENS)
    input_ids = encoded["input_ids"]
    if input_ids.shape[1] < 3:
        raise ms.TextTooShortError("Text is too short to score — a few sentences at least.")

    with torch.no_grad():
        obs_logits = observer(input_ids).logits[:, :-1, :]      # predicts tokens 1..T-1
        targets = input_ids[:, 1:]

        # (1) observer's log-perplexity = mean NLL of the actual tokens
        log_ppl = F.cross_entropy(obs_logits.transpose(1, 2), targets).item()

        # (2) cross-perplexity
        logp_obs = F.log_softmax(obs_logits, dim=-1)
        if performer is not None:
            perf_logits = performer(input_ids).logits[:, :-1, :]
            p_perf = F.softmax(perf_logits, dim=-1)
            x_ppl = -(p_perf * logp_obs).sum(-1).mean().item()
        else:
            # single-model fallback: cross-entropy of the observer with itself = its entropy
            x_ppl = -(logp_obs.exp() * logp_obs).sum(-1).mean().item()

    return {
        "B": log_ppl / x_ppl,
        "log_perplexity": log_ppl,
        "perplexity": math.exp(log_ppl),
        "cross_perplexity": x_ppl,
        "mode": "binoculars" if performer is not None else "single-model (NLL/entropy)",
    }


def binoculars_signal(text: str) -> float:
    """
    The signal as a 0–1 score, **higher means more likely AI**, so it combines
    with model_signal and the style score the same way.

    B is roughly 0.6–1.0 for AI text and 0.9–1.4 for human text with a GPT-2
    pair; the exact split depends on the pair, so calibrate MIDPOINT on your
    four Milestone 4 inputs plus a plainly-written human paragraph, and say
    in the README where you set it.
    """
    b = binoculars_score(text)["B"]
    # Logistic on B, flipped: low B -> high AI score.
    score = 1.0 / (1.0 + math.exp(STEEPNESS * (b - MIDPOINT)))
    return round(min(max(score, 0.0), 1.0), 4)


def warm_up() -> str:
    ms._load()
    _load_performer()
    return f"{config.DETECTOR_MODEL} + {PERFORMER or '(single-model)'} loaded and ready."


if __name__ == "__main__":
    import sys

    text = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else (
        "The implementation of the proposed framework requires careful "
        "consideration of several key factors. First, it is important to "
        "note that the system must be able to handle a wide variety of "
        "different inputs. Additionally, the overall performance of the "
        "solution depends on a number of important variables."
    )
    r = binoculars_score(text)
    print(f"mode               {r['mode']}")
    print(f"perplexity         {r['perplexity']:.1f}")
    print(f"cross-perplexity   {r['cross_perplexity']:.3f}")
    print(f"B                  {r['B']:.3f}   (lower = more likely AI)")
    print(f"binoculars_signal  {binoculars_signal(text):.4f}   (higher = more likely AI)")