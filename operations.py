"""Track Flask requests, enforce shared deadlines, and summarize operational logs.

Request flow:
    1. ``app.py`` calls ``install(app)`` before installing its rate limiter.
    2. The first request hook creates a RequestState and records the arrival.
    3. Routes validate input and perform lookups or call ``inference_runtime``.
       All stages share the original deadline; scoring streams measurements back.
    4. Successful submission/certification writes call ``before_persist()``.
    5. Response/teardown hooks finalize measurements, update an admitted request's
       circuit state, release its inference slot, and clear request context.
    6. ``GET /metrics`` calls ``summarize()`` to aggregate saved request events.

The operational JSONL file is configured by LOG_DIR and OPERATIONAL_LOG_FILENAME.
It stores metadata and measurements, not full submitted text. Certificate-only
requests still pass through these hooks even though they never run inference.
The deadline measures processing inside Flask, excluding network/server queuing;
CPU totals combine handler-thread CPU and reported inference-process CPU.
"""

from collections import Counter
from contextvars import ContextVar
from datetime import datetime, timedelta, timezone
import fcntl
import json
import math
import threading
import time
import uuid

import config
import model_metrics

# Context-local state keeps concurrent Flask requests' deadlines and collectors
# separate. The file lock below additionally serializes appends within a process.
_active = ContextVar("operation", default=None)
_file_lock = threading.Lock()


class DeadlineExceeded(RuntimeError):
    """Signal budget expiry; the installed Flask handler converts it to HTTP 504."""

    pass


def current():
    """Return this execution context's RequestState, or None outside a request."""
    return _active.get()


def check_deadline():
    """Mark and raise DeadlineExceeded when an enabled request budget has expired.

    Calls outside an instrumented request, or with timeouts disabled, do nothing.
    Non-inference handlers use these cooperative checks; inference_runtime also
    stops the worker process when a scoring job exceeds the remaining budget.
    """
    state = current()
    if state and state.timeout_enabled and time.perf_counter() >= state.deadline:
        state.timed_out = True
        raise DeadlineExceeded("The request exceeded its processing-time limit.")


def before_persist():
    """Check the deadline and mark that this request is beginning persistence.

    This does not write or commit data itself. Once the marker is set, the
    response hook preserves the route's outcome instead of substituting a late
    timeout response after a write may have happened. Later explicit deadline
    checks can still raise; there is no transaction or rollback across files.
    """
    check_deadline()
    if current():
        current().persistence_started = True


def log_path():
    """Return the configured operational JSONL path under the deployment's logs."""
    return config.LOG_DIR / config.OPERATIONAL_LOG_FILENAME


def append(record):
    """Append one JSON event under thread/process locks, creating missing paths.

    The write is flushed before unlocking. Serialization and filesystem errors
    propagate to the caller so arrival and completion hooks can handle failures
    differently: a failed arrival blocks work, while a failed completion cannot
    undo a result already saved by the route.
    """
    path = log_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(record, ensure_ascii=True, allow_nan=False) + "\n"
    with _file_lock, path.open("a", encoding="utf-8") as handle:
        fcntl.flock(handle, fcntl.LOCK_EX)
        try:
            handle.write(line)
            handle.flush()
        finally:
            fcntl.flock(handle, fcntl.LOCK_UN)


class RequestState:
    """Hold one request's clocks, settings, inference ownership, and measurements.

    Configuration is captured at arrival for historical reporting. The inference
    runtime updates admission, CPU, and token state; finish() consumes that state
    once and resets the context tokens created here.
    """

    def __init__(self, method, path, route):
        """Start clocks, snapshot configuration, and bind a new metrics collector."""
        self.started = time.perf_counter()
        self.cpu_started = time.thread_time()
        self.received_at = datetime.now(timezone.utc).isoformat()
        self.request_id = uuid.uuid4().hex
        self.method, self.path, self.route = method, path, route
        self.timeout_enabled = config.REQUEST_TIMEOUT_ENABLED
        self.timeout_seconds = config.REQUEST_TIMEOUT_SECONDS
        self.deadline = self.started + self.timeout_seconds
        self.recording = config.OPERATIONAL_METRICS_ENABLED
        self.breaker_enabled = config.CIRCUIT_BREAKER_ENABLED
        self.breaker_threshold = config.CIRCUIT_BREAKER_FAILURE_THRESHOLD
        self.breaker_recovery = config.CIRCUIT_BREAKER_RECOVERY_SECONDS
        self.breaker_admitted = False
        self.breaker = None
        self.circuit_rejected = False
        self.timed_out = False
        self.persistence_started = False
        self.inference_cpu_seconds = 0.0
        self.cpu_complete = True
        self.finalized = False
        self.collector, self.metrics_token = model_metrics.begin()
        self.state_token = _active.set(self)

    def common(self):
        """Return metadata shared by this request's receipt and completion events."""
        return {"schema_version": 1, "request_id": self.request_id,
                "received_at": self.received_at, "method": self.method,
                "path": self.path, "route": self.route,
                "timeout_enabled": self.timeout_enabled, "timeout_seconds": self.timeout_seconds,
                "circuit_breaker_enabled": self.breaker_enabled,
                "circuit_failure_threshold": self.breaker_threshold,
                "circuit_recovery_seconds": self.breaker_recovery}


def install(app):
    """Register request hooks and JSON error handlers on a Flask application.

    Install once, before Flask-Limiter, so rejected submissions are measured too.
    begin_request() owns arrival recording; finish_request() handles normal and
    handled-error responses; finish_failed_request() covers teardown when normal
    finalization was skipped. Both completion paths share the idempotent finish().
    """
    from flask import jsonify, request
    import inference_runtime

    @app.before_request
    def begin_request():
        """Create request state and record arrival before route work can begin."""
        state = RequestState(request.method, request.path,
                             request.url_rule.rule if request.url_rule else "unmatched")
        if state.recording:
            try:
                append({**state.common(), "event": "request_received"})
            except OSError:
                app.logger.exception("Cannot write operational request receipt")
                return jsonify(error="operational_log_unavailable", request_id=state.request_id), 503

    @app.errorhandler(DeadlineExceeded)
    def timeout_response(exc):
        """Return HTTP 504 with the request ID and the budget that was exceeded."""
        state = current()
        if state:
            state.timed_out = True
        return jsonify(error="request_timeout", message=str(exc),
                       request_id=state.request_id if state else None,
                       timeout_seconds=state.timeout_seconds if state else config.REQUEST_TIMEOUT_SECONDS), 504

    @app.errorhandler(inference_runtime.InferenceRejected)
    def unavailable_response(exc):
        """Return HTTP 503 and, when supplied, a whole-second Retry-After header."""
        response = jsonify(error=exc.code, message=str(exc), request_id=current().request_id)
        response.status_code = 503
        if exc.retry_after:
            response.headers["Retry-After"] = str(math.ceil(exc.retry_after))
        return response

    def finish(state, status, body):
        """Finalize one request and return whether completion logging succeeded.

        Only requests admitted to scoring update the circuit. Incomplete model
        calls make total CPU unknown rather than reporting a misleading zero.
        Cleanup runs even if writing the completion fails. Already-finalized
        requests and requests with logging disabled return True without writing.
        """
        if state.finalized:
            return True
        state.finalized = True
        elapsed = time.perf_counter() - state.started
        calls = list(state.collector.calls.values())
        # Streamed call-start events can survive a worker crash or timeout even
        # when the corresponding completion and CPU total never reach Flask.
        for call in calls:
            if call["status"] == "running":
                call["status"] = "aborted" if state.timed_out else "incomplete"
                state.cpu_complete = False
        if state.breaker_admitted:
            state.breaker.finish(state.timed_out, status < 500,
                                 state.breaker_threshold, state.breaker_recovery)
        body = body if isinstance(body, dict) else {}
        handler_cpu = time.thread_time() - state.cpu_started
        # Timing ends before this completion append and before the response is
        # transmitted. Keep unknown CPU totals null and preserve partial calls.
        record = {
            **state.common(), "event": "request_completed",
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "http_status": status, "duration_seconds": elapsed,
            "timed_out": state.timed_out,
            "deadline_exceeded": state.timeout_enabled and elapsed >= state.timeout_seconds,
            "circuit_rejected": state.circuit_rejected,
            "circuit_state": inference_runtime.breaker.snapshot()["state"],
            "cpu_time_seconds": handler_cpu + state.inference_cpu_seconds if state.cpu_complete else None,
            "handler_cpu_seconds": handler_cpu,
            "inference_cpu_seconds": state.inference_cpu_seconds if state.cpu_complete else None,
            "cpu_measurement_complete": state.cpu_complete,
            "label": body.get("label") if body.get("label") in ("human", "ai", "unsure") else None,
            "content_id": body.get("content_id"), "error": body.get("error"),
            "result_status": body.get("status"),
            "verified": body.get("verified") if isinstance(body.get("verified"), bool) else None,
            "model_calls": calls, "models": model_metrics.summarize(calls),
        }
        written = True
        try:
            if state.recording:
                append(record)
        except OSError:
            written = False
            app.logger.exception("Cannot write operational completion for %s", state.request_id)
        finally:
            # Request ownership spans all scoring stages and ends here, including
            # on errors. Releasing it prevents a failed log write blocking work.
            inference_runtime.release(state)
            model_metrics.end(state.metrics_token)
            _active.reset(state.state_token)
        return written

    @app.after_request
    def finish_request(response):
        """Apply the final deadline check, add tracing headers, and record outcome."""
        state = current()
        if state is None:
            return response
        # Read-only handlers also check the shared budget. Once persistence has
        # started, keep the route's outcome because records may already be saved.
        if not state.persistence_started and response.status_code < 500:
            try:
                check_deadline()
            except DeadlineExceeded as exc:
                response = app.make_response(timeout_response(exc))
        response.headers["X-Request-ID"] = state.request_id
        if not finish(state, response.status_code, response.get_json(silent=True)):
            response.headers["X-Operational-Metrics"] = "unavailable"
        return response

    @app.teardown_request
    def finish_failed_request(exc):
        """Record a fallback 500 and release state if response finalization failed."""
        state = current()
        if state is not None and not state.finalized:
            finish(state, 500, {"error": type(exc).__name__ if exc else "unfinished_request"})


def _timestamp(value):
    """Parse an ISO 8601 timestamp as UTC, rejecting timestamps without an offset."""
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        raise ValueError("Timestamp must have an offset")
    return parsed.astimezone(timezone.utc)


def _percentile(values, fraction):
    """Interpolate a percentile of sorted values, or return None for an empty list.

    The caller supplies fraction between zero and one; summarize() uses p50/p95.
    """
    if not values:
        return None
    position = (len(values) - 1) * fraction
    lower = math.floor(position)
    upper = math.ceil(position)
    return values[lower] + (values[upper] - values[lower]) * (position - lower)


def summarize(hours, now=None):
    """Aggregate events by request ID within a UTC arrival-time window.

    Args:
        hours: Finite positive window length, no greater than METRICS_MAX_HOURS.
        now: Optional timezone-aware endpoint for the window; defaults to UTC now.

    Returns:
        A JSON-compatible dictionary of request counts, completed-request timing,
        labels, statuses, timeout settings, model measurements, and known CPU time.
        Missing logs produce an empty report; malformed records are counted and
        skipped. A completion can establish a request even if its receipt is absent.

    Raises:
        ValueError: The requested window is outside the supported range.
        OSError: An existing log cannot be read.
        DeadlineExceeded: A cooperative scan check finds the request out of time.

    This reads the log without modifying it. During a logged /metrics request,
    its own receipt is visible but its completion is not written until afterward.
    """
    if not math.isfinite(hours) or not 0 < hours <= config.METRICS_MAX_HOURS:
        raise ValueError(f"hours must be greater than 0 and at most {config.METRICS_MAX_HOURS:g}.")
    now = now or datetime.now(timezone.utc)
    cutoff = now - timedelta(hours=hours)
    requests, completed = {}, {}
    malformed = 0
    path = log_path()
    try:
        handle = path.open(encoding="utf-8")
    except FileNotFoundError:
        handle = None
    if handle:
        with handle:
            # Filter on arrival time, then retain one receipt/completion per ID.
            # Check periodically so a growing log still respects the API budget.
            for index, line in enumerate(handle):
                if index % 100 == 0:
                    check_deadline()
                try:
                    row = json.loads(line)
                    if row.get("event") not in ("request_received", "request_completed"):
                        raise ValueError("Unknown operational event")
                    received = _timestamp(row["received_at"])
                    request_id = row["request_id"]
                    if not isinstance(request_id, str) or not request_id:
                        raise ValueError("Missing request ID")
                    if (not isinstance(row["method"], str) or not isinstance(row["route"], str)
                            or not isinstance(row["timeout_enabled"], bool)
                            or not isinstance(row["timeout_seconds"], (int, float))
                            or not math.isfinite(row["timeout_seconds"]) or row["timeout_seconds"] <= 0):
                        raise ValueError("Invalid request metadata")
                    if not cutoff <= received <= now:
                        continue
                    if row["event"] == "request_completed":
                        duration = row["duration_seconds"]
                        status = row["http_status"]
                        if (not isinstance(duration, (int, float)) or not math.isfinite(duration)
                                or duration < 0 or not isinstance(status, int) or not 100 <= status <= 599):
                            raise ValueError("Invalid completion metrics")
                        model_metrics.summarize(row.get("model_calls", []))
                        completed[request_id] = row
                    requests[request_id] = row
                except (ValueError, TypeError, KeyError, AttributeError):
                    malformed += 1

    # Count every observed request, but compute timing/status/CPU totals only for
    # completed requests. Unfinished receipts remain visible as a separate count.
    statuses = Counter({str(code): 0 for code in (200, 400, 429, 503, 504)})
    labels = Counter({label: 0 for label in ("human", "ai", "unsure")})
    appeal_labels = labels.copy()
    routes = Counter()
    durations, model_calls = [], []
    timeouts, circuit_rejections, cpu_incomplete = 0, 0, 0
    cpu_total = 0.0
    settings = {}
    for request_id, row in requests.items():
        routes[f"{row['method']} {row['route']}"] += 1
        key = (row["timeout_enabled"], row["timeout_seconds"])
        bucket = settings.setdefault(key, {"enabled": key[0], "timeout_seconds": key[1],
                                           "requests_received": 0, "timeouts": 0})
        bucket["requests_received"] += 1
        result = completed.get(request_id)
        if result is None:
            continue
        statuses[str(result["http_status"])] += 1
        durations.append(result["duration_seconds"])
        is_timeout = bool(result.get("timed_out"))
        timeouts += is_timeout
        bucket["timeouts"] += is_timeout
        circuit_rejections += bool(result.get("circuit_rejected"))
        label = result.get("label")
        # Existing-certificate responses have no new label. Appeal votes are
        # reported separately so they do not inflate submission classifications.
        if result["http_status"] == 200 and label in labels:
            if result["method"] == "POST" and result["route"] == "/submit":
                labels[label] += 1
            elif result["method"] == "POST" and result["route"] == "/appeal":
                appeal_labels[label] += 1
        cpu = result.get("cpu_time_seconds")
        if isinstance(cpu, (float, int)) and math.isfinite(cpu) and cpu >= 0:
            cpu_total += cpu
        else:
            cpu_incomplete += 1
        model_calls.extend(result.get("model_calls", []))
    durations.sort()
    average = sum(durations) / len(durations) if durations else None
    return {
        "window": {"hours": hours, "start": cutoff.isoformat(), "end": now.isoformat(),
                   "timestamp_basis": "received_at"},
        "requests_received": len(requests), "requests_completed": len(completed),
        "requests_without_completion": len(requests) - len(completed),
        "average_response_time_seconds": average,
        "response_time_seconds": {"average": average, "min": durations[0] if durations else None,
                                  "max": durations[-1] if durations else None,
                                  "p50": _percentile(durations, 0.5), "p95": _percentile(durations, 0.95)},
        "classification_counts": dict(labels), "classification_scope": "successful POST /submit",
        "appeal_classification_counts": dict(appeal_labels),
        "http_status_counts": dict(statuses), "timeout_count": timeouts,
        "timeout_configurations": sorted(settings.values(), key=lambda item: (item["enabled"], item["timeout_seconds"])),
        "circuit_breaker_rejections": circuit_rejections,
        "cpu_seconds": {"measured_total": cpu_total, "complete_requests": len(completed) - cpu_incomplete,
                        "incomplete_requests": cpu_incomplete},
        "models": model_metrics.summarize(model_calls), "requests_by_route": dict(routes),
        "malformed_records_skipped": malformed,
        "recording_enabled": config.OPERATIONAL_METRICS_ENABLED,
        "note": "Includes this metrics request's receipt; averages/statuses use completed requests only. Unfinished receipts may be in flight or interrupted.",
    }
