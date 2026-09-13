# Architecture: h-e1
# Global k-th Percentile Threshold Disparity Analysis

**Date:** 2026-07-30
**Hypothesis:** h-e1 (EXISTENCE / PoC)
**Phase:** 3 — Architecture
**Applied Pattern:** pandas/scipy statistical pipeline

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze
**Analyzed Path**: N/A
**Findings**: New single-script implementation from scratch

---

## Design Overview

Single-script, pure-function design. No classes. ~50 lines of pandas/scipy.

**File**: `code/run_h_e1.py` (one file, all logic)

**Output paths**:
- Cache: `docs/youra_research/redpajama_sample.parquet`
- Results: `docs/youra_research/h-e1/results.json`
- Gate: `docs/youra_research/h-e1/gate_verdict.json`
- Figures: `docs/youra_research/h-e1/figures/{cramers_v_bar,retention_heatmap,perplexity_kde,retention_gap}.png`

---

## Data Flow

```
HuggingFace API
    |
    v
load_dataset("togethercomputer/RedPajama-Data-V2", name="sample")
    |
    +--[cache exists?]--> redpajama_sample.parquet (read)
    |
    v
load_data() --> DataFrame[language, ccnet_perplexity]  (208,263 rows)
    |
    v
validate_data() --> raises ValueError on bad row count / missing languages / >1% NaN
    |
    v
analyze_thresholds(df, k_values=[10,20,30,40,50])
    |   for each k:
    |     quantile(k/100) --> threshold
    |     retained = perplexity < threshold
    |     crosstab(language, retained) --> 5x2 table
    |     association(table, 'cramer') --> cramers_v
    |     chi2_contingency(table) --> p_value
    |     groupby('language')['retained'].mean() --> retention_rates
    |
    v
apply_holm_correction(p_values) --> p_corrected[5]
    |
    v
results dict {k: {threshold, cramers_v, chi2, p_value, p_corrected, retention_rates}}
    |
    +-----> results.json
    |
    v
plot_figures(df, results, out_dir)
    |   cramers_v_bar.png
    |   retention_heatmap.png
    |   perplexity_kde.png
    |   retention_gap.png
    |
    v
check_gate(df, results) --> {gate_passed: bool, indicators: dict}
    |
    v
gate_verdict.json
```

---

## Function Signatures (`code/run_h_e1.py`)

```python
# --- data_loader ---

def load_data(
    cache_path: str = "docs/youra_research/redpajama_sample.parquet"
) -> pd.DataFrame:
    """Load from parquet cache if exists, else download and cache.
    Returns DataFrame with columns: [language, ccnet_perplexity]
    Raises KeyError if ccnet_perplexity missing from quality_signals.
    """
    ...

def _parse_quality_signals(row: dict) -> float | None:
    """Extract ccnet_perplexity from JSON quality_signals field.
    Returns signals["ccnet_perplexity"][0][2] or None on parse failure.
    """
    ...

# --- analyzer ---

def validate_data(df: pd.DataFrame) -> None:
    """Validate row count, language count, NaN rate.
    Raises ValueError with descriptive message on failure.
    Checks: len(df) > 190_000, nunique(language)==5, nan_rate < 0.01
    """
    ...

def analyze_thresholds(
    df: pd.DataFrame,
    k_values: list[int] = [10, 20, 30, 40, 50]
) -> dict[int, dict]:
    """For each k: compute threshold, contingency table, Cramér's V, p-value.
    Returns: {k: {threshold, cramers_v, chi2, p_value, retention_rates}}
    """
    ...

def apply_holm_correction(
    results: dict[int, dict],
    k_values: list[int]
) -> dict[int, dict]:
    """Add p_corrected key to each results[k] via Holm-Bonferroni.
    Mutates results in-place and returns it.
    """
    ...

# --- gate_checker ---

def check_gate(
    df: pd.DataFrame,
    results: dict[int, dict],
    k_values: list[int] = [10, 20, 30, 40, 50]
) -> dict:
    """Evaluate all 4 gate conditions.
    Returns: {gate_passed: bool, indicators: {str: bool}}
    Indicators:
      data_loaded: len(df) > 190_000
      five_languages: df['language'].nunique() == 5
      no_nan_perplexity: df['ccnet_perplexity'].isna().mean() < 0.01
      cramers_v_in_range: all(0.29 <= results[k]['cramers_v'] <= 0.45 for k in k_values)
    """
    ...

# --- visualizer ---

def plot_figures(
    df: pd.DataFrame,
    results: dict[int, dict],
    out_dir: str = "docs/youra_research/h-e1/figures",
    k_values: list[int] = [10, 20, 30, 40, 50]
) -> None:
    """Generate and save all 4 required figures.
    cramers_v_bar.png: bar chart V vs k, reference lines at 0.29 / 0.41
    retention_heatmap.png: seaborn heatmap, languages x k_values
    perplexity_kde.png: overlaid KDE per language
    retention_gap.png: max-min retention gap vs k line chart
    """
    ...

# --- main ---

def main() -> None:
    """Entry point. Runs full pipeline, writes JSON outputs, exits 0 on gate pass."""
    ...

if __name__ == "__main__":
    main()
```

---

## Error Handling

| Failure Mode | Location | Handling |
|---|---|---|
| `ccnet_perplexity` key missing | `_parse_quality_signals` | Return None; count NaN; raise if >1% |
| Row count < 190,000 | `validate_data` | Raise ValueError |
| Language count != 5 | `validate_data` | Raise ValueError |
| Parquet cache corrupted | `load_data` | Catch exception, re-download |
| Output dir missing | `plot_figures` | `os.makedirs(out_dir, exist_ok=True)` |

---

## Dependencies

| Package | Use |
|---|---|
| pandas >= 1.5 | DataFrame, groupby, crosstab, quantile, parquet I/O |
| scipy >= 1.7 | `contingency.association` (Cramér's V), `chi2_contingency` |
| numpy >= 1.21 | Array ops |
| datasets >= 2.0 | HuggingFace load_dataset |
| statsmodels >= 0.13 | `multipletests` (Holm-Bonferroni) |
| matplotlib >= 3.5 | Figure generation |
| seaborn >= 0.11 | `heatmap` for retention_heatmap.png |

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Data loader | `load_data` + `_parse_quality_signals` + parquet cache logic | 8 | 2+2+2+2 |
| A-2 | Validator | `validate_data` — row/language/NaN checks | 4 | 1+1+1+1 |
| A-3 | Threshold analyzer | `analyze_thresholds` — quantile loop, crosstab, Cramér's V | 10 | 3+2+3+2 |
| A-4 | Holm correction | `apply_holm_correction` — multipletests wrapper | 5 | 1+2+1+1 |
| A-5 | Gate checker | `check_gate` + write `gate_verdict.json` | 6 | 2+1+2+1 |
| A-6 | Visualizer | `plot_figures` — 4 figures (bar, heatmap, KDE, gap) | 12 | 3+3+3+3 |
| A-7 | Main + JSON output | `main()` wiring + `results.json` write | 5 | 1+2+1+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-3, A-6], Low(4-8): [A-1, A-2, A-4, A-5, A-7]
