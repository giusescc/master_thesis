"""The condition matrix: phase x config x variant. The single source for
the phase harness, ``exp:check`` and ``exp:compare``."""

from __future__ import annotations

CONFIGS = ("wac", "acp")
MIN_REPS = 10

VARIANTS: dict[str, tuple[str, ...]] = {
    "p1": ("direct",),
    "p2": ("proxyA", "proxyB"),
    "p3": ("default", "short", "unsub-bob", "unsub-anonymous", "unsub-alice"),
    "p4": ("a", "a-invalidate", "b"),
    "p5": ("naive", "403-aware"),
    "p6": ("rag",),
    "p7": ("cooperating", "non-cooperating"),
}


def conditions() -> list[tuple[str, str, str]]:
    return [(p, c, v) for p, vs in VARIANTS.items() for c in CONFIGS for v in vs]
