# Architecture: H-M1 (MECHANISM Validation)

**Hypothesis:** High HHI indicates community convergence on few datasets

Applied: no domain-specific KB pattern found (searched "statistical validation architecture", "HHI concentration metrics" — only unrelated diffusion-training results returned); using standard scipy.stats group-comparison pattern.

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-E1)
**Status**: `h-e1/code/` does not exist yet (glob returned no files) — H-E1 produced only specs, not implementation. Falling back to `h-e1/03_architecture.md` as reference per fallback rule (no actual code to trust over spec in this case).
**Analyzed Path**: `h-e1/code/` (empty/absent)
**Findings**: H-E1 spec defines `metrics.py::compute_hhi(dataset_counts) -> float` and `analyze.py` pipeline producing a venue-year metrics DataFrame (columns include `venue`, `year`, `hhi`). H-M1 will reuse this DataFrame shape and recompute top5_share directly from raw task-category counts rather than importing unbuilt H-E1 modules. Cached data expected at `h-e1/data/pwc_papers_filtered.parquet`; if absent, HF fallback load per PRD FR-1.2.

---

## File Structure (Minimal — validation script, not a training pipeline)

```
h-m1/code/
├── data_loader.py   # load cached H-E1 parquet or HF fallback
├── validate.py      # top5_share, group split, stats tests, gate
└── visualize.py      # 4 required figures
```

Single entrypoint (`validate.py`), no config.py needed (constants are few and used once).

---

## Modules

### data_loader.py

**Dependencies**: pandas, datasets (HF, fallback only)

```python
CACHE_PATH = "h-e1/data/pwc_papers_filtered.parquet"

def load_papers() -> pd.DataFrame:
    """Load cached PWC papers; fallback to HF load_dataset if cache missing.
    Returns DataFrame[paper_id, venue, year, task_categories(list[str])]."""
    ...

def build_venue_year_table(papers_df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate to one row per venue-year with task_counts (pd.Series per row) and hhi.
    Returns DataFrame[venue, year, hhi, task_counts]."""
    ...

def compute_hhi(task_counts: pd.Series) -> float: ...
```

### validate.py (entrypoint)

**Dependencies**: data_loader, scipy.stats, visualize

```python
def compute_top5_share(task_counts: pd.Series) -> float: ...

def validate_hhi_interpretation(venue_year_df: pd.DataFrame) -> dict:
    """Adds top5_share col, splits by median HHI, runs Mann-Whitney U (greater)
    and Spearman. Returns dict with means, stat, p-values, rho, gate_passed."""
    ...

def verify_mechanism_activation(results: dict) -> bool:
    """PoC-level sanity checks: groups_differ, correlation_positive."""
    ...

def main() -> None:
    """1. load_papers() 2. build_venue_year_table()
    3. validate_hhi_interpretation() 4. verify_mechanism_activation()
    5. visualize.generate_all() 6. save results dict to results/."""
    ...
```

### visualize.py

**Dependencies**: matplotlib/seaborn, validate (results dict + venue_year_df)

```python
def plot_group_comparison_bar(results: dict, out_path: str) -> None: ...
def plot_hhi_vs_top5_scatter(venue_year_df: pd.DataFrame, out_path: str) -> None: ...
def plot_distribution_histograms(venue_year_df: pd.DataFrame, median_hhi: float, out_path: str) -> None: ...
def plot_venue_year_heatmap(venue_year_df: pd.DataFrame, out_path: str) -> None: ...
def generate_all(results: dict, venue_year_df: pd.DataFrame, out_dir: str = "figures/") -> None: ...
```

---

## External Dependencies (Base Hypothesis)

**Note**: H-E1 has no built `code/` yet; nothing importable exists at analysis time. H-M1 re-implements the small `compute_hhi` function locally (per spec in `h-e1/03_architecture.md` `metrics.py`) rather than importing, to avoid a hard dependency on unbuilt code.

| Module | Import Path | File Location |
|--------|-------------|----------------|
| Cached data | N/A (file read) | `h-e1/data/pwc_papers_filtered.parquet` |
| HHI formula (spec ref, reimplemented) | N/A | `h-e1/03_architecture.md` → `metrics.py::compute_hhi` |

**Verified from**: `h-e1/code/` (absent — confirmed via glob), spec fallback used.

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Data loading | Load H-E1 cached parquet, HF fallback | 5 | 2+2+1+0 |
| A-2 | Venue-year aggregation | Build per-venue-year task_counts + hhi table | 6 | 2+1+2+1 |
| A-3 | Top-5 share computation | compute_top5_share + apply across table | 4 | 1+0+2+1 |
| A-4 | Group split | Median split into high/low HHI groups, balance check | 3 | 1+0+1+1 |
| A-5 | Statistical tests | Mann-Whitney U (one-sided) + Spearman correlation | 6 | 1+2+3+0 |
| A-6 | Gate + mechanism verification | gate_passed logic, verify_mechanism_activation checks | 4 | 1+1+1+1 |
| A-7 | Visualization | 4 required figures (bar, scatter, histograms, heatmap) | 7 | 3+1+1+2 |
| A-8 | Pipeline integration | Wire main(), save results.json, run end-to-end | 5 | 1+2+1+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [], Low(4-8): [A-1, A-2, A-3, A-4, A-5, A-6, A-7, A-8]

---

## Dependencies (external)

- pandas, numpy
- scipy.stats (mannwhitneyu, spearmanr)
- matplotlib, seaborn
- datasets (HuggingFace, fallback only)
