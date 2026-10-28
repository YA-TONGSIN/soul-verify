# -*- coding: utf-8 -*-
"""Statistics of v1.2: sign-flip permutation and Holm imported unchanged from exp10 (analyze10.py, exact when <= 20 non-zero differences,
i.e. 4,096 sign patterns for 12 clusters); cluster bootstrap and the zero-event upper bound copied from v0.9/s2stats.py (10,000, seed 0).
Kept in v1.2 so that no v0.9 module shadows a v1.2 module on sys.path."""
import pathlib
import random
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.append(str(REPO / "runs" / "exp10_2026-10-25_prereg"))
from analyze10 import holm, signflip  # noqa: E402,F401


def boot_ci(cells, b=10_000, seed=0):
    c = [x for x in cells if x is not None]
    if not c:
        return None
    rng = random.Random(seed)
    ms = sorted(sum(rng.choice(c) for _ in c) / len(c) for _ in range(b))
    return ms[int(0.025 * b)], ms[int(0.975 * b) - 1]


def zero_event_upper(n, alpha=0.05):
    """One-sided (1-alpha) Clopper-Pearson upper bound when 0 events were seen in n trials."""
    return None if n <= 0 else 1 - alpha ** (1 / n)
