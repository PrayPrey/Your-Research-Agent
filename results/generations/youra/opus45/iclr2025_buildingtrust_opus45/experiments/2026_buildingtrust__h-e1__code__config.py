"""
Configuration for H-E1 AUROC Discriminative Degradation Analysis.

Constants, model pairs, and paths for the experiment.
"""

import torch
from pathlib import Path

# Reproducibility
SEED: int = 42

# Bootstrap CI
BOOTSTRAP_N: int = 1000

# Checkpointing
CHECKPOINT_INTERVAL: int = 500  # Save every 500 samples

# Model settings
DTYPE = torch.float16
DEVICE: str = "cuda"

# Model pairs: family -> (base_id, instruct_id)
MODEL_PAIRS: dict[str, tuple[str, str]] = {
    "qwen": ("Qwen/Qwen2.5-7B", "Qwen/Qwen2.5-7B-Instruct"),
    "llama": ("meta-llama/Llama-2-7b-hf", "meta-llama/Llama-2-7b-chat-hf"),
    "mistral": ("mistralai/Mistral-7B-v0.1", "mistralai/Mistral-7B-Instruct-v0.2"),
}

# Paths (relative to code directory)
CODE_DIR = Path(__file__).parent
HYPOTHESIS_DIR = CODE_DIR.parent
RESULTS_DIR = HYPOTHESIS_DIR / "results"
FIGURES_DIR = HYPOTHESIS_DIR / "figures"
CACHE_DIR = HYPOTHESIS_DIR / "cache"
OUTPUTS_DIR = CODE_DIR / "outputs"

# Dataset
DATASET_NAME: str = "cais/mmlu"
DATASET_CONFIG: str = "all"
DATASET_SPLIT: str = "test"

# Prompt template
PROMPT_TEMPLATE: str = (
    "Question: {question}\n"
    "A. {a}\nB. {b}\nC. {c}\nD. {d}\nAnswer:"
)

# Choice labels
CHOICE_LABELS: tuple[str, str, str, str] = ("A", "B", "C", "D")

# Inference settings
TEMPERATURE: float = 0.0  # Greedy decoding
MAX_NEW_TOKENS: int = 1

# Gate configuration
GATE_TYPE: str = "MUST_WORK"


def ensure_directories() -> None:
    """Create all output directories if they don't exist."""
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
