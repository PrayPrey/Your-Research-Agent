"""
Configuration for QARP (Query-Aware Retention Policies) experiments.
"""
import os
from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class ExperimentConfig:
    # Model configuration
    model_name: str = "meta-llama/Llama-3.2-1B"

    # Dataset configuration
    dataset_name: str = "scrolls"
    dataset_subset: str = "qasper"
    max_samples: int = 100  # Limited for practical experiments
    max_seq_length: int = 2048  # Practical sequence length

    # KV Cache compression settings
    compression_ratios: List[float] = field(default_factory=lambda: [2.0, 4.0, 8.0])

    # RPN (Relevance Predictor Network) settings
    rpn_hidden_dim: int = 128
    rpn_num_layers: int = 2
    num_query_prototypes: int = 16
    recency_bias_alpha: float = 1.0

    # Training settings
    learning_rate: float = 1e-4
    batch_size: int = 4
    num_epochs: int = 3
    warmup_steps: int = 100

    # Evaluation settings
    eval_batch_size: int = 2

    # Output settings
    output_dir: str = "outputs"
    seed: int = 42

    # Device settings
    device: str = "cuda"

    def __post_init__(self):
        os.makedirs(self.output_dir, exist_ok=True)


@dataclass
class BaselineConfig:
    """Configuration for baseline methods."""
    # StreamingLLM settings
    attention_sink_size: int = 4
    recent_window_size: int = 256

    # H2O (Heavy Hitter Oracle) settings
    heavy_hitter_ratio: float = 0.2

    # Quantization settings
    quant_bits: List[int] = field(default_factory=lambda: [4, 8])
