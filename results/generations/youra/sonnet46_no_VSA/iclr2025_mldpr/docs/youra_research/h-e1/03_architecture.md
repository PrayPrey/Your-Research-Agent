# Architecture: H-E1 — Data Pipeline Validation & FAIL FAST Gate Verification

**Applied**: fail-fast sequential gate pattern (from PRD specification)
**Applied**: flat PoC file structure pattern (EXISTENCE tier)

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field — no existing code to analyze
**Analyzed Path**: N/A
**Findings**: New implementation from scratch; no existing patterns to reuse.

---

## File Structure

```
h-e1/
  code/
    pipeline.py      # DataLoader + PanelBuilder + FuzzyJoiner + DiversityAggregator
    gates.py         # GateValidator + VIFChecker
    output.py        # OutputWriter + Visualizer
    config.py        # constants and paths
    run.py           # entry point — orchestrates full pipeline
  figures/           # generated plots (auto-created)
  h_e2_panel_with_diversity.csv  # output artifact
```

---

## Module Definitions

### Config (`code/config.py`)

**Dependencies**: none

```python
FUZZY_THRESHOLD: int = 85
G0_COVERAGE_MIN: float = 0.80
G1_PARTIAL_R2_MIN: float = 0.01
G2_PARTIAL_R2_MIN: float = 0.01
G3_STD_MIN: float = 0.10
G4_VIF_WARN: float = 5.0
G4_VIF_MAX: float = 10.0
COLLINEARITY_R_MAX: float = 0.95
N_BENCHMARKS: int = 87
SEED: int = 1
HF_DATASET_ID: str = "pwc-archive/evaluation-tables"
OUTPUT_CSV: str = "h_e2_panel_with_diversity.csv"
FIGURES_DIR: str = "figures"
```

---

### DataLoader (`code/pipeline.py`)

**Dependencies**: datasets, pandas, config

```python
class DataLoader:
    def load(self) -> pd.DataFrame:
        """Load pwc-archive/evaluation-tables via HF API, return DataFrame."""
        ...
    def validate_columns(self, df: pd.DataFrame) -> None:
        """Assert task_path and paper_url present; raise ValueError if missing."""
        ...
```

---

### PanelBuilder (`code/pipeline.py`)

**Dependencies**: pandas, config

```python
class PanelBuilder:
    def load_or_build(self, panel_path: str) -> pd.DataFrame:
        """Load h_e2_panel.csv if exists; else raise FileNotFoundError with instructions."""
        ...
    def validate(self, panel: pd.DataFrame) -> None:
        """Assert required columns: task_path, duration, event, task_age,
        log_publication_volume, benchmark_introduction_year."""
        ...
```

---

### FuzzyJoiner (`code/pipeline.py`)

**Dependencies**: pandas, rapidfuzz, config

```python
class FuzzyJoiner:
    def join(self, eval_df: pd.DataFrame, panel: pd.DataFrame) -> pd.DataFrame:
        """Map eval_df.task_path → panel task slugs via token_sort_ratio >= 85.
        Adds 'matched_task' column; None if below threshold."""
        ...
    def coverage_count(self, joined: pd.DataFrame) -> int:
        """Count h-e2 benchmarks with >=1 non-null paper_url after join."""
        ...
```

---

### DiversityAggregator (`code/pipeline.py`)

**Dependencies**: pandas, numpy, config

```python
class DiversityAggregator:
    def filter_temporal(self, joined: pd.DataFrame, panel: pd.DataFrame) -> pd.DataFrame:
        """Retain rows where pub_year <= intro_year per benchmark.
        Fallback: use all rows if pub_year unavailable."""
        ...
    def aggregate(self, filtered: pd.DataFrame) -> pd.DataFrame:
        """Per benchmark: unique_count, total_rows, diversity_ratio, log_unique_count."""
        ...
    def z_standardize(self, stats_df: pd.DataFrame) -> pd.DataFrame:
        """Add log_unique_paper_count_at_intro_z, paper_diversity_ratio_at_intro_z columns."""
        ...
```

---

### GateValidator (`code/gates.py`)

**Dependencies**: pandas, numpy, statsmodels, config

```python
class GateResult:
    gate: str
    passed: bool
    value: float
    threshold: float
    message: str

class GateValidator:
    def run_all(self, stats_df: pd.DataFrame, panel: pd.DataFrame,
                n_matched: int) -> list[GateResult]:
        """Run G0->G4 in order; raise SystemExit on first failure after logging."""
        ...
    def g0_coverage(self, n_matched: int) -> GateResult: ...
    def g1_log_count_time_independence(self, stats_df: pd.DataFrame,
                                       panel: pd.DataFrame) -> GateResult: ...
    def g2_diversity_ratio_time_independence(self, stats_df: pd.DataFrame,
                                             panel: pd.DataFrame) -> GateResult: ...
    def g3_diversity_variance(self, stats_df: pd.DataFrame) -> GateResult: ...
    def g4_vif(self, enriched_panel: pd.DataFrame) -> GateResult: ...

def compute_partial_r2(predictor: pd.Series, controls: pd.DataFrame) -> float:
    """OLS residualization: 1 - rsquared of predictor ~ controls."""
    ...
```

---

### VIFChecker (`code/gates.py`)

**Dependencies**: statsmodels, pandas, numpy, config

```python
class VIFChecker:
    COVARIATES = [
        "log_unique_paper_count_at_intro_z",
        "paper_diversity_ratio_at_intro_z",
        "task_age",
        "log_publication_volume",
        "benchmark_introduction_year",
    ]

    def compute(self, panel: pd.DataFrame) -> dict[str, float]:
        """Return {covariate: VIF} using variance_inflation_factor on sm.add_constant(X)."""
        ...
    def collinearity_failsafe(self, stats_df: pd.DataFrame) -> float:
        """Pearson r(log_count_z, diversity_ratio_z); log warning if |r| > 0.95."""
        ...
```

---

### OutputWriter (`code/output.py`)

**Dependencies**: pandas, config

```python
class OutputWriter:
    def merge_and_save(self, panel: pd.DataFrame, stats_df: pd.DataFrame,
                       out_path: str) -> pd.DataFrame:
        """Left-join enriched diversity columns to panel; save CSV; return merged df."""
        ...
```

---

### Visualizer (`code/output.py`)

**Dependencies**: matplotlib, seaborn, pandas, config

```python
class Visualizer:
    def __init__(self, figures_dir: str): ...
    def plot_gate_metrics(self, gate_results: list) -> None:
        """Bar chart: gate value vs threshold; green=pass, red=fail."""
        ...
    def plot_coverage_heatmap(self, joined: pd.DataFrame, panel: pd.DataFrame) -> None:
        """Matched vs unmatched h-e2 task_paths."""
        ...
    def plot_predictor_distributions(self, stats_df: pd.DataFrame) -> None:
        """Histograms of log_unique_paper_count_at_intro and paper_diversity_ratio_at_intro."""
        ...
    def plot_correlation_matrix(self, enriched_panel: pd.DataFrame) -> None:
        """Pearson r heatmap for all Cox covariates."""
        ...
    def plot_partial_r2(self, gate_results: list) -> None:
        """G1/G2 partial_r² vs 0.01 threshold bar chart."""
        ...
    def save_all(self, joined, stats_df, gate_results, enriched_panel) -> None:
        """Call all five plot methods."""
        ...
```

---

### run.py (`code/run.py`)

**Dependencies**: all modules above

```python
def main() -> None:
    """Orchestrate: load -> build panel -> fuzzy join -> aggregate ->
    gates -> collinearity check -> output -> visualize."""
    ...

if __name__ == "__main__":
    main()
```

---

## Module Dependency Graph

- `run.py` -> `pipeline.py`, `gates.py`, `output.py`, `config.py`
- `pipeline.py` -> `config.py`
- `gates.py` -> `config.py`
- `output.py` -> `config.py`

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown | Type |
|----|------|-------------|------------|-----------|------|
| E1 | Project Setup & Config | Create flat file structure, config.py constants, requirements.txt | 5 | Size=1 + Deps=1 + Algo=1 + Integ=2 | infrastructure |
| E2 | Data Loading & Panel Building | DataLoader (HF API) + PanelBuilder (load h_e2_panel.csv) + column validation | 9 | Size=2 + Deps=3 + Algo=1 + Integ=3 | data-pipeline |
| E3 | Fuzzy Join & Diversity Aggregation | FuzzyJoiner (rapidfuzz token_sort_ratio=85) + DiversityAggregator (unique_count, ratio, log, z-score) + temporal filter | 13 | Size=3 + Deps=3 + Algo=4 + Integ=3 | data-pipeline |
| E4 | Gate Validation (G0-G4) | GateValidator: sequential G0→G4 with STOP-on-fail; compute_partial_r2 via OLS | 14 | Size=3 + Deps=3 + Algo=5 + Integ=3 | evaluation |
| E5 | VIF Checker & Collinearity Failsafe | VIFChecker: statsmodels VIF + Pearson r failsafe warning | 10 | Size=2 + Deps=3 + Algo=3 + Integ=2 | evaluation |
| E6 | Output Writer & CSV Artifact | OutputWriter: merge diversity columns to panel, save h_e2_panel_with_diversity.csv | 6 | Size=2 + Deps=1 + Algo=1 + Integ=2 | data-pipeline |
| E7 | Visualization (5 Figures) | Visualizer: gate bar chart, coverage heatmap, histograms, corr matrix, partial R² bar | 11 | Size=3 + Deps=2 + Algo=2 + Integ=4 | visualization |
| E8 | Integration & End-to-End Run | run.py orchestration; verify all gates pass; validate output artifact; smoke test | 9 | Size=2 + Deps=2 + Algo=1 + Integ=4 | integration |

**Distribution**: High(14-17): [E4], Medium(9-13): [E3, E5, E7, E2, E8], Low(4-8): [E1, E6]

---

## External Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| datasets | >=2.0.0 | HF dataset loading |
| pandas | >=1.5.0 | DataFrame operations |
| numpy | >=1.21.0 | log1p, z-standardize |
| rapidfuzz | >=3.0.0 | token_sort_ratio fuzzy join |
| statsmodels | >=0.14.0 | OLS (partial R²), VIF |
| scipy | >=1.7.0 | Pearson r (stats.pearsonr) |
| matplotlib | >=3.5.0 | figure generation |
| seaborn | >=0.12.0 | heatmap, corr matrix |
