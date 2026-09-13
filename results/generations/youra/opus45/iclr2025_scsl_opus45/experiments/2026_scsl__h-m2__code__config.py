"""Configuration module for H-M2 experiment.

Spurious-specificity mechanism test: GroupDRO attenuation analysis.
Gate: AUROC_ERM - AUROC_GroupDRO > 0.10 AND AUROC_ERM - AUROC_Random < 0.05
"""

from dataclasses import dataclass
from typing import Tuple


@dataclass
class Config:
    """Experiment configuration for H-M2 hypothesis validation."""

    # Dataset
    data_root: str = "../../.data_cache/datasets/waterbirds/waterbird_complete95_forest2water2"
    dataset: str = "waterbirds"
    num_workers: int = 4
    pin_memory: bool = True

    # Preprocessing
    train_crop_size: int = 224
    eval_resize: int = 256
    eval_crop_size: int = 224
    img_mean: Tuple[float, float, float] = (0.485, 0.456, 0.406)
    img_std: Tuple[float, float, float] = (0.229, 0.224, 0.225)

    # Model
    model_name: str = "resnet50"
    num_classes: int = 2

    # Training (shared across regimes)
    epochs: int = 20
    trajectory_epochs: int = 5
    batch_size: int = 128
    lr: float = 0.001
    momentum: float = 0.9

    # Multi-seed
    base_seed: int = 42
    num_seeds: int = 3

    # Group info
    num_groups: int = 4

    # ERM hyperparams
    weight_decay_erm: float = 0.0001

    # GroupDRO hyperparams (from kohpangwei/group_DRO)
    weight_decay_gdro: float = 1.0  # Strong regularization
    groupdro_gamma: float = 0.1  # Exponentiated gradient step size

    # Evaluation
    n_folds: int = 5
    lr_clf_max_iter: int = 1000

    # Gate thresholds
    delta_gdro_threshold: float = 0.10
    delta_random_threshold: float = 0.05

    # Output
    output_dir: str = "./outputs"
    figures_dir: str = "./figures"

    # Visualization
    fig_dpi: int = 300
    fig_format: str = "png"
    fig_gate_filename: str = "gate_metrics.png"
    fig_auroc_comparison_filename: str = "auroc_comparison.png"
    fig_group_weights_filename: str = "group_weights_evolution.png"
    fig_grad_variance_filename: str = "gradient_variance.png"
    fig_trajectory_panels_filename: str = "loss_trajectory_panels.png"

    # Results output
    results_filename: str = "results.json"


def get_config() -> Config:
    """Return default experiment configuration."""
    return Config()
