# Architecture: H-M1 (Foundation Model Emergence Timeline)

Applied: statistical-field-normalization-pattern (z-score comparison against reference distribution)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze
**Analyzed Path**: N/A
**Findings**: New implementation from scratch; no base hypothesis code reuse. Statistical/API analysis task, not ML training.

---

## Module Structure

### DataCollector (`data_collector.py`)

**Dependencies**: semanticscholar

```python
class DataCollector:
    def __init__(self, cache_dir: str = "cache/"): ...
    def fetch_foundation_papers(self, paper_ids: list[str]) -> list[dict]: ...
    def fetch_comparison_set(self, years: list[int], venues: list[str], min_per_year: int = 1000) -> list[dict]: ...
    def _cached_get(self, key: str, fetch_fn: callable) -> dict: ...
```

### StatsEngine (`stats_engine.py`)

**Dependencies**: numpy, scipy

```python
class StatsEngine:
    def compute_field_stats(self, comparison_papers: list[dict]) -> dict: ...  # {mean, std}
    def compute_zscore(self, citation_count: int, field_mean: float, field_std: float) -> float: ...
    def compute_percentile(self, citation_count: int, field_citations: list[int]) -> float: ...
    def evaluate_gate(self, foundation_results: dict) -> bool: ...  # >=3/5 z>2.0
```

### Visualizer (`visualizer.py`)

**Dependencies**: matplotlib, StatsEngine

```python
class Visualizer:
    def __init__(self, output_dir: str = "figures/"): ...
    def plot_zscore_bar(self, foundation_results: dict) -> str: ...  # gate figure, 2sigma line
    def plot_citation_histogram(self, field_citations: list[int], foundation_results: dict) -> str: ...
    def plot_percentile_table(self, foundation_results: dict) -> str: ...
```

### Pipeline (`run_experiment.py`)

**Dependencies**: DataCollector, StatsEngine, Visualizer

```python
def main() -> dict: ...  # orchestrates fetch -> stats -> gate -> figures -> report
```

### Config (`config.py`)

```python
FOUNDATION_PAPERS = ["ARXIV:2005.14165", "ARXIV:2010.11929", "ACL:N19-1423",
                      "ARXIV:1907.11692", "ARXIV:1910.10683"]
VENUES = ["NeurIPS", "ICML", "ACL", "CVPR"]
YEARS = [2019, 2020, 2021]
MIN_PAPERS_PER_YEAR = 1000
ZSCORE_THRESHOLD = 2.0
GATE_MIN_PASSING = 3
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Config setup | Define paper IDs, venues, thresholds | 4 | 1+1+1+1 |
| A-2 | Semantic Scholar client + caching | API wrapper with rate-limit handling, disk cache | 12 | 3+3+3+3 |
| A-3 | Fetch foundation papers | Batch fetch 5 target papers | 6 | 2+2+1+1 |
| A-4 | Fetch comparison set | Bulk search 1000+/year across venues, 2019-2021 | 13 | 3+4+3+3 |
| A-5 | Field statistics computation | mean/std/percentile via numpy/scipy | 6 | 2+1+2+1 |
| A-6 | Z-score computation + gate logic | Per-paper z-score, exceeds_2sigma, gate evaluation | 8 | 2+2+3+1 |
| A-7 | Bar chart (gate figure) | Z-scores vs 2sigma threshold line | 6 | 2+1+1+2 |
| A-8 | Histogram + percentile table | Distribution plot, percentile ranking table | 7 | 2+1+2+2 |
| A-9 | End-to-end pipeline + report | Orchestration script, pass/fail report output | 9 | 2+3+2+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-2, A-4, A-6, A-9], Low(4-8): [A-1, A-3, A-5, A-7, A-8]

---

## External Dependencies

None — green-field, no base hypothesis code.

## Notes

- No ablation/baseline model modules — this is statistical analysis, not ML training (per PRD/brief: "Not applicable - training protocol").
- Caching (A-2) mitigates API rate-limit risk (NFR-1) and reproducibility (NFR-2).
