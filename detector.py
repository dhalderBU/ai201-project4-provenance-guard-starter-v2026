"""
Signal one: the model signal.

This is the signal that "reads the text for meaning". It runs a language model
on your own machine and asks one question: **how predictable is this text?**

The idea is the one every AI-detection product is built on. A language model
writes by repeatedly picking a likely next word, so text a model produced tends
to be text a model finds easy to predict. Human writing wanders more — odd word
choices, abrupt turns, the specific rather than the typical.

The measure is called **perplexity**. Low perplexity means "I could have
guessed this"; high perplexity means "that surprised me". This module turns
that into a 0–1 score where **higher means more likely AI**.

    from detector import model_signal
    score = model_signal("some text")     # 0.0 human-ish … 1.0 AI-ish

Everything runs locally. No account, no key, no card.

⚠️ **The blind spot, which you have to name in Milestone 1.**

Predictability is not the same thing as authorship. What this signal actually
rewards is **common words in short, ordinary sentences** — and plenty of real
people write that way.

Someone writing in a second language, sticking to vocabulary they're sure of.
A younger writer. Anyone writing plainly on purpose. Measured against gpt2,
writing like that scores about as machine-like as machine writing does.

The reverse trips people up too: dense, ornate prose full of rare words often
scores as *human* on this signal, because rare words are exactly what a
language model fails to predict. Formality on its own doesn't decide it.

So the writers this signal is most likely to accuse are the ones with the
least room to argue back. That is structural rather than a bug you can fix,
and it is the person Milestone 1 asks you to follow through your service.

Don't take that on trust — it's a claim you can check. Milestone 4 has you run
four calibration inputs. Add a plainly-written human paragraph to them and see
for yourself where it lands.
"""

import math

import config

_model = None
_tokenizer = None


class DetectorUnavailable(RuntimeError):
    """The model or requested inference device could not be loaded."""


class TextTooShortError(ValueError):
    """The input has too few tokens for the detector to score."""


def inference_device():
    """Choose the shared model device, honoring an explicit override."""
    import torch

    requested = config.INFERENCE_DEVICE
    if requested not in {"auto", "cpu", "cuda", "mps"}:
        raise DetectorUnavailable(
            f"Unknown AI201_DEVICE '{requested}'. Use auto, cpu, cuda, or mps."
        )
    if requested == "auto":
        if torch.cuda.is_available():
            return torch.device("cuda")
        if torch.backends.mps.is_available():
            return torch.device("mps")
        return torch.device("cpu")
    if requested == "cuda" and not torch.cuda.is_available():
        raise DetectorUnavailable("AI201_DEVICE=cuda requested, but CUDA is unavailable.")
    if requested == "mps" and not torch.backends.mps.is_available():
        raise DetectorUnavailable("AI201_DEVICE=mps requested, but Apple's MPS GPU backend is unavailable.")
    return torch.device(requested)


def _load():
    """Load and cache the model on the selected device after successful setup."""
    global _model, _tokenizer
    if _model is not None:
        return _model, _tokenizer

    try:
        import torch  # noqa: F401
        from transformers import AutoModelForCausalLM, AutoTokenizer
    except ImportError as exc:
        raise DetectorUnavailable(
            f"transformers or torch isn't installed ({exc}).\n"
            f"Run: pip install -r requirements.txt"
        ) from exc

    try:
        device = inference_device()
        tokenizer = AutoTokenizer.from_pretrained(config.DETECTOR_MODEL)
        model = AutoModelForCausalLM.from_pretrained(config.DETECTOR_MODEL)
        model.to(device).eval()
    except Exception as exc:  # noqa: BLE001
        raise DetectorUnavailable(
            f"Couldn't load '{config.DETECTOR_MODEL}': {exc}\n"
            "Check the selected device, available memory, and model download."
        ) from exc

    _model, _tokenizer = model, tokenizer
    return _model, _tokenizer


def perplexity(text: str) -> float:
    """
    How surprised the model is by this text. Lower means more predictable.

    Returns a positive number. Typical values land roughly between 10 and 200,
    but that range shifts with topic and length, which is one reason the raw
    number isn't what you score on.
    """
    import torch

    model, tokenizer = _load()

    encoded = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        max_length=config.DETECTOR_MAX_TOKENS,
    )
    input_ids = encoded["input_ids"].to(model.device)

    # Two tokens is not enough to be surprised by anything.
    if input_ids.shape[1] < 3:
        # raise ValueError("Text is too short to score — a few sentences at least.")
        # Give the route a specific error it can return as a bad request.
        raise TextTooShortError("Text is too short to score — a few sentences at least.")

    with torch.no_grad():
        output = model(input_ids, labels=input_ids)

    # The model's loss here IS mean negative log-likelihood per token.
    return float(math.exp(output.loss.item()))


def model_signal(text: str) -> float:
    """
    The signal, as a 0–1 score. **Higher means more likely AI.**

    Perplexity is unbounded and roughly log-distributed, so it gets squashed
    onto 0–1 rather than clipped. The midpoint below is the perplexity that
    maps to 0.5 — text this surprising is a coin flip.

    You may want to move that midpoint once you've run the four calibration
    inputs in Milestone 4 and seen what your own text actually scores. If you
    do, say so in your README: it's a scoring decision, not a detail.
    """
    ppl = perplexity(text)

    #midpoint = 45.0    # perplexity that scores 0.5
    #steepness = 1.6    # how sharply the score moves either side of it

        # ***deb..start stretch feature*** detector calibration***
    # (comment explaining why the constants moved to config)
    midpoint = getattr(config, "DETECTOR_MIDPOINT", 45.0)      # perplexity that scores 0.5
    steepness = getattr(config, "DETECTOR_STEEPNESS", 1.6)    # how sharply the score moves either side of it
    # ***deb ..end of stretch feature*** detector calibration***

    # Logistic on log-perplexity. Low perplexity -> high AI score.
    score = 1.0 / (1.0 + (ppl / midpoint) ** steepness)
    return round(min(max(score, 0.0), 1.0), 4)


def warm_up() -> str:
    """Load the model without scoring anything. Run this before class."""
    model, _ = _load()
    return f"{config.DETECTOR_MODEL} loaded and ready on {model.device}."


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        text = " ".join(sys.argv[1:])
    else:
        text = (
            "The implementation of the proposed framework requires careful "
            "consideration of several key factors. First, it is important to "
            "note that the system must be able to handle a wide variety of "
            "different inputs. Additionally, the overall performance of the "
            "solution depends on a number of important variables."
        )
        print("(no text given — scoring a sample)\n")

    print(f"Loading {config.DETECTOR_MODEL} (weights download on first use)…")
    print(warm_up())
    print(f"perplexity     {perplexity(text):.1f}")
    print(f"model_signal   {model_signal(text):.4f}   (higher = more likely AI)")
