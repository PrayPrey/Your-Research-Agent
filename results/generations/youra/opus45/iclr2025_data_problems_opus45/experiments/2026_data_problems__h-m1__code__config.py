"""
Configuration for H-M1: Convex Metric Coupling
Testing that corr(rho_r, rho_m | budget) >= 0.95 in convex settings.
"""

from dataclasses import dataclass, field
from typing import List
import os


@dataclass
class HM1Config:
    # Data
    data_root: str = './data'
    he1_checkpoint: str = '../../h-e1/code/checkpoints/model_seed0_final.pt'
    he1_code_path: str = '../../h-e1/code'
    train_subset_size: int = 5000
    test_subset_size: int = 100
    subset_seed: int = 42
    feature_dim: int = 512
    n_classes: int = 10

    # Logistic Regression
    C: float = 100.0  # lambda_reg = 1/C = 0.01
    lr_solver: str = 'lbfgs'
    lr_max_iter: int = 1000

    # Experiment
    methods: List[str] = field(default_factory=lambda: ['TRAK', 'TracIn', 'IF', 'FastIF'])
    compute_budgets: List[int] = field(default_factory=lambda: [10, 25, 50, 75, 100])
    seeds: List[int] = field(default_factory=lambda: [0, 1, 2])
    n_bootstrap: int = 1000

    # Success thresholds (MUST_WORK gate)
    partial_corr_threshold: float = 0.95
    r2_threshold: float = 0.95

    # I/O
    results_dir: str = './results'
    figures_dir: str = './figures'


def get_config() -> HM1Config:
    """Get configuration, create directories if needed."""
    cfg = HM1Config()
    os.makedirs(cfg.results_dir, exist_ok=True)
    os.makedirs(cfg.figures_dir, exist_ok=True)
    return cfg
