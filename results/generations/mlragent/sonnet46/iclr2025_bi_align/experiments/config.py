"""Configuration for CAVE experiments."""

import torch

# Experiment settings
NUM_USERS = 100
NUM_TIMESTEPS = 200
NUM_VALUE_DIMS = 8  # e.g., privacy, autonomy, fairness, efficiency, honesty, safety, creativity, simplicity
NUM_CONTEXT_DIMS = 16
NUM_ACTIONS = 10
LATENT_DIM = 32
NUM_DEMOGRAPHIC_GROUPS = 4

# Training settings
LEARNING_RATE = 1e-3
BATCH_SIZE = 32
NUM_EPOCHS = 50
SEED = 42

# CAVE hyperparameters
ELICITATION_LAMBDA = 0.5  # tradeoff: uncertainty vs burden
ELICITATION_THRESHOLD = 0.3
DRIFT_THRESHOLD_PERCENTILE = 95  # KL divergence threshold percentile
VALUE_DRIFT_WINDOW = 20  # timesteps for drift detection

# Evaluation
HELD_OUT_FRACTION = 0.2
NUM_RUNS = 3

# Device
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
