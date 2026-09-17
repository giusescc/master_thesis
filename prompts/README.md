# Prompt archive

Every instruction given to the AI assistant on this project, verbatim and in the
order received, one numbered folder each.

Each folder contains:

| File | Contents |
|---|---|
| `prompt.md` | The instruction **exactly as given**, unedited. |
| `outcome.md` | Decisions taken in response, files produced, and the tool/version provenance at that moment. |

## Why this exists

Two reasons.

1. **Academic-integrity disclosure.** This thesis was produced with AI
   assistance. This archive documents precisely what was asked for, what was
   decided by the author, and what was generated — rather than leaving the
   division of labour implicit.
2. **Reproducibility.** Each `outcome.md` records the tool versions in force
   when that step ran, so a result can be traced to the exact environment that
   produced it.

## Division of labour, stated plainly

- The **research questions, experiment scope, and every design decision** were
  the author's, made by answering multiple-choice questions put by the assistant
  (see each `outcome.md` for the questions and the answers chosen).
- The **code, documentation and figures** were AI-generated to the author's
  specification, then run and verified against a live server.
- The **legal analysis is not AI-generated.** `RESULTS.md` deliberately stops at
  "bears on" hooks phrased as open questions; it draws no legal conclusions.
