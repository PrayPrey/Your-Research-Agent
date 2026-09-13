"""
Configuration settings for the Mutual Calibration Framework experiments.
"""

import os

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(BASE_DIR, "results")
FIGURES_DIR = os.path.join(RESULTS_DIR, "figures")

# Model settings
MODEL_CONFIG = {
    "ensemble_size": 5,
    "hidden_dim": 128,
    "calibration_hidden_dim": 64,
    "deference_hidden_dim": 64,
    "user_profile_dim": 32,
    "dropout": 0.1,
}

# Training settings
TRAINING_CONFIG = {
    "batch_size": 64,
    "learning_rate": 1e-3,
    "epochs": 50,
    "patience": 10,
    "weight_decay": 1e-4,
}

# Loss weights (lambda values from proposal)
LOSS_WEIGHTS = {
    "accuracy": 1.0,
    "calibration": 0.5,
    "reliance": 0.3,
    "deference": 0.2,
}

# Experiment settings
EXPERIMENT_CONFIG = {
    "num_simulated_users": 100,
    "interactions_per_user": 50,
    "expertise_levels": ["novice", "intermediate", "expert"],
    "deference_threshold_high": 0.7,
    "deference_threshold_low": 0.3,
}

# Random seed for reproducibility
SEED = 42

# Device settings
import torch
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
