"""Run scoring in one persistent CPU process with deadlines and circuit control.

Execution flow:
    1. Native startup or Gunicorn calls ``engine.start()``. The spawned worker
       loads models and reports readiness; loading is outside request budgets.
    2. A scoring route calls ``call(job, text)`` with its operations.RequestState.
       The first call checks the circuit and reserves the single computation slot.
    3. ``engine.run()`` sends the job through a local pipe and collects streamed
       model measurements until the worker returns a result or error.
    4. Later stages of the same request reuse its reservation and original
       deadline. Expiry while waiting kills the worker and starts model reload.
    5. The HTTP route saves business records. The operations completion hook
       updates the circuit and calls ``release()`` even after a failed request.

The worker performs computation only; it never writes submissions, certificates,
or audit records. Health/metrics handlers and existing-certificate lookups do not
call this scoring path. Standalone calls without request state execute inline;
inline HTTP execution is reserved for tests with request timeouts disabled.
"""

import atexit
import multiprocessing
import threading
import time

import config
import model_metrics


class InferenceRejected(RuntimeError):
    """Describe unavailable scoring; operations.install() maps this to HTTP 503."""

    def __init__(self, code, message, retry_after=0):
        """Keep the JSON error code, readable reason, and optional retry seconds."""
        super().__init__(message)
        self.code, self.retry_after = code, retry_after


class CircuitBreaker:
    """Track scoring timeouts and allow one recovery probe after a cooldown.

    State is shared by threads in one HTTP worker and resets on restart. Closed
    admits requests; open rejects them until cooldown expires; half_open admits
    only the probe already selected by enter(). Computation-slot reservation is
    separate and can reject a request even after circuit admission.
    """

    def __init__(self, clock=time.monotonic):
        """Start closed, using an injectable monotonic clock for recovery timing."""
        self.clock = clock
        self.lock = threading.Lock()
        self.state = "closed"
        self.failures = 0
        self.open_until = 0.0

    def enter(self):
        """Return (allowed, retry_seconds), admitting at most one half-open probe."""
        with self.lock:
            if self.state == "open":
                remaining = self.open_until - self.clock()
                if remaining > 0:
                    return False, remaining
                self.state = "half_open"
                return True, 0
            return (False, 1) if self.state == "half_open" else (True, 0)

    def finish(self, timed_out, success, threshold, recovery):
        """Update the circuit once an admitted HTTP request has finished.

        operations passes success=True for HTTP statuses below 500. Timeouts
        accumulate until the threshold opens the circuit; a successful request
        resets a closed circuit's count. A half-open probe closes the circuit on
        success or starts a new cooldown on failure. Other closed-state failures
        do not clear the timeout count.
        """
        with self.lock:
            if timed_out:
                self.failures += 1
            if timed_out and (self.failures >= threshold or self.state == "half_open"):
                self.state, self.open_until = "open", self.clock() + recovery
            elif self.state == "half_open":
                if success:
                    self.state, self.failures = "closed", 0
                else:
                    self.state, self.open_until = "open", self.clock() + recovery
            elif success and self.state == "closed":
                self.failures = 0

    def snapshot(self):
        """Return the current state, timeout count, and remaining open cooldown."""
        with self.lock:
            return {"state": self.state, "consecutive_timeouts": self.failures,
                    "retry_after_seconds": max(0.0, self.open_until - self.clock()) if self.state == "open" else 0.0}


def _execute(job, text):
    """Dispatch one named computation job without persistence or HTTP handling.

    Supported jobs are perplexity, binoculars, style, and appeal. The worker uses
    this dispatcher after warm-up; standalone/mock-based calls also use it inline.
    Unknown job names raise ValueError, and scoring errors propagate to the caller.
    """
    if job == "perplexity":
        import detector
        return detector.model_signal(text)
    if job == "binoculars":
        import binoculars_signal
        return binoculars_signal.binoculars_signal(text)
    if job == "style":
        import stylometry
        return stylometry.style_signal(text)
    if job == "appeal":
        import appeals
        return appeals.reassess(text)
    raise ValueError("Unknown inference job")


def _worker(connection, settings):
    """Load models in the child process, then serve jobs from the parent's pipe.

    The protocol sends ready/startup_error once at initialization. Each received
    (job, text) produces zero or more model_call messages followed by result/error
    with measured process CPU seconds. Application errors are sent as a type name
    and message; the parent reconstructs supported exceptions. Losing the parent
    connection ends the loop and closes the child endpoint.
    """
    # Spawn starts a fresh interpreter. Apply the parent's selected scoring
    # settings before importing modules that read configuration at import time.
    for name, value in settings.items():
        setattr(config, name, value)
    try:
        import detector
        import binoculars_signal
        detector.warm_up()
        binoculars_error = None
        try:
            binoculars_signal._load_performer()
        except detector.DetectorUnavailable as exc:
            # Preserve the original perplexity-only fallback when the optional
            # performer is unavailable. Retry its initialization on restart.
            binoculars_error = str(exc)
        connection.send({"type": "ready", "binoculars_ready": binoculars_error is None,
                         "binoculars_error": binoculars_error})
    except Exception as exc:
        connection.send({"type": "startup_error", "message": str(exc)})
        connection.close()
        return
    try:
        while True:
            job, text = connection.recv()
            # Stream call starts/completions immediately so the parent retains
            # partial measurements if this process must be killed mid-job.
            collector, token = model_metrics.begin(
                lambda record: connection.send({"type": "model_call", "record": record})
            )
            # Process CPU includes inference threads, but excludes startup and
            # time waiting above for the next job. It can exceed elapsed time.
            cpu_started = time.process_time()
            try:
                if job == "binoculars" and binoculars_error:
                    raise detector.DetectorUnavailable(binoculars_error)
                result = {"type": "result", "value": _execute(job, text)}
            except Exception as exc:
                result = {"type": "error", "error_type": type(exc).__name__, "message": str(exc)}
            finally:
                model_metrics.end(token)
            result["cpu_seconds"] = time.process_time() - cpu_started
            connection.send(result)
    except (EOFError, BrokenPipeError, OSError):
        pass
    finally:
        connection.close()


class InferenceProcess:
    """Own the child process, its pipe, readiness state, and request reservation.

    guard protects process/pipe operations during startup, health inspection,
    and a running job. reservation is held across every stage of one HTTP
    request, preventing other scoring requests from waiting behind its work.
    Health snapshots use a nonblocking guard acquisition so scoring cannot make
    health checks wait for a model result.
    """

    def __init__(self, target=_worker):
        """Initialize a stopped engine; tests may supply a lightweight worker target."""
        self.target = target
        self.guard = threading.Lock()
        self.reservation = threading.Lock()
        self.process = None
        self.connection = None
        self.ready = False
        self.binoculars_ready = False
        self.binoculars_error = None
        self.error = None
        self.retry_at = 0.0
        self.closed = False

    def _start_locked(self):
        """Spawn the worker when eligible; the caller must hold guard.

        A live process, permanent closure, or startup-retry cooldown prevents a
        new spawn. Only selected scoring settings are copied into the child.
        """
        if self.closed or self.process is not None or time.monotonic() < self.retry_at:
            return
        context = multiprocessing.get_context("spawn")
        parent, child = context.Pipe()
        settings = {name: getattr(config, name) for name in (
            "DETECTOR_MODEL", "DETECTOR_MAX_TOKENS", "BINOCULARS_PERFORMER",
            "BINOCULARS_MIDPOINT", "BINOCULARS_STEEPNESS", "BINOCULARS_SKIP_TOKENS",
            "APPEAL_WEIGHT_MODEL_SIGNAL", "APPEAL_WEIGHT_STYLE_SIGNAL", "HUMAN_THRESHOLD", "AI_THRESHOLD")}
        self.process = context.Process(target=self.target, args=(child, settings), daemon=True)
        self.process.start()
        child.close()
        self.connection = parent
        self.ready, self.error = False, None
        self.binoculars_ready, self.binoculars_error = False, None

    def _stop_locked(self):
        """Kill the current worker and clear its pipe/readiness while holding guard.

        This stops the current process without permanently closing the engine;
        close() sets the separate closed flag when replacement is no longer wanted.
        """
        if self.process is not None:
            if self.process.is_alive():
                self.process.kill()
            self.process.join(timeout=0.05)
            if not self.process.is_alive():
                self.process.close()
        if self.connection is not None:
            self.connection.close()
        self.process, self.connection, self.ready = None, None, False
        self.binoculars_ready = False

    def _refresh_locked(self):
        """Consume startup status or detect worker death while holding guard.

        Startup failures discard the process and set a retry cooldown. Optional
        performer failure is reported separately and leaves the detector usable.
        A later start(), snapshot(), or run() can initiate an eligible replacement.
        """
        if self.process is not None and self.ready and not self.process.is_alive():
            self.error = "Inference process exited; waiting for model reload."
            self._stop_locked()
        if self.connection and not self.ready and self.connection.poll():
            try:
                message = self.connection.recv()
            except (EOFError, OSError):
                message = {"type": "startup_error", "message": "Inference process exited during startup."}
            if message["type"] == "ready":
                self.ready = True
                self.binoculars_ready = message.get("binoculars_ready", True)
                self.binoculars_error = message.get("binoculars_error")
            else:
                self.error = message.get("message", "Model startup failed.")
                self._stop_locked()
                self.retry_at = time.monotonic() + config.CIRCUIT_BREAKER_RECOVERY_SECONDS

    def start(self):
        """Begin startup and refresh available status without waiting for readiness."""
        if not config.INFERENCE_PROCESS_ENABLED:
            return
        with self.guard:
            self._start_locked()
            self._refresh_locked()

    def close(self):
        """Permanently close this engine and stop its child during server shutdown."""
        with self.guard:
            self.closed = True
            self._stop_locked()

    def snapshot(self):
        """Return readiness/startup errors without blocking behind an active job.

        When the guard is available, refresh state and start an eligible worker.
        Otherwise return the last known flags. Ready means models are loaded, not
        that the computation slot is free or the circuit will admit a request.
        """
        if self.guard.acquire(blocking=False):
            try:
                self._refresh_locked()
                if config.INFERENCE_PROCESS_ENABLED:
                    self._start_locked()
            finally:
                self.guard.release()
        return {"ready": self.ready, "startup_error": self.error,
                "binoculars_ready": self.binoculars_ready, "binoculars_error": self.binoculars_error}

    def run(self, job, text, state):
        """Execute one job using the caller's remaining shared request budget.

        The caller has already reserved the computation slot. An unready worker
        raises InferenceRejected immediately instead of waiting for model loading.
        Streamed measurements update state.collector; the final message adds CPU
        time and returns a value or raises the corresponding scoring exception.

        Expiry while waiting marks CPU incomplete, kills the process, schedules
        model reload, and raises DeadlineExceeded. A lost pipe produces
        InferenceRejected instead. No failed or abandoned job is replayed.
        """
        import detector
        import operations
        with self.guard:
            self._start_locked()
            self._refresh_locked()
            if not self.ready:
                raise InferenceRejected("model_not_ready", "Models are loading or unavailable; retry when /health reports inference_ready.", 1)
            try:
                self.connection.send((job, text))
                while True:
                    # Recompute remaining time after every streamed message.
                    # Starting another stage must not reset the request budget.
                    remaining = state.deadline - time.perf_counter() if state.timeout_enabled else None
                    if remaining is not None and remaining <= 0:
                        state.timed_out, state.cpu_complete = True, False
                        self._stop_locked()
                        # Reload only model state, never an abandoned request.
                        threading.Thread(target=self.start, daemon=True).start()
                        raise operations.DeadlineExceeded("The request exceeded its processing-time limit.")
                    if not self.connection.poll(remaining):
                        continue
                    message = self.connection.recv()
                    if message["type"] == "model_call":
                        state.collector.update(message["record"])
                        continue
                    state.inference_cpu_seconds += message["cpu_seconds"]
                    if message["type"] == "result":
                        # A result can arrive at the deadline boundary; reject
                        # it here before the route can persist a successful score.
                        operations.check_deadline()
                        return message["value"]
                    # Preserve errors that app.py handles explicitly for 400s
                    # and optional-model fallback; unexpected errors become 500s.
                    if message["error_type"] == "TextTooShortError":
                        if job == "style":
                            import stylometry
                            raise stylometry.TextTooShortError(message["message"])
                        raise detector.TextTooShortError(message["message"])
                    if message["error_type"] == "DetectorUnavailable":
                        raise detector.DetectorUnavailable(message["message"])
                    raise RuntimeError("Inference worker failed: " + message["message"])
            except (EOFError, BrokenPipeError, OSError) as exc:
                state.cpu_complete = False
                self._stop_locked()
                raise InferenceRejected("inference_unavailable", "The inference process exited; retry after model reload.", 1) from exc


# One pair is shared by threads in this HTTP worker. Gunicorn/native startup
# starts the engine; explicit worker shutdown and interpreter exit both close it.
breaker = CircuitBreaker()
engine = InferenceProcess()
atexit.register(engine.close)


def call(job, text):
    """Admit a scoring stage, reserve its request's slot, and execute the job.

    With active request state, check the deadline first and enter the circuit
    once for the whole request. Reserve the engine without waiting, then reuse
    that reservation for later stages until the operations completion hook
    releases it. Rejections carry the reason used in the HTTP 503 response.

    Without request state, execute inline for standalone callers. Disabling
    process isolation inside a request is allowed only with timeouts disabled;
    that test mode marks total CPU incomplete because no child reports CPU time.
    """
    import operations
    state = operations.current()
    operations.check_deadline()
    if state is None:
        return _execute(job, text)
    # Calls for perplexity, Binoculars, and style belong to one admitted request,
    # so neither the breaker count nor reservation is acquired anew per stage.
    if state.breaker_enabled and not state.breaker_admitted:
        allowed, retry_after = breaker.enter()
        if not allowed:
            state.circuit_rejected = True
            raise InferenceRejected("circuit_open", "Scoring is temporarily paused after repeated timeouts.", retry_after)
        state.breaker, state.breaker_admitted = breaker, True
    if not config.INFERENCE_PROCESS_ENABLED:
        if state.timeout_enabled:
            raise InferenceRejected("invalid_timeout_configuration", "Request timeouts require inference process isolation.")
        state.cpu_complete = False
        return _execute(job, text)
    if not getattr(state, "inference_reserved", False):
        if not engine.reservation.acquire(blocking=False):
            raise InferenceRejected("inference_busy", "Another scoring request is running; retry shortly.", 1)
        state.inference_reserved = True
    return engine.run(job, text, state)


def release(state):
    """Release a request's computation reservation once during response finalization.

    Requests that never reserved inference, including certificate lookups, are
    harmless no-ops here. The completion hook calls this even if logging fails.
    """
    if getattr(state, "inference_reserved", False):
        state.inference_reserved = False
        engine.reservation.release()
