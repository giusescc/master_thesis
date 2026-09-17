# Results — what Solid enforces, and what it only declares

62 checks across four experiments, run against a local **Community Solid Server
7.2.0**. Every check declared its expected outcome **before** the run (committed
separately in the git history), and any mismatch is flagged `UNEXPECTED` rather
than reclassified afterwards.

| | Count |
|---|---|
| **ENFORCED** — the server changed its behaviour because of it | 39 |
| **NOT-SUPPORTED** — no mechanism exists at all | 17 |
| **DECLARED-ONLY** — present as metadata, no effect on any decision | 6 |
| **UNEXPECTED** — a stated expectation did not hold | 0 |

`UNEXPECTED` is zero *after* three documented corrections during experiment 03:
one pre-run arithmetic slip, one genuinely wrong prediction of ours (recorded in
full below), and two bugs in our own code. None were hidden; see
[`experiments/03_portability/README.md`](experiments/03_portability/README.md)
and the commit history.

---

## The one-table answer

**Advertised** is kept distinct from **declared-only** throughout. The
`WAC-Allow` header is the server *advertising* permissions it genuinely does
apply — it is not a broken promise, and conflating it with the inert ODRL policy
would blur the central finding.

| # | What was tested | Result | Advertised (`WAC-Allow`) |
|---|---|---|---|
| **00** | Owner can read and write her own resource | **ENFORCED** | matched enforcement |
| 00 | Authenticated-but-unauthorised agent refused (`403`) | **ENFORCED** | matched |
| 00 | Unauthenticated client refused (`401`) | **ENFORCED** | matched |
| 00 | A new pod's **root container is world-readable** by default | **ENFORCED** | `public="read"` |
| **01** | Sharing via a WAC `.acl` grant | **ENFORCED** | `user="read"` |
| 01 | Revocation takes effect **immediately** | **ENFORCED** | advertisement disappeared |
| 01 | Bob's **already-issued unexpired token** stops working at once | **ENFORCED** | — |
| 01 | Preventing a reader from copying the data | **NOT-SUPPORTED** | — |
| 01 | Reaching a copy Bob saved locally | **NOT-SUPPORTED** | — |
| 01 | Reaching a copy **inside Bob's own pod** (read → `403`, delete → `403`) | **NOT-SUPPORTED** | — |
| **02** | Attaching an ODRL/DPV policy to the spec's description resource | **ENFORCED** (storage) | — |
| 02 | **Prohibition flip: `Permission` → `Prohibition` changed nothing** (`200` both) | **DECLARED-ONLY** | `user="read"` |
| 02 | Prohibition on redistribution | **DECLARED-ONLY** | — |
| 02 | Client-side voluntary enforcement (bypassed by not implementing it) | **DECLARED-ONLY** | — |
| 02 | Declaring a **purpose** of processing on a request | **NOT-SUPPORTED** | — |
| 02 | Recording the declared purpose anywhere server-side | **NOT-SUPPORTED** | — |
| 02 | **An ordinary `PUT` silently destroyed the consent policy** | **NOT-SUPPORTED** | — |
| 02 | Policy durability via voluntary `Link: rel="preserve"` | **DECLARED-ONLY** | — |
| **03** | Documents + binary migrate intact (media type, byte-identical SHA-256) | **ENFORCED** | — |
| 03 | Generic traversal of a whole pod via `ldp:contains` | **ENFORCED** | — |
| 03 | Internal links surviving a verbatim move (still name the old provider) | **NOT-SUPPORTED** | — |
| 03 | Any protocol mechanism to rewrite IRIs on migration | **NOT-SUPPORTED** | — |
| 03 | ACLs travelling with the data (invisible to `ldp:contains`) | **NOT-SUPPORTED** | — |
| 03 | Cross-provider authentication, **while the old provider runs** | **ENFORCED** | `user="read"` |
| 03 | ODRL policy re-attached on the new provider — still inert | **DECLARED-ONLY** | — |
| 03 | `owl:sameAs` making a grant to the old WebID reach the new identity (`403`) | **NOT-SUPPORTED** | — |
| 03 | Leaving a redirect or tombstone at the old WebID | **NOT-SUPPORTED** | — |
| 03 | A **provider-independent WebID** linked after an ownership proof | **ENFORCED** | — |
| 03 | **Provider A off: a provider-hosted identity cannot authenticate anywhere** | **NOT-SUPPORTED** | — |
| 03 | **Provider A off: the independent identity still reads (`200`)** | **ENFORCED** | `user="read"` |

Per-experiment tables, with every status code, are in each experiment's
`README.md`; the raw HTTP transcripts behind every row are in
`experiments/*/evidence/`.

---

## In plain language

**Access control is real.** This is worth saying first, because the rest of this
document is about limits. Web Access Control is not decoration: an authenticated
Solid user with valid credentials and no grant is refused, an anonymous one is
refused, and revocation bites on the very next request even when the recipient
is still holding an access token valid for another hour. The server also
advertises its decisions honestly — what `WAC-Allow` said always matched what
the status codes did.

**What Solid controls is access to a URL, and nothing beyond it.** Every gap we
found follows from that single fact. The moment a read succeeds, the protocol's
job is complete. There is no notion of a copy, no obligation that travels with
data, and no way for the person the data is about to reach it afterwards. When
Bob copied Alice's file into his own pod — same server, same protocol, same
access-control system — Alice could neither read it nor delete it. Nothing
malfunctioned; there is simply no mechanism, and WAC works exactly as designed
in refusing her.

**Consent can be expressed beautifully and means nothing.** We attached a proper
ODRL 2.2 agreement using DPV vocabulary in the slot the Solid Protocol itself
designates for metadata about a resource, written with the patch format the
server advertises. The server stored it, served it back intact — and never read
it. We know it never read it because we replaced the permission with its exact
contradiction, a prohibition on the same read by the same person, and the
response was identical: `200` both times. A policy that produces the same
outcome whether it says "may" or "must not" is not a control.

**Purpose has nowhere to live at all.** This is different from the policy being
ignored. There is no field, header or claim in which a requesting party can say
*why* it wants the data. We invented a header to demonstrate this; the server
accepted the request, ignored the header, and recorded nothing. Purpose
limitation is a cornerstone of European data protection, and the core Solid
stack has no place to put it. (This is scoped precisely — see
[Related work](experiments/02_odrl_consent/RELATED_WORK.md). Research prototypes
*do* enforce purpose, and one commercial product records it.)

**And consent records are fragile in a way nobody is warned about.** Because the
policy lives in a description resource, and because the server resets that
resource whenever the data is written, an ordinary update deleted the consent
policy silently. The access rule was untouched, so the data kept flowing. Only
the record of the agreed terms disappeared.

**Portability works for bytes and fails for meaning.** The migration itself went
well: every document and the binary arrived intact, byte-identical, with media
types preserved, walked by a generic client that knew nothing about the
contents. But copied verbatim, the data still pointed at the pod Alice had left —
intact and simultaneously wrong. Rewriting the links works, but there is no
protocol support for it, so it means mutating the data subject's own records and
breaking anyone who linked to the old addresses. Her access rules did not move at
all: they live in auxiliary resources that a containment-based export never even
sees.

**The deepest problem is that identity belongs to the provider.** Alice's WebID
was an address owned by the company she was leaving. She can state that her new
identity is the same person as the old one, and the server will happily store
that statement, but nothing acts on it — a permission granted to her old address
gave her new identity a `403`. She cannot leave a forwarding address either. When
we switched the old provider off, Bob, whose identity lived there, could not
authenticate **anywhere** — including to resources on the *other* provider that
had been explicitly granted to him. His identity did not merely lose its data; it
ceased to exist along with his provider. The identity we had deliberately hosted
on an independent origin carried on working.

That last comparison is, we think, the most useful thing in this report: in
Solid, moving your files is the part that works. What does not move is the web of
references, the permissions, and above all the identifier — and an identifier
hosted by the provider you are trying to leave is not portable at all.

---

## Legal hooks — open questions, not conclusions

These are **not** legal conclusions. Each row records a technical observation and
names the provision it bears on, phrased as a question for the legal analysis.

> ### ⚠️ On the legal text
>
> **The official texts could not be retrieved.** EUR-Lex returned HTTP `202`
> with an empty body to automated requests on 2026-09-17, for both the CELEX
> HTML endpoint and the ELI endpoint.
>
> Consequently **nothing below is quoted**. Every characterisation of a
> provision is a **paraphrase, labelled as such**, written from the provision's
> subject matter rather than its wording. Article numbers, Official Journal
> references and ELI links are given so each can be checked against the
> authoritative text. **Verify every characterisation against the Official
> Journal before relying on it.**

| Observation | Bears on | Open question |
|---|---|---|
| Withdrawal is immediate and prospective on the original resource | **GDPR Art. 7(3)** *(paraphrase: concerns the right to withdraw consent)* | Is withdrawal that leaves lawfully-made copies untouched sufficient? |
| The controller must be able to show consent was given; the record here is destroyed by a routine data update | **GDPR Art. 7(1)** *(paraphrase: concerns demonstrating that consent was given)* | Can a consent record with this durability support a demonstrability requirement? |
| A purpose of processing cannot be expressed or evaluated anywhere in the core stack | **GDPR Art. 5(1)(b)** *(paraphrase: concerns purpose limitation)* | What does purpose limitation require of a protocol that has no concept of purpose? |
| The recipient holds an unreachable copy in his own pod and controls it exclusively | **GDPR Art. 4(7)** *(paraphrase: concerns the definition of a controller)* | Does the recipient thereby become a controller? *This experiment establishes only exclusive technical control; it does not answer the legal characterisation.* |
| The data subject has no protocol mechanism to erase a copy held by a recipient | **GDPR Art. 17** *(paraphrase: concerns the right to erasure)* | What can erasure mean in an architecture with no reach beyond the origin resource? |
| Data is exportable and machine-readable; links, ACLs and identity are not portable | **GDPR Art. 20** *(paraphrase: concerns receiving personal data in a structured, commonly used, machine-readable format and transmitting it to another controller)* | Is data whose internal references and permissions do not survive the move "portable"? Does an unportable identifier constitute hindrance? |
| Verbatim-migrated links die when the old provider stops serving; a provider-hosted identity dies with the provider | **EU Data Act, Chapter VI** *(paraphrase: concerns switching between data processing services)* | Does effective switching require identity portability, not only data portability? |
| Continuous access was **not tested** in this round | **DMA Art. 6(9)** *(paraphrase: concerns effective portability of data provided by or generated through the end user's activity)* | Deferred — see Limitations. |

**Sources to verify against**

| Act | Official Journal reference | ELI |
|---|---|---|
| GDPR — Regulation (EU) 2016/679 | OJ L 119, 4.5.2016, p. 1 | https://eur-lex.europa.eu/eli/reg/2016/679/oj |
| DMA — Regulation (EU) 2022/1925 | OJ L 265, 12.10.2022, p. 1 | https://eur-lex.europa.eu/eli/reg/2022/1925/oj |
| Data Act — Regulation (EU) 2023/2854 | OJ L, 2023/2854, 22.12.2023 | https://eur-lex.europa.eu/eli/reg/2023/2854/oj |

*OJ references above are also to be verified; they were not machine-retrieved.*

---

## Methods

**Pre-registration.** Each experiment's README, containing every check's expected
outcome, was committed **before** its code ran. The git history is therefore
independent evidence that predictions were not retrofitted:
`git log --oneline` shows a `Hypotheses for NN_... (pre-run)` commit preceding
each `Results for NN_...` commit.

**The one wrong prediction, in full.** In experiment 03 we predicted that after
Alice deleted her data, a verbatim-migrated link would return `404`. It returns
`401`. CSS does not disclose whether a resource exists to an unauthenticated
client, so a stranger following a dead link cannot even learn that it is dead;
the owner asking for the same URL does get `404`. The link is broken either way,
so the finding stands, but the prediction was wrong and is recorded as such.

**Two bugs of ours, not findings.** Also in 03: `@prefix` declarations nested
inside a `solid:inserts { }` graph (invalid N3), and a `solid:oidcIssuer` IRI
written without the trailing slash carried by the issuer's `iss` claim, which
makes the token verifier reject the identity. Both are our errors and say
nothing about Solid.

**Simulation caveat.** Three `localhost` ports (3000, 3001, 3002) *simulate*
three independent origins. They are not separate providers. DNS, TLS, CORS,
contractual and organisational boundaries are out of scope, and no claim is made
about them.

**Synthetic data.** All personal data is fictional. The binary is generated
programmatically (`fixtures/generate.py`), so reproduction needs no network and
the bytes are identical everywhere. The licence statement attached to that image
*inside the pod* is part of the test scenario — content whose survival is
observed — not a statement about this repository.

**Authentication.** We emit the RFC 9449 `ath` claim on DPoP proofs bound to an
access token. We did **not** test whether CSS accepts proofs without it, so no
claim is made about that.

**Not claimed.** A single HTTP `500` was observed once when listing linked
WebIDs. It did not reproduce across four accounts and is **not** reported as a
finding.

---

## Limitations

- **Continuous/real-time access (DMA Art. 6(9)) was not tested.** A standing
  grant with live updates over Solid Notifications is the obvious next
  experiment (`04_continuous_access`).
- **Onward sharing (Data Act Art. 5) was not tested** — whether a recipient can
  re-share, and what `acl:Control` implies (`05_onward_sharing`).
- **One server implementation.** Findings about *CSS* are distinguished from
  findings about the *specifications* throughout, but only CSS was run.
- **WAC only.** CSS also ships an ACP configuration (`@css:config/file-acp.json`),
  and its documentation states an intention to phase WAC out in favour of ACP.
  Access rules written for one system are meaningless to the other — itself a
  portability question, untested here.
- **ODRL enforcement was cited, not run.** SolidLab's `user-managed-access`
  genuinely enforces `odrl:purpose`, but its packages are unpublished to npm and
  it targets a pre-release CSS `8.0.0-alpha`, not the pinned 7.2.0. See
  [Related work](experiments/02_odrl_consent/RELATED_WORK.md).

---

## Exact versions (for reproduction)

Every version is pinned. `package-lock.json` and `uv.lock` are committed.

| Component | Version |
|---|---|
| `@solid/community-server` | **7.2.0** (pinned in `package.json` + `package-lock.json`) |
| CSS configuration | `@css:config/file.json` — file storage, **WAC** authorization |
| Node.js | v22.23.2 |
| Python | **3.12.13** (pinned via `uv`, `.python-version`, `uv.lock`) |
| `requests` | 2.32.5 |
| `rdflib` | 7.1.4 |
| `jwcrypto` | 1.5.6 |
| `PyJWT` | 2.10.1 |
| `python-dotenv` | 1.1.1 |
| `pytest` | 8.4.2 |

Vendored, not depended upon: the DPoP client-credentials flow in
`solidlib/auth.py` is adapted from `SolidClientCredentials` 1.0.3 (MIT, A_A) —
licence in `solidlib/vendor/`.

**Reproduce from a clean checkout:**

```bash
./start.sh --reset     # wipe storage, start 3 servers, provision all users
uv run pytest -q       # re-verify every claim in this document
```

Run date of the results above: **2026-09-17**.
