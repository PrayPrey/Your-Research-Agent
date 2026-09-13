"""
Configuration for SECACE experiments.
"""

import os

# Model configuration
MODEL_NAME = "gpt-4o-mini"  # Use GPT-4o-mini for experiments
TEMPERATURE = 0.7
MAX_TOKENS = 2048

# API keys (from environment variables)
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")

# Experiment settings
NUM_TASKS = 20  # Number of programming tasks to evaluate
MAX_ATTEMPTS = 5  # Maximum number of fix attempts per task
TIMEOUT = 30  # Timeout for code execution in seconds

# Training hyperparameters (for simulation)
LAMBDA_1 = 1.0  # DPO loss weight
LAMBDA_2 = 0.5  # Location-aware loss weight
LAMBDA_3 = 0.3  # Contrastive loss weight
ALPHA = 2.0  # Location weight multiplier
BETA = 0.1  # DPO divergence control
TAU = 0.07  # Temperature for contrastive learning

# Counterfactual generation strategies
MUTATION_OPERATORS = [
    "condition_flip",
    "boundary_adjustment",
    "api_substitution",
    "type_conversion"
]

# Paths
DATA_DIR = "data"
RESULTS_DIR = "results"
FIGURES_DIR = "results/figures"

# Random seed
RANDOM_SEED = 42
