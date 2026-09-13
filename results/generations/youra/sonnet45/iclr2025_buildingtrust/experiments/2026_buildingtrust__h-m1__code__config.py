"""Configuration for H-M1: Logit Delta Anisotropy Analysis.

H-M1 MECHANISM hypothesis: extends H-E1 with logit delta covariance eigendecomposition.
Seed changed from 42 (H-E1) to 1 for controlled comparison.
"""

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HYPOTHESIS_DIR = os.path.dirname(BASE_DIR)  # h-m1/

# H-E1 code path for importing data_loader and model_runner
HE1_CODE_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "..", "h-e1", "code"))

# 3 model pairs: pair2 (DPO), pair4 (SFT), pair_new (PPO)
# NOTE: allenai/tulu-2-ppo-7b (404) and reciprocate/ppo_hh_pythia-1B (tokenizer error) excluded
MODEL_PAIRS = [
    {
        "pair_id": "pair2",
        "base": "allenai/tulu-2-7b",
        "aligned": "allenai/tulu-2-dpo-7b",
        "method": "DPO",
    },
    {
        "pair_id": "pair4",
        "base": "EleutherAI/pythia-6.9b",
        "aligned": "dvruette/oasst-pythia-6.9b-4000-steps",
        "method": "SFT",
    },
    {
        "pair_id": "pair_new",
        "base": "EleutherAI/pythia-1.4b",
        "aligned": "pvduy/pythia-1.4b-rl-trlx-dolly15k",
        "method": "PPO",
    },
]

DATASETS = [
    {"name": "mmlu",       "hf_id": "cais/mmlu",       "config": "all",             "split": "test"},
    {"name": "truthfulqa", "hf_id": "truthful_qa",      "config": "multiple_choice", "split": "validation"},
    {"name": "arc",        "hf_id": "allenai/ai2_arc",  "config": "ARC-Challenge",   "split": "test"},
]

CACHE_DIR = os.path.join(HYPOTHESIS_DIR, "cache")
FIGURES_DIR = os.path.join(HYPOTHESIS_DIR, "figures")
SEED = 1          # Changed from H-E1's 42 for controlled comparison

TORCH_DTYPE = "float16"
DEVICE_MAP = "auto"
BATCH_SIZE = 1

GATE_THRESHOLDS = {
    "anisotropy_ratio_min": 1.0,   # r = λ₁ / mean(λ₂,λ₃,λ₄) must exceed this
    "pvalue_max": 0.05,            # paired t-test significance threshold
    "families_min": 2,             # minimum families passing both criteria
}

VIZ_CONFIG = {
    "figsize": (10, 6),
    "dpi": 150,
    "n_quintiles": 5,
    "color_palette": "colorblind",
    "save_formats": ["pdf", "png"],
}

# Figure-specific configs
FIG1_CONFIG = {
    "figsize": (10, 6),
    "dpi": 150,
    "threshold_line": 1.0,
    "bar_color": "steelblue",
    "threshold_color": "red",
    "save_name": "fig1_anisotropy_gate_metrics",
}

FIG2_CONFIG = {
    "figsize": (12, 5),
    "dpi": 150,
    "save_name": "fig2_eigenvalue_spectrum",
}

FIG3_CONFIG = {
    "figsize": (8, 7),
    "dpi": 150,
    "n_quintiles": 5,
    "cmap": "viridis",
    "save_name": "fig3_delta_pca",
}

FIG4_CONFIG = {
    "figsize": (8, 5),
    "dpi": 150,
    "n_quintiles": 5,
    "marker": "o",
    "save_name": "fig4_anisotropy_by_quintile",
}

FIG5_CONFIG = {
    "figsize": (10, 6),
    "dpi": 150,
    "methods": ["DPO", "SFT", "PPO"],
    "axes": ["decision", "orthogonal_1", "orthogonal_2", "orthogonal_3"],
    "save_name": "fig5_method_comparison",
}
