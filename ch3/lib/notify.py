"""Solid Notifications client pieces for P3 (and P7's subscription check).

* ``subscribe``      POST a subscription request to a CSS subscription service
* ``WSListener``     connect to a WebSocketChannel2023 ``receiveFrom`` and log
                     every message verbatim, on its own thread
* ``WebhookReceiver`` a local HTTP server (127.0.0.1 only) that logs every
                     WebhookChannel2023 POST CSS makes to it

Every message is logged with its arrival time and full payload.
"""

from __future__ import annotations

import base64
import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from websockets.exceptions import ConnectionClosed
from websockets.sync.client import connect

from ch3.lib.agents import Agent, redact, response_record
from ch3.lib.env import base_url
from ch3.lib.jsonl import RunLog

NS = "http://www.w3.org/ns/solid/notifications#"
TYPES = {"ws": "WebSocketChannel2023", "webhook": "WebhookChannel2023"}


def endpoint(config: str, kind: str) -> str:
    return f"{base_url(config)}.notifications/{TYPES[kind]}/"


def subscribe(log: RunLog, agent: Agent, kind: str, topic: str, label: str,
              send_to: str | None = None) -> dict:
    body = {"@context": ["https://www.w3.org/ns/solid/notification/v1"],
            "type": NS + TYPES[kind], "topic": topic}
    if send_to:
        body["sendTo"] = send_to
    r = agent.post(endpoint(agent.config, kind), json.dumps(body), "application/ld+json")
    try:
        parsed = r.json()
    except ValueError:
        parsed = None
    rec = response_record(r, body=True)
    log.write("subscribe", agent=agent.name, kind=kind, label=label, topic=topic, request=body,
              response=rec, channel=parsed)
    return {"status": r.status_code, "channel": parsed if r.ok else None}


def jwt_claims(authorization: str | None) -> dict | None:
    """Decode (not verify) the payload of ``DPoP <jwt>``; the signature is never logged."""
    if not authorization or " " not in authorization:
        return None
    token = authorization.split(" ", 1)[1]
    try:
        payload = token.split(".")[1]
        return json.loads(base64.urlsafe_b64decode(payload + "=" * (-len(payload) % 4)))
    except (IndexError, ValueError):
        return {"undecodable": True}


class WSListener(threading.Thread):
    def __init__(self, log: RunLog, label: str, url: str) -> None:
        super().__init__(daemon=True)
        self.log, self.label, self.url = log, label, url
        self.messages: list[dict] = []
        self.connected = threading.Event()
        self.connect_error: str | None = None
        self.closed_by: str | None = None
        self.close_code: int | None = None
        self._ws = None

    def run(self) -> None:
        try:
            self._ws = connect(self.url, open_timeout=10)
        except Exception as exc:  # noqa: BLE001 -- a refused connection is an observation
            self.connect_error = repr(exc)
            self.log.write("ws_connect", label=self.label, url=self.url, ok=False, error=repr(exc))
            self.connected.set()
            return
        self.log.write("ws_connect", label=self.label, url=self.url, ok=True)
        self.connected.set()
        try:
            for raw in self._ws:
                try:
                    payload = json.loads(raw)
                except (TypeError, ValueError):
                    payload = None
                rec = {"label": self.label, "t_ms": self.log.t_ms(), "raw": raw, "payload": payload}
                self.messages.append(rec)
                self.log.write("ws_message", label=self.label, raw=raw, payload=payload)
            if self.closed_by is None:
                self.closed_by = "server"
        except ConnectionClosed as exc:
            if self.closed_by is None:
                self.closed_by = "server"
            self.close_code = exc.rcvd.code if exc.rcvd else None
        self.log.write("ws_closed", label=self.label, closed_by=self.closed_by,
                       code=self.close_code if self.close_code is not None else
                       (self._ws.close_code if self._ws else None))

    def close(self) -> None:
        self.closed_by = self.closed_by or "client"
        if self._ws is not None:
            self._ws.close()
        self.join(timeout=5)


class WebhookReceiver:
    """Receives WebhookChannel2023 POSTs at ``/hook/<label>`` on 127.0.0.1."""

    def __init__(self, log: RunLog) -> None:
        self.log = log
        self.messages: list[dict] = []
        receiver = self

        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):  # noqa: N802
                length = int(self.headers.get("content-length", 0))
                raw = self.rfile.read(length).decode("utf-8", "replace")
                try:
                    payload = json.loads(raw)
                except ValueError:
                    payload = None
                label = self.path.rsplit("/", 1)[-1]
                claims = jwt_claims(self.headers.get("authorization"))
                rec = {"label": label, "t_ms": receiver.log.t_ms(), "raw": raw, "payload": payload,
                       "claims": claims, "has_dpop": bool(self.headers.get("dpop"))}
                receiver.messages.append(rec)
                receiver.log.write("webhook_message", label=label, path=self.path, raw=raw, payload=payload,
                                   headers=redact(self.headers), token_claims=claims,
                                   dpop_proof_claims=jwt_claims("x " + self.headers.get("dpop", "")))
                self.send_response(200)
                self.end_headers()

            def log_message(self, *args):  # silence stderr
                pass

        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.port = self.server.server_address[1]
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def url(self, label: str) -> str:
        return f"http://127.0.0.1:{self.port}/hook/{label}"

    def close(self) -> None:
        self.server.shutdown()
        self.server.server_close()


def modify(log: RunLog, alice: Agent, url: str, k: int | str) -> dict:
    """alice inserts one triple into ``url`` (N3 Patch; @prefix outside the braces)."""
    body = f"""@prefix solid: <http://www.w3.org/ns/solid/terms#>.
@prefix ex: <https://example.org/ch3/mod#>.
_:patch a solid:InsertDeletePatch;
    solid:inserts {{ <#me> ex:modification "{k}". }}.
"""
    r = alice.patch_n3(url, body)
    return log.write("modify", actor="alice", resource=url, k=k, response=response_record(r))
