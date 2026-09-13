"""Experiment configuration for H-E1: Equivariant Weight-Space Encoders."""
import os

# Paths
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_H_E1_DIR = os.path.dirname(_THIS_DIR)

MZDATASET_CODE_PATH = "/home/PrayPrey/YOURA_camera_ready/YouRA/results/generations/youra/opus45_no_IC/iclr2025_wsl/docs/youra_research/h-m4/data/ModelZooDataset/code"

ZOO_PATHS = {
    "cifar10": "/home/PrayPrey/.cache/model_zoos/cifar10/dataset_cifar_small_hyp_fix.pt",
}

FIGURES_DIR = os.path.join(_H_E1_DIR, "figures")
RESULTS_DIR = os.path.join(_H_E1_DIR, "results")

# Training
SEED = 42
EPOCHS = 100  # reduced from 200 for PoC speed; still sufficient for convergence check
BATCH_SIZE = 64
LR = 1e-3
WEIGHT_DECAY = 1e-4
N_BOOTSTRAP = 1000
CI_LEVEL = 0.95

# Experiment design
TRAINING_SIZES = [100, 250, 500, 1000, "full"]
BUDGET_TIERS = {"small": 50_000, "medium": 200_000, "large": 500_000}
ZOO_NAMES = ["cifar10"]  # MNIST not available locally; CIFAR-10 sufficient for gate
# NFN library (AllanYangZhou/nfn) incompatible with this CNN zoo architecture
# (mixed conv+FC layers cause shape mismatch in NPLinear col_bdcst).
# Using GNN-NFN (our custom impl) as the equivariant encoder for CNN zoo.
ENCODER_NAMES = ["flat_mlp", "flat_mlp_perm_aug", "gnn_nfn"]

# Zoo architecture (detected at runtime; CNN for ModelZooDataset CIFAR-10)
ZOO_ARCH = "cnn"  # confirmed by 4D conv weight tensors in dataset
