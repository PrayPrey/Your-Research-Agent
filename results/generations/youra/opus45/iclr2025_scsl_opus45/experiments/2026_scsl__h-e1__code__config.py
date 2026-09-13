"""Configuration module for H-E1 experiment.

Per-sample loss trajectory features for minority group prediction.
AUROC > 0.75 target (MUST_WORK gate).
"""

from dataclasses import dataclass
from typing import Tuple


@dataclass
class Config:
    """Experiment configuration for H-E1 hypothesis validation."""

    # Dataset
    data_root: str = "./data/waterbirds"
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

    # Training
    seed: int = 42
    epochs: int = 20
    trajectory_epochs: int = 5
    batch_size: int = 128
    lr: float = 0.001
    momentum: float = 0.9
    weight_decay: float = 0.0001

    # Evaluation
    n_folds: int = 5
    auroc_threshold: float = 0.75
    lr_clf_max_iter: int = 1000

    # Output
    output_dir: str = "./outputs"
    figures_dir: str = "./figures"

    # Visualization
    fig_dpi: int = 300
    fig_format: str = "png"
    fig_gate_filename: str = "gate_metrics.png"
    fig_trajectory_filename: str = "loss_trajectories.png"
    fig_roc_filename: str = "roc_curve.png"
    fig_features_filename: str = "feature_distributions.png"


def get_config() -> Config:
    """Return default experiment configuration."""
    return Config()
