from dataclasses import dataclass, field
from typing import List


@dataclass
class ExperimentConfig:
    """Configuration for H-M2 epsilon robustness experiment."""

    # Model settings
    model_name: str = "meta-llama/Llama-3.1-8B"
    n_layers: int = 32
    torch_dtype: str = "float16"
    device_map: str = "auto"

    # Experiment settings
    n_samples: int = 512
    batch_size: int = 8
    seed: int = 42
    max_length: int = 512

    epsilons: List[float] = field(default_factory=lambda: [0.001, 0.01, 0.05, 0.1])
    primary_epsilon: float = 0.01

    # Dataset identifiers
    alpaca_dataset: str = "tatsu-lab/alpaca"
    wikitext_dataset: str = "wikitext"
    wikitext_config: str = "wikitext-103-raw-v1"

    # Output paths
    figures_dir: str = "/home/anonymous/YouRA_results_new_4/TEST_scope_4/docs/youra_research/20260508_scope/h-m2/figures"
    results_path: str = "/home/anonymous/YouRA_results_new_4/TEST_scope_4/docs/youra_research/20260508_scope/h-m2/experiment_results.json"

    # Gate thresholds
    cv_threshold: float = 0.3
    cv_pass_min_count: int = 3
    cross_epsilon_tau_threshold: float = 0.7
    cross_dist_tau_threshold: float = 0.6

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
        assert self.cv_pass_min_count in [1, 2, 3, 4], (
            f"cv_pass_min_count ({self.cv_pass_min_count}) must be in [1,2,3,4]"
        )
        assert 0 < self.cross_epsilon_tau_threshold <= 1, (
            f"cross_epsilon_tau_threshold must be in (0, 1]"
        )
        assert 0.0 < self.cv_threshold < 1.0, "cv_threshold must be in (0, 1)"
        assert self.torch_dtype in ("float16", "bfloat16", "float32"), (
            f"torch_dtype '{self.torch_dtype}' not supported"
        )
