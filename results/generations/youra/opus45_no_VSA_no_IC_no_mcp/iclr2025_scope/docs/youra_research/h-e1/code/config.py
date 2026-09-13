"""H-E1 Configuration: Fixed constants for PoC."""

MODEL_NAME = "bert-base-uncased"
SUPERGLUE_TASKS = ["boolq", "cb", "copa", "wic", "wsc"]
MAX_SAMPLES_PER_TASK = 200
MAX_SEQ_LEN = 128
N_CLUSTERS = 8
RANDOM_SEED = 42
OUTPUT_DIR = "h-e1/results/"
FIGURES_DIR = "h-e1/figures/"
