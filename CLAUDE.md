# CLAUDE.md — project context for future sessions

## What this is

The coding component of Giuseppe Soccio's Master's thesis at HSG, supervised by
**Prof. Simon Mayer**, with **Prof. Aurelia Tamò-Larrieux (Law)** as
co-supervisor. It is a local Solid laboratory producing reproducible evidence
for a legal analysis of Solid against **GDPR Art. 20**, the **EU Data Act**
(Art. 4/5; Chapter VI switching) and **DMA Art. 6(9)**.

One question runs through every experiment:

> **What does the protocol/server actually ENFORCE, versus what is merely
> DECLARED?**

Giuseppe had not used Solid before this project. Explain Solid concepts in plain
language; do not assume familiarity.

## The rules that matter most

1. **Never invent a result.** If the server or the spec cannot do something, say
   so plainly. Those gaps *are* the thesis findings — they are more valuable
   than a workaround.
2. **Never overclaim.** Scope every claim to what was actually tested
   (CSS 7.2.0 + WAC + Solid-OIDC). Other parts of the Solid ecosystem behave
   differently; see `experiments/02_odrl_consent/RELATED_WORK.md`.
3. **Pre-register hypotheses.** Write each experiment's expected outcomes into
   its README and **commit that before running the code**. The git history is
   the evidence that predictions were not retrofitted.
4. **Corrections are documented, never silent.** If a prediction is wrong, say
   so and say why. If the bug is ours rather than a finding, say that too.
5. **No legal conclusions.** `RESULTS.md` stops at "bears on" hooks phrased as
   open questions. The legal analysis is Giuseppe's work, not the assistant's.
6. **Never quote legal text from memory.** EUR-Lex currently returns HTTP 202
   with an empty body to automated requests. When it cannot be fetched, use a
   reference plus a **labelled paraphrase** and note the retrieval failure.
7. **Secrets and state never get committed**: `.env`, `data/`, `data2/`,
   `webid/`, `logs/`. The repo is **private**.
8. **Never touch anything outside this project folder.**
9. **If blocked, stop and ask.** Do not work around a problem silently. Asking
   is cheaper than guessing.

## Vocabulary — keep these three distinct

| Term | Meaning | Example |
|---|---|---|
| **Enforced** | The server changes behaviour because of it | a `.acl` rule producing `403` |
| **Advertised** | The server states permissions it does apply | the `WAC-Allow` header |
| **Declared only** | Metadata with no effect on any decision | the ODRL policy |

`WAC-Allow` is **advertised**, never "declared". Conflating it with the inert
ODRL policy blurs the central finding.

## Environment

- **CSS 7.2.0**, pinned. Config `@css:config/file.json` (file storage, **WAC**).
  Do **not** use `8.0.0-alpha`.
- **Python 3.12** via `uv` (`uv.lock`, `.python-version`). Run everything with
  `uv run`.
- Three processes: `:3000` provider A (alice, bob) · `:3001` provider B
  (alice2) · `:3002` static host for a provider-independent WebID.
- Start with `./start.sh` (resume) or `./start.sh --reset` (clean room).
  `./start.sh --stop` stops everything.
- **Chapter 3** runs its own two CSS 7.2.0 processes, independent of the
  above: `:3100` WAC and `:3101` ACP (alice, appr, bob on each), started with
  `npm run exp:setup [-- --reset]`, stopped with `npm run exp:stop`. P2 adds
  nginx in Docker on `:3180–3183`; P6/P7 use Ollama on `127.0.0.1:11434`.
  See `ch3/README.md`.

## Users

| Who | Where | Role |
|---|---|---|
| **alice** | provider A, `:3000` | the data subject |
| **bob** | provider A, `:3000` | recipient of shared data |
| **alice2** | provider B, `:3001` | Alice's account at a second provider |
| *independent WebID* | `:3002/alice.ttl#me` | Alice's provider-independent identity |

Credentials live in `.env`, written by `./start.sh`, never printed, never
committed.

## Layout

```
solidlib/            client library (auth, provisioning, WAC, description
                     resources, evidence logging, the four-state check model)
experiments/NN_name/ README.md (hypotheses + result), run.py, evidence/
figures/             SVG figures, drawn from observed results
prompts/             every instruction given, verbatim, with outcomes
RESULTS.md           the cross-experiment table and plain-language summary
ch3/                 Chapter 3, revocation half-life (P1–P7): HYPOTHESES.md,
                     config/, fixtures/, lib/, phases/, tools/, results/
                     (raw JSONL, OBSERVATIONS, SPEC_VS_IMPL, INTERPRETATION_NOTES)
```

## Gotchas already paid for

- **Account API order.** `password.create`, `account.pod` and
  `account.clientCredentials` only appear in `controls` **after** authenticating.
  Re-read `controls` with the session token; never hardcode endpoint URLs.
- **DPoP must use ES256.** CSS's OIDC provider advertises EdDSA, but the
  resource-side verifier (`@solid/access-token-verifier`) does not accept it.
- **`solid:oidcIssuer` needs the trailing slash** (`http://localhost:3001/`).
  The `iss` claim carries it; without it the token verifier returns `401`.
- **N3 Patch: `@prefix` goes OUTSIDE `solid:inserts { }`.** Inside the braces is
  invalid N3 and CSS rejects it.
- **Description resources are PATCH-only.** `PUT`/`DELETE` are refused, and a
  `PUT` to the *subject* resource **resets** them unless the client sends
  `Link: <...>; rel="preserve"`.
- **CSS returns `401`, not `404`,** to an unauthenticated client for a resource
  that does not exist. The owner gets `404`.
- **Pod names are forced lower case** (CSS ≥ 7.1.7).
- **Client secrets are shown once** and cannot be read back.

## Definition of done

The build is complete only when, from a clean checkout:

1. `./start.sh --reset` succeeds,
2. `uv run pytest -q` passes, and
3. every experiment runs twice in a row with identical results.

## Not yet done

`04_continuous_access` (DMA Art. 6(9), Solid Notifications) and
`05_onward_sharing` (Data Act Art. 5) were deliberately deferred pending review
of the first four. `solidlib/` is structured so they drop in cheaply.

04 remains deferred. Ch3 P3 tests the same mechanism (Solid Notifications) from the revocation angle, not the continuous-access/portability angle; P3 setup and results may be reusable if 04 is revisited.
