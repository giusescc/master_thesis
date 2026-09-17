"""02_odrl_consent -- is an ODRL/DPV consent policy enforced, or only declared?

See README.md for the hypotheses, committed before this ran, and
RELATED_WORK.md for the scope of the claim.
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))
sys.path.insert(0, str(HERE))

from policy_client import evaluate_read  # noqa: E402

from solidlib import lab  # noqa: E402
from solidlib.checks import CheckTable, Status  # noqa: E402
from solidlib.meta import meta_url, put_preserving_meta, read_meta  # noqa: E402
from solidlib.report import finish  # noqa: E402
from solidlib.resources import put_turtle  # noqa: E402
from solidlib.wac import owner_plus_reader, write_acl  # noqa: E402

CONTENT = """@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>.
<#dataset> rdfs:label "Alice's research dataset (synthetic test data)" .
"""
CONTENT_UPDATED = """@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>.
<#dataset> rdfs:label "Alice's research dataset (synthetic test data, revised)" .
"""

SCIENTIFIC_RESEARCH = "https://w3id.org/dpv#ScientificResearch"
DIRECT_MARKETING = "https://w3id.org/dpv#DirectMarketing"

PREFIXES = (
    "@prefix odrl: <http://www.w3.org/ns/odrl/2/>. "
    "@prefix dpv: <https://w3id.org/dpv#>. "
)


def permission_triples(meta: str, resource: str, alice: str, bob: str) -> str:
    """The ODRL Agreement in its permissive form (ODRL 2.2 s.2.6.1)."""
    return (
        f"<{meta}#agreement> a odrl:Agreement ; "
        f"odrl:assigner <{alice}> ; odrl:assignee <{bob}> ; "
        f"odrl:permission <{meta}#read-permission> . "
        f"<{meta}#read-permission> odrl:target <{resource}> ; "
        f"odrl:action odrl:read ; odrl:constraint <{meta}#purpose-constraint> . "
        f"<{meta}#purpose-constraint> odrl:leftOperand odrl:purpose ; "
        f"odrl:operator odrl:eq ; odrl:rightOperand dpv:ScientificResearch . "
        f"<{meta}#agreement> odrl:prohibition <{meta}#no-redistribution> . "
        f"<{meta}#no-redistribution> odrl:target <{resource}> ; "
        f"odrl:action odrl:distribute . "
    )


def prohibition_triples(meta: str, resource: str) -> str:
    """The exact contradiction: a Prohibition on the very same read."""
    return (
        f"<{meta}#agreement> odrl:prohibition <{meta}#read-prohibition> . "
        f"<{meta}#read-prohibition> odrl:target <{resource}> ; "
        f"odrl:action odrl:read . "
    )


def patch(session, target_meta: str, *, inserts: str = "", deletes: str = ""):
    """Send an N3 Patch (Solid Protocol s.5.3.1) to a description resource."""
    body = ["@prefix solid: <http://www.w3.org/ns/solid/terms#>. ", PREFIXES,
            "<> a solid:InsertDeletePatch"]
    if deletes:
        body.append(f"; solid:deletes {{ {deletes} }}")
    if inserts:
        body.append(f"; solid:inserts {{ {inserts} }}")
    body.append(".")
    return session.patch_n3(target_meta, "\n".join(body))


def main() -> int:
    evidence = lab.evidence_for(HERE, "02_odrl_consent")
    alice = lab.session("ALICE", evidence, name="Alice")
    bob = lab.session("BOB", evidence, name="Bob")

    resource = f"{alice.pod_url}research-dataset.ttl"
    table = CheckTable("02_odrl_consent -- enforced, or only declared?")

    # -- Setup: the resource, and a WAC rule that really does grant Bob read.
    # The ODRL policy is therefore the ONLY thing that could restrict him
    # further. If he reads anyway, the policy is doing nothing.
    put_turtle(alice, resource, CONTENT)
    write_acl(alice, resource, owner_plus_reader(resource, alice.web_id, bob.web_id))

    # -- 1. The spec's designated metadata slot ---------------------------
    meta = meta_url(alice, resource)
    table.check(
        "Resource advertises a describedby description resource",
        expected=True,
        actual=meta is not None,
        on_match=Status.ENFORCED,
        note=f"Solid Protocol s.4.3.2; discovered at {meta}",
    )
    assert meta is not None

    # -- 2-3. Attach the ODRL/DPV policy ----------------------------------
    response = patch(alice, meta, inserts=permission_triples(meta, resource, alice.web_id, bob.web_id))
    table.check(
        "ODRL policy written to the description resource (N3 PATCH)",
        expected=True,
        actual=response.ok,
        on_match=Status.ENFORCED,
        note=f"HTTP {response.status_code}",
    )

    status, policy_doc = read_meta(alice, resource)
    table.check(
        "Policy reads back with its purpose constraint intact",
        expected=True,
        actual=("ScientificResearch" in policy_doc and "purpose" in policy_doc),
        on_match=Status.ENFORCED,
        note=f"GET {meta} -> HTTP {status}",
    )

    # -- 4. Description resources are PATCH-only --------------------------
    response = alice.put(meta, b"", "text/turtle", note="PUT to a description resource")
    table.check(
        "PUT to the description resource is refused",
        expected=True,
        actual=400 <= response.status_code < 500,
        on_match=Status.ENFORCED,
        note=f"HTTP {response.status_code}; they always exist and cannot be replaced",
    )

    # -- 5. Bob reads under the Permission --------------------------------
    response = bob.get(resource, note="Bob reads while an ODRL Permission is in force")
    permitted_status = response.status_code
    table.check(
        "Bob reads while an ODRL Permission is in force",
        expected=200,
        actual=permitted_status,
        on_match=Status.ENFORCED,
        advertised=response.headers.get("WAC-Allow"),
        note="Allowed by WAC, not by ODRL",
    )

    # -- 6-7. THE FLIP: replace the Permission with its exact contradiction
    response = patch(
        alice, meta,
        deletes=(
            f"<{meta}#agreement> odrl:permission <{meta}#read-permission> . "
            f"<{meta}#read-permission> odrl:action odrl:read . "
        ),
        inserts=prohibition_triples(meta, resource),
    )
    table.check(
        "Policy flipped from Permission to Prohibition",
        expected=True,
        actual=response.ok,
        on_match=Status.ENFORCED,
        note=f"HTTP {response.status_code}",
    )

    response = bob.get(resource, note="Bob reads while an ODRL PROHIBITION forbids it")
    prohibited_status = response.status_code
    table.check(
        "Bob reads while an ODRL Prohibition forbids it",
        expected=200,
        actual=prohibited_status,
        on_match=Status.DECLARED_ONLY,
        advertised=response.headers.get("WAC-Allow"),
        note=f"Identical to the permitted case ({permitted_status}): the policy changed nothing",
    )

    # -- 8. Redistribution, despite odrl:Prohibition on distribute --------
    redistributed = f"{bob.pod_url}redistributed-dataset.ttl"
    response = put_turtle(
        bob, redistributed, response.text,
        note="Bob redistributes despite odrl:Prohibition on odrl:distribute",
    )
    table.check(
        "Bob redistributes despite the prohibition on distribution",
        expected=201,
        actual=response.status_code,
        on_match=Status.DECLARED_ONLY,
        note="No duty travels with the data once it has been read",
    )

    # -- 9-10. Voluntary client-side enforcement vs a non-cooperating one --
    _, current_policy = read_meta(bob, resource)
    decision = evaluate_read(
        current_policy, base=meta, assignee=bob.web_id,
        target=resource, purpose=SCIENTIFIC_RESEARCH,
    )
    table.check(
        "A policy-aware client refuses the read voluntarily",
        expected=False,
        actual=decision.allowed,
        on_match=Status.DECLARED_ONLY,
        note=f"Client-side only: {decision.reason}",
    )

    response = bob.get(resource, note="A non-cooperating client makes the same request")
    table.check(
        "A non-cooperating client performing the same read succeeds",
        expected=200,
        actual=response.status_code,
        on_match=Status.DECLARED_ONLY,
        note="The voluntary control is bypassed simply by not implementing it",
    )

    # -- 11-12. Declaring a purpose on the request ------------------------
    # There is no standard header for this, because there is no purpose channel.
    # We invent one to demonstrate that the server has nowhere to put it.
    response = bob.get(
        resource,
        headers={"Purpose": DIRECT_MARKETING},
        note="Bob declares a DPV purpose that CONTRADICTS the policy constraint",
    )
    table.check(
        "Bob declares a contradicting DPV purpose; server accepts the request",
        expected=200,
        actual=response.status_code,
        on_match=Status.NOT_SUPPORTED,
        advertised=response.headers.get("WAC-Allow"),
        note="No standard header exists; the purpose is neither required nor checked",
    )

    _, after_purpose = read_meta(alice, resource)
    table.check(
        "The declared purpose is recorded anywhere server-side",
        expected=False,
        actual=(DIRECT_MARKETING in after_purpose),
        on_match=Status.NOT_SUPPORTED,
        note="Nothing records it: there is no purpose channel to record into",
    )

    # -- 13. Does an ordinary data update destroy the consent policy? -----
    put_turtle(alice, resource, CONTENT_UPDATED, note="Alice makes an ORDINARY data update")
    _, after_update = read_meta(alice, resource)
    table.check(
        "The policy survives an ordinary PUT to the resource",
        expected=False,
        actual=("ScientificResearch" in after_update),
        on_match=Status.NOT_SUPPORTED,
        note="CSS resets the description resource on PUT unless asked not to",
    )

    # -- 14. ... and with the voluntary preserve header? ------------------
    patch(alice, meta, inserts=permission_triples(meta, resource, alice.web_id, bob.web_id))
    put_preserving_meta(alice, resource, CONTENT.encode(), "text/turtle")
    _, after_preserve = read_meta(alice, resource)
    table.check(
        'The policy survives a PUT sent with Link rel="preserve"',
        expected=True,
        actual=("ScientificResearch" in after_preserve),
        on_match=Status.DECLARED_ONLY,
        note="Durability exists, but only if the writing client opts in",
    )

    # -- Cleanup ----------------------------------------------------------
    alice.delete(resource, note="cleanup")
    bob.delete(redistributed, note="cleanup")

    summary = f"""
The ODRL policy is inert. That is the result, and the experiment is built so
that the claim can be checked rather than taken on trust.

Bob read the resource while an `odrl:Permission` was in force and received
`{permitted_status}`. The policy was then replaced with its exact contradiction —
an `odrl:Prohibition` on the very same read by the very same assignee — and Bob
received `{prohibited_status}`. The two responses are identical. Nothing about the
access decision consulted the policy, so flipping the policy from "may" to
"must not" changed nothing at all. The prohibition on redistribution fared no
better: Bob copied the data into his own pod without resistance.

This is not a shortcoming of the policy's placement. It was attached to the
resource's **description resource**, the slot the Solid Protocol itself
designates for metadata about a resource (§4.3.2), discovered through the
server's own `describedby` link and written with the N3 Patch mechanism the
server advertises in `Accept-Patch`. The server stored it faithfully and served
it back intact. It simply never reads it when deciding access — the Community
Solid Server builds its authorization context from the target IRI, the agent's
WebID, the client ID and the issuer, and nothing else.

The policy-aware client shows what enforcement would have to look like in the
absence of server support, and in doing so shows why that is not enforcement.
Our client read the prohibition and declined to make the request. A client that
simply does not implement this — including `curl`, and including our own
ordinary session object — performed exactly the same read and got `200`.
Compliance is therefore voluntary, evaluated by the party it constrains, and
invisible to the data subject: nothing in the protocol lets Alice tell a
compliant reader from a non-compliant one.

Purpose has nowhere to live. Bob declared a DPV purpose on his request that
directly contradicted the policy's constraint, using an invented header, because
no standard header exists. The server accepted the request, ignored the header,
and recorded the declared purpose nowhere. There is no purpose channel to
record into. (This claim is scoped to CSS + WAC + Solid-OIDC — see
RELATED_WORK.md, which distinguishes ecosystem approaches that genuinely enforce
purpose from those that merely record it.)

The most practically alarming result is the last one. Because the policy lives
in the description resource, and because CSS resets a description resource
whenever the subject resource is written, **an ordinary data update silently
destroyed the consent policy**. The access rule in the `.acl` was untouched, so
Bob's access continued exactly as before — only the record of the agreed terms
vanished, with no warning to anyone. The policy survives only if the writing
client volunteers a `Link: rel="preserve"` header, which is once again a
protection that depends entirely on client goodwill.
"""

    print("\n" + evidence.summary())
    return finish(HERE, table, summary)


if __name__ == "__main__":
    raise SystemExit(main())
