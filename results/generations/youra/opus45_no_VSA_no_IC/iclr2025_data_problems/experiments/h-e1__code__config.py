"""Configuration for h-e1 experiment: Attribution Method Distinctness."""

SEED = 42
BATCH_SIZE = 128
EVAL_BATCH_SIZE = 256
NUM_WORKERS = 4
NUM_CLASSES = 10

# Training (if needed)
EPOCHS = 10  # ponytail: CPU-only PoC, enough for feature extraction
LR = 0.1
MOMENTUM = 0.9
WEIGHT_DECAY = 5e-4
CHECKPOINT_EPOCHS = [5, 10]  # 2 checkpoints for CPU tractability

# Attribution
TRAIN_SUBSET_SIZE = 500  # ponytail: CPU PoC, scale to full 50K on GPU
EVAL_SUBSET_SIZE = 500  # Test samples for pairwise scoring
PROJECTION_DIM = 2048  # TRAK
CORR_THRESHOLD = 0.9  # Distinctness gate

# CIFAR-10 normalization
NORMALIZE_MEAN = (0.4914, 0.4822, 0.4465)
NORMALIZE_STD = (0.2470, 0.2435, 0.2616)

# Paths
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
CHECKPOINT_DIR = os.path.join(BASE_DIR, "checkpoints")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
FIGURES_DIR = os.path.join(BASE_DIR, "figures")
