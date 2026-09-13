# config.py - h-m1 semantic entropy configuration
SEED = 42

# LLM
MODEL_ID = "meta-llama/Meta-Llama-3-8B-Instruct"
DTYPE = "bfloat16"
DEVICE_MAP = "auto"
MAX_NEW_TOKENS = 128

# Multi-sample generation for semantic entropy
NUM_SAMPLES = 10
TEMPERATURE = 0.7

# NLI model for bidirectional entailment clustering
NLI_MODEL_ID = "facebook/bart-large-mnli"
NLI_MAX_LENGTH = 256
ENTAILMENT_THRESHOLD = 0.7

# Gate
AUROC_GATE = 0.70

# Dataset
DATASET_NAME = "truthful_qa"
DATASET_CONFIG = "multiple_choice"
CACHE_DIR = "../../h-e1/code/.cache"

# Baseline references from h-e1 validated run
BASELINE_SCORES_CSV = "../../h-e1/code/outputs/scores_mc.csv"
BASELINE_METRICS_JSON = "../../h-e1/code/outputs/metrics_mc.json"

# Output
RESULTS_DIR = "results"
FIGURES_DIR = "../figures"
