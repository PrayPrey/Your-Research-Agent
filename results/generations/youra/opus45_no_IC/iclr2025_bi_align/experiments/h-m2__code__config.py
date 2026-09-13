"""Configuration for H-M2 formality correlation experiment."""

import os
from dataclasses import dataclass

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
H_M1_DIR = os.path.join(os.path.dirname(BASE_DIR), "h-m1")

SEED = 42
DATASET_NAME = "Anthropic/hh-rlhf"
MIN_TURNS = 4
MIN_MSG_LEN = 5
MODEL_NAME = "s-nlp/deberta-large-formality-ranker"
MAX_SEQ_LEN = 512
BATCH_SIZE = 32
N_PERMUTATIONS = 1000
GATE_R_THRESHOLD = 0.1
GATE_P_THRESHOLD = 0.001
MIN_SAMPLE_SIZE = 10000

OUTPUT_DIR = os.path.join(BASE_DIR, "results")
FIGURES_DIR = os.path.join(BASE_DIR, "figures")
RESULTS_PATH = os.path.join(OUTPUT_DIR, "formality_correlation.pkl")

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(FIGURES_DIR, exist_ok=True)


@dataclass
class ExperimentConfig:
    seed: int = SEED
    dataset_name: str = DATASET_NAME
    min_turns: int = MIN_TURNS
    min_msg_len: int = MIN_MSG_LEN
    results_dir: str = OUTPUT_DIR
    figures_dir: str = FIGURES_DIR
    results_path: str = RESULTS_PATH


@dataclass
class FormalityScorerConfig:
    model_name: str = MODEL_NAME
    max_seq_len: int = MAX_SEQ_LEN
    batch_size: int = BATCH_SIZE


@dataclass
class CorrelationConfig:
    gate_r_threshold: float = GATE_R_THRESHOLD
    gate_p_threshold: float = GATE_P_THRESHOLD
    min_sample_size: int = MIN_SAMPLE_SIZE


@dataclass
class BaselineConfig:
    n_permutations: int = N_PERMUTATIONS
    random_seed: int = SEED


@dataclass
class AblationConfig:
    turn_position: int = 2
    low_q: float = 0.25
    high_q: float = 0.75


@dataclass
class OutputConfig:
    figure_dpi: int = 150
    figure_format: str = "png"
    figures: tuple = (
        "scatter_regression.png",
        "correlation_bar.png",
        "hexbin_density.png",
        "qq_plot.png",
        "residual_plot.png",
    )
