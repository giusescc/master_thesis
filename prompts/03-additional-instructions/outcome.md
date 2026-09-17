# Outcome — prompt 03 (ten additional instructions)

## Provenance

Received before any code was written; every point was folded into the approved
plan before the build began. Assistant: Claude Opus 5. CSS 7.2.0, Python 3.12.13.

## How each instruction was applied

| # | Instruction | Where it landed |
|---|---|---|
| 1 | Pin exact versions, record in RESULTS.md | `package.json` + `package-lock.json` (CSS 7.2.0), `pyproject.toml` + `uv.lock` + `requirements.txt` (Python 3.12.13); "Exact versions" section of `RESULTS.md` |
| 2 | Art. 4(7) as an open question | `experiments/01_share_revoke/README.md` and the legal-hooks table — phrased as a question, with an explicit note that only exclusive *technical* control was established |
| 3 | Scope the purpose finding; note other approaches; don't overclaim | `experiments/02_odrl_consent/RELATED_WORK.md` — separates approaches that **enforce** purpose from those that only **record** it |
| 4 | Independent-WebID variant; realistic data; container with own ACL; Art. 17 + Data Act Ch. VI hooks | `experiments/03_portability/` — independent WebID on `:3002`, fictional contacts/notes/binary, custom container ACL, both hooks as open questions |
| 5 | EUR-Lex links; mark quoted phrases to be verified | Legal-hooks table in `RESULTS.md` |
| 6 | Expected outcomes in the README before running | Every experiment README; committed in a separate earlier commit |
| 7 | Figures only after the runs, reflecting UNEXPECTED results | `figures/` — drawn after all four experiments completed |
| 8 | outcome.md disclosures | This archive; see the disclosure note below |
| 9 | Never commit .env/data/data2; keep repo private | `.gitignore`; verified by a test in `tests/test_experiments.py`; repo confirmed private |
| 10 | Never touch anything outside the folder; stop if blocked | `CLAUDE.md` ground rules; `start.sh` stops processes by pidfile only, never by matching the process table |

## On instruction 3 — two corrections worth recording

Research against primary sources corrected two plausible assumptions:

- **Inrupt Access Grants use GConsent (`forPurpose`), not DPV.** And their
  purpose field appears only as credential metadata and a query filter. Since
  ESS is closed-source, `RELATED_WORK.md` states that no *documented*
  server-side check exists, rather than asserting that none exists.
- **SolidLab's `user-managed-access` genuinely enforces `odrl:purpose`** — but
  its packages are unpublished to npm and it targets a pre-release CSS
  `8.0.0-alpha`. That is why it is cited rather than run.

## On instruction 5 — it could not be fully satisfied

EUR-Lex returned HTTP `202` with an empty body to automated requests on
2026-09-17, for both the CELEX HTML and ELI endpoints. Following the author's
later instruction (prompt 04), **nothing is quoted**: `RESULTS.md` uses
references plus clearly-labelled paraphrases and records the retrieval failure.

> **AI-use disclosure.** The author's answers to the planning questions were made
> **with advice from a separate Claude chat session**. All figures in `figures/`
> are **AI-generated**, produced after the experiments ran and based on observed
> results.
