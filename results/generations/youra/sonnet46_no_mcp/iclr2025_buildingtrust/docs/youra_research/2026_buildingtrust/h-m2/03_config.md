# Configuration: H-M2
# Epistemic Composite Predictive Validity for Adversarial Robustness

Applied: module_level_constants_pattern (matching H-M1 codebase convention)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Config classes verified from H-M1 actual code
**Config Files Found**: `h-m1/code/config.py`
**Pattern Used**: module-level constants (no dataclass — consistent with H-M1)

---

## Inherited Configuration (Base Hypothesis)

From `/h-m1/code/config.py` (ACTUAL CODE — verified field names):

```python
# Inherited patterns from H-M1:
N_BOOTSTRAP: int = 10_000          # ← same value in H-M2
BOOTSTRAP_SEED: int = 42           # ← same value in H-M2
REQUIRED_COLS: list[str] = [...]   # ← extended in H-M2 (same columns)
FIGURE_DPI: int = 150              # ← same value in H-M2
FIGURE_FORMAT: str = "png"         # ← same value in H-M2
# Path pattern: _CODE_DIR / _BASE anchor from os.path.abspath(__file__)
```

H-M1 uses module-level typed constants (no dataclass). H-M2 follows the same pattern.

---

## A-7: Visualizer — Corr+Feature Figures [Complexity: 10, Budget: 1 subtask]

Applied: module_level_constants_pattern

### Configuration

```python
# In h-m2/code/config.py — Corr + Feature figure constants

FIGURE_DPI: int = 150
FIGURE_FORMAT: str = "png"

FIGURE_NAMES: dict = {
    "partial_correlation_comparison": "fig3_partial_correlation_comparison.png",
    "feature_importance":             "fig5_feature_importance.png",
    "epistemic_vs_adversarial_scatter": "fig6_epistemic_vs_adversarial_scatter.png",
    # Also used by A-6:
    "gate_metrics_comparison":        "fig1_gate_metrics_comparison.png",
    "roc_curves_comparison":          "fig2_roc_curves_comparison.png",
    "advglue_drop_distribution":      "fig4_advglue_drop_distribution.png",
}

# Scatter plot settings
SCATTER_ALPHA: float = 0.75
SCATTER_SIZE: int = 60

# Feature importance (LOO coefficient) settings
COEF_CI_ALPHA: float = 0.05        # 95% CI band for coefficient stability
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-7-1 | figure-config | Define FIGURE_NAMES dict + scatter/coef display constants |

---

## A-6: Visualizer — AUC Figures [Complexity: 9, Budget: 1 subtask]

Applied: module_level_constants_pattern

### Configuration

```python
# In h-m2/code/config.py — AUC figure + gate threshold constants

AUC_THRESHOLD: float = 0.70
DELTA_AUC_THRESHOLD: float = 0.10

# ROC curve display
ROC_LINEWIDTH: float = 2.0
ROC_DIAGONAL_STYLE: str = "--"

# Bar chart (gate_metrics_comparison)
BAR_CAPSIZE: int = 5
BAR_ALPHA: float = 0.85
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-6-1 | auc-figure-config | Gate threshold constants + ROC/bar chart display settings |

---

## A-10: Tests [Complexity: 9, Budget: 1 subtask]

Applied: pytest_fixture_design_pattern

### Configuration

```python
# In h-m2/code/config.py — test fixture sizing

MIN_MODELS: int = 25               # inherited from H-M1 logic
TEST_N_MODELS: int = 10            # small synthetic fixture (fast CI)
TEST_BOOTSTRAP_N: int = 100        # reduced bootstrap for test speed
TEST_SEED: int = 42
```

```python
# In h-m2/tests/conftest.py

import pytest
import numpy as np
import pandas as pd
from config import (
    REQUIRED_COLS, COMPOSITE_COLS, BASELINE_COLS, TARGET_COL,
    TEST_N_MODELS, TEST_SEED,
)

@pytest.fixture
def synthetic_score_matrix():
    rng = np.random.default_rng(TEST_SEED)
    n = TEST_N_MODELS
    df = pd.DataFrame({
        "model_id":         [f"model_{i}" for i in range(n)],
        "ECE":              rng.uniform(0.01, 0.30, n),
        "Brier":            rng.uniform(0.05, 0.40, n),
        "TruthfulQA_pct":   rng.uniform(0.20, 0.80, n),
        "AdvGLUE_drop":     rng.uniform(0.0,  0.50, n),
        "ANLI_drop":        rng.uniform(0.0,  0.40, n),
        "MMLU_acc":         rng.uniform(0.30, 0.85, n),
        "HumanEval_pass1":  rng.uniform(0.0,  0.60, n),
    })
    threshold = df["AdvGLUE_drop"].quantile(0.75)
    df[TARGET_COL] = (df["AdvGLUE_drop"] >= threshold).astype(int)
    return df

@pytest.fixture
def results_dir(tmp_path):
    d = tmp_path / "results"
    d.mkdir()
    return d

@pytest.fixture
def figures_dir(tmp_path):
    d = tmp_path / "figures"
    d.mkdir()
    return d
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-10-1 | pytest-fixture-design | conftest.py with synthetic_score_matrix, results_dir, figures_dir fixtures; reduced bootstrap N for test speed |

---

## Complete config.py (H-M2)

```python
from __future__ import annotations
import os

_CODE_DIR = os.path.dirname(os.path.abspath(__file__))   # h-m2/code/
_HM2_DIR  = os.path.dirname(_CODE_DIR)                   # h-m2/
_BASE     = os.path.dirname(_HM2_DIR)                    # research folder

# --- Paths ---
SCORE_MATRIX_PATH: str = os.path.join(_BASE, "h-e1", "results", "score_matrix.csv")
RESULTS_DIR: str       = os.path.join(_BASE, "h-m2", "results")
FIGURES_DIR: str       = os.path.join(_BASE, "h-m2", "figures")

# --- Bootstrap (inherited from H-M1) ---
N_BOOTSTRAP: int   = 10_000
BOOTSTRAP_SEED: int = 42

# --- Column definitions ---
REQUIRED_COLS: list[str] = [
    "model_id", "ECE", "Brier", "TruthfulQA_pct",
    "AdvGLUE_drop", "ANLI_drop", "MMLU_acc", "HumanEval_pass1",
]
COMPOSITE_COLS: list[str] = ["ECE", "TruthfulQA_pct", "Brier"]
BASELINE_COLS: list[str]  = ["MMLU_acc"]
TARGET_COL: str           = "top_quartile_advglue"
PARTIAL_X: str            = "ECE"
PARTIAL_Y_ADV: str        = "AdvGLUE_drop"
PARTIAL_Y_ANLI: str       = "ANLI_drop"
COVARIATE: str            = "MMLU_acc"
MIN_MODELS: int           = 25

# --- Gate thresholds ---
AUC_THRESHOLD: float          = 0.70
DELTA_AUC_THRESHOLD: float    = 0.10
PARTIAL_RHO_THRESHOLD: float  = 0.40
ANLI_RHO_THRESHOLD: float     = 0.30

# --- Logistic regression ---
LR_C: float     = 1.0
LR_MAX_ITER: int = 1000
TOP_QUARTILE: float = 0.75

# --- Figures ---
FIGURE_DPI: int    = 150
FIGURE_FORMAT: str = "png"
FIGURE_NAMES: dict = {
    "gate_metrics_comparison":          "fig1_gate_metrics_comparison.png",
    "roc_curves_comparison":            "fig2_roc_curves_comparison.png",
    "partial_correlation_comparison":   "fig3_partial_correlation_comparison.png",
    "advglue_drop_distribution":        "fig4_advglue_drop_distribution.png",
    "feature_importance":               "fig5_feature_importance.png",
    "epistemic_vs_adversarial_scatter": "fig6_epistemic_vs_adversarial_scatter.png",
}

# Figure display constants
SCATTER_ALPHA: float    = 0.75
SCATTER_SIZE: int       = 60
ROC_LINEWIDTH: float    = 2.0
ROC_DIAGONAL_STYLE: str = "--"
BAR_CAPSIZE: int        = 5
BAR_ALPHA: float        = 0.85
COEF_CI_ALPHA: float    = 0.05

# --- Test-only constants ---
TEST_N_MODELS: int    = 10
TEST_BOOTSTRAP_N: int = 100
TEST_SEED: int        = 42
```
