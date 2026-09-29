"""P7 withdrawal notice: on revoke, alice POSTs a JSON-LD notice (ODRL + DPV)
to each recipient's LDN inbox; recipient handlers purge their P5 aggregator
rows and P6 memory chunks. What does alice see, and can she tell a
cooperating recipient from a non-cooperating one? (HYPOTHESES.md, P7)

The notice mechanism, the handlers and the purge are a prototype written for
this experiment, not a Solid or CSS feature. No acknowledgement mechanism is
added: the run only records whether one exists.

The ``-consent`` variants send notice v2, which adds a DPV consent status
(``dpv:hasConsentStatus dpv:ConsentWithdrawn``; HYPOTHESES.md, P7 notice v2).
It is declared only: the handlers act on ``odrl:target`` alone.

    npm run exp:p7 [-- --config wac|acp] [--variant cooperating|non-cooperating|cooperating-consent|non-cooperating-consent] [--reps N] [--dry-run]
"""

from __future__ import annotations

import json
import re
import threading
import time
import uuid
from datetime import datetime, timezone

import rdflib

from ch3.lib import access, harness, scene
from ch3.lib.agents import Agent, response_record
from ch3.lib.aggregator import Aggregator
from ch3.lib.env import CH3, STATE, base_url
from ch3.lib.memory import Memory, verify_models
from ch3.lib.notify import endpoint, subscribe

POLL_S, WAIT_AFTER_S, K = 1.0, 5.0, 4
LDP = rdflib.Namespace("http://www.w3.org/ns/ldp#")
LDP_INBOX = "http://www.w3.org/ns/ldp#inbox"
DPV = rdflib.Namespace("https://w3id.org/dpv#")
QUESTIONS = json.loads((CH3 / "fixtures" / "questions.json").read_text())["questions"]
CONTEXT = {"odrl": "http://www.w3.org/ns/odrl/2/", "dpv": "https://w3id.org/dpv#",
           "ch3n": "https://example.org/ch3/notice#", "xsd": "http://www.w3.org/2001/XMLSchema#"}


# --- item (b): the recipient's inbox, advertised in its WebID profile, Append-only for alice

def setup_inbox(log, recipient: Agent, alice: Agent) -> str:
    inbox = f"{recipient.pod_url}ch3-inbox/"
    head = recipient.request("HEAD", inbox)
    created = None
    if head.status_code == 404:
        created = recipient.put(inbox, "", "text/turtle")
    profile = recipient.web_id.split("#")[0]
    patch = f"""@prefix solid: <http://www.w3.org/ns/solid/terms#>.
@prefix ldp: <http://www.w3.org/ns/ldp#>.
_:inbox a solid:InsertDeletePatch;
    solid:inserts {{ <{recipient.web_id}> ldp:inbox <{inbox}>. }}.
"""
    pr = recipient.patch_n3(profile, patch)
    doc_url, doc_body, ar = access.set_readers(recipient, inbox, [alice.web_id], mode="acl:Append", container=True)
    log.write("inbox_setup", recipient=recipient.name, inbox=inbox, existed=head.status_code != 404,
              create_response=response_record(created) if created is not None else None,
              profile=profile, profile_patch=patch, profile_patch_response=response_record(pr),
              access_doc_url=doc_url, access_doc_body=doc_body, access_doc_response=response_record(ar))
    return inbox


def discover_inbox(log, alice: Agent, recipient: Agent) -> str | None:
    """LDN §3.1: Link rel=inbox header first, then ldp:inbox in the RDF."""
    profile = recipient.web_id.split("#")[0]
    head = alice.request("HEAD", profile)
    links = re.findall(r'<([^>]+)>\s*;\s*rel="([^"]+)"', head.headers.get("Link", ""))
    from_header = next((t for t, rel in links if rel in (LDP_INBOX, "inbox")), None)
    get = alice.get(profile, headers={"accept": "text/turtle"})
    graph = rdflib.Graph().parse(data=get.text, format="turtle", publicID=profile) if get.ok else rdflib.Graph()
    from_rdf = graph.value(rdflib.URIRef(recipient.web_id), LDP.inbox)
    log.write("inbox_discovery", actor="alice", recipient=recipient.name, head=response_record(head),
              inbox_from_link_header=from_header, get_status=get.status_code,
              inbox_from_rdf=str(from_rdf) if from_rdf else None)
    return from_header or (str(from_rdf) if from_rdf else None)


def notice_version(variant: str) -> int:
    return 2 if variant.endswith("-consent") else 1


def notice(alice: Agent, recipient: Agent, target: str, version: int = 1) -> dict:
    body = {
        "@context": CONTEXT,
        "@id": f"urn:uuid:{uuid.uuid4()}",
        "dpv:hasRecipient": {"@id": recipient.web_id},
        "dpv:hasDataSubject": {"@id": target + "#me"},
        "ch3n:sender": {"@id": alice.web_id},
        "ch3n:withdrawnAt": {"@value": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
                             "@type": "xsd:dateTime"},
        "ch3n:withdrawnPermission": {"@type": "odrl:Permission", "odrl:target": {"@id": target},
                                     "odrl:assignee": {"@id": recipient.web_id},
                                     "odrl:action": {"@id": "odrl:read"}},
        "ch3n:requests": {"@id": "ch3n:DeleteCopiesOfTarget"},
    }
    if version == 2:
        body["ch3n:withdrawnConsent"] = {"@type": "dpv:Consent",
                                         "dpv:hasConsentStatus": {"@id": "dpv:ConsentWithdrawn"}}
    return body


def has_consent_withdrawn(body) -> bool:
    """Does the notice, parsed as JSON-LD, state a dpv:Consent with status dpv:ConsentWithdrawn?"""
    graph = rdflib.Graph().parse(data=json.dumps(body), format="json-ld")
    return any((c, rdflib.RDF.type, DPV.Consent) in graph
               for c in graph.subjects(DPV.hasConsentStatus, DPV.ConsentWithdrawn))


# --- the recipient side: stores + an inbox-polling handler

class Recipient:
    def __init__(self, log, agent: Agent, s, cooperating: bool) -> None:
        self.log, self.agent, self.cooperating = log, agent, cooperating
        stores = STATE / "stores"
        stores.mkdir(parents=True, exist_ok=True)
        self.agg = Aggregator(log, stores / f"{log.run_id}-p7-{agent.name}.sqlite", agent,
                              [s.person, s.distractor], "naive")
        self.agg.sync()
        self.memory = Memory(stores / f"{log.run_id}-p7-{agent.name}-memory.sqlite")
        for url in (s.person, s.distractor):
            r = agent.get(url, headers={"accept": "text/turtle"})
            r.raise_for_status()
            self.memory.add(url, r.text)
        self.inbox: str | None = None
        self.seen: set[str] = set()
        self.received: list[dict] = []
        self.purged: list[dict] = []
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._loop, daemon=True)

    def _listing(self) -> set[str]:
        r = self.agent.get(self.inbox, headers={"accept": "text/turtle"})
        graph = rdflib.Graph().parse(data=r.text, format="turtle", publicID=self.inbox)
        return {str(o) for o in graph.objects(rdflib.URIRef(self.inbox), LDP.contains)}

    def start(self, inbox: str) -> None:
        self.inbox = inbox
        self.seen = self._listing()  # notices from earlier reps are not this run's
        self._thread.start()

    def _loop(self) -> None:
        while not self._stop.is_set():
            for item in sorted(self._listing() - self.seen):
                self.seen.add(item)
                r = self.agent.get(item, headers={"accept": "application/ld+json"})
                rec = self.log.write("notice_received", recipient=self.agent.name, item=item,
                                     response=response_record(r, body=True))
                try:
                    body = r.json()
                    body = body[0] if isinstance(body, list) else body
                    target = body["ch3n:withdrawnPermission"]["odrl:target"]["@id"]
                except (ValueError, KeyError, TypeError, IndexError) as exc:
                    self.log.write("notice_unparsed", recipient=self.agent.name, item=item, error=repr(exc))
                    continue
                try:
                    consent_withdrawn = has_consent_withdrawn(r.json())
                except Exception as exc:  # noqa: BLE001 -- recorded, not fatal to the handler
                    self.log.write("notice_jsonld_unparsed", recipient=self.agent.name, item=item, error=repr(exc))
                    consent_withdrawn = False
                self.received.append({"t_ms": rec["t_ms"], "target": target, "consent_withdrawn": consent_withdrawn})
                if self.cooperating:
                    rows, chunks = self.agg.purge(target), self.memory.purge(target)
                    done = self.log.write("purge_done", recipient=self.agent.name, target=target,
                                          rows_deleted=rows, chunks_deleted=chunks)
                    self.purged.append({"t_ms": done["t_ms"], "rows": rows, "chunks": chunks})
                else:
                    self.log.write("purge_skipped", recipient=self.agent.name, target=target,
                                   note="non-cooperating handler: received, not acted on")
            self._stop.wait(POLL_S)

    def stop(self) -> None:
        self._stop.set()
        self._thread.join(timeout=10)

    def residual(self, person: str, distractor: str) -> dict:
        top1 = 0
        for q in QUESTIONS:
            hits = self.memory.retrieve(q["question"], K)
            self.log.write("retrieval_after", recipient=self.agent.name, qid=q["id"], hits=hits)
            top1 += bool(hits) and hits[0]["source"] == person
        return {"rows_person": self.agg.rows(person), "chunks_person": self.memory.count(person),
                "rows_distractor": self.agg.rows(distractor), "chunks_distractor": self.memory.count(distractor),
                "questions_top1_from_revoked": top1}

    def close(self) -> None:
        self.agg.close()
        self.memory.close()


def acl_names(log, alice: Agent, url: str, who: dict[str, str], when: str) -> dict:
    doc = access.acl_link(alice, url)
    r = alice.get(doc, headers={"accept": "text/turtle"})
    names = {name: web_id in r.text for name, web_id in who.items()}
    log.write("access_doc_read", actor="alice", when=when, doc_url=doc, response=response_record(r, body=True),
              names_recipient=names)
    return names


def run_one(log, config, variant, rep, rng) -> None:
    log.write("models", **verify_models())
    cooperating = variant.startswith("cooperating")
    version = notice_version(variant)
    s = scene.build(log, config)
    recipients = {a.name: a for a in (s.appr, s.bob)}

    # item (c) setup: appR holds a notification subscription on person.ttl
    sub = subscribe(log, s.appr, "ws", s.person, "ws-person")
    channel_id = (sub["channel"] or {}).get("id")

    handlers = {name: Recipient(log, agent, s, cooperating) for name, agent in recipients.items()}
    inboxes = {name: setup_inbox(log, agent, s.alice) for name, agent in recipients.items()}
    for name, h in handlers.items():
        h.start(inboxes[name])

    # item (a): where alice's recipient list comes from. `server_exposed=False` here and
    # `recipient_list_from_own_grant_log: True` in the summary are constants this script
    # writes by design, not measurements; the measured support is
    # `access_doc_names_recipients_after` (acl_names below).
    grant_log = sorted(recipients[n].web_id for n in recipients)
    log.write("recipient_list", source="alice's own grant log (the 'grant' lines this run wrote)",
              recipients=grant_log, server_exposed=False,
              note="CSS 7.2.0 offers no endpoint listing past grantees or readers; see access_doc_read")
    who = {n: a.web_id for n, a in recipients.items()}
    acl_before = acl_names(log, s.alice, s.person, who, "before_revoke")
    scene.revoke(log, s, s.person, [])
    acl_after = acl_names(log, s.alice, s.person, who, "after_revoke")

    # item (c): can alice see who holds subscriptions on her resource?
    probes = {"storage_description": f"{s.alice.pod_url}.well-known/solid",
              "subscription_endpoint": endpoint(config, "ws"),
              "notifications_root": f"{base_url(config)}.notifications/"}
    subs_visible = {}
    for name, url in probes.items():
        r = s.alice.get(url)
        seen = bool((channel_id and channel_id in r.text) or s.appr.web_id in r.text)
        log.write("subscription_probe", actor="alice", probe=name, response=response_record(r, body=True),
                  shows_appr_or_channel=seen)
        subs_visible[name] = seen

    sent = {}
    for name, agent in recipients.items():
        inbox = discover_inbox(log, s.alice, agent)
        body = notice(s.alice, agent, s.person, version)
        r = s.alice.post(inbox, json.dumps(body), "application/ld+json")
        rec = log.write("notice_sent", actor="alice", recipient=name, inbox=inbox, notice_version=version, notice=body,
                        response=response_record(r, body=True))
        sent[name] = {"t_ms": rec["t_ms"], "inbox": inbox, "discovered": inbox == inboxes[name], "response": r}
    time.sleep(WAIT_AFTER_S)
    for h in handlers.values():
        h.stop()

    # what alice can see, per recipient
    alice_view = {}
    for name, info in sent.items():
        r = info["response"]
        location = r.headers.get("Location")
        loc_status = s.alice.get(location).status_code if location else None
        inbox_status = s.alice.get(info["inbox"]).status_code
        view = {"post_status": r.status_code, "post_has_location": bool(location),
                "post_header_names": sorted(k.lower() for k in r.headers
                                            if k.lower() not in {"date", "location", "content-length",
                                                                 "keep-alive", "connection"}),
                "post_body_empty": not r.text, "get_location_status": loc_status, "get_inbox_status": inbox_status}
        log.write("alice_view", recipient=name, **view)
        alice_view[name] = view

    per = {}
    metrics = {}
    for name, h in handlers.items():
        res = h.residual(s.person, s.distractor)
        per[name] = {"discovered_inbox": sent[name]["discovered"], "received": bool(h.received),
                     "purged": bool(h.purged), **res}
        if version == 2:  # v1 outcomes stay exactly as recorded in the earlier runs
            per[name]["notice_has_consent_status"] = bool(h.received) and all(
                x["consent_withdrawn"] for x in h.received)
        t0 = sent[name]["t_ms"]
        metrics[f"{name}_sent_to_received_ms"] = round(h.received[0]["t_ms"] - t0, 1) if h.received else None
        metrics[f"{name}_sent_to_purged_ms"] = round(h.purged[0]["t_ms"] - t0, 1) if h.purged else None
        log.write("recipient_result", recipient=name, **per[name])
        h.close()

    log.summary(
        outcome={
            "recipient_list_from_own_grant_log": True,
            "access_doc_names_recipients_before": acl_before,
            "access_doc_names_recipients_after": acl_after,
            "alice_sees_subscriptions": subs_visible,
            "recipients": per,
            "alice_view": alice_view,
        },
        metrics=metrics,
    )


if __name__ == "__main__":
    raise SystemExit(harness.main("p7", run_one))
