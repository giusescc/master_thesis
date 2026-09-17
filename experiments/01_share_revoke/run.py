"""01_share_revoke -- what does withdrawal actually reach?

See README.md for the hypotheses, committed before this ran.
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
from solidlib.wac import owner_only, owner_plus_reader, parse_wac_allow, write_acl  # noqa: E402

CONTENT = """@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>.
<#record> rdfs:label "Alice's shared health note (synthetic test data)" ;
          rdfs:comment "Shared with Bob for the purposes of this experiment." .
"""

LOCAL_COPY_DIR = HERE / "bob_local_copy"


def main() -> int:
    evidence = lab.evidence_for(HERE, "01_share_revoke")
    alice = lab.session("ALICE", evidence, name="Alice")
    bob = lab.session("BOB", evidence, name="Bob")

    shared = f"{alice.pod_url}shared-note.ttl"
    bobs_copy = f"{bob.pod_url}copy-of-alices-note.ttl"
    table = CheckTable("01_share_revoke -- what does revocation reach?")

    # -- 1-2. Alice creates the resource and grants Bob read --------------
    response = put_turtle(alice, shared, CONTENT)
    table.check("Alice writes the resource", 201, response.status_code, Status.ENFORCED)

    response = write_acl(alice, shared, owner_plus_reader(shared, alice.web_id, bob.web_id))
    table.check(
        "Alice writes an ACL granting Bob acl:Read",
        expected=True,
        actual=response.ok,
        on_match=Status.ENFORCED,
        note=f"HTTP {response.status_code}; requires acl:Control (WAC s.4.2)",
    )

    # -- 3-4. Bob reads -----------------------------------------------------
    response = bob.get(shared, note="Bob reads while the grant is in force")
    granted_advert = response.headers.get("WAC-Allow")
    table.check(
        "Bob reads the shared resource",
        200,
        response.status_code,
        Status.ENFORCED,
        advertised=granted_advert,
    )
    bob_modes = " ".join(sorted(parse_wac_allow(granted_advert).get("user", set())))
    table.check(
        "WAC-Allow advertises Bob's granted mode",
        expected="read",
        actual=bob_modes,
        on_match=Status.ENFORCED,
        advertised=granted_advert,
    )
    read_body = response.text

    # -- 5. Bob saves a copy to local disk ---------------------------------
    LOCAL_COPY_DIR.mkdir(parents=True, exist_ok=True)
    local_file = LOCAL_COPY_DIR / "alices-note.ttl"
    local_file.write_text(read_body)
    table.check(
        "Bob saves a copy to local disk",
        expected=True,
        actual=local_file.exists(),
        on_match=Status.NOT_SUPPORTED,
        note="No mechanism in Solid or WAC can prevent a reader from copying",
    )

    # -- 6. Bob writes a copy into his OWN pod ------------------------------
    response = put_turtle(bob, bobs_copy, read_body, note="Bob copies into his own pod")
    table.check(
        "Bob writes a copy into his own pod",
        201,
        response.status_code,
        Status.NOT_SUPPORTED,
        note="Nothing ties an obligation to the data once it is read",
    )

    # -- 7. Alice revokes ---------------------------------------------------
    response = write_acl(alice, shared, owner_only(shared, alice.web_id))
    table.check(
        "Alice revokes by rewriting the ACL to owner-only",
        expected=True,
        actual=response.ok,
        on_match=Status.ENFORCED,
        note=f"HTTP {response.status_code}",
    )

    # -- 8. Bob retries with his EXISTING, unexpired token ------------------
    # Deliberately no refresh: this is the question of whether revocation is
    # immediate or only takes effect when the token expires (Bob's is valid for
    # 3600 s). GDPR Art. 7(3) is about withdrawal taking effect, not eventually.
    assert bob.has_cached_token(), "Bob should still be holding his original token"
    response = bob.get(shared, note="Bob retries with his ORIGINAL unexpired token")
    revoked_advert = response.headers.get("WAC-Allow")
    table.check(
        "Bob re-reads with his existing, unexpired token",
        403,
        response.status_code,
        Status.ENFORCED,
        advertised=revoked_advert,
        note="ACLs are evaluated per request; permissions are not baked into the token",
    )

    # -- 9. And with a freshly issued token --------------------------------
    bob.force_new_token()
    response = bob.get(shared, note="Bob retries with a freshly issued token")
    table.check(
        "Bob re-reads with a freshly issued token",
        403,
        response.status_code,
        Status.ENFORCED,
        advertised=response.headers.get("WAC-Allow"),
    )

    # -- 10. The advertisement tracks the revocation ------------------------
    table.check(
        "WAC-Allow no longer advertises read for Bob",
        expected="",
        actual=" ".join(sorted(parse_wac_allow(revoked_advert).get("user", set()))),
        on_match=Status.ENFORCED,
        advertised=revoked_advert or "(absent)",
    )

    # -- 11-12. But the copies are untouched --------------------------------
    table.check(
        "Bob's local copy is still readable after revocation",
        expected=True,
        actual=local_file.read_text() == read_body,
        on_match=Status.NOT_SUPPORTED,
        note="Revocation has no reach outside the server",
    )

    response = bob.get(bobs_copy, note="Bob reads his own copy after revocation")
    table.check(
        "Bob reads his own copy in his pod after revocation",
        200,
        response.status_code,
        Status.NOT_SUPPORTED,
        advertised=response.headers.get("WAC-Allow"),
    )

    # -- 13-14. Alice cannot reach the copy in Bob's pod --------------------
    response = alice.get(bobs_copy, note="Alice attempts to READ Bob's copy")
    table.check(
        "Alice tries to read Bob's copy in Bob's pod",
        403,
        response.status_code,
        Status.NOT_SUPPORTED,
        advertised=response.headers.get("WAC-Allow"),
        note="Same server, same protocol, her data -- no access",
    )

    response = alice.delete(bobs_copy, note="Alice attempts to DELETE Bob's copy")
    table.check(
        "Alice tries to delete Bob's copy in Bob's pod",
        403,
        response.status_code,
        Status.NOT_SUPPORTED,
        note="No protocol-level erasure mechanism reaches a recipient's pod",
    )

    # -- Cleanup ------------------------------------------------------------
    alice.delete(shared, note="cleanup")
    bob.delete(bobs_copy, note="cleanup")
    if local_file.exists():
        local_file.unlink()
    if LOCAL_COPY_DIR.exists():
        LOCAL_COPY_DIR.rmdir()

    summary = """
Revocation works, and it works immediately — but only on the original resource.

The immediacy is worth stating precisely, because it is a point where Solid
behaves better than one might assume. Bob's access token was valid for a full
hour and he still held it. Rewriting the ACL cut him off on his very next
request, with no token refresh involved, because the Community Solid Server
evaluates access control *per request* rather than encoding permissions into the
token at issue time. Withdrawal is therefore effective at once, not at the next
token expiry.

Everything else in this experiment is about the limits of that guarantee. While
authorised, Bob read the resource — and at that moment the data left the reach
of access control entirely. His copy on local disk was untouched by revocation,
which is unsurprising. The copy **inside his own pod** is the significant one: it
sits on the same server, under the same protocol, governed by the same access
control system, and Alice can neither read it (`403`) nor delete it (`403`).
Bob's pod is Bob's, and WAC works exactly as designed in refusing her.

The gap this exposes is not a defect in the Community Solid Server or in WAC.
Web Access Control governs access to a resource at a URL. It has no vocabulary
for a copy, no notion of onward transfer, and no way to attach an obligation
that travels with data. Once a read succeeds, the protocol's job is finished.

For the legal chapter, the technical facts are these: withdrawal is immediate
and effective prospectively on the original; it has no effect whatsoever on
copies already made; and the data subject has no protocol mechanism to reach a
copy held by a recipient, even a recipient on the same server. Whether Bob
thereby becomes a controller determining the purposes and means of processing
under Art. 4(7), and what Art. 17 erasure could mean in this architecture, are
questions this experiment poses rather than answers.
"""

    print("\n" + evidence.summary())
    return finish(HERE, table, summary)


if __name__ == "__main__":
    raise SystemExit(main())
