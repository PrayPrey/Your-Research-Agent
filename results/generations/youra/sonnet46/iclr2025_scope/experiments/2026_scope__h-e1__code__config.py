from dataclasses import dataclass, field
from typing import List


@dataclass
class ExperimentConfig:
    """Configuration for H-E1 activation sparsity measurement experiment."""

    # Model settings
    model_name: str = "meta-llama/Meta-Llama-3-8B"
    n_layers: int = 32
    torch_dtype: str = "float16"
    device_map: str = "auto"

    # Experiment settings
    n_samples: int = 512
    batch_size: int = 8
    seed: int = 42

    epsilons: List[float] = field(default_factory=lambda: [0.001, 0.01, 0.05, 0.1])
    primary_epsilon: float = 0.01

    # Sequence lengths
    short_length: int = 128
    long_length: int = 512

    # Dataset identifiers
    alpaca_dataset: str = "tatsu-lab/alpaca"
    wikitext_dataset: str = "wikitext"
    wikitext_config: str = "wikitext-103-raw-v1"

    # Output paths
    figures_dir: str = "h-e1/figures"
    results_dir: str = "h-e1/results"

    # Gate thresholds
    cv_threshold: float = 0.3
    tau_threshold: float = 0.6

    def __post_init__(self):
        assert self.n_layers > 0, "n_layers must be positive"
        assert self.n_samples > 0, "n_samples must be positive"
        assert self.batch_size > 0, "batch_size must be positive"
        assert self.n_samples % self.batch_size == 0, (
            f"n_samples ({self.n_samples}) must be divisible by batch_size ({self.batch_size})"
        )
        assert self.primary_epsilon in self.epsilons, (
            f"primary_epsilon ({self.primary_epsilon}) must be in epsilons list {self.epsilons}"
        )
        assert self.short_length < self.long_length, (
            f"short_length ({self.short_length}) must be < long_length ({self.long_length})"
        )
        assert 0.0 < self.cv_threshold < 1.0, "cv_threshold must be in (0, 1)"
        assert 0.0 < self.tau_threshold <= 1.0, "tau_threshold must be in (0, 1]"
        assert self.torch_dtype in ("float16", "bfloat16", "float32"), (
            f"torch_dtype '{self.torch_dtype}' not supported"
        )
