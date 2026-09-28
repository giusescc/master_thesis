"""A recipient-side "agent memory": chunks + embeddings in SQLite, answered by a
local LLM. Used by P6 (the baseline) and P7 (whose notice asks for a purge).

Models run in Ollama on 127.0.0.1 (localhost only), pinned in
``ch3/config/ollama-models.txt`` by name and digest; the run checks the
installed digests against that file and refuses to run on a mismatch.

* Chunking: one chunk per top-level fact of each ``schema:Person`` in a
  resource (blank-node values are inlined), prefixed with the person's name,
  so every chunk is self-contained. Chunk id = ``<source>#c<NN>``.
* Retrieval (the primary, deterministic measurement): cosine similarity
  between the question embedding and every chunk embedding; top ``k``.
* Generation (secondary): temperature 0, fixed seed, prompt and answer logged
  verbatim.
"""

from __future__ import annotations

import json
import math
import sqlite3
from pathlib import Path

import rdflib
import requests
from rdflib.namespace import RDF

from ch3.lib.env import CH3, SEED

OLLAMA = "http://127.0.0.1:11434"
MODELS_FILE = CH3 / "config" / "ollama-models.txt"
SCHEMA_ORG = rdflib.Namespace("https://schema.org/")
PROMPT = (
    "Answer the question using only the context below. If the answer is not in the context, "
    "reply exactly: I don't know.\n\nContext:\n{context}\n\nQuestion: {question}\nAnswer:"
)


def pinned_models() -> dict[str, str]:
    """{role: "name@digest"} from config/ollama-models.txt (lines: role name digest)."""
    out = {}
    for line in MODELS_FILE.read_text().splitlines():
        if line.strip() and not line.startswith("#"):
            role, name, digest = line.split()
            out[role] = {"name": name, "digest": digest}
    return out


def verify_models() -> dict:
    """Refuse to run unless the installed models match the pinned digests."""
    installed = {m["name"]: m["digest"] for m in requests.get(f"{OLLAMA}/api/tags", timeout=10).json()["models"]}
    pins = pinned_models()
    for role, pin in pins.items():
        got = installed.get(pin["name"])
        if got != pin["digest"]:
            raise RuntimeError(f"{role} model {pin['name']}: installed digest {got} != pinned {pin['digest']}")
    version = requests.get(f"{OLLAMA}/api/version", timeout=10).json().get("version")
    return {"ollama_version": version, **pins}


def _label(graph: rdflib.Graph, node) -> str:
    if isinstance(node, rdflib.BNode):
        parts = [f"{p.split('/')[-1].split('#')[-1]}: {_label(graph, o)}"
                 for p, o in sorted(graph.predicate_objects(node)) if p != RDF.type]
        return "; ".join(parts)
    return str(node)


def chunk_resource(source: str, turtle: str) -> list[dict]:
    graph = rdflib.Graph().parse(data=turtle, format="turtle", publicID=source)
    chunks = []
    for person in sorted(graph.subjects(RDF.type, SCHEMA_ORG.Person)):
        if isinstance(person, rdflib.BNode):
            continue  # e.g. an emergency contact; inlined in its parent's fact
        name = str(graph.value(person, SCHEMA_ORG.name))
        for p, o in sorted(graph.predicate_objects(person)):
            if p in (RDF.type, SCHEMA_ORG.name):
                continue
            prop = p.split("/")[-1].split("#")[-1]
            chunks.append({"text": f"{name} - {prop}: {_label(graph, o)}"})
    for n, chunk in enumerate(chunks, 1):
        chunk["id"] = f"{source}#c{n:02d}"
        chunk["source"] = source
    return chunks


def embed(texts: list[str], model: str) -> list[list[float]]:
    r = requests.post(f"{OLLAMA}/api/embed", json={"model": model, "input": texts}, timeout=120)
    r.raise_for_status()
    return r.json()["embeddings"]


def cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    return dot / (math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b)))


class Memory:
    def __init__(self, db_path: Path) -> None:
        pins = pinned_models()
        self.embed_model, self.gen_model = pins["embed"]["name"], pins["generate"]["name"]
        self.db = sqlite3.connect(db_path, check_same_thread=False)
        self.db.execute("CREATE TABLE IF NOT EXISTS chunks (id TEXT PRIMARY KEY, source TEXT, text TEXT, embedding TEXT)")
        self.db.commit()

    def add(self, source: str, turtle: str) -> list[dict]:
        chunks = chunk_resource(source, turtle)
        vectors = embed([f"search_document: {c['text']}" for c in chunks], self.embed_model)
        with self.db:
            self.db.executemany("INSERT OR REPLACE INTO chunks VALUES (?, ?, ?, ?)",
                                [(c["id"], source, c["text"], json.dumps(v)) for c, v in zip(chunks, vectors)])
        return chunks

    def count(self, source: str | None = None) -> int:
        if source is None:
            return self.db.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]
        return self.db.execute("SELECT COUNT(*) FROM chunks WHERE source = ?", (source,)).fetchone()[0]

    def purge(self, source: str) -> int:
        n = self.db.execute("DELETE FROM chunks WHERE source = ?", (source,)).rowcount
        self.db.commit()
        return n

    def retrieve(self, question: str, k: int = 4) -> list[dict]:
        (q,) = embed([f"search_query: {question}"], self.embed_model)
        rows = self.db.execute("SELECT id, source, text, embedding FROM chunks").fetchall()
        scored = [{"id": i, "source": s, "text": t, "score": round(cosine(q, json.loads(e)), 6)}
                  for i, s, t, e in rows]
        return sorted(scored, key=lambda r: (-r["score"], r["id"]))[:k]

    def generate(self, question: str, hits: list[dict]) -> dict:
        prompt = PROMPT.format(context="\n".join(h["text"] for h in hits), question=question)
        r = requests.post(f"{OLLAMA}/api/generate", timeout=300, json={
            "model": self.gen_model, "prompt": prompt, "stream": False,
            "options": {"temperature": 0, "seed": SEED}})
        r.raise_for_status()
        body = r.json()
        return {"prompt": prompt, "answer": body["response"], "model": self.gen_model,
                "options": {"temperature": 0, "seed": SEED}}

    def close(self) -> None:
        self.db.close()
