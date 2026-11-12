"""Run an unchanged supplied set with IP-aware pacing and capture full evidence.

Uses run_attacks.py's input loader and HTTP sender. Normal rows run in batches
within the minute allowance; a flood family starts in a fresh window and runs
as a burst. No server settings or attack bodies are changed.
"""

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import time

import requests

import config
from run_attacks import auto_verdict, load_attacks, send


class AttackPacer:
    def __init__(self, allowance, clock=time.monotonic, sleep=time.sleep):
        self.allowance = allowance
        self.clock = clock
        self.sleep = sleep
        self.started = None
        self.count = 0
        self.previous_family = None

    def before_request(self, family):
        flood = family == "flood_same_creator"
        entering_flood = flood and self.previous_family != family
        now = self.clock()
        delay = 0.0
        if self.started is not None and (
            (entering_flood and self.count) or (not flood and self.count >= self.allowance)
        ):
            # The limiter starts a 60-second window at the first request.
            # One extra second accommodates the local request's travel time.
            delay = max(0.0, self.started + 61.0 - now)
            if delay:
                print(f"Waiting {delay:.1f}s for a fresh IP minute allowance...", flush=True)
            while self.clock() < self.started + 61.0:
                self.sleep(min(30.0, self.started + 61.0 - self.clock()))
            now = self.clock()
            self.started = None
        if self.started is None or now - self.started >= 61.0:
            self.started = now
            self.count = 0
        self.count += 1
        self.previous_family = family
        return delay


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--set", required=True, type=Path, dest="folder")
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--url", default="http://127.0.0.1:5000")
    parser.add_argument("--health-wait", type=float, default=10.0)
    parser.add_argument("--timeout", type=float, default=90.0)
    args = parser.parse_args()
    if args.health_wait < 0:
        parser.error("--health-wait must be nonnegative")
    attacks, problems = load_attacks(args.folder)
    if problems or not attacks:
        parser.error("The set could not be loaded completely: " + repr(problems))
    if len({attack['id'] for attack in attacks}) != len(attacks):
        parser.error("Duplicate attack IDs would make the evidence ambiguous")
    args.output.mkdir(parents=True, exist_ok=False)
    inputs = args.output / "inputs"
    inputs.mkdir()
    source_hashes = {}
    for filename in ("attacks.csv", "attacks_malformed_requests.csv"):
        source = args.folder / filename
        if source.exists():
            shutil.copyfile(source, inputs / filename)
            source_hashes[filename] = hashlib.sha256(source.read_bytes()).hexdigest()
    frozen_files = ("app.py", "audit.py", "config.py", "detector.py", "binoculars_signal.py", "scoring.py", "stylometry.py")
    metadata = {
        "input_folder": str(args.folder.resolve()), "url": args.url,
        "attack_count": len(attacks), "input_sha256": source_hashes,
        "service_sha256": {name: hashlib.sha256(Path(name).read_bytes()).hexdigest() for name in frozen_files},
        "minute_limit": config.RATE_LIMIT_PER_MINUTE,
        "day_limit": config.RATE_LIMIT_PER_DAY,
        "pacing": "At most nine normal requests per 61-second window; flood rows burst in a fresh window.",
    }
    health = requests.get(args.url + "/health", timeout=10)
    health.raise_for_status()
    metadata["health_before"] = health.json()
    metadata["health_before_at_utc"] = utc_now()
    if not metadata["health_before"].get("rate_limiting"):
        raise SystemExit("Rate limiting must remain enabled for this run")
    (args.output / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")
    started_wait = time.monotonic()
    time.sleep(args.health_wait)
    metadata["health_wait_seconds"] = time.monotonic() - started_wait
    metadata["attack_started_at_utc"] = utc_now()
    pacer = AttackPacer(config.RATE_LIMIT_PER_MINUTE)
    rows = []
    for index, attack in enumerate(attacks, 1):
        delay = pacer.before_request(attack["family"])
        sent_at = utc_now()
        started = time.monotonic()
        status, response, error = send(args.url, attack, args.timeout)
        elapsed = time.monotonic() - started
        received_at = utc_now()
        verdict, note = auto_verdict(status, response, error)
        body = response if isinstance(response, dict) else {}
        row = {
            "id": attack["id"], "family": attack["family"], "targets": attack["targets"],
            "request": {key: attack[key] for key in ("body", "raw", "content_type") if key in attack},
            "sent_at_utc": sent_at, "received_at_utc": received_at,
            "pacing_wait_seconds": delay, "duration_seconds": elapsed,
            "status": status, "response": response, "error": error,
            "model_score": body.get("model_score"), "style_score": body.get("style_score"),
            "combined_score": body.get("combined_score"), "label": body.get("label"),
            "content_id": body.get("content_id"), "verdict": verdict, "note": note,
        }
        rows.append(row)
        with (args.output / "responses.jsonl").open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
        print(f"[{index:02}/{len(attacks)}] {attack['id']:<8} {status} {body.get('label', body.get('error', error))}", flush=True)

    metadata["attack_finished_at_utc"] = utc_now()
    # The next HTTP request is the requested immediate post-attack health check.
    after = requests.get(args.url + "/health", timeout=10)
    metadata["health_after_at_utc"] = utc_now()
    after.raise_for_status()
    metadata["health_after"] = after.json()
    audit_response = requests.get(args.url + "/log", timeout=10)
    audit_response.raise_for_status()
    entries = audit_response.json()["entries"][metadata["health_before"]["log_entries"]:]
    (args.output / "audit_excerpt.jsonl").write_text(
        "".join(json.dumps(entry, ensure_ascii=False) + "\n" for entry in entries)
    )
    metadata["audit_entries_captured"] = len(entries)
    metadata["service_unchanged"] = all(
        hashlib.sha256(Path(name).read_bytes()).hexdigest() == digest
        for name, digest in metadata["service_sha256"].items()
    )
    (args.output / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")
    print(f"Recorded {len(rows)} outcomes and {len(entries)} audit entries in {args.output}", flush=True)


if __name__ == "__main__":
    main()
