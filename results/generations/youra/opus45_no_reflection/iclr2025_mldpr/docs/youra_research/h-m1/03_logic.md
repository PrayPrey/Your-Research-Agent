# Logic: H-M1 (Foundation Model Emergence Timeline)

Applied: statistical-field-normalization-pattern (z-score comparison against reference distribution)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

---

## A-2: Semantic Scholar client + caching [Complexity: 12, Budget: 5]

**Applied**: disk-cache-key-hash-pattern (JSON-serializable cache key -> sha256 -> pickle/json file)

### API Signatures

```python
class DataCollector:
    def __init__(self, cache_dir: str = "cache/", rate_limit_sleep: float = 1.0):
        """Init cache dir and SemanticScholar client."""
        ...

    def fetch_foundation_papers(self, paper_ids: list[str]) -> list[dict]:
        """Batch fetch via sch.get_papers(paper_ids). Returns list of paper dicts."""
        ...

    def fetch_comparison_set(
        self, years: list[int], venues: list[str], min_per_year: int = 1000
    ) -> list[dict]:
        """Bulk search per (year, venue), dedup by paperId. Returns flat list."""
        ...

    def _cached_get(self, key: str, fetch_fn: Callable[[], dict]) -> dict:
        """Return cached JSON at cache_dir/{sha256(key)}.json if exists, else call fetch_fn, save, return."""
        ...

    def _rate_limited_call(self, fn: Callable[[], Any]) -> Any:
        """Call fn(), sleep(rate_limit_sleep), retry on 429 with exponential backoff (max 3)."""
        ...
```

### Tensor Shapes

| Variable | Type | Note |
|----------|------|------|
| paper dict | `{paperId: str, title: str, citationCount: int, year: int, venue: str}` | per API |

### Pseudo-code (rate-limit + cache)

```
1. key = f"{fn_name}:{sorted(args)}"
2. cache_path = cache_dir / sha256(key).hexdigest() + ".json"
3. if cache_path.exists(): return json.load(cache_path)
4. try: result = fetch_fn()
   except HTTPError as 429: sleep(backoff); retry (max 3)
5. json.dump(result, cache_path)
6. return result
```

### Subtasks [3/5 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-A2-1 | Cache layer | `_cached_get` with sha256 key, JSON disk cache |
| L-A2-2 | SemanticScholar wrapper | init client, `fetch_foundation_papers` via batch endpoint |
| L-A2-3 | Rate-limit/retry | `_rate_limited_call` with sleep + exponential backoff on 429 |

---

## A-4: Fetch comparison set [Complexity: 13, Budget: 2 remaining]

### API Signatures

```python
def fetch_comparison_set(
    self, years: list[int], venues: list[str], min_per_year: int = 1000
) -> list[dict]:
    """
    For each year: bulk search across venues until >= min_per_year unique papers.
    Returns: list[dict] len >= min_per_year * len(years)
    """
    ...

def _bulk_search_year(self, year: int, venues: list[str], target: int) -> list[dict]:
    """sch.search_paper(query='machine learning', year=str(year), venue=venues,
    fields_of_study=['Computer Science'], bulk=True, fields=['citationCount','year','venue'])
    Paginate until len(results) >= target or exhausted."""
    ...
```

### Pseudo-code

```
1. all_papers = []
2. for year in years:
3.     year_papers = _bulk_search_year(year, venues, min_per_year)  # cached per year
4.     all_papers.extend(year_papers)
5. dedup by paperId
6. return all_papers  # list[dict], len >= 1000 * len(years)
```

### Subtasks [2/5 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-A4-1 | Bulk search + pagination | `_bulk_search_year`, cursor-based paging until target size |
| L-A4-2 | Dedup + cache orchestration | dedup by paperId, cache per-year result via `_cached_get` |

---

## A-6: Z-score computation + gate logic [Complexity: 8, Budget: 0 remaining — folded into A-4/A-2 design]

### API Signatures

```python
class StatsEngine:
    def compute_field_stats(self, comparison_papers: list[dict]) -> dict:
        """{'mean': float, 'std': float, 'n': int} from citationCount field."""
        ...

    def compute_zscore(self, citation_count: int, field_mean: float, field_std: float) -> float:
        """(citation_count - field_mean) / field_std"""
        ...

    def compute_percentile(self, citation_count: int, field_citations: list[int]) -> float:
        """scipy.stats.percentileofscore(field_citations, citation_count)"""
        ...

    def evaluate_gate(self, foundation_results: dict) -> bool:
        """foundation_results: {paper_id: {'z_score': float, 'exceeds_2sigma': bool, ...}}
        Pass if sum(exceeds_2sigma) >= GATE_MIN_PASSING (3)."""
        ...
```

### Tensor Shapes

| Variable | Shape/Type | Note |
|----------|------|------|
| foundation_results | `dict[str, dict]` | keyed by paper_id, 5 entries |
| field_citations | `list[int]` | len >= 3000 |

---

## Visualizer (`visualizer.py`)

**Applied**: Standard matplotlib bar/hist patterns

```python
class Visualizer:
    def __init__(self, output_dir: str = "figures/"):
        ...

    def plot_zscore_bar(self, foundation_results: dict) -> str:
        """Bar chart of z-scores per paper, horizontal line at y=2.0. Returns saved path."""
        ...

    def plot_citation_histogram(self, field_citations: list[int], foundation_results: dict) -> str:
        """Histogram of field_citations, vertical lines/markers at each foundation paper's citation count."""
        ...

    def plot_percentile_table(self, foundation_results: dict) -> str:
        """matplotlib table: paper | citations | z_score | percentile. Returns saved path."""
        ...
```

---

## Pipeline (`run_experiment.py`)

```python
def main() -> dict:
    """
    Orchestrates: fetch -> stats -> zscore -> gate -> figures -> report.
    Returns: {'gate_pass': bool, 'foundation_results': dict, 'field_stats': dict, 'figures': list[str]}
    """
    ...
```

### Pseudo-code

```
1. dc = DataCollector(); se = StatsEngine(); viz = Visualizer()
2. foundation = dc.fetch_foundation_papers(FOUNDATION_PAPERS)
3. comparison = dc.fetch_comparison_set(YEARS, VENUES, MIN_PAPERS_PER_YEAR)
4. field_stats = se.compute_field_stats(comparison)
5. field_citations = [p['citationCount'] for p in comparison]
6. foundation_results = {}
7. for p in foundation:
8.     z = se.compute_zscore(p['citationCount'], field_stats['mean'], field_stats['std'])
9.     pct = se.compute_percentile(p['citationCount'], field_citations)
10.    foundation_results[p['paperId']] = {title, citations, z_score: z, exceeds_2sigma: z > 2.0, percentile: pct}
11. gate_pass = se.evaluate_gate(foundation_results)
12. figures = [viz.plot_zscore_bar(...), viz.plot_citation_histogram(...), viz.plot_percentile_table(...)]
13. write report (json/md) with gate_pass, foundation_results, field_stats
14. return {gate_pass, foundation_results, field_stats, figures}
```

---

## Config (`config.py`)

```python
FOUNDATION_PAPERS: list[str] = ["ARXIV:2005.14165", "ARXIV:2010.11929", "ACL:N19-1423",
                                 "ARXIV:1907.11692", "ARXIV:1910.10683"]
VENUES: list[str] = ["NeurIPS", "ICML", "ACL", "CVPR"]
YEARS: list[int] = [2019, 2020, 2021]
MIN_PAPERS_PER_YEAR: int = 1000
ZSCORE_THRESHOLD: float = 2.0
GATE_MIN_PASSING: int = 3
```

---

## External Dependencies

None — green-field, no base hypothesis code.
