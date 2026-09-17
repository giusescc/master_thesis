"""00_hello_pod -- is Web Access Control actually enforced?

See README.md for the hypotheses, which were committed before this ran.
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from solidlib import lab  # noqa: E402
from solidlib.checks import CheckTable, Status  # noqa: E402
from solidlib.report import finish  # noqa: E402
from solidlib.resources import put_turtle  # noqa: E402

CONTENT = """@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>.
<#note> rdfs:label "Alice's private note (synthetic test data)" .
"""


def main() -> int:
    evidence = lab.evidence_for(HERE, "00_hello_pod")
    alice = lab.session("ALICE", evidence, name="Alice")
    bob = lab.session("BOB", evidence, name="Bob")
    anon = lab.anonymous("ALICE", evidence)

    target = f"{alice.pod_url}private-note.ttl"
    table = CheckTable("00_hello_pod -- is WAC enforced?")

    # -- Alice writes, then reads back -----------------------------------
    response = put_turtle(alice, target, CONTENT)
    table.check(
        "Alice writes a new private resource",
        expected=201,
        actual=response.status_code,
        on_match=Status.ENFORCED,
        note="Owner holds acl:Write on her own pod (WAC s.4.2)",
    )

    response = alice.get(target)
    advertised = response.headers.get("WAC-Allow")
    table.check(
        "Alice reads it back",
        expected=200,
        actual=response.status_code,
        on_match=Status.ENFORCED,
        advertised=advertised,
    )
    table.check(
        "Bytes read match bytes written",
        expected=True,
        actual=CONTENT.strip() in response.text,
        on_match=Status.ENFORCED,
    )

    modes = " ".join(sorted(
        (advertised or "").split('user="')[-1].split('"')[0].split()
    ))
    table.check(
        "WAC-Allow advertises Alice's own modes",
        expected="append control read write",
        actual=modes,
        on_match=Status.ENFORCED,
        advertised=advertised,
        note="The server advertising the permissions it will apply (WAC s.6.1)",
    )

    # -- Bob, authenticated but not authorised ---------------------------
    response = bob.get(target)
    table.check(
        "Bob (authenticated, not granted) reads Alice's resource",
        expected=403,
        actual=response.status_code,
        on_match=Status.ENFORCED,
        advertised=response.headers.get("WAC-Allow"),
        note="Authentication is not authorisation",
    )

    # -- Anonymous --------------------------------------------------------
    response = anon.get(target)
    table.check(
        "Anonymous client reads Alice's resource",
        expected=401,
        actual=response.status_code,
        on_match=Status.ENFORCED,
        advertised=response.headers.get("WAC-Allow"),
    )

    # -- The default pod ACL's public grant on the root container --------
    response = anon.get(alice.pod_url)
    root_advertised = response.headers.get("WAC-Allow")
    table.check(
        "Anonymous client reads Alice's pod ROOT container",
        expected=200,
        actual=response.status_code,
        on_match=Status.ENFORCED,
        advertised=root_advertised,
        note="CSS default pod template grants acl:Read to acl:agentClass foaf:Agent",
    )
    public_modes = " ".join(sorted(
        (root_advertised or "").split('public="')[-1].split('"')[0].split()
    ))
    table.check(
        "WAC-Allow advertises the public read on the root",
        expected="read",
        actual=public_modes,
        on_match=Status.ENFORCED,
        advertised=root_advertised,
    )

    # -- Cleanup, so the experiment can be re-run -------------------------
    response = alice.delete(target)
    table.check(
        "Alice deletes her own resource",
        expected=True,
        actual=response.ok,
        on_match=Status.ENFORCED,
        note=f"HTTP {response.status_code}; also makes the run repeatable",
    )

    summary = """
Web Access Control is genuinely enforced by the Community Solid Server. Alice
could read and write her own resource; Bob, who is a fully authenticated Solid
user with valid credentials, was refused with `403`; an unauthenticated client
was refused with `401`. The distinction between the two codes is meaningful:
`401` invites the client to authenticate, `403` tells an already-identified
agent that identity is not the problem.

The server also *advertises* its decisions through the `WAC-Allow` header, and
the advertisement matched the enforcement in every case. That is worth stating
explicitly, because later experiments show statements that do **not** match
behaviour — and it is the contrast that matters.

One result deserves attention beyond the access-control question. A
freshly-created pod is not private by default: CSS's pod template grants
`acl:Read` to `acl:agentClass foaf:Agent` on the pod's root container, so any
anonymous client on the network can list what a new pod contains. The grant
carries no `acl:default`, so it does not cascade to the resources inside — the
contents stay private, only the listing is exposed. Whether a data subject
creating a pod would anticipate that is a question for the legal analysis
rather than one this experiment can answer.
"""

    print("\n" + evidence.summary())
    return finish(HERE, table, summary)


if __name__ == "__main__":
    raise SystemExit(main())
