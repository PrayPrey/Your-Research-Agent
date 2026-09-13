# Configuration: H-E1
## Residual Instability — Existence & Construct Validity (PoC)

**Hypothesis:** H-E1 (EXISTENCE / FOUNDATION)
**Type:** Statistical Analysis Pipeline
**Tier:** LIGHT

Applied: typed-module-constants pattern (YAML + dataclass config for statistical pipeline)

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field — no existing codebase to analyze. Serena skipped.
**Config Files Found**: None - new config design
**Pattern Used**: dataclass + YAML schema

---

## Overview

- **Hypothesis ID**: H-E1
- **Type**: EXISTENCE / Statistical Analysis
- **Tier**: LIGHT
- No neural network training; all parameters are statistical thresholds and I/O paths.
- Single seed (42), no hyperparameter tuning required.

---

## Config Module (code/config.py)

```python
"""
config.py — Fixed constants for H-E1 Residual Instability pipeline.

All values are EXISTENCE-tier defaults; no tuning is performed.
"""

from __future__ import annotations

# Reproducibility
SEED: int = 42

# Gate thresholds (from hypothesis specification)
SD_THRESHOLD: float = 0.05   # Gate 1: SD(AdvGLUE_drop) must exceed this
R2_THRESHOLD: float = 0.80   # Gate 2: R²_residualization must be below this

# PCA quality guard: PC1 must explain at least this fraction of variance
PC1_VAR_THRESHOLD: float = 0.70

# Multicollinearity guard: VIF must be below this value
VIF_THRESHOLD: float = 5.0

# Bootstrap confidence intervals
N_BOOTSTRAP: int = 10000

# Dataset size requirements
MIN_MODELS: int = 30    # Minimum number of LLMs required
MIN_FAMILIES: int = 3   # Minimum distinct model families required

# Capability columns fed into PCA
CAP_COLS: list[str] = ["mmlu", "gsm8k", "bbh", "hellaswag", "winogrande"]

# Output directories (relative to h-e1/)
RESULTS_DIR: str = "results"
FIGURES_DIR: str = "figures"
```

---

## Experiment Configuration YAML Schema

```yaml
experiment:
  hypothesis_id: "h-e1"
  seed: 42
  tier: "LIGHT"

data:
  trustllm_data_dir: "data/trustllm"
  lmeval_results_dir: "data/lmeval"
  min_models: 30
  min_families: 3
  cap_cols:
    - mmlu
    - gsm8k
    - bbh
    - hellaswag
    - winogrande

analysis:
  sd_threshold: 0.05
  r2_threshold: 0.80
  pc1_var_threshold: 0.70
  vif_threshold: 5.0
  n_bootstrap: 10000

visualization:
  figures_dir: "figures"
  figure_dpi: 300
  figure_format: "png"
  style: "seaborn-v0_8-whitegrid"
  palette: "muted"
  figsize_default: [8, 5]

output:
  results_dir: "results"
  matrix_csv: "results/model_matrix.csv"
  ri_csv: "results/ri_scores.csv"
  gate_yaml: "results/gate_results.yaml"
  summary_json: "results/summary.json"
```

---

## Dataclass Definitions

```python
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class DataConfig:
    trustllm_data_dir: str = "data/trustllm"
    lmeval_results_dir: str = "data/lmeval"
    min_models: int = 30
    min_families: int = 3
    cap_cols: list[str] = field(default_factory=lambda: [
        "mmlu", "gsm8k", "bbh", "hellaswag", "winogrande"
    ])


@dataclass
class AnalysisConfig:
    seed: int = 42
    sd_threshold: float = 0.05
    r2_threshold: float = 0.80
    pc1_var_threshold: float = 0.70
    vif_threshold: float = 5.0
    n_bootstrap: int = 10000


@dataclass
class VisualizationConfig:
    figures_dir: str = "figures"
    figure_dpi: int = 300
    figure_format: str = "png"
    style: str = "seaborn-v0_8-whitegrid"
    palette: str = "muted"
    figsize_default: tuple[int, int] = (8, 5)
    # Per-figure sizes
    figsize_bar: tuple[int, int] = (10, 5)
    figsize_violin: tuple[int, int] = (8, 6)
    figsize_hist: tuple[int, int] = (7, 5)
    figsize_scatter: tuple[int, int] = (7, 6)
    figsize_box: tuple[int, int] = (9, 6)


@dataclass
class ExperimentConfig:
    hypothesis_id: str = "h-e1"
    data: DataConfig = field(default_factory=DataConfig)
    analysis: AnalysisConfig = field(default_factory=AnalysisConfig)
    visualization: VisualizationConfig = field(default_factory=VisualizationConfig)
    results_dir: str = "results"
```

---

## requirements.txt

```
pandas>=2.0
numpy>=1.24
scikit-learn>=1.3
pingouin==0.6.1
scipy>=1.10
statsmodels>=0.14
matplotlib>=3.7
seaborn>=0.12
datasets>=2.14
lm-eval>=0.4.0
pyyaml>=6.0
```

---

## A-E4: Visualization Configuration [Complexity: 1, Budget: 1]

**Applied**: Standard matplotlib/seaborn defaults with 300 DPI publication output

### Configuration (Python Dataclass)

```python
@dataclass
class VisualizationConfig:
    figures_dir: str = "figures"
    figure_dpi: int = 300
    figure_format: str = "png"
    style: str = "seaborn-v0_8-whitegrid"
    palette: str = "muted"
    figsize_default: tuple[int, int] = (8, 5)
    figsize_bar: tuple[int, int] = (10, 5)
    figsize_violin: tuple[int, int] = (8, 6)
    figsize_hist: tuple[int, int] = (7, 5)
    figsize_scatter: tuple[int, int] = (7, 6)
    figsize_box: tuple[int, int] = (9, 6)
```

### C-E4-1: Visualization Configuration Subtask [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-E4-1 | Visualization config | Define per-figure size/style settings for all 5 required figures |

### Figure-by-Figure Settings

**fig_gate_metrics.png** (bar chart)
- `figsize`: (10, 5)
- x-axis: gate metric names (SD_AdvGLUE, R2_residualization)
- y-axis: metric value with threshold hline overlay
- color: two bars in `palette="muted"`, threshold lines in red dashed

**fig_ri_distribution.png** (violin plot)
- `figsize`: (8, 6)
- x-axis: model_family
- y-axis: RI score
- hue: training_regime
- inner: "box" (show quartiles inside violin)

**fig_advglue_hist.png** (histogram)
- `figsize`: (7, 5)
- x-axis: advglue_drop values
- bins: 20
- kde overlay: True
- vline at mean and ±1 SD

**fig_pc1_scatter.png** (scatter plot)
- `figsize`: (7, 6)
- x-axis: pc1_score
- y-axis: advglue_drop
- hue: model_family
- regression line overlay via `seaborn.regplot`

**fig_ri_regime.png** (box plot)
- `figsize`: (9, 6)
- x-axis: scale (7B / 13B / 70B+)
- y-axis: ri_score
- hue: training_regime
- showfliers: True
