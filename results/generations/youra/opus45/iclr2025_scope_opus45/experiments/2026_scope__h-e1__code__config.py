"""Configuration for H-E1: Spectral Memory Horizon Stability Experiment."""

from dataclasses import dataclass


@dataclass
class ExperimentConfig:
    """Configuration for H_spec stability measurement."""

    # Model
    model_id: str = "state-spaces/mamba-1.4b"
    model_370m_id: str = "state-spaces/mamba-370m"
    tokenizer_id: str = "EleutherAI/gpt-neox-20b"

    # Measurement
    num_samples: int = 1000
    seq_length: int = 512
    seed: int = 42

    # Gate condition
    cv_threshold: float = 0.3

    # Compute
    device: str = "cuda"
    dtype: str = "float32"

    # Output
    figures_dir: str = "figures"
    results_path: str = "results.yaml"
