"""Configuration for H-E1 experiment."""

import os

SEED = 42
N_CLASSES = 10
RESIDUAL_RATIO_THRESHOLD = 0.05

# Data paths
DATA_URL = "https://zenodo.org/records/6620869/files/dataset_cifar_small_hyp_rand.pt"
DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "dataset_cifar_small_hyp_rand.pt")
CIFAR_ROOT = "/home/PrayPrey/ai_scientist/Fabrication/experiments_sonnet46/2026-05-14_08-19-11_training_data_forensics_from_weights_attempt_0/0-run/process_SpawnProcess-8/data"

# Output paths
FIGURES_DIR = os.path.join(os.path.dirname(__file__), "..", "figures")
RESULTS_PATH = os.path.join(os.path.dirname(__file__), "outputs", "results.json")
OUTPUTS_DIR = os.path.join(os.path.dirname(__file__), "outputs")

# Ensure directories exist
os.makedirs(FIGURES_DIR, exist_ok=True)
os.makedirs(OUTPUTS_DIR, exist_ok=True)
