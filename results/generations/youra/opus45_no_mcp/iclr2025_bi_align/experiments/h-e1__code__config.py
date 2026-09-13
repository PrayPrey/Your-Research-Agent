"""Experiment configuration for H-E1 calibration inversion clustering."""

from dataclasses import dataclass, field
from typing import List


@dataclass
class ExperimentConfig:
    # Datasets
    datasets: List[str] = field(default_factory=lambda: ["truthfulqa", "mmlu_moral", "anthropic_hh"])

    # Models
    models: List[str] = field(default_factory=lambda: [
        "meta-llama/Llama-2-7b-chat-hf",
        "meta-llama/Llama-2-13b-chat-hf",
        "mistralai/Mistral-7B-Instruct-v0.2",
    ])
    primary_model_index: int = 0

    # Calibration
    inversion_threshold: float = 0.1

    # Clustering
    k_range: List[int] = field(default_factory=lambda: [2, 3, 4, 5])
    default_k: int = 3
    silhouette_gate: float = 0.3

    # Inference
    batch_size: int = 8
    device: str = "cuda"

    # Reproducibility
    seed: int = 42

    # Output
    output_dir: str = "outputs"
    results_path: str = "outputs/results.json"
    figures_dir: str = "../figures"


CONFIG = ExperimentConfig()
