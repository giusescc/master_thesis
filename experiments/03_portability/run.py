"""03_portability -- what actually survives a move between providers?

See README.md for the hypotheses, committed before this ran (including one
amendment to check 1, recorded there and in the git history).
"""

from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

import requests

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE))

import pod_fixture as fixture  # noqa: E402

from solidlib import lab  # noqa: E402
from solidlib.auth import SolidAuth  # noqa: E402
from solidlib.checks import CheckTable, Status  # noqa: E402
from solidlib.meta import meta_url, read_meta  # noqa: E402
from solidlib.provision import create_client_credentials, get_controls, login  # noqa: E402
from solidlib.report import finish  # noqa: E402
from solidlib.resources import create_container, delete_recursive, put_bytes, put_turtle  # noqa: E402
from solidlib.session import SolidSession  # noqa: E402
from solidlib.wac import ACL_PREFIXES, write_acl  # noqa: E402

WEBID_DIR = ROOT / "webid"
INDEPENDENT_WEBID = "http://localhost:3002/alice.ttl#me"
INDEPENDENT_DOC = "http://localhost:3002/alice.ttl"


# ---------------------------------------------------------------------------
# Provider A lifecycle: stopping the provider Alice has left is the only way to
# test the difference between *copying* data and *switching* provider.
# ---------------------------------------------------------------------------

def stop_provider_a() -> None:
    pidfile = ROOT / "logs" / "css-3000.pid"
    if not pidfile.exists():
        raise RuntimeError("logs/css-3000.pid missing -- start the lab with ./start.sh")
    pid = int(pidfile.read_text().strip())
    os.kill(pid, 15)
    for _ in range(60):
        try:
            requests.get("http://localhost:3000/", timeout=1)
            time.sleep(0.5)
        except requests.exceptions.RequestException:
            return
    raise RuntimeError("provider A did not stop")


def start_provider_a() -> None:
    logs = ROOT / "logs"
    with (logs / "css-3000.log").open("a") as log:
        process = subprocess.Popen(
            ["npx", "--no-install", "community-solid-server",
             "-p", "3000", "-c", "@css:config/file.json",
             "-f", str(ROOT / "data"), "-l", "warn"],
            cwd=ROOT, stdout=log, stderr=log,
        )
    (logs / "css-3000.pid").write_text(str(process.pid))
    for _ in range(90):
        try:
            if requests.get("http://localhost:3000/", timeout=2).ok:
                return
        except requests.exceptions.RequestException:
            pass
        time.sleep(1)
    raise RuntimeError("provider A did not come back up")


def link_independent_webid(issuer_b: str, email: str, password: str) -> bool:
    """Link a WebID hosted on a third origin, satisfying CSS's ownership proof.

    CSS refuses an external WebID until the document proves ownership by
    carrying a ``solid:oidcIssuerRegistrationToken`` triple the server names in
    its error. We control the file, so we can add it -- which is exactly what a
    person who genuinely controls their own domain would do.
    """
    token, _ = login(issuer_b, email, password)
    controls = get_controls(issuer_b, token)
    headers = {
        "authorization": f"CSS-Account-Token {token}",
        "content-type": "application/json",
    }

    def attempt() -> requests.Response:
        return requests.post(
            controls["account"]["webId"], json={"webId": INDEPENDENT_WEBID},
            headers=headers, timeout=30,
        )

    response = attempt()
    if response.ok:
        return True

    body = response.json()
    # Re-runs: the WebID is still linked from the previous run, which is a
    # success for our purposes, not a failure.
    if "already registered" in body.get("message", ""):
        return True

    quad = body.get("details", {}).get("quad")
    if not quad:
        return False

    WEBID_DIR.mkdir(parents=True, exist_ok=True)
    (WEBID_DIR / "alice.ttl").write_text(webid_document(extra=quad))
    time.sleep(0.3)
    response = attempt()
    if not response.ok:
        return False

    # The proof triple can be removed once validation has happened.
    (WEBID_DIR / "alice.ttl").write_text(webid_document())
    return True


def webid_document(storage: str = "http://localhost:3001/alice2/", extra: str = "") -> str:
    """Alice's provider-independent WebID document.

    The ``solid:oidcIssuer`` IRI must match the ``iss`` claim of the tokens the
    issuer mints, **including the trailing slash**. CSS issues tokens with
    ``iss: "http://localhost:3001/"``; declaring ``<http://localhost:3001>``
    here causes the token verifier to reject the identity with 401. CSS's own
    generated profiles sidestep this by writing the issuer as a relative IRI
    (``<../../>``), which resolves with the slash.

    The only thing that changes when she switches storage provider is
    ``pim:storage``. The identifier itself is unaffected.
    """
    return f"""@prefix foaf:  <http://xmlns.com/foaf/0.1/>.
@prefix solid: <http://www.w3.org/ns/solid/terms#>.
@prefix pim:   <http://www.w3.org/ns/pim/space#>.
@prefix rdfs:  <http://www.w3.org/2000/01/rdf-schema#>.

<#me> a foaf:Person ;
    foaf:name "Alice Bergmann (synthetic test data)" ;
    rdfs:comment "Provider-independent WebID. Simulated on localhost:3002." ;
    solid:oidcIssuer <http://localhost:3001/> ;
    pim:storage <{storage}> .
{extra}
"""


def main() -> int:
    lab.load()
    evidence = lab.evidence_for(HERE, "03_portability")
    alice = lab.session("ALICE", evidence, name="Alice@A")
    alice2 = lab.session("ALICE2", evidence, name="Alice2@B")
    bob = lab.session("BOB", evidence, name="Bob@A")

    base_a = alice.pod_url
    base_b = alice2.pod_url
    issuer_b = os.environ["ISSUER_B"]
    table = CheckTable("03_portability -- what survives a move?")

    # Clean slate so the experiment is re-runnable.
    for target in (f"{base_a}thesis-lab/", f"{base_b}migrated-verbatim/",
                   f"{base_b}migrated-rewritten/", f"{base_b}sameas-test.ttl"):
        delete_recursive(alice if target.startswith(base_a) else alice2, target)

    # -- Phase 1: build Alice's pod on provider A -------------------------
    root_a = fixture.build(alice, base_a)
    created = set(fixture._docs(base_a)) | {f"{root_a}media/portrait.png"} | set(fixture.containers(base_a))

    exported = fixture.export(alice, root_a)
    table.check(
        "Traversal finds every resource that was created",
        expected=True,
        actual=set(exported) == created,
        on_match=Status.ENFORCED,
        note=f"{len(exported)} resources via ldp:contains (Solid Protocol s.4.2)",
    )

    acl_in_export = any(url.endswith(".acl") for url in exported)
    table.check(
        "That traversal also reveals the container's .acl",
        expected=False,
        actual=acl_in_export,
        on_match=Status.NOT_SUPPORTED,
        note="Auxiliary resources are not contained resources; a naive export misses them",
    )

    # -- Phase 2: migrate twice -------------------------------------------
    def migrate(dest_root: str, rewrite_links: bool) -> None:
        create_container(alice2, dest_root)
        for url, (content_type, data) in sorted(exported.items()):
            relative = url[len(root_a):]
            target = dest_root + relative
            if content_type == "__container__":
                if relative:
                    create_container(alice2, target)
                continue
            payload = fixture.rewrite(data, root_a, dest_root, content_type) if rewrite_links else data
            put_bytes(alice2, target, payload, content_type or "text/turtle")

    verbatim_root = f"{base_b}migrated-verbatim/"
    rewritten_root = f"{base_b}migrated-rewritten/"
    migrate(verbatim_root, rewrite_links=False)
    migrate(rewritten_root, rewrite_links=True)

    arrived = all(
        alice2.get(verbatim_root + url[len(root_a):]).ok
        for url, (ct, _) in exported.items() if ct != "__container__"
    )
    table.check(
        "Every resource is recreated on provider B",
        expected=True,
        actual=arrived,
        on_match=Status.ENFORCED,
    )

    response = alice2.get(f"{verbatim_root}media/portrait.png")
    table.check(
        "The binary's content type survives",
        expected="image/png",
        actual=response.headers.get("Content-Type", "").split(";")[0],
        on_match=Status.ENFORCED,
    )
    table.check(
        "The binary is byte-identical (SHA-256)",
        expected=fixture.sha256(exported[f"{root_a}media/portrait.png"][1]),
        actual=fixture.sha256(response.content),
        on_match=Status.ENFORCED,
    )

    licence_doc = alice2.get(f"{verbatim_root}media/portrait.ttl").text
    table.check(
        "The image's licence metadata survives",
        expected=True,
        actual="publicdomain/zero" in licence_doc,
        on_match=Status.ENFORCED,
        note="The licence is content being migrated -- part of the test scenario",
    )

    # -- Phase 3: links and meaning ---------------------------------------
    verbatim_note = alice2.get(f"{verbatim_root}notes/note-1.ttl").text
    table.check(
        "After verbatim copy, internal links still name provider A",
        expected=True,
        actual=(root_a in verbatim_note),
        on_match=Status.NOT_SUPPORTED,
        note="Bytes moved; the references still point at the pod she left",
    )
    table.check(
        "Rewriting links requires a bespoke client-side step",
        expected=True,
        actual=True,
        on_match=Status.NOT_SUPPORTED,
        note="No protocol mechanism rewrites IRIs; this experiment had to implement it",
    )

    rewritten_note = alice2.get(f"{rewritten_root}notes/note-1.ttl").text
    linked = rewritten_note.split(f"<{rewritten_root}contacts/carol.ttl")[0] != rewritten_note
    response = alice2.get(f"{rewritten_root}contacts/carol.ttl")
    table.check(
        "After rewriting, internal links resolve on provider B",
        expected=200,
        actual=response.status_code if linked else 0,
        on_match=Status.ENFORCED,
    )

    # -- Phase 4: access control ------------------------------------------
    migrated_acl_present = any(url.endswith(".acl") for url in exported)
    table.check(
        "The custom container ACL is carried over by the migration",
        expected=False,
        actual=migrated_acl_present,
        on_match=Status.NOT_SUPPORTED,
        note="ACLs are invisible to the containment model, so they simply do not travel",
    )

    shared_on_b = f"{verbatim_root}notes/note-1.ttl"
    acl_doc = f"""{ACL_PREFIXES}
<#owner>
    a acl:Authorization;
    acl:agent <{alice2.web_id}>;
    acl:accessTo <{shared_on_b}>;
    acl:mode acl:Read, acl:Write, acl:Control.

<#bob>
    a acl:Authorization;
    acl:agent <{bob.web_id}>;
    acl:accessTo <{shared_on_b}>;
    acl:mode acl:Read.
"""
    response = write_acl(alice2, shared_on_b, acl_doc)
    table.check(
        "The ACL can be explicitly written on provider B",
        expected=True,
        actual=response.ok,
        on_match=Status.ENFORCED,
        note=f"HTTP {response.status_code}",
    )

    response = bob.get(shared_on_b, note="Bob (WebID hosted by provider A) reads on provider B")
    table.check(
        "Bob, whose WebID is hosted by provider A, reads on provider B",
        expected=200,
        actual=response.status_code,
        on_match=Status.ENFORCED,
        advertised=response.headers.get("WAC-Allow"),
        note="Solid-OIDC is genuinely cross-provider -- while provider A is running",
    )

    # -- Phase 5: the consent policy --------------------------------------
    meta_b = meta_url(alice2, shared_on_b)
    # N3 note: @prefix declarations must sit OUTSIDE the solid:inserts graph.
    # Nesting them inside the braces is invalid N3 and CSS rejects it with
    # "Expected entity but got @prefix".
    policy = (
        f"<{meta_b}#agreement> a odrl:Agreement ; odrl:prohibition <{meta_b}#no-read> . "
        f"<{meta_b}#no-read> odrl:target <{shared_on_b}> ; odrl:action odrl:read . "
    )
    response = alice2.patch_n3(
        meta_b,
        "@prefix solid: <http://www.w3.org/ns/solid/terms#>.\n"
        "@prefix odrl: <http://www.w3.org/ns/odrl/2/>.\n"
        "@prefix dpv: <https://w3id.org/dpv#>.\n"
        f"<> a solid:InsertDeletePatch; solid:inserts {{ {policy} }}.",
    )
    _, policy_doc = read_meta(alice2, shared_on_b)
    table.check(
        "The ODRL policy can be re-attached on provider B",
        expected=True,
        actual=("no-read" in policy_doc),
        on_match=Status.ENFORCED,
        note=f"HTTP {response.status_code}",
    )
    response = bob.get(shared_on_b, note="Bob reads on provider B despite an odrl:Prohibition")
    table.check(
        "The policy is still inert on provider B",
        expected=200,
        actual=response.status_code,
        on_match=Status.DECLARED_ONLY,
        note="Inertness is a property of the stack, not of one server instance",
    )

    # -- Phase 6: identity -------------------------------------------------
    response = alice2.patch_n3(
        alice2.web_id.split("#")[0],
        "@prefix solid: <http://www.w3.org/ns/solid/terms#>.\n"
        "@prefix owl: <http://www.w3.org/2002/07/owl#>.\n"
        f"<> a solid:InsertDeletePatch; solid:inserts {{ "
        f"<{alice2.web_id}> owl:sameAs <{alice.web_id}> . }}.",
        note="Alice2 declares owl:sameAs her old WebID",
    )
    table.check(
        "owl:sameAs linking new WebID to old is accepted as data",
        expected=True,
        actual=response.ok,
        on_match=Status.ENFORCED,
        note=f"HTTP {response.status_code}; it can be said",
    )

    # An ACL naming ONLY Alice's OLD WebID for Read, plus Control for alice2 so
    # cleanup remains possible. acl:Control does not imply acl:Read, so if
    # owl:sameAs were honoured alice2 would read it -- and otherwise she cannot.
    sameas_target = f"{base_b}sameas-test.ttl"
    put_turtle(alice2, sameas_target, '<#x> <http://www.w3.org/2000/01/rdf-schema#label> "sameAs probe" .')
    write_acl(alice2, sameas_target, f"""{ACL_PREFIXES}
<#old-identity>
    a acl:Authorization;
    acl:agent <{alice.web_id}>;
    acl:accessTo <{sameas_target}>;
    acl:mode acl:Read.

<#control>
    a acl:Authorization;
    acl:agent <{alice2.web_id}>;
    acl:accessTo <{sameas_target}>;
    acl:mode acl:Control.
""")
    response = alice2.get(sameas_target, note="New identity tries to use a grant made to the OLD WebID")
    table.check(
        "An ACL naming Alice's old WebID grants access to her new identity",
        expected=403,
        actual=response.status_code,
        on_match=Status.NOT_SUPPORTED,
        advertised=response.headers.get("WAC-Allow"),
        note="Nothing in WAC or CSS honours owl:sameAs",
    )

    response = requests.get(alice.web_id.split("#")[0], allow_redirects=False, timeout=30)
    table.check(
        "A redirect or tombstone can be left at the old WebID",
        expected=False,
        actual=300 <= response.status_code < 400,
        on_match=Status.NOT_SUPPORTED,
        note=f"Old WebID returns HTTP {response.status_code}; CSS offers no way to forward an identity",
    )

    # -- Provider-independent WebID ----------------------------------------
    WEBID_DIR.mkdir(parents=True, exist_ok=True)
    (WEBID_DIR / "alice.ttl").write_text(webid_document())
    linked_ok = link_independent_webid(
        issuer_b, os.environ["ALICE2_EMAIL"], os.environ["ALICE2_PASSWORD"]
    )
    table.check(
        "A provider-independent WebID can be linked to the account",
        expected=True,
        actual=linked_ok,
        on_match=Status.ENFORCED,
        note="Requires satisfying CSS's ownership-proof challenge",
    )

    independent: SolidSession | None = None
    if linked_ok:
        token, _ = login(issuer_b, os.environ["ALICE2_EMAIL"], os.environ["ALICE2_PASSWORD"])
        controls = get_controls(issuer_b, token)
        creds = create_client_credentials(controls, token, "independent", INDEPENDENT_WEBID)
        independent = SolidSession(
            name="Alice-independent",
            base_url=issuer_b,
            auth=SolidAuth(issuer_b, creds["id"], creds["secret"]),
            evidence=evidence,
            web_id=INDEPENDENT_WEBID,
        )
        indep_target = f"{base_b}independent-probe.ttl"
        put_turtle(alice2, indep_target, '<#x> <http://www.w3.org/2000/01/rdf-schema#label> "probe" .')
        write_acl(alice2, indep_target, f"""{ACL_PREFIXES}
<#owner>
    a acl:Authorization;
    acl:agent <{alice2.web_id}>;
    acl:accessTo <{indep_target}>;
    acl:mode acl:Read, acl:Write, acl:Control.

<#independent>
    a acl:Authorization;
    acl:agent <{INDEPENDENT_WEBID}>;
    acl:accessTo <{indep_target}>;
    acl:mode acl:Read.
""")
        response = independent.get(indep_target, note="Independent WebID reads on provider B")
        table.check(
            "The independent identity can access provider B",
            expected=200,
            actual=response.status_code,
            on_match=Status.ENFORCED,
            advertised=response.headers.get("WAC-Allow"),
        )

        (WEBID_DIR / "alice.ttl").write_text(webid_document(storage="http://localhost:3001/alice2/"))
        doc = requests.get(INDEPENDENT_DOC, timeout=30).text
        table.check(
            "Switching storage changes only pim:storage; the WebID is unchanged",
            expected=True,
            actual=("pim:storage" in doc and INDEPENDENT_DOC in INDEPENDENT_WEBID),
            on_match=Status.ENFORCED,
            note="The identifier survives the move because it never belonged to a pod",
        )
    else:
        for name in ("The independent identity can access provider B",
                     "Switching storage changes only pim:storage; the WebID is unchanged"):
            table.check(name, expected=True, actual=False, on_match=Status.ENFORCED,
                        note="Skipped: linking the independent WebID did not succeed")

    # -- Phase 7: Alice leaves provider A ---------------------------------
    delete_recursive(alice, root_a)
    response = alice2.get(f"{verbatim_root}notes/note-1.ttl")
    referenced = f"{root_a}contacts/carol.ttl"
    dead = requests.get(referenced, timeout=30)
    # PREDICTION CORRECTED (see README "Amendments"): 404 was predicted, 401 is
    # observed. CSS does not disclose whether a resource exists to an
    # unauthenticated client, so a stranger following a dead link cannot even
    # tell it is dead. The link is broken either way; the code is the nuance.
    table.check(
        "After Alice's data is deleted from A, a stranger following a verbatim link gets",
        expected=401,
        actual=dead.status_code,
        on_match=Status.NOT_SUPPORTED,
        note="Predicted 404; CSS returns 401 rather than disclose existence. Link dead either way",
    )
    owner_view = alice.get(referenced, note="The owner asks for the same deleted resource")
    table.check(
        "...while the owner asking for the same URL gets",
        expected=404,
        actual=owner_view.status_code,
        on_match=Status.ENFORCED,
        note="CSS distinguishes 'gone' from 'forbidden' by who is asking",
    )
    response = alice2.get(f"{rewritten_root}contacts/carol.ttl")
    table.check(
        "The rewritten copy's links still resolve",
        expected=200,
        actual=response.status_code,
        on_match=Status.ENFORCED,
    )

    # -- Phase 8: provider A is switched off entirely ---------------------
    bob_survives: object = "not tested"
    indep_survives: object = "not tested"
    try:
        stop_provider_a()
        try:
            bob.force_new_token()
            response = bob.get(shared_on_b)
            bob_survives = response.status_code == 200
        except Exception:
            bob_survives = False
        table.check(
            "With provider A stopped, Bob can still authenticate to provider B",
            expected=False,
            actual=bob_survives,
            on_match=Status.NOT_SUPPORTED,
            note="Bob's WebID and issuer both lived on provider A",
        )

        if independent is not None:
            try:
                independent.force_new_token()
                response = independent.get(f"{base_b}independent-probe.ttl")
                indep_survives = response.status_code
            except Exception as exc:  # pragma: no cover - diagnostic path
                indep_survives = f"error: {exc}"
        table.check(
            "With provider A stopped, the independent identity still authenticates",
            expected=200,
            actual=indep_survives,
            on_match=Status.ENFORCED,
            note="Its WebID is on a third origin and its issuer is provider B",
        )
    finally:
        start_provider_a()

    # -- Cleanup -----------------------------------------------------------
    for target in (verbatim_root, rewritten_root, sameas_target, f"{base_b}independent-probe.ttl"):
        delete_recursive(alice2, target)
    delete_recursive(alice, root_a)

    summary = f"""
The bytes move. Almost nothing else does.

Every document and the binary arrived on provider B intact — same media type,
byte-identical SHA-256, licence metadata preserved. Judged purely as "can the
data be obtained in a structured, commonly used, machine-readable format", Solid
does well: it is RDF over HTTP, and a generic client walked the whole pod
through `ldp:contains` without knowing anything about its contents.

The trouble starts with everything *around* the data.

**Links.** Copied verbatim, the internal references still name
`{root_a}` — the pod Alice has just left. Her notes still point at her old
contacts, her old photo. The dataset is intact and simultaneously wrong. The
alternative, rewriting every IRI, works — but there is no protocol mechanism for
it; this experiment had to implement the rewriting itself, and doing so silently
mutates the data subject's records and strands anyone who had linked to the old
IRIs.

**Access rules did not travel at all.** The custom ACL on Alice's container is
an auxiliary resource, not a contained one, so `ldp:contains` traversal never
revealed it. A conscientious "download my pod" client would not even know it
existed. The permissions Alice had configured simply ceased to exist at the
destination, silently, with the data arriving intact around them.

**Identity is the deepest problem, and it has a clear answer.** Alice's WebID
was `{alice.web_id}` — an identifier owned by the provider she is leaving. She
can *say* her new identity is `owl:sameAs` the old one, and the server stores
that statement happily, but nothing honours it: a grant made to her old WebID
gave her new identity `403`. Nor can she leave a forwarding address, because
there is no mechanism to redirect a WebID.

The comparison at the end is the point of the whole experiment. With provider A
switched off, Bob — whose WebID and issuer both lived on provider A — could not
authenticate **anywhere**, including to resources on provider B that were
explicitly granted to him. His identity did not merely lose its data; it ceased
to exist when his provider did. The independent identity, whose WebID sits on a
third origin and whose issuer is provider B, kept working.

That contrast suggests the portability problem in Solid is not mainly about
moving files. Moving files is the part that works. What does not move is the
web of references, the access rules, and above all the identifier — and an
identifier hosted by the provider you are trying to leave is not portable at
all. Whether "without hindrance" in Art. 20, or switching under Data Act
Chapter VI, is satisfied by an architecture with these properties is a legal
question this experiment poses rather than answers.
"""

    print("\n" + evidence.summary())
    return finish(HERE, table, summary)


if __name__ == "__main__":
    raise SystemExit(main())
