"""Configuration for H-M4 SNR comparison experiment."""
import sys
import os
from dataclasses import dataclass, field

H_M3_CODE = os.path.join(os.path.dirname(__file__), '../../h-m3/code')
sys.path.insert(0, H_M3_CODE)

from h_m3_config import SEED, MODEL_NAME, U_LINE_ERRORS, U_IGNORE_ERRORS

N_SAMPLES = 200  # ponytail: 100 per category for PoC speed, scale up for full validation


@dataclass
class BootstrapConfig:
    n_bootstrap: int = 500  # ponytail: reduced for PoC
    confidence_level: float = 0.95
    seed: int = SEED


@dataclass
class PermutationConfig:
    n_permutation: int = 4999  # ponytail: reduced for PoC
    significance_threshold: float = 0.05


@dataclass
class VizConfig:
    style: str = "seaborn-v0_8-whitegrid"
    dpi: int = 150
    snr_comparison_path: str = "figures/snr_comparison.png"
    bootstrap_dist_path: str = "figures/snr_bootstrap_distribution.png"
    scatter_path: str = "figures/signal_noise_scatter.png"
    contribution_path: str = "figures/error_type_contribution.png"


@dataclass
class H_M4_Config:
    seed: int = SEED
    n_samples: int = N_SAMPLES
    n_per_category: int = 100  # ponytail: 100 per category for PoC
    bootstrap: BootstrapConfig = field(default_factory=BootstrapConfig)
    permutation: PermutationConfig = field(default_factory=PermutationConfig)
    viz: VizConfig = field(default_factory=VizConfig)
    output_dir: str = "results"
    figures_dir: str = "figures"


def get_config() -> H_M4_Config:
    return H_M4_Config()


def setup_dirs(cfg: H_M4_Config):
    os.makedirs(cfg.output_dir, exist_ok=True)
    os.makedirs(cfg.figures_dir, exist_ok=True)
