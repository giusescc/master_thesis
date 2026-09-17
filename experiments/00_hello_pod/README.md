# 00 — Hello Pod: is Web Access Control actually enforced?

## Goal

Establish the baseline the rest of the thesis rests on. Before asking whether
Solid enforces *consent* or *portability*, we need to know whether it enforces
the thing it actually claims to: access control.

Alice writes a resource to her pod and reads it back. Bob — a real,
authenticated Solid user who simply has not been granted anything — tries to
read it. An unauthenticated client tries too. We record what the server
**enforces** (status codes) alongside what it **advertises** (`WAC-Allow`).

This experiment is deliberately unsurprising. Its value is that every later
claim about something *not* being enforced can be contrasted with a case that
demonstrably *is*.

## Hypotheses (written and committed before the run)

Recorded in advance so that a wrong prediction shows up as `UNEXPECTED` rather
than being quietly reclassified after the fact.

| # | Check | Expected | If it holds, that means |
|---|---|---|---|
| 1 | Alice writes a new private resource | `201` | Owner has `acl:Write` — **ENFORCED** |
| 2 | Alice reads it back | `200` | Owner has `acl:Read` — **ENFORCED** |
| 3 | The bytes Alice read match what she wrote | `True` | Storage is faithful — **ENFORCED** |
| 4 | `WAC-Allow` on Alice's read advertises her own modes | `append control read write` | Server advertises permissions — **ENFORCED** |
| 5 | Bob reads Alice's private resource | `403` | Authenticated ≠ authorised — **ENFORCED** |
| 6 | Anonymous client reads Alice's private resource | `401` | Unauthenticated is refused — **ENFORCED** |
| 7 | Anonymous client reads Alice's **pod root container** | `200` | The default pod ACL makes the root container world-readable — **ENFORCED** (and a privacy default worth noting) |
| 8 | `WAC-Allow` on the anonymous root read advertises public read | `read` | The server openly advertises the public grant — **ENFORCED** |
| 9 | Alice deletes her own resource | `True` (2xx) | Owner may remove her own data — **ENFORCED** |

### Why 7 and 8 are in here

They are not padding. CSS's default pod template (`templates/pod/wac/.acl.hbs`)
contains:

```turtle
<#public>
    a acl:Authorization;
    acl:agentClass foaf:Agent;
    acl:accessTo <./>;
    acl:mode acl:Read.
```

`acl:agentClass foaf:Agent` means *everyone, including unauthenticated clients*
(WAC §4.3). Because there is no `acl:default`, the grant does **not** cascade to
contained resources — but the container listing itself is public on a
brand-new pod. Whether a data subject creating a pod would expect that is a
question worth putting to the legal analysis.

## Steps

1. Alice `PUT`s a Turtle resource into her pod.
2. Alice `GET`s it and compares the bytes.
3. Bob `GET`s the same URL with his own valid credentials.
4. An unauthenticated client `GET`s it.
5. The unauthenticated client `GET`s Alice's pod root container.
6. Alice deletes the resource (cleanup, so the experiment is re-runnable).

Every exchange is written to `evidence/transcript.md` and
`evidence/transcript.jsonl` with `Authorization` and `DPoP` headers redacted.

## Spec references

- **Solid Protocol** §10 Authentication, §11.1 Web Access Control —
  https://solidproject.org/TR/protocol (v0.11.0, 2024-05-12)
- **WAC** §4.2 Access Modes, §4.3 Access Subjects, §5.1 Effective ACL Resource,
  §6.1 `wac-allow` header — https://solidproject.org/TR/wac (v1.0.0, 2024-05-12)
- **Solid-OIDC** §9.3 DPoP-bound token use — https://solidproject.org/TR/oidc
- **RFC 9449** (DPoP) §4.2, §7.1 — https://www.rfc-editor.org/rfc/rfc9449.html

## Result

<!-- filled in by the run; see RESULTS.md for the cross-experiment table -->
_Not yet run._
