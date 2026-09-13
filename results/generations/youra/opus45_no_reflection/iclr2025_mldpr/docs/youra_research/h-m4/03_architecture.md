# Architecture: H-M4 (Traditional Benchmark Persistence with Reduced Dominance)

**Type:** MECHANISM | **Applied:** Time-series share/count stability testing pattern (statistical, no ML model)

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** green-field - no code to analyze (statistical analysis, no base hypothesis code dependency)
**Analyzed Path:** N/A
**Findings:** New implementation from scratch; no prior H-M3 code reuse required (data-source overlap only).

---

## File Organization

```
h-m4/code/
  config.py          # constants: benchmarks, date boundary, thresholds
  data_loader.py      # HF dataset loading + preprocessing
  metrics.py           # share/count computation + gate checks
  stats.py              # Mann-Whitney significance test
  visualize.py          # 4 required figures
  run_experiment.py     # orchestration entrypoint
  results.yaml           # output (generated)
figures/
  gate_metrics.png, share_timeseries.png, stacked_area.png, per_benchmark.png
```

## Modules

### config.py

```python
TRADITIONAL_BENCHMARKS: list[str] = ["imagenet", "imagenet-1k", "cifar-10", "cifar-100"]
SPLIT_DATE: str = "2020-01"
COUNT_RATIO_BOUNDS: tuple[float, float] = (0.8, 1.2)
DATE_RANGE: tuple[str, str] = ("2018-01", "2024-12")
```

### data_loader.py (`code/data_loader.py`)

**Dependencies**: config

```python
def load_pwc_data() -> tuple["Dataset", "Dataset"]:
    """Loads pwc-archive/evaluation-tables and pwc-archive/datasets."""
def extract_paper_benchmark_records(eval_tables, datasets_meta) -> pd.DataFrame:
    """Returns DataFrame[paper_id, dataset_name, date]."""
def filter_date_range(df: pd.DataFrame, start: str, end: str) -> pd.DataFrame: ...
```

### metrics.py (`code/metrics.py`)

**Dependencies**: config, pandas

```python
def compute_monthly_metrics(eval_data: pd.DataFrame) -> pd.DataFrame:
    """Returns DataFrame[month, traditional_count, total_count, share]."""
def split_pre_post(monthly: pd.DataFrame, split_date: str) -> tuple[pd.DataFrame, pd.DataFrame]: ...
def evaluate_gate(pre: pd.DataFrame, post: pd.DataFrame, ratio_bounds: tuple[float, float]) -> dict:
    """Returns dict with share_decreased, counts_stable, count_ratio, gate_pass, means."""
```

### stats.py (`code/stats.py`)

**Dependencies**: scipy

```python
def mann_whitney_share_test(pre_shares: pd.Series, post_shares: pd.Series) -> tuple[float, float]:
    """Returns (statistic, p_value), alternative='greater'."""
def per_benchmark_stability(eval_data: pd.DataFrame, benchmarks: list[str], split_date: str) -> dict[str, float]:
    """Per-benchmark count ratio, for secondary metric P2."""
```

### visualize.py (`code/visualize.py`)

**Dependencies**: metrics, matplotlib

```python
def plot_gate_metrics(gate_result: dict, out_path: str) -> None: ...
def plot_share_timeseries(monthly: pd.DataFrame, split_date: str, out_path: str) -> None: ...
def plot_stacked_area(eval_data: pd.DataFrame, monthly: pd.DataFrame, out_path: str) -> None: ...
def plot_per_benchmark(eval_data: pd.DataFrame, benchmarks: list[str], out_path: str) -> None: ...
```

### run_experiment.py (`code/run_experiment.py`)

**Dependencies**: all modules above

```python
def main() -> None:
    """Load -> preprocess -> compute metrics -> gate eval -> stats -> figures -> write results.yaml."""
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Config setup | Define constants (benchmarks, thresholds, date range) | 4 | 1+1+1+1 |
| A-2 | Data loading | Load HF datasets, join eval-tables + datasets metadata | 10 | 3+3+2+2 |
| A-3 | Record extraction | Build paper-benchmark DataFrame with dates, filter range | 8 | 2+2+2+2 |
| A-4 | Monthly aggregation | Group by month, compute traditional/total counts + share | 8 | 2+2+3+1 |
| A-5 | Pre/post split & gate eval | Split at 2020-01, compute means, ratio, gate_pass | 7 | 2+2+2+1 |
| A-6 | Significance testing | Mann-Whitney U test, per-benchmark stability (P2) | 6 | 2+1+2+1 |
| A-7 | Required visualization | Gate metrics bar chart (mandatory figure) | 5 | 2+1+1+1 |
| A-8 | Additional visualizations | Time series, stacked area, per-benchmark breakdown | 10 | 3+2+3+2 |
| A-9 | Orchestration & output | run_experiment.py wiring, results.yaml, error handling | 8 | 2+3+1+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-2, A-8], Low(4-8): [A-1, A-3, A-4, A-5, A-6, A-7, A-9]
