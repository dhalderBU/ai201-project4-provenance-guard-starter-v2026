"""Store original submissions separately from decision and review audit records."""

from datetime import datetime, timezone
import json
import threading

import config


_lock = threading.Lock()


def save_submission(content_id: str, creator_id: str, text: str, **decision_fields) -> dict:
    """Append the exact text, initial decision fields, and acceptance time in UTC."""
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "content_id": content_id,
        "creator_id": creator_id,
        "text": text,
        **decision_fields,
    }
    path = config.SUBMISSIONS_FILE
    path.parent.mkdir(parents=True, exist_ok=True)
    with _lock, path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return entry


def get_submission(content_id: str) -> dict | None:
    """Find a saved submission by content ID, including after a server restart."""
    path = config.SUBMISSIONS_FILE
    with _lock:
        if not path.exists():
            return None
        with path.open(encoding="utf-8") as handle:
            for line in handle:
                if not line.strip():
                    continue
                entry = json.loads(line)
                if entry.get("content_id") == content_id:
                    return entry
    return None


def for_decision(decision: dict) -> dict | None:
    """Load the same original for automatic and human review, including legacy items."""
    submission = get_submission(decision["content_id"])
    if submission is not None:
        return submission
    text = decision.get("text")
    if isinstance(text, str) and text.strip():
        return {
            "timestamp": decision["timestamp"],
            "content_id": decision["content_id"],
            "creator_id": decision.get("creator_id", "unknown"),
            "text": text,
        }
    return None
