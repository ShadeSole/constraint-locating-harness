"""Poster figures for the AAAI-27 Undergraduate Consortium (docs/aaai27/poster_outline.md, Figures 3, 4 and 5).

Every number is read from committed result files; nothing is typed in by hand:
  docs/item75/evaluation.json, docs/item76/evaluation.json   suites C, L1, L2 on the generated faults (items 75, 76)
  docs/item75/stats.json, docs/item76/stats.json             random equal-size suites, 200 draws (item 78)
  docs/item85/cp_regression_evaluation.json, cp_regression.jsonl, docs/item76/suite_L1.json   real-bug case (item 85)
Needs matplotlib (pip install matplotlib); run from the repository root:
  python scripts/aaai27_figures.py            -> docs/aaai27/figures/fig{3,4,5}_*.png (300 dpi) and .pdf (vector)
Colours: reference palette of the dataviz method, validated with its validate_palette.js (blue/orange and blue/aqua
pairs pass; aqua is below 3:1 contrast, so every aqua segment carries a visible label)."""
import json, os, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
OUT = os.path.join(ROOT, "docs", "aaai27", "figures")
os.makedirs(OUT, exist_ok=True)

BLUE, ORANGE, AQUA, GREY = "#2a78d6", "#eb6834", "#1baf7a", "#b9b7b0"
INK, INK2, GRID, SURFACE, TINT = "#0b0b0b", "#52514e", "#e4e2dc", "#ffffff", "#e8f0fb"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 15, "axes.edgecolor": GRID, "axes.labelcolor": INK2,
                     "xtick.color": INK2, "ytick.color": INK2, "text.color": INK, "axes.titleweight": "bold",
                     "axes.titlesize": 17, "figure.facecolor": SURFACE, "axes.facecolor": SURFACE,
                     "savefig.facecolor": SURFACE})

load = lambda p: json.load(open(os.path.join(ROOT, p), encoding="utf-8"))
PROGRAMS = [("textwrap", "docs/item75"), ("configparser", "docs/item76")]


def save(fig, name):
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(OUT, f"{name}.{ext}"), dpi=300, bbox_inches="tight")
    plt.close(fig)
    print("wrote", os.path.join("docs", "aaai27", "figures", name + ".{png,pdf}"))


def style(ax):
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.tick_params(length=0)


def fig4():
    """Correct diagnoses and wrong causes named, per suite, per program (grouped bars, two panels)."""
    fig, axes = plt.subplots(1, 2, figsize=(15, 6.2), sharey=False)
    for ax, (prog, folder) in zip(axes, PROGRAMS):
        ev, st = load(f"{folder}/evaluation.json"), load(f"{folder}/stats.json")
        size = ev["suite_sizes"]
        rows = [(f"Covering only\n{size['C']} tests", ev["summary"]["C/all"]["correct"],
                 ev["summary"]["C/all"]["misleading"], False),
                (f"One-fault\nlocating\n{size['L1']} tests", ev["summary"]["L1/all"]["correct"],
                 ev["summary"]["L1/all"]["misleading"], False),
                (f"Two-fault\nlocating\n{size['L2']} tests", ev["summary"]["L2/all"]["correct"],
                 ev["summary"]["L2/all"]["misleading"], False),
                (f"Random, same size\n(mean of {st['random_draws']})", st["metrics"]["per_mutant/correct"]["mean"],
                 st["metrics"]["per_mutant/misleading"]["mean"], True)]
        w = 0.36
        for i, (label, good, bad, is_mean) in enumerate(rows):
            for dx, val, col in ((-w / 2 - 0.02, good, BLUE), (w / 2 + 0.02, bad, ORANGE)):
                ax.bar(i + dx, val, width=w, color=col, edgecolor=SURFACE, linewidth=2,
                       hatch="//" if is_mean else None, zorder=2)
                txt = f"{val:.1f}" if is_mean else f"{val:d}"
                ax.text(i + dx, val + 1.2, txt, ha="center", va="bottom", fontsize=14, color=INK)
        ax.set_xticks(range(len(rows)), [r[0] for r in rows], fontsize=13)
        ax.set_title(f"{prog}: {ev['config_dependent']} configuration-dependent bugs", loc="left")
        ax.yaxis.grid(True, color=GRID, linewidth=1, zorder=0)
        style(ax)
        ax.set_ylim(0, max(max(r[1], r[2]) for r in rows) * 1.18 + 2)
    axes[0].set_ylabel("number of bugs")
    handles = [plt.Rectangle((0, 0), 1, 1, color=BLUE), plt.Rectangle((0, 0), 1, 1, color=ORANGE)]
    fig.legend(handles, ["diagnosed correctly", "named a wrong cause"], loc="upper center", ncol=2, frameon=False,
               bbox_to_anchor=(0.5, 1.04), fontsize=15)
    fig.text(0.01, -0.04, "Remaining bugs: reported as \"no single explanation fits\", or no test failed. "
             "Hatched bars: mean over random suites. Source: PROJECT_NOTES items 75, 76, 78 (reproduced locally).",
             fontsize=11, color=INK2)
    fig.tight_layout()
    save(fig, "fig4_diagnoses")


def fig3():
    """Shape of the generated faults: does each failure set fit the 'one or two faulty pairs' model?"""
    fig, ax = plt.subplots(figsize=(15, 3.6))
    cats = [("exactly one faulty pair", "pair", BLUE), ("exactly two faulty pairs", "two_pairs", AQUA),
            ("wider than two pairs", "other", GREY)]
    for y, (prog, folder) in enumerate(PROGRAMS):
        ev = load(f"{folder}/evaluation.json")
        types, n = ev["ground_truth_types"], ev["config_dependent"]
        left = 0.0
        for name, key, col in cats:
            k = types.get(key, 0)
            share = k / n
            if k:
                ax.barh(y, share, left=left, color=col, edgecolor=SURFACE, linewidth=2, height=0.6)
            mid = left + share / 2
            if share > 0.06:
                ax.text(mid, y, str(k), ha="center", va="center", fontsize=15,
                        color=SURFACE if col == BLUE else INK, fontweight="bold")
            else:  # too narrow to label inside: name it in words just below the bar's start
                ax.text(left, y + 0.42, f"{name}: {k}", fontsize=13, color=INK2, ha="left", va="center")
            left += share
        ax.text(-0.01, y, f"{prog}\n({n} bugs)", ha="right", va="center", fontsize=15)
    ax.set_xlim(0, 1)
    ax.set_ylim(-0.6, 1.75)
    ax.invert_yaxis()
    ax.set_yticks([])
    ax.set_xticks([0, 0.25, 0.5, 0.75, 1], ["0%", "25%", "50%", "75%", "100%"])
    ax.xaxis.grid(True, color=GRID, linewidth=1, zorder=0)
    ax.set_axisbelow(True)
    style(ax)
    handles = [plt.Rectangle((0, 0), 1, 1, color=c) for _, _, c in cats]
    ax.legend(handles, [c[0] for c in cats], loc="upper center", ncol=3, frameon=False, bbox_to_anchor=(0.5, 1.32),
              fontsize=14)
    fig.text(0.01, -0.06, "Failure set = every valid configuration on which the generated bug fails. "
             "Source: PROJECT_NOTES items 75, 76 (reproduced locally).", fontsize=11, color=INK2)
    save(fig, "fig3_fault_shapes")


def named_pair(model, suite_file, failing):
    from cla_harness.io import load_model
    from cla_harness.core import valid_configurations, feasible_interactions, contains_interaction
    configs = valid_configurations(*load_model(os.path.join(ROOT, model)))
    key = lambda c: tuple(sorted(c.items()))
    index = {key(c): k for k, c in enumerate(configs)}
    suite = [index[key(c)] for c in load(suite_file)["suite"]]
    rows = [r for r, k in enumerate(suite) if k in failing]
    for p in feasible_interactions(configs, 2):
        if [r for r, k in enumerate(suite) if contains_interaction(configs[k], p)] == rows:
            return sorted(p), len(configs)
    return None, len(configs)


def fig5():
    """Real-bug case study: configparser gh-130941 with the fix's regression-test input."""
    ev = load("docs/item85/cp_regression_evaluation.json")
    run = json.loads(open(os.path.join(ROOT, "docs/item85/cp_regression.jsonl"), encoding="utf-8").readline())
    pair, total = named_pair("docs/item76/configparser_model.json", "docs/item76/suite_L1.json", set(run["failing"]))
    outcome = {p["suite"]: p["outcome"] for p in ev["per_mutant"]}
    sizes = ev["suite_sizes"]
    pair_txt = " + ".join(f"{a} = {'True' if v == 'T' else v}" for a, v in pair)
    text = {"missed": ("Missed", "no test failed"),
            "flagged": ("Caught", "\"no single explanation fits\""),
            "misleading": ("Caught and named", pair_txt)}
    rows = [("Covering only", sizes["C"], *text[outcome["C"]], False),
            ("One-fault locating", sizes["L1"], *text[outcome["L1"]], True),
            ("Two-fault locating", sizes["L2"], *text[outcome["L2"]], False)]
    fig, ax = plt.subplots(figsize=(15, 5.4))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.text(0, 0.97, "Real bug: CPython gh-130941, fixed April 2025", fontsize=19, fontweight="bold", va="top")
    ax.text(0, 0.84, "\"Fix configparser parsing values with allow_no_value and interpolation set\"  ·  "
            f"{run['n_fail']:,} of {total:,} configurations fail", fontsize=14, color=INK2, va="top")
    cols = [0.0, 0.30, 0.42]
    for x, head in zip(cols, ["Test suite", "Tests", "Result"]):
        ax.text(x + 0.01, 0.66, head, fontsize=13, color=INK2, fontweight="bold", va="center")
    ax.plot([0, 1], [0.61, 0.61], color=GRID, linewidth=1.5)
    y = 0.52
    for name, n, verdict, detail, highlight in rows:
        weight = "bold" if highlight else "normal"
        if highlight:  # two lines: the verdict, then the named settings on their own line
            ax.add_patch(FancyBboxPatch((0.0, y - 0.15), 1.0, 0.21, boxstyle="round,pad=0,rounding_size=0.01",
                                        facecolor=TINT, edgecolor=BLUE, linewidth=2))
            ax.text(0.01, y - 0.045, name, fontsize=16, va="center", fontweight=weight)
            ax.text(0.31, y - 0.045, str(n), fontsize=16, va="center", fontweight=weight)
            ax.text(0.43, y, verdict + " the cause:", fontsize=16, va="center", fontweight=weight)
            ax.text(0.43, y - 0.09, detail, fontsize=15, va="center", fontweight=weight, family="DejaVu Sans Mono")
            y -= 0.27
        else:
            ax.text(0.01, y, name, fontsize=16, va="center")
            ax.text(0.31, y, str(n), fontsize=16, va="center")
            ax.text(0.43, y, f"{verdict}: {detail}", fontsize=16, va="center")
            y -= 0.17
    ax.text(0, -0.08, "The named pair is the one in the official bug report. Input: the regression test from the fix "
            "(our original inputs never triggered this bug). In our test the failure also needs '=' as a separator, "
            "because of how that input is written.\nSource: PROJECT_NOTES item 85 (cloud run; reproduce with "
            "reproduce.py realbug).", fontsize=11, color=INK2, va="top")
    save(fig, "fig5_real_bug")


if __name__ == "__main__":
    fig3()
    fig4()
    fig5()
