"""H-M1 Configuration: Zero-Reward Basin Mechanism Analysis."""

from dataclasses import dataclass
import os


@dataclass
class HM1Config:
    """Configuration for H-M1 hypothesis validation.

    H-M1 tests the zero-reward basin mechanism:
    P(assertion | failure, RL) > P(assertion | failure, DPO)
    using one-sided Fisher's exact test.
    """

    # H-E1 data paths (relative to h-m1/code/)
    h_e1_code_dir: str = os.path.join(os.path.dirname(__file__), "..", "..", "h-e1", "code")
    h_e1_output_dir: str = os.path.join(os.path.dirname(__file__), "..", "..", "h-e1", "code", "outputs")
    rl_results_path: str = os.path.join(os.path.dirname(__file__), "..", "..", "h-e1", "code", "outputs", "rl_execution_results.json")
    dpo_results_path: str = os.path.join(os.path.dirname(__file__), "..", "..", "h-e1", "code", "outputs", "dpo_execution_results.json")
    h_e1_experiment_results_path: str = os.path.join(os.path.dirname(__file__), "..", "..", "h-e1", "code", "outputs", "experiment_results.json")
    h_e1_metrics_path: str = os.path.join(os.path.dirname(__file__), "..", "..", "h-e1", "code", "outputs", "metrics.json")

    # Output paths
    output_dir: str = os.path.join(os.path.dirname(__file__), "outputs")
    figures_dir: str = os.path.join(os.path.dirname(__file__), "figures")

    # Statistical thresholds for MUST_WORK gate
    fisher_p_threshold: float = 0.05
    alternative: str = "greater"  # One-sided: P(assertion|fail,RL) > P(assertion|fail,DPO)

    # Expected counts from H-E1 (for validation)
    expected_rl_failures: int = 236
    expected_dpo_failures: int = 530

    def __post_init__(self):
        """Normalize paths to absolute."""
        self.h_e1_code_dir = os.path.abspath(self.h_e1_code_dir)
        self.h_e1_output_dir = os.path.abspath(self.h_e1_output_dir)
        self.rl_results_path = os.path.abspath(self.rl_results_path)
        self.dpo_results_path = os.path.abspath(self.dpo_results_path)
        self.h_e1_experiment_results_path = os.path.abspath(self.h_e1_experiment_results_path)
        self.h_e1_metrics_path = os.path.abspath(self.h_e1_metrics_path)
        self.output_dir = os.path.abspath(self.output_dir)
        self.figures_dir = os.path.abspath(self.figures_dir)


CONFIG = HM1Config()
