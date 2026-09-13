import os
import torch

H_E3_CODE = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../h-e3/code")
)

# Paths — resolved relative to repo root (run from TEST_scsl/)
DATA_ROOT = "/home/PrayPrey/data/waterbirds_v1.0/waterbirds_v1.0/"
CKPT_DIR = "docs/youra_research/h-e3/results/checkpoints/"
RESULTS_PATH = "docs/youra_research/h-m1/results/confidence_results.json"
FIGURES_DIR = "docs/youra_research/h-m1/figures"

# Evaluation schedule (same as H-E3 training checkpoints)
CHECKPOINT_EPOCHS = [0, 1, 5, 10, 20, 50]
SEEDS = [1, 2, 3, 4, 5]
# t* per seed from H-E3 04_validation.md (argmax AUROC)
TSTAR_PER_SEED = {1: 20, 2: 50, 3: 50, 4: 20, 5: 5}

BATCH_SIZE = 256
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]
MINORITY_GROUPS = (1, 2)  # H-M1 definition (overrides H-E3's (1,3))
MAJORITY_GROUPS = (0, 3)

# Gate thresholds
GATE_P_MIN_LOW = 0.3
GATE_P_MIN_HIGH = 0.7
GATE_P_MAJ = 0.80
GATE_N_SEEDS = 4  # ≥4/5 seeds must pass

# Visualization constants
VIZ = {
    "minority_color": "#d62728",
    "majority_color": "#1f77b4",
    "gate_low_color": "#888888",
    "gate_high_color": "#888888",
    "gate_maj_color": "#2ca02c",
    "threshold_linestyle": "--",
    "threshold_linewidth": 1.5,
    "fig_width": 8,
    "fig_height": 5,
    "dpi": 150,
    "format": "png",
}


def ckpt_path(seed: int, epoch: int) -> str:
    return os.path.join(CKPT_DIR, f"ckpt_seed{seed}_epoch{epoch}.pt")


def ensure_dirs() -> None:
    os.makedirs(FIGURES_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(RESULTS_PATH), exist_ok=True)
