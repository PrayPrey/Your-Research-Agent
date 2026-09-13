"""Experiment configuration for H-M2: Sample Efficiency Learning Curve."""
import os

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_H_M2_DIR = os.path.dirname(_THIS_DIR)
_YOURA_DIR = os.path.dirname(_H_M2_DIR)  # docs/youra_research/

H_E1_CODE_DIR = os.path.join(_YOURA_DIR, "h-e1", "code")
H_M1_CODE_DIR = os.path.join(_YOURA_DIR, "h-m1", "code")
H_E1_RESULTS_DIR = os.path.join(_YOURA_DIR, "h-e1", "results")
H_E1_RESULTS_JSON = os.path.join(H_E1_RESULTS_DIR, "results.json")

MZDATASET_CODE_PATH = "/home/PrayPrey/YOURA_camera_ready/YouRA/results/generations/youra/opus45_no_IC/iclr2025_wsl/docs/youra_research/h-m4/data/ModelZooDataset/code"

ZOO_PATHS = {
    "cifar10": "/home/PrayPrey/.cache/model_zoos/cifar10/dataset_cifar_small_hyp_fix.pt",
}

FIGURES_DIR = os.path.join(_H_M2_DIR, "figures")
RESULTS_DIR = os.path.join(_H_M2_DIR, "results")

SEED = 42
EPOCHS = 100
BATCH_SIZE = 64
BATCH_SIZE_SMALL = 16
SMALL_SIZE_THRESHOLD = 250
LR = 1e-3
WEIGHT_DECAY = 1e-4

TRAINING_SIZES = [100, 250, 500, 1000, "full"]
# H-E1 didn't store gnn_nfn "full" — we use N=1000 as last available point
# The efficiency ratio uses only sizes present in results, so this is safe
SEEDS = [0, 1, 2, 3, 4]
ZOO_NAMES = ["cifar10"]
ENCODER_NAMES = ["flat_mlp", "flat_mlp_perm_aug", "gnn_nfn"]

ZOO_ARCH = "cnn"
GNN_HIDDEN_DIM = 64
GNN_NUM_LAYERS = 4

PEAK_FRACTION = 0.90
EFFICIENCY_GATE = 2.0
N_BOOT = 1000
CI_LEVEL = 0.95

BUDGET_TIERS = {"small": 50_000, "medium": 200_000, "large": 1_000_000}
PRIMARY_TIER = "medium"
PRIMARY_BUDGET = BUDGET_TIERS[PRIMARY_TIER]
