"""H-M1 Configuration: KS test for category-specific confidence distributions."""

import torch
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "h-e1" / "code"))
from config import (
    SEED, MODEL_ID, DTYPE, DEVICE_MAP, DATASET_ID, DATASET_CONFIG,
    DATASET_SPLIT, BATCH_SIZE, CATEGORY_TO_CLUSTER, CLUSTER_NAMES
)

# KS test parameters
ALPHA = 0.05
N_CLUSTERS = 7
MIN_CLUSTER_SIZE = 100
MAJORITY_PAIRS_REQUIRED = 11  # of 21 total pairs (C(7,2))

# Output paths
RESULTS_JSON = "outputs/results.json"
VALIDATION_MD = "../04_validation.md"
FIGURES_DIR = "figures/"
