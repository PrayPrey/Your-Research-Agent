"""Configuration for Semantic Entropy Decomposition experiments."""

import os
from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class ExperimentConfig:
    """Configuration for SED experiments."""

    # Model settings
    model_name: str = "Qwen/Qwen2.5-0.5B-Instruct"  # Small model for efficiency
    device: str = "cuda"

    # Probe settings
    probe_layers: List[int] = field(default_factory=lambda: [8, 10, 12, 14, 16, 18, 20, 22])  # Upper layers
    probe_hidden_dim: int = 256
    probe_dropout: float = 0.1

    # Training settings
    num_epochs: int = 10
    batch_size: int = 8
    learning_rate: float = 1e-4
    weight_decay: float = 0.01
    warmup_steps: int = 50

    # Loss weights
    lambda_contrast: float = 0.5
    lambda_consist: float = 0.3
    margin: float = 0.2

    # Semantic entropy settings
    num_samples_for_se: int = 3  # Number of samples for ground truth semantic entropy
    temperature: float = 0.7
    max_new_tokens: int = 32

    # Dataset settings
    train_samples: int = 300
    val_samples: int = 60
    test_samples: int = 100

    # Evaluation settings
    num_bins: int = 10  # For ECE calculation

    # Paths
    output_dir: str = "outputs"
    checkpoint_dir: str = "checkpoints"

    # Random seed
    seed: int = 42


def get_config() -> ExperimentConfig:
    """Get default experiment configuration."""
    config = ExperimentConfig()

    # Adjust probe layers based on model
    if "0.5B" in config.model_name or "0.6B" in config.model_name:
        config.probe_layers = [12, 14, 16, 18, 20, 22]  # Qwen2.5-0.5B has 24 layers
    elif "1B" in config.model_name:
        config.probe_layers = [14, 16, 18, 20, 22, 24, 26, 28]

    return config
