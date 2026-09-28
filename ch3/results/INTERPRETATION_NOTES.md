# INTERPRETATION NOTES (Chapter 3), clearly labelled: not observations

> **These are notes for Giuseppe's later legal analysis, not results.** Each
> note points at observations in `OBSERVATIONS.md` and is phrased as an open
> question ("bears on ..."). No legal conclusion is drawn here, and no legal
> text is quoted from memory (CLAUDE.md rules 5 and 6).

Scope of every note: CSS 7.2.0 with the WAC and ACP configurations in
`ch3/config/`, a local lab, and the recipients and client software named in
each phase. Other Solid servers (for example Inrupt ESS with Access Grants,
not tested here) may behave differently. The Enforced / Advertised /
Declared-only vocabulary is the one in `CLAUDE.md`.

**Provisions named in these notes are pointers for Giuseppe to check, not
readings.** Where a provision is named it is named by number only. Its text
was not fetched for this file (EUR-Lex does not answer automated requests, see
CLAUDE.md rule 6), and nothing here paraphrases what it says.

## 1. Revocation is enforced at the server, and only there

- **Observed:** P1, P2 (config A), P4 and P5. After alice's revoke, the first
  request appR sent was refused (403), on WAC and ACP. No stale read came
  from CSS itself.
- **Bears on:** when a right or a withdrawal "takes effect" technically. For
  requests to the pod, CSS 7.2.0 enforced the revoke at once, per request.
  Open question: is "access ended at the server" the relevant event for the
  analysis, or is the relevant event the end of *use* of the data? P5–P7 show
  those two come apart.

## 2. What persists after the revoke is outside the server's reach

- **Observed:** copies (P5 naive: 23/23 rows), derived indexes (P6: 10/10
  questions still answered correctly from the pre-revoke memory) and
  intermediaries (P2 config B: the cached copy served for ~60 s, even to an
  anonymous client). None of these was touched by anything CSS sent.
- **Bears on:** who, in a Solid deployment, is technically able to act on a
  withdrawal. The pod could not reach any of these copies. Only the recipient
  (P5 403-aware, P7 cooperating) removed them, by code we wrote. Open question:
  how obligations that attach to recipients (Giuseppe to check, for example,
  GDPR Art. 7(3), 17 and 19, and Data Act Art. 5) map onto a design where the
  data holder's server can only stop *future* reads.

## 3. No component is told that access ended

- **Observed:** P3: no message on any channel about the ACL/ACR change; P5:
  the 403 is identical for "withdrawn", "never granted" and "deleted"; P4: the
  query engine's error does not mention access. appR learns only that a
  request was refused, and only if it makes one.
- **Bears on:** whether a recipient can be said to "know" of a withdrawal in
  this architecture. Open question: does a duty that depends on the
  recipient's knowledge need an explicit signal that CSS 7.2.0 (as tested)
  did not provide?

## 4. Notification channels outlive the permission they were granted under

- **Observed:** P3: appR's existing WebSocket and Webhook channels kept
  delivering every change to the revoked resource (20/20), on WAC and ACP.
  Reconnecting to the channel URL needed no credentials. Only *new*
  subscriptions were refused. Channels end at `endAt` (20160 min by default),
  or when anyone who knows the channel id sends DELETE. The owner cannot list
  or find them (P3, P7 item c).
- **Bears on:** the Enforced/Advertised/Declared-only distinction. Read access
  to the resource was **enforced** after the revoke. Change events about it
  still flowed, so the enforcement did not cover this second path. The
  notification payload carries no content, only the fact, time and ETag of
  a change (`Update`, `object`, `state`, `published`). Open question: is an
  ongoing stream of change events about a resource "access" in the legal
  sense (DMA Art. 6(9) continuous access and Data Act Art. 4/5 come to mind),
  and does its survival past a revoke matter?

## 5. A withdrawal notice works only with a cooperating recipient, and the sender cannot tell

- **Observed:** P7: the notice arrived at both recipients within ~1 s. A
  cooperating handler purged everything, a non-cooperating one nothing, and
  alice's view was **identical** in both cases (201, then 403). Her recipient
  list existed only in her own grant log. After the revoke, the server no
  longer named the former recipients anywhere.
- **Bears on:** what a data subject or data holder can **demonstrate**. The
  notice is **declared only** in the vocabulary sense: it changes no decision
  that CSS makes. Open questions: whether a notification duty toward
  recipients presupposes a recipient record that the pod (as tested) does not
  keep; and whether a mechanism without acknowledgement can support any claim
  that copies were deleted.
- **Design note (not a result):** the notice deliberately used no
  consent-status or right-exercise term (for example `dpv:ConsentWithdrawn`),
  so as not to presuppose a legal basis. Choosing the terms is part of the
  legal analysis.

## 6. Caching intermediaries: a configuration question, not a CSS one

- **Observed:** P2. CSS 7.2.0 sent no `Cache-Control`. A proxy that honours
  origin headers stored nothing. A deliberately permissive proxy (config B,
  written for this experiment and not claimed to be common) served stale and
  unauthenticated reads for ~60 s.
- **Bears on:** where responsibility for intermediaries sits. Open question:
  whether the absence of explicit `Cache-Control: private/no-store` on
  access-controlled resources is relevant to the analysis, given that RFC 9111
  §3.5 already forbids a shared cache from reusing responses to requests
  that carried `Authorization`, unless `Cache-Control` allows it
  (`SPEC_VS_IMPL.md` P2-2).

## 7. Limits to keep in view

- Every phase ran on one machine, localhost only, with one fixture. The
  timings (e.g. ~1 s notice latency, ~60 s proxy window) are properties of our
  instruments (polling intervals, proxy configuration), not of CSS or Solid.
- The P6 memory used `qwen2.5:3b`, a small model (the User's choice), with a
  fixture of 10 invented facts. Retrieval, the primary measurement, does not
  depend on the generator.
- The fixture's appointment is a **passport renewal**, not a medical
  appointment, to keep clear of health data (special-category data).
- P8 (Inrupt ESS with Access Grants, VC status-list revocation) was out of
  scope. Notes 1–5 may not carry over to it.
