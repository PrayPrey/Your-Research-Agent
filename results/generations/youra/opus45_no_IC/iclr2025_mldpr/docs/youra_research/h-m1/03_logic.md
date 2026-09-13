# Logic: H-M1 (MECHANISM Validation)

**Hypothesis:** High HHI indicates community convergence on few datasets

Applied: standard scipy.stats group-comparison pattern (mannwhitneyu + spearmanr); KB search for "scipy stats API" / "statistical validation" returned no relevant results (unrelated repos only).

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-E1)
**Status**: `h-e1/code/` does not exist yet — confirmed absent. Using `h-e1/03_architecture.md` spec as reference for the `compute_hhi` formula instead of verified code (none exists to verify against).
**Analyzed Path**: N/A (no code to query via Serena)
**Relevant Symbols**: None - H-M1 reimplements `compute_hhi` locally per H-E1 spec rather than importing unbuilt code.

Subtask budget: 0 (all tasks Low complexity per architecture; no breakdown needed).

---

## Module: data_loader.py

```python
CACHE_PATH = "h-e1/data/pwc_papers_filtered.parquet"

def load_papers() -> pd.DataFrame:
    """Load cached PWC papers; fallback to HF load_dataset if cache missing."""
    ...

def build_venue_year_table(papers_df: pd.DataFrame) -> pd.DataFrame:
    """One row per venue-year: columns [venue, year, hhi, task_counts]."""
    ...

def compute_hhi(task_counts: pd.Series) -> float:
    """HHI = sum((count_i / total)^2 for each task category)."""
    shares = task_counts / task_counts.sum()
    return float((shares ** 2).sum())
```

---

## Module: validate.py (entrypoint)

### API Signatures

```python
def compute_top5_share(task_counts: pd.Series) -> float:
    """Sum of top-5 category counts / total count. Returns ratio in [0, 1]."""
    ...

def validate_hhi_interpretation(venue_year_df: pd.DataFrame) -> dict:
    """Adds top5_share col, median-splits by hhi, runs Mann-Whitney U (one-sided,
    greater) and Spearman correlation. Returns results dict (see schema below)."""
    ...

def verify_mechanism_activation(results: dict) -> bool:
    """PoC sanity gate: groups_differ AND correlation_positive."""
    ...

def main() -> None:
    """1. load_papers() 2. build_venue_year_table()
    3. validate_hhi_interpretation() 4. verify_mechanism_activation()
    5. visualize.generate_all() 6. save results dict -> results/results.json."""
    ...
```

### Pseudo-code: validate_hhi_interpretation

```
1. venue_year_df['top5_share'] = venue_year_df['task_counts'].apply(compute_top5_share)
2. median_hhi = venue_year_df['hhi'].median()
3. high = venue_year_df[venue_year_df['hhi'] > median_hhi]['top5_share']
   low  = venue_year_df[venue_year_df['hhi'] <= median_hhi]['top5_share']
4. stat, mw_p = mannwhitneyu(high, low, alternative='greater')
5. rho, sp_p = spearmanr(venue_year_df['hhi'], venue_year_df['top5_share'])
6. gate_passed = mw_p < 0.05
7. return {
     'high_mean': high.mean(), 'low_mean': low.mean(),
     'high_n': len(high), 'low_n': len(low),
     'mann_whitney_stat': stat, 'mann_whitney_p': mw_p,
     'spearman_rho': rho, 'spearman_p': sp_p,
     'gate_passed': gate_passed,
   }
```

### results dict schema

| Key | Type | Note |
|-----|------|------|
| high_mean, low_mean | float | mean top5_share per group |
| high_n, low_n | int | group sizes (~10-11 each) |
| mann_whitney_stat, mann_whitney_p | float | one-sided, alternative='greater' |
| spearman_rho, spearman_p | float | rho > 0.7 is SHOULD criterion |
| gate_passed | bool | mann_whitney_p < 0.05 |

### verify_mechanism_activation logic

```
groups_differ = results['high_mean'] > results['low_mean']
correlation_positive = results['spearman_rho'] > 0
return groups_differ and correlation_positive
```

---

## Module: visualize.py

```python
def plot_group_comparison_bar(results: dict, out_path: str) -> None: ...
def plot_hhi_vs_top5_scatter(venue_year_df: pd.DataFrame, out_path: str) -> None: ...
def plot_distribution_histograms(venue_year_df: pd.DataFrame, median_hhi: float, out_path: str) -> None: ...
def plot_venue_year_heatmap(venue_year_df: pd.DataFrame, out_path: str) -> None: ...
def generate_all(results: dict, venue_year_df: pd.DataFrame, out_dir: str = "h-m1/figures/") -> None:
    """Calls all 4 plot functions above, writes PNGs to out_dir."""
    ...
```

No tensor shapes — this module operates on scipy/pandas scalars and DataFrames only, not DL tensors.

---

## External Dependencies (Base Hypothesis)

H-E1 has no built `code/`; nothing importable exists at spec time. `compute_hhi` is reimplemented locally in `data_loader.py` per the formula in `h-e1/03_architecture.md::metrics.py::compute_hhi`, rather than importing unbuilt code.

| Module | Import Path | File Location |
|--------|-------------|----------------|
| Cached data | N/A (file read) | `h-e1/data/pwc_papers_filtered.parquet` |
| HHI formula (reimplemented) | N/A | `h-e1/03_architecture.md` → `metrics.py::compute_hhi` |

**Verified from**: `h-e1/code/` (absent, confirmed) — spec fallback used, no code to trust over spec.

---

## Subtasks

None — budget is 0, all epic tasks (A-1..A-8) are Low complexity per architecture and require no further breakdown.
