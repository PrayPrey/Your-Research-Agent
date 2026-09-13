---
title: "Config: H-M2 — PCA Concentration Test"
hypothesis_id: H-M2
hypothesis_type: MECHANISM
tier: FULL
date: 2026-08-27
author: Anonymous
base_hypothesis: H-M1
budget: 2 subtasks (Config Agent allocation)
---

Applied: Dataclass-first config pattern (typed, default-complete)
Applied: Incremental config extension (inherit H-M1 dataset params; add PCA/regression settings)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-M1 incremental continuation)
**Status**: Config classes verified from H-M1 actual code and 03_config.md
**Config Files Found**: `h-m1/03_config.md` (DataConfig, VisualizationConfig patterns)
**Pattern Used**: dataclass

**Key findings from H-M1 actual code:**
- `data_loader.py`: `EXPECTED_DIM = 51850` — authoritative; PRD value of 50890 is incorrect
- `data_loader.py`: loader function is `load_zoo()` (not `load_local_zoo()` as PRD states)
- `data_loader.py`: data path is `./data/`
- `statistics.py`: bootstrap CI pattern available for reference

---

## Inherited Configuration

```python
# From: h-m1/03_config.md (verified against h-m1/code/data_loader.py)

# Dataset constants (unchanged in H-M2)
HF_IDENTIFIER = "schurholt/model_zoos_dataset"
HF_CONFIG = "mnist"
HF_SPLIT = "train+validation+test"
LOCAL_DATA_PATH = "./data/"
EXPECTED_WEIGHT_DIM = 51_850   # ← from actual code; PRD erroneously states 50890
SEED = 42
```

---

## C-6-1: Experiment Configuration

**Parent Epic**: E-6

```python
from dataclasses import dataclass, field


@dataclass
class ExperimentConfig:
    """Primary configuration for H-M2 PCA concentration test."""

    # Reproducibility
    seed: int = 42

    # Data
    data_path: str = "./data/"
    """Local zoo archive path. Same as H-M1."""

    expected_weight_dim: int = 51_850
    """Flat weight vector dimension per model. Fail-fast if mismatch."""

    # Train/test split
    test_size: int = 50
    """Number of held-out models (≈10% of 500). Consistent with H-M1."""

    # PCA sweep
    k_values: list = field(default_factory=lambda: [10, 20, 50])
    """PC counts for R² sweep."""

    # Bootstrap
    n_boot: int = 1000
    """Bootstrap resamples for 95% CI on each R²."""

    # Gate condition
    gate_k: int = 20
    """PC count used for gate comparison (R²_D vs R²_A)."""

    gate_threshold: float = 0.667
    """Fraction of tasks requiring non-overlapping CI pass. 2/3 = 0.667."""

    # Property labels
    property_labels: list = field(default_factory=lambda: [
        "test_accuracy",
        "generalization_gap",
        "learning_rate",
    ])

    # Output
    output_dir: str = "docs/youra_research/h-m2"
    results_path: str = "docs/youra_research/h-m2/results.json"

    # H-M1 code path (for reusing data_loader.py)
    h_m1_code_dir: str = "docs/youra_research/h-m1/code"
```

---

## C-4-1: Figure Configuration

**Parent Epic**: E-4

```python
@dataclass
class FigureConfig:
    """Configuration for H-M2 figure generation (5 figures)."""

    figures_dir: str = "docs/youra_research/h-m2/figures"
    dpi: int = 150
    format: str = "png"

    # Figure sizes
    figsize_bar: tuple = (8, 5)
    """Fig 1 (gate metric bar chart) and Fig 3 (delta R² bar)."""

    figsize_line: tuple = (10, 4)
    """Fig 2 (R² vs k line plot, 3 subplots side-by-side)."""

    figsize_scatter: tuple = (6, 5)
    """Fig 4 (PCA variance explained) and Fig 5 (scatter R²_D vs R²_A)."""

    # Color palette — Condition A (raw) vs Condition D (canonical)
    color_condition_a: str = "#1f77b4"   # matplotlib blue
    color_condition_d: str = "#d62728"   # matplotlib red (distinct from H-M1 orange)
    color_ci: str = "#aec7e8"            # light blue for CI bands
    color_pass: str = "#2ca02c"          # green for gate-pass indicators
    color_fail: str = "#d62728"          # red for gate-fail indicators

    # File naming convention
    # fig1_gate_metric.png       — mandatory gate bar: R²_D vs R²_A at k=20
    # fig2_r2_vs_k.png           — R² vs k sweep, both conditions, 3-panel
    # fig3_delta_r2.png          — ΔR² = R²_D − R²_A with CI, per task
    # fig4_pca_variance.png      — cumulative explained variance (A vs D)
    # fig5_r2_scatter.png        — scatter R²_D vs R²_A per (task, k)
    fig_names: dict = field(default_factory=lambda: {
        "gate_metric":    "fig1_gate_metric.png",
        "r2_vs_k":        "fig2_r2_vs_k.png",
        "delta_r2":       "fig3_delta_r2.png",
        "pca_variance":   "fig4_pca_variance.png",
        "r2_scatter":     "fig5_r2_scatter.png",
    })
```

---

## YAML Schema

```yaml
# h-m2/experiment_config.yaml

experiment:
  seed: 42
  data_path: "./data/"
  expected_weight_dim: 51850
  test_size: 50
  k_values: [10, 20, 50]
  n_boot: 1000
  gate_k: 20
  gate_threshold: 0.667
  property_labels:
    - "test_accuracy"
    - "generalization_gap"
    - "learning_rate"
  output_dir: "docs/youra_research/h-m2"
  results_path: "docs/youra_research/h-m2/results.json"
  h_m1_code_dir: "docs/youra_research/h-m1/code"

figures:
  figures_dir: "docs/youra_research/h-m2/figures"
  dpi: 150
  format: "png"
  figsize_bar: [8, 5]
  figsize_line: [10, 4]
  figsize_scatter: [6, 5]
  color_condition_a: "#1f77b4"
  color_condition_d: "#d62728"
  color_ci: "#aec7e8"
  color_pass: "#2ca02c"
  color_fail: "#d62728"
  fig_names:
    gate_metric:  "fig1_gate_metric.png"
    r2_vs_k:      "fig2_r2_vs_k.png"
    delta_r2:     "fig3_delta_r2.png"
    pca_variance: "fig4_pca_variance.png"
    r2_scatter:   "fig5_r2_scatter.png"
```

---

## Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-4-1 | Figure Configuration | FigureConfig dataclass + YAML section for all 5 figures |
| C-6-1 | Experiment Configuration | ExperimentConfig dataclass + YAML section covering all experiment params |
