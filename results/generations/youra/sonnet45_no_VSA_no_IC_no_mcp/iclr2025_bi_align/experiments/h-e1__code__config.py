"""Experiment configuration for h-e1 reformulation analysis."""

from dataclasses import dataclass


@dataclass
class ExperimentConfig:
    """Configuration for reformulation slope experiment."""

    # Dataset
    min_turns: int = 5
    dataset_name: str = "Anthropic/hh-rlhf"
    split: str = "train"

    # Reformulation Detection
    sbert_model_name: str = "all-MiniLM-L6-v2"
    semantic_threshold: float = 0.7
    syntactic_threshold: float = 0.3

    # Statistical Testing
    alpha: float = 0.05
    random_seed: int = 42

    # Output
    output_dir: str = "../results"
    figures_dir: str = "../figures"

    # Sampling for fast iteration (set to None for full dataset)
    max_samples: int = 2000  # Use 2000 conversations for experiment


def get_config():
    """Get experiment configuration."""
    return ExperimentConfig()
