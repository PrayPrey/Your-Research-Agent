# Architecture: h-c1

**Applied: single-file statistical experiment (incremental DV swap from h-m3)**

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: patterns found from base code
**Analyzed Path**: `docs/youra_research/h-m3/code/experiment_hm3.py`
**Findings**: Single-file experiment with 13 top-level functions and module-level constants. All logic is self-contained; no package structure. DV is `delta` throughout — h-c1 changes this to `length_controlled_winrate`.

---

## Overview

H-C1 is a DV-swap of H-M3. The only structural change is replacing `delta` with `length_controlled_winrate` as the dependent variable in `run_kruskal_wallis`, `run_dunn_posthoc`, `load_data`, and the figure functions. Architecture mirrors h-m3 exactly: one script, no packages.

**Reuse strategy**: Copy `experiment_hm3.py` → `experiment_hc1.py`, apply targeted substitutions, add H-C1-specific extras (comparison-with-H-M3 figure, bootstrap CI on Dunn p).

---

## File Structure

- `docs/youra_research/h-c1/code/experiment_hc1.py` — single experiment script
- `docs/youra_research/h-c1/figures/` — output directory (auto-created)
- `docs/youra_research/h-c1/04_validation.md` — written by script
- `docs/youra_research/h-c1/results_hc1.json` — written by script

---

## Module: experiment_hc1 (`code/experiment_hc1.py`)

**Dependencies**: pandas, numpy, scipy, scikit_posthocs, matplotlib, seaborn, pathlib, json, sys

Single-file, no imports from h-m3. Constants and functions listed below (interface only).

### Constants

```python
CSV_PATH: Path      # docs/data_AlpacaEval_2/weighted_alpaca_eval_gpt4_turbo_leaderboard.csv
FIGURES_DIR: Path   # docs/youra_research/h-c1/figures/
OUTPUT_PATH: Path   # docs/youra_research/h-c1/04_validation.md
RESULTS_PATH: Path  # docs/youra_research/h-c1/results_hc1.json
N_BOOTSTRAP: int    # 1000
RANDOM_STATE: int   # 42
ALPHA: float        # 0.05
N_QUARTILES: int    # 4
QUARTILE_LABELS: list[str]   # ['Q1','Q2','Q3','Q4']
MIN_N_CLEAN: int    # 200
MIN_GROUP_SIZE: int # 5
QUARTILE_PALETTE: dict       # {Q1: color, ..., Q4: color}
# H-M3 reference values for comparison figure
HM3_QUARTILE_MEDIANS_DELTA: dict   # {'Q1': 2.19, 'Q2': 2.96, 'Q3': 5.43, 'Q4': 0.91}
```

### Functions

```python
def load_data(csv_path: Path) -> pd.DataFrame:
    # Loads CSV, drops NA on win_rate/length_controlled_winrate/avg_length,
    # asserts N >= MIN_N_CLEAN, computes delta (kept for comparison figure),
    # adds quartile column via pd.qcut(win_rate, q=4, labels=QUARTILE_LABELS),
    # asserts all group sizes >= MIN_GROUP_SIZE.
    ...

def run_kruskal_wallis(df: pd.DataFrame) -> dict:
    # Groups by quartile on 'length_controlled_winrate' (NOT delta),
    # computes H, kw_p, epsilon_sq = (H - k + 1)/(N - k),
    # quartile_medians/means/sizes/q25/q75, monotonic_trend.
    # Returns dict with all stats.
    ...

def run_dunn_posthoc(df: pd.DataFrame) -> pd.DataFrame:
    # sp.posthoc_dunn(df, val_col='length_controlled_winrate',
    #                 group_col='quartile', p_adjust='bonferroni')
    # Returns 4x4 DataFrame of Bonferroni-corrected p-values.
    ...

def run_bootstrap_dunn_ci(
    df: pd.DataFrame,
    n_bootstrap: int,
    random_state: int
) -> dict:
    # NEW vs h-m3: Bootstrap 1000 resamples of Dunn Q1 vs Q4 p-value.
    # Returns {'ci_lower': float, 'ci_upper': float, 'bootstrap_p_values': list}
    ...

def run_spearman(df: pd.DataFrame, n_bootstrap: int, random_state: int) -> dict:
    # Spearman rho(win_rate, length_controlled_winrate) with bootstrap CI.
    # Secondary metric only.
    ...

def evaluate_gate(kw_p: float, dunn_q1q4_p: float, alpha: float,
                  quartile_medians: dict) -> dict:
    # Returns gate_label ('PASS'/'FAIL'), passes_gate bool,
    # both_conditions_met (kw_p < alpha AND dunn_q1q4_p < alpha),
    # monotonic_trend bool.
    # H-C1 gate requires BOTH conditions (unlike h-m3 which only needed KW).
    ...

def _boxplot_lc_by_quartile(df: pd.DataFrame, kw_results: dict) -> plt.Figure:
    # Boxplot of length_controlled_winrate per quartile with individual points.
    ...

def _dunn_heatmap(dunn_matrix: pd.DataFrame) -> plt.Figure:
    # 4x4 heatmap of Bonferroni-corrected p-values (green=significant, red=not).
    ...

def _bar_quartile_medians(kw_results: dict) -> plt.Figure:
    # Bar chart of quartile median LC_winrate with error bars.
    ...

def _gate_metrics_bar(kw_p: float, dunn_q1q4_p: float, alpha: float) -> plt.Figure:
    # Required: KW p and Dunn Q1 vs Q4 p vs 0.05 threshold.
    ...

def _comparison_hm3_hc1(kw_results: dict) -> plt.Figure:
    # NEW vs h-m3: Side-by-side quartile median bars for
    # Δ (H-M3, from HM3_QUARTILE_MEDIANS_DELTA constant) vs
    # LC_winrate (H-C1, from kw_results['quartile_medians']).
    ...

def save_all_figures(
    df: pd.DataFrame,
    kw_results: dict,
    dunn_matrix: pd.DataFrame | None,
    bootstrap_results: dict | None,
    figures_dir: Path
) -> list[Path]:
    # Saves all figures to figures_dir, returns list of saved paths.
    ...

def write_validation_report(
    kw_results: dict,
    gate_result: dict,
    dunn_matrix: pd.DataFrame | None,
    bootstrap_results: dict | None,
    spearman_results: dict,
    figure_paths: list[Path],
    output_path: Path
) -> None:
    # Writes 04_validation.md with all metrics, tables, figure refs.
    ...

def main() -> None:
    # Orchestrates: load_data → run_kruskal_wallis → evaluate_gate
    # → run_dunn_posthoc (if KW passes) → run_bootstrap_dunn_ci
    # → run_spearman → save_all_figures → write_validation_report
    # → write results_hc1.json → sys.exit(0 if passes_gate else 1)
    ...
```

---

## External Dependencies (Base Hypothesis)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| load_data pattern | direct copy, adapt `delta` → `length_controlled_winrate` | `h-m3/code/experiment_hm3.py:40-51` |
| run_kruskal_wallis pattern | direct copy, swap val column | `h-m3/code/experiment_hm3.py:55-92` |
| run_dunn_posthoc pattern | direct copy, swap val_col | `h-m3/code/experiment_hm3.py:115-121` |
| write_validation_report pattern | adapt for h-c1 metrics | `h-m3/code/experiment_hm3.py:294-431` |
| main pattern | direct copy, add bootstrap step | `h-m3/code/experiment_hm3.py:435-474` |

**Verified from**: `docs/youra_research/h-m3/code/experiment_hm3.py` (actual implementation)

**Key DV change locations** (lines in h-m3 that need updating in h-c1):
- `load_data`: remove `df['delta'] = ...` line (keep for comparison figure only), keep quartile assignment
- `run_kruskal_wallis`: change `df[...]['delta'].values` → `df[...]['length_controlled_winrate'].values`
- `run_dunn_posthoc`: change `val_col='delta'` → `val_col='length_controlled_winrate'`
- `evaluate_gate`: add `dunn_q1q4_p` parameter; gate now requires both KW AND Dunn Q1 vs Q4 < alpha
- All figure functions: update axis labels and titles from "Δ" to "LC_winrate"

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Project Setup | Create output dirs, copy h-m3 as base, configure constants | 4 | 1+1+1+1 |
| A-2 | Adapt load_data | Keep CSV/quartile logic; drop delta as primary DV (keep for comparison) | 5 | 1+1+2+1 |
| A-3 | Adapt run_kruskal_wallis | Swap DV from delta to length_controlled_winrate | 6 | 2+1+2+1 |
| A-4 | Adapt run_dunn_posthoc + evaluate_gate | val_col swap; add dual gate (KW AND Dunn Q1 vs Q4) | 7 | 2+2+2+1 |
| A-5 | Implement run_bootstrap_dunn_ci | NEW: 1000-resample bootstrap of Dunn Q1 vs Q4 p-value | 9 | 2+2+3+2 |
| A-6 | Adapt figure functions | Update labels; add _gate_metrics_bar and _comparison_hm3_hc1 | 8 | 2+1+3+2 |
| A-7 | Adapt write_validation_report | H-C1 metrics, dual gate table, bootstrap CI row, H-M3 comparison | 7 | 2+1+2+2 |
| A-8 | Wire main() + JSON output | Orchestrate new bootstrap step; update hypothesis_id to h-c1 | 5 | 1+1+2+1 |
| A-9 | End-to-end validation | Run script, verify gate output, check all figures saved | 6 | 1+2+2+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-5], Low(4-8): [A-1, A-2, A-3, A-4, A-6, A-7, A-8, A-9]
