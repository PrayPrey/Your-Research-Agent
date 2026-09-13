"""H-M2 Configuration: Execution Depth Analysis for RL vs DPO failures."""

from dataclasses import dataclass
import os


@dataclass
class HM2Config:
    """Configuration for H-M2 hypothesis validation.

    H-M2 tests the execution depth mechanism:
    mean_depth(RL failures) > mean_depth(DPO failures)
    using one-sided Welch's t-test.
    """

    # H-E1 data paths (relative to h-m2/code/)
    rl_results_path: str = os.path.join(
        os.path.dirname(__file__), "..", "..", "h-e1", "code", "outputs", "rl_execution_results.json"
    )
    dpo_results_path: str = os.path.join(
        os.path.dirname(__file__), "..", "..", "h-e1", "code", "outputs", "dpo_execution_results.json"
    )
    h_e1_experiment_results_path: str = os.path.join(
        os.path.dirname(__file__), "..", "..", "h-e1", "code", "outputs", "experiment_results.json"
    )
    h_e1_metrics_path: str = os.path.join(
        os.path.dirname(__file__), "..", "..", "h-e1", "code", "outputs", "metrics.json"
    )

    # Output paths
    output_dir: str = os.path.join(os.path.dirname(__file__), "outputs")
    figures_dir: str = os.path.join(os.path.dirname(__file__), "figures")

    # Statistical thresholds for SHOULD_WORK gate
    t_test_p_threshold: float = 0.05
    alternative: str = "greater"  # One-sided: mean_depth(RL) > mean_depth(DPO)

    # Execution tracing settings
    execution_timeout: float = 5.0  # seconds per sample; signal.alarm-based
    random_seed: int = 42

    # Expected counts from H-E1 (for data integrity validation)
    expected_rl_failures: int = 236
    expected_dpo_failures: int = 530

    def __post_init__(self):
        """Normalize paths to absolute."""
        self.rl_results_path = os.path.abspath(self.rl_results_path)
        self.dpo_results_path = os.path.abspath(self.dpo_results_path)
        self.h_e1_experiment_results_path = os.path.abspath(self.h_e1_experiment_results_path)
        self.h_e1_metrics_path = os.path.abspath(self.h_e1_metrics_path)
        self.output_dir = os.path.abspath(self.output_dir)
        self.figures_dir = os.path.abspath(self.figures_dir)


CONFIG = HM2Config()
