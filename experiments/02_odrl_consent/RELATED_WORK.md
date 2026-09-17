# Purpose in the Solid ecosystem — what exists, and what it actually does

This file scopes the claim made by experiment 02. That experiment shows that
**CSS + WAC + Solid-OIDC** have no channel for a purpose of processing. That is
a narrow claim about the core stack, and it would be an overclaim to extend it
to "Solid cannot express purpose". Other work does express purpose. The
distinction that matters is whether purpose is **enforced** in an access
decision or merely **recorded** as metadata.

All claims below were verified against primary sources on 2026-09-17. Where a
source could not be read, that is stated rather than glossed.

## Summary

| Approach | Expresses purpose? | Vocabulary | **Enforced in an access decision?** | Status | Works with CSS? |
|---|---|---|---|---|---|
| Solid Protocol / WAC / ACP / Solid-OIDC | **No** | — | No — no channel at all | CG Reports / EDs | is CSS |
| Inrupt Access Grants (ESS) | Yes, `forPurpose` | **GConsent** | No documented server-side check — see caveat | Commercial product | No (ESS only) |
| Solid Application Interoperability (DIP) | **No** | — | n/a | Draft CG Report v0.2 | No |
| SolidLab `user-managed-access` + `OdrlAuthorizer` | Yes | ODRL `odrl:purpose`, DPV values | **Yes — genuinely enforced** | Research prototype, unpublished | Yes, but CSS `8.0.0-alpha` |
| OAC / DPV+ODRL literature | Yes | ODRL + DPV | Authoring, not enforcement | Papers + draft profiles | Varies |
| Consent receipts (ISO 27560 / DPV) | Yes, `dpv:hasPurpose` | DPV | **Recording only, by design** | Standard; no Solid implementation found | n/a |

## 1. The core stack has no purpose channel — confirmed four ways

- **Solid-OIDC** (https://solidproject.org/TR/oidc, v0.1.0; and the current ED,
  last modified 2026-07-20): the words "purpose" and "intent" do not appear.
  The only Solid-specific scope defined is `webid`.
- **Solid Protocol** (https://solidproject.org/TR/protocol, v0.11.0,
  2024-05-12): "purpose" appears twice, both editorial ("for the purposes of
  this specification").
- **WAC** (https://solidproject.org/TR/wac, v1.0.0, 2024-05-12): one editorial
  occurrence.
- **ACP** (https://solidproject.org/TR/acp, ED v0.9.0): its complete context is
  `acp:target`, `acp:mode`, `acp:agent`, `acp:creator`, `acp:owner`,
  `acp:client`, `acp:issuer`, `acp:vc`. No purpose attribute.

Confirmed at implementation level in CSS's own ACP context builder
(`src/authorization/AcpReader.ts`), which builds a context of exactly four
fields — target, agent, client, issuer. `WebAclReader.ts` is narrower still.

**Important qualification.** ACP is *extensible* via sub-properties of
`acp:attribute`, so a purpose attribute is architecturally possible, merely
unspecified. "No purpose channel" is a statement about what is specified, not
about what could be built.

## 2. Inrupt Access Grants — records purpose, no documented enforcement

Inrupt's Enterprise Solid Server issues Access Grants as Verifiable Credentials
carrying a purpose field. **The vocabulary is GConsent, not DPV** —
`https://w3id.org/GConsent#forPurpose`, confirmed in Inrupt's published JSON-LD
context (https://schema.inrupt.com/credentials/v2.jsonld) and in the client
library source. Values are opaque IRIs; Inrupt's own examples use an invented
namespace rather than DPV.

The entire purpose-related API surface of `@inrupt/solid-client-access-grants`
is a **reader** (`getPurposes`) and a **query filter**. Inrupt's documentation
describes the field as the "stated purpose(s)" and calls the grant a "receipt".

> ⚠️ **Stated carefully, because this cannot be fully verified.** Inrupt's
> documentation is *silent* on purpose enforcement rather than explicitly
> denying it, and ESS is closed-source. The defensible formulation is:
> *"Inrupt's Access Grants carry a `forPurpose` field, but the published
> documentation and client libraries expose purpose only as credential metadata
> and as a query filter; no documented mechanism ties the stated purpose to a
> server-side access decision."* Do **not** write "Inrupt does not enforce
> purpose" as a bare assertion.

GConsent: Pandit et al. (2019), ESWC, https://doi.org/10.1007/978-3-030-21348-0_18

## 3. Solid Application Interoperability — no purpose at all

The W3C Solid Data Interoperability Panel's specification
(https://solid.github.io/data-interoperability-panel/specification/, Draft CG
Report v0.2, 2026-09-10) models an Access Need as a shape tree, access modes,
and an `accessNecessity` flag. "Purpose" does not occur in any normative source
file.

This gap is acknowledged and unresolved — a useful citation:

> **Issue #281, "Consider changing `AccessNeed` and related concepts with
> `Purpose`"**, opened by Harshvardhan J. Pandit on 2022-10-21, arguing that
> purpose "is normative, well defined and understood both legally and socially"
> whereas `AccessNeed` has no legal grounding. **Still open, four years later.**
> https://github.com/solid/data-interoperability-panel/issues/281

## 4. SolidLab user-managed-access — genuinely enforces purpose

https://github.com/SolidLabResearch/user-managed-access (IDLab, Ghent; MIT;
actively developed, last push 2026-09-10) replaces WAC/ACP with a UMA 2.0 flow.
Its `OdrlAuthorizer` converts a client's purpose claim into an `odrl:Constraint`
(`leftOperand` `odrl:purpose`, `operator` `odrl:eq`) and evaluates it. Its own
unit tests use `https://w3id.org/dpv#ScientificResearch` — the same IRI
experiment 02 uses. Its documentation states plainly that if a client provides
the purpose during token exchange authorization succeeds, and otherwise fails.

**This is real purpose-conditioned allow/deny, not metadata.**

Two qualifications matter for reproducibility:

- Its packages are marked `"private": true` and are **not published to npm**
  (`@solidlab/uma`, `@solidlab/uma-css`, `@solidlab/ucp` all return HTTP 404).
- It depends on `"@solid/community-server": "^8.0.0-alpha.1"` — a **pre-release
  CSS 8 alpha**, not the 7.2.0 stable line this lab pins.

This is why the experiment **cites rather than runs** it: reproducing it would
require abandoning the pinned stable server for an unreleased alpha.

The underlying engine, `odrl-evaluator`, *is* on npm (0.6.0, 2026-01-21) and its
support matrix lists `odrl:purpose` as supported — while noting it is
**non-normative** in ODRL itself.

Citations: Slabbinck et al., *From Access Control to Usage Control with
User-Managed Access*, arXiv:2601.18761; Slabbinck et al., *Interoperable
Interpretation and Evaluation of ODRL Policies*, ESWC 2025,
https://doi.org/10.1007/978-3-031-94578-6_11

## 5. The ODRL/DPV literature — authoring, not enforcement

- **OAC (ODRL Profile for Access Control)**, Esteves, Pandit,
  Rodríguez-Doncel — https://beatrizesteves.org/odrl-access-control-profile/oac.html
  (Draft v0.2, 2023-10-09). Uses DPV for purposes. No enforcement engine; the
  profile itself contains placeholder text and is stalled at draft.
- Esteves, Pandit, Rodríguez-Doncel (2021), *ODRL Profile for Expressing Consent
  through Granular Access Control Policies in Solid*, IEEE EuroS&PW,
  https://doi.org/10.1109/EuroSPW54576.2021.00038 — a proposal.
- **SOPE** (Esteves et al., ESWC 2022 Posters/Demos,
  https://doi.org/10.1007/978-3-031-11609-4_3) — a policy **editor**. Its repo
  was last pushed 2024-03-30.
- Esteves & Rodríguez-Doncel (2024), *Analysis of ontologies and policy
  languages to represent information flows in GDPR*, Semantic Web 15(3),
  709–743, https://doi.org/10.3233/SW-223009 — the best single citation for
  "this gap is systematically documented".
- Pandit (2023), *Making Sense of Solid for Data Governance and GDPR*,
  Information 14(2), 114, https://doi.org/10.3390/info14020114.

> ⚠️ Two MDPI papers (Esposito et al., *Assessing the Solid Protocol in Relation
> to Security and Privacy Obligations*, Information 14(7), 411; and Florea &
> Esteves, *Is Automated Consent in Solid GDPR-Compliant?*, Information 14(12),
> 631) returned HTTP 403 to automated retrieval. Their bibliographic metadata is
> verified via Crossref, but **their full texts have not been read** and nothing
> is attributed to them here.

## 6. Consent receipts — recording by construction

ISO/IEC TS 27560:2023 (from the Kantara Consent Receipt Specification v1.1) has
a machine-readable realisation in DPV, including `dpv:hasPurpose`
(https://w3c-cg.github.io/dpv/guides/consent-27560).

**No Solid-specific consent-receipt implementation was found** — no repository,
product or paper storing ISO 27560 / DPV consent records in a pod and connecting
them to an access decision.

The category point strengthens the thesis: a consent receipt is *by definition*
a record. ISO 27560 is titled "consent **record** information structure". Even a
perfect Solid implementation of it would be a recording channel, not an
enforcement one, unless separately wired into an authorizer — which nobody has
done.

Citation: Pandit, Lindquist, Krog (2024), APF,
https://doi.org/10.1007/978-3-031-68024-3_12 (preprint arXiv:2405.04528)

## The scoped claim

> Purpose is not a first-class concept in core Solid. The Solid Protocol
> (v0.11.0), Web Access Control (v1.0.0), Access Control Policy (ED 0.9.0) and
> Solid-OIDC contain no mechanism for a requesting party to declare, or a server
> to evaluate, a purpose of processing. This is reflected in the reference
> implementation: the Community Solid Server builds its authorization context
> from the target IRI, the agent's WebID, the client ID and the issuer, and
> nothing else. Purpose therefore cannot enter a core-Solid access decision.
> This does not mean the ecosystem is silent on purpose. **Recording
> approaches** attach a purpose without conditioning access on it: Inrupt's
> Access Grants carry a GConsent `forPurpose` field that the published
> documentation and client libraries expose only as metadata and as a query
> filter, with no documented server-side check — Inrupt itself calls the grant a
> "receipt"; ISO/IEC TS 27560 consent records expressed with DPV are records by
> construction, and no Solid implementation of them was found. The Solid Data
> Interoperability Panel's specification does not model purpose at all, and a
> 2022 proposal to introduce it remains open. **Enforcing approaches** exist
> only in research prototypes: SolidLab's `user-managed-access` translates a
> client's purpose claim into an `odrl:purpose` constraint and evaluates it,
> yielding a genuine purpose-conditioned decision against DPV IRIs — but its
> packages are unpublished and it targets a pre-release CSS 8 alpha. In short:
> a purpose channel for Solid is demonstrated and buildable, but as of September
> 2026 it exists outside the core specifications, and where it ships in a
> production product it records rather than enforces.
