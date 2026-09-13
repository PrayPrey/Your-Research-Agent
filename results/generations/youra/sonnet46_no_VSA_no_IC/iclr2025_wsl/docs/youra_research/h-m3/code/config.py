"""Configuration for H-M3: PermAug partial equivariance benefit."""
import os

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_H_M3_DIR = os.path.dirname(_THIS_DIR)
_YOURA_DIR = os.path.dirname(_H_M3_DIR)

# Sibling hypothesis code dirs
H_E1_CODE_DIR = os.path.join(_YOURA_DIR, "h-e1", "code")
H_M1_CODE_DIR = os.path.join(_YOURA_DIR, "h-m1", "code")
H_M2_CODE_DIR = os.path.join(_YOURA_DIR, "h-m2", "code")

# Results from completed hypotheses
H_E1_RESULTS_JSON = os.path.join(_YOURA_DIR, "h-e1", "results", "results.json")
H_M2_RESULTS_JSON = os.path.join(_YOURA_DIR, "h-m2", "results", "learning_curve_results.json")

MZDATASET_CODE_PATH = "/home/PrayPrey/YOURA_camera_ready/YouRA/results/generations/youra/opus45_no_IC/iclr2025_wsl/docs/youra_research/h-m4/data/ModelZooDataset/code"

ZOO_PATHS = {
    "cifar10": "/home/PrayPrey/.cache/model_zoos/cifar10/dataset_cifar_small_hyp_fix.pt",
}

FIGURES_DIR = os.path.join(_H_M3_DIR, "figures")
RESULTS_DIR = os.path.join(_H_M3_DIR, "results")

# Training hyperparameters (match H-E1/H-M2)
SEED = 42
EPOCHS = 100
BATCH_SIZE = 64
BATCH_SIZE_SMALL = 16
SMALL_SIZE_THRESHOLD = 250
LR = 1e-3
WEIGHT_DECAY = 1e-4

# Analysis
N_BOOT = 1000
CI_LEVEL = 0.95

# Experiment scope
TRAINING_SIZES = [100, 250, 500, 1000]
ZOO_NAMES = ["cifar10"]
NUM_PERMUTATIONS = 10
ZOO_ARCH = "cnn"

# FlatMLP architecture — permutation is applied to THESE hidden layers
FLATMLP_HIDDEN = [256, 128]
# layer_sizes = [input_dim] + FLATMLP_HIDDEN + [1] constructed at runtime

GNN_HIDDEN_DIM = 64
GNN_NUM_LAYERS = 4
