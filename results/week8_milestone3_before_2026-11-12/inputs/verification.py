"""Manual draft review and item-specific certificates, persisted in JSONL logs."""

from contextlib import contextmanager
from datetime import datetime, timezone
import fcntl
import json
import os
import threading
import uuid

import audit
import config
import submissions


_lock = threading.Lock()
REQUEST_EVENT = "human_verification_request"
REVIEW_EVENT = "human_verification_review"


class VerificationError(ValueError):
    def __init__(self, message, status_code=400, code="bad_request"):
        super().__init__(message)
        self.status_code = status_code
        self.code = code


@contextmanager
def _locked():
    """Serialize verification changes across Flask threads and server processes."""
    config.LOG_DIR.mkdir(parents=True, exist_ok=True)
    with _lock, (config.LOG_DIR / ".verification.lock").open("a") as handle:
        fcntl.flock(handle, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(handle, fcntl.LOCK_UN)


def _certificates():
    path = config.VERIFIED_HUMAN_CERTIFICATION_LOG
    if not path.exists():
        return []
    # Fail on a damaged certificate log instead of overlooking existing IDs.
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()]


def _unique_id(prefix, existing):
    while True:
        candidate = prefix + uuid.uuid4().hex[:16]
        if candidate not in existing:
            return candidate


def _review(entries, certificates, request_id):
    # An approved certificate remains authoritative if audit appending failed.
    return next((entry for entry in reversed(certificates + entries)
                 if entry.get("event") == REVIEW_EVENT
                 and entry.get("verification_request_id") == request_id), None)


def _original(entries):
    decision = next((entry for entry in entries
                     if entry.get("status") == "decided" and not entry.get("event")), None)
    if decision is None:
        raise VerificationError("No submission exists for that content_id.", 404, "not_found")
    return decision


def _submission(decision):
    submission = submissions.for_decision(decision)
    if submission is not None and submission.get("creator_id") != decision.get("creator_id", "unknown"):
        raise VerificationError("The submission and decision have different creator IDs.",
                                409, "submission_mismatch")
    return submission


def _latest_request(entries):
    request = next((entry for entry in reversed(entries)
                    if entry.get("event") == REQUEST_EVENT), None)
    if request is None:
        raise VerificationError("This item has no human-verification request.",
                                409, "verification_required")
    return request


def review_details(content_id):
    """Join the original text with saved evidence and outcome without writing either file."""
    with _locked():
        entries = audit.entries_for(content_id)
        original = _original(entries)
        request = _latest_request(entries)
        return {
            "content_id": content_id,
            "submission": _submission(original),
            "decision": {key: value for key, value in original.items() if key != "text"},
            "verification_request": request,
            "review": _review(entries, _certificates(), request["verification_request_id"]),
        }


def request_review(content_id, reasoning, additional_text):
    """Record supporting text for an existing submission; never issue a credential."""
    with _locked():
        entries = audit.read_entries()
        item_entries = [entry for entry in entries if entry.get("content_id") == content_id]
        original = _original(item_entries)
        submission = _submission(original)
        certificates = _certificates()
        if any(entry.get("content_id") == content_id for entry in certificates):
            raise VerificationError("This item already has a verified-human certificate.", 409, "already_verified")
        for entry in item_entries:
            if entry.get("event") == REQUEST_EVENT and _review(
                entries, certificates, entry["verification_request_id"]
            ) is None:
                raise VerificationError("This item already has a pending human-verification request.",
                                        409, "verification_pending")
        request_id = _unique_id("vr_", {entry.get("verification_request_id") for entry in entries})
        return audit.log_verification(
            content_id=content_id,
            creator_id=submission["creator_id"] if submission is not None else original.get("creator_id", "unknown"),
            event=REQUEST_EVENT,
            status="under_review",
            review_type="human_verification",
            verification_request_id=request_id,
            requested_dt_time=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
            reasoning=reasoning,
            additional_text=additional_text,
        )


def review_content(content_id, status, reviewer, notes):
    """Resolve the item's latest human-review request, with repeat-safe issuance."""
    if status not in ("certified", "not_certified"):
        raise VerificationError("status must be certified or not_certified.")
    if not isinstance(reviewer, str) or not reviewer.strip():
        raise VerificationError("Provide a reviewer name.")
    if not isinstance(notes, str):
        raise VerificationError("review_notes must be a string.")
    with _locked():
        entries = audit.read_entries()
        item_entries = [entry for entry in entries if entry.get("content_id") == content_id]
        original = _original(item_entries)
        request = _latest_request(item_entries)
        request_id = request["verification_request_id"]
        certificates = _certificates()
        existing = _review(entries, certificates, request_id)
        if existing is not None:
            if existing["review_decision"] != status:
                raise VerificationError("This request already has a different review decision.",
                                        409, "already_reviewed")
            # Recover an approved review if its certificate was saved but audit writing failed.
            if not any(entry.get("event") == REVIEW_EVENT
                       and entry.get("verification_request_id") == request_id for entry in entries):
                audit.log_verification(**existing)
            return existing

        submission = _submission(original)
        text = submission.get("text") if submission is not None else None
        if status == "certified" and (not isinstance(text, str) or not text.strip()):
            raise VerificationError("The original submitted text is unavailable for certification.",
                                    409, "original_text_unavailable")

        now = datetime.now(timezone.utc)
        credential = None
        if status == "certified":
            certificate_id = _unique_id("vh_", {
                entry["credential"]["Certificate_id"] for entry in certificates
            })
            credential = {
                "type": "verified_human",
                "method": "draft_review",
                "Certificate_id": certificate_id,
                "verified_dt_time": now.strftime("%Y-%m-%d %H:%M:%S UTC"),
            }
        review = {
            "timestamp": now.isoformat(timespec="seconds"),
            "content_id": request["content_id"],
            "creator_id": request["creator_id"],
            "event": REVIEW_EVENT,
            "status": status,
            "review_type": "human_verification",
            "verification_request_id": request_id,
            "review_decision": status,
            "reviewer": reviewer.strip(),
            "review_notes": notes.strip(),
            "credential": credential,
        }
        if credential is not None:
            path = config.VERIFIED_HUMAN_CERTIFICATION_LOG
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(review, ensure_ascii=False) + "\n")
                handle.flush()
                os.fsync(handle.fileno())
        audit.log_verification(**review)
        return review


def content_status(content_id):
    """Return current workflow status plus a certificate only for this item."""
    with _locked():
        entries = audit.entries_for(content_id)
        if not entries:
            raise VerificationError("No submission exists for that content_id.", 404, "not_found")
        certificates = [entry for entry in _certificates() if entry["content_id"] == content_id]
        credential = certificates[-1]["credential"] if certificates else None
        result = {"content_id": content_id, "status": entries[-1]["status"],
                  "credential": credential}
        request = next((entry for entry in reversed(entries)
                        if entry.get("event") == REQUEST_EVENT), None)
        if request is not None:
            request_id = request["verification_request_id"]
            review = _review(entries, certificates, request_id)
            result["verification_request_id"] = request_id
            result["verification_status"] = review["review_decision"] if review else "pending"
            if review and entries[-1].get("event") == REQUEST_EVENT:
                result["status"] = review["status"]
        return result
