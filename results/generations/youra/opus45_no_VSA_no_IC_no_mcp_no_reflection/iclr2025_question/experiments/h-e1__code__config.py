# config.py - h-e1 EXISTENCE PoC configuration
SEED = 42

# Generation model
MODEL_ID = "meta-llama/Meta-Llama-3-8B-Instruct"
DTYPE = "bfloat16"
DEVICE_MAP = "auto"
MAX_NEW_TOKENS = 256

# Sampling for semantic entropy / SelfCheckGPT
NUM_SAMPLES = 10
SELFCHECK_K_SAMPLES = 5
TEMPERATURE = 0.7

# NLI model (semantic entropy clustering + SelfCheckNLI)
NLI_MODEL_ID = "microsoft/deberta-v3-large"
NLI_DTYPE = "float32"
NLI_MAX_LENGTH = 512

# Evaluation
AUROC_THRESHOLD = 0.55

# Dataset
DATASET_NAME = "truthful_qa"
DATASET_CONFIG = "multiple_choice"
CACHE_DIR = ".cache"

# Output
RESULTS_DIR = "outputs"
FIGURES_DIR = "../figures"
