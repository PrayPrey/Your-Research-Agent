# Architecture: H-M2
# Differential Rank Stability — Fairness vs. Adversarial Robustness

**Date:** 2026-08-20
**Hypothesis Type:** MECHANISM (EXISTENCE-tier PoC)
**Applied:** flat single-directory module pattern (no sub-packages)

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis
**Status:** Patterns found from base code (h-m1)
**Analyzed Path:** `docs/youra_research/h-m1/code/`
**Findings:** Four flat files — `data.py`, `analysis.py`, `visualize.py`, `config.py` — plus `run_experiment.py` entry point. Imports via `importlib.util` for cross-hypothesis references. Paths resolved via `Path(__file__).parent`. No sub-packages. `DATA_DIR`, `FIGURES_DIR`, `RESULTS_DIR` defined in `config.py` as `Path` objects relative to `code/../`.

---

## File Organization

```
docs/youra_research/h-m2/
  code/
    config.py          # thresholds, paths, robustness score constants
    data.py            # load h-m1 base + extend with robustness columns
    analysis.py        # raw rho, partial rho x3, delta_rho, Fisher z
    visualize.py       # 4 figures
    run_experiment.py  # entry point + --dry-run self-check
  data/
    trustllm_scores_hm2.csv   (generated)
  figures/
    gate_metrics_comparison.png
    rank_heatmap.png
    per_dimension_scatter.png
    forest_plot.png
  results/
    results.json              (generated)
```

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| h-m1 scores CSV | `pd.read_csv(H_M1_DATA_DIR / "h_m1_scores.csv")` | `h-m1/data/h_m1_scores.csv` |
| h-e1 paper_scores | `importlib.util` load from `h-e1/code/paper_scores.py` | `h-m1/code/data.py` pattern |

**Verified from:** `docs/youra_research/h-m1/code/` (actual implementation)

H-M2 does NOT call h-m1 code directly. It reads the CSV output (`h_m1_scores.csv`) and extends it. Same `importlib.util` pattern used in h-m1 is available if needed for cross-hypothesis constants.

---

## Module Definitions

### Config (`code/config.py`)

**Dependencies:** pathlib only

```python
DELTA_RHO_GATE: float = 0.2
FISHER_Z_P_THRESHOLD: float = 0.10  # lenient, exploratory
N_COMMON_MIN: int = 8
RANDOM_SEED: int = 1

# Robustness scores embedded as fallback constants (same pattern as h-m1 WINOGRANDE_SCORES)
ROBUSTNESS_SCORES: dict = { ... }   # glue, advglue, anli_r1, anli_r3 per model

_HERE = Path(__file__).parent.parent
DATA_DIR   = _HERE / "data"
FIGURES_DIR = _HERE / "figures"
RESULTS_DIR = _HERE / "results"

H_M1_DATA_DIR = _HERE.parent / "h-m1" / "data"   # path to h_m1_scores.csv
```

---

### Data (`code/data.py`)

**Dependencies:** config, pandas

```python
def load_hm1_base() -> pd.DataFrame:
    """
    Load h-m1 validated DataFrame from H_M1_DATA_DIR/h_m1_scores.csv.
    Columns: [model_name, bbq_disambig, bbq_ambig, mmlu, winogrande]
    Returns: DataFrame (N_common rows)
    """
    ...

def build_robustness_scores() -> pd.DataFrame:
    """
    Build per-model robustness DataFrame from ROBUSTNESS_SCORES constant in config.
    Columns: [model_name, glue_score, advglue_score, anli_r1_score, anli_r3_score]
    Returns: DataFrame
    """
    ...

def build_master_dataframe() -> pd.DataFrame:
    """
    Inner join h-m1 base with robustness scores on model_name.
    Validates: N >= N_COMMON_MIN, all 7 score columns present, nunique > 3 per score.
    Saves: DATA_DIR/trustllm_scores_hm2.csv
    Returns: DataFrame columns [model_name, bbq_disambig, bbq_ambig, mmlu, winogrande,
                                 glue_score, advglue_score, anli_r1_score, anli_r3_score]
    Side effects: logs N_common_robust, any models dropped vs h-m1
    """
    ...

def verify_preconditions(df: pd.DataFrame) -> int:
    """Assert N >= N_COMMON_MIN, required columns present, variance OK. Return N."""
    ...
```

---

### Analysis (`code/analysis.py`)

**Dependencies:** config, pandas, scipy, numpy, pingouin

```python
def compute_raw_rho_all(df: pd.DataFrame) -> dict:
    """
    Raw Spearman rho (no MMLU control) for all 3 dimension pairs.
    Returns: {rho_fair_raw, rho_advglue_raw, rho_anli_raw, delta_rho_raw, n}
    """
    ...

def compute_partial_rho(df: pd.DataFrame, x: str, y: str,
                         covar: str = "mmlu") -> dict:
    """
    Partial Spearman rho via pingouin.partial_corr, alternative='two-sided'.
    Returns: {rho, p_value, ci95, n, covar}
    Raises: ValueError if p_value is NaN or |rho| > 0.999
    """
    ...

def fisher_z_test_difference(rho1: float, rho2: float, n: int) -> dict:
    """
    Fisher z-test for difference between two independent correlations.
    Formula: psinger/CorrelationStats independent_corr (inline, no package).
    Guard: if |rho1| > 0.999 or |rho2| > 0.999 → raises ValueError (fallback to Kendall tau).
    Returns: {z_stat, p_value_two_tailed}
    """
    ...

def run_full_analysis(df: pd.DataFrame) -> dict:
    """
    Full H-M2 analysis pipeline:
      1. raw rho (all 3 pairs)
      2. partial rho_fairness (MMLU-controlled, two-sided)
      3. partial rho_advglue (MMLU-controlled, two-sided)
      4. partial rho_anli   (MMLU-controlled, two-sided)
      5. delta_rho = rho_fairness - mean(rho_advglue, rho_anli)
      6. Fisher z-test for difference
      7. gate evaluation: delta_rho >= DELTA_RHO_GATE
      8. sensitivity: repeat 2-7 with winogrande as covar
    Saves: RESULTS_DIR/results.json
    Returns: consolidated dict with all metrics and gate_directional bool
    """
    ...

def evaluate_gate(delta_rho: float) -> bool:
    """Return delta_rho >= DELTA_RHO_GATE."""
    ...
```

---

### Visualize (`code/visualize.py`)

**Dependencies:** config, pandas, matplotlib, seaborn

```python
def plot_gate_metrics_bar(results: dict, out_dir: Path) -> None:
    """
    Bar chart: partial rho for fairness, AdvGLUE, ANLI with 95% CI.
    Annotates delta_rho and 0.2 threshold dashed line.
    Saves: out_dir/gate_metrics_comparison.png
    """
    ...

def plot_rank_heatmap(df: pd.DataFrame, out_dir: Path) -> None:
    """
    Heatmap: models (rows, sorted by MMLU rank) x 6 benchmarks (cols), rank position colored.
    Saves: out_dir/rank_heatmap.png
    """
    ...

def plot_per_dimension_scatter(df: pd.DataFrame, results: dict, out_dir: Path) -> None:
    """
    3-panel scatter: (bbq_disambig vs bbq_ambig), (glue vs advglue), (anli_r1 vs anli_r3).
    Each panel annotates Spearman rho.
    Saves: out_dir/per_dimension_scatter.png
    """
    ...

def plot_forest(results: dict, out_dir: Path) -> None:
    """
    Forest plot: partial rho per dimension with 95% CI, plus delta_rho row.
    Marks delta_rho = 0.2 threshold.
    Saves: out_dir/forest_plot.png
    """
    ...

def generate_all_figures(df: pd.DataFrame, results: dict, out_dir: Path) -> None:
    """Call all four plot functions."""
    ...
```

---

### Entry Point (`code/run_experiment.py`)

**Dependencies:** data, analysis, visualize, config

```python
def main() -> None:
    """
    CLI: --skip-figures, --dry-run
    Flow: build_master_dataframe() → verify_preconditions() → run_full_analysis() →
          generate_all_figures() → print gate status
    """
    ...

def _self_check() -> None:
    """10-row synthetic DataFrame smoke test for analysis functions."""
    ...
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Config & scaffolding | config.py with paths, thresholds, embedded ROBUSTNESS_SCORES dict | 5 | 1+1+1+2 |
| A-2 | Data assembly | data.py: load h-m1 CSV, join robustness scores, validate, save hm2 CSV | 10 | 2+2+2+4 |
| A-3 | Raw rho baseline | compute_raw_rho_all() via scipy.stats.spearmanr | 5 | 1+2+1+1 |
| A-4 | Partial rho x3 + delta | compute_partial_rho() for 3 pairs, delta_rho, reuse pingouin pattern from h-m1 | 10 | 2+3+2+3 |
| A-5 | Fisher z-test | fisher_z_test_difference() inline from psinger formula, guard for |rho|>0.999 | 8 | 2+2+3+1 |
| A-6 | Sensitivity analysis | Winogrande-controlled repeat of partial rho x3 + delta within run_full_analysis | 7 | 1+2+2+2 |
| A-7 | Gate evaluation + JSON output | evaluate_gate(), assemble results dict, save results.json | 4 | 1+2+1+0 |
| A-8 | Visualizations (4 figures) | bar chart, heatmap, scatter (3 panels), forest plot | 12 | 2+2+3+5 |
| A-9 | Entry point + self-check | run_experiment.py CLI, _self_check() with 10-row synthetic data | 6 | 1+3+1+1 |

**Distribution:** VeryHigh(18-20): [] | High(14-17): [] | Medium(9-13): [A-2, A-4, A-8] | Low(4-8): [A-1, A-3, A-5, A-6, A-7, A-9]
