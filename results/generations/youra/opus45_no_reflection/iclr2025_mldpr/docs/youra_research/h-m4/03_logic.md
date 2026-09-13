# Logic: H-M4 (Traditional Benchmark Persistence)

## Codebase Analysis (Serena)

**Project Type**: green-field (no base_hypothesis code dependency; H-M3 checked for pattern reference only, not called)
**Status**: New implementation. Reused loading pattern from `h-m3/code/data_collection.py::fetch_from_huggingface_fallback` (HF dataset load + alias matching), adapted to `pwc-archive/evaluation-tables` join.
**Analyzed Path**: `docs/youra_research/h-m3/code/data_collection.py`
**Relevant Symbols**: `fetch_from_huggingface_fallback`, `collect_paper_counts` (reference only, not imported)

Applied: HF datasets load_dataset + pandas join pattern (from h-m3 precedent)

---

## A-2: Data Loading [Complexity: 10, Budget: 2 subtasks]

**Applied**: HuggingFace `datasets.load_dataset` + pandas join (KB: no direct match found; used codebase precedent)

### API Signatures

```python
# code/data_loader.py
from datasets import load_dataset, Dataset
import pandas as pd

def load_pwc_data() -> tuple[Dataset, Dataset]:
    """Load pwc-archive/evaluation-tables and pwc-archive/datasets, split='train'."""
    eval_tables = load_dataset("pwc-archive/evaluation-tables", split="train")
    datasets_meta = load_dataset("pwc-archive/datasets", split="train")
    return eval_tables, datasets_meta


def extract_paper_benchmark_records(
    eval_tables: Dataset,
    datasets_meta: Dataset,
) -> pd.DataFrame:
    """Join eval rows to dataset metadata on dataset name; derive month.
    Returns DataFrame[paper_id: str, dataset_name: str, date: str, month: str]
    """
    ...


def filter_date_range(
    df: pd.DataFrame,
    start: str,  # "YYYY-MM"
    end: str,    # "YYYY-MM"
) -> pd.DataFrame:
    """Filter df['month'] to [start, end] inclusive."""
    return df[(df["month"] >= start) & (df["month"] <= end)]
```

### Pseudo-code (join + date derivation — non-trivial due to schema mismatch across the two HF datasets)

```
1. eval_df = eval_tables.to_pandas()      # cols: paper_id/paper_url, dataset (name), metric rows
2. meta_df = datasets_meta.to_pandas()    # cols: name, introduced_date, full_name
3. eval_df["dataset_name_norm"] = eval_df["dataset"].str.lower().str.strip()
4. meta_df["dataset_name_norm"] = meta_df["name"].str.lower().str.strip()
5. merged = eval_df.merge(meta_df[["dataset_name_norm", "introduced_date"]],
                            on="dataset_name_norm", how="left")
6. date = merged["introduced_date"].fillna(merged.get("eval_date"))  # fallback if present
7. drop rows where date is null; month = date[:7]
8. return DataFrame[paper_id, dataset_name, date, month].drop_duplicates()
```

### Tensor Shapes / Schema

| Variable | Type | Note |
|----------|------|------|
| eval_tables | HF Dataset | raw evaluation-tables rows |
| datasets_meta | HF Dataset | raw datasets metadata rows |
| merged df | pd.DataFrame[N, 4] | paper_id, dataset_name, date, month |

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-A2-1 | HF load + normalize | `load_pwc_data`; lowercase/strip dataset name keys for join |
| L-A2-2 | Join + extract | `extract_paper_benchmark_records` merge, date derivation, `filter_date_range` |

---

## Metrics Computation (metrics.py)

**Applied**: pandas groupby monthly aggregation (standard pattern)

```python
# code/metrics.py
import pandas as pd

def compute_monthly_metrics(eval_data: pd.DataFrame) -> pd.DataFrame:
    """Group by month; count unique paper_id in TRADITIONAL_BENCHMARKS vs total.
    Returns DataFrame[month: str, traditional_count: int, total_count: int, share: float]
    """
    ...

def split_pre_post(
    monthly: pd.DataFrame, split_date: str
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """pre = month < split_date, post = month >= split_date."""
    pre = monthly[monthly["month"] < split_date]
    post = monthly[monthly["month"] >= split_date]
    return pre, post
```

---

## Gate Evaluation Logic (metrics.py)

```python
def evaluate_gate(
    pre: pd.DataFrame,
    post: pd.DataFrame,
    ratio_bounds: tuple[float, float] = (0.8, 1.2),
) -> dict:
    """
    pre_share_mean = pre["share"].mean()
    post_share_mean = post["share"].mean()
    pre_count_mean = pre["traditional_count"].mean()
    post_count_mean = post["traditional_count"].mean()
    count_ratio = post_count_mean / pre_count_mean

    share_decreased = post_share_mean < pre_share_mean
    counts_stable = ratio_bounds[0] <= count_ratio <= ratio_bounds[1]
    gate_pass = share_decreased and counts_stable

    Returns:
      {
        "pre_share_mean": float, "post_share_mean": float,
        "pre_count_mean": float, "post_count_mean": float,
        "count_ratio": float,
        "share_decreased": bool, "counts_stable": bool,
        "gate_pass": bool,
      }
    """
    ...
```

---

## Significance Testing (stats.py)

```python
from scipy.stats import mannwhitneyu

def mann_whitney_share_test(
    pre_shares: pd.Series, post_shares: pd.Series
) -> tuple[float, float]:
    """mannwhitneyu(pre_shares, post_shares, alternative='greater'). Returns (statistic, p_value)."""
    ...

def per_benchmark_stability(
    eval_data: pd.DataFrame, benchmarks: list[str], split_date: str
) -> dict[str, float]:
    """For each benchmark: count_ratio = post_count/pre_count (paper_id nunique). P2 metric."""
    ...
```

---

## Results Output Schema (results.yaml)

```yaml
hypothesis: H-M4
gate: SHOULD_WORK
gate_pass: bool
metrics:
  pre_share_mean: float
  post_share_mean: float
  pre_count_mean: float
  post_count_mean: float
  count_ratio: float
  share_decreased: bool
  counts_stable: bool
significance:
  mann_whitney_statistic: float
  mann_whitney_p_value: float
per_benchmark_stability:
  imagenet: float
  imagenet-1k: float
  cifar-10: float
  cifar-100: float
figures:
  - figures/gate_metrics.png
  - figures/share_timeseries.png
  - figures/stacked_area.png
  - figures/per_benchmark.png
```

`run_experiment.py::main()` writes this via `yaml.safe_dump(results, f)` after wiring: load -> extract -> filter -> compute_monthly_metrics -> split_pre_post -> evaluate_gate -> mann_whitney_share_test -> per_benchmark_stability -> plot_* -> write results.yaml.
