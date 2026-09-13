"""Configuration for HalluConform experiment."""

import os

# Model configuration - use small model for efficiency
MODEL_NAME = "Qwen/Qwen3-0.6B"

# Data configuration
DATASETS = {
    "trivia_qa": {
        "hf_name": "trivia_qa",
        "hf_config": "rc",
        "split": "validation",
        "n_samples": 300,
        "domain": "factual",
        "risk_level": "low",
    },
    "medical_qa": {
        "hf_name": "medmcqa",
        "hf_config": None,
        "split": "validation",
        "n_samples": 200,
        "domain": "medical",
        "risk_level": "high",
    },
}

# Conformal prediction settings
ALPHA_BASE = 0.1  # base error rate (90% coverage)
ALPHA_RISK = {
    "low": 0.1,
    "medium": 0.05,
    "high": 0.01,
}

# Calibration split
CAL_RATIO = 0.5   # 50% for calibration
TEST_RATIO = 0.5  # 50% for test

# Generation settings
MAX_NEW_TOKENS = 50
BATCH_SIZE = 8

# Baselines
BASELINES = ["entropy_threshold", "max_prob_threshold", "length_normalized_entropy"]

# Output paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Device
import torch
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
