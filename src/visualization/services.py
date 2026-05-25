"""Asynchronous execution services for the dashboard."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from queue import Empty, Queue
from typing import Any, Callable


@dataclass(frozen=True)
class TaskEvent:
    """Event emitted by the background runner."""

    kind: str
    payload: Any


class BackgroundRunner:
    """Single-worker background executor for UI-safe I/O."""

    def __init__(self) -> None:
        self._events: Queue[TaskEvent] = Queue()
        self._executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="spotify-dashboard")

    def submit(self, label: str, task: Callable[[], Any]) -> None:
        """Schedule a task and emit lifecycle events."""
        self._events.put(TaskEvent("started", label))
        self._executor.submit(self._run_task, label, task)

    def drain(self) -> list[TaskEvent]:
        """Return all queued task events."""
        events: list[TaskEvent] = []
        while True:
            try:
                events.append(self._events.get_nowait())
            except Empty:
                return events

    def shutdown(self) -> None:
        """Stop the background executor."""
        self._executor.shutdown(wait=False, cancel_futures=True)

    def _run_task(self, label: str, task: Callable[[], Any]) -> None:
        """Execute work and capture its outcome."""
        try:
            result = task()
        except Exception as exc:  # pragma: no cover
            self._events.put(TaskEvent("failed", (label, exc)))
            return
        self._events.put(TaskEvent("completed", (label, result)))
