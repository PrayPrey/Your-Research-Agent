"""
Configuration file for the causal data valuation experiment.
"""

import torch
import os

# Device configuration
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
NUM_GPUS = torch.cuda.device_count()

# Model configuration
MODEL_CONFIGS = {
    "small": {
        "hidden_size": 256,
        "num_layers": 4,
        "num_heads": 4,
        "vocab_size": 5000,
        "max_seq_length": 128,
        "dropout": 0.1
    },
    "medium": {
        "hidden_size": 512,
        "num_layers": 6,
        "num_heads": 8,
        "vocab_size": 10000,
        "max_seq_length": 256,
        "dropout": 0.1
    }
}

# Training configuration for different stages
STAGE_CONFIGS = {
    "pretraining": {
        "batch_size": 32,
        "learning_rate": 1e-4,
        "num_epochs": 10,
        "warmup_steps": 100,
        "weight_decay": 0.01,
        "objective": "next_token_prediction"
    },
    "instruction_tuning": {
        "batch_size": 16,
        "learning_rate": 5e-5,
        "num_epochs": 5,
        "warmup_steps": 50,
        "weight_decay": 0.01,
        "objective": "supervised_finetuning"
    },
    "alignment": {
        "batch_size": 8,
        "learning_rate": 1e-5,
        "num_epochs": 3,
        "warmup_steps": 20,
        "weight_decay": 0.01,
        "objective": "preference_learning"
    }
}

# Data configuration
DATA_CONFIG = {
    "pretrain_samples": 5000,
    "instruction_samples": 1000,
    "alignment_samples": 500,
    "test_samples": 200,
    "validation_split": 0.1,
    "seed": 42
}

# Valuation configuration
VALUATION_CONFIG = {
    "num_samples": 100,  # Number of samples to value
    "low_rank_dim": 50,  # Low-rank approximation dimension
    "num_coalitions": 20,  # For Shapley value estimation
    "influence_batch_size": 16,
    "checkpoint_freq": 1  # Save checkpoint every N stages
}

# Experiment configuration
EXPERIMENT_CONFIG = {
    "model_size": "small",
    "num_runs": 3,  # Number of independent runs for averaging
    "save_checkpoints": True,
    "compute_ground_truth": True,
    "methods": [
        "stage_aware_influence",  # Our proposed method
        "standard_influence",     # Standard influence functions
        "data_shapley",          # Data Shapley
        "tracin",                # TracIn
        "random_baseline"        # Random valuation
    ]
}

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
RESULTS_DIR = os.path.join(BASE_DIR, "results")
CHECKPOINT_DIR = os.path.join(BASE_DIR, "checkpoints")

# Create directories if they don't exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)
os.makedirs(CHECKPOINT_DIR, exist_ok=True)
