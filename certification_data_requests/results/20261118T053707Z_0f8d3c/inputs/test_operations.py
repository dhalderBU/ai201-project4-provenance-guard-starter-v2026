"""Operational counts, actual child-process cancellation, breaker recovery, and token accounting."""

from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import tempfile
import threading
import time
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from app import app
import config
import inference_runtime
import model_metrics
import operations


def fake_worker(connection, settings):
    """A real child process with predictable work; no model downloads."""
    connection.send({"type": "ready"})
    try:
        while True:
            job, text = connection.recv()
            collector, token = model_metrics.begin(
                lambda record: connection.send({"type": "model_call", "record": record}))
            started = time.process_time()
            if text == "crash":
                os._exit(2)
            model = settings["DETECTOR_MODEL"]
            if job == "style":
                if text == "style_short":
                    model_metrics.end(token)
                    connection.send({"type": "error", "error_type": "TextTooShortError",
                                     "message": "Need more sentences", "cpu_seconds": time.process_time() - started})
                    continue
                time.sleep(0.5 if text.startswith("style_slow") else 0.001)
            else:
                with model_metrics.forward_pass(model, job, 7, 6):
                    time.sleep(0.5 if text.startswith("slow") else 0.04 if text.startswith("medium") else 0.001)
            if job == "binoculars":
                with model_metrics.forward_pass(settings["BINOCULARS_PERFORMER"], "performer", 7, 6):
                    time.sleep(0.001)
            value = {"perplexity": 0.8, "binoculars": 0.2, "style": 0.4}[job]
            model_metrics.end(token)
            connection.send({"type": "result", "value": value,
                             "cpu_seconds": time.process_time() - started})
    except (EOFError, BrokenPipeError, OSError):
        pass


class OperationalApiTests(unittest.TestCase):
    def setUp(self):
        root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.enterContext(patch.object(config, "LOG_DIR", root))
        for setting, name in [("AUDIT_LOG", "audit.jsonl"), ("SUBMISSIONS_FILE", "submissions.jsonl"),
                              ("VERIFIED_HUMAN_CERTIFICATION_LOG", "certificates.jsonl")]:
            self.enterContext(patch.object(config, setting, root / name))
        self.enterContext(patch.object(config, "OPERATIONAL_METRICS_ENABLED", True))
        self.enterContext(patch.object(config, "REQUEST_TIMEOUT_ENABLED", False))
        self.enterContext(patch.object(config, "CIRCUIT_BREAKER_ENABLED", False))
        self.enterContext(patch.object(config, "INFERENCE_PROCESS_ENABLED", False))
        self.client = app.test_client()
        self.client.environ_base["REMOTE_ADDR"] = self.id()

    def records(self):
        return [json.loads(line) for line in operations.log_path().read_text().splitlines()]

    def test_receipt_and_completion_link_to_request_header_and_capture_errors(self):
        ping = self.client.post("/ping", json={"message": "check"})
        missing = self.client.get("/missing-operational-test-route")
        invalid = self.client.post("/submit", json={"text": ""})
        self.assertEqual([ping.status_code, missing.status_code, invalid.status_code], [200, 404, 400])
        rows = self.records()
        self.assertEqual(len(rows), 6)
        for index, response in enumerate((ping, missing, invalid)):
            received, completed = rows[index * 2:index * 2 + 2]
            self.assertEqual(received["event"], "request_received")
            self.assertEqual(completed["event"], "request_completed")
            self.assertEqual(received["request_id"], response.headers["X-Request-ID"])
            self.assertEqual(completed["request_id"], received["request_id"])
            self.assertGreaterEqual(completed["duration_seconds"], 0)
            self.assertEqual(completed["http_status"], response.status_code)
            self.assertEqual(completed["models"], {})

    def test_metrics_download_includes_own_receipt_but_not_own_completion(self):
        self.client.post("/ping", json={})
        response = self.client.get("/metrics?hours=1&download=1")
        self.assertEqual(response.status_code, 200)
        body = response.get_json()
        self.assertEqual(body["requests_received"], 2)
        self.assertEqual(body["requests_completed"], 1)
        self.assertEqual(body["requests_without_completion"], 1)
        self.assertEqual(body["http_status_counts"]["200"], 1)
        self.assertEqual(body["classification_counts"], {"human": 0, "ai": 0, "unsure": 0})
        self.assertEqual(response.mimetype, "application/json")
        self.assertIn('filename="operational-metrics-last-1-hours.json"', response.headers["Content-Disposition"])

    def test_invalid_hours_are_rejected_and_fractional_hours_work(self):
        for hours in ("0", "-1", "nan", "inf", "nope", "721"):
            with self.subTest(hours=hours):
                self.assertEqual(self.client.get("/metrics?hours=" + hours).status_code, 400)
        self.assertEqual(self.client.get("/metrics?hours=0.5").status_code, 200)

    def test_recording_can_be_disabled(self):
        with patch.object(config, "OPERATIONAL_METRICS_ENABLED", False):
            self.assertEqual(self.client.post("/ping", json={}).status_code, 200)
        self.assertFalse(operations.log_path().exists())

    def test_log_failure_prevents_unrecorded_business_work(self):
        with patch("operations.append", side_effect=OSError("disk unavailable")), patch("detector.model_signal") as model:
            with self.assertLogs(app.logger, level="ERROR"):
                response = self.client.post("/submit", json={"text": "input"})
            self.assertEqual(response.status_code, 503)
            model.assert_not_called()

    def test_unexpected_exception_is_recorded_as_500_and_next_request_is_clean(self):
        def broken():
            raise RuntimeError("test failure")
        with patch.dict(app.config, TESTING=False, PROPAGATE_EXCEPTIONS=False), patch.dict(
                app.view_functions, ping=broken), self.assertLogs(app.logger, level="ERROR"):
            self.assertEqual(self.client.post("/ping", json={}).status_code, 500)
        self.assertEqual(self.client.post("/ping", json={}).status_code, 200)
        self.assertEqual([row["http_status"] for row in self.records() if row["event"] == "request_completed"], [500, 200])


class WindowTests(OperationalApiTests):
    def add(self, identity, when, status=None, label=None, limit=3.0, route="/submit", duration=0.2):
        row = {"event": "request_received", "request_id": identity, "received_at": when.isoformat(),
               "method": "POST", "route": route, "timeout_enabled": True, "timeout_seconds": limit}
        operations.append(row)
        if status is not None:
            operations.append({**row, "event": "request_completed", "http_status": status,
                               "label": label, "duration_seconds": duration, "timed_out": status == 504,
                               "cpu_time_seconds": None if status == 504 else 0.1,
                               "circuit_rejected": status == 503, "model_calls": []})

    def test_window_counts_statuses_labels_pending_and_historical_timeout_settings(self):
        now = datetime(2026, 11, 16, 12, tzinfo=timezone.utc)
        when = now - timedelta(minutes=10)
        cases = [(200, "human", 3), (200, "ai", 3), (200, "unsure", 3),
                 (400, None, 3), (429, None, 3), (504, None, 3),
                 (504, None, 5), (503, None, 5), (500, None, 5)]
        for index, (status, label, limit) in enumerate(cases):
            self.add(str(index), when, status, label, limit, duration=index + 1)
        self.add("appeal", when, 200, "human", route="/appeal", duration=1)
        self.add("pending", when)
        self.add("old", now - timedelta(hours=2), 200, "ai")
        self.add("future", now + timedelta(seconds=1), 200, "ai")
        with operations.log_path().open("a") as handle:
            handle.write('{broken\n{"event":"request_completed"}\n')
        result = operations.summarize(1, now)
        self.assertEqual(result["requests_received"], 11)
        self.assertEqual(result["requests_completed"], 10)
        self.assertEqual(result["requests_without_completion"], 1)
        self.assertAlmostEqual(result["average_response_time_seconds"], 4.6)
        self.assertEqual(result["classification_counts"], {"human": 1, "ai": 1, "unsure": 1})
        self.assertEqual(result["appeal_classification_counts"]["human"], 1)
        self.assertEqual(result["http_status_counts"], {"200": 4, "400": 1, "429": 1, "503": 1, "504": 2, "500": 1})
        self.assertEqual(result["timeout_count"], 2)
        self.assertEqual([(x["timeout_seconds"], x["timeouts"]) for x in result["timeout_configurations"]], [(3, 1), (5, 1)])
        self.assertEqual(result["cpu_seconds"]["incomplete_requests"], 2)
        self.assertEqual(result["malformed_records_skipped"], 2)

    def test_empty_window_has_no_invented_latency(self):
        result = operations.summarize(1)
        self.assertEqual(result["requests_received"], 0)
        self.assertIsNone(result["average_response_time_seconds"])


class BreakerTests(unittest.TestCase):
    def test_open_half_open_single_probe_and_recovery(self):
        now = [0.0]
        breaker = inference_runtime.CircuitBreaker(lambda: now[0])
        self.assertTrue(breaker.enter()[0])
        breaker.finish(True, False, 2, 10)
        self.assertEqual(breaker.snapshot()["state"], "closed")
        breaker.finish(True, False, 2, 10)
        self.assertEqual(breaker.enter(), (False, 10))
        now[0] = 10
        self.assertTrue(breaker.enter()[0])
        self.assertFalse(breaker.enter()[0])
        breaker.finish(False, True, 2, 10)
        self.assertEqual(breaker.snapshot()["state"], "closed")
        self.assertEqual(breaker.snapshot()["consecutive_timeouts"], 0)

    def test_failed_half_open_probe_reopens_and_success_resets_failure_count(self):
        now = [0.0]
        breaker = inference_runtime.CircuitBreaker(lambda: now[0])
        breaker.finish(True, False, 1, 2)
        now[0] = 3
        breaker.enter()
        breaker.finish(True, False, 1, 2)
        self.assertEqual(breaker.enter(), (False, 2))
        now[0] = 6
        breaker.enter()
        breaker.finish(False, True, 1, 2)
        self.assertEqual(breaker.snapshot()["consecutive_timeouts"], 0)


class ProcessTimeoutTests(OperationalApiTests):
    def setUp(self):
        super().setUp()
        self.enterContext(patch.object(config, "REQUEST_TIMEOUT_ENABLED", True))
        self.enterContext(patch.object(config, "REQUEST_TIMEOUT_SECONDS", 0.08))
        self.enterContext(patch.object(config, "INFERENCE_PROCESS_ENABLED", True))
        self.enterContext(patch.object(config, "CIRCUIT_BREAKER_ENABLED", True))
        self.enterContext(patch.object(config, "CIRCUIT_BREAKER_FAILURE_THRESHOLD", 1))
        self.enterContext(patch.object(config, "CIRCUIT_BREAKER_RECOVERY_SECONDS", 10))
        self.engine = inference_runtime.InferenceProcess(target=fake_worker)
        self.enterContext(patch.object(inference_runtime, "engine", self.engine))
        self.enterContext(patch.object(inference_runtime, "breaker", inference_runtime.CircuitBreaker()))
        self.addCleanup(self.engine.close)
        self.engine.start()
        self.ready()

    def ready(self):
        end = time.monotonic() + 5
        while not self.engine.snapshot()["ready"]:
            if time.monotonic() >= end:
                self.fail("Fake worker did not become ready")
            time.sleep(0.01)

    def test_timeout_kills_work_records_partial_metrics_and_opens_circuit(self):
        original_pid = self.engine.process.pid
        started = time.perf_counter()
        response = self.client.post("/submit", json={"text": "slow input", "creator_id": "deadline"})
        self.assertEqual(response.status_code, 504)
        self.assertLess(time.perf_counter() - started, 0.4)
        self.assertEqual(response.get_json()["timeout_seconds"], 0.08)
        with self.assertRaises(ProcessLookupError):
            os.kill(original_pid, 0)
        self.assertFalse(config.SUBMISSIONS_FILE.exists())
        completion = self.records()[-1]
        self.assertTrue(completion["timed_out"])
        self.assertIsNone(completion["cpu_time_seconds"])
        self.assertEqual(completion["models"][config.DETECTOR_MODEL]["input_tokens"], 7)
        self.assertEqual(completion["models"][config.DETECTOR_MODEL]["completed_input_tokens"], 0)
        self.assertEqual(completion["model_calls"][0]["status"], "aborted")
        rejected = self.client.post("/submit", json={"text": "next input"})
        self.assertEqual(rejected.status_code, 503)
        self.assertEqual(rejected.get_json()["error"], "circuit_open")
        self.assertIn("Retry-After", rejected.headers)
        self.assertTrue(self.records()[-1]["circuit_rejected"])

    def test_recovered_probe_and_token_totals_for_both_models(self):
        inference_runtime.breaker.finish(True, False, 1, 10)
        inference_runtime.breaker.open_until = time.monotonic() - 1
        with patch("stylometry.style_signal", return_value=0.4):
            response = self.client.post("/submit", json={"text": "fast input", "creator_id": "probe"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(inference_runtime.breaker.snapshot()["state"], "closed")
        row = self.records()[-1]
        self.assertEqual(row["models"][config.DETECTOR_MODEL]["input_tokens"], 14)
        self.assertEqual(row["models"][config.BINOCULARS_PERFORMER]["input_tokens"], 7)
        self.assertEqual(sum(model["output_tokens"] for model in row["models"].values()), 0)
        self.assertTrue(row["cpu_measurement_complete"])
        self.assertGreaterEqual(row["cpu_time_seconds"], 0)

    def test_breaker_flag_can_disable_open_circuit_rejection(self):
        inference_runtime.breaker.finish(True, False, 1, 10)
        with patch.object(config, "CIRCUIT_BREAKER_ENABLED", False), patch("stylometry.style_signal", return_value=0.4):
            self.assertEqual(self.client.post("/submit", json={"text": "fast input"}).status_code, 200)

    def test_timeout_flag_can_allow_a_longer_request(self):
        with patch.object(config, "REQUEST_TIMEOUT_ENABLED", False), patch("stylometry.style_signal", return_value=0.4):
            response = self.client.post("/submit", json={"text": "slow input"})
        self.assertEqual(response.status_code, 200)
        self.assertGreater(self.records()[-1]["duration_seconds"], 0.08)
        self.assertFalse(self.records()[-1]["timed_out"])

    def test_worker_exit_returns_503_without_a_submission(self):
        response = self.client.post("/submit", json={"text": "crash"})
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.get_json()["error"], "inference_unavailable")
        self.assertFalse(config.SUBMISSIONS_FILE.exists())

    def test_idle_worker_death_is_detected_and_reloaded_by_health(self):
        original_pid = self.engine.process.pid
        self.engine.process.kill()
        self.engine.process.join(timeout=1)
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.get_json()["inference_ready"])
        self.ready()
        self.assertNotEqual(self.engine.process.pid, original_pid)

    def test_worker_style_minimum_failure_still_returns_400(self):
        response = self.client.post("/submit", json={"text": "style_short"})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()["message"], "Need more sentences")
        self.assertFalse(config.SUBMISSIONS_FILE.exists())

    def test_deadline_is_shared_across_both_model_jobs(self):
        with patch.object(config, "REQUEST_TIMEOUT_SECONDS", 0.06):
            response = self.client.post("/submit", json={"text": "medium input"})
        self.assertEqual(response.status_code, 504)
        calls = self.records()[-1]["model_calls"]
        self.assertEqual(calls[0]["status"], "completed")
        self.assertEqual(calls[1]["status"], "aborted")
        self.assertFalse(config.SUBMISSIONS_FILE.exists())

    def test_style_analysis_shares_the_deadline_and_is_killed_before_persistence(self):
        started = time.perf_counter()
        response = self.client.post("/submit", json={"text": "style_slow input"})
        self.assertEqual(response.status_code, 504)
        self.assertLess(time.perf_counter() - started, 0.4)
        completion = self.records()[-1]
        self.assertEqual(len(completion["model_calls"]), 3)
        self.assertTrue(all(call["status"] == "completed" for call in completion["model_calls"]))
        self.assertFalse(completion["cpu_measurement_complete"])
        self.assertFalse(config.SUBMISSIONS_FILE.exists())

    def test_health_and_metrics_stay_responsive_and_busy_work_is_not_queued(self):
        result = []
        def score():
            with app.test_client() as client:
                result.append(client.post("/submit", json={"text": "slow input"}))
        with patch.object(config, "REQUEST_TIMEOUT_SECONDS", 0.35):
            thread = threading.Thread(target=score)
            thread.start()
            try:
                end = time.monotonic() + 1
                while not self.engine.reservation.locked():
                    self.assertLess(time.monotonic(), end)
                    time.sleep(0.002)
                started = time.perf_counter()
                self.assertEqual(self.client.get("/health").status_code, 200)
                summary = self.client.get("/metrics?hours=1")
                self.assertEqual(summary.status_code, 200)
                self.assertGreaterEqual(summary.get_json()["requests_without_completion"], 2)
                busy = self.client.post("/submit", json={"text": "fast input"})
                self.assertEqual(busy.status_code, 503)
                self.assertEqual(busy.get_json()["error"], "inference_busy")
                self.assertLess(time.perf_counter() - started, 0.25)
            finally:
                thread.join(timeout=2)
            self.assertFalse(thread.is_alive())
            self.assertEqual(result[0].status_code, 504)


class WorkerStartupTests(unittest.TestCase):
    def test_optional_performer_failure_preserves_perplexity_fallback(self):
        import detector
        from unittest.mock import Mock
        connection = Mock()
        connection.recv.side_effect = [("binoculars", "text"), ("perplexity", "text"), EOFError()]
        with patch("detector.warm_up"), patch("binoculars_signal._load_performer",
                side_effect=detector.DetectorUnavailable("performer missing")), patch(
                "inference_runtime._execute", return_value=0.4) as execute:
            inference_runtime._worker(connection, {})
        sent = [call.args[0] for call in connection.send.call_args_list]
        self.assertEqual(sent[0]["type"], "ready")
        self.assertFalse(sent[0]["binoculars_ready"])
        self.assertEqual(sent[1]["error_type"], "DetectorUnavailable")
        self.assertEqual(sent[2]["value"], 0.4)
        execute.assert_called_once_with("perplexity", "text")
        connection.close.assert_called_once()

    def test_primary_model_failure_does_not_advertise_readiness(self):
        import detector
        from unittest.mock import Mock
        connection = Mock()
        with patch("detector.warm_up", side_effect=detector.DetectorUnavailable("primary missing")):
            inference_runtime._worker(connection, {})
        self.assertEqual(connection.send.call_args.args[0]["type"], "startup_error")
        connection.recv.assert_not_called()


class ModelTokenTests(unittest.TestCase):
    def test_real_instrumented_model_functions_count_repeated_observer_passes(self):
        import torch
        import detector
        import binoculars_signal
        ids = torch.tensor([[1, 2, 3, 4, 5]])
        def tokenizer(*args, **kwargs):
            return {"input_ids": ids}
        def model(*args, **kwargs):
            return SimpleNamespace(loss=torch.tensor(1.0), logits=torch.zeros(1, 5, 8))
        collector, token = model_metrics.begin()
        try:
            with patch("detector._load", return_value=(model, tokenizer)), patch(
                    "binoculars_signal._load_performer", return_value=model):
                detector.perplexity("test")
                binoculars_signal.binoculars_score("test")
            summary = model_metrics.summarize(collector.calls.values())
        finally:
            model_metrics.end(token)
        self.assertEqual(summary[config.DETECTOR_MODEL]["calls"], 2)
        self.assertEqual(summary[config.DETECTOR_MODEL]["input_tokens"], 10)
        self.assertEqual(summary[config.DETECTOR_MODEL]["scored_tokens"], 8)
        self.assertEqual(summary[config.BINOCULARS_PERFORMER]["input_tokens"], 5)
        self.assertEqual(summary[config.BINOCULARS_PERFORMER]["scored_tokens"], 4)
        self.assertTrue(all(row["output_tokens"] == 0 for row in summary.values()))


if __name__ == "__main__":
    unittest.main()
