"""Configuration constants for H-E1 BCS experiment."""

import os

DATASET_PRIMARY = "lmsys/lmsys-chat-1m"
DATASET_SECONDARY = "Anthropic/hh-rlhf"
MIN_TURNS = 4
SPACY_MODEL = "en_core_web_sm"
BCS_SD_TARGET = 0.15
N_TARGET = 10000
BATCH_SIZE = 100
SEED = 42

FK_GRADE_MAX = 20
SENT_LEN_MAX = 50
DEP_DIST_MAX = 5

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "results")
FIGURES_DIR = os.path.join(BASE_DIR, "figures")
RESULTS_JSON = os.path.join(OUTPUT_DIR, "bcs_stats.json")
CHECKPOINT_PATH = os.path.join(OUTPUT_DIR, "bcs_checkpoint.pkl")

N_WORKERS = 8
CHECKPOINT_EVERY = 5000

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(FIGURES_DIR, exist_ok=True)
