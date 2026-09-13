from dataclasses import dataclass, field
from typing import Tuple


@dataclass
class ExperimentConfig:
    # Analysis parameters
    seed: int = 42
    n_bootstrap: int = 1000
    n_samples_per_example: int = 5
    aggregation_gate_threshold: float = 0.50
    aggregation_ci_lower_threshold: float = 0.30
    collapse_rate_threshold: float = 0.20
    correlation_threshold: float = 0.10

    # NLI model for fallback re-clustering
    nli_model_id: str = "microsoft/deberta-large-mnli"

    # Input paths (relative to h-m2/code/)
    se_scores_path: str = "../../h-e1/code/outputs/uq_scores/semantic_entropy.json"
    stochastic_samples_path: str = "../../h-e1/code/outputs/stochastic_samples.jsonl"
    dataset_path: str = "../../h-e1/code/data/halueval_qa_2k.json"
    hm1_results_path: str = "../../h-m1/code/outputs/experiment_results.json"
    h_e1_code_dir: str = "../../h-e1/code"

    # Output paths (relative to h-m2/code/)
    results_dir: str = "outputs"
    figures_dir: str = "../figures"

    # Visualization
    figure_dpi: int = 150
    figure_format: str = "png"
    bar_figsize: Tuple[int, int] = (7, 5)
    histogram_figsize: Tuple[int, int] = (8, 5)
    boxplot_figsize: Tuple[int, int] = (7, 5)
    cdf_figsize: Tuple[int, int] = (8, 5)
    bar_type_figsize: Tuple[int, int] = (9, 5)


def get_config() -> ExperimentConfig:
    return ExperimentConfig()
