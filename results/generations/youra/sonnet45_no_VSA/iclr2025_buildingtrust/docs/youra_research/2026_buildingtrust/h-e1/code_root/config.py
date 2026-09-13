"""Configuration module for H-E1 Cross-Benchmark Rank Correlation Analysis."""

from dataclasses import dataclass, field
from typing import List


@dataclass
class DataSourceConfig:
    """Configuration for benchmark data sources."""
    trustllm_url: str = "https://trustllmbenchmark.github.io/TrustLLM-Website/leaderboard.html"
    multitrust_repo: str = "https://github.com/thu-ml/MMTrustEval"
    fintrust_source: str = "TBD"
    hf_dataset: str = "TrustLLM/TrustLLM-dataset"
    min_overlap: int = 10
    retry_attempts: int = 3
    retry_backoff: float = 2.0
    timeout_seconds: int = 30


@dataclass
class ScrapingConfig:
    """Configuration for web scraping."""
    user_agent: str = "Mozilla/5.0 (compatible; ResearchBot/1.0)"
    parser: str = "html.parser"
    verify_ssl: bool = True


@dataclass
class PreprocessingConfig:
    """Configuration for data preprocessing."""
    min_model_overlap: int = 10
    score_column: str = "overall_score"
    ranking_method: str = "average"
    ascending: bool = False
    handle_ties: str = "average"


@dataclass
class StatisticalConfig:
    """Configuration for statistical correlation analysis."""
    significance_level: float = 0.01
    target_rho_min: float = 0.3
    target_rho_max: float = 0.6
    scalar_threshold: float = 0.8
    random_threshold: float = 0.1
    nan_policy: str = "omit"
    alternative: str = "two-sided"
    min_success_count: int = 2


@dataclass
class VisualizationConfig:
    """Configuration for visualization output."""
    output_dir: str = "figures/"
    dpi: int = 300
    figure_format: str = "png"
    heatmap_figsize: tuple = (8, 6)
    heatmap_cmap: str = "RdYlGn"
    heatmap_vmin: float = -1.0
    heatmap_vmax: float = 1.0
    heatmap_center: float = 0.0
    heatmap_annot: bool = True
    heatmap_fmt: str = ".2f"
    scatter_figsize: tuple = (6, 6)
    scatter_alpha: float = 0.6
    scatter_color: str = "#3498db"
    scatter_marker: str = "o"
    scatter_s: int = 100
    bar_figsize: tuple = (10, 6)
    bar_colors: List[str] = field(default_factory=lambda: ["#2ecc71", "#e74c3c"])
    bar_width: float = 0.35
    significance_markers: dict = field(default_factory=lambda: {
        0.001: "***",
        0.01: "**",
        0.05: "*"
    })


@dataclass
class ExportConfig:
    """Configuration for results export."""
    output_dir: str = "results/"
    json_indent: int = 2
    json_ensure_ascii: bool = False
    console_output: bool = True


@dataclass
class ExperimentConfig:
    """Master experiment configuration for H-E1."""
    data_sources: DataSourceConfig = field(default_factory=DataSourceConfig)
    scraping: ScrapingConfig = field(default_factory=ScrapingConfig)
    preprocessing: PreprocessingConfig = field(default_factory=PreprocessingConfig)
    statistics: StatisticalConfig = field(default_factory=StatisticalConfig)
    visualization: VisualizationConfig = field(default_factory=VisualizationConfig)
    export: ExportConfig = field(default_factory=ExportConfig)

    hypothesis_id: str = "h-e1"
    hypothesis_folder: str = "experiments/h-e1/"
    seed: int = 42


def get_default_config() -> ExperimentConfig:
    """Factory function for default configuration."""
    return ExperimentConfig()
