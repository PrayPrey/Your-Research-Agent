"""
Configuration for EmbedPrint experiments.
"""
import os
from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class ExperimentConfig:
    """Configuration for EmbedPrint experiment."""

    # Model settings
    model_name: str = "distilgpt2"  # Small model for efficiency
    hidden_dim: int = 768
    signature_dim: int = 64
    projection_dim: int = 256

    # Clustering settings
    num_coarse_clusters: int = 10  # K1
    num_fine_clusters_per_coarse: int = 10  # K2

    @property
    def total_clusters(self) -> int:
        return self.num_coarse_clusters * self.num_fine_clusters_per_coarse

    # Training settings
    batch_size: int = 16
    learning_rate: float = 5e-5
    fingerprint_lr: float = 1e-3
    lambda_fp: float = 0.01  # Weight for fingerprint loss
    temperature: float = 0.07
    num_epochs: int = 3
    max_seq_length: int = 128
    num_neg_samples: int = 64  # Negative samples for contrastive loss

    # Dataset settings
    dataset_name: str = "wikitext"
    dataset_config: str = "wikitext-2-raw-v1"
    num_train_samples: int = 5000  # Subset for efficiency
    num_eval_samples: int = 500
    num_canary_samples: int = 100  # Distinctive samples for evaluation

    # Evaluation settings
    top_k_values: List[int] = field(default_factory=lambda: [1, 5, 10, 20])

    # Output settings
    output_dir: str = "outputs"
    results_dir: str = "results"
    seed: int = 42

    # Device settings
    device: str = "cuda"
    use_fp16: bool = True

    def __post_init__(self):
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.results_dir, exist_ok=True)


@dataclass
class BaselineConfig:
    """Configuration for baseline methods."""

    # TracIn settings
    tracin_checkpoints: int = 5  # Number of checkpoints for TracIn

    # Influence function settings
    influence_samples: int = 100  # Samples for influence estimation
    influence_recursion_depth: int = 10

    # TRAK settings
    trak_projection_dim: int = 512

    # Embedding similarity settings
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
