# Architecture: H-M3 (MECHANISM Validation)

**Hypothesis:** Citing papers use same benchmarks as cited papers (citation drives benchmark comparability).

Applied: no relevant KB pattern found (searched "citation network analysis architecture" — only unrelated arxiv results, similarity <0.42); using standard PWC+S2 API pattern from experiment brief (semantic-scholar-skills, paper_network_builder references).

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-M2) — but not yet built
**Status**: `h-m2/code/` does not exist (glob returned no files). H-M2 architecture spec exists but is unimplemented. Falling back to specs; no importable modules.
**Analyzed Path**: `h-m2/code/` (absent)
**Findings**: H-M2 spec defines `data_loader.py::load_papers() -> DataFrame[paper_id, venue, year, datasets_used]`. H-M3 reuses this pattern locally (own copy) rather than importing unbuilt code — same PWC source, extended with S2 citation fetch. No code to import; new implementation from scratch.

---

## File Structure (Minimal — statistical analysis, not a training pipeline)

```
h-m3/code/
├── data_loader.py   # PWC papers load+filter; S2 citation fetch+cache
├── overlap.py        # Jaccard computation, citing-pair + random-pair construction
├── analyze.py        # entrypoint: stats test, gate check
└── visualize.py       # required + additional figures
```

Single entrypoint (`analyze.py`), no config.py (few constants: VENUES, YEARS, SEED).

---

## Modules

### data_loader.py

**Dependencies**: pandas, requests, datasets (HF), os

```python
VENUES = ("NeurIPS", "ICML", "ICLR")
YEARS = range(2018, 2025)
S2_BASE = "https://api.semanticscholar.org/graph/v1"
CACHE_DIR = "cache/"

def load_papers() -> pd.DataFrame:
    """Load PWC papers-with-abstracts, filter to VENUES/YEARS, require
    non-empty dataset tags. Returns DataFrame[paper_id, venue, year, datasets(list[str])]."""
    ...

def fetch_citations(paper_id: str, api_key: str) -> list[dict]:
    """Query S2 citations endpoint for paper_id, cache response to
    CACHE_DIR/{paper_id}.json. Exponential backoff on 429."""
    ...

def build_citation_pairs(papers_df: pd.DataFrame, api_key: str) -> pd.DataFrame:
    """For each paper in scope, fetch citations, keep only citing/cited pairs
    both within papers_df. Returns DataFrame[citing_id, cited_id, venue_year]."""
    ...
```

### overlap.py

**Dependencies**: pandas, random, numpy

```python
def jaccard_similarity(set1: set, set2: set) -> float:
    """Standard Jaccard; 0.0 if both empty."""
    ...

def sample_random_pairs(paper_ids: list[str], n_pairs: int, seed: int = 42) -> list[tuple[str, str]]:
    """Sample n_pairs random (p1, p2) without replacement per venue-year."""
    ...

def compute_citation_dataset_overlap(
    papers_df: pd.DataFrame, citations_df: pd.DataFrame, seed: int = 42
) -> tuple[list[float], list[float]]:
    """Per venue-year: Jaccard for citing pairs + matched-N random pairs.
    Returns (citing_overlaps, random_overlaps)."""
    ...
```

### analyze.py (entrypoint)

**Dependencies**: data_loader, overlap, scipy.stats, numpy, visualize

```python
def run_statistical_test(citing_overlaps: list[float], random_overlaps: list[float]) -> dict:
    """Mann-Whitney U (alternative='greater') + Cohen's d.
    Returns {mann_whitney_stat, p_value, mean_citing_overlap, mean_random_overlap,
    cohens_d, n_citing_pairs, n_random_pairs}."""
    ...

def gate_check(metrics: dict) -> bool:
    """p_value < 0.01 AND cohens_d > 0.3 AND n_citing_pairs >= 1000."""
    ...

def main() -> None:
    """1. load_papers() 2. build_citation_pairs()
    3. compute_citation_dataset_overlap()
    4. run_statistical_test() + gate_check()
    5. visualize.generate_all() 6. save results dict to results/."""
    ...
```

### visualize.py

**Dependencies**: matplotlib/seaborn, analyze (metrics dict + overlap lists)

```python
def plot_gate_metrics(metrics: dict, out_path: str) -> None: ...
def plot_overlap_distribution(citing_overlaps: list[float], random_overlaps: list[float], out_path: str) -> None: ...
def plot_venue_year_heatmap(papers_df: pd.DataFrame, citations_df: pd.DataFrame, out_path: str) -> None: ...
def generate_all(metrics: dict, citing_overlaps: list[float], random_overlaps: list[float],
                  papers_df: pd.DataFrame, citations_df: pd.DataFrame, out_dir: str = "figures/") -> None: ...
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | PWC data loading | Load papers-with-abstracts, filter venues/years, extract dataset tags | 5 | 2+1+1+1 |
| A-2 | S2 citation fetch + cache | Query S2 API per paper, exponential backoff, local JSON cache | 8 | 2+3+1+2 |
| A-3 | Citation pair construction | Build citing/cited pairs within venue scope, both must have dataset tags | 6 | 2+2+1+1 |
| A-4 | Jaccard overlap computation | Implement + validate Jaccard similarity function | 3 | 1+0+1+1 |
| A-5 | Random pair baseline | Matched-N random sampling per venue-year with seed | 4 | 1+1+1+1 |
| A-6 | Overlap distribution pipeline | Wire citing/random overlap computation across all venue-years | 6 | 2+2+1+1 |
| A-7 | Statistical test | Mann-Whitney U + Cohen's d, gate_check | 5 | 1+1+2+1 |
| A-8 | Visualization | 3 figures (gate metrics, distribution histograms, venue-year heatmap) | 7 | 3+1+1+2 |
| A-9 | Pipeline integration | Wire main(), save results.json, run end-to-end | 5 | 1+2+1+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [], Low(4-8): [A-1, A-2, A-3, A-4, A-5, A-6, A-7, A-8, A-9]

---

## Dependencies (external)

- pandas, numpy
- requests (S2 API)
- scipy.stats (mannwhitneyu)
- matplotlib, seaborn
- datasets (HuggingFace, PWC load)
- S2_API_KEY environment variable
