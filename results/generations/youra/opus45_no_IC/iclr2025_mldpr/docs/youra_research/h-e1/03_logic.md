# Logic Design: H-E1 (EXISTENCE / PoC)

**Type:** Data analysis (HHI concentration), no model training.

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** Green-field - no existing code to analyze. New API design.
**Analyzed Path:** N/A
**Relevant Symbols:** None - new implementation

**Applied:** Standard pandas HHI/entropy computation (no DL-specific KB pattern applicable - this is econometric analysis, not model architecture)

---

## A-1: Data Loading [Complexity: Low, Budget: 2]

**Applied:** HuggingFace `datasets.load_dataset` bulk-download pattern

### API Signatures

```python
from datasets import load_dataset
import pandas as pd

def load_pwc_data() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Load papers-with-abstracts and evaluation-tables from HF Hub."""
    papers = load_dataset("pwc-archive/papers-with-abstracts", split="train").to_pandas()
    eval_tables = load_dataset("pwc-archive/evaluation-tables", split="train").to_pandas()
    return papers, eval_tables

def build_papers_df(papers: pd.DataFrame, eval_tables: pd.DataFrame) -> pd.DataFrame:
    """Join papers with dataset tags from eval_tables.
    Returns columns: ['paper_id', 'venue', 'year', 'datasets']
    'datasets' is a list[str] per paper (may be empty).
    """
    ...
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-1-1 | HF loader | `load_pwc_data()` with try/except -> fallback to `paperswithcode-client` if load fails |
| L-1-2 | Join builder | `build_papers_df()` maps paper_id -> list of dataset names via eval_tables |

---

## A-2: HHI & Entropy Metrics [Complexity: Low, Budget: 2]

**Applied:** Standard pandas HHI formula (Stack Overflow / DOJ methodology, verified in experiment brief)

### API Signatures

```python
def compute_hhi(dataset_counts: pd.Series) -> float:
    """HHI = sum(share_i^2). Returns NaN if total==0. Range [0,1]."""
    ...

def compute_entropy(dataset_counts: pd.Series) -> float:
    """Normalized Shannon entropy: -sum(p*log p)/log(N). Range [0,1]."""
    ...
```

### Pseudo-code

```
1. total = counts.sum(); if total == 0: return nan
2. shares = counts / total
3. hhi = sum(shares**2)
4. entropy: shares_nz = shares[shares>0]; H = -sum(shares_nz*log(shares_nz)); return H/log(len(shares_nz)) if len>1 else 0
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-2-1 | compute_hhi | Exact signature from experiment brief |
| L-2-2 | compute_entropy | Exact signature from experiment brief |

---

## A-3: Venue-Year Aggregation & Validation [Complexity: Low, Budget: 2]

**Applied:** Group-by + explode pandas pattern

### API Signatures

```python
def extract_venue_year_metrics(
    papers_df: pd.DataFrame,
    venues: list = ["NeurIPS", "ICML", "ICLR"],
    years: list = list(range(2018, 2025)),
) -> pd.DataFrame:
    """Returns DataFrame: ['venue','year','hhi','entropy','n_papers','n_unique_datasets']"""
    ...

def validate_hhi_scores(metrics_df: pd.DataFrame) -> Tuple[bool, Dict]:
    """Checks 21/21 non-null HHI, HHI in [0,1], variance>0. Returns (success, details)."""
    ...
```

### Tensor / Data Shapes

| Variable | Shape/Type | Note |
|----------|-----------|------|
| papers_df | DataFrame, N rows | cols: paper_id, venue, year, datasets(list) |
| metrics_df | DataFrame, ≤21 rows | one row per venue-year |

### Pseudo-code (extract_venue_year_metrics)

```
for venue in venues:
  for year in years:
    subset = papers_df[(venue==v) & (year==y)]
    if empty: continue
    exploded = subset.explode('datasets')
    counts = exploded['datasets'].value_counts()
    append(venue, year, compute_hhi(counts), compute_entropy(counts), len(subset), len(counts))
return DataFrame(results)
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-3-1 | extract_venue_year_metrics | Exact signature from brief; explode-based aggregation |
| L-3-2 | validate_hhi_scores | Gate check: valid_count==21, in_range, variance>0 |

---

## A-4: Visualization [Complexity: Low, Budget: 1]

**Applied:** matplotlib/seaborn standard plotting

### API Signatures

```python
def plot_gate_metrics(details: Dict, save_path: str) -> None:
    """Mandatory bar chart: HHI coverage 21/21."""
    ...

def plot_hhi_heatmap(metrics_df: pd.DataFrame, save_path: str) -> None:
    """Venue (rows) x Year (cols) heatmap of hhi."""
    ...

def plot_hhi_timeseries(metrics_df: pd.DataFrame, save_path: str) -> None:
    """Line plot: hhi over year, one line per venue."""
    ...
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-4-1 | Figure generation | All figures saved to `{hypothesis_folder}/figures/`; pivot table via `metrics_df.pivot(index='venue', columns='year', values='hhi')` for heatmap |

---

## Total Subtask Budget: 7/8 used (within LIGHT tier)
