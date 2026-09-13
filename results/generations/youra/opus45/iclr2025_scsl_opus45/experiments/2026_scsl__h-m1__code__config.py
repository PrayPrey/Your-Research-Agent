"""Configuration module for H-M1 experiment.

Curvature timing analysis: minority samples show delayed curvature stabilization
(sign-flip epoch >= 3 epochs later than majority in >= 70% of seeds).

SHOULD_WORK gate - extends H-E1 infrastructure.
"""

from dataclasses import dataclass, field
from typing import List, Tuple


@dataclass
class Config:
    """Experiment configuration for H-M1 hypothesis validation."""

    # Dataset (unchanged from H-E1)
    data_root: str = "/home/anonymous/YouRA_results_new_4_sonnet45/TEST_scsl_opus45_4/docs/youra_research/20260414_scsl/.data_cache/datasets/waterbirds/waterbird_complete95_forest2water2"
    dataset: str = "waterbirds"
    num_workers: int = 4
    pin_memory: bool = True

    # Preprocessing (unchanged from H-E1)
    train_crop_size: int = 224
    eval_resize: int = 256
    eval_crop_size: int = 224
    img_mean: Tuple[float, float, float] = (0.485, 0.456, 0.406)
    img_std: Tuple[float, float, float] = (0.229, 0.224, 0.225)

    # Model (unchanged from H-E1)
    model_name: str = "resnet50"
    num_classes: int = 2

    # Training (extended from H-E1)
    epochs: int = 20
    trajectory_epochs: int = 20  # Changed from H-E1's 5 to track ALL epochs
    batch_size: int = 128
    lr: float = 0.001
    momentum: float = 0.9
    weight_decay: float = 0.0001

    # Multi-seed (NEW - replaces single seed from H-E1)
    seeds: List[int] = field(default_factory=lambda: [42, 123, 456, 789, 1011])

    # Curvature parameters (NEW)
    smoothing_sigma: float = 1.0
    curvature_threshold: float = -0.002
    consecutive_epochs: int = 2

    # Gate parameters (NEW)
    timing_gap_threshold: float = 3.0
    pass_rate_threshold: float = 0.70

    # Output
    output_dir: str = "./outputs"
    figures_dir: str = "./figures"
    fig_dpi: int = 300


def get_config() -> Config:
    """Return default H-M1 experiment configuration."""
    return Config()
