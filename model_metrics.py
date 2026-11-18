"""Collect token counts and CPU/wall time for individual model forward passes.

Measurement flow:
    1. ``operations`` starts a collector for each request; ``inference_runtime``
       starts a separate collector for each computation job in its worker.
    2. Detector and Binoculars code wrap model calls with ``forward_pass()``.
       It records a running event, then updates the same call on exit.
    3. The worker's optional sink streams each update through the pipe. The HTTP
       process merges those records into its request collector by call_id.
    4. ``summarize()`` groups the latest call records by model for operational
       completions and metrics reports. ``end()`` restores the previous context.

This module does not write log files or enforce deadlines. It measures the
wrapped computation, not the whole request. Generated output tokens are zero
because the instrumented models score supplied text rather than generate text.
"""

from contextlib import contextmanager
from contextvars import ContextVar
import time
import uuid

# Keep concurrent execution contexts separate; callers restore the previous
# binding with the token returned by begin().
_collector = ContextVar("model_metrics", default=None)


class Collector:
    """Keep the latest measurement for each call and optionally forward updates.

    A running event and its final event share a call_id. Replacing that entry
    prevents one forward pass being counted twice after updates cross the pipe.
    """

    def __init__(self, sink=None):
        """Create an empty collector with an optional synchronous record callback."""
        self.calls = {}
        self.sink = sink

    def update(self, record):
        """Replace a call's record and pass a separate shallow copy to the sink.

        Copies protect saved measurements from later changes to the input dict
        or the dict received by the sink. Missing call IDs and sink errors
        propagate to the caller.
        """
        self.calls[record["call_id"]] = dict(record)
        if self.sink:
            self.sink(dict(record))


def begin(sink=None):
    """Bind a new collector and return (collector, context_token).

    An optional sink receives every update, as used by the worker's pipe sender.
    Pair this with end(context_token) in a finally block to restore prior state.
    """
    collector = Collector(sink)
    token = _collector.set(collector)
    return collector, token


def end(token):
    """Restore the collector binding saved by begin() in the same context."""
    _collector.reset(token)


@contextmanager
def forward_pass(model, stage, input_tokens, scored_tokens):
    """Measure one wrapped model computation, or yield unmeasured if no collector.

    Args:
        model: Configured model name used as the aggregation key.
        stage: Call purpose, such as perplexity or binoculars_observer.
        input_tokens: Actual token count passed to the model after truncation.
        scored_tokens: Prediction positions used by this scoring pass.

    The call starts as running, becomes completed on normal exit, or becomes
    failed if the wrapped block raises. Exceptions are re-raised after timing is
    recorded. Wall time uses perf_counter(); process_time() includes CPU consumed
    by the process's threads, so CPU seconds can exceed elapsed seconds.

    A forcibly killed worker cannot execute finally: its streamed running record
    retains null timings, and operations marks its status aborted/incomplete.
    Output tokens mean generated tokens and remain zero for these scoring calls.
    """
    collector = _collector.get()
    if collector is None:
        yield
        return
    record = {"call_id": uuid.uuid4().hex, "model": model, "stage": stage,
              "input_tokens": int(input_tokens), "output_tokens": 0,
              "scored_tokens": int(scored_tokens), "status": "running",
              "duration_seconds": None, "cpu_seconds": None}
    # Publish the call before entering model code so a timeout can retain its
    # input-token count even when no final measurements return from the worker.
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
        # Reuse the call ID to replace the running record, including on failure.
        record["duration_seconds"] = time.perf_counter() - started
        record["cpu_seconds"] = time.process_time() - cpu_started
        collector.update(record)


def summarize(calls):
    """Return per-model totals from an iterable of latest-per-call records.

    Pass Collector.calls.values() or equivalent records already deduplicated by
    call ID; this function sums its input and does not deduplicate it. Every
    started pass contributes calls/input_tokens. Only completed passes contribute
    completed_input_tokens and scored_tokens; all other statuses count as
    incomplete_calls. Available timings are summed even for failed calls, while
    None timings are omitted. No calls produces an empty dictionary.
    """
    result = {}
    for call in calls:
        row = result.setdefault(call["model"], {
            "calls": 0, "completed_calls": 0, "incomplete_calls": 0,
            "input_tokens": 0, "completed_input_tokens": 0, "output_tokens": 0,
            "scored_tokens": 0, "measured_duration_seconds": 0.0,
            "measured_cpu_seconds": 0.0,
        })
        row["calls"] += 1
        # Started-token totals include interrupted work. Keep completed-token
        # totals separate so incomplete inference is not presented as finished.
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
