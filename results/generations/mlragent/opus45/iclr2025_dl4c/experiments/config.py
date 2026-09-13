"""
Configuration for ExePlay Experiment
"""
import os

# Base paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(BASE_DIR, "outputs")

# Model configuration
MODEL_NAME = "Qwen/Qwen2.5-Coder-1.5B-Instruct"  # Small model for experiments
DEVICE = "cuda"

# EQS weights (Execution Quality Score)
EQS_WEIGHTS = {
    "test_pass_rate": 0.4,      # alpha
    "coverage": 0.2,            # beta
    "error_proximity": 0.2,     # gamma
    "behavior_similarity": 0.2  # delta
}

# Training configuration
TRAINING_CONFIG = {
    "num_iterations": 3,
    "samples_per_task": 4,  # K value
    "batch_size": 4,
    "learning_rate": 1e-5,
    "max_length": 512,
    "temperature": 0.7,
    "num_tasks": 50,  # Use subset for faster experiments
}

# DPO configuration
DPO_CONFIG = {
    "beta": 0.1,
    "lambda_margin": 0.5,  # Margin weight scaling
}

# Experiment settings
EXPERIMENT_CONFIG = {
    "seed": 42,
    "num_eval_samples": 5,
    "max_generation_length": 256,
}
