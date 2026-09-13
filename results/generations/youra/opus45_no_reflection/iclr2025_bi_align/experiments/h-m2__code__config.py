"""H-M2 inference comparison configuration."""
import os

SEED: int = 42
BASELINE_MODEL: str = "mistralai/Mistral-7B-Instruct-v0.2"
BIDPO_MODEL_BASE: str = "mistralai/Mistral-7B-Instruct-v0.2"
BIDPO_CHECKPOINT_PATH: str = "../../h-m1/code/outputs/final.pt"

DTYPE: str = "bfloat16"
DEVICE_MAP: str = "auto"

N_PROMPTS: int = 500
MAX_PROMPT_LENGTH: int = 768
MAX_NEW_TOKENS: int = 256
TEMPERATURE: float = 0.7
TOP_P: float = 0.9
DO_SAMPLE: bool = True

ALPHA_ONE_SIDED: float = 0.05
COHENS_D_THRESHOLD: float = 0.2

OUTPUT_DIR: str = "outputs/"
FIGURES_DIR: str = "figures/"
RESULTS_PATH: str = "outputs/results.json"


def ensure_dirs() -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(FIGURES_DIR, exist_ok=True)
