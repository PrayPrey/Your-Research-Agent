"""Configuration for H-M4: Layer-wise Grassmann Distance Analysis."""

import os
import sys

# Path setup
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# H-E1 paths (adapter data source)
H_E1_DIR = os.path.abspath(os.path.join(_SCRIPT_DIR, "../../h-e1"))
H_E1_RESULTS_DIR = os.path.join(H_E1_DIR, "results")
H_E1_ADAPTER_DIR = os.path.join(H_E1_DIR, "adapters")
H_E1_CODE_DIR = os.path.join(H_E1_DIR, "code")

# Ensure h-m4/code is first in path
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)

# Add h-e1/code for bridge imports (after h-m4/code)
if H_E1_CODE_DIR not in sys.path:
    sys.path.append(H_E1_CODE_DIR)

# H-M4 output paths
HYPOTHESIS_FOLDER = os.path.dirname(_SCRIPT_DIR)
RESULTS_DIR = os.path.join(HYPOTHESIS_FOLDER, "results")
FIGURES_DIR = os.path.join(HYPOTHESIS_FOLDER, "figures")

for _dir in [RESULTS_DIR, FIGURES_DIR]:
    os.makedirs(_dir, exist_ok=True)

# Tasks and seeds (verified: integer seeds 0-4 from h-e1/results/adapter_metadata.json)
TASKS: list = ["gsm8k", "arc", "logiqa", "strategyqa", "mnli", "qqp", "sst2", "mrpc"]
SEEDS: list = [0, 1, 2, 3, 4]  # Integer seeds as in actual H-E1 metadata
N_ADAPTERS: int = 40  # 8 tasks x 5 seeds

# Task categories (FLAN taxonomy)
TASK_CATEGORIES: dict = {
    "gsm8k": "reasoning",
    "arc": "reasoning",
    "logiqa": "reasoning",
    "strategyqa": "reasoning",
    "mnli": "nlu",
    "qqp": "nlu",
    "sst2": "nlu",
    "mrpc": "nlu",
}

# Layer type definitions (TinyLlama architecture)
ATTENTION_LAYER_TYPES: list = ["q_proj", "k_proj", "v_proj", "o_proj"]
MLP_LAYER_TYPES: list = ["up_proj", "down_proj", "gate_proj"]
ALL_LAYER_TYPES: list = ATTENTION_LAYER_TYPES + MLP_LAYER_TYPES  # 7 total
N_TRANSFORMER_LAYERS: int = 22  # TinyLlama has 22 layers

# LoRA configuration
LORA_CONFIG: dict = {
    "r": 32,
    "lora_alpha": 64,
    "lora_dropout": 0.05,
    "target_modules": ALL_LAYER_TYPES,
}

# Analysis configuration
ANALYSIS_CONFIG: dict = {
    "cohens_d_threshold": 0.8,  # Gate threshold
    "n_bootstrap": 2000,
    "random_seed": 42,
    "ci_level": 0.95,
    "p_threshold": 0.05,
}

# Visualization configuration
VIZ_CONFIG: dict = {
    # Figure sizes per chart type
    "bar_chart_figsize": (10, 6),      # cohens_d_by_layer_type
    "ranking_figsize": (8, 6),         # layer_type_ranking (horizontal bars)
    "comparison_figsize": (8, 6),      # attention_vs_mlp box/violin
    "heatmap_figsize": (9, 7),         # best_layer_heatmap 8x8

    # Colors
    "attention_color": "#4C72B0",      # blue for attention layers
    "mlp_color": "#DD8452",            # orange for MLP layers
    "threshold_line_color": "red",

    # Style
    "style": "whitegrid",
    "font_scale": 1.1,
    "dpi": 150,
    "format": "png",
}

# Test configuration (for unit tests)
TEST_CONFIG: dict = {
    "random_seed": 42,
    "n_adapters_small": 4,    # small fixture: 2 tasks x 2 seeds
    "n_layers_small": 3,      # reduced layers for fast unit tests
    "lora_r": 4,              # small rank for test matrices
    "hidden_dim": 16,         # small hidden dim for test matrices
    "atol": 1e-5,             # tolerance for numerical comparisons
}
