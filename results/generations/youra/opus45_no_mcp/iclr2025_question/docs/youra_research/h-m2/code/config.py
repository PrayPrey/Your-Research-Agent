"""H-M2 Configuration: Semantic Consistency as Hallucination Predictor"""
import os

MODEL_NAME = "meta-llama/Llama-2-7b-chat-hf"
TORCH_DTYPE = "float16"
DEVICE_MAP = "auto"
HF_TOKEN = os.environ.get("HF_TOKEN", "")

TEMPERATURE = 0.7
TOP_P = 0.9
MAX_NEW_TOKENS = 128
NUM_RESPONSES = 10

DATASET_NAME = "trivia_qa"
DATASET_CONFIG = "rc.nocontext"
DATASET_SPLIT = "validation"
N_QUESTIONS = 20  # PoC scale for Phase 4 validation

# Embedding model for semantic consistency (NEW for H-M2)
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

AUROC_TARGET = 0.55
P_VALUE_TARGET = 0.05

CHECKPOINT_PATH = "results/checkpoint.json"
CHECKPOINT_EVERY = 50
OUTPUT_PATH = "results/h-m2_results.json"
FIGURES_DIR = "figures/"

SEED = 42
