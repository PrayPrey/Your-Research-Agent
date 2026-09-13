"""Configuration constants for H-M3 Brier decomposition experiment.

Adapted for margin-based analysis using actual H-E1 cache data structure
(margins + correctness arrays instead of full logits).
"""
from pathlib import Path

# Reproducibility
SEED: int = 42

# Bootstrap parameters
BOOTSTRAP_N: int = 1000

# Brier decomposition parameters
N_BINS: int = 15

# Decomposition verification tolerance (relaxed for binning numerical effects)
DECOMP_TOLERANCE: float = 5e-3

# Model families
FAMILIES: list[str] = ["qwen", "mistral"]

# Gate configuration
GATE_TYPE: str = "SHOULD_WORK"
P_VALUE_THRESHOLD: float = 0.05

# Data validation
EXPECTED_N: int = 14042
N_CLASSES: int = 4

# Path resolution
CODE_DIR: Path = Path(__file__).parent
HYPOTHESIS_DIR: Path = CODE_DIR.parent
H_E1_CACHE_DIR: Path = HYPOTHESIS_DIR.parent / "h-e1" / "cache"
FIGURES_DIR: Path = HYPOTHESIS_DIR / "figures"
RESULTS_YAML: Path = HYPOTHESIS_DIR / "experiment_results.yaml"
VALIDATION_MD: Path = HYPOTHESIS_DIR / "04_validation.md"

# Cache file mapping (actual H-E1 structure with per-family subdirectories)
# Format: {family}/{model_id}_{metric}.npy
CACHE_FILE_PATTERNS = {
    "qwen": {
        "base_margins": "qwen/Qwen_Qwen2.5-7B_margins.npy",
        "base_correctness": "qwen/Qwen_Qwen2.5-7B_correctness.npy",
        "inst_margins": "qwen/Qwen_Qwen2.5-7B-Instruct_margins.npy",
        "inst_correctness": "qwen/Qwen_Qwen2.5-7B-Instruct_correctness.npy",
    },
    "mistral": {
        "base_margins": "mistral/mistralai_Mistral-7B-v0.1_margins.npy",
        "base_correctness": "mistral/mistralai_Mistral-7B-v0.1_correctness.npy",
        "inst_margins": "mistral/mistralai_Mistral-7B-Instruct-v0.2_margins.npy",
        "inst_correctness": "mistral/mistralai_Mistral-7B-Instruct-v0.2_correctness.npy",
    },
}


def ensure_directories() -> None:
    """Create output directories if they don't exist."""
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
