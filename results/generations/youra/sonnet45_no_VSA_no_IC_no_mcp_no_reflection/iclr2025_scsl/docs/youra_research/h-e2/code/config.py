"""
Configuration for h-e2: Gradient variance + forgetting analysis.
Extends h-e1 config with tracker parameters.
"""

from dataclasses import dataclass
from typing import Literal

@dataclass
class TrainConfig:
    dataset: str
    lr: float
    max_epochs: int
    weight_decay: float
    batch_size: int
    seed: int

@dataclass
class DatasetConfig:
    name: Literal['CMNIST', 'Waterbirds', 'CelebA', 'NICO++']
    batch_size: int
    num_workers: int = 4

# Extended config for h-e2
EXTENDED_TRAIN_CONFIG = {
    'dataset': 'CMNIST',
    'lr': 0.001,
    'max_epochs': 30,
    'weight_decay': 1e-4,
    'batch_size': 128,
    'seed': 0,
    'enable_tracking': True
}

# Gradient tracking
GRADIENT_TRACKER_CONFIG = {
    'window_size': 3,
    'checkpoint_epochs': [10, 20, 30],
    'track_per_param': False
}

# Forgetting tracking
FORGETTING_TRACKER_CONFIG = {
    'log_interval': 1,
    'num_samples': 50000
}

# Statistical tests
STATS_CONFIG = {
    'variance_ratio_threshold': 0.7,
    'p_value_threshold': 0.05,
    'test_variance': 'f_test',
    'test_forgetting': 'paired_ttest'
}

# PoC gate
POC_GATE = {
    'variance_ratio_max': 0.7,
    'forgetting_direction': 'spurious_less_than_core',
    'require_stats': False
}

# Visualization
PLOT_CONFIG = {
    'backend': 'Agg',
    'dpi': 150,
    'figsize': (10, 6),
    'color_spurious': '#E74C3C',
    'color_core': '#3498DB',
    'output_dir': './h-e2/figures'
}

PLOT_TYPES = ['gate_metrics', 'rolling_variance']

# Output paths
OUTPUT_CONFIG = {
    'results_dir': './h-e2/results',
    'figures_dir': './h-e2/figures',
    'variance_csv': 'variance_ratios.csv',
    'forgetting_csv': 'forgetting_rates.csv',
    'gate_plot': 'gate_metrics.png',
    'variance_plot': 'rolling_variance.png'
}
