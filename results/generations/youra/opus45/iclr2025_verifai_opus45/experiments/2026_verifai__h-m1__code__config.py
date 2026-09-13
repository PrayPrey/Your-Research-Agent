"""Experiment configuration for H-M1: Granularity Effect on Repair Success."""

from dataclasses import dataclass

# Granularity levels for error feedback
GRANULARITY_LEVELS = ["G0", "G1", "G2", "G3", "G4"]


@dataclass
class RepairConfig:
    """Configuration for granularity-controlled repair experiment."""

    # Model (same as H-E1)
    model_id: str = "codellama/CodeLlama-7b-Instruct-hf"
    max_new_tokens: int = 512
    temperature: float = 0.0
    do_sample: bool = False
    seed: int = 1

    # Data
    h_e1_results_path: str = "data/h_e1_results.json"
    mbpp_dataset_name: str = "google-research-datasets/mbpp"
    task_id_min: int = 11
    task_id_max: int = 510

    # Execution
    execution_timeout: int = 10

    # Paths
    results_dir: str = "results"
    figures_dir: str = "figures"
    output_json: str = "results/repair_results.json"
    output_metrics: str = "results/metrics.yaml"
    output_posthoc: str = "results/posthoc.yaml"
    checkpoint_path: str = "results/checkpoint.json"

    # Gate (ANOVA-specific)
    anova_alpha: float = 0.05
    eta_squared_threshold: float = 0.02


# For compatibility with H-E1 CodeGenerator which expects ExperimentConfig
@dataclass
class ExperimentConfig:
    """H-E1 compatible config for CodeGenerator."""

    model_id: str = "codellama/CodeLlama-7b-Instruct-hf"
    max_new_tokens: int = 512
    temperature: float = 0.0
    do_sample: bool = False
    seed: int = 1
    dataset_name: str = "mbpp"
    task_id_min: int = 11
    task_id_max: int = 510
    execution_timeout: int = 10
    results_dir: str = "results"
    figures_dir: str = "figures"
    output_json: str = "results/execution_results.json"
    output_metrics: str = "results/metrics.yaml"
    gate_threshold: float = 0.30
    ci_confidence: float = 0.95
    ci_method: str = "wilson"


def repair_config_to_experiment_config(rc: RepairConfig) -> ExperimentConfig:
    """Convert RepairConfig to ExperimentConfig for CodeGenerator compatibility."""
    return ExperimentConfig(
        model_id=rc.model_id,
        max_new_tokens=rc.max_new_tokens,
        temperature=rc.temperature,
        do_sample=rc.do_sample,
        seed=rc.seed,
        task_id_min=rc.task_id_min,
        task_id_max=rc.task_id_max,
        execution_timeout=rc.execution_timeout,
        results_dir=rc.results_dir,
    )
