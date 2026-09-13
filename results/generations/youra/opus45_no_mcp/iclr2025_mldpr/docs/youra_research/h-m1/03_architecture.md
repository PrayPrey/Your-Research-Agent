# Architecture: H-M1 (Bibliometric Study)

**Applied**: bibliometric-pipeline-pattern (OpenML run-count ranking + Semantic Scholar paper-count query + Mann-Whitney U gate)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: MCP unavailable this session; h-e1/code/ inspected via Glob and contains only CIFAR/CINIC image data (no reusable Python modules) — treated as green-field for h-m1.
**Analyzed Path**: `docs/youra_research/h-e1/code/`
**Findings**: No prior bibliometric/API code to reuse. New implementation from scratch.

---

## File Structure

```
h-m1/code/
  config.py
  openml_client.py
  semantic_scholar_client.py
  aggregate.py
  stats.py
  visualize.py
  gate.py
  run.py
  cache/           # cached API responses (NFR-1)
  results/         # intermediate + final JSON/CSV outputs
  figures/         # 4 required PNGs
```

---

## Modules

### config.py

**Dependencies**: none

```python
VISION_KEYWORDS: list[str] = ["cifar", "mnist", "imagenet", "svhn", "fashion"]
N_HIGH: int = 10
N_LOW: int = 10
RATIO_THRESHOLD: float = 3.0
P_THRESHOLD: float = 0.05
S2_API_URL: str = "https://api.semanticscholar.org/graph/v1/paper/search"
S2_RATE_LIMIT_SLEEP: float = 3.1  # ~100 req/5min
CACHE_DIR: str = "cache/"
RESULTS_DIR: str = "results/"
FIGURES_DIR: str = "figures/"
```

### openml_client.py (`h-m1/code/openml_client.py`)

**Dependencies**: config

```python
def fetch_vision_datasets() -> "pandas.DataFrame": ...
def select_high_low_groups(df: "pandas.DataFrame") -> tuple[list[dict], list[dict]]: ...
```

### semantic_scholar_client.py (`h-m1/code/semantic_scholar_client.py`)

**Dependencies**: config

```python
def build_query(dataset_name: str) -> str: ...
def count_optimization_papers(dataset_name: str, use_cache: bool = True) -> int: ...
def _request_with_retry(params: dict, max_retries: int = 5) -> dict: ...
```

### aggregate.py (`h-m1/code/aggregate.py`)

**Dependencies**: openml_client, semantic_scholar_client

```python
def build_dataset_records(high: list[dict], low: list[dict]) -> "pandas.DataFrame":
    # columns: name, group[high|low], run_count, paper_count
    ...
def save_records(df: "pandas.DataFrame", path: str) -> None: ...
```

### stats.py (`h-m1/code/stats.py`)

**Dependencies**: aggregate (DataFrame input)

```python
def compute_ratio(df: "pandas.DataFrame") -> dict:
    # {"high_use_avg": float, "low_use_avg": float, "ratio": float}
    ...
def mannwhitney_test(df: "pandas.DataFrame") -> dict:
    # {"statistic": float, "p_value": float}
    ...
def spearman_correlation(df: "pandas.DataFrame") -> dict:
    # {"rho": float, "p_value": float}
    ...
```

### visualize.py (`h-m1/code/visualize.py`)

**Dependencies**: aggregate, stats

```python
def plot_gate_comparison(stats_result: dict, out_path: str) -> None: ...   # required figure
def plot_per_dataset_bars(df: "pandas.DataFrame", out_path: str) -> None: ...
def plot_boxplot(df: "pandas.DataFrame", out_path: str) -> None: ...
def plot_correlation_scatter(df: "pandas.DataFrame", corr: dict, out_path: str) -> None: ...
```

### gate.py (`h-m1/code/gate.py`)

**Dependencies**: stats

```python
def evaluate_gate(ratio_result: dict, mw_result: dict) -> dict:
    # {"pass_gate": bool, "ratio": float, "p_value": float}
    ...
def write_gate_report(gate_result: dict, path: str) -> None: ...
```

### run.py (`h-m1/code/run.py`)

**Dependencies**: all modules above

```python
def main() -> None:
    # 1. fetch_vision_datasets -> select_high_low_groups
    # 2. count_optimization_papers per dataset -> build_dataset_records
    # 3. compute_ratio, mannwhitney_test, spearman_correlation
    # 4. evaluate_gate -> write_gate_report
    # 5. generate all 4 figures
    ...
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Config + project scaffold | config.py, dirs, dependency check | 4 | 1+1+1+1 |
| A-2 | OpenML client | fetch + filter + rank + split high/low | 8 | 2+2+2+2 |
| A-3 | Semantic Scholar client | query builder, HTTP retry/backoff, rate-limit sleep, disk cache | 12 | 3+3+3+3 |
| A-4 | Aggregation module | merge OpenML + S2 results into single DataFrame, persist | 6 | 2+2+1+1 |
| A-5 | Statistical analysis | ratio, Mann-Whitney U, Spearman correlation | 8 | 2+2+3+1 |
| A-6 | Gate evaluation | pass/fail decision, report writer | 4 | 1+1+1+1 |
| A-7 | Visualization suite | 4 required matplotlib/seaborn figures | 10 | 3+2+2+3 |
| A-8 | Pipeline orchestration | run.py wiring all modules, logging, error handling | 9 | 2+3+2+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-3, A-5, A-7, A-8], Low(4-8): [A-1, A-2, A-4, A-6]

---

## External Dependencies (Base Hypothesis)

None. h-e1/code/ contains only CIFAR/CINIC image dataset files, no reusable Python modules or bibliometric utilities. h-m1 implemented from scratch.
