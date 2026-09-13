# Architecture: h-e1-v3-v4
# Global k-th Percentile Threshold Disparity Analysis (Updated Gate)

**Date:** 2026-07-30
**Hypothesis:** h-e1-v3-v4 (EXISTENCE / PoC)
**Type:** Pure statistical analysis — pandas/scipy, CPU-only, no neural models

Applied: single-script functional pipeline (no classes, no modules)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (h-e1)
**Status**: Patterns found from base code
**Analyzed Path**: `docs/youra_research/h-e1/code/run_h_e1.py`
**Findings**: h-e1 contains 9 functions (`_parse_signals_file`, `_find_signals_files`, `_load_from_arrow_cache`, `load_data`, `validate_data`, `analyze_thresholds`, `check_gate`, `plot_figures`, `main`) and 8 constants. h-e1-v3-v4 reuses the same function signatures; only gate bounds change from [0.29, 0.41] → [0.40, 0.57].

---

## File Structure

- `docs/youra_research/h-e1-v3-v4/code/run_experiment.py` — single script, all logic
- `docs/youra_research/h-e1-v3-v4/results.json` — full per-k results (output)
- `docs/youra_research/h-e1-v3-v4/gate_verdict.json` — gate pass/fail (output)
- `docs/youra_research/h-e1-v3-v4/figures/cramers_v_bar.png` — output
- `docs/youra_research/h-e1-v3-v4/figures/retention_heatmap.png` — output
- `docs/youra_research/h-e1-v3-v4/figures/perplexity_kde.png` — output
- `docs/youra_research/h-e1-v3-v4/figures/retention_gap.png` — output
- `docs/youra_research/redpajama_sample.parquet` — input (pre-existing, 208,262 rows)

---

## Module: `run_experiment.py` (`docs/youra_research/h-e1-v3-v4/code/run_experiment.py`)

**Dependencies**: pandas, scipy, numpy, statsmodels, matplotlib, seaborn, pyarrow

### Constants

```python
BASE_DIR = Path("docs/youra_research/h-e1-v3-v4")
CACHE_PATH = Path("docs/youra_research/redpajama_sample.parquet")
OUTPUT_DIR = BASE_DIR
FIGURES_DIR = BASE_DIR / "figures"
K_VALUES = [10, 20, 30, 40, 50]
GATE_V_MIN = 0.40   # updated from h-e1's 0.29
GATE_V_MAX = 0.57   # updated from h-e1's 0.41
```

### Interface

```python
def load_data(cache_path: Path) -> pd.DataFrame:
    # Primary: pd.read_parquet(cache_path)
    # Fallback: pyarrow.ipc if parquet missing
    # Returns: DataFrame with columns [language, ccnet_perplexity]
    ...

def validate_data(df: pd.DataFrame) -> pd.DataFrame:
    # Assert len(df) > 190_000
    # Assert df['language'].nunique() == 5
    # Assert df['ccnet_perplexity'].isna().mean() < 0.01
    # Drop NaN ccnet_perplexity rows
    # Returns: cleaned DataFrame
    ...

def analyze_thresholds(df: pd.DataFrame, k_values: list[int]) -> dict:
    # For each k: compute global quantile, crosstab, Cramér's V, chi2, p_value, retention rates
    # Returns: {k: {threshold, cramers_v, chi2, p_value, retention_rates, max_min_gap}}
    ...

def apply_holm_correction(results: dict, k_values: list[int]) -> dict:
    # Extract p_values list, call multipletests(p_values, method='holm')
    # Attach p_holm to each k entry in results
    # Returns: updated results dict
    ...

def check_gate(df: pd.DataFrame, results: dict, k_values: list[int]) -> tuple[bool, dict]:
    # Checks all 5 gate conditions from FR-5
    # GATE_V_MIN=0.40, GATE_V_MAX=0.57
    # Returns: (gate_passed: bool, indicators: dict)
    ...

def verify_mechanism_activated(results: dict) -> tuple[bool, dict]:
    # Wider check: V ∈ [0.38, 0.60], Holm p < 0.001
    # Returns: (activated: bool, indicators: dict)
    ...

def plot_figures(df: pd.DataFrame, results: dict, k_values: list[int], figures_dir: Path) -> None:
    # cramers_v_bar.png: bar chart V per k, horizontal band [0.40, 0.57]
    # retention_heatmap.png: seaborn heatmap language × k
    # perplexity_kde.png: KDE per language (matplotlib/seaborn)
    # retention_gap.png: max-min gap vs k line plot
    ...

def main() -> None:
    # Orchestrates: load → validate → analyze → holm → gate → plot → write JSON
    # Writes results.json and gate_verdict.json to OUTPUT_DIR
    # Exits 0 on gate pass, 1 on gate fail
    ...
```

---

## External Dependencies (Base Hypothesis)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| load_data pattern | adapted from h-e1 | `docs/youra_research/h-e1/code/run_h_e1.py:111-160` |
| Arrow IPC fallback | `_load_from_arrow_cache` pattern | `docs/youra_research/h-e1/code/run_h_e1.py` |
| analyze_thresholds pattern | adapted from h-e1 | `docs/youra_research/h-e1/code/run_h_e1.py` |
| check_gate pattern | GATE_V_MIN/MAX updated | `docs/youra_research/h-e1/code/run_h_e1.py` |

**Key diff from h-e1**: `GATE_V_MIN = 0.40` (was 0.29), `GATE_V_MAX = 0.57` (was 0.41). All other logic identical.

**Verified from**: `docs/youra_research/h-e1/code/run_h_e1.py` (actual implementation)

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Setup & Config | Create output dirs, constants (gate bounds, paths, k_values) | 4 | 1+1+1+1 |
| A-2 | Data Loading | load_data() with parquet primary + Arrow IPC fallback; validate_data() | 7 | 2+1+2+2 |
| A-3 | Statistical Analysis | analyze_thresholds() + apply_holm_correction(): crosstab, Cramér's V, chi2, Holm | 10 | 3+2+3+2 |
| A-4 | Gate & Output | check_gate(), verify_mechanism_activated(), write results.json + gate_verdict.json, plot_figures() | 9 | 2+2+2+3 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-3, A-4], Low(4-8): [A-1, A-2]

---

## Notes for Phase 4 Coder

- Copy h-e1's `run_h_e1.py` as starting point; change `GATE_V_MIN/MAX` and output path constants only
- `numpy.bool_` → `bool()` cast required before `json.dump` (h-e1 lesson)
- `scipy.stats.contingency.association(table.values, method='cramer')` — pass `.values`, not DataFrame
- Script must exit with `sys.exit(0)` on gate pass, `sys.exit(1)` on gate fail
- `verify_mechanism_activated` uses wider bounds [0.38, 0.60] (from FR-7); `check_gate` uses strict [0.40, 0.57] (from FR-5)
