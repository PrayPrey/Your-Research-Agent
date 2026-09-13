# Architecture: h-e1-v3
# Global Percentile Threshold Language Retention Disparity Analysis

Applied: custom pipeline — no matching KB patterns (KB is vision/diffusion content only)

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field — no existing code to analyze
**Analyzed Path**: N/A
**Findings**: New implementation from scratch. h-e1-v3 is a SELF_MODIFY restart; prior h-e1 code is in archive and explicitly excluded per 02c_experiment_brief.md.

---

## File Organization

```
code/
├── run_h_e1_v3.py      # Orchestration entry point
├── data_loader.py       # Cache-aware data loading + validation
├── analysis.py          # Global threshold + Cramér's V + Holm correction
├── visualization.py     # 4 required figures
└── reporter.py          # JSON output + gate check + mechanism verification

docs/youra_research/h-e1-v3/
├── figures/
│   ├── gate_metrics.png
│   ├── retention_heatmap.png
│   ├── perplexity_kde.png
│   └── gap_vs_k.png
├── results.json
└── experiment_results.json

docs/youra_research/
└── redpajama_sample.parquet   # Cache (confirmed present from h-e1 run)
```

---

## Module Interfaces

### DataLoader (`code/data_loader.py`)

**Dependencies**: pandas, datasets (HuggingFace, cache-miss only)

```python
CACHE_PATH = "docs/youra_research/redpajama_sample.parquet"
REQUIRED_COLS = ["language", "ccnet_perplexity"]
MIN_ROWS = 190_000

def load(cache_path: str = CACHE_PATH) -> pd.DataFrame:
    """Returns df with columns ['language', 'ccnet_perplexity'].
    Checks cache first; downloads from HuggingFace on miss/corruption.
    Raises AssertionError if validation fails."""
    ...

def _validate(df: pd.DataFrame) -> None:
    """Asserts: len >= 190_000, nunique('language') == 5, NaN rate < 0.01."""
    ...

def _download_and_cache(cache_path: str) -> pd.DataFrame:
    """Downloads RedPajama-V2 sample, extracts fields, saves Parquet."""
    ...
```

---

### Analysis (`code/analysis.py`)

**Dependencies**: pandas, scipy, statsmodels

```python
K_VALUES = [10, 20, 30, 40, 50]

def compute_disparity(df: pd.DataFrame, k_values: list = K_VALUES) -> dict:
    """Returns dict[k] = {threshold, cramers_v, chi2, p_value, retention_rates, max_min_gap}.
    Does NOT apply Holm correction (caller does that via apply_holm)."""
    ...

def apply_holm(results: dict, k_values: list = K_VALUES) -> dict:
    """Adds 'p_holm' key to each results[k] entry. Returns updated results."""
    ...

def verify_mechanism_activated(df: pd.DataFrame, results: dict, k_values: list) -> tuple[bool, dict]:
    """Returns (activated: bool, indicators: dict) — 5 indicator checks."""
    ...
```

---

### Visualization (`code/visualization.py`)

**Dependencies**: matplotlib, seaborn, pandas

```python
FIGURES_DIR = "docs/youra_research/h-e1-v3/figures"

def plot_gate_metrics(results: dict, k_values: list, out_dir: str = FIGURES_DIR) -> None:
    """FR-5.1: Bar chart of Cramér's V per k. Green in [0.29,0.41], red outside."""
    ...

def plot_retention_heatmap(df: pd.DataFrame, results: dict, k_values: list, out_dir: str = FIGURES_DIR) -> None:
    """FR-5.2: Heatmap — languages × k values, color = retention rate."""
    ...

def plot_perplexity_kde(df: pd.DataFrame, out_dir: str = FIGURES_DIR) -> None:
    """FR-5.3: Overlaid KDE of ccnet_perplexity per language."""
    ...

def plot_gap_vs_k(results: dict, k_values: list, out_dir: str = FIGURES_DIR) -> None:
    """FR-5.4: Line chart — x=k, y=max_min_gap."""
    ...
```

---

### Reporter (`code/reporter.py`)

**Dependencies**: json, pathlib

```python
RESULTS_DIR = "docs/youra_research/h-e1-v3"

def check_gate(results: dict, k_values: list) -> tuple[bool, str]:
    """Returns (passed: bool, message: str).
    Condition A: all V in [0.29, 0.41]. Condition B: all p_holm < 0.001."""
    ...

def write_results(results: dict, k_values: list, gate_passed: bool, out_dir: str = RESULTS_DIR) -> None:
    """Writes results.json and experiment_results.json (FR-4.1, FR-4.2)."""
    ...
```

---

### Orchestrator (`code/run_h_e1_v3.py`)

**Dependencies**: data_loader, analysis, visualization, reporter

```python
def main() -> None:
    """Runs full pipeline: load → analyze → apply_holm → visualize → report → gate."""
    ...

if __name__ == "__main__":
    main()
```

---

## Proposed Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Data Loading | Implement `data_loader.py`: cache detection, validation, HuggingFace fallback, Parquet save (FR-1) | 8 | 2+2+2+2 |
| A-2 | Statistical Analysis | Implement `analysis.py`: global threshold loop, Cramér's V, chi2, per-language retention rates, Holm correction (FR-2) | 11 | 3+2+4+2 |
| A-3 | Visualization | Implement `visualization.py`: all 4 required figures (FR-5.1–5.4) | 9 | 3+1+3+2 |
| A-4 | Reporting & Gate | Implement `reporter.py`: gate evaluation, results.json, experiment_results.json, mechanism verification (FR-3, FR-4) | 8 | 2+2+2+2 |
| A-5 | Orchestration & Smoke Test | Implement `run_h_e1_v3.py` entry point; wire all modules; run end-to-end on cached Parquet; verify gate output | 7 | 1+2+2+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-2, A-3], Low(4-8): [A-1, A-4, A-5]

---

## Data Flow

- `run_h_e1_v3.py` calls `data_loader.load()` → `pd.DataFrame`
- passes df to `analysis.compute_disparity()` → raw results dict
- passes results to `analysis.apply_holm()` → results with p_holm
- passes df + results to `visualization.plot_*()` → 4 PNG files
- passes df + results to `analysis.verify_mechanism_activated()` → logs indicators
- passes results to `reporter.check_gate()` → (gate_passed, message)
- passes results + gate to `reporter.write_results()` → 2 JSON files

---

## Key Constraints

- `scipy >= 1.7` required for `contingency.association(method='cramer')`
- Cache path relative to working directory where `run_h_e1_v3.py` is invoked
- `matplotlib` must use `Agg` backend (CPU-only, no display required)
- All paths must resolve from `code/` working directory or use absolute paths via `__file__`
