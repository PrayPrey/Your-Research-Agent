"""Configuration module for H-E1 Cross-Benchmark Factor Analysis."""

from dataclasses import dataclass, field
from typing import Tuple


@dataclass
class DataSourceConfig:
    """Configuration for benchmark data sources."""
    truthfulqa_url: str = "https://llm-stats.com/benchmarks/truthfulqa"
    trustllm_url: str = "https://trustllmbenchmark.github.io/TrustLLM-Website/leaderboard.html"
    halubench_urls: Tuple[str, ...] = (
        "https://github.com/tianyi-lab/HaluEval",
        "https://hf.co/datasets/pminervini/HaluBench"
    )
    min_models: int = 15
    min_coverage: float = 0.6
    retry_attempts: int = 3
    timeout_seconds: int = 30


@dataclass
class PreprocessingConfig:
    """Configuration for data preprocessing."""
    standardization_method: str = "zscore"
    imputation_method: str = "em"
    max_missing_ratio: float = 0.4


@dataclass
class FactorAnalysisConfig:
    """Configuration for factor extraction."""
    random_state: int = 42
    kaiser_threshold: float = 1.0
    max_iter: int = 1000
    svd_method: str = "randomized"
    expected_n_factors: Tuple[int, int] = (2, 3)


@dataclass
class ValidationConfig:
    """Configuration for statistical validation."""
    cumulative_var_threshold: float = 0.7
    bartlett_alpha: float = 0.01
    kmo_threshold: float = 0.6
    parallel_iterations: int = 100


@dataclass
class VisualizationConfig:
    """Configuration for visualization."""
    output_dir: str = "figures/"
    dpi: int = 300
    figure_format: str = "png"
    heatmap_cmap: str = "RdBu_r"
    heatmap_vmin: float = -1.0
    heatmap_vmax: float = 1.0
    loading_threshold: float = 0.4


@dataclass
class ExportConfig:
    """Configuration for results export."""
    output_dir: str = "results/"
    data_dir: str = "data/"
    json_indent: int = 2


@dataclass
class ExperimentConfig:
    """Master configuration for H-E1 factor analysis."""
    data_sources: DataSourceConfig = field(default_factory=DataSourceConfig)
    preprocessing: PreprocessingConfig = field(default_factory=PreprocessingConfig)
    factor_analysis: FactorAnalysisConfig = field(default_factory=FactorAnalysisConfig)
    validation: ValidationConfig = field(default_factory=ValidationConfig)
    visualization: VisualizationConfig = field(default_factory=VisualizationConfig)
    export: ExportConfig = field(default_factory=ExportConfig)

    hypothesis_id: str = "h-e1"
    hypothesis_folder: str = "experiments/h-e1/"


def get_default_config() -> ExperimentConfig:
    """Factory function for default configuration."""
    return ExperimentConfig()
