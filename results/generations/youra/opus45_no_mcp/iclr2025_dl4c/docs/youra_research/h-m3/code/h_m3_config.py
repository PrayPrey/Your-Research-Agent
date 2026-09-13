"""Configuration for H-M3 gradient noise analysis."""
import sys
import os
from dataclasses import dataclass, field

H_M2_CODE = os.path.join(os.path.dirname(__file__), '../../h-m2/code')
sys.path.insert(0, H_M2_CODE)

import importlib.util
_spec = importlib.util.spec_from_file_location("h_m2_config", os.path.join(H_M2_CODE, "config.py"))
_h_m2_cfg = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_h_m2_cfg)
U_LINE_ERRORS = _h_m2_cfg.U_LINE_ERRORS
U_IGNORE_ERRORS = _h_m2_cfg.U_IGNORE_ERRORS
SEED = _h_m2_cfg.SEED

MODEL_NAME = "Salesforce/codet5-small"
MAX_INPUT_LEN = 512
MAX_OUTPUT_LEN = 256
N_PER_CATEGORY = 250  # Reduced for real data feasibility


@dataclass
class SamplesConfig:
    n_per_category: int = N_PER_CATEGORY
    seed: int = SEED
    dataset_name: str = "codeparrot/apps"
    dataset_split: str = "train"
    use_synthetic_fallback: bool = True


@dataclass
class NoiseConfig:
    target_penalty: float = -1.0
    other_penalty: float = -0.1
    normalize_by_line_length: bool = True
    eps: float = 1e-8


@dataclass
class StatsConfig:
    significance_threshold: float = 0.05
    confidence_level: float = 0.95
    bootstrap_n: int = 10000
    effect_size_medium: float = 0.5


@dataclass
class VizConfig:
    style: str = "seaborn-v0_8-whitegrid"
    dpi: int = 150
    boxplot_path: str = "figures/concentration_boxplot.png"
    histogram_path: str = "figures/noise_ratio_histogram.png"
    heatmap_path: str = "figures/gradient_heatmap.png"
    scatter_path: str = "figures/concentration_vs_noise_scatter.png"


@dataclass
class H_M3_Config:
    seed: int = SEED
    samples: SamplesConfig = field(default_factory=SamplesConfig)
    noise: NoiseConfig = field(default_factory=NoiseConfig)
    stats: StatsConfig = field(default_factory=StatsConfig)
    viz: VizConfig = field(default_factory=VizConfig)
    output_dir: str = "results"
    figures_dir: str = "figures"


def get_config():
    return H_M3_Config()
