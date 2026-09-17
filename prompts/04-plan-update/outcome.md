# Outcome — prompt 04 (plan update before building)

## Provenance

Received while the plan was awaiting approval; the plan was revised and
re-presented before any code was written. Assistant: Claude Opus 5.
CSS 7.2.0, Python 3.12.13.

## What changed

1. **Definition of done promoted to the top of the plan.** Working, re-runnable
   prototypes are the priority. "Done" means: from a clean checkout,
   `./start.sh --reset` succeeds, `pytest -q` passes, and every experiment runs
   twice in a row with identical results. All three were verified.
2. **Hypotheses committed before running.** Each experiment has a
   `Hypotheses for NN_... (pre-run)` commit preceding its `Results for NN_...`
   commit, so the git history is independent evidence they were not retrofitted.
3. **The six follow-ups**, all applied:
   - `WAC-Allow` is recorded as **advertised permissions**, deliberately distinct
     from the ODRL declared-only finding. A three-term vocabulary
     (enforced / advertised / declared-only) is defined in `CLAUDE.md` and used
     consistently.
   - The `ath` behaviour was **not** directly tested, so **no finding is
     recorded** — only a methods note that the lab emits `ath`.
   - The localhost simulation caveat appears wherever the independent-WebID
     result is reported.
   - The image licence is described as part of the test scenario; all personal
     data is marked synthetic at the point of use.
   - EUR-Lex proved unfetchable, so nothing is quoted — references plus labelled
     paraphrase, with the failure noted.
   - Official Journal references are given for all three acts.
4. **Prof. Aurelia Tamò-Larrieux (Law)** added as co-supervisor in the plan
   context, `CLAUDE.md` and `RESULTS.md` framing.

## Result

All four experiments ran to completion: **62 checks, 0 UNEXPECTED** after three
documented corrections (one pre-run fixture miscount, one genuinely wrong
prediction, two bugs in the experiment's own code). Full detail in
`RESULTS.md` under "Methods".

> **AI-use disclosure.** The author's answers to the planning questions were made
> **with advice from a separate Claude chat session**. All figures are
> **AI-generated**, drawn after the runs from observed results. The legal
> analysis is *not* AI-generated: `RESULTS.md` stops at open questions.
