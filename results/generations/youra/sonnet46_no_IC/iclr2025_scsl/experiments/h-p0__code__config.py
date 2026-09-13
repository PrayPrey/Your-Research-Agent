"""H-P0 experiment constants."""
import os
import torch

# Dataset
WILDS_CACHE = "/home/PrayPrey/.wilds_cache"
HF_REPO = "izmailovpavel/spurious_feature_learning"
SEEDS = [1, 2, 3]
N_IMAGES = 50
DATA_SEED = 42

# Local checkpoint archive (pre-cached from previous pipeline runs)
LOCAL_CHECKPOINT_ARCHIVE = "/home/PrayPrey/YouRA_no_IC_sonnet46/TEST_scsl/docs/youra_research/_archive/20260805T130336_routing_recovery/h-e1/checkpoints"

# Gate thresholds
GATE_MEAN_SIM = 0.9999
GATE_VARIANCE = 1e-6

# Device
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# Paths (relative to run location)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # h-p0/
OUTPUT_DIR = os.path.join(BASE_DIR, "results")
FIGURES_DIR = os.path.join(BASE_DIR, "figures")
CHECKPOINT_DIR = os.path.join(BASE_DIR, "code", "checkpoints")

# Checkpoint map: method -> seed -> HF filename
CHECKPOINT_MAP = {
    "erm": {1: "erm_seed1/final_checkpoint.pt", 2: "erm_seed2/final_checkpoint.pt", 3: "erm_seed3/final_checkpoint.pt"},
    "dfr": {1: "dfr_seed1/final_checkpoint.pt", 2: "dfr_seed2/final_checkpoint.pt", 3: "dfr_seed3/final_checkpoint.pt"},
}

# Expected tensor shapes
EXPECTED_SHAPES = {
    "images": (N_IMAGES, 3, 224, 224),
    "features": (N_IMAGES, 2048),
    "layer4_raw": (N_IMAGES, 2048, 7, 7),
}
