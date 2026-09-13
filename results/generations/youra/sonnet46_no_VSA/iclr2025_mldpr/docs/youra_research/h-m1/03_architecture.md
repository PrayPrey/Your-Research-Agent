# Architecture: H-M1
# Cox Proportional Hazards — Diversity Predictor Significance Test

**Date:** 2026-08-03
**Hypothesis:** H-M1 (MECHANISM, INCREMENTAL extends H-E1)
**Phase:** 3 — Implementation Planning

Applied: statistical-estimation-pipeline (no training loop, deterministic MLE)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-M1 extends H-E1)
**Status**: patterns found from base code
**Analyzed Path**: `docs/youra_research/h-e1/code/`
**Findings**: H-E1 uses dataclass configs (H1Config, FigureConfig), class-per-concern pattern (DataLoader, Visualizer, OutputWriter, GateValidator). H-M1 replicates this structure minimally — config dataclass, analysis module, visualization module, runner script.

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| H1Config | `from docs.youra_research.h_e1.code.config import H1Config` | Not reused directly — column names replicated in H-M1 config |
| FigureConfig style | Reference only | `docs/youra_research/h-e1/code/config.py` |

**Note:** H-M1 does NOT import H-E1 code at runtime. It only consumes the output CSV. Column names are copied into H-M1 config for self-containment.

**Verified from**: `docs/youra_research/h-e1/code/` (actual implementation)

---

## File Structure

- `docs/youra_research/h-m1/code/`
  - `config.py` — dataclass config (paths, column names, thresholds)
  - `cox_analysis.py` — M0/M1 fitting, LRT, HR extraction, diagnostics
  - `visualization.py` — 5 required figures
  - `run.py` — orchestration entry point
- `docs/youra_research/h-m1/figures/` — output figures
- `docs/youra_research/h-m1/experiment_results.json` — output results

---

## Modules

### Config (`code/config.py`)

**Dependencies**: stdlib only (dataclasses)

```python
from dataclasses import dataclass

@dataclass
class CoxConfig:
    panel_path: str = "docs/youra_research/h-e1/h_e2_panel_with_diversity.csv"
    figures_dir: str = "docs/youra_research/h-m1/figures"
    results_path: str = "docs/youra_research/h-m1/experiment_results.json"

    duration_col: str = "duration"
    event_col: str = "event"
    base_covariates: tuple = ("task_age", "log_publication_volume", "benchmark_introduction_year")
    diversity_col: str = "log_unique_paper_count_at_intro_z"
    km_col: str = "log_unique_paper_count_at_intro"

    penalizer: float = 0.1
    penalizer_fallback: float = 0.5
    lrt_df: int = 1
    p_threshold: float = 0.05
    hr_effect_threshold: float = 0.10

@dataclass
class FigureConfig:
    dpi: int = 150
    color_pass: str = "#2ecc71"
    color_fail: str = "#e74c3c"
    color_neutral: str = "#3498db"

CFG = CoxConfig()
FIG_CFG = FigureConfig()
```

---

### CoxAnalysis (`code/cox_analysis.py`)

**Dependencies**: config, lifelines, scipy, pandas, numpy

```python
import pandas as pd
import numpy as np
from scipy import stats
from lifelines import CoxPHFitter
from dataclasses import dataclass
from typing import Tuple

@dataclass
class LRTResult:
    lrt_stat: float
    p_value: float
    HR: float
    CI_lower: float
    CI_upper: float
    abs_effect: float
    concordance: float
    M0_log_likelihood: float
    M1_log_likelihood: float
    direction: str      # "H1" | "H2" | "H0"
    gate_passed: bool

def load_panel(cfg: CoxConfig) -> pd.DataFrame: ...
    # reads CSV, asserts shape and columns, drops NaN

def fit_models(panel_df: pd.DataFrame, cfg: CoxConfig) -> Tuple[CoxPHFitter, CoxPHFitter]: ...
    # fits M0 and M1 with penalizer fallback on convergence warning

def run_lrt(M0: CoxPHFitter, M1: CoxPHFitter, cfg: CoxConfig) -> LRTResult: ...
    # computes chi2 LRT, extracts HR+CI, evaluates gate, determines direction

def run_diagnostics(M1: CoxPHFitter, panel_df: pd.DataFrame) -> dict: ...
    # returns concordance_index_, PH assumption violations list
```

---

### Visualization (`code/visualization.py`)

**Dependencies**: config, cox_analysis.LRTResult, matplotlib, lifelines, pandas

```python
from lifelines import KaplanMeierFitter

def plot_gate_metrics(result: LRTResult, cfg: CoxConfig, fig_cfg: FigureConfig) -> str: ...
    # Fig 1: bar chart p_value vs 0.05, abs_effect vs 0.10 — saves gate_metrics.png

def plot_km_quartiles(panel_df: pd.DataFrame, cfg: CoxConfig, fig_cfg: FigureConfig) -> str: ...
    # Fig 2: KM curves Q1 vs Q4 of km_col — saves km_quartiles.png

def plot_partial_effects(M1: CoxPHFitter, panel_df: pd.DataFrame, cfg: CoxConfig, fig_cfg: FigureConfig) -> str: ...
    # Fig 3: M1.plot_partial_effects_on_outcome(diversity_col, values=[-2,-1,0,1,2]) — saves partial_effects.png

def plot_forest(M1: CoxPHFitter, cfg: CoxConfig, fig_cfg: FigureConfig) -> str: ...
    # Fig 4: HR+CI for all M1 covariates, color by p<0.05 — saves forest_plot.png

def plot_schoenfeld(M1: CoxPHFitter, panel_df: pd.DataFrame, cfg: CoxConfig, fig_cfg: FigureConfig) -> str: ...
    # Fig 5: check_assumptions output — saves schoenfeld_residuals.png

def save_all_figures(M1: CoxPHFitter, panel_df: pd.DataFrame, result: LRTResult, cfg: CoxConfig, fig_cfg: FigureConfig) -> list[str]: ...
    # calls all 5 plot functions, returns list of saved paths
```

---

### Runner (`code/run.py`)

**Dependencies**: config, cox_analysis, visualization, json, datetime

```python
def main() -> None: ...
    # 1. load_panel → 2. fit_models → 3. run_lrt → 4. run_diagnostics
    # 5. save_all_figures → 6. write experiment_results.json
    # prints gate result summary

if __name__ == "__main__":
    main()
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Project Setup | Create directory structure, config.py with all paths/thresholds/column names | 5 | 1+1+1+2 |
| A-2 | Panel Loading | load_panel(): read CSV, assert shape (345,≥8), assert required columns, drop NaN rows | 6 | 2+1+1+2 |
| A-3 | Model Fitting | fit_models(): M0 + M1 CoxPHFitter with penalizer fallback on convergence warning | 10 | 3+2+3+2 |
| A-4 | LRT + HR Extraction | run_lrt(): chi2.sf LRT, HR/CI extraction, gate evaluation, direction interpretation | 12 | 3+2+4+3 |
| A-5 | Diagnostics | run_diagnostics(): concordance_index_, check_assumptions(), log PH violations | 7 | 2+2+2+1 |
| A-6 | Gate Metrics Figure | plot_gate_metrics(): bar chart p_value vs 0.05, abs_effect vs 0.10 | 6 | 1+2+2+1 |
| A-7 | KM Quartile Figure | plot_km_quartiles(): KaplanMeierFitter Q1 vs Q4 survival curves | 8 | 2+2+2+2 |
| A-8 | Partial Effects Figure | plot_partial_effects(): M1.plot_partial_effects_on_outcome across [-2,-1,0,1,2] | 7 | 2+2+2+1 |
| A-9 | Forest Plot Figure | plot_forest(): HR+CI for all covariates, color by p<0.05 | 9 | 2+2+3+2 |
| A-10 | Schoenfeld Figure | plot_schoenfeld(): PH assumption diagnostic via check_assumptions | 6 | 1+2+2+1 |
| A-11 | Results Serialization | Write experiment_results.json with all LRTResult fields + timestamp | 5 | 1+1+2+1 |
| A-12 | Integration + Validation | run.py orchestration, end-to-end smoke test, assert M1.ll >= M0.ll | 8 | 2+2+2+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-4, A-9], Low(4-8): [A-1, A-2, A-3, A-5, A-6, A-7, A-8, A-10, A-11, A-12]

**Total complexity**: 89 | **Estimated tasks**: 12
