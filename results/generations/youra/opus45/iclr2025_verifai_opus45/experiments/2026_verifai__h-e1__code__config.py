"""Experiment configuration for H-E1: Runtime Error Prevalence."""

from dataclasses import dataclass


@dataclass
class ExperimentConfig:
    """Configuration for runtime error prevalence experiment."""

    # Model
    model_id: str = "codellama/CodeLlama-7b-Instruct-hf"
    max_new_tokens: int = 512
    temperature: float = 0.0
    do_sample: bool = False

    # Dataset
    dataset_name: str = "mbpp"
    task_id_min: int = 11
    task_id_max: int = 510

    # Execution
    execution_timeout: int = 10

    # Reproducibility
    seed: int = 1

    # Paths
    results_dir: str = "results"
    figures_dir: str = "results/figures"
    output_json: str = "results/execution_results.json"
    output_metrics: str = "results/metrics.yaml"

    # Gate
    gate_threshold: float = 0.30
    ci_confidence: float = 0.95
    ci_method: str = "wilson"
