---
title: "Config: H-M2 Static Analysis Measurement — Pylint/Mypy on H-E1 and H-M1 Outputs"
hypothesis_id: h-m2
hypothesis_type: MECHANISM
phase: 3
date: "2026-08-05"
status: complete
---

# Configuration: H-M2

Applied: Standard argparse CLI pattern (stdlib, inherited from H-M1)
Applied: Hardcoded dict for figure specs (inherited from H-M1 visualizer pattern)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-M2 extends H-M1 outputs as data source)
**Status**: H-M1 config verified from `docs/youra_research/h-m1/03_config.md` (actual implementation confirmed)
**Config Files Found**: `docs/youra_research/h-m1/03_config.md` — module-level constants + argparse + hardcoded dicts
**Pattern Used**: Module-level constants (config.py) + argparse CLI + hardcoded dict for figures

---

## Inherited Configuration (Base Hypothesis)

### Config Constants (From Actual H-M1 Code)

```python
# From: experiments/h-m1/config.py (ACTUAL CODE — verified from h-m1/03_config.md)
SEED: int = 42
N_BOOTSTRAP: int = 10000
MCNEMAR_ALPHA: float = 0.05
CI_LEVEL: float = 0.95
RESULTS_DIR: str = "results/h-m1"         # H-M2 reads this as input
FIGURES_DIR: str = "docs/youra_research/h-m1/figures"

# H-M2 overrides:
# RESULTS_DIR input  → "results/h-e1" and "results/h-m1" (both consumed as input)
# RESULTS_DIR output → "results/h-m2"
# FIGURES_DIR        → "docs/youra_research/h-m2/figures"
```

**Verified from**: `docs/youra_research/h-m1/03_config.md` (actual implementation)

---

## A-4: Visualization and CLI Configuration [Complexity: 10, Budget: 2]

Applied: Standard argparse CLI pattern (stdlib)

### C-4-1: FigureConfig [Budget: 1]

```python
# experiments/h-m2/visualizer.py — top of file

import matplotlib as mpl

FIGURE_RC = {
    "figure.figsize": (8, 5),
    "figure.dpi":     150,
    "font.size":      11,
    "axes.titlesize": 13,
    "axes.labelsize": 11,
    "legend.fontsize": 10,
    "savefig.bbox":   "tight",
    "savefig.dpi":    150,
}

mpl.rcParams.update(FIGURE_RC)

OUTPUT_FORMAT: str = "png"

FIGURES_TO_GENERATE = {
    "figure1_pylint_scores_distribution": True,   # MANDATORY
    "figure2_mypy_error_counts":          True,   # MANDATORY
    "figure3_score_vs_pass_rate":         True,
    "figure4_condition_comparison":       True,
}

# Figure 1: pylint score distribution (violin/box per condition)
FIG1_CONFIG = {
    "filename": "figure1_pylint_scores_distribution.png",
    "title":    "Pylint Score Distribution by Condition (H-E1 vs H-M1 Execution vs H-M1 Pylint)",
    "xlabel":   "Condition",
    "ylabel":   "Pylint Score (0–10)",
    "ylim":     (0.0, 10.5),
    "plot_type": "violin",   # violin shows full distribution for static scores
    "colors": {
        "baseline":  "#4C72B0",
        "pylint":    "#55A868",
        "execution": "#C44E52",
    },
}

# Figure 2: mypy error count distribution
FIG2_CONFIG = {
    "filename": "figure2_mypy_error_counts.png",
    "title":    "Mypy Error Count per Problem by Condition",
    "xlabel":   "Condition",
    "ylabel":   "Mypy Errors per Problem",
    "plot_type": "box",
    "colors": {
        "baseline":  "#4C72B0",
        "pylint":    "#55A868",
        "execution": "#C44E52",
    },
}

# Figure 3: pylint score vs pass@1 scatter
FIG3_CONFIG = {
    "filename": "figure3_score_vs_pass_rate.png",
    "title":    "Pylint Score vs Pass@1 (per Problem)",
    "xlabel":   "Pylint Score",
    "ylabel":   "Passed Tests (0 or 1)",
    "alpha":    0.3,
    "color":    "#4C72B0",
    "jitter":   0.05,   # Non-standard: jitter y-axis to separate 0/1 clusters
}

# Figure 4: condition comparison bar chart (mean pylint score per condition)
FIG4_CONFIG = {
    "filename": "figure4_condition_comparison.png",
    "title":    "Mean Pylint Score and Mypy Errors by Condition",
    "bar_width": 0.35,
    "colors": {
        "baseline":  "#4C72B0",
        "pylint":    "#55A868",
        "execution": "#C44E52",
    },
    "show_ci": True,   # 95% bootstrap CI error bars
}
```

### C-4-2: Experiment CLI Config [Budget: 1]

```python
# experiments/h-m2/run_experiment.py

import argparse

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="H-M2: Static analysis (pylint/mypy) measurement on H-E1 and H-M1 outputs"
    )

    # --- Input sources ---
    parser.add_argument("--h-e1-results", type=str, default="results/h-e1",
                        help="Path to H-E1 results directory")
    parser.add_argument("--h-m1-results", type=str, default="results/h-m1",
                        help="Path to H-M1 results directory")

    # --- Output ---
    parser.add_argument("--output-dir",  type=str, default="results/h-m2")
    parser.add_argument("--figures-dir", type=str,
                        default="docs/youra_research/h-m2/figures")

    # --- Bootstrap ---
    parser.add_argument("--seed",        type=int, default=42)
    parser.add_argument("--n-bootstrap", type=int, default=10000)

    # --- Pylint/Mypy options ---
    # No custom .pylintrc — use pylint defaults
    # Mypy flags: --ignore-missing-imports --no-strict-optional (lenient for generated stubs)
    parser.add_argument("--mypy-flags", type=str,
                        default="--ignore-missing-imports --no-strict-optional",
                        help="Extra mypy flags (space-separated)")

    # --- Execution control ---
    parser.add_argument("--conditions", type=str, nargs="+",
                        default=["baseline", "pylint", "execution"],
                        choices=["baseline", "pylint", "execution"],
                        help="Which conditions to analyze")
    parser.add_argument("--skip-figures", action="store_true", default=False)
    parser.add_argument("--log-level", type=str, default="INFO",
                        choices=["DEBUG", "INFO", "WARNING", "ERROR"])

    args = parser.parse_args()

    if args.n_bootstrap < 100:
        parser.error("--n-bootstrap must be >= 100")

    return args


# Output directory structure
# results/h-m2/
#   raw/
#     {condition}_{benchmark}_{model_tag}_pylint.jsonl   # per-problem pylint scores
#     {condition}_{benchmark}_{model_tag}_mypy.jsonl     # per-problem mypy error counts
#   metrics.json                                          # aggregated statistics
#   figures/                                              # same as --figures-dir
```

### YAML Schema

```yaml
# experiments/h-m2/config.yaml (documentation reference — not loaded at runtime)
experiment:
  seed: 42
  n_bootstrap: 10000
  conditions: [baseline, pylint, execution]

paths:
  h_e1_results: "results/h-e1"
  h_m1_results: "results/h-m1"
  output_dir:   "results/h-m2"
  figures_dir:  "docs/youra_research/h-m2/figures"

static_analysis:
  pylint_rc:  null          # use pylint defaults (no custom .pylintrc)
  mypy_flags: "--ignore-missing-imports --no-strict-optional"

figures:
  dpi:    150
  format: "png"
  figsize: [8, 5]
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-4-1 | FigureConfig | FIGURE_RC rcParams, FIG1-4 spec dicts, output format PNG 150 DPI |
| C-4-2 | Experiment CLI | argparse defaults, output directory structure, validation |

---

## Summary

| Subtask | Format | Key Defaults |
|---------|--------|--------------|
| C-4-1 | hardcoded dict | figsize=(8,5), dpi=150, png, 4 figures, violin for pylint dist |
| C-4-2 | argparse + YAML ref | --seed=42, --n-bootstrap=10000, mypy lenient flags, no .pylintrc |

**Validation rules enforced in parse_args():**
- `n_bootstrap >= 100`
- `conditions subset of {"baseline", "pylint", "execution"}`

**H-M1 overrides:**
- `RESULTS_DIR` input: "results/h-e1" + "results/h-m1" (both consumed)
- `RESULTS_DIR` output: "results/h-m1" -> "results/h-m2"
- `FIGURES_DIR`: "docs/youra_research/h-m1/figures" -> "docs/youra_research/h-m2/figures"
- No model config (h-m2 is CPU-only static analysis, no LLM calls)
