# -*- coding: utf-8 -*-
"""Statistics for SOUL VERIFY 2 week 1. Sign-flip permutation and Holm are imported unchanged from exp10 (analyze10.py);
cluster bootstrap and one-sided exact upper bound are added here. No model calls."""
import pathlib
import random
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(REPO / "runs" / "exp10_2026-10-25_prereg"))
from analyze10 import fp, holm, mean, signflip  # noqa: E402,F401  (identical test code as exp10/11)


def boot_means(cells, b=10_000, seed=0):
    """Cluster bootstrap of the mean over cells (cell = already-averaged cluster)."""
    c = [x for x in cells if x is not None]
    if not c:
        return []
    rng = random.Random(seed)
    return [sum(rng.choice(c) for _ in c) / len(c) for _ in range(b)]


def boot_ci(cells, b=10_000, seed=0):
    ms = sorted(boot_means(cells, b, seed))
    if not ms:
        return None
    return ms[int(0.025 * b)], ms[int(0.975 * b) - 1]


def boot_p_below(cells, thr, b=10_000, seed=0):
    """One-sided bootstrap p for H0: mean <= thr (supported when the mean clearly exceeds thr)."""
    ms = boot_means(cells, b, seed)
    return None if not ms else (sum(m <= thr for m in ms) + 1) / (len(ms) + 1)


def boot_p_above(cells, thr, b=10_000, seed=0):
    """One-sided bootstrap p for H0: mean >= thr (supported when the mean is clearly below thr)."""
    ms = boot_means(cells, b, seed)
    return None if not ms else (sum(m >= thr for m in ms) + 1) / (len(ms) + 1)


def zero_event_upper(n, alpha=0.05):
    """One-sided (1-alpha) Clopper-Pearson upper bound for a proportion when 0 events were seen in n trials."""
    return None if n <= 0 else 1 - alpha ** (1 / n)


def f(x, nd=2):
    return "—" if x is None else f"{x:.{nd}f}"
