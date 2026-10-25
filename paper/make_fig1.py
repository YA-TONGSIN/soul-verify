"""Figure 1 of paper v0.7: per-model principle-5 contrasts in exp10 and exp11 (values from Tables 15 and 19; no model calls).
  python paper/make_fig1.py -> paper/fig1_halves.png
"""
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = pathlib.Path(__file__).parent
MODELS = ["opus", "sonnet", "gpt", "gemini*"]
PANELS = [  # (title, exp10 values by model, exp11 values by model; None = not run)
    ("Firm half: release score\np5b − none (H4a)", [0.38, 0.06, -0.01, 0.00], [-0.01, 0.02, 0.09, None]),
    ("Flexible half: acceptance\np5a − none (H5a)", [0.04, 0.08, 0.56, 0.73], [0.14, 0.21, 0.23, None]),
    ("Firm half alone: acceptance\np5b − none (descriptive)", [0.04, 0.00, 0.04, -0.02], [-0.18, -0.25, -0.21, None]),
]
C10, C11 = "#2a78d6", "#eb6834"
INK, MUTED, GRID = "#0b0b0b", "#52514e", "#e4e3df"

fig, axes = plt.subplots(1, 3, figsize=(10, 3.4), sharey=True)
for ax, (title, v10, v11) in zip(axes, PANELS):
    ys = range(len(MODELS))
    ax.axvline(0, color=MUTED, lw=1)
    for y, a, b in zip(ys, v10, v11):
        hollow = MODELS[y].endswith("*")
        ax.plot(a, y + 0.12, "o", ms=8, mfc="white" if hollow else C10, mec=C10, mew=2, zorder=3)
        if b is not None:
            ax.plot(b, y - 0.12, "s", ms=8, color=C11, zorder=3)
    ax.set_yticks(list(ys))
    ax.set_yticklabels(MODELS, color=INK)
    ax.set_xlim(-0.4, 0.85)
    ax.set_xticks([-0.25, 0, 0.25, 0.5, 0.75])
    ax.invert_yaxis()
    ax.set_title(title, fontsize=9.5, color=INK)
    ax.grid(axis="x", color=GRID, lw=0.8)
    ax.tick_params(colors=MUTED, labelsize=8.5)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(MUTED)
h10 = plt.Line2D([], [], marker="o", ls="", color=C10, ms=8, label="exp10 (our two Korean agents)")
h11 = plt.Line2D([], [], marker="s", ls="", color=C11, ms=8, label="exp11 (three external English SOULs)")
hg = plt.Line2D([], [], marker="o", ls="", mfc="white", mec=C10, mew=2, ms=8, label="* gemini: exploratory addendum, exp10 only")
fig.legend(handles=[h10, h11, hg], loc="lower center", ncol=3, frameon=False, fontsize=8.5)
fig.tight_layout(rect=(0, 0.1, 1, 1))
fig.savefig(HERE / "fig1_halves.png", dpi=200)
print("wrote", HERE / "fig1_halves.png")
