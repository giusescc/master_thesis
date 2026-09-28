"""Unit tests for the Chapter 3 raw-evidence logger and checker (no servers needed).

Run with ``uv run pytest -q ch3/tests``.
"""

from __future__ import annotations

import importlib
import json

import pytest


@pytest.fixture()
def ch3_tmp(tmp_path, monkeypatch):
    """Point RAW/RESULTS at a temp dir so tests never touch real evidence."""
    from ch3.lib import env

    monkeypatch.setattr(env, "RAW", tmp_path / "raw")
    monkeypatch.setattr(env, "RESULTS", tmp_path)
    from ch3.lib import jsonl

    jsonl = importlib.reload(jsonl)
    from ch3.tools import rawindex

    rawindex = importlib.reload(rawindex)
    monkeypatch.setattr(rawindex, "RAW", tmp_path / "raw")
    return jsonl, rawindex


def test_every_line_has_iso_ms_utc_ts(ch3_tmp):
    jsonl, rawindex = ch3_tmp
    log = jsonl.RunLog("p1", "wac", "direct", 1)
    log.write("observation", status=200)
    log.summary({"x": 1})
    log.close()
    for line in jsonl.read_run(log.path):
        assert rawindex.TS.match(line["ts"]), line["ts"]
    assert [l["event"] for l in jsonl.read_run(log.path)] == ["run_start", "observation", "summary", "run_end"]


def test_existing_file_is_never_overwritten(ch3_tmp, monkeypatch):
    jsonl, _ = ch3_tmp
    log = jsonl.RunLog("p1", "wac", "direct", 1)
    log.close()

    class Frozen:
        @staticmethod
        def now(tz=None):
            import datetime as dt
            return dt.datetime.strptime(log.run_id.split("-")[0], "%Y%m%dT%H%M%S.%fZ").replace(tzinfo=dt.timezone.utc)

    monkeypatch.setattr(jsonl, "datetime", Frozen)
    with pytest.raises(FileExistsError):
        jsonl.RunLog("p1", "wac", "direct", 1)


def test_manifest_detects_modification(ch3_tmp):
    jsonl, rawindex = ch3_tmp
    log = jsonl.RunLog("p1", "wac", "direct", 1)
    log.summary({"x": 1})
    log.close()
    assert rawindex.integrity() == []
    with open(log.path, "a") as fh:
        fh.write(json.dumps({"ts": "2026-01-01T00:00:00.000Z", "event": "tampered"}) + "\n")
    assert any("changed after" in p for p in rawindex.integrity())


def test_run_without_summary_is_not_completed(ch3_tmp):
    jsonl, rawindex = ch3_tmp
    log = jsonl.RunLog("p1", "wac", "direct", 1)
    log.write("run_error", error="X")
    log.close()
    (run,) = rawindex.load_runs()
    assert not run.completed
