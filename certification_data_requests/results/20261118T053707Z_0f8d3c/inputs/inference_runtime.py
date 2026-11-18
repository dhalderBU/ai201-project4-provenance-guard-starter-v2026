"""One persistent, killable CPU inference process; it never writes application records."""

import atexit
import multiprocessing
import threading
import time

import config
import model_metrics


class InferenceRejected(RuntimeError):
    def __init__(self, code, message, retry_after=0):
        super().__init__(message)
        self.code, self.retry_after = code, retry_after


class CircuitBreaker:
    def __init__(self, clock=time.monotonic):
        self.clock = clock
        self.lock = threading.Lock()
        self.state = "closed"
        self.failures = 0
        self.open_until = 0.0

    def enter(self):
        with self.lock:
            if self.state == "open":
                remaining = self.open_until - self.clock()
                if remaining > 0:
                    return False, remaining
                self.state = "half_open"
                return True, 0
            return (False, 1) if self.state == "half_open" else (True, 0)

    def finish(self, timed_out, success, threshold, recovery):
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
        with self.lock:
            return {"state": self.state, "consecutive_timeouts": self.failures,
                    "retry_after_seconds": max(0.0, self.open_until - self.clock()) if self.state == "open" else 0.0}


def _execute(job, text):
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
            collector, token = model_metrics.begin(
                lambda record: connection.send({"type": "model_call", "record": record})
            )
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
    def __init__(self, target=_worker):
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
        if not config.INFERENCE_PROCESS_ENABLED:
            return
        with self.guard:
            self._start_locked()
            self._refresh_locked()

    def close(self):
        with self.guard:
            self.closed = True
            self._stop_locked()

    def snapshot(self):
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
                        operations.check_deadline()
                        return message["value"]
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


breaker = CircuitBreaker()
engine = InferenceProcess()
atexit.register(engine.close)


def call(job, text):
    import operations
    state = operations.current()
    operations.check_deadline()
    if state is None:
        return _execute(job, text)
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
    if getattr(state, "inference_reserved", False):
        state.inference_reserved = False
        engine.reservation.release()
