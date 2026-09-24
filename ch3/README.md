# Chapter 3: revocation half-life

After alice revokes a recipient's read access to a pod resource, what
persists, where, for how long, and does any component receive a signal that
access ended? Measured on **CSS 7.2.0** with two configurations: WAC on
:3100 and ACP on :3101, both on the file backend with notifications enabled.

> Work in progress. This README is completed at the end of the build, with
> clean-machine reproduction steps, every phase, and the expected outputs.

## Quick start

```bash
npm run exp:setup -- --reset   # CSS 7.2.0 WAC :3100 + ACP :3101, seeded; writes results/ENVIRONMENT.md
npm run exp:p1                 # ... exp:p7, each >= 10 reps per condition on both configs
npm run exp:check              # every condition has >= 10 runs; every line has an ISO-ms-UTC ts
npm run exp:compare            # full run 1 vs full run 2: identical categorical outcomes
npm run exp:stop
```

## Layout

```
ch3/
  config/        css-wac.json, css-acp.json, *-short.json (maxDuration 2 min), seed.json
  fixtures/      person.ttl (revoked), distractor.ttl (kept), questions.json
  lib/           env, agents (DPoP via solidlib), access (WAC/ACP), scene, jsonl, harness, conditions
  phases/        pN_*/run.py, one per phase
  tools/         setup.sh, provision, environment, check, compare
  results/
    raw/<phase>/<config>/<run-id>.jsonl   never overwritten; MANIFEST.sha256
    ENVIRONMENT.md, OBSERVATIONS.md, INTERPRETATION_NOTES.md, SPEC_VS_IMPL.md
  HYPOTHESES.md  pre-registered, one commit per phase before its first run
```

State (`ch3/.state/`: pod data, credentials, server logs) is git-ignored.
Chapter 2's lab on :3000–3002 is independent and untouched.
