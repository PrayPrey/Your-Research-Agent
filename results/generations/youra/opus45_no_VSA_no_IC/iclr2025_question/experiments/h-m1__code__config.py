"""Configuration for h-m1 cross-dataset transfer experiment."""

import os

SEED = 42

MODEL_ID = "meta-llama/Meta-Llama-3-8B-Instruct"
N_LAYERS = 32
HIDDEN_DIM = 4096

TRAIN_DATASET = "trivia_qa"
TRAIN_N_SAMPLES = 50  # ponytail: minimal for PoC; 500+ for Phase 5
EVAL_DATASET = "truthful_qa"

NLI_MODEL_ID = "MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli-ling-wanli"

N_SAMPLES = 5
TEMPERATURE = 1.0
LAYER_IDX = -1
ABLATION_LAYERS = list(range(20, 32))

PROBE_SOLVER = "lbfgs"
PROBE_MAX_ITER = 1000
PROBE_C = 1.0

TORCH_DTYPE = "float16"
DEVICE_MAP = "auto"

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(BASE_DIR, "results")
FIGURES_DIR = os.path.join(BASE_DIR, "figures")

AUROC_PASS_THRESHOLD = 0.70
AUROC_FAIL_THRESHOLD = 0.60
