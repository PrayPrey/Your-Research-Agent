"""Configuration for H-M1 lagged correlation experiment."""

import os
from dataclasses import dataclass, field

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
H_E1_DIR = os.path.join(os.path.dirname(BASE_DIR), "h-e1")

SEED = 42
N_WORKERS = 8

BCS_CHECKPOINT_PATH = os.path.join(H_E1_DIR, "results", "bcs_checkpoint.pkl")
DATASET_FALLBACK = "Anthropic/hh-rlhf"
MIN_ALIGNED_TURNS = 4
MAX_LAG = 3
N_PERMUTATIONS = 1000
LENGTH_BINS = {"short": (4, 6), "medium": (7, 10), "long": (11, None)}

OUTPUT_DIR = os.path.join(BASE_DIR, "results")
FIGURES_DIR = os.path.join(BASE_DIR, "figures")
RESULTS_PATH = os.path.join(OUTPUT_DIR, "lag_analysis.pkl")

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(FIGURES_DIR, exist_ok=True)


@dataclass
class ExperimentConfig:
    seed: int = 42
    n_workers: int = 8
    bcs_checkpoint_path: str = BCS_CHECKPOINT_PATH
    dataset_fallback: str = DATASET_FALLBACK
    results_dir: str = OUTPUT_DIR
    figures_dir: str = FIGURES_DIR
    results_path: str = RESULTS_PATH


@dataclass
class LagAnalysisConfig:
    max_lag: int = 3
    min_turns: int = 4
    min_valid_len: int = 3
    primary_lag: int = 1
    significance_threshold: float = 0.05


@dataclass
class BaselineConfig:
    n_permutations: int = 1000
    random_seed: int = 42
    null_p_threshold: float = 0.10


@dataclass
class LengthStratConfig:
    bins: dict = field(default_factory=lambda: {
        "short": (4, 6),
        "medium": (7, 10),
        "long": (11, None),
    })


@dataclass
class OutputConfig:
    checkpoint_path: str = RESULTS_PATH
    figure_dpi: int = 150
    figure_format: str = "png"
    figures: tuple = (
        "lag_profile.png",
        "gate_pvalue.png",
        "lag1_histogram.png",
        "length_scatter.png",
        "shuffled_vs_real.png",
        "length_heatmap.png",
    )
