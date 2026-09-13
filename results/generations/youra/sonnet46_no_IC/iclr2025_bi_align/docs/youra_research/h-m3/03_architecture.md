# Architecture: h-m3

**Hypothesis:** Bidirectional alignment gap (Δ = LC_winrate − win_rate) is smaller for high-capability models (Kruskal-Wallis p < 0.05 across win_rate quartiles)
**Type:** MECHANISM — Statistical Analysis (no GPU, no model training)
**Date:** 2026-08-04

Applied: modular-single-responsibility pattern (h-m2 baseline)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (h-m2 PASSED)
**Status**: patterns found from base code
**Analyzed Path**: `docs/youra_research/h-m2/code/`
**Findings**: h-m2 uses 6-module layout — `data_loader.py` (load_and_validate), `spearman_analysis.py` (analysis functions), `visualizer.py` (save_all_figures + private helpers), `gate_evaluator.py` (evaluate_gate), `report_writer.py` (write_validation_report), `run_experiment.py` (main + constants). h-m3 mirrors this structure, swapping spearman residual analysis for Kruskal-Wallis quartile analysis.

---

## File Structure

```
docs/youra_research/h-m3/
  code/
    experiment_hm3.py     — main entry point + constants
    analysis.py           — KW + Dunn + Spearman + OLS analyses
    visualization.py      — 4 figure generation functions
    report.py             — 04_validation.md writer
  figures/                — output figures (pre-existing)
  04_validation.md        — Phase 4 output
```

---

## Modules

### DataLoader (reused from h-m2, inline in `experiment_hm3.py`)

**Dependencies**: pandas, numpy

```python
def load_data(csv_path: str) -> pd.DataFrame:
    """Load CSV, drop NaN, compute delta, assign quartile labels."""
    ...
    # Returns df with columns: win_rate, length_controlled_winrate,
    #   avg_length, delta, quartile (Q1–Q4)
```

Note: h-m2's `data_loader.load_and_validate` loads the same CSV but does not compute delta/quartiles. Rather than modifying shared code, h-m3 wraps it inline in experiment_hm3.py.

---

### Analysis (`code/analysis.py`)

**Dependencies**: scipy, scikit_posthocs, statsmodels, sklearn, numpy

```python
def run_kruskal_wallis(df: pd.DataFrame) -> dict:
    """Primary gate: KW H-test on delta across Q1–Q4.
    Returns: {H_stat, kw_p, epsilon_sq, quartile_medians, quartile_sizes}
    """
    ...

def run_dunn_posthoc(df: pd.DataFrame) -> pd.DataFrame:
    """Dunn post-hoc with Bonferroni. Returns 4x4 pairwise p-value DataFrame.
    Only called if kw_p < 0.05.
    """
    ...

def run_spearman(df: pd.DataFrame, n_bootstrap: int, random_state: int) -> dict:
    """Spearman rho(win_rate, delta) with bootstrap CI.
    Returns: {rho, p, ci_lower, ci_upper}
    NOTE: mathematical dependency present (delta contains -win_rate term).
    """
    ...

def run_ols_delta(df: pd.DataFrame) -> dict:
    """OLS: delta ~ win_rate_std + avg_length_std.
    Returns: {beta_win, beta_len, p_win, p_len, r_squared, ols_result}
    """
    ...

def evaluate_gate(kw_p: float, alpha: float, quartile_medians: dict) -> dict:
    """Returns: {passes_gate, monotonic_trend, gate_label}"""
    ...
```

---

### Visualization (`code/visualization.py`)

**Dependencies**: matplotlib, seaborn, pandas, numpy

```python
def save_all_figures(
    df: pd.DataFrame,
    kw_results: dict,
    dunn_matrix: pd.DataFrame,
    spearman_results: dict,
    figures_dir: str,
) -> list[str]:
    """Saves 4 figures, returns list of file paths."""
    ...

def _boxplot_delta_by_quartile(df, kw_p, dunn_matrix, out_path): ...
    # fig1_delta_boxplot.png: boxplot per quartile, KW p annotation, Dunn Q1vQ4 bracket

def _scatter_winrate_delta(df, spearman_results, out_path): ...
    # fig2_scatter_winrate_delta.png: scatter with quartile colors, LOWESS trend

def _dunn_heatmap(dunn_matrix, out_path): ...
    # fig3_dunn_heatmap.png: 4x4 pairwise Bonferroni p-values, log scale

def _bar_quartile_medians(kw_results, out_path): ...
    # fig4_quartile_median_bar.png: median delta per quartile with IQR error bars
```

---

### Report (`code/report.py`)

**Dependencies**: pathlib

```python
def write_validation_report(
    results: dict,
    figures_dir: str,
    output_path: str,
) -> None:
    """Writes 04_validation.md. results dict contains all analysis outputs."""
    ...
```

---

### Experiment Entry Point (`code/experiment_hm3.py`)

**Dependencies**: all modules above

```python
# Constants
CSV_PATH: str = "docs/data_AlpacaEval_2/weighted_alpaca_eval_gpt4_turbo_leaderboard.csv"
FIGURES_DIR: str = "docs/youra_research/h-m3/figures"
OUTPUT_PATH: str = "docs/youra_research/h-m3/04_validation.md"
N_BOOTSTRAP: int = 1000
RANDOM_STATE: int = 42
ALPHA: float = 0.05
N_QUARTILES: int = 4

def load_data(csv_path: str) -> pd.DataFrame: ...
    # inline: load + dropna + assert N>=200 + compute delta + qcut quartile

def main() -> None:
    """Orchestrates full h-m3 experiment pipeline."""
    ...
```

---

## External Dependencies (Base Hypothesis)

| Module | Usage | File Location |
|--------|-------|---------------|
| data pattern | reused inline (not imported) | `h-m2/code/data_loader.py` |
| constants pattern | CSV_PATH, RANDOM_STATE, ALPHA | `h-m2/code/run_experiment.py` |
| report pattern | write_validation_report signature | `h-m2/code/report_writer.py` |

Note: h-m3 does NOT import h-m2 code directly. Patterns are replicated to keep experiments self-contained.

---

## Data Flow

```
CSV_PATH
  → load_data()                          → df (with delta, quartile)
  → run_kruskal_wallis(df)               → kw_results
  → run_dunn_posthoc(df) [if p<0.05]    → dunn_matrix
  → run_spearman(df)                     → spearman_results
  → run_ols_delta(df)                    → ols_results
  → evaluate_gate(kw_p, alpha, medians)  → gate_result
  → save_all_figures(...)                → figure_paths
  → write_validation_report(...)         → 04_validation.md
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Project Setup | File structure, constants, load_data() in experiment_hm3.py, CSV verify | 6 | 1+1+2+2 |
| A-2 | Kruskal-Wallis Analysis | run_kruskal_wallis + epsilon-squared + quartile descriptives | 9 | 2+2+3+2 |
| A-3 | Dunn Post-Hoc | run_dunn_posthoc with Bonferroni via scikit-posthocs | 8 | 2+2+2+2 |
| A-4 | Secondary Analyses | run_spearman (bootstrap CI) + run_ols_delta (StandardScaler + statsmodels) | 10 | 2+3+3+2 |
| A-5 | Gate Evaluation | evaluate_gate: passes_gate + monotonic_trend check + assertion | 5 | 1+1+2+1 |
| A-6 | Visualization | 4 figures: boxplot, scatter, heatmap, bar chart | 12 | 3+2+4+3 |
| A-7 | Report Writer | write_validation_report → 04_validation.md with all sections | 8 | 2+1+3+2 |
| A-8 | Integration & Smoke Test | main() wiring, end-to-end run, assert gate, verify output files | 7 | 1+2+2+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-2, A-4, A-6], Low(4-8): [A-1, A-3, A-5, A-7, A-8]

**Total complexity**: 65 | **Task count**: 8 (within MECHANISM 6-12 range)

---

## Implementation Notes

- `scikit-posthocs` is the only new dependency vs h-m2 (install: `pip install scikit-posthocs`)
- All analyses are deterministic except bootstrap Spearman CI (seed=42)
- Kruskal-Wallis requires ≥5 per group — assert before running (N≈55/quartile satisfies this)
- Mathematical dependency caveat (Δ contains −win_rate) must appear in report for Spearman section
- Dunn post-hoc only runs if KW passes gate (conditional branch in main)
