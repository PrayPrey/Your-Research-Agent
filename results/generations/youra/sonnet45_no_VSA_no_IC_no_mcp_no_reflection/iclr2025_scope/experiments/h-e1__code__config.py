# Configuration: H-E1
# Mamba-130M checkpoint validation

CHECKPOINT_NAME = "state-spaces/mamba-130m-hf"
GLUE_TASKS = ["mnli", "qqp", "sst2"]
BATCH_SIZE = 16
MAX_LENGTH = 512
DEVICE = "cuda"
DTYPE = "float16"
MEMORY_LIMIT_GB = 16.0
RANDOM_SEED = 42
OUTPUT_DIR = None
FIGURES_DIR = None
