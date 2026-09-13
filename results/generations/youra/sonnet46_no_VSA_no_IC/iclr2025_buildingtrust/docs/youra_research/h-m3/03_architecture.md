# Architecture: H-M3
# Per-Pair Adversarial Rank Disruption Analysis

**Date:** 2026-08-20
**Hypothesis Type:** MECHANISM (INCREMENTAL on H-M2)
**Applied:** flat single-directory module pattern (no sub-packages) — same as H-M1/H-M2

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis (incremental on H-M2)
**Status:** Patterns found from base code (h-m2)
**Analyzed Path:** `docs/youra_research/h-m2/code/`
**Findings:** Five flat files — `config.py`, `data.py`, `analysis.py`, `visualize.py`, `run_experiment.py`. Imports via relative `from config import ...` (scripts run from `code/` dir). Paths via `Path(__file__).parent.parent`. `H_M1_DATA_DIR` cross-links to prior hypothesis data. H-M3 mirrors this exact structure and reuses H-M2 data artifact (`trustllm_scores_hm2.csv`) rather than rebuilding from h-m1.

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| H-M2 master CSV | `pd.read_csv(H_M2_DATA_DIR / "trustllm_scores_hm2.csv")` | `h-m2/data/trustllm_scores_hm2.csv` |
| H-M2 config constants | embedded in h-m3 config (copied values) | `h-m2/code/config.py` |

**Verified from:** `docs/youra_research/h-m2/code/` (actual implementation)

H-M3 reads `trustllm_scores_hm2.csv` (already contains glue_score, advglue_score, anli_r1_score, anli_r3_score, mmlu, bbq_disambig). No new data download. Column names follow H-M2 convention (snake_case with `_score` suffix).

---

## File Organization

```
docs/youra_research/h-m3/
  code/
    config.py          # thresholds, paths, H-M1 rho_fairness reference
    data.py            # load + validate trustllm_scores_hm2.csv
    analysis.py        # per-pair partial Spearman, Fisher z, rank reversals, mechanism check
    visualize.py       # 6 figures
    run_experiment.py  # entry point + --dry-run self-check
  figures/
    gate_metrics_comparison.png
    rank_scatter_advglue.png
    rank_scatter_anli.png
    rank_reversal_heatmap.png
    correlation_summary_table.png
    fisher_z_distribution.png
  results.json
```

---

## Module Definitions

### Config (`code/config.py`)

**Dependencies:** pathlib only

```python
RHO_THRESHOLD: float = 0.4           # gate threshold per pair
ALPHA: float = 0.05
N_BOOTSTRAP: int = 1000
RANDOM_SEED: int = 42
N_COMMON_MIN: int = 10
RANK_REVERSAL_MIN_SHIFT: int = 5

# H-M1 reference value for bar chart baseline
RHO_FAIRNESS_HM1: float = None       # loaded from h-m1 results.json at runtime; fallback 0.60

_HERE = Path(__file__).parent.parent
FIGURES_DIR = _HERE / "figures"
RESULTS_JSON = _HERE / "results.json"

H_M2_DATA_DIR = _HERE.parent / "h-m2" / "data"
H_M1_RESULTS  = _HERE.parent / "h-m1" / "results" / "results.json"
```

---

### Data (`code/data.py`)

**Dependencies:** config, pandas

```python
def load_scores() -> pd.DataFrame:
    """
    Load trustllm_scores_hm2.csv from H_M2_DATA_DIR.
    Validates required columns: [model_name, glue_score, advglue_score,
                                  anli_r1_score, anli_r3_score, mmlu].
    Drops NaN rows in required cols.
    Asserts N >= N_COMMON_MIN.
    Logs shape.
    Returns: DataFrame (N, 6+)
    """
    ...

def load_rho_fairness() -> float:
    """
    Read rho_fairness from H_M1_RESULTS/results.json key 'rho_fairness'.
    Returns RHO_FAIRNESS_HM1 fallback (0.60) if file missing.
    """
    ...
```

---

### Analysis (`code/analysis.py`)

**Dependencies:** config, pandas, numpy, scipy, pingouin

```python
def compute_partial_spearman(df: pd.DataFrame, x_col: str, y_col: str,
                              covar_col: str = "mmlu",
                              alternative: str = "greater",
                              n_bootstrap: int = 1000) -> dict:
    """
    Partial Spearman rho(x, y | covar) via pingouin.partial_corr(method='spearman').
    Bootstrap CI: 1000 resamples of spearmanr(x[idx], y[idx]).
    Returns: {rho, p_asymptotic, ci_lower, ci_upper, n}
    """
    ...

def fisher_z_test_vs_threshold(rho: float, n: int,
                                threshold: float = 0.4,
                                alternative: str = "less") -> dict:
    """
    One-tailed test H0: rho >= threshold; H1: rho < threshold.
    z = (arctanh(rho) - arctanh(threshold)) / (1/sqrt(n-3))
    p = norm.cdf(z)
    Returns: {z, p, significant}
    """
    ...

def count_rank_reversals(df: pd.DataFrame, id_col: str,
                          ood_col: str, min_shift: int = 5) -> int:
    """
    Count models where |rank(id_col) - rank(ood_col)| >= min_shift.
    Returns: int count
    """
    ...

def verify_mechanism_activated(df: pd.DataFrame, results: dict) -> tuple[bool, dict]:
    """
    Checks: data_complete, n_sufficient, advglue_computed, anli_computed,
            pairs_differ, reversals_counted.
    Returns: (all_ok: bool, indicators: dict)
    """
    ...

def evaluate_gate(rho_advglue: float, p_advglue: float,
                  rho_anli: float, p_anli: float,
                  threshold: float = 0.4) -> bool:
    """
    Gate passes if (rho_advglue < threshold OR p_advglue >= 0.05)
                AND (rho_anli   < threshold OR p_anli   >= 0.05).
    """
    ...

def run_full_analysis(df: pd.DataFrame, rho_fairness: float) -> dict:
    """
    Full H-M3 pipeline:
      1. compute_partial_spearman for AdvGLUE pair (GLUE, AdvGLUE | MMLU)
      2. compute_partial_spearman for ANLI pair (ANLI_R1, ANLI_R3 | MMLU)
      3. fisher_z_test_vs_threshold for each pair
      4. count_rank_reversals for each pair
      5. verify_mechanism_activated()
      6. evaluate_gate()
    Saves RESULTS_JSON.
    Returns: consolidated dict with all metrics, gate_passed, mechanism_ok.
    """
    ...
```

---

### Visualize (`code/visualize.py`)

**Dependencies:** config, pandas, matplotlib, seaborn

```python
def plot_gate_metrics_bar(results: dict, rho_fairness: float, out_dir: Path) -> None:
    """
    Bar chart: rho_AdvGLUE and rho_ANLI vs rho_fairness with 95% CI error bars.
    Horizontal dashed line at rho = 0.4.
    Saves: out_dir/gate_metrics_comparison.png
    """
    ...

def plot_rank_scatter_advglue(df: pd.DataFrame, out_dir: Path) -> None:
    """
    Scatter: GLUE rank vs AdvGLUE rank per model, colored by |rank_shift|.
    Saves: out_dir/rank_scatter_advglue.png
    """
    ...

def plot_rank_scatter_anli(df: pd.DataFrame, out_dir: Path) -> None:
    """
    Scatter: ANLI_R1 rank vs ANLI_R3 rank per model, colored by |rank_shift|.
    Saves: out_dir/rank_scatter_anli.png
    """
    ...

def plot_rank_reversal_heatmap(df: pd.DataFrame, out_dir: Path) -> None:
    """
    Heatmap: model (rows) x [glue_score, advglue_score, anli_r1_score, anli_r3_score] rank positions.
    Highlight cells where shift >= RANK_REVERSAL_MIN_SHIFT.
    Saves: out_dir/rank_reversal_heatmap.png
    """
    ...

def plot_correlation_summary_table(results: dict, rho_fairness: float, out_dir: Path) -> None:
    """
    Table figure: rho_fairness, rho_AdvGLUE, rho_ANLI with CI and p-values.
    Saves: out_dir/correlation_summary_table.png
    """
    ...

def plot_fisher_z_distribution(results: dict, out_dir: Path) -> None:
    """
    Normal distribution plot showing z_AdvGLUE and z_ANLI positions relative to threshold.
    Saves: out_dir/fisher_z_distribution.png
    """
    ...

def generate_all_figures(df: pd.DataFrame, results: dict,
                          rho_fairness: float, out_dir: Path) -> None:
    """Call all six plot functions."""
    ...
```

---

### Entry Point (`code/run_experiment.py`)

**Dependencies:** data, analysis, visualize, config

```python
def main() -> None:
    """
    CLI: --skip-figures, --dry-run
    Flow: load_scores() -> load_rho_fairness() -> run_full_analysis() ->
          generate_all_figures() -> print gate status + mechanism indicators
    """
    ...

def _self_check() -> None:
    """10-row synthetic DataFrame smoke test: verify mechanism + gate functions run without error."""
    ...
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Config & scaffolding | config.py with paths, thresholds, H_M2_DATA_DIR, RHO_FAIRNESS_HM1 fallback | 5 | 1+1+1+2 |
| A-2 | Data loading | data.py: load trustllm_scores_hm2.csv, validate columns, load_rho_fairness() | 7 | 2+2+1+2 |
| A-3 | Partial Spearman per pair | compute_partial_spearman() with pingouin + bootstrap CI; apply to AdvGLUE and ANLI pairs | 10 | 2+3+3+2 |
| A-4 | Fisher z vs threshold | fisher_z_test_vs_threshold() one-tailed; apply to both pairs | 7 | 1+2+3+1 |
| A-5 | Rank reversal counting | count_rank_reversals() per pair; per-model rank delta computation | 5 | 1+2+1+1 |
| A-6 | Mechanism verification + gate | verify_mechanism_activated(), evaluate_gate(), run_full_analysis() orchestration | 9 | 2+3+2+2 |
| A-7 | Results export | Assemble results dict, save results.json to RESULTS_JSON path | 4 | 1+2+1+0 |
| A-8 | Required figure | plot_gate_metrics_bar() with CI error bars and rho=0.4 threshold line | 7 | 1+2+2+2 |
| A-9 | Additional figures (5) | rank scatters x2, heatmap, summary table, Fisher z distribution | 12 | 2+2+3+5 |
| A-10 | Entry point + self-check | run_experiment.py CLI, _self_check() with 10-row synthetic data | 6 | 1+3+1+1 |

**Distribution:** VeryHigh(18-20): [] | High(14-17): [] | Medium(9-13): [A-3, A-6, A-9] | Low(4-8): [A-1, A-2, A-4, A-5, A-7, A-8, A-10]
