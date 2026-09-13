# Architecture: H-E1
# PELT Change-Point Detection on PwC Benchmark CoV Series

**Hypothesis:** H-E1 (EXISTENCE / FOUNDATION)
**Date:** 2026-08-21
**Author:** yoon303@etri.re.kr

Applied: N/A — no domain-relevant Archon KB content found for statistical analysis domain

---

## Codebase Analysis (Serena)

**Project Type**: existing_codebase (archive)
**Status**: existing patterns found
**Analyzed Path**: `docs/youra_research/_archive/20260821T055106_routing_recovery/h-e1/code/`
**Findings**: Archive contains working `ingest_pwc.py` (fetch_pwc_benchmarks + fetch_pwc_results_via_evaluations) and `derive.py` (compute_result_cov). Both reused directly. Archive config.py sets MIN_PAPERS=10 — new config.py mirrors this. Archive also has `run.py`, `ablation.py`, `report.py`, `join.py` — NOT reused (H-E1 is PELT-focused, simpler scope).

---

## File Structure

- `h-e1/code/`
  - `config.py` — constants (MIN_PAPERS, seeds, paths, PELT params)
  - `ingest_pwc.py` — copied from archive (confirmed working)
  - `derive.py` — copied from archive (compute_result_cov only needed)
  - `pipeline.py` — OLS detrend + PELT detection
  - `evaluate.py` — permutation test, bootstrap CI, piecewise F-test, verify_mechanism_activated
  - `visualize.py` — 6 figures → h-e1/figures/
  - `run_experiment.py` — orchestrator, saves experiment_results.json
- `h-e1/figures/` — output directory (auto-created)

---

## Modules

### Config (`code/config.py`)

**Dependencies**: none

```python
MIN_PAPERS: int = 5           # benchmarks with < MIN_PAPERS papers excluded
MIN_COV_ROWS: int = 3         # minimum result rows for CoV computation
SEED: int = 42
N_PERMUTATIONS: int = 1000
N_BOOTSTRAP: int = 1000
PELT_MIN_SIZE: int = 3
PELT_JUMP: int = 1
PELT_MODEL: str = "l2"
PEN_RANGE: tuple = (1, 50)
N_PEN: int = 20
PAPER_COUNT_STAR_MIN: int = 10
PAPER_COUNT_STAR_MAX: int = 120
BOOTSTRAP_CI_WIDTH_MAX: int = 20
P_THRESHOLD: float = 0.05
FIGURES_DIR: str  # absolute path to h-e1/figures/
RESULTS_JSON: str  # absolute path to h-e1/experiment_results.json
```

---

### IngestPwC (`code/ingest_pwc.py`)

**Dependencies**: config, datasets, pandas, numpy

Copied from archive. Public interface:

```python
def fetch_pwc_benchmarks(min_papers: int = MIN_PAPERS) -> pd.DataFrame: ...
    # returns: name, dataset_name, task_name, paper_count, year_introduced, num_rows

def fetch_pwc_results_via_evaluations(pwc_df: pd.DataFrame) -> pd.DataFrame: ...
    # returns: benchmark_name, model, metric_value, year
```

---

### Derive (`code/derive.py`)

**Dependencies**: config, pandas, numpy, scipy.stats

Copied from archive. Only `compute_result_cov` is used in H-E1:

```python
def compute_result_cov(results_df: pd.DataFrame) -> pd.Series: ...
    # CoV = std(ddof=1)/mean per benchmark, NaN if < 3 rows
    # returns Series indexed by benchmark_name
```

---

### Pipeline (`code/pipeline.py`)

**Dependencies**: config, numpy, scipy.stats, ruptures

```python
def ols_detrend(
    paper_counts: np.ndarray,
    cov_values: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, dict]: ...
    # returns: sorted_paper_counts, residual_cov, ols_metrics
    # ols_metrics keys: slope, intercept, rho, r2

def run_pelt_changepoint(
    paper_counts: np.ndarray,
    cov_values: np.ndarray,
    pen_range: tuple = PEN_RANGE,
    n_pen: int = N_PEN,
    min_size: int = PELT_MIN_SIZE,
) -> dict: ...
    # returns: paper_count_star, breakpoint_idx, pen_used, n_bkps,
    #          residual_cov_sorted, sorted_paper_counts, bkps_list, pen_values
```

---

### Evaluate (`code/evaluate.py`)

**Dependencies**: config, pipeline, numpy, scipy.stats, statsmodels

```python
def run_permutation_test(
    paper_counts: np.ndarray,
    cov_values: np.ndarray,
    n_permutations: int = N_PERMUTATIONS,
    seed: int = SEED,
) -> dict: ...
    # returns: permutation_p, null_distribution (array of breakpoint positions)

def run_bootstrap_ci(
    paper_counts: np.ndarray,
    cov_values: np.ndarray,
    n_resamples: int = N_BOOTSTRAP,
    seed: int = SEED,
) -> dict: ...
    # returns: bootstrap_ci_lower, bootstrap_ci_upper, bootstrap_ci_width, bootstrap_estimates

def run_piecewise_ftest(
    paper_counts: np.ndarray,
    cov_values: np.ndarray,
    paper_count_star: float,
) -> dict: ...
    # returns: piecewise_f_p, f_statistic

def verify_mechanism_activated(results: dict) -> tuple[bool, dict]: ...
    # returns: (all_pass, indicators)
    # indicators: pelt_detected_breakpoint, paper_count_star_in_range, permutation_p_significant
```

---

### Visualize (`code/visualize.py`)

**Dependencies**: config, matplotlib, seaborn, numpy

```python
def plot_gate_metrics(results: dict, figures_dir: str) -> None: ...
    # fig1: bar chart permutation_p vs 0.05, paper_count_star vs [10,120]

def plot_cov_scatter(
    paper_counts: np.ndarray,
    cov_values: np.ndarray,
    paper_count_star: float,
    ols_metrics: dict,
    figures_dir: str,
) -> None: ...
    # fig2: scatter + OLS line + vertical dashed line at paper_count*

def plot_residual_series(
    sorted_paper_counts: np.ndarray,
    residual_cov: np.ndarray,
    breakpoint_idx: int,
    figures_dir: str,
) -> None: ...
    # fig3: residual CoV series with pre/post shading

def plot_permutation_null(
    null_distribution: np.ndarray,
    observed_bkp_idx: int,
    figures_dir: str,
) -> None: ...
    # fig4: histogram of null breakpoint positions + observed marked

def plot_bootstrap_ci(
    bootstrap_estimates: np.ndarray,
    ci_lower: float,
    ci_upper: float,
    figures_dir: str,
) -> None: ...
    # fig5: distribution of 1000 bootstrap paper_count* estimates + CI bounds

def plot_penalty_sensitivity(
    pen_values: np.ndarray,
    bkps_list: list,
    pen_used: float,
    figures_dir: str,
) -> None: ...
    # fig6: n_bkps vs penalty (log scale) + BIC penalty marked

def save_all_figures(
    paper_counts: np.ndarray,
    cov_values: np.ndarray,
    pelt_results: dict,
    eval_results: dict,
    figures_dir: str,
) -> None: ...
    # calls all 6 plot functions
```

---

### RunExperiment (`code/run_experiment.py`)

**Dependencies**: all modules above, json, pathlib

```python
def main() -> None: ...
    # 1. mkdir figures_dir
    # 2. fetch_pwc_benchmarks() → pwc_df
    # 3. fetch_pwc_results_via_evaluations(pwc_df) → results_df
    # 4. compute_result_cov(results_df) → cov_series; merge with pwc_df
    # 5. early-fail if N < 10 or residual std == 0
    # 6. run_pelt_changepoint() → pelt_results
    # 7. run_permutation_test() → perm_results
    # 8. run_bootstrap_ci() → boot_results
    # 9. run_piecewise_ftest() → ftest_results
    # 10. verify_mechanism_activated(all_results)
    # 11. save_all_figures()
    # 12. write experiment_results.json
    # 13. print gate pass/fail summary

if __name__ == "__main__":
    main()
```

---

## External Dependencies (Archive)

| Module | Source File | Reuse Strategy |
|--------|-------------|----------------|
| fetch_pwc_benchmarks | archive/h-e1/code/ingest_pwc.py | Copy verbatim |
| fetch_pwc_results_via_evaluations | archive/h-e1/code/ingest_pwc.py | Copy verbatim |
| compute_result_cov | archive/h-e1/code/derive.py | Copy function only |

Config values carried over: `MIN_PAPERS=5` (archive default was 10; PRD FR-1.4 says default=5), `NORM_REGEX`, `MIN_MODELS_PER_COHORT`.

**Verified from**: `docs/youra_research/_archive/20260821T055106_routing_recovery/h-e1/code/` (actual implementation)

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Setup & Config | Create h-e1/code/ structure, config.py, copy ingest_pwc.py + derive.py from archive | 5 | 1+1+1+2 |
| A-2 | Pipeline (OLS + PELT) | Implement pipeline.py: ols_detrend + run_pelt_changepoint with BIC penalty + elbow sweep | 10 | 2+2+4+2 |
| A-3 | Evaluate | Implement evaluate.py: permutation test (N=1000) + bootstrap CI + piecewise F-test + verify_mechanism_activated | 13 | 3+2+5+3 |
| A-4 | Visualize | Implement visualize.py: 6 figures saved to h-e1/figures/ | 8 | 2+1+3+2 |
| A-5 | Orchestrate & Output | Implement run_experiment.py: wire all modules, early-fail guards, JSON output, gate summary | 9 | 2+3+2+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-2, A-3, A-5], Low(4-8): [A-1, A-4]
