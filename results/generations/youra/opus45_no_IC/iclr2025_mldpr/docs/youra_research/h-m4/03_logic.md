# Logic: H-M4 (MECHANISM Validation)

**Applied**: no relevant KB pattern found (searched "statistical analysis API patterns scipy" — top hit similarity 0.41, unrelated diffusion-model repos); using standard scipy.stats.spearmanr + pandas groupby pattern.

## Codebase Analysis (Serena)

Green-field project - no existing code. H-M4 is a fresh statistical analysis module; H-M3 base code does not exist yet (per architecture doc), so no prior implementation to verify signatures against.

---

## A-1/A-2: data_loader.py [Complexity: 6+3, Budget: 9]

```python
from dataclasses import dataclass
import pandas as pd
from pathlib import Path

VENUES = ("NeurIPS", "ICML", "ICLR")
YEARS = range(2018, 2025)
PWC_CACHE = "pwc-archive/papers-with-abstracts"
E1_RESULTS_PATH = "h-e1/results/"

def load_multi_benchmark_papers(
    pwc_cache: str = PWC_CACHE,
    venues: tuple[str, ...] = VENUES,
    years: range = YEARS,
) -> pd.DataFrame:
    """Load PWC, filter venue/year, keep papers with 2+ same-task-type
    benchmark results. Returns df[paper_id, venue, year, benchmark_results]
    where benchmark_results: list[dict(benchmark, metric_name, metric_value,
    higher_is_better, task_type)]."""
    ...

def load_entropy_by_venue_year(
    e1_path: str = E1_RESULTS_PATH,
) -> dict[tuple[str, int], float]:
    """Load H-E1 entropy/HHI json, key by (venue, year). 21 entries expected."""
    ...
```

### Pseudo-code (multi-benchmark selection)

```
1. load raw PWC records (HF datasets.load_dataset or local parquet)
2. filter venue in VENUES, year in YEARS
3. group results by paper_id -> list of (benchmark, metric, task_type)
4. keep paper if group_by(task_type) has any task_type with >=2 distinct benchmarks
5. log excluded paper_ids (insufficient benchmarks) to results/excluded_papers.json
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | PWC raw load + venue/year filter | HF dataset load, filter |
| L-1-2 | Multi-benchmark task-type grouping | group_by paper_id/task_type, >=2 check |
| L-1-3 | H-E1 entropy load + keying | json read, (venue,year) dict |

---

## A-3/A-4: variance.py [Complexity: 5+4, Budget: 9]

```python
import numpy as np

def normalize_metrics(benchmarks: list[dict]) -> list[dict]:
    """Min-max scale metric_value to [0,1] within each benchmark's paper group;
    flip (1 - x) if higher_is_better=False. Adds 'normalized_score' key."""
    ...

def compute_cross_benchmark_variance(paper: dict) -> float | None:
    """CV = std(normalized_scores) / mean(normalized_scores).
    None if <2 benchmarks or mean <= 0."""
    benchmarks = paper["benchmark_results"]
    if len(benchmarks) < 2:
        return None
    normalized = normalize_metrics(benchmarks)
    values = np.array([m["normalized_score"] for m in normalized])
    return float(np.std(values) / np.mean(values)) if np.mean(values) > 0 else 0.0

def aggregate_venue_year(
    papers_df: pd.DataFrame, min_papers: int = 10
) -> pd.DataFrame:
    """Compute per-paper CV, groupby (venue, year), mean CV.
    Drop groups with n_papers < min_papers.
    Returns df[venue, year, mean_cv, n_papers, paper_ids]."""
    ...
```

**Note**: `normalize_metrics` min-max scaling requires cross-paper context per benchmark (min/max across all papers reporting that benchmark) — not per-paper. Implementation must first build per-benchmark min/max lookup table before scaling individual paper scores.

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | Per-benchmark min/max lookup + scaling | build lookup, apply, flip direction |
| L-3-2 | CV computation + venue-year aggregation | compute_cross_benchmark_variance + groupby |

---

## A-6/A-7: analyze.py [Complexity: 4+6, Budget: 10]

```python
from scipy.stats import spearmanr

def run_correlation_test(
    entropy_by_vy: dict[tuple[str, int], float],
    variance_by_vy: pd.DataFrame,
) -> dict:
    """Align on common (venue, year) keys. Spearman rho+p over aggregate;
    then per-venue (>=3 venue-years required, else omit from per_venue).
    Returns {spearman_rho, p_value, n_venue_years,
    per_venue: {venue: {rho, p, n}}}."""
    ...

def gate_check(results: dict) -> bool:
    """rho < 0 AND p_value < 0.05 AND
    count(v for v in per_venue if per_venue[v]['rho'] < 0) >= 2."""
    return (
        results["spearman_rho"] < 0
        and results["p_value"] < 0.05
        and sum(1 for v in results["per_venue"].values() if v["rho"] < 0) >= 2
    )

def main() -> None:
    """1. load_multi_benchmark_papers() 2. load_entropy_by_venue_year()
    3. aggregate_venue_year() 4. run_correlation_test() + gate_check()
    5. visualize.generate_all() 6. save results dict -> results/results.json."""
    ...
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-6-1 | Spearman aggregate + per-venue + gate | spearmanr calls, gate_check, main() wiring |

---

## A-8: visualize.py [Complexity: 7, Budget: 7]

```python
def plot_gate_metrics(
    results: dict, agg_df: pd.DataFrame, out_path: str = "figures/gate_metrics.png"
) -> None:
    """Scatter entropy(x) vs mean_cv(y), sns.regplot for line+CI band,
    hue=venue, annotate rho/p in title. Saves PNG."""
    ...

def plot_entropy_variance_scatter(
    agg_df: pd.DataFrame, out_path: str = "figures/entropy_variance_scatter.png"
) -> None:
    """Detailed scatter, marker per venue, size=n_papers."""
    ...

def plot_per_venue_correlation(
    results: dict, out_path: str = "figures/per_venue_correlation.png"
) -> None:
    """Bar chart: x=venue, y=rho from results['per_venue']."""
    ...

def plot_variance_by_entropy_quartile(
    agg_df: pd.DataFrame, out_path: str = "figures/variance_by_entropy_quartile.png"
) -> None:
    """pd.qcut(agg_df['entropy'], 4) -> boxplot of mean_cv per quartile."""
    ...

def generate_all(
    results: dict, agg_df: pd.DataFrame, out_dir: str = "figures/"
) -> None:
    """Calls all 4 plot functions with out_dir-prefixed paths."""
    ...
```

### Tensor/Array Shapes

| Variable | Shape/Type | Note |
|----------|-----------|------|
| agg_df | DataFrame[N<=21, 5] | cols: venue, year, mean_cv, n_papers, paper_ids |
| entropy_by_vy | dict[(str,int), float] | 21 entries expected |
| results['per_venue'][v]['rho'] | float | NaN-safe if n<3 |

### Subtasks [0/0 used — single unit, no further split]

Budget fully allocated to A-8 implementation as one task; no subtask breakdown needed (visualize functions are independent one-liners composed via generate_all).

---

## Total Subtasks: 6/6 used

| ID | Task |
|----|------|
| L-1-1 | PWC load + filter |
| L-1-2 | Multi-benchmark grouping |
| L-1-3 | H-E1 entropy load |
| L-3-1 | Metric normalization |
| L-3-2 | CV + aggregation |
| L-6-1 | Correlation + gate + main |
