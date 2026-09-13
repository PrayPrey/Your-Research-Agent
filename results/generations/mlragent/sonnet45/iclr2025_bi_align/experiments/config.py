"""
Configuration file for Adaptive Alignment experiments
"""

import torch

# General settings
RANDOM_SEED = 42
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
NUM_RUNS = 3  # Number of experimental runs for averaging

# Dataset settings
NUM_USERS = 50  # Number of simulated users
NUM_TIMESTEPS = 100  # Number of interaction timesteps per user
NUM_CONTEXTS = 5  # Number of different contexts
FEATURE_DIM = 20  # Dimensionality of state features
ACTION_DIM = 10  # Number of possible actions

# Preference dynamics settings
PREFERENCE_DRIFT_RATE = 0.02  # Rate of gradual preference evolution
CONTEXT_SHIFT_PROB = 0.2  # Probability of context change
FUNDAMENTAL_CHANGE_PROB = 0.05  # Probability of fundamental value change

# Model hyperparameters
HIDDEN_DIM = 128
NUM_LAYERS = 3
LEARNING_RATE = 1e-4
BATCH_SIZE = 32
META_LEARNING_RATE = 1e-3

# Training settings
NUM_EPOCHS = 50
TEMPORAL_LAMBDA = 0.1  # Weight for temporal regularization
CONSISTENCY_THRESHOLD = 0.6  # Threshold for triggering reflection prompts

# Evaluation settings
EVAL_EVERY = 5  # Evaluate every N epochs
SAVE_CHECKPOINTS = False  # Don't save large checkpoints

# Scenario types for evaluation
SCENARIOS = ['gradual_drift', 'rapid_shift', 'value_conflict']

# Baseline configurations
BASELINES = {
    'static_alignment': {'temporal_modeling': False, 'bidirectional': False},
    'ceva_basic': {'temporal_modeling': True, 'bidirectional': False},
    'ceva_full': {'temporal_modeling': True, 'bidirectional': True, 'meta_learning': False},
    'adaptive_alignment': {'temporal_modeling': True, 'bidirectional': True, 'meta_learning': True}
}

# Visualization settings
FIG_SIZE = (10, 6)
DPI = 100
