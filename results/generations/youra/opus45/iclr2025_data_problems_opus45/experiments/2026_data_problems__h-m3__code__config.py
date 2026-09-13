"""
Configuration for H-M3: Method Disagreement Analysis
Top-k Jaccard gate for demonstrating method design paradigm trade-offs.
"""

from dataclasses import dataclass, field
from typing import List
import os


@dataclass
class H3Config:
    # Data (matching H-E1 naming conventions exactly)
    data_root: str = './data'
    train_subset_size: int = 5000
    loo_test_size: int = 100
    subset_seed: int = 42
    train_batch_size: int = 128
    test_batch_size: int = 256

    # Attribution (matching H-E1 exactly)
    methods: List[str] = field(default_factory=lambda: ['TRAK', 'TracIn', 'IF', 'FastIF'])
    compute_budgets: List[int] = field(default_factory=lambda: [10, 25, 50, 75, 100])
    method_seeds: List[int] = field(default_factory=lambda: [0, 1, 2])

    # Jaccard Analysis (gate metric)
    top_k: int = 50
    jaccard_threshold: float = 0.70  # gate: min(Jaccard) must be BELOW this

    # Persistence Analysis
    persistence_threshold: float = 0.60  # method must lead >60% of budgets

    # External Paths (relative to h-m3/code/)
    base_code_dir: str = '../../h-e1/code'
    checkpoint_path: str = '../../h-e1/code/checkpoints/model_seed0_final.pt'

    # I/O
    results_dir: str = './results'
    figures_dir: str = './figures'


def get_config() -> H3Config:
    """Get configuration, create output directories."""
    cfg = H3Config()
    os.makedirs(cfg.results_dir, exist_ok=True)
    os.makedirs(cfg.figures_dir, exist_ok=True)
    return cfg
