# Config: H-M3 - FLAN Taxonomy Correlation with Grassmann Distances

**Applied**: correlation-analysis-reuse pattern
**Applied**: spearman-bootstrap-ci pattern

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Config classes verified from actual H-E1 code (read via filesystem)
**Config Files Found**: `h-e1/code/config.py`
**Pattern Used**: hardcoded dict (consistent with H-E1 style)

---

## Inherited Configuration (Base Hypothesis)

From `h-e1/code/config.py` (actual code - verified field names):

```python
# H-E1 actual field names (verified)
TASK_CATEGORIES = {           # field name: TASK_CATEGORIES (not FLAN_CATEGORIES)
    "gsm8k": "reasoning",
    "arc": "reasoning",
    "logiqa": "reasoning",
    "strategyqa": "reasoning",
    "mnli": "nlu",
    "qqp": "nlu",
    "sst2": "nlu",
    "mrpc": "nlu",
}

ANALYSIS_CONFIG = dict(       # H-E1 uses: p_threshold, cohens_d_threshold, ci_level, n_bootstrap=10000
    p_threshold=0.05,
    cohens_d_threshold=0.5,
    ci_level=0.95,
    n_bootstrap=10000,
)

CONTROL_SEEDS = [42, 43, 44, 45, 46]   # field: CONTROL_SEEDS
PRIMARY_SEED = 42                        # field: PRIMARY_SEED

# Path pattern (verified):
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
HYPOTHESIS_FOLDER = os.path.dirname(_SCRIPT_DIR)
RESULTS_DIR = os.path.join(HYPOTHESIS_FOLDER, "results")
FIGURES_DIR = os.path.join(HYPOTHESIS_FOLDER, "figures")
```

**Key differences in H-M3**: H-E1 uses `TASK_CATEGORIES`; H-M3 uses `FLAN_CATEGORIES` (same content, renamed for clarity). H-E1 `n_bootstrap=10000`; H-M3 uses `n_bootstrap=1000` (analysis-only, faster). H-M3 adds `spearman_rho_threshold` and `p3_ratio_threshold` not present in H-E1.

---

## A-4: TaxonomyMatrix [Complexity: 8, Budget: 2 subtasks]

**Applied**: Standard hardcoded dict pattern

### Configuration

```python
# In config.py

FLAN_CATEGORIES: dict[str, str] = {
    "gsm8k": "reasoning",
    "arc": "reasoning",
    "logiqa": "reasoning",
    "strategyqa": "reasoning",
    "mnli": "nlu",
    "qqp": "nlu",
    "sst2": "nlu",
    "mrpc": "nlu",
}

TAXONOMY_CONFIG: dict = {
    "mode": "binary",          # 0=same category, 1=different category
    "n_tasks": 8,
    "n_adapters": 40,          # 8 tasks x 5 seeds
}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-4-1 | Build matrix | `build_taxonomy_distance_matrix` using FLAN_CATEGORIES binary mode |
| C-4-2 | Validate & save | Verify (40,40) shape, symmetry, zero diagonal; save taxonomy_distances.npy |

---

## A-8/A-9/A-10/A-11: Visualization Configs [Budget: 2 subtasks]

**Applied**: Standard matplotlib/seaborn defaults

### Configuration

```python
# In config.py

VIZ_CONFIG: dict = {
    # Figure sizes
    "bar_chart_figsize": (7, 5),
    "scatter_figsize": (7, 6),
    "heatmap_figsize": (8, 7),
    "distribution_figsize": (8, 5),
    # Color scheme
    "reasoning_color": "#4C72B0",
    "nlu_color": "#DD8452",
    "threshold_line_color": "red",
    "regression_line_color": "steelblue",
    # Seaborn style
    "style": "whitegrid",
    "font_scale": 1.1,
    # Output
    "dpi": 150,
    "format": "png",
}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-V-1 | Static figure configs | figsize, colors, style, dpi for all 4 plots |
| C-V-2 | Annotation params | Threshold lines, CI error bars, regression annotation format |

---

## Full config.py (Copy-Paste Ready)

```python
"""Configuration for H-M3: FLAN Taxonomy Correlation with Grassmann Distances."""

import os
import sys

# H-E1 bridge: add h-e1/code to sys.path
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
H_E1_CODE_DIR = os.path.abspath(os.path.join(_SCRIPT_DIR, "../../h-e1/code"))
H_E1_HYPOTHESIS_DIR = os.path.abspath(os.path.join(_SCRIPT_DIR, "../../h-e1"))
if H_E1_CODE_DIR not in sys.path:
    sys.path.insert(0, H_E1_CODE_DIR)

# Output paths
HYPOTHESIS_FOLDER = os.path.dirname(_SCRIPT_DIR)
RESULTS_DIR = os.path.join(HYPOTHESIS_FOLDER, "results")
FIGURES_DIR = os.path.join(HYPOTHESIS_FOLDER, "figures")

for _dir in [RESULTS_DIR, FIGURES_DIR]:
    os.makedirs(_dir, exist_ok=True)

# FLAN taxonomy - ground truth categories (same content as H-E1 TASK_CATEGORIES)
FLAN_CATEGORIES: dict = {
    "gsm8k": "reasoning",
    "arc": "reasoning",
    "logiqa": "reasoning",
    "strategyqa": "reasoning",
    "mnli": "nlu",
    "qqp": "nlu",
    "sst2": "nlu",
    "mrpc": "nlu",
}

TASKS: list = list(FLAN_CATEGORIES.keys())   # ordered list of 8 tasks
SEEDS: list = [42, 43, 44, 45, 46]
N_ADAPTERS: int = 40  # 8 tasks x 5 seeds

# Taxonomy matrix config
TAXONOMY_CONFIG: dict = {
    "mode": "binary",
    "n_tasks": 8,
    "n_adapters": 40,
}

# Analysis thresholds and bootstrap params
ANALYSIS_CONFIG: dict = {
    "spearman_rho_threshold": 0.3,
    "p_threshold": 0.05,
    "n_bootstrap": 1000,       # 1000 sufficient for analysis-only (H-E1 used 10000 for training gate)
    "random_seed": 42,
    "p3_ratio_threshold": 0.5,
    "ci_level": 0.95,
}

# Visualization params
VIZ_CONFIG: dict = {
    "bar_chart_figsize": (7, 5),
    "scatter_figsize": (7, 6),
    "heatmap_figsize": (8, 7),
    "distribution_figsize": (8, 5),
    "reasoning_color": "#4C72B0",
    "nlu_color": "#DD8452",
    "threshold_line_color": "red",
    "regression_line_color": "steelblue",
    "style": "whitegrid",
    "font_scale": 1.1,
    "dpi": 150,
    "format": "png",
}
```
