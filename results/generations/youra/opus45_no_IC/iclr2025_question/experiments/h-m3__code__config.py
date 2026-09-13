"""Configuration for H-M3: Within-cluster threshold transfer experiment."""

import os

SEED = 42
BENCHMARKS = ["trivia_qa", "squad", "pop_qa"]
CLUSTER_1 = ["trivia_qa", "squad"]
CLUSTER_2 = ["pop_qa"]
WITHIN_CLUSTER_PAIRS = [
    ("trivia_qa", "squad"),
]

SAMPLE_SIZE = 100  # Reduced for PoC; full run uses 1000
CALIB_SPLIT = 0.7
TARGET_FPR = 0.1

GEN_MODEL = "meta-llama/Llama-2-7b-hf"
NLI_MODEL = "microsoft/deberta-v3-large"
N_GENERATIONS = 10
TEMPERATURE = 1.0
MAX_NEW_TOKENS = 64

NLI_BATCH_SIZE = 32
ENTAILMENT_THRESHOLD = 0.5
F1_THRESHOLD = 0.3
DATASET_SUBSET = "rc"

DEGRADATION_THRESHOLD = 0.08
CI_UPPER_THRESHOLD = 0.12
N_BOOTSTRAP = 1000

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")
FIGURES_DIR = os.path.join(BASE_DIR, "figures")

os.makedirs(OUTPUTS_DIR, exist_ok=True)
os.makedirs(FIGURES_DIR, exist_ok=True)
