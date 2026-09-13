"""Configuration for H-E1: Confidence Margin Predicts Argmax Flip (EXISTENCE PoC)."""

import os

# Base hypothesis folder path (resolved at runtime)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HYPOTHESIS_DIR = os.path.dirname(BASE_DIR)  # h-e1/

MODEL_PAIRS = [
    {"pair_id": "pair1", "base": "allenai/tulu-2-7b",      "aligned": "allenai/tulu-2-ppo-7b",              "method": "PPO"},
    {"pair_id": "pair2", "base": "allenai/tulu-2-7b",      "aligned": "allenai/tulu-2-dpo-7b",              "method": "DPO"},
    {"pair_id": "pair3", "base": "EleutherAI/pythia-1.4b", "aligned": "reciprocate/ppo_hh_pythia-1B",       "method": "PPO"},
    {"pair_id": "pair4", "base": "EleutherAI/pythia-6.9b", "aligned": "dvruette/oasst-pythia-6.9b-4000-steps", "method": "SFT"},
]

DATASETS = [
    {"name": "mmlu",       "hf_id": "cais/mmlu",        "config": "all",             "split": "test"},
    {"name": "truthfulqa", "hf_id": "truthful_qa",       "config": "multiple_choice", "split": "validation"},
    {"name": "arc",        "hf_id": "allenai/ai2_arc",   "config": "ARC-Challenge",   "split": "test"},
]

CACHE_DIR   = os.path.join(HYPOTHESIS_DIR, "cache")
FIGURES_DIR = os.path.join(HYPOTHESIS_DIR, "figures")
RESULTS_DIR = os.path.join(HYPOTHESIS_DIR, "results")
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")
SEED        = 42

TORCH_DTYPE = "float16"
DEVICE_MAP  = "auto"
BATCH_SIZE  = 1

GATE_THRESHOLDS = {
    "beta1_max":        0.0,
    "pvalue_max":       0.005,
    "auroc_min":        0.75,
    "partial_eta2_min": 0.06,
}

VIZ_CONFIG = {
    "figsize":       (10, 6),
    "dpi":           150,
    "n_quintiles":   5,
    "color_palette": "colorblind",
    "save_formats":  ["pdf", "png"],
}
