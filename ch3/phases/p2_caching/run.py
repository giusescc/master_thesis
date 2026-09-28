"""P2 HTTP caching: does a caching proxy between appR and CSS serve a cached
copy after the revoke? (HYPOTHESES.md, P2)

    npm run exp:p2 [-- --config wac|acp] [--variant proxyA|proxyB] [--reps N] [--dry-run]
"""

from __future__ import annotations

import hashlib
import time

from ch3.lib import harness, proxy, scene
from ch3.lib.agents import Agent, response_record
from ch3.lib.env import base_url

POST_S, INTERVAL_S = 70.0, 1.0


def _h(headers, name: str) -> str:
    return next((v for k, v in headers.items() if k.lower() == name.lower()), "<absent>")


def _obs(log, event: str, agent: Agent, url: str, **extra) -> dict:
    r = agent.get(url)
    rec = response_record(r)
    rec["body_sha256"] = hashlib.sha256(r.content).hexdigest()
    rec["cache_status"] = _h(r.headers, "X-Cache-Status")
    log.write(event, agent=agent.name, **rec, **extra)
    return rec


def run_one(log, config, variant, rep, rng) -> None:
    s = scene.build(log, config)
    origin, front = base_url(config), proxy.proxy_base(variant, config)
    via = lambda url: front + url[len(origin):]  # noqa: E731
    anon = Agent.of(config, "anonymous")
    for agent in (s.appr, s.bob):
        agent.htu_rewrite = (front, origin)  # DPoP names the origin URL (lab arrangement)
    log.write("proxy", variant=variant, image=proxy.IMAGE, front=front, origin=origin)

    direct_before = _obs(log, "direct_before", s.appr, s.person)
    p1 = _obs(log, "proxy_before", s.appr, via(s.person), n=1)
    p2 = _obs(log, "proxy_before", s.appr, via(s.person), n=2)
    bob_before = _obs(log, "proxy_before", s.bob, via(s.person), n=1)

    marks = scene.revoke(log, s, s.person, [s.bob.web_id])
    revoke_done = marks["done"]["t_ms"]
    direct_after = _obs(log, "direct_after", s.appr, s.person)
    anon_proxy_early = _obs(log, "anon_proxy_after", anon, via(s.person), when="early")
    anon_direct = _obs(log, "anon_direct_after", anon, s.person)

    polls = []
    t0 = time.perf_counter()
    k = 0
    while (k * INTERVAL_S) <= POST_S:
        delay = t0 + k * INTERVAL_S - time.perf_counter()
        if delay > 0:
            time.sleep(delay)
        rec = _obs(log, "proxy_after", s.appr, via(s.person), k=k)
        rec["t_ms"] = log.t_ms()
        polls.append(rec)
        k += 1
    anon_proxy_late = _obs(log, "anon_proxy_after", anon, via(s.person), when="late")
    bob_after = _obs(log, "proxy_after_bob", s.bob, via(s.person))

    fixture_hash = p1["body_sha256"]
    stale = [p for p in polls if p["status"] == 200]
    stale_same_body = all(p["body_sha256"] == fixture_hash for p in stale)
    first_denied = next((p for p in polls if p["status"] != 200), None)
    ordered = [p["status"] == 200 for p in polls]
    # stale reads form one block at the start, then denial (no 200 after a denial)
    contiguous = ordered == sorted(ordered, reverse=True)
    origin_hdrs = direct_before["headers"]

    log.summary(
        outcome={
            "origin_cache_control": _h(origin_hdrs, "Cache-Control"),
            "origin_expires": _h(origin_hdrs, "Expires"),
            "origin_vary": _h(origin_hdrs, "Vary"),
            "origin_has_etag": _h(origin_hdrs, "ETag") != "<absent>",
            "origin_has_last_modified": _h(origin_hdrs, "Last-Modified") != "<absent>",
            "origin_wac_allow": _h(origin_hdrs, "WAC-Allow"),
            "proxy_before_cache_status": [p1["cache_status"], p2["cache_status"]],
            "bob_before": [bob_before["status"], bob_before["cache_status"]],
            "direct_after_status": direct_after["status"],
            "proxy_served_cached_after_revoke": bool(stale),
            "proxy_after_first": [polls[0]["status"], polls[0]["cache_status"]],
            "proxy_stale_body_equals_fixture": stale_same_body if stale else None,
            "proxy_denied_within_window": first_denied is not None,
            "proxy_after_denied_status": first_denied["status"] if first_denied else None,
            "proxy_stale_then_denied_contiguous": contiguous,
            "anon_proxy_after_early": [anon_proxy_early["status"], anon_proxy_early["cache_status"]],
            "anon_proxy_after_late_status": anon_proxy_late["status"],
            "anon_direct_after_status": anon_direct["status"],
            "bob_after_status": bob_after["status"],
        },
        metrics={
            "stale_reads": len(stale),
            "stale_window_ms": round(stale[-1]["t_ms"] - revoke_done, 1) if stale else 0,
            "first_denied_after_revoke_ms": round(first_denied["t_ms"] - revoke_done, 1) if first_denied else None,
            "last_stale_age_header": stale[-1]["headers"].get("Age") if stale else None,
            "polls": len(polls),
        },
    )


if __name__ == "__main__":
    raise SystemExit(harness.main(
        "p2", run_one,
        before_variant=lambda config, variant: proxy.start(variant),
        after_variant=lambda config, variant: proxy.stop(variant),
    ))
