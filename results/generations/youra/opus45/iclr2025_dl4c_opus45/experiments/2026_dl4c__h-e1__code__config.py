"""Configuration for H-E1: Alignment-Induced Error Type Divergence experiment."""

from dataclasses import dataclass


@dataclass
class ExperimentConfig:
    """Single fixed configuration for EXISTENCE PoC experiment."""

    # Models
    rl_model_id: str = "Salesforce/codet5-large-ntp-py"
    dpo_model_id: str = "codellama/CodeLlama-7b-Instruct-hf"

    # Generation (from CodeRL paper, Le et al. 2022)
    temperature: float = 0.8
    top_p: float = 0.95
    max_new_tokens: int = 512
    n_samples: int = 1    # Reduced for feasibility (542 samples/model = 1084 total)
    seed: int = 42

    # Execution
    timeout: int = 5      # EvalPlus default (seconds)

    # Paths
    output_dir: str = "outputs"
    figures_dir: str = "figures"

    # Statistical thresholds (Phase 2B success criteria)
    chi2_p_threshold: float = 0.05
    cramers_v_threshold: float = 0.05


CONFIG = ExperimentConfig()
