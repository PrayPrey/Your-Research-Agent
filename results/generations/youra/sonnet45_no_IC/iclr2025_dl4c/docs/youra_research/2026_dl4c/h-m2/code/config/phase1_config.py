"""
Phase1ExperimentConfig - Extension of h-e1 config for h-m1
Task: A-6
Hypothesis: h-m1
"""

import torch
from dataclasses import dataclass, field
from typing import List
from .experiment_config import ExperimentConfig, PPOConfig


@dataclass
class Phase1Config:
    """Phase 1 specific configuration."""
    checkpoints: List[float] = field(default_factory=lambda: [0.0, 0.1, 0.2, 0.3, 0.7, 1.0])
    gate_thresholds: dict = field(default_factory=lambda: {
        'weight_dominance_violations': 0,
        'min_phase1_improvement_ratio': 1.0,
        'min_weight_correlation': -0.5
    })


@dataclass
class Phase1ExperimentConfig(ExperimentConfig):
    """Extended configuration for h-m1 experiment."""
    phase1: Phase1Config = field(default_factory=Phase1Config)

    def __post_init__(self):
        # Override experiment name
        self.experiment_name = "h-m1-phase1-validation"

        # Override PPO config for PoC (reduced from 10k to 1k episodes)
        self.ppo.total_steps = 1000

        # Set checkpoint dir
        self.checkpoint_dir = "./checkpoints"

        # Auto-detect device (prefer CUDA if available)
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
