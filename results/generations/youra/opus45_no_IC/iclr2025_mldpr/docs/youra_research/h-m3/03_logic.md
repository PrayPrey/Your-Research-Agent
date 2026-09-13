# Logic: H-M3 (Citation-Benchmark Overlap Analysis)

**Applied**: no relevant KB pattern found (similarity <0.37, unrelated HF/diffusers results); using standard scipy.stats + pandas pattern from PRD.

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: `h-m2/code/` does not exist (confirmed absent in 03_architecture.md). No base hypothesis code to import; no existing `src/` in this repo path. New implementation from scratch.
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

---

## A-1/A-2/A-3: data_loader.py [Complexity: Low, Budget: 0 subtasks]

```python
import os
import time
import json
import requests
import pandas as pd

VENUES = ("NeurIPS", "ICML", "ICLR")
YEARS = range(2018, 2025)
S2_BASE = "https://api.semanticscholar.org/graph/v1"
CACHE_DIR = "cache/"

def load_papers() -> pd.DataFrame:
    """Load PWC papers-with-abstracts, filter venues/years, require non-empty datasets.
    Returns DataFrame[paper_id: str, venue: str, year: int, datasets: list[str]]."""
    ...

def fetch_citations(paper_id: str, api_key: str) -> list[dict]:
    """Query S2 /paper/{id}/citations, cache to CACHE_DIR/{paper_id}.json.
    Exponential backoff on HTTP 429. Returns list of {citingPaper: {paperId}}."""
    ...

def build_citation_pairs(papers_df: pd.DataFrame, api_key: str) -> pd.DataFrame:
    """Fetch citations per paper in papers_df, keep pairs where both citing/cited
    are in papers_df. Returns DataFrame[citing_id, cited_id, venue_year: str]."""
    ...
```

### Tensor / Data Shapes

| Variable | Shape/Type | Note |
|----------|-----------|------|
| papers_df | DataFrame, ~12000 rows | cols: paper_id, venue, year, datasets(list) |
| citations_df | DataFrame, ~50000+ rows | cols: citing_id, cited_id, venue_year |

---

## A-4/A-5/A-6: overlap.py [Complexity: Low, Budget: 0 subtasks]

```python
import random
import pandas as pd

def jaccard_similarity(set1: set, set2: set) -> float:
    """Standard Jaccard; 0.0 if both empty."""
    if not set1 and not set2:
        return 0.0
    union = len(set1 | set2)
    return len(set1 & set2) / union if union > 0 else 0.0

def sample_random_pairs(paper_ids: list[str], n_pairs: int, seed: int = 42) -> list[tuple[str, str]]:
    """Sample n_pairs random (p1, p2) without replacement, within given paper_ids scope."""
    ...

def compute_citation_dataset_overlap(
    papers_df: pd.DataFrame, citations_df: pd.DataFrame, seed: int = 42
) -> tuple[list[float], list[float]]:
    """Per venue-year group: Jaccard for each citation pair + matched-N random pairs
    (sampled via sample_random_pairs). Returns (citing_overlaps, random_overlaps)."""
    ...
```

### Pseudo-code (per venue-year loop)

```
for venue_year, group in citations_df.groupby('venue_year'):
    citing_datasets = lookup(papers_df, group.citing_id) -> list[set[str]]
    cited_datasets  = lookup(papers_df, group.cited_id)  -> list[set[str]]
    citing_overlaps += [jaccard_similarity(a, b) for a, b in zip(citing_datasets, cited_datasets)]

    scope_ids = papers_df[papers_df.venue_year == venue_year].paper_id
    random_pairs = sample_random_pairs(scope_ids, n_pairs=len(group), seed=seed)
    random_overlaps += [jaccard_similarity(dataset_set(p1), dataset_set(p2)) for p1, p2 in random_pairs]

return citing_overlaps, random_overlaps
```

---

## A-7: analyze.py (entrypoint) [Complexity: Low, Budget: 0 subtasks]

```python
from scipy.stats import mannwhitneyu
import numpy as np

def run_statistical_test(citing_overlaps: list[float], random_overlaps: list[float]) -> dict:
    """Mann-Whitney U (alternative='greater') + Cohen's d.
    Returns {mann_whitney_stat, p_value, mean_citing_overlap, mean_random_overlap,
    cohens_d, n_citing_pairs, n_random_pairs}."""
    ...

def gate_check(metrics: dict) -> bool:
    """p_value < 0.01 AND cohens_d > 0.3 AND n_citing_pairs >= 1000."""
    return metrics["p_value"] < 0.01 and metrics["cohens_d"] > 0.3 and metrics["n_citing_pairs"] >= 1000

def main() -> None:
    """1. load_papers() 2. build_citation_pairs()
    3. compute_citation_dataset_overlap()
    4. run_statistical_test() + gate_check()
    5. visualize.generate_all() 6. save results dict (Appendix schema) to results/results.json."""
    ...
```

### Cohen's d formula

```
pooled_std = sqrt((var(citing_overlaps) + var(random_overlaps)) / 2)
cohens_d = (mean(citing_overlaps) - mean(random_overlaps)) / pooled_std
```

---

## A-8: visualize.py [Complexity: Low, Budget: 0 subtasks]

```python
import pandas as pd

def plot_gate_metrics(metrics: dict, out_path: str) -> None:
    """Bar chart: mean citing vs random overlap, 95% CI error bars,
    annotated p-value + Cohen's d. Saves to h-m3/figures/gate_metrics.png."""
    ...

def plot_overlap_distribution(citing_overlaps: list[float], random_overlaps: list[float], out_path: str) -> None:
    """Side-by-side histograms, citing vs random overlap distributions."""
    ...

def plot_venue_year_heatmap(papers_df: pd.DataFrame, citations_df: pd.DataFrame, out_path: str) -> None:
    """Heatmap of Cohen's d effect size per venue-year cell."""
    ...

def generate_all(
    metrics: dict, citing_overlaps: list[float], random_overlaps: list[float],
    papers_df: pd.DataFrame, citations_df: pd.DataFrame, out_dir: str = "figures/"
) -> None:
    """Calls plot_gate_metrics, plot_overlap_distribution, plot_venue_year_heatmap."""
    ...
```

---

## Subtasks

None — all tasks Low complexity (4-8), budget 0 subtasks per allocation.
