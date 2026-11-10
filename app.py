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
    GET  /log         the audit log. Already works
    GET  /health      is the service up, and is the model loaded
"""

# from email.mime import text  # Not needed: text comes from the JSON payload.
import uuid

from flask import Flask, jsonify, request

import audit
import config

app = Flask(__name__)


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
    return jsonify({
        "ok": True,
        "detector_model": config.DETECTOR_MODEL,
        "detector_loaded": loaded,
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
        model_score = detector.model_signal(text)
    except detector.TextTooShortError as exc:
        return jsonify({"error": "bad_request", "message": str(exc)}), 400


    # Below lines commented so as to setup styling with default values
    import stylometry
    #style_score = 0.5

    try:
        style_score = stylometry.style_signal(text)
    except stylometry.TextTooShortError as exc:
        return jsonify({"error": "bad_request", "message": str(exc)}), 400


    # Combine the signals and select the label and reader-facing sentence.
    import scoring

    combined_score = scoring.combine_signals(model_score, style_score)
    label, confidence = scoring.score_to_label(combined_score)
    label_text = scoring.LABEL_TEXT[label]

    # Step 4 - log the decision. The content_id is what /appeal needs later.
    content_id = f"c_{uuid.uuid4().hex[:12]}"
    audit.log_decision(
        content_id=content_id,
        creator_id=creator_id,
        guess=label,
        text=text,
        model_score=model_score,
        style_score=style_score,
        combined_score=combined_score,
        label=label,
        label_text=label_text,
        confidence=confidence,
        status="decided",
    )

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
    }), 200

  

@app.post("/appeal")
def appeal():
    """Record an appeal and run the three-variant recheck from criteria.md."""
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

    entries = audit.entries_for(content_id)
    decision = next((entry for entry in entries if entry.get("status") == "decided"), None)
    if decision is None:
        return jsonify({"error": "not_found", "message": "No submission exists for that content_id."}), 404

    creator_id = decision.get("creator_id", "unknown")
    appeal_id = f"a_{uuid.uuid4().hex[:12]}"
    # Record acceptance before running inference, so even a failed recheck
    # leaves the writer's appeal and under_review status in the audit trail.
    audit.log_appeal(content_id, creator_id, reasoning, appeal_id=appeal_id)

    import appeals

    result = appeals.reassess(decision.get("text"))
    audit.log_appeal_result(content_id, creator_id, appeal_id, **result)
    return jsonify({
        "content_id": content_id,
        "appeal_id": appeal_id,
        "status": "under_review",
        **result,
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
