"""P6 agent memory: an index built from appR-readable data before the revoke;
what does it still retrieve and answer afterwards? (HYPOTHESES.md, P6)

Retrieval (top-k chunk ids, scores, from-revoked flags) is the primary,
deterministic measurement and goes into the categorical ``outcome``.
Generation is secondary: prompts and answers are logged verbatim, and their
correctness goes into ``metrics`` only, so answer variance is recorded, never
compared away.

    npm run exp:p6 [-- --config wac|acp] [--reps N] [--dry-run]
"""

from __future__ import annotations

import json

from ch3.lib import harness, scene
from ch3.lib.agents import response_record
from ch3.lib.env import CH3, STATE
from ch3.lib.memory import Memory, verify_models

K = 4
QUESTIONS = json.loads((CH3 / "fixtures" / "questions.json").read_text())["questions"]


def ask_all(log, memory: Memory, revoked: str, when: str) -> dict:
    out = {}
    for q in QUESTIONS:
        hits = memory.retrieve(q["question"], K)
        for h in hits:
            h["from_revoked"] = h["source"] == revoked
        log.write("retrieval", when=when, qid=q["id"], question=q["question"], k=K, hits=hits)
        gen = memory.generate(q["question"], hits)
        correct = any(m.lower() in gen["answer"].lower() for m in q["match"])
        log.write("generation", when=when, qid=q["id"], correct=correct, **gen)
        out[q["id"]] = {"ids": [h["id"].rsplit("/", 1)[-1] for h in hits],
                        "from_revoked": [h["from_revoked"] for h in hits],
                        "scores": [h["score"] for h in hits],
                        "answer_chunk_rank": next((i + 1 for i, h in enumerate(hits) if h["from_revoked"]
                                                   and any(m.lower() in h["text"].lower() for m in q["match"])), None),
                        "answer": gen["answer"], "correct": correct}
    return out


def run_one(log, config, variant, rep, rng) -> None:
    log.write("models", **verify_models())
    s = scene.build(log, config)
    stores = STATE / "stores"
    stores.mkdir(parents=True, exist_ok=True)
    memory = Memory(stores / f"{log.run_id}-p6-appr.sqlite")
    for url in (s.person, s.distractor):
        r = s.appr.get(url, headers={"accept": "text/turtle"})
        r.raise_for_status()
        chunks = memory.add(url, r.text)
        log.write("memory_add", agent="appr", source=url, status=r.status_code,
                  chunks=[{"id": c["id"], "text": c["text"]} for c in chunks])
    chunks_before = memory.count(s.person)
    before = ask_all(log, memory, s.person, "before_revoke")

    scene.revoke(log, s, s.person, [s.bob.web_id])
    direct = s.appr.get(s.person)
    log.write("direct_after", agent="appr", response=response_record(direct))
    after = ask_all(log, memory, s.person, "after_revoke")
    chunks_after, total_after = memory.count(s.person), memory.count()
    memory.close()

    log.summary(
        outcome={
            "chunks_from_revoked_before": chunks_before,
            "chunks_from_revoked_after": chunks_after,
            "chunks_total_after": total_after,
            "direct_after_status": direct.status_code,
            "after_topk_has_revoked": {q: any(v["from_revoked"]) for q, v in after.items()},
            "after_top1_from_revoked": {q: v["from_revoked"][0] for q, v in after.items()},
            "after_top1_ids": {q: v["ids"][0] for q, v in after.items()},
            "after_answer_chunk_rank": {q: v["answer_chunk_rank"] for q, v in after.items()},
            "retrieval_ids_same_before_after": all(before[q]["ids"] == after[q]["ids"] for q in after),
        },
        metrics={
            "generation_correct_before": sum(v["correct"] for v in before.values()),
            "generation_correct_after": sum(v["correct"] for v in after.values()),
            "answers_same_before_after": sum(before[q]["answer"] == after[q]["answer"] for q in after),
            "retrieval_scores_same_before_after": all(before[q]["scores"] == after[q]["scores"] for q in after),
        },
    )


if __name__ == "__main__":
    raise SystemExit(harness.main("p6", run_one))
