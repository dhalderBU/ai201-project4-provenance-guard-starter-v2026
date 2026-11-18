"""Request deadlines, persistent operational records, and time-window statistics."""

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

_active = ContextVar("operation", default=None)
_file_lock = threading.Lock()


class DeadlineExceeded(RuntimeError):
    pass


def current():
    return _active.get()


def check_deadline():
    state = current()
    if state and state.timeout_enabled and time.perf_counter() >= state.deadline:
        state.timed_out = True
        raise DeadlineExceeded("The request exceeded its processing-time limit.")


def before_persist():
    check_deadline()
    if current():
        current().persistence_started = True


def log_path():
    return config.LOG_DIR / config.OPERATIONAL_LOG_FILENAME


def append(record):
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
    def __init__(self, method, path, route):
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
        return {"schema_version": 1, "request_id": self.request_id,
                "received_at": self.received_at, "method": self.method,
                "path": self.path, "route": self.route,
                "timeout_enabled": self.timeout_enabled, "timeout_seconds": self.timeout_seconds,
                "circuit_breaker_enabled": self.breaker_enabled,
                "circuit_failure_threshold": self.breaker_threshold,
                "circuit_recovery_seconds": self.breaker_recovery}


def install(app):
    """Install before the rate limiter so rejected requests are measured too."""
    from flask import jsonify, request
    import inference_runtime

    @app.before_request
    def begin_request():
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
        state = current()
        if state:
            state.timed_out = True
        return jsonify(error="request_timeout", message=str(exc),
                       request_id=state.request_id if state else None,
                       timeout_seconds=state.timeout_seconds if state else config.REQUEST_TIMEOUT_SECONDS), 504

    @app.errorhandler(inference_runtime.InferenceRejected)
    def unavailable_response(exc):
        response = jsonify(error=exc.code, message=str(exc), request_id=current().request_id)
        response.status_code = 503
        if exc.retry_after:
            response.headers["Retry-After"] = str(math.ceil(exc.retry_after))
        return response

    def finish(state, status, body):
        if state.finalized:
            return True
        state.finalized = True
        elapsed = time.perf_counter() - state.started
        calls = list(state.collector.calls.values())
        for call in calls:
            if call["status"] == "running":
                call["status"] = "aborted" if state.timed_out else "incomplete"
                state.cpu_complete = False
        if state.breaker_admitted:
            state.breaker.finish(state.timed_out, status < 500,
                                 state.breaker_threshold, state.breaker_recovery)
        body = body if isinstance(body, dict) else {}
        handler_cpu = time.thread_time() - state.cpu_started
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
            inference_runtime.release(state)
            model_metrics.end(state.metrics_token)
            _active.reset(state.state_token)
        return written

    @app.after_request
    def finish_request(response):
        state = current()
        if state is None:
            return response
        # Read-only handlers also check the shared budget. Never rewrite a
        # successful mutation as a failure after its records have been committed.
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
        state = current()
        if state is not None and not state.finalized:
            finish(state, 500, {"error": type(exc).__name__ if exc else "unfinished_request"})


def _timestamp(value):
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        raise ValueError("Timestamp must have an offset")
    return parsed.astimezone(timezone.utc)


def _percentile(values, fraction):
    if not values:
        return None
    position = (len(values) - 1) * fraction
    lower = math.floor(position)
    upper = math.ceil(position)
    return values[lower] + (values[upper] - values[lower]) * (position - lower)


def summarize(hours, now=None):
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
