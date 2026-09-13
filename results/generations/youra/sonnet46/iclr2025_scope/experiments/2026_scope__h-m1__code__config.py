from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class ExperimentConfig:
    """Configuration for H-M1 cross-distribution activation sparsity measurement."""

    # Model settings
    model_name: str = "meta-llama/Llama-3.1-8B"
    n_layers: int = 32
    torch_dtype: str = "float16"
    device_map: str = "auto"

    # Experiment settings
    n_samples: int = 512
    batch_size: int = 8
    seed: int = 42
    epsilons: List[float] = field(default_factory=lambda: [0.001, 0.01, 0.05, 0.1])
    primary_epsilon: float = 0.01

    # Sequence length (single value; h-e1 used short_length/long_length)
    max_length: int = 512

    # Dataset identifiers
    alpaca_dataset: str = "tatsu-lab/alpaca"
    wikitext_dataset: str = "wikitext"
    wikitext_config: str = "wikitext-103-raw-v1"
    sst2_dataset: str = "SetFit/sst2"
    sst2_config_name: Optional[str] = None
    mnli_dataset: str = "nyu-mll/multi_nli"
    mnli_config_name: Optional[str] = None
    mnli_split: str = "validation_matched"
    sep_token: str = " [SEP] "

    # Output paths
    figures_dir: str = "h-m1/figures"
    results_path: str = "h-m1/experiment_results.json"

    # Gate thresholds
    icc_threshold: float = 0.75
    tau_threshold: float = 0.6

    def __post_init__(self):
        assert self.n_samples >= 512, "n_samples must be >= 512"
        assert self.n_samples % self.batch_size == 0, (
            f"n_samples ({self.n_samples}) must be divisible by batch_size ({self.batch_size})"
        )
        assert self.primary_epsilon in self.epsilons, (
            f"primary_epsilon ({self.primary_epsilon}) must be in epsilons list {self.epsilons}"
        )
        assert 0.0 < self.icc_threshold < 1.0, "icc_threshold must be in (0, 1)"
        assert 0.0 < self.tau_threshold <= 1.0, "tau_threshold must be in (0, 1]"
        assert self.torch_dtype in ("float16", "bfloat16", "float32"), (
            f"torch_dtype '{self.torch_dtype}' not supported"
        )
