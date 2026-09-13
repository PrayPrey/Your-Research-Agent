"""Configuration module for low-rank analysis experiment."""

from dataclasses import dataclass, field
from typing import Optional
import os


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
    num_samples: int = 50  # Minimal for PoC validation (sufficient for SVD analysis)
    context_length: int = 512  # Reduced to avoid OOM (from 2048)
    batch_size: int = 1  # Minimum batch size to avoid OOM

    # Runtime configuration
    random_seed: int = 42
    output_dir: str = "../figures"
    device: str = "cuda"
    use_fp16: bool = True

    # HuggingFace authentication
    hf_token: Optional[str] = None


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
