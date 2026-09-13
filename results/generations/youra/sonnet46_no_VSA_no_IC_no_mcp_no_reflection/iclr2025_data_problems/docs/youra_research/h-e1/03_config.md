# Configuration: H-E1 — Corpus Curation Generalization Balance (EXISTENCE PoC)

**Date:** 2026-08-31
**Author:** yoon303@ust.ac.kr
**Hypothesis Type:** EXISTENCE (PoC)

Applied: Single-Source-of-Truth Config pattern — all constants in config.py, no magic numbers in implementation files.

---

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** green-field — no existing codebase. Serena MCP skipped per green-field rule.
**Config Files Found:** None — new config
**Pattern Used:** hardcoded module-level variables (no dataclass needed; evaluation-only, no training hyperparameter sweep)

---

## Full `config.py`

```python
# code/config.py
# H-E1: Corpus Curation Generalization Balance — EXISTENCE PoC
# All constants here. No magic numbers elsewhere.

# ── Model IDs & Revisions ──────────────────────────────────────────────────
PYTHIA_ID       = "EleutherAI/pythia-6.9b"
PYTHIA_REVISION = "step143000"
PYTHIA_TOKENS   = 143_000 * 2_097_152   # ~300B

OLMO_ID         = "allenai/OLMo-7B-hf"
OLMO_REVISION   = "step149531"           # verified at runtime by precondition_check
OLMO_TOKENS     = 149_531 * 2_000_000   # ~300B; ponytail: approximate, precondition_check verifies

# ── Evaluation Tasks ───────────────────────────────────────────────────────
TASKS        = ["mmlu", "hellaswag", "arc_easy", "arc_challenge"]
FEWSHOT_MAP  = {"mmlu": 5, "hellaswag": 0, "arc_easy": 25, "arc_challenge": 25}

# ── Token Matching ─────────────────────────────────────────────────────────
TARGET_TOKENS   = 300e9
TOKEN_TOLERANCE = 0.10   # ±10%

# ── Statistical Thresholds ─────────────────────────────────────────────────
RATIO_THRESHOLD   = 0.02   # primary: olmo_ratio - pythia_ratio must exceed this
P_THRESHOLD       = 0.05   # one-sided bootstrap p-value
COHENS_D_THRESHOLD = 0.2   # minimum effect size
ARC_DELTA_P_THRESHOLD = 0.10  # secondary criterion

# ── Bootstrap ──────────────────────────────────────────────────────────────
BOOTSTRAP_N = 1000
SEED        = 42

# ── Paths ──────────────────────────────────────────────────────────────────
RESULTS_DIR = "results"
FIGURES_DIR = "docs/youra_research/h-e1/figures"

# ── Figure Styling (E5-C1) ─────────────────────────────────────────────────
# Wong colorblind-safe palette
COLOR_PYTHIA = "#0072B2"   # blue
COLOR_OLMO   = "#E69F00"   # orange

FIG_STYLE = {
    "figsize":   (10, 6),
    "dpi":        300,
    "font_size":  12,
    "title_size": 14,
    "label_size": 11,
    "tick_size":  10,
    "legend_fontsize": 10,
    "savefig_format": "png",
    "savefig_bbox_inches": "tight",
}

# Heatmap gets taller to fit 57 MMLU subjects
HEATMAP_FIGSIZE = (8, 18)

# ── Figure Annotation (E5-C2) ──────────────────────────────────────────────
# Bootstrap histogram threshold lines
BOOTSTRAP_VLINE_ZERO = {
    "color":     "#CC79A7",   # Wong pink — null hypothesis boundary
    "linestyle": "--",
    "linewidth": 1.5,
    "label":     "null (0)",
    "zorder":    3,
}

BOOTSTRAP_VLINE_THRESHOLD = {
    "color":     "#D55E00",   # Wong vermillion — effect threshold
    "linestyle": "-.",
    "linewidth": 1.5,
    "label":     f"threshold ({RATIO_THRESHOLD})",
    "zorder":    3,
}

# CI error bar style for ratio_delta bar chart
ERRORBAR_STYLE = {
    "fmt":     "none",
    "ecolor":  "#333333",
    "elinewidth": 1.5,
    "capsize":  5,
    "capthick": 1.5,
    "zorder":   4,
}
```

---

## E5-C1: Figure Layout Config [Complexity: 2, Budget: 2]

**Applied**: Wong palette (colorblind-safe), matplotlib explicit kwargs — no rcParams mutation to avoid global side effects.

```python
# Kwargs passed directly to fig/ax calls in figures.py

BAR_KWARGS_PYTHIA = {"color": COLOR_PYTHIA, "label": "Pythia-6.9B", "alpha": 0.85}
BAR_KWARGS_OLMO   = {"color": COLOR_OLMO,   "label": "OLMo-7B",     "alpha": 0.85}

SAVEFIG_KWARGS = {
    "dpi":         FIG_STYLE["dpi"],
    "bbox_inches": FIG_STYLE["savefig_bbox_inches"],
    "format":      FIG_STYLE["savefig_format"],
}

# Usage in figures.py:
# fig, ax = plt.subplots(figsize=FIG_STYLE["figsize"])
# ax.bar(x - 0.2, pythia_vals, width=0.4, **BAR_KWARGS_PYTHIA)
# ax.bar(x + 0.2, olmo_vals,   width=0.4, **BAR_KWARGS_OLMO)
# ax.tick_params(labelsize=FIG_STYLE["tick_size"])
# ax.set_xlabel("Task", fontsize=FIG_STYLE["label_size"])
# fig.savefig(path, **SAVEFIG_KWARGS)
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| E5-C1 | Figure layout config | figsize, dpi, font sizes, color palette, output format |
| E5-C2 | Figure annotation config | Threshold line styles, CI error bar style |

---

## E5-C2: Figure Annotation Config [Complexity: 2, Budget: 2]

**Applied**: Distinct line styles (dashed vs dash-dot) so lines are distinguishable in greyscale print too.

```python
# Bootstrap histogram annotation — usage in figures.py:
# ax.axvline(0,              **BOOTSTRAP_VLINE_ZERO)
# ax.axvline(RATIO_THRESHOLD, **BOOTSTRAP_VLINE_THRESHOLD)
# ax.legend(fontsize=FIG_STYLE["legend_fontsize"])

# Ratio/delta CI error bars — usage in figures.py:
# ax.errorbar(x_positions, means, yerr=ci_half_widths, **ERRORBAR_STYLE)
```

All annotation constants live in `config.py` under the `E5-C2` block above — no separate file needed.
