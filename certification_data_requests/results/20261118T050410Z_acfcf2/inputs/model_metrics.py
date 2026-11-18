"""Per-forward-pass measurements, independent of Flask and shared with the worker."""

from contextlib import contextmanager
from contextvars import ContextVar
import time
import uuid

_collector = ContextVar("model_metrics", default=None)


class Collector:
    def __init__(self, sink=None):
        self.calls = {}
        self.sink = sink

    def update(self, record):
        self.calls[record["call_id"]] = dict(record)
        if self.sink:
            self.sink(dict(record))


def begin(sink=None):
    collector = Collector(sink)
    token = _collector.set(collector)
    return collector, token


def end(token):
    _collector.reset(token)


@contextmanager
def forward_pass(model, stage, input_tokens, scored_tokens):
    """Output tokens means generated tokens: these scoring models generate zero."""
    collector = _collector.get()
    if collector is None:
        yield
        return
    record = {"call_id": uuid.uuid4().hex, "model": model, "stage": stage,
              "input_tokens": int(input_tokens), "output_tokens": 0,
              "scored_tokens": int(scored_tokens), "status": "running",
              "duration_seconds": None, "cpu_seconds": None}
    collector.update(record)
    started, cpu_started = time.perf_counter(), time.process_time()
    try:
        yield
    except BaseException:
        record["status"] = "failed"
        raise
    else:
        record["status"] = "completed"
    finally:
        record["duration_seconds"] = time.perf_counter() - started
        record["cpu_seconds"] = time.process_time() - cpu_started
        collector.update(record)


def summarize(calls):
    result = {}
    for call in calls:
        row = result.setdefault(call["model"], {
            "calls": 0, "completed_calls": 0, "incomplete_calls": 0,
            "input_tokens": 0, "completed_input_tokens": 0, "output_tokens": 0,
            "scored_tokens": 0, "measured_duration_seconds": 0.0,
            "measured_cpu_seconds": 0.0,
        })
        row["calls"] += 1
        row["input_tokens"] += call["input_tokens"]
        row["output_tokens"] += call["output_tokens"]
        if call["status"] == "completed":
            row["completed_calls"] += 1
            row["completed_input_tokens"] += call["input_tokens"]
            row["scored_tokens"] += call["scored_tokens"]
        else:
            row["incomplete_calls"] += 1
        for source, dest in (("duration_seconds", "measured_duration_seconds"),
                             ("cpu_seconds", "measured_cpu_seconds")):
            if call[source] is not None:
                row[dest] += call[source]
    return result
