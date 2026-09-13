import os
from dataclasses import dataclass

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SEED = 42
DATASET_NAME = "Anthropic/hh-rlhf"
MIN_TURNS = 2
MODEL_NAME = "s-nlp/deberta-large-formality-ranker"
MAX_SEQ_LEN = 512
BATCH_SIZE = 64
N_BOOT = 2000
ALPHA = 0.05
MIN_SAMPLE_SIZE = 10000

OUTPUT_DIR = os.path.join(BASE_DIR, "code", "outputs")
FIGURES_DIR = os.path.join(BASE_DIR, "figures")
CACHE_DIR = os.path.join(BASE_DIR, "cache")
RESULTS_PATH = os.path.join(BASE_DIR, "results.json")

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(FIGURES_DIR, exist_ok=True)
os.makedirs(CACHE_DIR, exist_ok=True)


@dataclass
class ExperimentConfig:
    seed: int = SEED
    dataset_name: str = DATASET_NAME
    min_turns: int = MIN_TURNS
    n_boot: int = N_BOOT
    alpha: float = ALPHA
    min_sample_size: int = MIN_SAMPLE_SIZE
    figures_dir: str = FIGURES_DIR
    cache_dir: str = CACHE_DIR
    results_path: str = RESULTS_PATH


@dataclass
class FormalityScorerConfig:
    model_name: str = MODEL_NAME
    max_seq_len: int = MAX_SEQ_LEN
    batch_size: int = BATCH_SIZE
