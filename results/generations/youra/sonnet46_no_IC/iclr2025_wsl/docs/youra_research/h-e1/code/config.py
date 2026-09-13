import os

# Model
HIDDEN_DIM   = 256
LATENT_DIM   = 128
NUM_LAYERS   = 4

# Training
LR           = 1e-3
WEIGHT_DECAY = 1e-4
BETAS        = (0.9, 0.999)
BATCH_SIZE   = 64
EPOCHS       = 100

# Scheduler
T_MAX        = 100
ETA_MIN      = 1e-5

# SSL Objective
TEMPERATURE  = 0.07
LAMBDA_SWEEP = [0.01, 0.1, 1.0, 10.0]
SEEDS        = [0, 1, 2, 3, 4]

# Data
VAL_FRACTION = 0.1

# Evaluation
N_MMD_KERNELS  = 5
MMD_RATIO_PASS = 2.0
MMD_RATIO_STOP = 1.5

# Paths
DATA_ROOT      = os.environ.get('DATA_ROOT', './data')
CHECKPOINT_DIR = os.environ.get('CHECKPOINT_DIR', 'checkpoints/h-e1/')
RESULTS_DIR    = 'docs/youra_research/h-e1/'
FIGURES_DIR    = 'docs/youra_research/h-e1/figures/'
