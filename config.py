"""
Settings for Provenance Guard.

Everything you're likely to change lives here, at the top, on purpose.

You'll edit the thresholds in Milestone 5 and the rate limits in unit 8.
"""

import os
from pathlib import Path

ROOT = Path(__file__).parent


# ─── The service ─────────────────────────────────────────────────────────────

# `127.0.0.1` is loopback — only your own machine can reach it, which is what
# you want all through units 7 and 8. A host somewhere else has to accept
# traffic from outside the box, and that means `0.0.0.0`. Setting the env var
# is how you get it; the default keeps your local `curl` commands unchanged.
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "5000"))

# Flask's debug mode gives anyone who can reach the service an interactive
# Python prompt inside your process. Fine on loopback, a gift to strangers
# anywhere else — so it turns itself off the moment HOST isn't loopback.
DEBUG = os.getenv("AI201_DEBUG", "1") == "1" and HOST in ("127.0.0.1", "localhost")

# ─── The local model ─────────────────────────────────────────────────────────
# Your first signal runs a language model ON YOUR OWN MACHINE. No account, no
# key, no card. Model weights download on first use; GPT-2 Large and Medium
# together need roughly 4.5 GB for their FP32 weights.
#
# What it measures: how *predictable* your text is to a language model. Text a
# model finds easy to predict tends to be text a model wrote.
#
# The first call is the slow one — ten to twenty seconds while the model loads,
# longer on an older laptop. After that it stays in memory and a submission
# takes a second or two. That cost is part of what you're learning: this is
# what running a model inline in a request actually looks like.

DETECTOR_MODEL = os.getenv("AI201_DETECTOR_MODEL", "gpt2-large")

# Both model signals use the same device. Auto prefers CUDA, then Apple's MPS
# GPU backend, then CPU. An explicit unavailable device produces an error.
INFERENCE_DEVICE = os.getenv("AI201_DEVICE", "auto").strip().lower()

# Longer text gives a steadier reading but takes longer. 400 tokens is roughly
# 300 words, which is enough for the signal to mean something.
DETECTOR_MAX_TOKENS = 400

DETECTOR_MIDPOINT = 15.3
DETECTOR_STEEPNESS = 4.6 #5.77

# ─── Scoring (Milestone 4) ───────────────────────────────────────────────────
# How much each signal counts toward the combined score.
#
# The model contributes 70% and style contributes 30%. Both scores point
# toward AI as they increase; the weights sum to 1.0.

WEIGHT_MODEL_SIGNAL = 0.65
WEIGHT_STYLE_SIGNAL = 0.35

# Within the model component, use this blend when Binoculars contributes.
# These weights sum to 1.0 and are separate from the model/style weights above.
MODEL_WEIGHT_PERPLEXITY = 0.5
MODEL_WEIGHT_BINOCULARS = 0.5


# Appeals compare three text variants with more weight on style (criteria.md). slightly relax the model since the person is asking for rewview as the person may have written instead of AI
APPEAL_WEIGHT_MODEL_SIGNAL = 0.6
APPEAL_WEIGHT_STYLE_SIGNAL = 0.4


# ─── Thresholds (Milestone 5) ────────────────────────────────────────────────
# Where one label becomes another. Scores run 0.0 (confidently human) to 1.0
# (confidently AI).
#
#   score < HUMAN_THRESHOLD          -> high-confidence human
#   between the two                  -> unsure
#   score > AI_THRESHOLD             -> high-confidence AI
#
# ⚠️ This is where your false-positive decision from Milestone 1 actually gets
# made. Widening the unsure band means fewer wrong accusations and more AI text
# getting through. There is no setting that avoids the trade — only settings
# that decide who pays for it.

HUMAN_THRESHOLD = 0.4
AI_THRESHOLD = 0.60

# A weighted average with nonnegative weights summing to 1.0 stays between
# its two inputs. With these weights, the model has more influence when the
# signals disagree.
#
# If a label you can't reach is the problem, the fix is upstream of the
# thresholds: a style signal that actually varies. `scoring.label_ranges()`
# prints the bands; the reachable range is a different question.


# ─── Rate limiting (UNIT 8) ──────────────────────────────────────────────────
# Enabled by default. Set AI201_RATE_LIMITS=0 to disable it explicitly.
#
# Think about two people: a real writer submitting their own work a few times
# an hour, and a script sending a thousand variations to map your thresholds.
# Your README has to say why your numbers and not others.

RATE_LIMITING_ENABLED = os.getenv("AI201_RATE_LIMITS", "1") == "1"

RATE_LIMIT_PER_MINUTE = 900
RATE_LIMIT_PER_DAY = 400

# Flask-Limiter warns loudly without this. In-memory is right for one laptop
# and wrong for anything real — a restart forgets every count, and two copies
# of the service wouldn't share limits.
RATE_LIMIT_STORAGE = "memory://"


# ─── Paths ───────────────────────────────────────────────────────────────────

LOG_DIR = ROOT / "logs"
AUDIT_LOG = LOG_DIR / "audit.jsonl"
SUBMISSIONS_FILE = LOG_DIR / "submissions.jsonl"
VERIFIED_HUMAN_CERTIFICATION_LOG = LOG_DIR / "verified_human_certification_log.jsonl"
RESULTS_DIR = ROOT / "results"

## ─── Binoculars constants- Thresholds ─────────────────────────────────────────────────────────
# ***deb..start stretch feature*** binocular***
# Binoculars signal (Hans et al., 2024): a second model-side score that divides
# the detector's perplexity by a cross-perplexity, so text that is predictable
# only because its TOPIC is predictable stops scoring as AI. Used by
# binoculars_signal.py; blended with model_signal through scoring.py.

# Set AI201_BINOCULARS=0 before starting the process to skip all Binoculars
# computation and performer loading. Perplexity and style remain active.

BINOCULARS_ENABLED = True
#BINOCULARS_ENABLED = os.getenv("AI201_BINOCULARS", "1") == "1"

# The second ("performer") model must share the observer's tokenizer.
# None = single-model mode, which uses the detector's own entropy instead
# and needs no extra download. It does not disable Binoculars computation.
BINOCULARS_PERFORMER = os.getenv("AI201_BINOCULARS_PERFORMER", "gpt2-medium")

# The raw Binoculars ratio B that maps to a 0.5 score. B runs LOW for AI text, so
# B below this scores toward 1 (AI) and above it toward 0 (human). Its scale depends
# on the model pair, so it must be re-fit whenever either model changes.
# Fit for GPT-2 Large/Medium on 2026-11-11 using 150 AI + 150 human HC3
# answers of 50–100 words, with a separate 300-answer validation split.
# See results/calibration_2026-11-11_large_medium/hc3_50_100/report.md.
BINOCULARS_MIDPOINT = 0.762

# How sharply the 0-1 score moves either side of the midpoint. Fitted together
# with the midpoint above; refit both when changing the model pair.
BINOCULARS_STEEPNESS = 25 #35.5

# Below this many whitespace-separated words, use perplexity alone for the
# model component. At or above it, use 70% perplexity and 30% Binoculars.
# This 250-word gate was selected by the user after the short-text comparison;
# the earlier calibration reports record the previous gate and blend.
# When enabled, Binoculars is still computed below the gate, with
# binoculars_used: false.
BINOCULARS_MIN_WORDS = 50

# Positions skipped at the start of the text when averaging, because the first few
# tokens are high-surprisal regardless of author. 0 = use every position. Changing
# this changes the B scale, so re-fit BINOCULARS_MIDPOINT afterwards.
BINOCULARS_SKIP_TOKENS = 0

# ── How to calibrate ─────────────────────────────────────────────────────────
# Samples: *.json files with a "text" field, named with "human", "ai" or
# "borderline" so the scripts can label them. Borderline files are scored but
# not fitted. The prepared short-text set has separate calibration/validation
# folders. Fit only on calibration; use validation to evaluate fixed settings.
# Include other generators, writers and lengths before generalizing the results.
#
# 1. Fit the Binoculars midpoint/steepness (re-run after changing either model
#    or SKIP_TOKENS, since the B scale moves with them):
#        python calibrate.py calibration_samples/hc3_50_100/calibration --fit --max-fpr 0.2
#    Prints one row per sample (ppl, raw B, both signals), then two answers:
#    rule 1 = logistic fit (gives midpoint AND steepness), rule 2 = highest-recall
#    midpoint that keeps human false positives under --max-fpr (default 0.4).
#    These rules optimize different objectives. Check their effect on the
#    combined score before choosing a curve; the current values use rule 1.
#
# 2. Check the combined score (weights + AI cutoff), which is where the FPR
#    ceiling actually has to hold:
#        python calibrate_combined.py calibration_samples/hc3_50_100/calibration --max-fpr 0.2 --min-words 80
#    Prints every signal and the combined score with the same blend rounding
#    (including BINOCULARS_MIN_WORDS), then for each WEIGHT_MODEL_SIGNAL the band
#    of AI cutoffs that keeps human-flagged <= --max-fpr. A wide band means the
#    data isn't constraining the cutoff; add harder samples before changing it.
#    --min-words N repeats the sweep for samples above and below N words
#    (reporting only; it does NOT change BINOCULARS_MIN_WORDS).
#
# 3. Restart app.py and re-run the curl loop; combined_score in the responses
#    must match the "combined" column from step 2. Record sample counts, the
#    rule used and the resulting values in the README.

# ***deb ..end of stretch feature*** binocular_______***
