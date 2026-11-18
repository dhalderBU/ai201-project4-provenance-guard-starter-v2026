"""Shared automatic/manual certifications and exact-text certificate verification."""

from contextlib import contextmanager
from datetime import datetime, timezone
import fcntl
import hashlib
import hmac
import json
import os
import threading
import uuid

import audit
import config
import submissions
import operations


_lock = threading.Lock()
REQUEST_EVENT = "human_verification_request"
REVIEW_EVENT = "human_verification_review"
ASSESSMENT_EVENT = "automatic_certification"


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


def _certificate_object(pairs):
    """Reject ambiguous JSON before its earlier field values can be discarded."""
    record = {}
    for key, value in pairs:
        if key in record:
            raise ValueError(f"Duplicate field in certificate record: {key}")
        record[key] = value
    return record


def _certificates():
    path = config.CERTIFICATION_LOG
    legacy = path.with_name("verified_human_certification_log.jsonl")
    if legacy.exists():
        if path.exists():
            raise ValueError("Both legacy and current certification logs exist; merge them before continuing.")
        # Called under the verification lock. Preserve historical records byte for byte.
        legacy.rename(path)
    if not path.exists():
        return []
    # Fail on a damaged certificate log instead of overlooking existing IDs.
    return [json.loads(line, object_pairs_hook=_certificate_object)
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()]


def _unique_id(prefix, existing):
    while True:
        candidate = prefix + uuid.uuid4().hex[:16]
        if candidate not in existing:
            return candidate


def _content_hash(text):
    """Hash the complete UTF-8 text without trimming or normalization."""
    try:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()
    except UnicodeEncodeError as exc:
        raise VerificationError("text must contain valid UTF-8 characters.") from exc


def _credential(text, now, method):
    digest = _content_hash(text)
    return {
        "type": "content_certification", "method": method,
        "Certificate_id": digest[-8:],
        "verified_dt_time": now.strftime("%Y-%m-%d %H:%M:%S UTC"),
        "hash_algorithm": "sha256", "content_hash": digest,
    }


def _append_certificate(record):
    """One persistence boundary for a future document-store implementation."""
    path = config.CERTIFICATION_LOG
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False, allow_nan=False) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def certify_assessment(content_id, creator_id, text, assessment, source, assessment_id):
    """Persist each human assessment once, without claiming a manual review."""
    if assessment.get("label") != "human":
        return None
    if source not in ("submission", "automatic_appeal"):
        raise VerificationError("Unknown certification assessment source.")
    if not isinstance(text, str) or not text.strip():
        raise VerificationError("The original submitted text is unavailable for certification.",
                                409, "original_text_unavailable")
    digest = _content_hash(text)
    with _locked():
        certificates = _read_certificate_store()
        event_id = "ce_" + assessment_id
        existing = [record for record in certificates
                    if record.get("certification_event_id") == event_id]
        if existing:
            _validated_certifications(existing)
            record = existing[-1]
            if (record["content_id"] != content_id
                    or record["credential"]["content_hash"] != digest
                    or record.get("assessment_source") != source):
                raise VerificationError("The assessment has conflicting certification records.",
                                        409, "certificate_unverifiable")
            return record
        now = datetime.now(timezone.utc)
        record = {
            "schema_version": 1, "certification_event_id": event_id,
            "timestamp": now.isoformat(timespec="microseconds"),
            "content_id": content_id, "creator_id": creator_id,
            "event": ASSESSMENT_EVENT, "status": "certified",
            "assessment_source": source, "assessment_id": assessment_id,
            "assessment": dict(assessment),
            "credential": _credential(text, now, "automated_assessment"),
        }
        operations.before_persist()
        _append_certificate(record)
        return record


def _certification_time(record):
    """Return an approval's UTC instant; never substitute lookup time."""
    try:
        moment = datetime.fromisoformat(record["timestamp"])
        displayed = datetime.strptime(record["credential"]["verified_dt_time"],
                                      "%Y-%m-%d %H:%M:%S UTC").replace(tzinfo=timezone.utc)
        if moment.tzinfo is None:
            raise ValueError("Certification timestamp needs a timezone")
        moment = moment.astimezone(timezone.utc)
        if moment.replace(microsecond=0) != displayed:
            raise ValueError("Certification timestamps disagree")
        return moment
    except (KeyError, TypeError, ValueError, OverflowError) as exc:
        raise VerificationError("The certificate has unusable certification timestamps.",
                                409, "certificate_unverifiable") from exc


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
        if any(entry.get("content_id") == content_id
               and entry.get("credential", {}).get("method") == "draft_review"
               for entry in certificates):
            raise VerificationError("This item already has a verified-human certificate.", 409, "already_verified")
        for entry in item_entries:
            if entry.get("event") == REQUEST_EVENT and _review(
                entries, certificates, entry["verification_request_id"]
            ) is None:
                raise VerificationError("This item already has a pending human-verification request.",
                                        409, "verification_pending")
        request_id = _unique_id("vr_", {entry.get("verification_request_id") for entry in entries})
        operations.before_persist()
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
                operations.before_persist()
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
            credential = _credential(text, now, "draft_review")
        review = {
            "schema_version": 1,
            "certification_event_id": "ce_" + request_id,
            # Preserve subsecond order when identical text is approved twice.
            "timestamp": now.isoformat(timespec="microseconds"),
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
        operations.before_persist()
        if credential is not None:
            _append_certificate(review)
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


def _read_certificate_store():
    """Read usable JSON objects, preserving the store's fail-closed behavior."""
    try:
        certificates = _certificates()
    except (OSError, ValueError) as exc:
        raise VerificationError("Certificate records could not be read.",
                                503, "certificate_store_unavailable") from exc
    if any(not isinstance(record, dict)
           or not isinstance(record.get("credential"), dict) for record in certificates):
        raise VerificationError("Certificate records could not be read.",
                                503, "certificate_store_unavailable")
    return certificates


def _validated_certifications(records):
    """Validate approval metadata and conflicting copies before using any match."""
    candidates, seen_events = [], {}
    for index, record in enumerate(records):
        operations.check_deadline()
        credential = record["credential"]
        certificate_id = credential.get("Certificate_id")
        stored_hash = credential.get("content_hash")
        request_id = record.get("verification_request_id")
        event_id = record.get("certification_event_id")
        assessment = record.get("assessment")
        method = credential.get("method")
        manual = (method == "draft_review" and record.get("review_decision") == "certified"
                  and isinstance(request_id, str) and bool(request_id))
        automatic = (method == "automated_assessment"
                     and credential.get("type") == "content_certification"
                     and record.get("event") == ASSESSMENT_EVENT
                     and record.get("assessment_source") in ("submission", "automatic_appeal")
                     and isinstance(record.get("assessment_id"), str) and bool(record["assessment_id"])
                     and event_id == "ce_" + record["assessment_id"]
                     and isinstance(assessment, dict) and assessment.get("label") == "human")
        short_id = (isinstance(certificate_id, str) and len(certificate_id) == 8
                    and all(c in "0123456789abcdef" for c in certificate_id))
        if (record.get("status") != "certified"
                or not (manual or automatic)
                or not isinstance(record.get("content_id"), str) or not record["content_id"]
                or not isinstance(certificate_id, str) or not certificate_id.strip()
                or credential.get("type") not in ("content_certification", "verified_human")
                or (credential.get("type") == "content_certification"
                    and (record.get("schema_version") != 1
                         or not isinstance(event_id, str) or not event_id))
                or credential.get("hash_algorithm") != "sha256"
                or not isinstance(stored_hash, str) or len(stored_hash) != 64
                or any(char not in "0123456789abcdef" for char in stored_hash)
                or (short_id and stored_hash[-8:] != certificate_id)):
            raise VerificationError("This certificate has no usable SHA-256 certification record.",
                                    409, "certificate_unverifiable")
        for key in _activity_keys(record):
            if key in seen_events and seen_events[key] != record:
                raise VerificationError("The certification activity has conflicting records.",
                                        409, "certificate_unverifiable")
            seen_events[key] = record
        candidates.append((_certification_time(record), index, record))
    return candidates


def _activity_keys(record):
    """Identify both new certification events and historical review activities."""
    keys = set()
    for field in ("certification_event_id", "verification_request_id", "assessment_id"):
        value = record.get(field)
        if isinstance(value, str) and value:
            keys.add((field, value))
    return keys


def find_certified_content(text):
    """Find an existing approval by full text hash, without requiring its ID."""
    presented_hash = _content_hash(text)
    with _locked():
        certificates = _read_certificate_store()
        matches = []
        for record in certificates:
            operations.check_deadline()
            if record["credential"].get("content_hash") == presented_hash:
                matches.append(record)
        if not matches:
            return None

        # Check related copies as well, so a damaged or conflicting approval
        # cannot be hidden by filtering on its one remaining correct hash.
        certificate_ids = {record["credential"]["Certificate_id"] for record in matches
                           if isinstance(record["credential"].get("Certificate_id"), str)}
        activity_keys = set().union(*(_activity_keys(record) for record in matches))
        related = []
        for record in certificates:
            operations.check_deadline()
            certificate_id = record["credential"].get("Certificate_id")
            if (record["credential"].get("content_hash") == presented_hash
                    or (isinstance(certificate_id, str) and certificate_id in certificate_ids)
                    or _activity_keys(record) & activity_keys):
                related.append(record)
        candidates = _validated_certifications(related)
        matching = [candidate for candidate in candidates if hmac.compare_digest(
            presented_hash, candidate[2]["credential"]["content_hash"])]
        moment, _, record = max(matching, key=lambda candidate: candidate[:2])
        return {
            "content_id": record["content_id"],
            "certificate_id": record["credential"]["Certificate_id"],
            "credential": record["credential"],
            "latest_certification_at": moment.isoformat(),
        }


def verify_content(certificate_id, text):
    """Verify the full hash and return the latest matching certification activity.

    This is a lookup, not another review: it never runs a model, changes a
    workflow status, or backfills old certificates from mutable submission text.
    A short ID can repeat, even for different full hashes; it is only a lookup key.
    """
    if not isinstance(certificate_id, str) or not certificate_id.strip():
        raise VerificationError("Provide a non-empty certificate_id.")
    if not isinstance(text, str) or not text.strip():
        raise VerificationError("Provide non-empty text to verify.")
    certificate_id = certificate_id.strip()
    presented_hash = _content_hash(text)

    with _locked():
        certificates = _read_certificate_store()
        matches = [record for record in certificates
                   if record["credential"].get("Certificate_id") == certificate_id]
        if not matches:
            raise VerificationError("No certificate exists for that certificate_id.",
                                    404, "certificate_not_found")
        candidates = _validated_certifications(matches)

        matching = [candidate for candidate in candidates if hmac.compare_digest(
            presented_hash, candidate[2]["credential"]["content_hash"])]
        verified = bool(matching)
        # Timestamp order, with append order breaking exact ties. Never select
        # a newer approval of different content that shares the short suffix.
        latest = max(matching or candidates, key=lambda candidate: candidate[:2])
        record = latest[2]
        unambiguous = len({row[2]["credential"]["content_hash"] for row in candidates}) == 1
        return {
            "certificate_id": certificate_id,
            "content_id": record["content_id"] if verified or unambiguous else None,
            "verified": verified,
            "status": "verified" if verified else "content_mismatch",
            "hash_algorithm": "sha256",
            "verified_dt_time": record["credential"]["verified_dt_time"] if verified else None,
            "latest_certification_at": latest[0].isoformat() if verified else None,
            "certification_method": record["credential"].get("method") if verified else None,
        }
