"""Configuration dataclasses for H-E2 SAT profiling experiment."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Literal
import random
import numpy as np
import torch


@dataclass
class CNNConfig:
    """Configuration for CNN profiling experiments."""

    # Model specification
    model_name: str
    dataset: str
    optimizer: str

    # Training hyperparameters
    batch_size: int
    lr: float
    momentum: float = 0.9
    weight_decay: float = 0.0001

    # Profiling settings
    num_profiling_batches: int = 50
    device: str = "cpu"  # CPU mode for compatibility


@dataclass
class TransformerConfig:
    """Configuration for Transformer profiling experiments."""

    # Model specification
    model_name: str
    dataset: str
    optimizer: str

    # Training hyperparameters
    batch_size: int
    seq_length: int
    lr: float
    weight_decay: float = 0.01

    # Profiling settings
    num_profiling_batches: int = 50
    device: str = "cpu"  # CPU mode for compatibility


@dataclass
class ProfilingConfig:
    """SAT profiling protocol configuration."""

    # Batch-level profiling
    num_batches: int = 50
    warmup_batches: int = 5

    # GPU monitoring
    gpu_util_sampling_interval: float = 0.1  # seconds
    use_torch_cuda_utilization: bool = False

    # Epoch timing validation
    measure_full_epoch: bool = True

    # Synchronization
    cuda_synchronize: bool = True


@dataclass
class JitterConfig:
    """Synthetic jitter experiment configuration."""

    # Delay injection (milliseconds)
    delay_levels: List[int] = field(default_factory=lambda: [0, 50, 100, 200])

    # Causality validation
    num_batches_per_delay: int = 50
    warmup_batches: int = 5

    # Reference config for jitter experiments
    base_config_type: Literal["cnn", "transformer"] = "cnn"


@dataclass
class AnalysisConfig:
    """Metrics and evaluation configuration."""

    # SAT threshold for degradation prediction
    sat_threshold: float = 1.5
    degradation_threshold: float = 0.15  # 15%

    # Metrics targets
    precision_target: float = 0.80
    recall_target: float = 0.70
    f1_target: float = 0.75

    # Causality validation
    gpu_util_low_threshold: float = 0.90  # Below 90% = data loading bottleneck


@dataclass
class OutputConfig:
    """Output and logging configuration."""

    # Results directory
    hypothesis_folder: Path = Path("docs/youra_research/h-e2")

    # Output files
    profiling_results: str = "profiling_results.json"
    metrics_summary: str = "metrics_summary.json"

    # Figures
    figure_format: str = "png"
    dpi: int = 300
    figures_subdir: str = "figures"

    # Logging
    log_level: str = "INFO"


@dataclass
class ReproducibilityConfig:
    """Reproducibility settings for profiling experiments."""

    random_seed: int = 42
    deterministic_cuda: bool = False  # Profiling experiments - prioritize realism

    # Environment
    cuda_visible_devices: str = "0"

    # Logging
    log_pytorch_version: bool = True
    log_cuda_version: bool = True
    log_gpu_model: bool = True


@dataclass
class ExperimentConfig:
    """Master configuration for H-E2 SAT profiling experiment."""

    profiling: ProfilingConfig = field(default_factory=ProfilingConfig)
    jitter: JitterConfig = field(default_factory=JitterConfig)
    analysis: AnalysisConfig = field(default_factory=AnalysisConfig)
    output: OutputConfig = field(default_factory=OutputConfig)
    reproducibility: ReproducibilityConfig = field(default_factory=ReproducibilityConfig)

    def __post_init__(self):
        """Validate configuration and create directories."""
        # Validate SAT threshold
        assert self.analysis.sat_threshold > 1.0, \
            "SAT threshold must be > 1.0 (ratio of P95/Median)"

        # Validate degradation threshold
        assert 0.0 < self.analysis.degradation_threshold < 1.0, \
            "Degradation threshold must be between 0 and 1"

        # Validate profiling batches
        assert self.profiling.num_batches >= 50, \
            "Minimum 50 batches required for reliable P95 estimation"

        # Create output directories
        self.output.hypothesis_folder.mkdir(parents=True, exist_ok=True)
        (self.output.hypothesis_folder / "results").mkdir(parents=True, exist_ok=True)
        (self.output.hypothesis_folder / self.output.figures_subdir).mkdir(
            parents=True, exist_ok=True
        )


def get_cnn_configs() -> List[CNNConfig]:
    """Generate simplified CNN profiling configurations (reduced for PoC)."""

    configs = []

    # Reduced model set for faster PoC validation (8 -> 3 models)
    cnn_models = ["resnet18", "mobilenet_v2", "efficientnet_b0"]

    # Single dataset for PoC
    dataset = "cifar10"

    # Reduced optimizer set (3 -> 2)
    optimizers = ["sgd", "adam"]

    # Batch sizes
    batch_sizes = {
        "resnet18": 64,
        "mobilenet_v2": 64,
        "efficientnet_b0": 32
    }

    # Learning rates
    lrs = {"sgd": 0.01, "adam": 0.001}

    # Generate configs: 3 models × 2 optimizers = 6 configs
    for model in cnn_models:
        for opt in optimizers:
            configs.append(CNNConfig(
                model_name=model,
                dataset=dataset,
                optimizer=opt,
                batch_size=batch_sizes[model],
                lr=lrs[opt]
            ))

    return configs


def get_transformer_configs() -> List[TransformerConfig]:
    """Generate simplified Transformer profiling configurations (reduced for PoC)."""

    configs = []

    # Reduced model set for faster PoC (8 -> 3 models)
    transformer_models = ["distilbert-base-uncased", "albert-base-v2", "google/electra-small-discriminator"]

    # Single dataset for PoC
    dataset = "personachat"

    # Reduced optimizer set (3 -> 2)
    optimizers = ["adam", "adamw"]

    # Model configs
    model_configs = {
        "distilbert-base-uncased": {"seq_length": 128, "batch_size": 16},
        "albert-base-v2": {"seq_length": 128, "batch_size": 16},
        "google/electra-small-discriminator": {"seq_length": 128, "batch_size": 16}
    }

    # Learning rate
    lr = 2e-5

    # Generate configs: 3 models × 2 optimizers = 6 configs
    for model in transformer_models:
        for opt in optimizers:
            configs.append(TransformerConfig(
                model_name=model,
                dataset=dataset,
                optimizer=opt,
                batch_size=model_configs[model]["batch_size"],
                seq_length=model_configs[model]["seq_length"],
                lr=lr
            ))

    return configs


def set_reproducibility(config: ReproducibilityConfig):
    """Configure environment for reproducible profiling."""
    import os

    # Set seeds
    random.seed(config.random_seed)
    np.random.seed(config.random_seed)
    torch.manual_seed(config.random_seed)

    if torch.cuda.is_available():
        torch.cuda.manual_seed(config.random_seed)
        torch.cuda.manual_seed_all(config.random_seed)

        if config.deterministic_cuda:
            torch.backends.cudnn.deterministic = True
            torch.backends.cudnn.benchmark = False

    # Set environment variables
    os.environ["CUDA_VISIBLE_DEVICES"] = config.cuda_visible_devices


def log_environment(config: ReproducibilityConfig):
    """Log environment information for reproducibility."""
    import logging

    logger = logging.getLogger(__name__)

    if config.log_pytorch_version:
        logger.info(f"PyTorch version: {torch.__version__}")

    if config.log_cuda_version and torch.cuda.is_available():
        logger.info(f"CUDA version: {torch.version.cuda}")

    if config.log_gpu_model and torch.cuda.is_available():
        logger.info(f"GPU model: {torch.cuda.get_device_name(0)}")
        logger.info(f"GPU memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
