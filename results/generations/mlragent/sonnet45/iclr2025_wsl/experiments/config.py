"""
Configuration file for the weight fingerprinting experiment.
"""

import torch

# General settings
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
SEED = 42

# Data generation settings
NUM_BASE_MODELS = 20  # Reduced for faster experiments
NUM_SYMMETRY_VARIANTS = 4  # Number of symmetry variants per base model
NUM_BACKDOOR_MODELS = 10  # Reduced for faster experiments

# Model architectures to use
ARCHITECTURES = ['mlp']  # Use only MLP for faster experiments
INPUT_DIMS = [28*28]  # MNIST
HIDDEN_DIMS = [64]  # Reduced size
NUM_CLASSES = 10

# GNN fingerprinting settings
GNN_HIDDEN_DIM = 64  # Reduced for faster training
GNN_NUM_LAYERS = 2  # Reduced for faster training
GNN_EMBEDDING_DIM = 64  # Reduced for faster training
GNN_POOLING = 'attention'  # 'mean', 'max', 'sum', 'attention'

# Training settings
BATCH_SIZE = 16
LEARNING_RATE = 1e-3  # Increased for faster convergence
NUM_EPOCHS = 10  # Reduced for faster experiments
WEIGHT_DECAY = 1e-5
TRIPLET_MARGIN = 0.5
TEMPERATURE = 0.1
LAMBDA_SUP = 0.5

# Evaluation settings
TOP_K_VALUES = [1, 5, 10]
FPR_THRESHOLD = 0.01

# Baseline settings
PCA_COMPONENTS = 128
STAT_FEATURES = ['mean', 'std', 'min', 'max', 'skew', 'kurtosis']

# Paths
DATA_DIR = 'data'
RESULTS_DIR = 'results'
CHECKPOINTS_DIR = 'checkpoints'
