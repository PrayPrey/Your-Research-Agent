"""Configuration module for low-rank analysis experiment."""

from dataclasses import dataclass, field
from typing import Optional, List
import os
import torch


@dataclass
class AnalysisConfig:
    """Configuration for low-rank structure analysis."""

    # Model configuration
    # Using Mistral-7B as substitute for LLaMA-7B (same architecture: 32 layers, 4096 hidden dim)
    # LLaMA-2 requires gated access which is not available
    model_name: str = "mistralai/Mistral-7B-v0.1"
    target_layers: range = field(default_factory=lambda: range(20, 32))  # Deep layers L≥20 as per hypothesis
    variance_threshold: float = 0.99

    # Data configuration
    num_samples: int = 1000  # Statistically meaningful sample size for SVD analysis
    context_length: int = 2048  # Standard context length for analysis
    batch_size: int = 4  # Batch size for efficiency

    # Runtime configuration
    random_seed: int = 42
    output_dir: str = "../figures"
    device: str = "cuda"
    use_fp16: bool = True

    # HuggingFace authentication
    hf_token: Optional[str] = None


@dataclass
class MechanismConfig(AnalysisConfig):
    """Configuration for mechanism validation experiment (h-m1)."""

    # Context stability testing (reduced to avoid OOM on single GPU)
    context_lengths: List[int] = field(default_factory=lambda: [2048, 4096, 8192])
    samples_per_context: int = 10
    stability_threshold: float = 1.2
    baseline_context_length: int = 2048

    # Override for mechanism testing
    context_length: int = 2048
    num_samples: int = 100  # Reasonable sample size for SVD analysis (100 batches = 100 samples with batch_size=1)
    batch_size: int = 1  # Reduce to 1 to avoid OOM with long contexts


def load_config() -> AnalysisConfig:
    """Load configuration from environment or use defaults."""
    config = AnalysisConfig()

    # Override from environment variables if present
    if "HF_TOKEN" in os.environ:
        config.hf_token = os.environ["HF_TOKEN"]

    if "NUM_SAMPLES" in os.environ:
        config.num_samples = int(os.environ["NUM_SAMPLES"])

    if "OUTPUT_DIR" in os.environ:
        config.output_dir = os.environ["OUTPUT_DIR"]

    if "MODEL_NAME" in os.environ:
        config.model_name = os.environ["MODEL_NAME"]

    return config


def load_mechanism_config() -> MechanismConfig:
    """Load mechanism configuration with environment variable overrides."""
    config = MechanismConfig()

    # Override from environment
    if "HF_TOKEN" in os.environ:
        config.hf_token = os.environ["HF_TOKEN"]

    if "MODEL_NAME" in os.environ:
        config.model_name = os.environ["MODEL_NAME"]

    if "NUM_SAMPLES" in os.environ:
        config.num_samples = int(os.environ["NUM_SAMPLES"])

    if "OUTPUT_DIR" in os.environ:
        config.output_dir = os.environ["OUTPUT_DIR"]

    if not torch.cuda.is_available():
        config.device = "cpu"

    return config
