# Architecture: H-M1
# BCBHS Submission Count → Score Compression Causal Mechanism

Applied: modular-statistical-pipeline pattern

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Serena project activation unavailable; direct file read used instead
**Analyzed Path**: `docs/youra_research/20260519_mldpr/h-e1/code/`
**Findings**: H-E1 code uses flat module layout (no subdirectories). `data_pipeline.py` exports `load_pwc_panel()`, `load_openml_panel()`, `label_saturation()`, `get_domain_panels()`. `run_experiment.py` uses inline CONFIG dict + argparse. All imports are local (e.g., `from data_pipeline import load_pwc_panel`). `evaluate.py` exports `verify_mechanism_activated`, `check_gate_condition`, `save_results`.

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| load_pwc_panel | `from data_pipeline import load_pwc_panel` | `h-e1/code/data_pipeline.py` |
| load_openml_panel | `from data_pipeline import load_openml_panel` | `h-e1/code/data_pipeline.py` |
| label_saturation | `from data_pipeline import label_saturation` | `h-e1/code/data_pipeline.py` |
| DOMAIN_MAP | `from data_pipeline import DOMAIN_MAP` | `h-e1/code/data_pipeline.py` |

**Verified from**: `h-e1/code/data_pipeline.py` (actual implementation)

---

## File Organization

```
h-m1/code/
├── data_pipeline.py        # PWC quarterly panel (extends H-E1)
├── sigma_estimation.py     # σ_measurement per benchmark
├── compression_detector.py # 1.5σ threshold + consecutive flagging
├── spearman_baseline.py    # Spearman ρ co-occurrence test
├── granger_causality.py    # Granger test, ADF, reverse causality
├── evaluate.py             # Mechanism verification + gate check
├── visualize.py            # 6 figures
└── run_experiment.py       # Entry point

h-m1/figures/
├── gate_metrics.png
├── scatter_submission_compression.png
├── lag_profile.png
├── timeseries_overlay.png
├── compression_distribution.png
└── reverse_causality.png
```

---

## Module Interfaces

### DataPipeline (`data_pipeline.py`)

**Dependencies**: datasets (HuggingFace), pandas, numpy; reuses H-E1 `load_pwc_panel` pattern

```python
import sys, os
# Add h-e1/code to path OR re-implement load_pwc_panel locally
# H-M1 re-implements with extended quarterly panel columns

DOMAIN_MAP: dict  # same as H-E1

def load_pwc_raw() -> pd.DataFrame:
    """Load raw PWC evaluation-tables from HuggingFace. Returns normalized df."""
    ...

def compute_quarterly_panel(
    pwc_raw: pd.DataFrame,
    min_submissions: int = 20,
    min_quarters: int = 8,
) -> pd.DataFrame:
    """Build (benchmark_id, quarter) panel with cumulative_count, score_var_top10.
    Returns: DataFrame[benchmark_id, task, dataset, quarter, submission_count,
                        cumulative_count, score_var_top10]
    """
    ...

def load_panel(min_submissions: int = 20, min_quarters: int = 8) -> pd.DataFrame:
    """Top-level: load raw + compute quarterly panel. Returns panel DataFrame."""
    ...
```

---

### SigmaEstimation (`sigma_estimation.py`)

**Dependencies**: pandas, numpy

```python
def estimate_sigma_measurement(pwc_raw: pd.DataFrame) -> pd.Series:
    """Per-benchmark σ_measurement from repeated model submissions.
    Returns: Series indexed by (task, dataset) named 'sigma_meas'.
    Fallback: benchmarks with no repeats get cross-benchmark median.
    """
    ...

def get_sigma_map(pwc_raw: pd.DataFrame) -> pd.Series:
    """Alias; calls estimate_sigma_measurement with fallback applied."""
    ...
```

---

### CompressionDetector (`compression_detector.py`)

**Dependencies**: pandas, numpy; SigmaEstimation

```python
def flag_compression(
    panel_df: pd.DataFrame,
    sigma_map: pd.Series,
    threshold: float = 1.5,
    min_consecutive: int = 2,
) -> pd.DataFrame:
    """Merge sigma_map into panel; add 'compressed' and 'compression_event' columns.
    Returns: panel_df extended with [sigma_meas, compressed, compression_event].
    """
    ...

def summarize_compression(panel_df: pd.DataFrame) -> dict:
    """Return counts: n_compression_events, n_qualifying_benchmarks, pct_compressed."""
    ...
```

---

### SpearmanBaseline (`spearman_baseline.py`)

**Dependencies**: scipy.stats, pandas

```python
def compute_spearman_baseline(panel_df: pd.DataFrame) -> dict:
    """Spearman ρ between cumulative_count and compression_event across all rows.
    Returns: {'rho': float, 'p_value': float, 'n_obs': int}
    """
    ...
```

---

### GrangerCausality (`granger_causality.py`)

**Dependencies**: statsmodels.tsa.stattools, pandas, numpy

```python
def check_stationarity(series: pd.Series) -> bool:
    """ADF test; returns True if stationary (p < 0.05)."""
    ...

def make_stationary(series: pd.Series) -> pd.Series:
    """First-order difference if non-stationary; log-transform fallback."""
    ...

def test_granger_causality(
    benchmark_panel: pd.DataFrame,
    max_lag: int = 4,
) -> dict | None:
    """ADF check + differencing + grangercausalitytests for one benchmark.
    Input columns: ['score_var_top10', 'cumulative_count'] sorted by quarter.
    Returns: {lag: p_value} for lags 1-4, or None if insufficient data.
    """
    ...

def test_reverse_causality(
    benchmark_panel: pd.DataFrame,
    max_lag: int = 4,
) -> dict | None:
    """Test compression_event → cumulative_count direction.
    Returns: {lag: p_value} or None.
    """
    ...

def run_granger_panel(
    panel_df: pd.DataFrame,
    max_lag: int = 4,
) -> tuple[dict, dict]:
    """Run forward + reverse Granger for all benchmarks.
    Returns: (forward_results, reverse_results)
      Each: {benchmark_id: {lag: p_value} | None}
    """
    ...

def aggregate_granger_panel(
    granger_results: dict,
    target_lag: int = 2,
) -> dict:
    """Aggregate per-benchmark results to panel-level summary stats.
    Returns: {n_benchmarks_tested, n_significant_lag2, pct_significant_lag2,
              min_p_lag2, median_p_lag2}
    """
    ...
```

---

### Evaluate (`evaluate.py`)

**Dependencies**: pandas, numpy; SpearmanBaseline, GrangerCausality, CompressionDetector

```python
def verify_mechanism_activated(
    panel_df: pd.DataFrame,
    granger_results: dict,
    spearman_result: dict,
) -> tuple[bool, dict]:
    """Check all mechanism activation indicators.
    Returns: (activated: bool, indicators: dict)
    indicators keys: panel_constructed, sufficient_benchmarks, spearman_computed,
                     granger_computed, spearman_significant, granger_significant_lag2
    """
    ...

def check_gate_condition(
    spearman_result: dict,
    granger_agg: dict,
) -> tuple[bool, dict]:
    """PASS if Spearman ρ>0.4 AND p<0.05 OR Granger p<0.05 at lag=2.
    Returns: (gate_passed: bool, gate_details: dict)
    """
    ...

def save_results(results: dict, output_path: str) -> None:
    """Serialize results dict to JSON."""
    ...
```

---

### Visualize (`visualize.py`)

**Dependencies**: matplotlib, seaborn, pandas, numpy

```python
def plot_gate_metrics(
    spearman_result: dict,
    granger_agg: dict,
    output_dir: str,
) -> None:
    """Bar chart: target vs actual for Spearman ρ and Granger p at lag=2."""
    ...

def plot_scatter_submission_compression(
    panel_df: pd.DataFrame,
    output_dir: str,
) -> None:
    """Scatter: cumulative_count vs compression_event, colored by domain."""
    ...

def plot_lag_profile(
    granger_results: dict,
    output_dir: str,
) -> None:
    """Granger p-values at lags 1-4 (forward vs reverse)."""
    ...

def plot_timeseries_overlay(
    panel_df: pd.DataFrame,
    output_dir: str,
    example_benchmark: str | None = None,
) -> None:
    """Dual-panel time series: submission count (top), score variance (bottom)."""
    ...

def plot_compression_distribution(
    panel_df: pd.DataFrame,
    output_dir: str,
) -> None:
    """Histogram: first compression quarter relative to cumulative count."""
    ...

def plot_reverse_causality(
    forward_results: dict,
    reverse_results: dict,
    output_dir: str,
) -> None:
    """Bar chart: forward vs reverse Granger p-values at lag=2."""
    ...

def generate_all_figures(
    panel_df: pd.DataFrame,
    spearman_result: dict,
    granger_results: dict,
    reverse_results: dict,
    granger_agg: dict,
    output_dir: str,
) -> None:
    """Call all 6 plot functions."""
    ...
```

---

### RunExperiment (`run_experiment.py`)

**Dependencies**: all modules above

```python
CONFIG = {
    "seed": 42,
    "min_submissions": 20,
    "min_quarters": 8,
    "compression_threshold": 1.5,
    "min_consecutive": 2,
    "granger_max_lag": 4,
    "spearman_rho_target": 0.4,
    "granger_p_target": 0.05,
    "output_dir": "h-m1/figures/",
    "results_json": "h-m1/results.json",
    "results_csv": "h-m1/results.csv",
}

def parse_args(config: dict, args=None) -> dict: ...

def main(args=None) -> None:
    """
    Steps:
    1. load_panel() → pwc_raw, panel_df
    2. get_sigma_map(pwc_raw) → sigma_map
    3. flag_compression(panel_df, sigma_map) → panel_df
    4. compute_spearman_baseline(panel_df) → spearman_result
    5. run_granger_panel(panel_df) → granger_results, reverse_results
    6. aggregate_granger_panel(granger_results) → granger_agg
    7. verify_mechanism_activated(...) → activated, indicators
    8. check_gate_condition(...) → gate_passed, gate_details
    9. generate_all_figures(...)
    10. save_results(...)
    """
    ...
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Setup & Data Pipeline | `data_pipeline.py`: load_pwc_raw, compute_quarterly_panel, load_panel. Reuse H-E1 loading pattern; extend with quarterly panel schema | 10 | 3+2+3+2 |
| A-2 | Sigma Estimation | `sigma_estimation.py`: estimate σ_measurement from repeated submissions; cross-benchmark median fallback | 8 | 2+2+2+2 |
| A-3 | Compression Detector | `compression_detector.py`: merge sigma, flag 1.5σ threshold, rolling 2-quarter consecutive detection | 9 | 2+2+3+2 |
| A-4 | Spearman Baseline | `spearman_baseline.py`: compute_spearman_baseline with validity checks | 6 | 1+1+2+2 |
| A-5 | Granger Causality Core | `granger_causality.py`: ADF stationarity, differencing, grangercausalitytests lags 1-4 per benchmark | 14 | 3+3+4+4 |
| A-6 | Reverse Causality & Panel Aggregation | `granger_causality.py`: test_reverse_causality, run_granger_panel, aggregate_granger_panel | 12 | 3+3+3+3 |
| A-7 | Evaluate & Gate | `evaluate.py`: verify_mechanism_activated, check_gate_condition, save_results | 9 | 2+2+3+2 |
| A-8 | Visualization | `visualize.py`: all 6 figures, generate_all_figures | 10 | 3+2+2+3 |
| A-9 | Entry Point & Integration | `run_experiment.py`: CONFIG, argparse, orchestrate all 10 steps, CSV output | 8 | 2+2+2+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-5], Medium(9-13): [A-3, A-6, A-7, A-8, A-1], Low(4-8): [A-2, A-4, A-9]
