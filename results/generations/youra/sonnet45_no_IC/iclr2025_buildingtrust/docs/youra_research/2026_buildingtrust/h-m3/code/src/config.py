"""
Configuration for H-M3 Fisher z-Test Experiment
"""

from dataclasses import dataclass, field
import os


@dataclass
class FisherTestConfig:
    """Fisher z-test parameters"""
    alpha: float = 0.05
    confidence_level: float = 0.95
    p_threshold: float = 0.05
    delta_r_threshold: float = 0.1


@dataclass
class GateConfig:
    """SHOULD_WORK gate thresholds"""
    factual_r_threshold: float = 0.4
    misinfo_r_threshold: float = 0.3
    p_threshold: float = 0.05
    delta_r_threshold: float = 0.1


@dataclass
class ExperimentConfig:
    """Main configuration for h-m3 Fisher z-test experiment"""

    # Sub-configurations
    fisher_test: FisherTestConfig = field(default_factory=FisherTestConfig)
    gate: GateConfig = field(default_factory=GateConfig)

    # Paths
    h_m1_output_path: str = "../../h-m1/code/outputs/results.csv"
    output_dir: str = "outputs"
    figures_dir: str = "figures"

    def __post_init__(self):
        """Create output directories on initialization"""
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.figures_dir, exist_ok=True)

    def validate(self) -> bool:
        """Validate configuration completeness"""
        # Check h-m1 results file exists
        if not os.path.exists(self.h_m1_output_path):
            print(f"Error: H-M1 results not found at {self.h_m1_output_path}")
            return False

        # Validate thresholds
        if self.fisher_test.alpha <= 0 or self.fisher_test.alpha >= 1:
            print("Error: alpha must be between 0 and 1")
            return False

        if self.fisher_test.confidence_level <= 0 or self.fisher_test.confidence_level >= 1:
            print("Error: confidence_level must be between 0 and 1")
            return False

        return True


def load_config() -> ExperimentConfig:
    """Load and validate experiment configuration"""
    config = ExperimentConfig()

    if not config.validate():
        raise ValueError("Configuration validation failed")

    return config
