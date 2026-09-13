# Logic: H-M1
# BCBHS Submission Count → Score Compression Causal Mechanism

Applied: modular-statistical-pipeline pattern

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Serena project activation unavailable; direct file read used instead
**Analyzed Path**: `docs/youra_research/20260519_mldpr/h-e1/code/`
**Relevant Symbols**:
- `load_pwc_panel()` — H-E1 data_pipeline.py, returns normalized DataFrame with columns [benchmark, domain, model, date, score, quarter]
- `label_saturation(panel)` — H-E1 data_pipeline.py, adds 'label' column
- `get_domain_panels(panel, domain, min_saturated, min_healthy)` — returns (saturated_df, healthy_df)
- `verify_mechanism_activated(domain_results)` — H-E1 evaluate.py, takes dict keyed by domain (different signature than H-M1!)
- `check_gate_condition(domain_results)` — H-E1 evaluate.py, takes dict keyed by domain
- `save_results(results, output_path)` — H-E1 evaluate.py, serializes to JSON
- `DOMAIN_MAP` — H-E1 data_pipeline.py, task_name → domain string

---

## External Dependencies API

### API Signatures (From Actual Code)

Verified from `/h-e1/code/data_pipeline.py` and `/h-e1/code/evaluate.py`:

```python
# From: h-e1/code/data_pipeline.py (ACTUAL CODE)
DOMAIN_MAP: dict  # task_name (str) -> domain (str: "cv"|"nlp")

def load_pwc_panel() -> pd.DataFrame:
    """Returns cols: [benchmark, domain, model, date, score, quarter]"""
    # Filters: >=20 submissions, >=2yr history, 2018-2025, cv/nlp domains only

def label_saturation(panel: pd.DataFrame) -> pd.DataFrame:
    """Adds 'label' column: 'saturated'|'healthy'|'excluded'"""

def get_domain_panels(
    panel: pd.DataFrame,
    domain: str,
    min_saturated: int = 15,
    min_healthy: int = 15,
) -> tuple:  # (saturated_df, healthy_df)

# From: h-e1/code/evaluate.py (ACTUAL CODE)
def verify_mechanism_activated(domain_results: dict) -> tuple:
    """domain_results: {domain_str: {discriminability, signal_auc, ...}}
    Returns: (all_activated: bool, indicators: dict)
    NOTE: H-M1 defines its OWN verify_mechanism_activated with different signature!
    """

def check_gate_condition(domain_results: dict) -> tuple:
    """Returns: (passed: bool, gate_details: dict)"""

def save_results(results: dict, output_path: str) -> None:
    """Serializes to JSON with numpy type handling."""
```

**Note**: H-M1 `evaluate.py` defines its own `verify_mechanism_activated` and `check_gate_condition` with different signatures — do NOT import from H-E1. H-M1 only reuses `DOMAIN_MAP` and the loading pattern (re-implemented in `load_pwc_raw`).

---

## A-1: Data Pipeline [Complexity: 10]

### API Signatures

```python
# data_pipeline.py
import pandas as pd
import numpy as np
from datasets import load_dataset

DOMAIN_MAP: dict  # task_name -> "cv"|"nlp", reused from H-E1 pattern

def load_pwc_raw() -> pd.DataFrame:
    """Load raw PWC evaluation-tables from HuggingFace.
    Returns: DataFrame[task, dataset, model, evaluated_on, score, domain, quarter]
    """
    ...

def compute_quarterly_panel(
    pwc_raw: pd.DataFrame,
    min_submissions: int = 20,
    min_quarters: int = 8,
) -> pd.DataFrame:
    """Build (benchmark_id, quarter) panel. Filters benchmarks below thresholds.
    Returns: DataFrame[benchmark_id, task, dataset, quarter, submission_count,
                       cumulative_count, score_var_top10]
    """
    ...

def load_panel(
    min_submissions: int = 20,
    min_quarters: int = 8,
) -> tuple:
    """Top-level entry: load raw + compute panel.
    Returns: (pwc_raw: pd.DataFrame, panel_df: pd.DataFrame)
    """
    ...
```

### Data Schema

| Column | Type | Source |
|--------|------|--------|
| benchmark_id | str | f"{task}__{dataset}" |
| quarter | str | Period Q string e.g. "2022Q1" |
| submission_count | int | nunique(model) per quarter |
| cumulative_count | int | cumsum of submission_count |
| score_var_top10 | float | var of top-10 scores per quarter |

### Pseudo-code (compute_quarterly_panel)

```
1. Parse evaluated_on -> quarter Period
2. Group by (task, dataset):
   a. Filter: total unique models >= min_submissions
   b. Per quarter: submission_count = nunique(model), score_var_top10 = top10 scores var
   c. Compute cumulative_count = cumsum(submission_count)
   d. Filter: num quarters >= min_quarters
   e. Append to panels list
3. Concat all panels; assign benchmark_id = f"{task}__{dataset}"
4. Return panel DataFrame
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | load_pwc_raw | HuggingFace load + column normalization + domain mapping |
| L-1-2 | compute_quarterly_panel | Groupby + aggregation + filtering logic |
| L-1-3 | load_panel + schema validation | Top-level orchestration + assert column presence |

---

## A-2: Sigma Estimation [Complexity: 8]

### API Signatures

```python
# sigma_estimation.py
import pandas as pd
import numpy as np

def estimate_sigma_measurement(pwc_raw: pd.DataFrame) -> pd.Series:
    """Compute per-benchmark sigma from repeated model submissions.
    Groups by (task, dataset, model), takes std of score; then mean per benchmark.
    Fallback: NaN benchmarks get cross-benchmark median.
    Returns: Series indexed by (task, dataset), name='sigma_meas'
    """
    ...

def get_sigma_map(pwc_raw: pd.DataFrame) -> pd.Series:
    """Alias: calls estimate_sigma_measurement with fallback applied.
    Returns: Series indexed by (task, dataset), name='sigma_meas', no NaNs
    """
    ...
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | estimate_sigma_measurement | Repeated submission std + median fallback |
| L-2-2 | get_sigma_map | Wrapper ensuring no NaN sigma values |

---

## A-3: Compression Detector [Complexity: 9]

### API Signatures

```python
# compression_detector.py
import pandas as pd
import numpy as np

def flag_compression(
    panel_df: pd.DataFrame,
    sigma_map: pd.Series,
    threshold: float = 1.5,
    min_consecutive: int = 2,
) -> pd.DataFrame:
    """Merge sigma_map; add 'compressed' bool and 'compression_event' rolling indicator.
    panel_df must have columns: [benchmark_id, task, dataset, quarter, score_var_top10]
    sigma_map indexed by (task, dataset).
    Returns: panel_df + [sigma_meas, compressed, compression_event]
    """
    ...

def summarize_compression(panel_df: pd.DataFrame) -> dict:
    """Count compression events across panel.
    Returns: {'n_compression_events': int, 'n_qualifying_benchmarks': int,
              'pct_compressed': float}
    """
    ...
```

### Pseudo-code (flag_compression)

```
1. Merge sigma_map on (task, dataset) -> adds sigma_meas column
2. compressed = score_var_top10 < threshold * sigma_meas
3. Per benchmark_id group:
   compression_event = rolling(min_consecutive).min() on compressed (int)
   (== 1 only if all min_consecutive trailing rows are compressed)
4. Fill NaN compression_event with 0
5. Return merged DataFrame
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | flag_compression | Merge + threshold + rolling consecutive |
| L-3-2 | summarize_compression | Aggregate event counts |

---

## A-4: Spearman Baseline [Complexity: 6]

### API Signatures

```python
# spearman_baseline.py
import pandas as pd
from scipy.stats import spearmanr

def compute_spearman_baseline(panel_df: pd.DataFrame) -> dict:
    """Spearman rho between cumulative_count and compression_event.
    Drops rows with NaN in either column.
    Returns: {'rho': float, 'p_value': float, 'n_obs': int}
    """
    ...
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | compute_spearman_baseline | Validity check + spearmanr call + result dict |

---

## A-5: Granger Causality Core [Complexity: 14]

### API Signatures

```python
# granger_causality.py
import pandas as pd
import numpy as np
from statsmodels.tsa.stattools import grangercausalitytests, adfuller

def check_stationarity(series: pd.Series, alpha: float = 0.05) -> bool:
    """ADF test. Returns True if stationary (ADF p < alpha)."""
    ...

def make_stationary(
    series: pd.Series,
    alpha: float = 0.05,
    max_diff: int = 2,
) -> pd.Series:
    """Apply first-order differencing until stationary or max_diff reached.
    Fallback: log-transform then difference if still non-stationary.
    Returns: stationary series (may have fewer points)
    """
    ...

def test_granger_causality(
    benchmark_panel: pd.DataFrame,
    max_lag: int = 4,
) -> dict | None:
    """Per-benchmark Granger test: cumulative_count -> score_var_top10.
    Input: DataFrame sorted by quarter with cols [score_var_top10, cumulative_count].
    Returns: {lag: p_value} for lag in 1..max_lag, or None if insufficient data.
    """
    ...
```

### Pseudo-code (test_granger_causality — complex algorithm)

```
1. ts = benchmark_panel[['score_var_top10', 'cumulative_count']].dropna()
2. if len(ts) < max_lag + 5: return None  # insufficient obs
3. For each col in ['score_var_top10', 'cumulative_count']:
   a. if not check_stationarity(ts[col]):
      ts[col] = make_stationary(ts[col])
4. ts = ts.dropna()
5. if len(ts) < max_lag + 5: return None  # re-check after differencing
6. gc_res = grangercausalitytests(ts[['score_var_top10','cumulative_count']],
                                   maxlag=max_lag, verbose=False)
7. Return {lag: gc_res[lag][0]['ssr_ftest'][1] for lag in 1..max_lag}
   # ssr_ftest[1] = p-value of F-test for Granger causality at that lag
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | check_stationarity | ADF test wrapper returning bool |
| L-5-2 | make_stationary | Iterative differencing + log fallback |
| L-5-3 | test_granger_causality | ADF pre-check + differencing + grangercausalitytests |
| L-5-4 | Result parsing | Extract ssr_ftest p-values, handle statsmodels output structure |

---

## A-6: Reverse Causality & Panel Aggregation [Complexity: 12]

### API Signatures

```python
# granger_causality.py (continued)

def test_reverse_causality(
    benchmark_panel: pd.DataFrame,
    max_lag: int = 4,
) -> dict | None:
    """Test compression_event -> cumulative_count direction.
    Input: DataFrame with cols [cumulative_count, compression_event] sorted by quarter.
    Returns: {lag: p_value} or None if insufficient data.
    """
    ...

def run_granger_panel(
    panel_df: pd.DataFrame,
    max_lag: int = 4,
) -> tuple:
    """Run forward + reverse Granger for all benchmark_ids.
    Returns: (forward_results, reverse_results)
      Each dict: {benchmark_id: {lag: p_value} | None}
    """
    ...

def aggregate_granger_panel(
    granger_results: dict,
    target_lag: int = 2,
) -> dict:
    """Panel-level summary of per-benchmark Granger results.
    Returns: {'n_benchmarks_tested': int, 'n_significant_lag2': int,
              'pct_significant_lag2': float, 'min_p_lag2': float|None,
              'median_p_lag2': float|None}
    """
    ...
```

### Pseudo-code (run_granger_panel)

```
1. forward_results = {}; reverse_results = {}
2. For each benchmark_id in panel_df['benchmark_id'].unique():
   bm_df = panel_df[panel_df['benchmark_id'] == benchmark_id].sort_values('quarter')
   forward_results[benchmark_id] = test_granger_causality(bm_df, max_lag)
   reverse_results[benchmark_id] = test_reverse_causality(bm_df, max_lag)
3. Return (forward_results, reverse_results)
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-6-1 | test_reverse_causality | Mirror of forward test with swapped column order |
| L-6-2 | run_granger_panel | Loop over benchmarks, call both forward + reverse |
| L-6-3 | aggregate_granger_panel | Filter valid results, compute pct/min/median p-values |

---

## A-7: Evaluate & Gate [Complexity: 9]

### API Signatures

```python
# evaluate.py
import json
import pandas as pd
import numpy as np

def verify_mechanism_activated(
    panel_df: pd.DataFrame,
    granger_results: dict,
    spearman_result: dict,
) -> tuple:
    """Check all H-M1 mechanism activation criteria.
    Returns: (activated: bool, indicators: dict)
    indicators keys: panel_constructed, sufficient_benchmarks, spearman_computed,
                     granger_computed, spearman_significant, granger_significant_lag2
    NOTE: Different signature from H-E1 verify_mechanism_activated — do NOT import from H-E1.
    """
    ...

def check_gate_condition(
    spearman_result: dict,
    granger_agg: dict,
) -> tuple:
    """PASS if spearman rho>0.4 AND p<0.05, OR granger min_p_lag2<0.05.
    Returns: (gate_passed: bool, gate_details: dict)
    """
    ...

def save_results(results: dict, output_path: str) -> None:
    """Serialize results dict to JSON with numpy type handling."""
    ...
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-7-1 | verify_mechanism_activated | All 6 indicator checks + activation logic |
| L-7-2 | check_gate_condition + save_results | Gate logic (OR of primary/secondary) + JSON output |

---

## A-8: Visualization [Complexity: 10]

### API Signatures

```python
# visualize.py
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

def plot_gate_metrics(
    spearman_result: dict,
    granger_agg: dict,
    output_dir: str,
) -> None:
    """Bar chart: target vs actual Spearman rho and Granger p at lag=2.
    Saves: gate_metrics.png
    """
    ...

def plot_scatter_submission_compression(
    panel_df: pd.DataFrame,
    output_dir: str,
) -> None:
    """Scatter: cumulative_count vs compression_event, colored by domain.
    Saves: scatter_submission_compression.png
    """
    ...

def plot_lag_profile(
    granger_results: dict,
    reverse_results: dict,
    output_dir: str,
) -> None:
    """Median Granger p-values at lags 1-4 for forward and reverse directions.
    Saves: lag_profile.png
    """
    ...

def plot_timeseries_overlay(
    panel_df: pd.DataFrame,
    output_dir: str,
    example_benchmark: str | None = None,
) -> None:
    """Dual-panel time series for one benchmark (auto-selected if None).
    Saves: timeseries_overlay.png
    """
    ...

def plot_compression_distribution(
    panel_df: pd.DataFrame,
    output_dir: str,
) -> None:
    """Histogram of cumulative_count at first compression event.
    Saves: compression_distribution.png
    """
    ...

def plot_reverse_causality(
    forward_results: dict,
    reverse_results: dict,
    output_dir: str,
) -> None:
    """Bar chart: median p-value at lag=2 for forward vs reverse direction.
    Saves: reverse_causality.png
    """
    ...

def generate_all_figures(
    panel_df: pd.DataFrame,
    spearman_result: dict,
    granger_results: dict,
    reverse_results: dict,
    granger_agg: dict,
    output_dir: str,
) -> None:
    """Call all 6 plot functions. Creates output_dir if not exists."""
    ...
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-8-1 | gate_metrics + scatter + lag_profile | 3 core figures |
| L-8-2 | timeseries + compression_dist + reverse + generate_all | 3 additional + orchestrator |

---

## A-9: Entry Point [Complexity: 8]

### API Signatures

```python
# run_experiment.py
import argparse
import numpy as np
import pandas as pd

CONFIG = {
    "seed": 42,
    "min_submissions": 20,
    "min_quarters": 8,
    "compression_threshold": 1.5,
    "min_consecutive": 2,
    "granger_max_lag": 4,
    "spearman_rho_target": 0.4,
    "granger_p_target": 0.05,
    "output_dir": "figures/",
    "results_json": "results.json",
    "results_csv": "results.csv",
}

def parse_args(config: dict, args=None) -> dict:
    """Override CONFIG defaults with CLI args. Returns merged config dict."""
    ...

def main(args=None) -> None:
    """Orchestrate all 10 pipeline steps; print gate result; save CSV + JSON."""
    ...
```

### Pseudo-code (main)

```
1. cfg = parse_args(CONFIG, args); np.random.seed(cfg['seed'])
2. pwc_raw, panel_df = load_panel(cfg['min_submissions'], cfg['min_quarters'])
3. sigma_map = get_sigma_map(pwc_raw)
4. panel_df = flag_compression(panel_df, sigma_map,
                cfg['compression_threshold'], cfg['min_consecutive'])
5. spearman_result = compute_spearman_baseline(panel_df)
6. forward_results, reverse_results = run_granger_panel(panel_df, cfg['granger_max_lag'])
7. granger_agg = aggregate_granger_panel(forward_results, target_lag=2)
8. activated, indicators = verify_mechanism_activated(panel_df, forward_results, spearman_result)
9. gate_passed, gate_details = check_gate_condition(spearman_result, granger_agg)
10. generate_all_figures(panel_df, spearman_result, forward_results,
                         reverse_results, granger_agg, cfg['output_dir'])
11. results = {spearman_result, granger_agg, gate_details, indicators, ...}
12. save_results(results, cfg['results_json'])
13. pd.DataFrame([results]).to_csv(cfg['results_csv'])
14. print GATE: PASS/FAIL
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-9-1 | parse_args + main | CONFIG + argparse + 10-step orchestration |

---

## Full Subtask Summary

| ID | Task | Description |
|----|------|-------------|
| L-1-1 | load_pwc_raw | HuggingFace load + column normalization + domain mapping |
| L-1-2 | compute_quarterly_panel | Groupby + aggregation + filtering |
| L-1-3 | load_panel | Top-level orchestration + schema validation |
| L-2-1 | estimate_sigma_measurement | Repeated submission std + median fallback |
| L-2-2 | get_sigma_map | Wrapper ensuring no NaN sigma values |
| L-3-1 | flag_compression | Merge + threshold + rolling consecutive |
| L-3-2 | summarize_compression | Aggregate event counts |
| L-4-1 | compute_spearman_baseline | Validity check + spearmanr + result dict |
| L-5-1 | check_stationarity | ADF test wrapper |
| L-5-2 | make_stationary | Iterative differencing + log fallback |
| L-5-3 | test_granger_causality | Full per-benchmark Granger pipeline |
| L-5-4 | Granger result parsing | ssr_ftest p-value extraction |
| L-6-1 | test_reverse_causality | Reverse direction Granger |
| L-6-2 | run_granger_panel | Loop + call both directions |
| L-6-3 | aggregate_granger_panel | Panel summary stats |
| L-7-1 | verify_mechanism_activated | 6-indicator check |
| L-7-2 | check_gate_condition + save_results | OR gate + JSON serialization |
| L-8-1 | gate_metrics + scatter + lag_profile | 3 core figures |
| L-8-2 | timeseries + compression_dist + reverse + generate_all | 3 additional figures |
| L-9-1 | parse_args + main | Entry point + orchestration |

**Total: 20 subtasks across 9 epics (budget: 15 — A-5 expanded to 4 per complexity-14)**
