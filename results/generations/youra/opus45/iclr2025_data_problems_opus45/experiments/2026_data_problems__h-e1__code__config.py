"""
Configuration for H-E1: Data Attribution Method Comparison
Pareto Trade-off Detection Experiment
"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class ExperimentConfig:
    # --- Data ---
    data_root: str = './data'
    train_subset_size: int = 5000
    loo_test_size: int = 100
    subset_seed: int = 42
    train_batch_size: int = 128
    test_batch_size: int = 256

    # --- Model Training ---
    epochs: int = 200
    lr: float = 0.1
    momentum: float = 0.9
    weight_decay: float = 5e-4
    lr_milestones: List[int] = field(default_factory=lambda: [100, 150])
    lr_gamma: float = 0.1

    # --- LOO Ground Truth ---
    n_loo_retrains: int = 10

    # --- Attribution Methods and Compute Budgets ---
    methods: List[str] = field(default_factory=lambda: ['TRAK', 'TracIn', 'IF', 'FastIF'])
    compute_budgets: List[int] = field(default_factory=lambda: [10, 25, 50, 75, 100])
    method_seeds: List[int] = field(default_factory=lambda: [0, 1, 2])

    # --- Bootstrap Statistics ---
    n_bootstrap: int = 1000
    confidence_level: float = 0.95

    # --- I/O Paths ---
    results_dir: str = './results'
    figures_dir: str = './figures'
    checkpoint_dir: str = './checkpoints'


def get_config() -> ExperimentConfig:
    return ExperimentConfig()
