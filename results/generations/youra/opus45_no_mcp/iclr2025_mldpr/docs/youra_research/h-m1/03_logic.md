# Logic: H-M1 (Bibliometric Study)

**Applied**: api-client-pattern (session-reused HTTP client + exponential backoff retry + disk JSON cache keyed by query)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: MCP unavailable this session (Serena not called). Per 03_architecture.md, h-e1/code/ contains only image data, no reusable modules. Designing all APIs new.
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

---

## Data Flow (DataFrame Schemas)

```
openml_client.fetch_vision_datasets()
  -> df[did:int, name:str, run_count:int, NumberOfInstances:int]
openml_client.select_high_low_groups(df)
  -> (high: list[dict{name, run_count}], low: list[dict{name, run_count}])
aggregate.build_dataset_records(high, low)
  -> df[name:str, group:{"high","low"}, run_count:int, paper_count:int]
stats.* consume this df -> dict results
visualize.* consume this df + dict results -> PNG files
gate.evaluate_gate(ratio_result, mw_result) -> dict -> report JSON
```

---

## A-3: Semantic Scholar Client [Complexity: 12, Budget: 12]

**Applied**: api-client-pattern (retry w/ exponential backoff + rate-limit sleep + disk cache)

### API Signatures

```python
# semantic_scholar_client.py
import requests, time, json, hashlib, os
from config import S2_API_URL, S2_RATE_LIMIT_SLEEP, CACHE_DIR

def build_query(dataset_name: str) -> str:
    """Build S2 search query string."""
    return f'"{dataset_name}" AND (architecture OR NAS OR hyperparameter OR tuning)'

def _cache_path(query: str) -> str:
    key = hashlib.md5(query.encode()).hexdigest()
    return os.path.join(CACHE_DIR, f"s2_{key}.json")

def _request_with_retry(params: dict, max_retries: int = 5) -> dict:
    """GET S2_API_URL with exponential backoff. Returns parsed JSON."""
    ...

def count_optimization_papers(dataset_name: str, use_cache: bool = True) -> int:
    """Query S2, return total paper count for dataset. Cached to disk."""
    ...
```

### Pseudo-code: Retry + Rate Limit

```
def _request_with_retry(params, max_retries=5):
    for attempt in range(max_retries):
        resp = requests.get(S2_API_URL, params=params, timeout=10)
        if resp.status_code == 200:
            time.sleep(S2_RATE_LIMIT_SLEEP)  # stay under 100 req/5min
            return resp.json()
        if resp.status_code == 429:
            wait = S2_RATE_LIMIT_SLEEP * (2 ** attempt)  # exponential backoff
            time.sleep(wait)
            continue
        if resp.status_code >= 500:
            time.sleep(2 ** attempt)
            continue
        resp.raise_for_status()  # 4xx non-429: fail fast
    raise RuntimeError(f"S2 request failed after {max_retries} retries")

def count_optimization_papers(dataset_name, use_cache=True):
    query = build_query(dataset_name)
    path = _cache_path(query)
    if use_cache and os.path.exists(path):
        return json.load(open(path))["count"]
    data = _request_with_retry({"query": query, "limit": 1})
    count = data.get("total", 0)
    if use_cache:
        json.dump({"query": query, "count": count}, open(path, "w"))
    return count
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | Query builder + cache key | `build_query`, `_cache_path` (md5 of query string) |
| L-3-2 | Retry/backoff HTTP call | `_request_with_retry`: 429 exponential backoff, 5xx retry, 4xx raise |
| L-3-3 | Cached count fetch | `count_optimization_papers`: cache-read/write wrapper around retry call |

---

## A-7: Visualization Suite [Complexity: 10, Budget: 10]

**Applied**: Standard matplotlib/seaborn (bar/box/scatter)

### API Signatures

```python
# visualize.py
import matplotlib.pyplot as plt
import seaborn as sns
from config import RATIO_THRESHOLD

def plot_gate_comparison(stats_result: dict, out_path: str) -> None:
    """Bar: high_use_avg vs low_use_avg with 3:1 threshold line. Required figure."""
    ...

def plot_per_dataset_bars(df: "pandas.DataFrame", out_path: str) -> None:
    """Grouped bar: paper_count per dataset, colored by group."""
    ...

def plot_boxplot(df: "pandas.DataFrame", out_path: str) -> None:
    """Boxplot: paper_count distribution by group (high vs low)."""
    ...

def plot_correlation_scatter(df: "pandas.DataFrame", corr: dict, out_path: str) -> None:
    """Scatter: run_count (x) vs paper_count (y), annotate rho/p from corr dict."""
    ...
```

### Tensor/Data Shapes

| Variable | Shape | Note |
|----------|-------|------|
| stats_result | dict | `{"high_use_avg", "low_use_avg", "ratio"}` |
| df | [20 rows, 4 cols] | name, group, run_count, paper_count |
| corr | dict | `{"rho", "p_value"}` |

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-7-1 | Gate comparison bar | `plot_gate_comparison`: 2-bar chart + horizontal threshold line at ratio=3.0 |
| L-7-2 | Per-dataset bars + boxplot | `plot_per_dataset_bars`, `plot_boxplot` (sns.barplot/sns.boxplot by group) |
| L-7-3 | Correlation scatter | `plot_correlation_scatter`: sns.regplot(run_count, paper_count), title shows rho/p |

---

## A-8: Pipeline Orchestration [Complexity: 9, Budget: 9]

**Applied**: Standard sequential pipeline w/ logging + try/except per stage

### API Signatures

```python
# run.py
import logging
from openml_client import fetch_vision_datasets, select_high_low_groups
from semantic_scholar_client import count_optimization_papers
from aggregate import build_dataset_records, save_records
from stats import compute_ratio, mannwhitney_test, spearman_correlation
from gate import evaluate_gate, write_gate_report
from visualize import (
    plot_gate_comparison, plot_per_dataset_bars,
    plot_boxplot, plot_correlation_scatter,
)

def main() -> None: ...
```

### Pseudo-code

```
def main():
    logging.basicConfig(level=logging.INFO)
    df_meta = fetch_vision_datasets()
    high, low = select_high_low_groups(df_meta)

    for group in (high, low):
        for d in group:
            d["paper_count"] = count_optimization_papers(d["name"])  # rate-limited

    df = build_dataset_records(high, low)
    save_records(df, "results/dataset_records.csv")

    ratio_result = compute_ratio(df)
    mw_result = mannwhitney_test(df)
    corr_result = spearman_correlation(df)

    gate_result = evaluate_gate(ratio_result, mw_result)
    write_gate_report(gate_result, "results/gate_report.json")

    plot_gate_comparison(ratio_result, "figures/gate_comparison.png")
    plot_per_dataset_bars(df, "figures/per_dataset_bars.png")
    plot_boxplot(df, "figures/boxplot.png")
    plot_correlation_scatter(df, corr_result, "figures/correlation_scatter.png")

    logging.info(f"Gate: {'PASS' if gate_result['pass_gate'] else 'FAIL'}")

if __name__ == "__main__":
    main()
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-8-1 | Data collection stage | fetch/select OpenML + loop S2 counts, error logging per dataset |
| L-8-2 | Analysis stage | aggregate, save_records, stats.* calls, gate evaluation + report write |
| L-8-3 | Figure generation stage | call all 4 plot functions, final PASS/FAIL log line |

---

## Statistical Test Implementations (stats.py, Complexity 8 - not subtask-allocated, direct spec)

```python
from scipy.stats import mannwhitneyu, spearmanr

def compute_ratio(df) -> dict:
    high_avg = df.loc[df.group == "high", "paper_count"].mean()
    low_avg = df.loc[df.group == "low", "paper_count"].mean()
    return {"high_use_avg": high_avg, "low_use_avg": low_avg,
            "ratio": high_avg / low_avg if low_avg else float("inf")}

def mannwhitney_test(df) -> dict:
    high = df.loc[df.group == "high", "paper_count"]
    low = df.loc[df.group == "low", "paper_count"]
    stat, p = mannwhitneyu(high, low, alternative="greater")
    return {"statistic": float(stat), "p_value": float(p)}

def spearman_correlation(df) -> dict:
    rho, p = spearmanr(df["run_count"], df["paper_count"])
    return {"rho": float(rho), "p_value": float(p)}
```
