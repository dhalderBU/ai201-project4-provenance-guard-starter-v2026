#!/usr/bin/env python3
"""
Provenance Guard — the web service.

    python app.py

Then, in another terminal:

    curl -X POST http://127.0.0.1:5000/ping \
      -H "Content-Type: application/json" \
      -d '{"message": "hello"}'

That's the example route. It works right now, before you've written anything.
**Leave it alone** — it's your control. When something breaks later, check that
`/ping` still answers: if it does, the problem is in your handler; if it
doesn't, it's the service itself.

Routes:

    POST /ping        the worked example. Already works. Don't edit it
    POST /submit      ← YOU BUILD THIS (Milestone 3, 4, 5)
    POST /appeal      ← YOU BUILD THIS (Milestone 5)
    POST /verification/review  reviewer decision: certified or not_certified
    GET  /verification/review/<id>  original submission and human-review evidence
    GET  /content/<id> the item's latest recorded status
    GET  /log         the audit log. Already works
    GET  /health      is the service up, and is the model loaded
"""

# from email.mime import text  # Not needed: text comes from the JSON payload.
import uuid

from flask import Flask, jsonify, request

import audit
import config
import submissions
import verification

app = Flask(__name__)


@app.errorhandler(verification.VerificationError)
def verification_error(exc):
    return jsonify({"error": exc.code, "message": str(exc)}), exc.status_code


# ── Rate limiting — UNIT 8 ────────────────────────────────────────────────────
# Enabled by default. The /submit decorator applies both limits from config.py.
# AI201_RATE_LIMITS=0 disables limiting and leaves the route untouched.
#
# The storage backend is preconfigured, which stops Flask-Limiter printing a
# warning on every start. In-memory is right for one laptop and wrong for
# anything real — a restart forgets every count.

class _LimiterOff:
    """
    Stands in for the real limiter while rate limiting is off.

    It makes @limiter.limit(...) a decorator that returns the route untouched.
    """

    def limit(self, *args, **kwargs):
        return lambda view: view


limiter = _LimiterOff()
if config.RATE_LIMITING_ENABLED:
    from flask_limiter import Limiter
    from flask_limiter.util import get_remote_address

    def rate_limit_key():
        """
        Who a request counts against.

        Falling back to the caller's address is the easy version. Unit 8's
        stretch asks about per-creator limits instead — and the difference
        matters: one script can look like a thousand callers, and one household
        can look like one.
        """
        payload = request.get_json(silent=True)
        # A body that parses as JSON but isn't an object — a bare list or
        # string — has no .get. Without this guard the key function raises
        # BEFORE the route runs, and a malformed request becomes a 500 that
        # looks like your handler crashed when your handler never ran.
        if not isinstance(payload, dict):
            return get_remote_address()
        creator = payload.get("creator_id")
        return creator if isinstance(creator, str) and creator.strip() else get_remote_address()

    limiter = Limiter(
        key_func=rate_limit_key,
        app=app,
        storage_uri=config.RATE_LIMIT_STORAGE,
        default_limits=[],
        headers_enabled=True,
    )

    @app.errorhandler(429)
    def rate_limited(exc):
        """
        A rejected request still leaves a trace.

        ⚠️ An attack that shows up only as an absence is one you'll never find.
        """
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            payload = {}
        audit.log_rejection(
            creator_id=payload.get("creator_id", "unknown"),
            reason="rate_limited",
            limit=str(exc.description),
        )
        return jsonify({
            "error": "rate_limited",
            "message": "Too many submissions. Please wait before trying again.",
            "limit": str(exc.description),
        }), 429


# ── The worked example. Already works. Don't edit. ────────────────────────────

@app.post("/ping")
def ping():
    """
    Everything a route needs, in six lines.

    JSON arrives as a dict. You pull things out of it. You return a dict and
    the framework turns it into a response. That's the whole idea.
    """
    payload = request.get_json(silent=True) or {}
    return jsonify({
        "ok": True,
        "you_sent": payload.get("message"),
        "service": "provenance-guard",
    })


@app.get("/health")
def health():
    """Is the service up, and has the model been downloaded yet?"""
    import detector

    loaded = detector._model is not None

    # ***deb..start stretch feature*** binocular***
    # Report the second (performer) model the Binoculars signal needs.
    # PERFORMER is None when running in single-model mode, which needs no extra download.
    import binoculars_signal

    binoculars_performer = binoculars_signal.PERFORMER
    binoculars_loaded = (
        loaded if binoculars_performer is None          # single-model mode reuses the detector
        else binoculars_signal._performer is not None
    )
    # ***deb ..end of stretch feature*** binocular***

    return jsonify({
        "ok": True,
        "detector_model": config.DETECTOR_MODEL,
        "detector_loaded": loaded,
        "device_setting": config.INFERENCE_DEVICE,
        "inference_device": str(detector._model.device) if loaded else None,
        # ***deb..start stretch feature*** binocular***
        "binoculars_enabled": config.BINOCULARS_ENABLED,
        "binoculars_performer": binoculars_performer,
        "binoculars_loaded": binoculars_loaded,
        # ***deb ..end of stretch feature*** binocular***
        "rate_limiting": config.RATE_LIMITING_ENABLED,
        "log_entries": len(audit.read_entries()),
    })


# ── YOU BUILD THIS ────────────────────────────────────────────────────────────

@app.post("/submit")
@limiter.limit(f"{config.RATE_LIMIT_PER_MINUTE}/minute;{config.RATE_LIMIT_PER_DAY}/day")
def submit():
    """
    Take a piece of text, decide about it, log the decision, answer.
    ← TODO — Milestones 3, 4 and 5

    Expects JSON:
        {"text": "...", "creator_id": "..."}

    Should return JSON with, at minimum:
        {"content_id": "...", "guess": "...", "confidence": 0.0, "label": "...",
         "model_score": 0.0, "style_score": 0.0}

    ⚠️ **Both signal scores go in the response, not just the log.** Unit 8's
    `run_attacks.py` and `run_eval.py` read `model_score` and `style_score`
    straight off this response and put them in your reports. Leave them out and
    every row of next unit's evidence says `null` — which is exactly the
    diagnostic you need to name a stage and a mechanism. You do not want to
    find that out after running the attack set.

    ─────────────────────────────────────────────────────────────────────────
    Build it in three passes. Do not skip ahead — the ordering is how you tell
    a broken route from a broken signal.

    **Milestone 3 — the route answers.**
      1. Return a hardcoded response. Confirm `curl` gets it back before you
         add any logic at all.
      2. Then pull `text` and `creator_id` out of the payload.
      3. Then call ONE signal — `detector.model_signal(text)` — and put the
         real number in. Leave confidence and label as placeholders.
      4. Log every submission with `audit.log_decision(...)`. The content_id
         matters: `/appeal` needs it, and a student who skips it rebuilds this
         whole flow later.

    **Milestone 4 — the second signal and the score.**
      5. Add `stylometry.style_signal(text)`.
      6. Combine them with `scoring.combine_signals(...)`.
      7. Log BOTH signal scores alongside the combined one, and put them in the
         response too. Next unit you can't diagnose anything without them.

    **Milestone 5 — the label.**
      8. `scoring.score_to_label(...)` and put the real label in the response.

    ─────────────────────────────────────────────────────────────────────────
    Worth deciding early, because unit 8's attack set will decide it for you:
    what should this do when `text` is missing, empty, or enormous? A crash on
    a malformed input is one of the most common real failures there is.
    """
    # Flask decodes valid JSON escapes and preserves backticks in the text.
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({
            "error": "bad_request",
            "message": (
                "Invalid JSON. Send a JSON object containing text and creator_id."
            ),
        }), 400

    text = payload.get("text")
    creator_id = payload.get("creator_id", "unknown")

    # Validate the text before calling the detector.
    if not isinstance(text, str) or not text.strip():
        return jsonify({"error": "bad_request", "message": "Send JSON with a non-empty \"text\"."}), 400

    # Step 3 - one real signal that we first tested from the terminal
    # python detector.py "some text"
    import detector

    #model_score=0.5

    # Below lines commented so as to setup styling with default values uncomment once the logic is implemented
    try:
        perplexity_score = detector.model_signal(text)
    except detector.TextTooShortError as exc:
        return jsonify({"error": "bad_request", "message": str(exc)}), 400

    # ***deb..start stretch feature*** binocular***
    # Second model-side signal: Binoculars (Hans et al., 2024). It divides the
    # detector's perplexity by a cross-perplexity so that text which is
    # predictable only because its TOPIC is predictable stops scoring as AI.
    #
    # The model component uses the configured perplexity/Binoculars weights.
    # scoring.combine_signals() then combines that component with style.
    #
    # If the second model can't load (no download yet, no disk), the route
    # degrades to the perplexity signal alone and says so in the response,
    # instead of failing every submission because of a stretch feature.
    import binoculars_signal
    import scoring

    # Below 250 whitespace-separated words, use perplexity alone. At or above
    # the gate, blend 70% perplexity with 30% Binoculars. When enabled, compute
    # and log Binoculars below the gate too for evaluation.
    min_words = config.BINOCULARS_MIN_WORDS
    word_count = len(text.split())

    binoculars_score = None
    if config.BINOCULARS_ENABLED:
        try:
            binoculars_score = binoculars_signal.binoculars_signal(text)
        except detector.DetectorUnavailable:
            pass

    binoculars_used = binoculars_score is not None and word_count >= min_words
    if binoculars_used:
        model_score = scoring.combine_model_signals(perplexity_score, binoculars_score)
    else:
        model_score = perplexity_score
    # ***deb ..end of stretch feature*** binocular***


    # Below lines commented so as to setup styling with default values
    import stylometry
    #style_score = 0.5

    try:
        style_score = stylometry.style_signal(text)
    except stylometry.TextTooShortError as exc:
        return jsonify({"error": "bad_request", "message": str(exc)}), 400


    # Combine the signals and select the label and reader-facing sentence.
    combined_score = scoring.combine_signals(model_score, style_score)
    label, confidence = scoring.score_to_label(combined_score)
    label_text = scoring.LABEL_TEXT[label]

    # Use the same initial decision values in both files, linked by content_id.
    content_id = f"c_{uuid.uuid4().hex[:12]}"
    decision_fields = dict(
        guess=label,
        model_score=model_score,
        style_score=style_score,
        combined_score=combined_score,
        label=label,
        label_text=label_text,
        confidence=confidence,
        status="decided",
        perplexity_score=perplexity_score,
        binoculars_score=binoculars_score,
        binoculars_used=binoculars_used,
        word_count=word_count,
    )
    submissions.save_submission(content_id, creator_id, text, **decision_fields)
    audit.log_decision(content_id=content_id, creator_id=creator_id, **decision_fields)

    # ***deb..start stretch feature*** binocular***
    # The log records the model score used, both component scores, whether
    # Binoculars contributed, and the input word count through **extra.
    # ***deb ..end of stretch feature*** binocular***

    # Step 2 - JSON goes in: pull text and creator_id out of the body
    # Validation now runs above, before the detector is called

    # Step 1 - to get the route working without any logic
    return jsonify({
        "content_id": content_id,
        "guess": label,
        "label": label,
        "label_text": label_text,
        "combined_score": combined_score,
        "confidence": confidence,
        "model_score": model_score,
        "style_score": style_score,
        # ***deb..start stretch feature*** binocular***
        # model_score above is what the decision used (the weighted blend when
        # Binoculars contributed). These are its components, for the eval reports and
        # for appeals.
        #------activate the below for
        #"perplexity_score": perplexity_score,
        #"binoculars_score": binoculars_score,
        #"binoculars_used": binoculars_used,     # false below BINOCULARS_MIN_WORDS or if it couldn't load
        #"word_count": word_count,
        # ***deb ..end of stretch feature*** binocular***
    }), 200


@app.post("/appeal")
def appeal():
    """Run an automatic appeal or record evidence for a manual certification review."""
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({
            "error": "bad_request",
            "message": "Send a JSON object containing content_id and reasoning.",
        }), 400

    content_id = payload.get("content_id")
    reasoning = payload.get("reasoning")
    if not isinstance(content_id, str) or not content_id.strip():
        return jsonify({"error": "bad_request", "message": "Provide a non-empty content_id."}), 400
    if not isinstance(reasoning, str) or not reasoning.strip():
        return jsonify({"error": "bad_request", "message": "Provide non-empty reasoning."}), 400
    content_id = content_id.strip()
    reasoning = reasoning.strip()
    review_type = payload.get("review_type", "automatic")
    if review_type not in ("automatic", "human_verification"):
        return jsonify({
            "error": "bad_request",
            "message": "review_type must be automatic or human_verification.",
        }), 400
    if review_type == "human_verification":
        additional_text = payload.get("additional_text")
        if not isinstance(additional_text, str) or not additional_text.strip():
            return jsonify({
                "error": "bad_request",
                "message": "Provide non-empty additional_text for human verification.",
            }), 400
        record = verification.request_review(content_id, reasoning, additional_text)
        return jsonify({
            "content_id": content_id,
            "verification_request_id": record["verification_request_id"],
            "review_type": review_type,
            "status": "under_review",
            "message": "Your human-verification request has been recorded.",
        }), 202

    entries = audit.entries_for(content_id)
    decision = next((entry for entry in entries if entry.get("status") == "decided"), None)
    if decision is None:
        return jsonify({"error": "not_found", "message": "No submission exists for that content_id."}), 404

    creator_id = decision.get("creator_id", "unknown")
    appeal_id = f"a_{uuid.uuid4().hex[:12]}"
    # Record acceptance before running inference, so even a failed recheck
    # leaves the writer's appeal and under_review status in the audit trail.
    audit.log_appeal(content_id, creator_id, reasoning,
                     appeal_id=appeal_id, review_type=review_type)

    import appeals

    submission = submissions.for_decision(decision)
    original_text = submission["text"] if submission is not None else None
    result = appeals.reassess(original_text)
    audit.log_appeal_result(content_id, creator_id, appeal_id, review_type=review_type, **result)
    return jsonify({
        "content_id": content_id,
        "appeal_id": appeal_id,
        "review_type": review_type,
        "status": "under_review",
        **result,
    }), 200


 # ***---deb..start stretch feature*** content id get call----***
# Stretch feature: look up one item's current status without rescoring it.
@app.get("/content/<content_id>")
def get_content(content_id: str):
    """Return the latest status and this item's approved credential, if any."""
    return jsonify(verification.content_status(content_id)), 200


@app.get("/verification/review/<content_id>")
def get_verification_review(content_id: str):
    """Load the saved submission, evidence, and outcome for a human reviewer."""
    return jsonify(verification.review_details(content_id)), 200


@app.post("/verification/review")
def review_verification():
    """Record a reviewer decision for one item's latest request without authentication."""
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"error": "bad_request",
                        "message": "Send a JSON object containing content_id and status."}), 400
    content_id = payload.get("content_id")
    if not isinstance(content_id, str) or not content_id.strip():
        return jsonify({"error": "bad_request", "message": "Provide a non-empty content_id."}), 400
    record = verification.review_content(
        content_id.strip(), payload.get("status"),
        payload.get("reviewer", "unspecified"),
        payload.get("review_notes", ""),
    )
    return jsonify({
        "content_id": record["content_id"],
        "verification_request_id": record["verification_request_id"],
        "status": record["status"],
        "credential": record["credential"],
    }), 200


# ── Already works ─────────────────────────────────────────────────────────────

@app.get("/log")
def get_log():
    """
    The audit log, most recent last.

        curl "http://127.0.0.1:5000/log?limit=10"

    You need this in unit 8 to paste entries into your README, and you need it
    now to see whether your logging is actually working.
    """
    limit = request.args.get("limit", type=int)
    content_id = request.args.get("content_id")
    if content_id is not None:
        entries = audit.entries_for(content_id)
        if limit:
            entries = entries[-limit:]
    else:
        entries = audit.read_entries(limit=limit)
    return jsonify({"count": len(entries), "entries": entries})


def main():
    print(f"Provenance Guard on http://{config.HOST}:{config.PORT}")
    print(f"  detector model:  {config.DETECTOR_MODEL}")
    print(f"  device setting:  {config.INFERENCE_DEVICE} (resolved when models load)")
    # ***deb..start stretch feature*** binocular***
    performer = getattr(config, "BINOCULARS_PERFORMER", "gpt2-medium")
    binoculars_status = (
        performer or 'single-model mode (no second download)'
        if config.BINOCULARS_ENABLED else 'OFF (AI201_BINOCULARS=0)'
    )
    print(f"  binoculars:      {binoculars_status}")
    # ***deb ..end of stretch feature*** binocular***
    print(f"  rate limiting:   {'ON' if config.RATE_LIMITING_ENABLED else 'off (AI201_RATE_LIMITS=0)'}")
    print(f"  audit log:       {config.AUDIT_LOG}")
    print()
    print("Check it's alive:")
    print(f'  curl -X POST http://{config.HOST}:{config.PORT}/ping \\')
    print('    -H "Content-Type: application/json" \\')
    print("    -d '{\"message\": \"hello\"}'")
    print()
    # debug=True hands out an interactive debugger, so it's local-only — see config.py
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)


if __name__ == "__main__":
    main()
