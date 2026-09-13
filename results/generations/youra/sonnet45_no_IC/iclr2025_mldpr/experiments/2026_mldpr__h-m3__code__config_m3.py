"""
Configuration for H-M3 Performance Variance Analysis
"""

from dataclasses import dataclass


@dataclass
class VarianceStudyConfig:
    """Configuration for variance analysis study."""

    # Data Collection
    TARGET_BENCHMARK_COUNT: int = 100
    HIGH_ARTIFACT_COUNT: int = 50  # Target for high-artifact group
    LOW_ARTIFACT_COUNT: int = 50   # Target for low-artifact group
    MIN_RESULTS_PER_BENCHMARK: int = 5

    # Artifact Threshold
    HIGH_ARTIFACT_THRESHOLD: int = 2  # ≥2 artifacts = high group

    # Years
    YEAR_START: int = 2019
    YEAR_END: int = 2024

    # Task Filter
    TASK_TYPE: str = "image-classification"

    # Variance Calculation
    OUTLIER_THRESHOLD: float = 3.0  # Number of standard deviations
    MIN_SAMPLES_AFTER_FILTER: int = 5

    # Statistical Tests
    ALPHA: float = 0.05  # Significance level
    COHENS_D_THRESHOLD: float = 0.5  # Medium effect size
    SPEARMAN_RHO_THRESHOLD: float = -0.3  # Target correlation

    # Gate Conditions
    GATE_TYPE: str = "SHOULD_WORK"

    # Output Paths
    OUTPUT_DIR: str = "./outputs"
    FIGURES_DIR: str = "../figures"

    # Seed for reproducibility
    RANDOM_SEED: int = 42


# Default configuration
DEFAULT_CONFIG = VarianceStudyConfig()
