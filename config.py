"""
Settings for Provenance Guard.

Everything you're likely to change lives here, at the top, on purpose.

You'll edit the thresholds in Milestone 5 and the rate limits in unit 8.
"""

import os
import math
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

# Server-side request budget; model work is isolated and killed on expiry.
# Network transfer and time spent waiting outside Flask are not part of this budget.
REQUEST_TIMEOUT_ENABLED = os.getenv("AI201_REQUEST_TIMEOUT_ENABLED", "1") == "1"
REQUEST_TIMEOUT_SECONDS = float(os.getenv("AI201_REQUEST_TIMEOUT_SECONDS", "3"))
# Keep isolation on in deployments, including when the deadline is disabled.
# The inline mode is for existing in-process mock-based tests only.
INFERENCE_PROCESS_ENABLED = os.getenv("AI201_INFERENCE_PROCESS_ENABLED", "1") == "1"
CIRCUIT_BREAKER_ENABLED = os.getenv("AI201_CIRCUIT_BREAKER_ENABLED", "1") == "1"
CIRCUIT_BREAKER_FAILURE_THRESHOLD = int(os.getenv("AI201_CIRCUIT_BREAKER_FAILURE_THRESHOLD", "3"))
CIRCUIT_BREAKER_RECOVERY_SECONDS = float(os.getenv("AI201_CIRCUIT_BREAKER_RECOVERY_SECONDS", "30"))
OPERATIONAL_METRICS_ENABLED = os.getenv("AI201_OPERATIONAL_METRICS_ENABLED", "1") == "1"
OPERATIONAL_LOG_FILENAME = "operational_metrics.jsonl"
METRICS_DEFAULT_HOURS = 24.0
METRICS_MAX_HOURS = 720.0

if not math.isfinite(REQUEST_TIMEOUT_SECONDS) or REQUEST_TIMEOUT_SECONDS <= 0:
    raise ValueError("AI201_REQUEST_TIMEOUT_SECONDS must be a positive finite number.")
if CIRCUIT_BREAKER_FAILURE_THRESHOLD < 1:
    raise ValueError("AI201_CIRCUIT_BREAKER_FAILURE_THRESHOLD must be at least 1.")
if not math.isfinite(CIRCUIT_BREAKER_RECOVERY_SECONDS) or CIRCUIT_BREAKER_RECOVERY_SECONDS <= 0:
    raise ValueError("AI201_CIRCUIT_BREAKER_RECOVERY_SECONDS must be a positive finite number.")

# ─── The local model ─────────────────────────────────────────────────────────
# Your first signal runs a language model ON YOUR OWN MACHINE. No account, no
# key, no card. It downloads about 550 MB the first time — do that before
# class, not during it.
#
# What it measures: how *predictable* your text is to a language model. Text a
# model finds easy to predict tends to be text a model wrote.
#
# The serving process starts a separate CPU worker to load the models. Wait
# for /health to report inference_ready before scoring. Loading is outside the
# request budget; subsequent inference uses the persistent worker in memory.

DETECTOR_MODEL = os.getenv("AI201_DETECTOR_MODEL", "gpt2")

# Longer text gives a steadier reading but takes longer. 400 tokens is roughly
# 300 words, which is enough for the signal to mean something.
DETECTOR_MAX_TOKENS = 400


# ─── Scoring (Milestone 4) ───────────────────────────────────────────────────
# How much each signal counts toward the combined score.
#
# The model contributes 70% and style contributes 30%. Both scores point
# toward AI as they increase; the weights sum to 1.0.

WEIGHT_MODEL_SIGNAL = 0.7
WEIGHT_STYLE_SIGNAL = 0.3


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

HUMAN_THRESHOLD = 0.45
AI_THRESHOLD = 0.60

# A weighted average with nonnegative weights summing to 1.0 stays between
# its two inputs. With these weights, the model has more influence when the
# signals disagree.
#
# If a label you can't reach is the problem, the fix is upstream of the
# thresholds: a style signal that actually varies. `scoring.label_ranges()`
# prints the bands; the reachable range is a different question.


# ─── Rate limiting (UNIT 8) ──────────────────────────────────────────────────
# Keep the limiter on for the Unit 8 measurements. Change this Boolean and
# restart the service if you need to disable it outside those measurements.
#
# Think about two people: a real writer submitting their own work a few times
# an hour, and a script sending a thousand variations to map your thresholds.
# Your README has to say why your numbers and not others.

RATE_LIMITING_ENABLED = True

# These same limits apply independently to each IP and each valid creator ID.
RATE_LIMIT_PER_MINUTE = 9
RATE_LIMIT_PER_DAY = 400

# Flask-Limiter warns loudly without this. In-memory is right for one laptop
# and wrong for anything real — a restart forgets every count, and two copies
# of the service wouldn't share limits.
RATE_LIMIT_STORAGE = "memory://"


# ─── Paths ───────────────────────────────────────────────────────────────────

# Resolve logs relative to the application directory in IDE, CLI, and Docker runs.
# Compose mounts the deployment's ./logs here so the same files are visible on the host.
LOG_DIR = ROOT / "logs"
AUDIT_LOG = LOG_DIR / "audit.jsonl"
SUBMISSIONS_FILE = LOG_DIR / "submissions.jsonl"
# Shared by automated human assessments and approved manual reviews.
CERTIFICATION_LOG = LOG_DIR / "certification_log.jsonl"
RESULTS_DIR = ROOT / "results"

## ─── Binoculars constants- Thresholds ─────────────────────────────────────────────────────────
# ***deb..start stretch feature*** binocular***
# Binoculars signal (Hans et al., 2024): a second model-side score that divides
# the detector's perplexity by a cross-perplexity, so text that is predictable
# only because its TOPIC is predictable stops scoring as AI. Used by
# binoculars_signal.py; averaged 50/50 with model_signal in app.py.

# The second ("performer") model. Must share gpt2's tokenizer: distilgpt2 (~330 MB,
# fast) or gpt2-medium (~1.5 GB, separates better). None = single-model mode, which
# uses the detector's own entropy instead and needs no extra download.
BINOCULARS_PERFORMER = "distilgpt2"

# The raw Binoculars ratio B that maps to a 0.5 score. B runs LOW for AI text, so
# B below this scores toward 1 (AI) and above it toward 0 (human). Its scale depends
# on the model pair, so it must be re-fit whenever BINOCULARS_PERFORMER changes.
# Fit on 2026-11-10 from 3 ai + 2 human samples (rule 1 gave 0.849, rule 2 0.830).
BINOCULARS_MIDPOINT = 0.85

# How sharply the 0-1 score moves either side of the midpoint. With a GPT-2 pair the
# useful range of B is narrow (~0.65-0.95), so this is steeper than model_signal's 1.6.
# Lower it if scores pile up at 0 and 1; raise it if everything sits near 0.5.
BINOCULARS_STEEPNESS = 20.0

# Below this many words the model term is the perplexity signal alone; at or above
# it, perplexity and Binoculars are averaged. Binoculars loses accuracy on short
# input (paper), and on our short samples it ranked a plain human paragraph as more
# AI-like than an AI one. Chosen from our data: 100 catches the short AI sample
# without changing any human label. The score is still computed and returned below
# the threshold (binoculars_used: false) so eval reports show what it would have said.
BINOCULARS_MIN_WORDS = 100

# Positions skipped at the start of the text when averaging, because the first few
# tokens are high-surprisal regardless of author. 0 = use every position. Changing
# this changes the B scale, so re-fit BINOCULARS_MIDPOINT afterwards.
BINOCULARS_SKIP_TOKENS = 0

# ── How to calibrate ─────────────────────────────────────────────────────────
# Samples: *.json files with a "text" field, named with "human", "ai" or
# "borderline" so the scripts can label them. Borderline files are scored but
# not fitted. Aim for 5+ per class, mixed lengths, more than one generator and
# more than one human writer, including plainly-written human text.
#
# 1. Fit the Binoculars midpoint/steepness (re-run after changing PERFORMER or
#    SKIP_TOKENS, since the B scale moves with them):
#        python calibrate.py Milestone4_test_sample samples --fit
#    Prints one row per sample (ppl, raw B, both signals), then two answers:
#    rule 1 = logistic fit (gives midpoint AND steepness), rule 2 = highest-recall
#    midpoint that keeps human false positives under --max-fpr (default 0.4).
#    If they agree, use rule 1; if rule 2 is higher, prefer it. Copy the numbers
#    into BINOCULARS_MIDPOINT / BINOCULARS_STEEPNESS, re-run without --fit to
#    confirm binoc_sig reads high for ai and low for human.
#
# 2. Check the combined score (weights + AI cutoff), which is where the FPR
#    ceiling actually has to hold:
#        python calibrate_combined.py Milestone4_test_sample samples --min-words 100
#    Prints every signal and the combined score exactly as /submit computes it
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
