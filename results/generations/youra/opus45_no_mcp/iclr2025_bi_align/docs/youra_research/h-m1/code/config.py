"""Configuration for H-M1 RLHF reward signal conflation analysis."""

from dataclasses import dataclass, field
from typing import List


@dataclass
class M1Config:
    # Inherited from H-E1 (must match for data/model reuse)
    datasets: List[str] = field(default_factory=lambda: ["truthfulqa", "mmlu_moral", "anthropic_hh"])
    models: List[str] = field(default_factory=lambda: [
        "meta-llama/Llama-2-7b-chat-hf",
        "meta-llama/Llama-2-13b-chat-hf",
        "mistralai/Mistral-7B-Instruct-v0.2",
    ])
    primary_model_index: int = 0
    batch_size: int = 8
    device: str = "cuda"
    seed: int = 42

    # H-M1 specific gates
    overlap_gate: float = 0.7
    mean_diff_gate: float = 0.1
    overlap_fail_gate: float = 0.5
    mean_diff_fail_gate: float = 0.2
    correlation_supporting_threshold: float = 0.3

    # Task classification
    bidir_score_threshold: int = 1  # ABL-1 sweeps: 1, 2, 3
    hist_bins: int = 50

    # Paths
    he1_results_path: str = "../../h-e1/code/outputs/results.json"
    output_dir: str = "outputs"
    results_path: str = "outputs/results.json"
    figures_dir: str = "../figures"


CONFIG = M1Config()
