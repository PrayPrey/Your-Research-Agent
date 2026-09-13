"""Configuration for H-E1: Static Coupling Metrics Extractor."""

from dataclasses import dataclass
from pathlib import Path


@dataclass
class ExperimentConfig:
    """Configuration for static coupling metrics extraction experiment."""

    # Dataset Configuration
    dataset_name: str = "codeparrot/codecomplex"
    language_filter: str = "Python"
    num_problems: int = 100
    min_submissions_per_problem: int = 15
    cache_path: Path = Path("./data/codenet_python/")

    # Metric Computation
    coupling_formula: str = "fan_in + fan_out"  # From Repo-Inspector
    centrality_algorithm: str = "pagerank"
    normalization_range: tuple = (0.0, 1.0)  # Min-max scaling

    # Gate Thresholds (EXISTENCE validation)
    cv_threshold: float = 0.3  # Coefficient of variation
    extraction_rate_threshold: float = 0.95
    parse_failure_tolerance: float = 0.05  # 5% max failures

    # Performance Settings
    max_processing_time: int = 1800  # 30 minutes
    memory_limit_gb: int = 8
    parallel_workers: int = 4

    # Output Paths
    results_path: Path = Path("./results/h-e1_metrics.json")
    cv_analysis_path: Path = Path("./results/h-e1_cv_analysis.json")
    figures_dir: Path = Path("./figures/")
    log_path: Path = Path("./logs/h-e1_experiment.log")

    # Logging
    log_level: str = "INFO"
    log_parse_errors: bool = True
    log_progress_interval: int = 100  # Log every N files


def validate_config(config: ExperimentConfig) -> None:
    """Validate configuration constraints."""
    assert config.num_problems > 0, "num_problems must be positive"
    assert config.min_submissions_per_problem >= 15, "min_submissions must be ≥15"
    assert 0 < config.cv_threshold < 1, "cv_threshold must be in (0, 1)"
    assert 0 < config.extraction_rate_threshold <= 1, "extraction_rate_threshold must be in (0, 1]"
    assert 0 < config.parse_failure_tolerance < 1, "parse_failure_tolerance must be in (0, 1)"
    assert config.max_processing_time > 0, "max_processing_time must be positive"
    assert config.parallel_workers > 0, "parallel_workers must be positive"

    # Create directories
    config.cache_path.mkdir(parents=True, exist_ok=True)
    config.figures_dir.mkdir(parents=True, exist_ok=True)
    config.log_path.parent.mkdir(parents=True, exist_ok=True)
    config.results_path.parent.mkdir(parents=True, exist_ok=True)
