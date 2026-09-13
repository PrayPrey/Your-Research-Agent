# Configuration: H-M1
# Cox Proportional Hazards — Diversity Predictor Significance Test

**Date:** 2026-08-03
**Hypothesis:** H-M1 (MECHANISM, INCREMENTAL extends H-E1)
**Phase:** 3 — Configuration

Applied: dataclass-per-concern (H-E1 in-repo pattern — H1Config + FigureConfig split)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-M1 extends H-E1)
**Status**: config classes verified from actual H-E1 code
**Config Files Found**: `docs/youra_research/h-e1/code/config.py` — H1Config, FigureConfig dataclasses
**Pattern Used**: dataclass (two-class split: CoxConfig + FigureConfig)

---

## Inherited Configuration (Base Hypothesis)

### Config Classes (From Actual H-E1 Code)

```python
# From: docs/youra_research/h-e1/code/config.py (ACTUAL CODE — verified)
@dataclass
class H1Config:
    hf_dataset_id: str = "pwc-archive/evaluation-tables"
    panel_path: str = "h_e2_panel_with_diversity.csv"
    output_csv: str = "h_e2_panel_with_diversity.csv"
    figures_dir: str = "figures"
    seed: int = 1
    fuzzy_threshold: int = 85
    n_benchmarks: int = 87
    g0_coverage_min: float = 0.80
    g1_partial_r2_min: float = 0.01
    g2_partial_r2_min: float = 0.01
    g3_std_min: float = 0.10
    g4_vif_warn: float = 5.0
    g4_vif_max: float = 10.0
    collinearity_r_max: float = 0.95

@dataclass
class FigureConfig:
    dpi: int = 150
    fig_size_single: Tuple[float, float] = (8, 5)
    fig_size_wide: Tuple[float, float] = (12, 5)
    fig_size_square: Tuple[float, float] = (7, 6)
    color_pass: str = "#2ecc71"
    color_fail: str = "#e74c3c"
    color_neutral: str = "#3498db"
    color_warn: str = "#f39c12"
    corr_palette: str = "coolwarm"
    corr_vmin: float = -1.0
    corr_vmax: float = 1.0
    font_size_title: int = 13
    font_size_label: int = 11
    font_size_tick: int = 9
```

**Verified from**: `docs/youra_research/h-e1/code/config.py` (actual implementation)

### Reuse Policy

H-M1 does NOT import H-E1 config at runtime. It consumes H-E1's output CSV only.
FigureConfig color tokens (`color_pass`, `color_fail`, `color_neutral`, `color_warn`) and `dpi=150` are replicated by value for self-containment. Column names from H-E1 schema are hardcoded as string defaults in CoxConfig.

---

## C1: CoxConfig Dataclass [A-9 forest plot, complexity 9]

**Applied**: dataclass-per-concern (H-E1 pattern)

### Configuration

```python
from dataclasses import dataclass, field
from typing import Tuple, List


@dataclass
class CoxConfig:
    # --- Paths ---
    panel_path: str = "docs/youra_research/h-e1/h_e2_panel_with_diversity.csv"
    figures_dir: str = "docs/youra_research/h-m1/figures"
    results_path: str = "docs/youra_research/h-m1/experiment_results.json"

    # --- Column names (from H-E1 schema, verified) ---
    duration_col: str = "duration"
    event_col: str = "event"
    base_covariates: Tuple[str, ...] = (
        "task_age",
        "log_publication_volume",
        "benchmark_introduction_year",
    )
    diversity_col: str = "log_unique_paper_count_at_intro_z"   # primary predictor (z-scored)
    km_col: str = "log_unique_paper_count_at_intro"            # raw scale for KM quartile split

    # --- Model hyperparameters ---
    penalizer: float = 0.1          # lifelines CoxPHFitter L2 ridge; standard starting value
    penalizer_fallback: float = 0.5 # Non-standard: increased on convergence warning, retry once
    lrt_df: int = 1                 # chi2 df for nested LRT (M1 adds exactly 1 predictor vs M0)

    # --- Gate thresholds ---
    p_threshold: float = 0.05
    hr_effect_threshold: float = 0.10   # |HR - 1| minimum for practical significance

    # --- Expected panel shape (for assertion) ---
    expected_rows: int = 345
    expected_min_cols: int = 8

    # --- Forest plot figure ---
    forest_fig_size: Tuple[float, float] = (10, 6)  # wide enough for CI bars + labels
    forest_sig_color: str = "#2ecc71"    # significant covariate (p < 0.05) — matches H-E1 color_pass
    forest_nonsig_color: str = "#3498db" # non-significant — matches H-E1 color_neutral
    forest_ci_linewidth: float = 2.0
    forest_marker_size: float = 8.0
    forest_fname: str = "forest_plot.png"


@dataclass
class FigureConfig:
    dpi: int = 150                                  # inherited from H-E1 FigureConfig.dpi
    fig_size_single: Tuple[float, float] = (8, 5)  # inherited
    fig_size_wide: Tuple[float, float] = (12, 5)   # inherited
    fig_size_square: Tuple[float, float] = (7, 6)  # inherited

    color_pass: str = "#2ecc71"     # inherited — gate PASS / significant
    color_fail: str = "#e74c3c"     # inherited — gate FAIL
    color_neutral: str = "#3498db"  # inherited — neutral bars / non-significant
    color_warn: str = "#f39c12"     # inherited — warning annotation

    font_size_title: int = 13       # inherited
    font_size_label: int = 11       # inherited
    font_size_tick: int = 9         # inherited

    # Figure filenames
    fname_gate_metrics: str = "gate_metrics.png"
    fname_km_quartiles: str = "km_quartiles.png"
    fname_partial_effects: str = "partial_effects.png"
    fname_forest_plot: str = "forest_plot.png"
    fname_schoenfeld: str = "schoenfeld_residuals.png"


CFG = CoxConfig()
FIG_CFG = FigureConfig()
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-1-1 | CoxConfig paths + columns | panel_path, figures_dir, results_path, all column name fields |
| C-1-2 | CoxConfig model + gate + forest | penalizer, lrt_df, p_threshold, hr_effect_threshold, forest plot styling fields |

---

## C2: KM + Partial Effects Config [A-7 KM quartile, complexity 8]

**Applied**: dataclass-per-concern (H-E1 pattern — fields added to CoxConfig above)

KM and partial effects parameters are embedded in CoxConfig and FigureConfig (no separate class needed — YAGNI). Below are the relevant field excerpts and the YAML schema for reproducibility logging.

### KM Quartile Fields (in CoxConfig)

```python
# Already in CoxConfig above:
km_col: str = "log_unique_paper_count_at_intro"   # raw (non-z) for interpretable quartile labels
# fig_size_wide used for KM figure (12, 5) — from FigureConfig
# fname_km_quartiles = "km_quartiles.png" — from FigureConfig
```

Quartile split strategy: `pd.qcut(panel_df[km_col], q=4, labels=False)` — Q1 (label=0) vs Q4 (label=3).

### Partial Effects Fields (in CoxConfig)

```python
# Embed as class-level constant (not a field — value never changes for this experiment)
PARTIAL_EFFECTS_VALUES: List[int] = [-2, -1, 0, 1, 2]   # z-score range for diversity_col
# y-axis label set in visualization.py: "Survival probability"
# fig_size_single (8, 5) used — from FigureConfig
```

### YAML Schema (Reproducibility Logging)

Saved alongside `experiment_results.json` as `experiment_config.yaml`:

```yaml
# H-M1 experiment configuration — auto-generated, do not edit manually
hypothesis_id: "H-M1"
date: "2026-08-03"

paths:
  panel_path: "docs/youra_research/h-e1/h_e2_panel_with_diversity.csv"
  figures_dir: "docs/youra_research/h-m1/figures"
  results_path: "docs/youra_research/h-m1/experiment_results.json"

columns:
  duration_col: "duration"
  event_col: "event"
  base_covariates:
    - "task_age"
    - "log_publication_volume"
    - "benchmark_introduction_year"
  diversity_col: "log_unique_paper_count_at_intro_z"
  km_col: "log_unique_paper_count_at_intro"

model:
  penalizer: 0.1
  penalizer_fallback: 0.5
  lrt_df: 1

gate:
  p_threshold: 0.05
  hr_effect_threshold: 0.10

visualization:
  dpi: 150
  partial_effects_values: [-2, -1, 0, 1, 2]
  km_quartile_strategy: "pd.qcut q=4, compare Q1 vs Q4"
  forest_fig_size: [10, 6]
  forest_sig_color: "#2ecc71"
  forest_nonsig_color: "#3498db"

panel_assertions:
  expected_rows: 345
  expected_min_cols: 8
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-2-1 | KM config fields | km_col, quartile split strategy, figure size mapping |
| C-2-2 | Partial effects + YAML schema | values list, y-axis label, full YAML for reproducibility logging |
