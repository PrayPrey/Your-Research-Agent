# Architecture: H-M4 (MECHANISM Validation)

**Hypothesis:** Reduced diversity hides benchmark-specific overfitting (low entropy venue-years show higher cross-benchmark variance).

Applied: no relevant KB pattern found (searched "DL experiment architecture cross-benchmark variance" — top hit similarity 0.465, unrelated diffusion-model repos); using standard PWC meta-analysis pattern from H-M3 (data_loader → analyze → visualize), extended with entropy join from H-E1.

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-M3) — not yet built
**Status**: `h-m3/code/` does not exist (glob returned no files). H-M3 architecture spec exists but unimplemented, same as when H-M3 itself was scoped. No importable modules from base hypothesis.
**Analyzed Path**: `h-m3/code/` (absent)
**Findings**: Reusing H-M3's *pattern* (data_loader.py / analyze.py / visualize.py split, VENUES/YEARS constants, seed=42) rather than importing code. New implementation from scratch, own copy of PWC loader extended for multi-benchmark filtering + H-E1 entropy join.

---

## File Structure (Minimal — statistical analysis, not a training pipeline)

```
h-m4/code/
├── data_loader.py   # PWC load+filter, multi-benchmark paper selection, H-E1 entropy load
├── variance.py       # metric normalization, per-paper CV, venue-year aggregation
├── analyze.py         # entrypoint: spearman correlation, per-venue, gate check
└── visualize.py       # required + additional figures
```

Single entrypoint (`analyze.py`), no config.py (few constants: VENUES, YEARS, SEED, MIN_PAPERS_PER_VY).

---

## Modules

### data_loader.py

**Dependencies**: pandas, datasets (HF), json, pathlib

```python
VENUES = ("NeurIPS", "ICML", "ICLR")
YEARS = range(2018, 2025)
PWC_CACHE = "pwc-archive/papers-with-abstracts"
E1_RESULTS_PATH = "h-e1/results/"

def load_multi_benchmark_papers() -> pd.DataFrame:
    """Load PWC papers, filter to VENUES/YEARS, keep papers with results on
    2+ benchmarks of same task type. Returns DataFrame[paper_id, venue, year,
    benchmark_results(list[dict])] where each dict has
    {benchmark, metric_name, metric_value, higher_is_better}."""
    ...

def load_entropy_by_venue_year() -> dict[tuple[str, int], float]:
    """Load H-E1 HHI/entropy results, key by (venue, year). 21 entries expected."""
    ...
```

### variance.py

**Dependencies**: numpy

```python
def normalize_metrics(benchmarks: list[dict]) -> list[dict]:
    """Min-max scale metric_value to [0,1] per benchmark; flip if
    higher_is_better=False. Returns list with added 'normalized_score'."""
    ...

def compute_cross_benchmark_variance(paper: dict) -> float | None:
    """CV = std(normalized_scores) / mean(normalized_scores). None if <2 benchmarks
    or mean <= 0."""
    ...

def aggregate_venue_year(papers_df: pd.DataFrame, min_papers: int = 10) -> pd.DataFrame:
    """Compute per-paper CV, group by (venue, year), mean CV per group.
    Drop venue-years with < min_papers. Returns DataFrame[venue, year, mean_cv, n_papers]."""
    ...
```

### analyze.py (entrypoint)

**Dependencies**: data_loader, variance, scipy.stats, numpy, visualize

```python
def run_correlation_test(
    entropy_by_vy: dict[tuple[str, int], float], variance_by_vy: pd.DataFrame
) -> dict:
    """Align on common (venue, year) keys. Spearman rho + p over aggregate,
    then per-venue (>=3 venue-years required). Returns
    {spearman_rho, p_value, n_venue_years, per_venue: {venue: {rho, p, n}}}."""
    ...

def gate_check(results: dict) -> bool:
    """rho < 0 AND p_value < 0.05 AND count(v for v in per_venue if per_venue[v]['rho'] < 0) >= 2."""
    ...

def main() -> None:
    """1. load_multi_benchmark_papers() 2. load_entropy_by_venue_year()
    3. aggregate_venue_year() 4. run_correlation_test() + gate_check()
    5. visualize.generate_all() 6. save results dict to results/."""
    ...
```

### visualize.py

**Dependencies**: matplotlib/seaborn, analyze (results dict + aggregated df)

```python
def plot_gate_metrics(results: dict, agg_df: pd.DataFrame, out_path: str) -> None:
    """Scatter: entropy vs mean_cv, regression line + CI band, color by venue,
    annotate rho/p. -> figures/gate_metrics.png"""
    ...

def plot_entropy_variance_scatter(agg_df: pd.DataFrame, out_path: str) -> None: ...
def plot_per_venue_correlation(results: dict, out_path: str) -> None: ...
def plot_variance_by_entropy_quartile(agg_df: pd.DataFrame, out_path: str) -> None: ...

def generate_all(results: dict, agg_df: pd.DataFrame, out_dir: str = "figures/") -> None: ...
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | PWC multi-benchmark loading | Load PWC papers, filter venues/years, select papers with 2+ same-task benchmarks | 6 | 2+1+2+1 |
| A-2 | H-E1 entropy loading | Load and key entropy results by (venue, year) | 3 | 1+1+0+1 |
| A-3 | Metric normalization | Min-max scale + direction handling per benchmark type | 5 | 2+1+2+0 |
| A-4 | Per-paper CV computation | Coefficient of variation over normalized scores, edge-case handling | 4 | 1+1+1+1 |
| A-5 | Venue-year aggregation | Group by (venue, year), mean CV, min-N filter (>=10 papers) | 4 | 1+1+1+1 |
| A-6 | Spearman correlation (aggregate) | Align entropy/variance keys, compute rho + p-value | 4 | 1+1+2+0 |
| A-7 | Per-venue correlation + gate check | Per-venue spearman (min 3 venue-years), gate logic (2/3 venues) | 6 | 1+2+2+1 |
| A-8 | Visualization | 4 figures (gate scatter, detailed scatter, per-venue bar, quartile box plots) | 7 | 3+1+1+2 |
| A-9 | Pipeline integration | Wire main(), save results.json, log excluded papers, run end-to-end | 5 | 1+2+1+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [], Low(4-8): [A-1, A-2, A-3, A-4, A-5, A-6, A-7, A-8, A-9]

---

## Dependencies (external)

- pandas, numpy
- scipy.stats (spearmanr)
- matplotlib, seaborn
- datasets (HuggingFace, PWC load)
- H-E1 results directory (input, no import — file read only)
