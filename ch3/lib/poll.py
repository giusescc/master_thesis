"""Fixed-cadence polling on a background thread, logging every request."""

from __future__ import annotations

import threading
import time

from ch3.lib.agents import Agent, redact
from ch3.lib.jsonl import RunLog, utc_ms


class Poller(threading.Thread):
    """GET ``url`` as ``agent`` every ``interval_s`` until ``stop()``.

    The schedule is absolute (t0 + k * interval), so a slow response does not
    shift later polls. A poll is skipped only if the previous one is still
    running, and skipped slots are counted.
    """

    def __init__(self, log: RunLog, agent: Agent, url: str, interval_s: float = 0.05,
                 event: str = "poll", body: bool = False) -> None:
        super().__init__(daemon=True)
        self.log, self.agent, self.url, self.interval = log, agent, url, interval_s
        self.event, self.body = event, body
        self._halt = threading.Event()
        self.records: list[dict] = []
        self.skipped = 0

    def stop(self) -> None:
        self._halt.set()

    def run(self) -> None:
        t0 = time.perf_counter()
        k = 0
        while not self._halt.is_set():
            target = t0 + k * self.interval
            now = time.perf_counter()
            if now < target:
                time.sleep(target - now)
            elif now - target > self.interval:
                missed = int((now - target) // self.interval)
                self.skipped += missed
                k += missed
            sent_t, sent_ts = self.log.t_ms(), utc_ms()
            try:
                r = self.agent.get(self.url)
                rec = {"agent": self.agent.name, "url": self.url, "sent_ts": sent_ts, "sent_t_ms": sent_t,
                       "recv_t_ms": self.log.t_ms(), "status": r.status_code, "headers": redact(r.headers)}
                if self.body:
                    rec["body"] = r.text[:4000]
            except Exception as exc:  # noqa: BLE001 -- a transport error is an observation too
                rec = {"agent": self.agent.name, "url": self.url, "sent_ts": sent_ts, "sent_t_ms": sent_t,
                       "recv_t_ms": self.log.t_ms(), "status": None, "error": repr(exc)}
            self.records.append(rec)
            self.log.write(self.event, **rec)
            k += 1
