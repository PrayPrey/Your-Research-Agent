from dataclasses import dataclass, field
from typing import Tuple


@dataclass
class ExperimentConfig:
    # Analysis parameters
    seed: int = 42
    n_bootstrap: int = 1000
    degenerate_threshold: float = 1e-6
    pearson_gate_threshold: float = 0.9
    divergence_sigma_multiplier: float = 1.0

    # Input paths (relative to h-m1/code/)
    te_scores_path: str = "../../h-e1/code/outputs/uq_scores/token_entropy_mean.json"
    se_scores_path: str = "../../h-e1/code/outputs/uq_scores/semantic_entropy.json"
    stochastic_samples_path: str = "../../h-e1/code/outputs/stochastic_samples.jsonl"
    dataset_path: str = "../../h-e1/code/data/halueval_qa_2k.json"

    # Output paths (relative to h-m1/code/)
    results_dir: str = "outputs"
    figures_dir: str = "../figures"
    results_file: str = "outputs/experiment_results.json"

    # Visualization
    figure_dpi: int = 150
    figure_format: str = "png"
    scatter_figsize: Tuple[int, int] = (8, 8)
    histogram_figsize: Tuple[int, int] = (10, 6)
    cdf_figsize: Tuple[int, int] = (8, 6)
    ttr_figsize: Tuple[int, int] = (8, 6)
    divergence_figsize: Tuple[int, int] = (10, 6)


def get_config() -> ExperimentConfig:
    return ExperimentConfig()
