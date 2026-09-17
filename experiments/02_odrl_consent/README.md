# 02 — ODRL + DPV consent: enforced, or only declared?

## Goal

Alongside the WAC rule that actually governs access, attach a machine-readable
consent policy in **ODRL 2.2** using **DPV** terms:

> Bob may **read** this resource **for the purpose of scientific research**, and
> **may not redistribute** it.

Then find out what the server does with it. The answer is expected to be
"nothing", so the experiment is designed to make that answer *falsifiable and
visible* rather than merely asserted:

1. **The prohibition flip.** Attach a `Permission`, observe Bob's read. Replace
   it with a `Prohibition` — the strongest possible contradiction — and observe
   Bob's read again. If the two are identical, the policy provably has no
   effect on the access decision.
2. **The voluntary client.** A small policy-aware client reads the policy and
   refuses on its own. This shows compliance is achievable, but only *if the
   client chooses* — and that any non-cooperating client walks straight through.
3. **The missing purpose channel.** Bob declares a purpose on the request. There
   is no standard header for this, because there is no purpose channel at all.
4. **Policy durability.** An ordinary data update is performed. Does the consent
   policy survive it?

Where the policy lives matters. It is attached to the resource's
**description resource** (Solid Protocol §4.3.2) — the slot the specification
itself designates for metadata *about* a resource, discovered via
`Link: rel="describedby"`. Using the spec's own designated slot makes the
strongest version of the finding: not "we put a policy somewhere odd and the
server ignored it", but "we used the mechanism the specification provides, and
it still changed nothing".

**Scope of the claim.** This experiment tests **CSS + WAC + Solid-OIDC**. Other
parts of the Solid ecosystem *do* carry purpose, and one research prototype
genuinely enforces it. See [`RELATED_WORK.md`](RELATED_WORK.md), which
distinguishes approaches that **enforce** purpose from those that only
**record** it. Nothing here should be read as "Solid cannot express purpose".

## Hypotheses (written and committed before the run)

| # | Check | Expected | If it holds, that means |
|---|---|---|---|
| 1 | The resource advertises a `describedby` description resource | `True` | The spec's metadata slot exists — **ENFORCED** |
| 2 | The ODRL policy can be written to it (N3 PATCH) | `2xx` | The mechanism works — **ENFORCED** |
| 3 | The policy reads back with its purpose constraint intact | `True` | Storage is faithful — **ENFORCED** |
| 4 | `PUT` to the description resource is refused | `4xx` | Description resources are PATCH-only by design — **ENFORCED** |
| 5 | Bob reads while an ODRL **Permission** is in force | `200` | WAC allows it — **ENFORCED** (by WAC, not by ODRL) |
| 6 | Policy flipped to **Prohibition**, written successfully | `2xx` | Setup — **ENFORCED** |
| 7 | **Bob reads while an ODRL `Prohibition` forbids it** | `200` | **The policy has no effect whatsoever — DECLARED-ONLY** |
| 8 | Bob redistributes despite `odrl:Prohibition` on distribution | `201` | No duty travels with the data — **DECLARED-ONLY** |
| 9 | A policy-aware client refuses the read voluntarily | `True` | Compliance is possible but **client-side and optional** — **DECLARED-ONLY** |
| 10 | A non-cooperating client performing the same read succeeds | `200` | The voluntary control is trivially bypassed — **DECLARED-ONLY** |
| 11 | Bob declares a DPV purpose on the request; server accepts it | `200` | The purpose is neither required nor checked — **NOT-SUPPORTED** |
| 12 | The declared purpose is recorded anywhere server-side | `False` | There is no purpose channel to record it — **NOT-SUPPORTED** |
| 13 | **The policy survives an ordinary `PUT` to the resource** | `False` | A routine data update silently destroys the consent policy — **NOT-SUPPORTED** |
| 14 | The policy survives a `PUT` sent with `Link: rel="preserve"` | `True` | Durability exists, but only if the client opts in — **DECLARED-ONLY** |

### Why check 13 is the sharpest one here

CSS resets a resource's description resource whenever the subject resource is
`PUT`, unless the client sends `Link: <...>; rel="preserve"`. If the consent
policy lives in that description resource, then **an ordinary data update
silently deletes the consent record while the data itself remains available**.
Nothing warns anyone. The access rule in the `.acl` is untouched, so the data
keeps flowing — only the record of the agreed terms disappears.

## The policy

ODRL 2.2 Agreement, DPV purpose vocabulary:

```turtle
@prefix odrl: <http://www.w3.org/ns/odrl/2/>.
@prefix dpv:  <https://w3id.org/dpv#>.

<#agreement> a odrl:Agreement ;
    odrl:uid <#agreement> ;
    odrl:assigner <ALICE_WEBID> ;
    odrl:assignee <BOB_WEBID> ;
    odrl:permission [
        odrl:target <RESOURCE> ;
        odrl:action odrl:read ;
        odrl:constraint [
            odrl:leftOperand  odrl:purpose ;
            odrl:operator     odrl:eq ;
            odrl:rightOperand dpv:ScientificResearch
        ]
    ] ;
    odrl:prohibition [
        odrl:target <RESOURCE> ;
        odrl:action odrl:distribute
    ] .
```

Note on `odrl:purpose`: it is defined in the ODRL **Common Vocabulary**
(§4.5.19), which is **non-normative**, and its definition is thin — "a defined
purpose for exercising the action of the Rule". Even in ODRL, purpose is a
semantically weak left operand.

## Bears on (open questions, not conclusions)

- **GDPR Art. 5(1)(b)** purpose limitation and **Art. 6(1)(a) / Art. 7** consent:
  observed, a purpose can be *expressed* in machine-readable form and stored
  next to the data, but no component reads it when deciding access.
- **GDPR Art. 7(1)** — the controller must be able to demonstrate consent.
  Observed: a consent record attached via the spec's designated metadata slot is
  destroyed by an ordinary data update unless the writing client opts in to
  preserve it. Whether a record with that durability can support the
  demonstrability requirement is a legal question.

Regulation (EU) 2016/679, OJ L 119, 4.5.2016, p. 1 —
https://eur-lex.europa.eu/eli/reg/2016/679/oj

## Spec references

- **ODRL 2.2 Information Model** §2.1 Policy, §2.6.1 Permission, §2.6.2
  Prohibition, §2.4 Action, §2.3.3 assigner/assignee, §2.5 Constraint —
  https://www.w3.org/TR/odrl-model/ (W3C Recommendation, 2018-02-15)
- **ODRL 2.2 Vocabulary & Expression** §4.5.19 `purpose` (non-normative) —
  https://www.w3.org/TR/odrl-vocab/
- **DPV 2.3** `dpv:ScientificResearch` — https://w3id.org/dpv/2.3
  (Final Community Group Report, 2026-02-25); IRI `https://w3id.org/dpv#ScientificResearch`
- **Solid Protocol** §4.3.2 Description Resource, §5.3.1 N3 Patch —
  https://solidproject.org/TR/protocol (v0.11.0, 2024-05-12)
- **WAC** §4.2 Access Modes — https://solidproject.org/TR/wac

## Result

_Not yet run._
