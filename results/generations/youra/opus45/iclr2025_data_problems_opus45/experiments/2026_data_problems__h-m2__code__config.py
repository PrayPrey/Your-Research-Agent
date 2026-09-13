"""
Configuration for H-M2: Deep Network Metric Decoupling
Tests R^2 drop from convex (H-M1) to non-convex (ResNet-18)
MUST_WORK gate: R^2_deep < 0.80
"""

from dataclasses import dataclass, field
from typing import List, Dict
import os


@dataclass
class HM2Config:
    # Data (matching H-E1/H-M1 exactly)
    data_root: str = './data'
    train_subset_size: int = 5000
    test_subset_size: int = 100
    subset_seed: int = 42
    train_batch_size: int = 128
    test_batch_size: int = 256

    # External paths (relative to h-m2/code/)
    he1_code_path: str = '../../h-e1/code'
    hm1_code_path: str = '../../h-m1/code'
    he1_checkpoint: str = '../../h-e1/code/checkpoints/model_seed0_final.pt'
    loo_cache_path: str = '../../h-e1/code/results/loo_cache.npy'
    he1_scores_path: str = '../../h-e1/code/results/all_scores.npz'
    hm1_results_path: str = '../../h-m1/code/results/metrics.csv'

    # Experiment
    methods: List[str] = field(default_factory=lambda: ['TRAK', 'TracIn', 'IF', 'FastIF'])
    compute_budgets: List[int] = field(default_factory=lambda: [10, 25, 50, 75, 100])
    seeds: List[int] = field(default_factory=lambda: [0, 1, 2])

    # Gate thresholds (H-M2 MUST_WORK: deep must show LOWER values)
    r2_threshold: float = 0.80         # R^2_deep must be BELOW this
    partial_corr_threshold: float = 0.85  # corr must be BELOW this
    delta_r2_threshold: float = 0.15   # delta_R^2 must be ABOVE this

    # H-M1 convex baseline (hardcoded from validated H-M1 results)
    hm1_r2_rho_r: float = 0.95
    hm1_r2_rho_m: float = 0.95
    hm1_partial_corr: Dict[int, float] = field(default_factory=lambda: {
        10: 0.9961, 25: 0.9945, 50: 0.9899, 75: 0.9905, 100: 0.9916
    })

    # I/O
    results_dir: str = './results'
    figures_dir: str = './figures'


def get_config() -> HM2Config:
    """Get configuration, create output directories."""
    cfg = HM2Config()
    os.makedirs(cfg.results_dir, exist_ok=True)
    os.makedirs(cfg.figures_dir, exist_ok=True)
    return cfg
