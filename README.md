# Solid Thesis Lab: what a Solid server enforces, and what it only declares

## What this is

This is the experimental part of a Master's thesis at the University of
St. Gallen (HSG), in law and computer science, supervised by Prof. Simon Mayer
with Prof. Aurelia Tamò-Larrieux (Law) as co-supervisor. It uses Solid as an
experimental architecture for personal data stores. The results are the
technical evidence for a legal analysis of EU platform and data law: GDPR
Art. 20, the Data Act and DMA Art. 6(9). Every experiment asks the same
question: **what does the server actually *enforce*, and what is merely
*declared*?** Everything runs locally against a pinned Community Solid Server
(CSS) 7.2.0. The repository records observations only. The legal analysis is
written separately and draws its own conclusions.

## Chapter map

| Chapter | Research question | Parts | Results |
|---|---|---|---|
| **2: Portability and consent** | What does CSS 7.2.0 with WAC enforce, and what does it only declare, when a data subject shares data, withdraws access, attaches consent terms, and moves to another provider? | [`00_hello_pod`](experiments/00_hello_pod/README.md), [`01_share_revoke`](experiments/01_share_revoke/README.md), [`02_odrl_consent`](experiments/02_odrl_consent/README.md), [`03_portability`](experiments/03_portability/README.md) | [`RESULTS.md`](RESULTS.md) |
| **3: Revocation half-life** | After alice revokes a recipient's read access to a pod resource, what persists, where, for how long, and does any component receive a signal that access ended? | P1 direct GET, P2 HTTP caching, P3 notifications, P4 Comunica, P5 aggregator, P6 agent memory, P7 withdrawal notice: [`ch3/README.md`](ch3/README.md) | [`ch3/results/RESULTS.md`](ch3/results/RESULTS.md) |

## Key findings

These are taken from each chapter's "In plain language" section, which gives
the full wording and the evidence behind each finding. They make no legal
claims.

**Chapter 2**: CSS 7.2.0 with `@css:config/file.json` (file storage, WAC).
Totals across 62 checks: 39 ENFORCED, 17 NOT-SUPPORTED, 6 DECLARED-ONLY,
0 UNEXPECTED ([details](RESULTS.md#in-plain-language)).

- **Access control is enforced.** An authenticated agent with no grant is
  refused, and so is an anonymous one. A revocation applies from the very next
  request, even while the recipient holds an access token that is valid for
  another hour. What the `WAC-Allow` header advertised always matched the
  status codes.
- **Control ends at the URL.** Bob copied Alice's file into his own pod, on
  the same server, under the same protocol and access-control system. Alice
  could then neither read that copy nor delete it (`403`). Nothing
  malfunctioned: no mechanism for this exists.
- **An ODRL 2.2 / DPV consent policy is declared only.** The policy sat in the
  resource's description resource. CSS stored it and served it back, and a
  read returned `200` whether the policy said Permission or Prohibition. No
  request field lets a client state a purpose. An ordinary `PUT` of the data
  silently reset the description resource, which deleted the policy.
- **Portability moves the bytes, not the meaning.** Documents and a binary
  migrated byte-identical, with their media types. The copied links still
  named the old provider, and the ACLs did not travel. A grant made to the
  old WebID gave the new identity `403`, even with an `owl:sameAs` link. With
  provider A switched off, the identity it hosted could not authenticate
  anywhere. A provider-independent WebID still read (`200`). Here, three
  localhost ports stand in for independent origins.

**Chapter 3**: CSS 7.2.0 with `ch3/config/css-wac.json` (WAC) and
`ch3/config/css-acp.json` (ACP). 36 conditions, 720 counted raw files, 0 failed
([details](ch3/results/RESULTS.md#in-plain-language)).

- **At the server, revocation is enforced at once.** Under both WAC and ACP,
  the first request appR sent after alice's revoke was refused (P1, 20/20 runs
  per config across both full runs). This held even though appR's access
  token was still valid. A query engine that had already read the data asked
  again and was refused (P4). Nothing stale ever came from CSS itself.
- **Data that has already left the server stays out of reach.** An aggregator
  kept all 23 copied rows (P5 naive). A retrieval memory kept all 10 of its
  chunks. For all 10 questions it still ranked a chunk of the revoked resource
  first, and `qwen2.5:3b` answered all 10 correctly (P6). Proxy config B,
  deliberately permissive and written for this experiment, served the revoked
  resource for about 60 seconds, including to an anonymous client that CSS
  itself refused (P2).
- **Nothing signals that access ended.** Notification channels (WebSocket and
  Webhook) opened before the revoke delivered all 20 of alice's later changes.
  No component received any message about the permission change (P3). The
  refusal is identical, in status, body and headers, whether access was
  withdrawn, never granted, or the resource was deleted (P5).
- **A withdrawal notice works only if the recipient acts on it.** The P7 notice
  arrived in about a second, a delay set by our handler's 1 s polling. A
  cooperating recipient deleted everything and a non-cooperating one kept
  everything. alice saw the same thing in both cases. A DPV "consent
  withdrawn" status in the notice is declared only: it arrived intact in
  160/160 receptions, and no component used it.

## Method

- **Setup.** Everything runs on localhost against CSS 7.2.0, pinned in
  `package-lock.json`, with Python 3.12 pinned through `uv.lock`. Chapter 2
  runs three processes: provider A on `:3000`, provider B on `:3001`, and a
  static WebID host on `:3002`. Chapter 3 runs its own two CSS instances,
  WAC on `:3100` and ACP on `:3101`.
- **Three terms, kept distinct** (defined in [`CLAUDE.md`](CLAUDE.md#vocabulary--keep-these-three-distinct)):

  | Term | Meaning | Example |
  |---|---|---|
  | **Enforced** | The server changes its behaviour because of it | a `.acl` rule producing `403` |
  | **Advertised** | The server states permissions it does apply | the `WAC-Allow` header |
  | **Declared only** | Metadata with no effect on any decision | the ODRL policy |

- **Pre-registration.** Every expected outcome was committed before the
  code that tests it ran. Chapter 2 has a `Hypotheses for NN_... (pre-run)`
  commit before each `Results for NN_...` commit. Chapter 3 commits each
  phase's section of [`ch3/HYPOTHESES.md`](ch3/HYPOTHESES.md) in its own
  commit, before that phase's first counted run. Chapter 3 was
  squash-merged into `main`, so these commits are not in `main`'s history.
  The seven per-phase `Hypotheses for Chapter 3 Pn … (pre-run)` commits are
  in [PR #4](https://github.com/giusescc/master_thesis/pull/4/commits)
  (tag `ch3-history`). The P7 notice v2 pre-registration commit `932b9f6`
  (`P7 notice v2: pre-register DPV consent-status predictions … before any
  run`) is in [PR #5](https://github.com/giusescc/master_thesis/pull/5/commits)
  (tag `ch3-closeout-history`). After
  `git fetch --tags`, run
  `git log --oneline ch3-history -- ch3/HYPOTHESES.md` and
  `git log --oneline ch3-closeout-history -- ch3/HYPOTHESES.md`. When a
  prediction was wrong, the prediction stays as written and the correction
  is recorded: one in Chapter 2 (`401`, not `404`), and in Chapter 3 H4.2
  was wrong and H3.7 partly wrong.
- **Repetitions.** In Chapter 2, every check declares its expected outcome and
  the test suite re-verifies it, and the definition of done in `CLAUDE.md`
  requires every experiment to run twice in a row with identical results.
  In Chapter 3 every condition ran twice, as full run 1 and full run 2, the
  second from a fresh reset, with 10 counted runs per full run.
  `npm run exp:compare` checks that the categorical outcome of every
  condition is identical across the two full runs.
- **Excluded runs.** Raw files are never deleted or rewritten. Chapter 3 keeps
  22 raw files that are not counted, each listed with its reason in
  [`ch3/results/raw/EXCLUDED.tsv`](ch3/results/raw/EXCLUDED.tsv). 7 of them
  were an instrument fault in P2. The other 15 spanned a macOS system suspend
  and were each replaced by a make-up rep (r11 and up). `npm run exp:check`
  rejects any run that spanned a system suspend. In Chapter 2,
  a one-off HTTP `500` that did not reproduce is noted and not reported as a
  finding.
- **Spec and implementation are kept apart.** A finding about CSS is not
  presented as a finding about the specifications.
  [`ch3/results/SPEC_VS_IMPL.md`](ch3/results/SPEC_VS_IMPL.md) sets each spec
  clause against observed behaviour. The clauses are quoted verbatim, with
  retrieval notes, in [`ch3/docs/spec_quotes.md`](ch3/docs/spec_quotes.md).
  [`RELATED_WORK.md`](experiments/02_odrl_consent/RELATED_WORK.md) scopes the
  Chapter 2 consent findings against other parts of the Solid ecosystem.

## How to navigate

| You want | Chapter 2 | Chapter 3 |
|---|---|---|
| The summary | [`RESULTS.md`](RESULTS.md) | [`ch3/results/RESULTS.md`](ch3/results/RESULTS.md) |
| Hypotheses, as committed before the run | each `experiments/NN_*/README.md` (hypotheses, then result) | [`ch3/HYPOTHESES.md`](ch3/HYPOTHESES.md) |
| Measured facts, per phase or experiment | the per-experiment README tables | [`ch3/results/OBSERVATIONS.md`](ch3/results/OBSERVATIONS.md) |
| Raw evidence | `experiments/*/evidence/` (redacted HTTP transcripts), `experiments/*/result.json` | `ch3/results/raw/<phase>/<config>/*.jsonl`, with [`MANIFEST.sha256`](ch3/results/raw/MANIFEST.sha256) |
| Spec quotes and spec vs implementation | [`RELATED_WORK.md`](experiments/02_odrl_consent/RELATED_WORK.md) | [`SPEC_VS_IMPL.md`](ch3/results/SPEC_VS_IMPL.md), [`spec_quotes.md`](ch3/docs/spec_quotes.md) |
| Exact versions | [`RESULTS.md`](RESULTS.md#exact-versions-for-reproduction) | [`ch3/results/ENVIRONMENT.md`](ch3/results/ENVIRONMENT.md) |
| Figures | [`figures/`](figures/) (SVG, drawn from observed results) | |

The client library is in [`solidlib/`](solidlib/). It covers DPoP
authentication, account provisioning, WAC, description resources, and evidence logging.

## Reproduce

**Requirements**

| Tool | Version | Needed for |
|---|---|---|
| Node.js | 22.23.2 (`.nvmrc`) | CSS 7.2.0, the P4 Comunica driver |
| uv | any recent; installs Python 3.12 from `.python-version` | every experiment and phase |
| Docker | a running daemon | Chapter 3 P2 only (nginx, pinned by digest) |
| Ollama | 0.34.4, with `qwen2.5:3b` and `nomic-embed-text` pulled | Chapter 3 P6 and P7 only (digests pinned in `ch3/config/ollama-models.txt`) |

**Chapter 2** (ports `:3000–3002`):

```bash
./start.sh --reset                                  # wipe storage, npm ci + uv sync, start 3 servers, provision users, write .env
uv run python experiments/02_odrl_consent/run.py    # run one experiment (00_hello_pod … 03_portability)
./start.sh --stop                                   # stop; ./start.sh without a flag resumes
```

**Chapter 3** (ports `:3100` and `:3101`; P2 also starts nginx in Docker):

```bash
npm run exp:setup -- --reset   # two CSS 7.2.0 instances (WAC, ACP), users, ch3/.state/.env, ENVIRONMENT.md
npm run exp:p1                 # … through exp:p7; each runs >= 10 reps per condition on both configs
npm run exp:check              # completeness, timestamps, hashes, suspends
CH3_FULL_RUN=2 npm run exp:p1  # … a second full run, after a fresh exp:setup -- --reset
npm run exp:compare            # full run 1 vs full run 2
npm run exp:stop
```

**Tests.** `uv run pytest -q` re-verifies the claims and needs both labs
running (`./start.sh --reset` and `npm run exp:setup -- --reset`). Running the
Chapter 2 tests rewrites the timestamps in the tracked Chapter 2 evidence.
Restore those files with `git restore experiments/` rather than committing
them. [`ch3/README.md`](ch3/README.md) has the per-phase options and the
approximate durations.

## How this was built

The code was written by Claude Code (Anthropic's coding agent) from my
specifications. [`CLAUDE.md`](CLAUDE.md) holds the working rules the agent
followed: never invent a result, pre-register hypotheses, document
corrections, draw no legal conclusions, never quote legal text from memory.
[`prompts/`](prompts/README.md) archives the early instructions verbatim,
with their outcomes, and [`docs/agents/build-log.md`](docs/agents/build-log.md)
records what each later piece of work built and the decisions it made. I
reviewed the design choices and the results, and chose between options where
the record says "the User chose".

## Limitations

- **One server implementation.** Every claim is scoped to CSS 7.2.0 with the
  configurations above: WAC only in Chapter 2, WAC and ACP in Chapter 3. Other
  servers may behave differently, for example Inrupt ESS with Access Grants,
  which was not run.
- **Localhost.** Ports on one machine stand in for independent origins. DNS,
  TLS, CORS and organisational boundaries are out of scope. Timings come from
  our instruments, such as polling intervals and a proxy configuration we
  wrote, and are not properties of CSS or of Solid.
- **Synthetic data.** All personal data is invented, and the binary fixture is
  generated rather than downloaded.
- **Recipients written for the experiment.** The Chapter 3 aggregator,
  retrieval memory, notice handlers, notice format and the permissive proxy B
  are our code. They are not claimed to be representative. P6 and P7 use a
  small model (`qwen2.5:3b`).
- **Not built.** Continuous access over Solid Notifications
  (`04_continuous_access`) and onward sharing (`05_onward_sharing`) were
  deferred. ODRL enforcement by research prototypes is cited in
  `RELATED_WORK.md`, not run.

## Status

The experiments for Chapters 2 and 3 are complete. The legal analysis is in
progress.

## Licence

Code is under the MIT licence ([`LICENSE`](LICENSE)). Documentation, results
and figures are under CC BY 4.0 ([`LICENSE-docs`](LICENSE-docs)). Quoted
third-party specification text keeps its original licence.
