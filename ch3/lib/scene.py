"""The per-run scene every phase starts from.

Each repetition gets a fresh container in alice's pod, ``/alice/ch3/<run-id>/``,
so no state leaks between runs:

* ``person.ttl``     the fixture; appR and bob get Read ("grant"), and appR
                     later loses it ("revoke").
* ``distractor.ttl`` similar facts about another fictional person; appR and bob
                     keep Read throughout.
* the container itself: appR and bob get Read on the container only (so they
  can list it and subscribe to it), not inherited by its members.

Every write is logged to the run's JSONL, including the access-control
documents' full text.
"""

from __future__ import annotations

from dataclasses import dataclass

from ch3.lib import access
from ch3.lib.agents import Agent, response_record
from ch3.lib.env import CH3
from ch3.lib.jsonl import RunLog

FIXTURES = CH3 / "fixtures"


@dataclass
class Scene:
    config: str
    container: str
    person: str
    distractor: str
    alice: Agent
    appr: Agent
    bob: Agent


def build(log: RunLog, config: str, readers: tuple[str, ...] = ("appr", "bob")) -> Scene:
    alice, appr, bob = Agent.of(config, "alice"), Agent.of(config, "appr"), Agent.of(config, "bob")
    for agent in (alice, appr, bob):
        agent.token_now()
    container = f"{alice.pod_url}ch3/{log.run_id}/"
    scene = Scene(config, container, container + "person.ttl", container + "distractor.ttl", alice, appr, bob)
    reader_ids = [a.web_id for a in (appr, bob) if a.name in readers]

    for name, url in (("person.ttl", scene.person), ("distractor.ttl", scene.distractor)):
        r = alice.put(url, (FIXTURES / name).read_text(), "text/turtle")
        log.write("fixture_written", actor="alice", resource=url, response=response_record(r))
    target, body, r = access.set_readers(alice, container, reader_ids, container=True)
    log.write("grant", actor="alice", resource=container, agents=reader_ids, doc_url=target,
              doc_body=body, response=response_record(r))
    for url in (scene.distractor, scene.person):
        target, body, r = access.set_readers(alice, url, reader_ids)
        log.write("grant", actor="alice", resource=url, agents=reader_ids, doc_url=target,
                  doc_body=body, response=response_record(r))
    log.write("scene_ready", container=container, person=scene.person, distractor=scene.distractor,
              authz=config.upper(), alice=alice.web_id, appr=appr.web_id, bob=bob.web_id)
    return scene


def revoke(log: RunLog, scene: Scene, url: str, remaining: list[str]) -> dict:
    """alice rewrites ``url``'s access document so only ``remaining`` may read.

    The revoke time is logged twice: when the request was sent and when its
    response arrived. Time-to-denial is measured from the latter (the moment
    the revoke write had succeeded, as seen by alice).
    """
    sent = log.write("revoke_sent", actor="alice", resource=url, remaining=remaining)
    target, body, r = access.set_readers(scene.alice, url, remaining)
    done = log.write("revoke_done", actor="alice", resource=url, remaining=remaining, doc_url=target,
                     doc_body=body, response=response_record(r))
    return {"sent": sent, "done": done}
