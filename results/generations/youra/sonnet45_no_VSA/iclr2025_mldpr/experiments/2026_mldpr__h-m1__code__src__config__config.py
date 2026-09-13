"""Configuration Module

Centralized configuration for H-M1 experiment.
"""

from dataclasses import dataclass, field
from typing import Optional
from pathlib import Path


@dataclass
class GitHubConfig:
    """GitHub API configuration."""
    token: Optional[str] = None  # GitHub Personal Access Token (optional, but recommended)
    max_retries: int = 3
    rate_limit_wait: int = 60  # seconds


@dataclass
class DataConfig:
    """Data loading and processing configuration."""
    h_e1_results_path: str = "../h-e1/code/outputs/results.csv"
    output_dir: str = "outputs"
    figures_dir: str = "figures"
    cache_dir: str = ".cache"


@dataclass
class ValidationConfig:
    """Data validation configuration."""
    quality_threshold: float = 0.95  # Minimum completeness ratio
    z_threshold: float = 3.0  # Z-score threshold for outlier detection
    min_sample_size: int = 50  # Minimum required sample size


@dataclass
class AnalysisConfig:
    """Statistical analysis configuration."""
    random_seed: int = 42
    one_tailed_test: bool = True  # H1: positive correlation
    alpha: float = 0.05  # Significance level
    bootstrap_iterations: int = 10000
    bootstrap_confidence: float = 0.95


@dataclass
class GateConfig:
    """Gate checking configuration."""
    primary_threshold: float = 0.30  # Spearman ρ threshold
    secondary_threshold: float = 0.25  # Partial correlation ρ threshold
    alpha: float = 0.05  # Significance level


@dataclass
class ExperimentConfig:
    """Main experiment configuration."""
    github: GitHubConfig = field(default_factory=GitHubConfig)
    data: DataConfig = field(default_factory=DataConfig)
    validation: ValidationConfig = field(default_factory=ValidationConfig)
    analysis: AnalysisConfig = field(default_factory=AnalysisConfig)
    gate: GateConfig = field(default_factory=GateConfig)

    def __post_init__(self):
        """Create output directories if they don't exist."""
        Path(self.data.output_dir).mkdir(parents=True, exist_ok=True)
        Path(self.data.figures_dir).mkdir(parents=True, exist_ok=True)
        Path(self.data.cache_dir).mkdir(parents=True, exist_ok=True)
