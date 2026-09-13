"""Configuration for H-M3: FLAN Taxonomy Correlation with Grassmann Distances."""

import os
import sys

# Path setup: h-m3/code first, then h-e1/code for bridge imports
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
H_E1_CODE_DIR = os.path.abspath(os.path.join(_SCRIPT_DIR, "../../h-e1/code"))
H_E1_HYPOTHESIS_DIR = os.path.abspath(os.path.join(_SCRIPT_DIR, "../../h-e1"))

# Ensure h-m3/code is first in path (for local modules like visualize.py)
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)

# Add h-e1/code for bridge imports (after h-m3/code)
if H_E1_CODE_DIR not in sys.path:
    sys.path.append(H_E1_CODE_DIR)  # append, not insert

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

# Alias for H-E1 compatibility (H-E1 analyze.py imports TASK_CATEGORIES)
TASK_CATEGORIES = FLAN_CATEGORIES

# H-E1 compatibility exports (required when h-e1/code/analyze.py is imported)
ADAPTER_DIR = os.path.join(H_E1_HYPOTHESIS_DIR, "adapters")
LORA_CONFIG = {
    "r": 32,
    "lora_alpha": 64,
    "lora_dropout": 0.05,
    "target_modules": ["q_proj", "k_proj", "v_proj", "o_proj", "up_proj", "down_proj", "gate_proj"],
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
    "n_bootstrap": 1000,       # 1000 sufficient for analysis-only
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
