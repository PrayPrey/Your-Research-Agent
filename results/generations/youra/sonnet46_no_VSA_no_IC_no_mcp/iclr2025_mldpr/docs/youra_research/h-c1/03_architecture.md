# H-C1 Architecture

**Applied: single-file experiment pattern (all logic in run.py)**
**Applied: reuse-first incremental hypothesis pattern**

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Patterns found from base code (h-m4/code/run.py read directly)
**Analyzed Path**: `docs/youra_research/h-m4/code/run.py`
**Findings**: H-M4 is a single monolithic `run.py` (597 lines). All functions are module-level. No submodule structure — reuse by direct import or copy of specific functions.

---

## Overview

H-C1 is a scope boundary test. It runs the same logistic fitting pipeline as H-E1/H-M4 on benchmarks with 30–49 entries (instead of ≥50) and compares fit quality against the ≥50 control group.

**Reuse strategy**: Import `logistic`, `load_timeseries`, `extract_params`, `setup_logging`, `write_results` from h-m4's `run.py` directly. Add only: benchmark discovery, fit_and_evaluate wrapper, group comparison, ablation runner, and comparison plots.

---

## File Organization

- `docs/youra_research/h-c1/code/run.py` — single experiment file (all H-C1 logic)
- `docs/youra_research/h-c1/code/test_run.py` — self-check (mirrors h-m4 pattern)
- `docs/youra_research/h-c1/figures/` — output figures
- `docs/youra_research/h-c1/code/outputs/` — results.csv, experiment_results.json

---

## External Dependencies (Base Hypothesis)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| logistic | `from h_m4_run import logistic` (or copy verbatim) | `h-m4/code/run.py:31` |
| extract_params | `from h_m4_run import extract_params` | `h-m4/code/run.py:64` |
| load_timeseries | `from h_m4_run import load_timeseries` | `h-m4/code/run.py:36` |
| setup_logging | `from h_m4_run import setup_logging` | `h-m4/code/run.py:434` |
| write_results | `from h_m4_run import write_results` | `h-m4/code/run.py:425` |

**Note**: Since h-m4 is a flat `run.py` with no package structure, the cleanest path for Phase 4 is to copy the 5 needed functions verbatim into h-c1/code/run.py (avoids sys.path manipulation). Mark each with `# verbatim from h-m4/code/run.py`.

**Verified from**: `docs/youra_research/h-m4/code/run.py` (actual implementation)

---

## Module Interfaces (`code/run.py`)

### Benchmark Discovery

```python
def discover_small_benchmarks(
    min_entries: int = 30,
    max_entries: int = 49,
    min_year: int = 2019,
) -> list[dict]:
    # Returns list of {"id": str, "name": str, "result_count": int}
    # Paginates client.benchmark_list() and filters by result_count
    ...

def fetch_timeseries(benchmark_id: str) -> tuple[np.ndarray, np.ndarray]:
    # Returns (t, y): months-since-release, normalized score [0,1]
    # Applies same preprocessing as H-E1: dedup, min-max norm, month offset
    ...
```

### Fit & Evaluate (H-C1 specific bounds from experiment brief)

```python
def fit_and_evaluate(
    times: np.ndarray,
    scores: np.ndarray,
    bounds: tuple = ([0.8, 0.1, 6], [1.0, 2.0, 48]),
) -> dict:
    # Returns: {converged, r_squared, params, ci_width, plausible}
    # K boundary hit: K >= 0.999; plausible: K<0.999 AND r>0.05 AND 6<t0<48
    ...
```

### Group Comparison

```python
def compare_groups(
    small_results: list[dict],
    control_results: list[dict],
) -> dict:
    # Returns: {convergence_rate_small, convergence_rate_control,
    #           mean_r2_small, mean_r2_control,
    #           plausibility_rate_small, k_boundary_hit_rate_small,
    #           h_c1_supported: bool}
    ...

def verify_boundary_test_activated(
    results_small: list[dict],
    results_control: list[dict],
) -> tuple[bool, dict]:
    # Returns (activated: bool, indicators: dict)
    # From experiment brief pseudocode (verbatim)
    ...
```

### Ablation Runner

```python
def run_ablation(
    timeseries_data: list[tuple[np.ndarray, np.ndarray]],
    control_results: list[dict],
) -> dict:
    # 4 variants:
    #   strict: failure = R2 < 0.5
    #   loose:  failure = R2 < 0.8
    #   split40: 30-39 vs 40-49 subgroups
    #   no_bounds: curve_fit with no bounds
    # Returns dict keyed by variant name -> comparison metrics
    ...
```

### Visualization

```python
def plot_group_comparison(comparison: dict, fig_dir: Path) -> None:
    # Bar chart: convergence rate, mean R2, plausibility rate — small vs control
    ...

def plot_r2_distribution(small_results: list[dict], control_results: list[dict], fig_dir: Path) -> None:
    # Histogram overlay of R2 values
    ...

def plot_fitted_curves(
    timeseries_data: list[tuple],
    small_results: list[dict],
    benchmark_names: list[str],
    fig_dir: Path,
) -> None:
    # Per-benchmark: raw data + fitted logistic (or "convergence failure" annotation)
    ...

def plot_ablation_summary(ablation_results: dict, fig_dir: Path) -> None:
    # Bar chart: mean R2 / convergence rate per ablation variant
    ...
```

### Verbatim from H-M4 (copy, do not modify)

```python
# logistic(t, K, r, t0) -> np.ndarray
# extract_params(t_data, y_data, benchmark_name) -> dict
#   NOTE: benchmark_name used only for logging; BENCHMARK_RELEASE_MONTH lookup
#         must be patched for non-GLUE/SuperGLUE benchmarks (default to 0)
# load_timeseries(csv_path) -> tuple  [used only if loading from CSV fallback]
# setup_logging(log_path) -> Logger
# write_results(results, out_path) -> None
```

### Main Entry Point

```python
def main() -> None:
    # 1. discover_small_benchmarks(30, 49, 2019) -> small_bms
    # 2. fetch_timeseries() for each -> timeseries_data
    # 3. fit_and_evaluate() for each -> small_results
    # 4. load H-E1 control results (GLUE, SuperGLUE) from h-m4 outputs or re-fit
    # 5. compare_groups(small_results, control_results) -> comparison
    # 6. verify_boundary_test_activated(small_results, control_results)
    # 7. run_ablation(timeseries_data, control_results) -> ablation_results
    # 8. plot_group_comparison, plot_r2_distribution, plot_fitted_curves, plot_ablation_summary
    # 9. write_results(payload, ...)
    # 10. sys.exit(0 if gate criteria met else 1)
    ...
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| C1-1 | Project setup | File structure, constants, logging, copy h-m4 verbatim functions, patch BENCHMARK_RELEASE_MONTH for dynamic benchmarks | 6 | 1+1+2+2 |
| C1-2 | Benchmark discovery | discover_small_benchmarks() with pagination + fetch_timeseries() with H-E1 preprocessing | 10 | 2+2+3+3 |
| C1-3 | Fit & evaluate | fit_and_evaluate() wrapper with boundary hit detection + plausibility checks | 9 | 2+2+3+2 |
| C1-4 | Control group loading | Load/re-fit H-E1 control (GLUE, SuperGLUE) results for comparison baseline | 7 | 2+2+2+1 |
| C1-5 | Group comparison & gate | compare_groups(), verify_boundary_test_activated(), gate pass/fail logic | 9 | 2+2+3+2 |
| C1-6 | Ablation runner | 4 variants (strict/loose threshold, split at 40, no bounds) across discovered benchmarks | 11 | 3+2+3+3 |
| C1-7 | Visualization | 4 figures: group comparison bar, R2 histogram, fitted curves per benchmark, ablation summary | 10 | 2+2+3+3 |
| C1-8 | Integration & test | main() integration, test_run.py self-check, results.json + CSV output | 8 | 2+2+2+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [C1-3, C1-5, C1-6, C1-7, C1-2], Low(4-8): [C1-1, C1-4, C1-8]

---

## Key Constraints for Phase 4

- `extract_params` from h-m4 uses `BENCHMARK_RELEASE_MONTH[benchmark_name]` dict lookup — Phase 4 must default to 0 for new benchmark names (not GLUE/SuperGLUE).
- H-M4 `bounds` in `extract_params` are `([0.5, 0.01, -24], [1.05, 3.0, 72])` — H-C1 uses tighter bounds `([0.8, 0.1, 6], [1.0, 2.0, 48])` per experiment brief. Use separate `fit_and_evaluate()` function, not `extract_params`.
- Control group: prefer loading from h-m4's `experiment_results.json` to avoid re-running; fall back to re-fitting GLUE/SuperGLUE CSVs.
- If fewer than 3 qualifying benchmarks found: log warning, continue with available (minimum 1).
- All figures saved to `docs/youra_research/h-c1/figures/`.
