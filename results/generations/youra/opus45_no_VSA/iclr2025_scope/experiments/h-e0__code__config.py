"""Configuration constants for h-e0 linear separability experiment."""
import os

SEED = 42
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_CSV_PATH = os.path.join(BASE_DIR, "data", "flan_metadata.csv")
TEXT_COLUMN = "instruction"
LABEL_COLUMN = "task_category"

MIN_SAMPLES_PER_FAMILY = 500
MIN_FAMILIES = 10
MAX_TOKENS = 128
TEST_SIZE = 0.2

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_DIM = 384

LOGREG_PARAMS = {
    "multi_class": "multinomial",
    "solver": "lbfgs",
    "class_weight": "balanced",
    "max_iter": 1000,
    "random_state": SEED,
}

GATE_MACRO_F1 = 0.75
FIGURES_DIR = os.path.join(BASE_DIR, "figures")
OUTPUTS_DIR = os.path.join(BASE_DIR, "code", "outputs")
