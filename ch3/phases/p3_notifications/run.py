"""P3 notifications: do appR's channels keep delivering after the revoke, does
anything tell appR its access ended, and who can end appR's channel?
(HYPOTHESES.md, P3)

    npm run exp:p3 [-- --config wac|acp] [--variant default|short|unsub-bob|unsub-anonymous|unsub-alice]
                   [--reps N] [--dry-run]

The ``short`` variant restarts the config's server with its 2-min-expiry
config (``ch3/start.sh --expiry short <config>``) and restores the default
afterwards.
"""

from __future__ import annotations

import subprocess
import time
from datetime import datetime

from ch3.lib import harness, scene
from ch3.lib.agents import Agent, response_record
from ch3.lib.env import CH3, base_url
from ch3.lib.notify import WebhookReceiver, WSListener, endpoint, modify, subscribe

N_MODS, MOD_INTERVAL_S, SIGNAL_WINDOW_S, SETTLE_S = 20, 1.0, 3.0, 3.0
SHORT_WAIT_S = 150.0  # 2.5 min after subscribing


def _end_at_minutes(channel: dict | None, subscribed_at: datetime) -> int | None:
    if not channel or not channel.get("endAt"):
        return None
    end = datetime.fromisoformat(channel["endAt"].replace("Z", "+00:00"))
    return round((end - subscribed_at).total_seconds() / 60)


def _count(msgs: list[dict], after_t: float, before_t: float = float("inf"), topic: str | None = None) -> int:
    return sum(1 for m in msgs if after_t < m["t_ms"] <= before_t
               and (topic is None or (m["payload"] or {}).get("object") == topic))


def _types(msgs: list[dict]) -> list[str]:
    return sorted({str((m["payload"] or {}).get("type")) for m in msgs})


def run_lifecycle(log, config, variant, rep) -> None:
    s = scene.build(log, config)
    hooks = WebhookReceiver(log)
    labels = {"ws-person": ("ws", s.person), "ws-container": ("ws", s.container),
              "hook-person": ("webhook", s.person), "hook-container": ("webhook", s.container)}
    subscribed_at = datetime.now().astimezone()
    subs = {label: subscribe(log, s.appr, kind, topic, label, hooks.url(label) if kind == "webhook" else None)
            for label, (kind, topic) in labels.items()}
    listeners = {}
    for label in ("ws-person", "ws-container"):
        ch = subs[label]["channel"]
        if ch and ch.get("receiveFrom"):
            listeners[label] = WSListener(log, label, ch["receiveFrom"])
            listeners[label].start()
            listeners[label].connected.wait(10)
    msgs = lambda label: (listeners[label].messages if label.startswith("ws") and label in listeners  # noqa: E731
                          else [m for m in hooks.messages if m["label"] == label])

    base_mark = modify(log, s.alice, s.person, "baseline")["t_ms"]
    time.sleep(SETTLE_S)
    marks = scene.revoke(log, s, s.person, [s.bob.web_id])
    revoke_t = marks["sent"]["t_ms"]
    time.sleep(SIGNAL_WINDOW_S)
    first_mod_t = None
    for k in range(1, N_MODS + 1):
        m = modify(log, s.alice, s.person, k)
        first_mod_t = first_mod_t or m["t_ms"]
        time.sleep(MOD_INTERVAL_S)
    time.sleep(SETTLE_S)
    mods_end_t = log.t_ms()

    # (i) reconnect to the old receiveFrom after the revoke
    reconnect_ok = reconnect_recv = None
    if "ws-person" in listeners:
        listeners["ws-person"].close()
        re = WSListener(log, "ws-person-reconnect", subs["ws-person"]["channel"]["receiveFrom"])
        re.start()
        re.connected.wait(10)
        reconnect_ok = re.connect_error is None
        t = modify(log, s.alice, s.person, "after-reconnect")["t_ms"]
        time.sleep(SETTLE_S)
        reconnect_recv = _count(re.messages, t) > 0
        listeners["ws-person-reconnect"] = re

    # (ii) new channels after the revoke
    new_subs = {f"new-{label}": subscribe(log, s.appr, kind, topic, f"new-{label}",
                                          hooks.url(f"new-{label}") if kind == "webhook" else None)["status"]
                for label, (kind, topic) in labels.items()}

    expiry = {}
    if variant == "short":
        remaining = SHORT_WAIT_S - (datetime.now().astimezone() - subscribed_at).total_seconds()
        log.write("waiting_for_expiry", seconds=round(max(0, remaining), 1))
        time.sleep(max(0, remaining))
        t = modify(log, s.alice, s.person, "after-expiry")["t_ms"]
        time.sleep(SETTLE_S)
        live = listeners.get("ws-person-reconnect")
        late = WSListener(log, "ws-person-after-expiry", subs["ws-person"]["channel"]["receiveFrom"])
        late.start()
        late.connected.wait(10)
        expiry = {
            "after_expiry_ws_person": _count(live.messages, t) if live else None,
            "after_expiry_hook_person": _count(msgs("hook-person"), t),
            "ws_closed_by_server_by_then": bool(live and live.closed_by == "server"),
            "reconnect_after_expiry_ok": late.connect_error is None,
        }
        listeners["ws-person-after-expiry"] = late

    for listener in listeners.values():
        listener.close()
    hooks.close()

    all_msgs = [m for l in listeners.values() for m in l.messages] + hooks.messages
    signal_msgs = [m for m in all_msgs if revoke_t < m["t_ms"] <= revoke_t + SIGNAL_WINDOW_S * 1000]
    mentions_acl = [m for m in all_msgs if ".acl" in m["raw"] or ".acr" in m["raw"]]
    log.summary(
        outcome={
            "subscribe_status": {k: v["status"] for k, v in subs.items()},
            "end_at_minutes": {k: _end_at_minutes(v["channel"], subscribed_at) for k, v in subs.items()},
            "baseline_received": {k: _count(msgs(k), base_mark, revoke_t) > 0 for k in labels},
            "after_revoke_notifications": {k: _count(msgs(k), first_mod_t - 1, mods_end_t) for k in labels},
            "message_types": {k: _types(msgs(k)) for k in labels},
            "acl_change_signal_in_window": bool(signal_msgs),
            "any_message_mentions_acl_or_acr": bool(mentions_acl),
            "reconnect_after_revoke_ok": reconnect_ok,
            "reconnect_after_revoke_receives": reconnect_recv,
            "new_subscription_status_after_revoke": new_subs,
            "webhook_token_webid": sorted({str((m.get("claims") or {}).get("webid")) for m in hooks.messages}),
            "webhook_has_dpop_proof": sorted({m.get("has_dpop") for m in hooks.messages}),
            **expiry,
        },
        metrics={"n_messages_total": len(all_msgs)},
    )


def run_unsub(log, config, variant, rep) -> None:
    s = scene.build(log, config)
    actor_name = variant.split("-", 1)[1]
    actor = {"bob": s.bob, "alice": s.alice}.get(actor_name) or Agent.of(config, "anonymous")
    sub = subscribe(log, s.appr, "ws", s.person, "ws-person")
    channel = sub["channel"]
    ws = WSListener(log, "ws-person", channel["receiveFrom"])
    ws.start()
    ws.connected.wait(10)
    t = modify(log, s.alice, s.person, "before-unsub")["t_ms"]
    time.sleep(SETTLE_S)
    before_ok = _count(ws.messages, t) > 0

    discovery = {}
    if actor_name == "alice":
        # Can alice find appR's channel without being told its id?
        probes = {
            "storage_description": f"{s.alice.pod_url}.well-known/solid",
            "subscription_endpoint": endpoint(config, "ws"),
            "notifications_root": f"{base_url(config)}.notifications/",
        }
        for name, url in probes.items():
            r = s.alice.get(url)
            listed = channel["id"] in r.text
            log.write("alice_discovery", probe=name, response=response_record(r, body=True), lists_channel_id=listed)
            discovery[name] = [r.status_code, listed]
        r = s.alice.delete(endpoint(config, "ws"))
        log.write("alice_delete_without_id", response=response_record(r, body=True))
        discovery["delete_subscription_endpoint"] = r.status_code
        t = modify(log, s.alice, s.person, "after-delete-without-id")["t_ms"]
        time.sleep(SETTLE_S)
        discovery["channel_alive_after_delete_without_id"] = _count(ws.messages, t) > 0
        log.write("channel_id_handed_to_alice", note="alice is given appR's channel id out of band for the next step")

    r = actor.delete(channel["id"])
    log.write("unsubscribe", actor=actor.name, channel_id=channel["id"], response=response_record(r, body=True))
    t = modify(log, s.alice, s.person, "after-unsub")["t_ms"]
    time.sleep(SETTLE_S)
    after = _count(ws.messages, t)
    closed_by_server = ws.closed_by == "server"
    ws.close()
    log.summary(
        outcome={
            "subscribe_status": sub["status"],
            "received_before_unsub": before_ok,
            "unsubscribe_actor": actor.name,
            "unsubscribe_status": r.status_code,
            "received_after_unsub": after > 0,
            "ws_closed_by_server": closed_by_server,
            **({"alice_discovery": discovery} if discovery else {}),
        },
        metrics={"messages_after_unsub": after},
    )


def run_one(log, config, variant, rep, rng) -> None:
    if variant.startswith("unsub-"):
        run_unsub(log, config, variant, rep)
    else:
        run_lifecycle(log, config, variant, rep)


def _expiry(mode: str, config: str) -> None:
    subprocess.run(["bash", str(CH3 / "start.sh"), "--expiry", mode, config], check=True)


if __name__ == "__main__":
    raise SystemExit(harness.main(
        "p3", run_one,
        before_variant=lambda c, v: _expiry("short", c) if v == "short" else None,
        after_variant=lambda c, v: _expiry("default", c) if v == "short" else None,
    ))
