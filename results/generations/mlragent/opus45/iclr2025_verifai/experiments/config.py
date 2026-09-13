"""Configuration for SpecBridge experiment."""
import os
import torch

# Model configurations - Using local HuggingFace models
# Using Qwen2.5-Coder-1.5B for both specification inference and code generation
MODEL_NAME = "Qwen/Qwen2.5-Coder-1.5B-Instruct"

# Device configuration
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
GPU_ID = 0  # Use first available GPU

# Experiment parameters
NUM_SAMPLES = 30  # Number of problems to evaluate
NUM_SPEC_CANDIDATES = 3  # K - number of specification candidates
ENSEMBLE_THRESHOLD = 0.5  # theta_D - disagreement threshold
MAX_REFINEMENT_ITERATIONS = 3  # Maximum refinement attempts
TEMPERATURE_SAMPLING = 0.7  # Temperature for diverse generation

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(BASE_DIR, "outputs")
LOG_FILE = os.path.join(BASE_DIR, "log.txt")
