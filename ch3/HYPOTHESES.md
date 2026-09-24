# Chapter 3: pre-registered hypotheses

Each phase's section is committed **in its own commit, before that phase's
first real run** (CLAUDE.md rule 3). `git log -- ch3/HYPOTHESES.md` is the
evidence that no prediction was written after the results. If a prediction
turns out wrong, the section is left as written, and the correction is
recorded in `results/OBSERVATIONS.md` with the reason.

Scope of every prediction: **CSS 7.2.0**, config `ch3/config/css-wac.json`
(WAC, file backend) on :3100 or `ch3/config/css-acp.json` (ACP, file backend)
on :3101, both with the notification components of
`css:config/http/notifications/all.json`. Predictions labelled
"source reading" come from reading the CSS v7.2.0 source. They are
predictions, not results.

Agents: **alice** owns the pod. **appR** is the recipient whose Read is
revoked. **bob** is the control, who keeps Read on `person.ttl` in P1–P6.
Each run uses a fresh container `/alice/ch3/<run-id>/` holding `person.ttl`
(the fixture, which gets revoked) and `distractor.ttl` (appR keeps Read on it).
