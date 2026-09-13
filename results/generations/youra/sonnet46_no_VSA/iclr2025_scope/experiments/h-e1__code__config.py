"""H-E1 experiment configuration. All hyperparameters in one place."""
import os
from pathlib import Path

# Paths (relative to code/ directory)
CODE_DIR = Path(__file__).parent
HYPOTHESIS_DIR = CODE_DIR.parent
REPOS_DIR = HYPOTHESIS_DIR / "repos"
CHECKPOINTS_DIR = HYPOTHESIS_DIR / "checkpoints"
RESULTS_DIR = HYPOTHESIS_DIR / "results"
FIGURES_DIR = HYPOTHESIS_DIR / "figures"

MOHAWK_REPO = str(REPOS_DIR / "mohawk")
LAWCAT_REPO = str(REPOS_DIR / "LAWCAT")
LONGBENCH_REPO = str(REPOS_DIR / "LongBench")

# Teacher model
TEACHER_MODEL = "meta-llama/Llama-3.1-8B"

# Datasets
C4_DATASET = ("allenai/c4", "en")
LONGBENCH_DATASET = ("THUDM/LongBench", "v2")

# MOHAWK stage configuration (≤1B token budget)
MOHAWK_STAGE_TOKENS = {
    "stage1": 26_000_000,    # matrix orientation
    "stage2": 52_000_000,    # hidden-state alignment
    "stage3": 920_000_000,   # end-to-end KD
}
MOHAWK_LR = {"stage1": 1e-3, "stage2": 5e-4, "stage3": 1e-4}
MOHAWK_BATCH = {"stage1": 8, "stage2": 8, "stage3": 32}
MOHAWK_SEQ_LEN = 2048
MOHAWK_SEED = 42

# LAWCAT configuration
LAWCAT_SEQ_LEN = 1024
LAWCAT_PHASE1_TOKENS = 50_000_000
LAWCAT_PHASE2_TOKENS = 950_000_000
LAWCAT_PHASE1_LR = 1e-2
LAWCAT_PHASE1_MSE_WEIGHT = 1000.0
LAWCAT_LORA_R = 16
LAWCAT_LORA_ALPHA = 32
LAWCAT_LORA_LR = 1e-4
LAWCAT_SEED = 0

# Hybrid-4: retain attention at layers 14-17
HYBRID4_KEPT_LAYERS = list(range(14, 18))  # [14, 15, 16, 17]
HYBRID4_STAGE3_TOKENS = 200_000_000

# Gate thresholds
PPL_GATE_MAX_RELATIVE_GAP = 0.05   # student PPL ≤ teacher * 1.05
L2_GATE_MAX_RATIO = 0.15            # hidden-state L2 ratio
STAGE1_FROBENIUS_MAX = 0.15         # avg Frobenius loss
ABORT_ON_GATE_FAIL = True

# LongBench v2 task categories
CATEGORIES = [
    "single_doc_qa",
    "multi_doc_qa",
    "long_in_context_learning",
    "long_dialogue",
    "code_repo",
    "long_structured_data",
]
RETRIEVAL_HEAVY = {"multi_doc_qa", "long_structured_data"}
GENERATION_HEAVY = {"long_in_context_learning"}

# LLaMA-3-8B architecture constants
D_MODEL = 4096
N_LAYERS = 32
N_HEADS = 32
N_KV_HEADS = 8
D_FF = 14336

# Number of GPUs (H100 NVL cluster)
N_GPUS = int(os.environ.get("WORLD_SIZE", 4))
MASTER_PORT = int(os.environ.get("MASTER_PORT", 29500))

# Cache — use the system HF cache which has pre-downloaded models
HF_CACHE = os.path.expanduser("~/.cache/huggingface")
os.environ.setdefault("HF_HOME", HF_CACHE)
os.environ.setdefault("HF_DATASETS_CACHE", str(Path(HF_CACHE) / "datasets"))
