# Architecture: H-E1 (EXISTENCE / PoC)

**Hypothesis:** HHI concentration measurable from PWC data for NeurIPS/ICML/ICLR (2018-2024)

Applied: standard pandas HHI/entropy computation pattern (no ML-specific KB pattern found; data-analysis pipeline is out of KB domain)

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze
**Analyzed Path**: N/A
**Findings**: New implementation from scratch. No base hypothesis, no existing `src/` codebase.

---

## File Structure (Minimal - EXISTENCE tier)

```
h-e1/code/
├── data_loader.py     # HF dataset loading + PWC API fallback
├── metrics.py          # HHI / entropy computation
├── analyze.py          # main pipeline: load -> filter -> compute -> validate -> visualize
└── config.py            # venues, years, thresholds
```

No `model.py`/`train.py` — this is observational data analysis, not model training.

---

## Modules

### config.py

```python
VENUES = ["NeurIPS", "ICML", "ICLR"]
YEARS = list(range(2018, 2025))
MIN_PAPERS_PER_VENUE_YEAR = 100
EXPECTED_VENUE_YEAR_COUNT = 21
OUTPUT_DIR = "results/"
FIGURES_DIR = "figures/"
```

### data_loader.py

**Dependencies**: config

```python
def load_pwc_data() -> pd.DataFrame:
    """Try HuggingFace datasets first, fallback to PWC API client.
    Returns DataFrame[paper_id, venue, year, datasets(list[str])]."""
    ...

def _load_from_huggingface() -> pd.DataFrame: ...
def _load_from_pwc_api() -> pd.DataFrame: ...
def _normalize_venue_names(df: pd.DataFrame) -> pd.DataFrame: ...
```

### metrics.py

**Dependencies**: none (pandas/numpy only)

```python
def compute_hhi(dataset_counts: pd.Series) -> float: ...
def compute_entropy(dataset_counts: pd.Series) -> float: ...
def extract_venue_year_metrics(
    papers_df: pd.DataFrame, venues: list, years: list
) -> pd.DataFrame: ...
def validate_hhi_scores(metrics_df: pd.DataFrame) -> tuple[bool, dict]: ...
```

### analyze.py (entrypoint)

**Dependencies**: data_loader, metrics, config

```python
def main() -> None:
    """1. load_pwc_data() 2. extract_venue_year_metrics()
    3. validate_hhi_scores() 4. save results + generate figures."""
    ...

def plot_heatmap(metrics_df: pd.DataFrame, out_path: str) -> None: ...
def plot_time_series(metrics_df: pd.DataFrame, out_path: str) -> None: ...
def plot_coverage_bar(details: dict, out_path: str) -> None: ...
def plot_entropy_vs_hhi(metrics_df: pd.DataFrame, out_path: str) -> None: ...
def plot_top_datasets(papers_df: pd.DataFrame, out_path: str) -> None: ...
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Setup config | Define venues/years/thresholds constants | 3 | 1+1+1+0 |
| A-2 | Data loading | HF dataset load + PWC API fallback + venue normalization | 10 | 3+3+2+2 |
| A-3 | Data filtering/extraction | Filter venue/year, explode dataset tags, aggregate counts | 6 | 2+1+2+1 |
| A-4 | HHI/entropy computation | Implement compute_hhi, compute_entropy, extract_venue_year_metrics | 7 | 2+1+3+1 |
| A-5 | Validation | validate_hhi_scores: coverage/range/variance checks + gate logic | 5 | 1+1+2+1 |
| A-6 | Visualization | Heatmap, time series, coverage bar, entropy scatter, top datasets | 9 | 3+1+2+3 |
| A-7 | Main pipeline integration | Wire analyze.py end-to-end, save results/provenance metadata | 6 | 1+3+1+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-2, A-4, A-6], Low(4-8): [A-1, A-3, A-5, A-7]

---

## Dependencies (external)

- pandas, numpy
- datasets (HuggingFace)
- matplotlib, seaborn
- paperswithcode-client (fallback only)
