# 01 — Share and revoke: what does withdrawal actually reach?

## Goal

Alice grants Bob read access via WAC, Bob reads, Alice revokes. The interesting
part is not whether revocation works on the original resource — it is what
revocation **cannot reach**.

Three questions, in increasing order of legal weight:

1. Does revocation take effect immediately, or does Bob's already-issued access
   token keep working until it expires? (Bob's token is valid for 3600 s.)
2. Bob saved a copy while he was authorised. Does revocation affect it?
3. If Bob's copy sits **in Bob's own pod**, can Alice reach it at all?

Question 3 is the one that matters. A copy on Bob's laptop is simply data
out of reach. A copy in Bob's pod is data held by an identified party, inside
the same protocol, on the same server — and if Alice still cannot touch it, then
Solid's architecture places the recipient, not the data subject, in control of
the copy.

## Hypotheses (written and committed before the run)

| # | Check | Expected | If it holds, that means |
|---|---|---|---|
| 1 | Alice writes the resource | `201` | Setup — **ENFORCED** |
| 2 | Alice writes an ACL granting Bob `acl:Read` | `2xx` | Owner holds `acl:Control` — **ENFORCED** |
| 3 | Bob reads the shared resource | `200` | The grant works — **ENFORCED** |
| 4 | `WAC-Allow` advertises Bob's granted mode | `read` | Advertisement matches the grant — **ENFORCED** |
| 5 | Bob saves a copy to local disk | `True` | Nothing prevents it — **NOT-SUPPORTED** (no mechanism exists to prevent copying) |
| 6 | Bob writes a copy into **his own pod** | `201` | Bob may store what he lawfully read — **NOT-SUPPORTED** (no onward-control mechanism) |
| 7 | Alice revokes by rewriting the ACL to owner-only | `2xx` | Revocation is expressible — **ENFORCED** |
| 8 | Bob re-reads with his **existing, unexpired token** | `403` | Revocation is immediate; ACLs are evaluated per request, not baked into tokens — **ENFORCED** |
| 9 | Bob re-reads with a **freshly issued** token | `403` | Same, via a different path — **ENFORCED** |
| 10 | `WAC-Allow` after revocation no longer advertises read for Bob | `` (empty) | Advertisement tracks revocation — **ENFORCED** |
| 11 | Bob's **local** copy is still readable | `True` | Revocation cannot reach it — **NOT-SUPPORTED** |
| 12 | Bob reads his own copy **in his pod** | `200` | The copy is unaffected — **NOT-SUPPORTED** |
| 13 | Alice tries to **read** Bob's copy in Bob's pod | `403` | Alice has no rights over the copy — **NOT-SUPPORTED** |
| 14 | Alice tries to **delete** Bob's copy in Bob's pod | `403` | Alice has no erasure mechanism — **NOT-SUPPORTED** |

### On the `NOT-SUPPORTED` rows

These are not failures of CSS, and nothing here is a bug. WAC governs *access to
a resource at a URL*. It has no concept of a copy, of onward transfer, or of an
obligation travelling with data. Rows 5, 6, 11–14 record the absence of a
mechanism, which is exactly the kind of gap this thesis is looking for.

## Steps

1. Alice creates the resource and an ACL granting Bob `acl:Read`.
2. Bob reads it, saves it to local disk, and writes a copy into his own pod.
3. Alice rewrites the ACL to owner-only.
4. Bob retries **without refreshing his token**, then again with a fresh one.
5. Alice attempts to read and then delete Bob's copy inside Bob's pod.
6. Everything created is deleted, so the experiment re-runs cleanly.

## Bears on (open questions, not conclusions)

- **GDPR Art. 7(3)** — withdrawal of consent must be as easy as giving it, and
  takes effect for the future. Observed: withdrawal is immediate *on the
  original resource*. Whether withdrawal that leaves lawful copies untouched
  satisfies the provision's purpose is a legal question, not a technical one.
- **GDPR Art. 17** — erasure. Observed: Alice has no protocol mechanism to erase
  a copy held in another user's pod on the same server.
- **GDPR Art. 4(7)** — *does Bob become a controller of Alice's personal data
  once the copy sits in his pod, determining the purposes and means of its
  processing?* Posed here as an **open question**. This experiment establishes
  only the technical fact that the copy is under Bob's exclusive control; it
  does not and cannot answer the legal characterisation.

Regulation (EU) 2016/679, OJ L 119, 4.5.2016, p. 1 —
https://eur-lex.europa.eu/eli/reg/2016/679/oj

## Spec references

- **WAC** §4.1 Access Objects, §4.2 Access Modes, §4.3 Access Subjects,
  §5.1 Effective ACL Resource, §6.1 `wac-allow` —
  https://solidproject.org/TR/wac (v1.0.0, 2024-05-12)
- **Solid Protocol** §4.3.1 Auxiliary Resources / Web Access Control —
  https://solidproject.org/TR/protocol (v0.11.0, 2024-05-12)

## Result

_Not yet run._
