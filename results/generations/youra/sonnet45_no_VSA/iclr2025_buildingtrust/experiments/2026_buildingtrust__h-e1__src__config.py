"""Configuration for H-E1: CV-Stability Meta-Analysis"""
from dataclasses import dataclass, field
from typing import List


@dataclass
class VisualizationConfig:
    """Configuration for all 4 required visualizations."""

    # Output settings
    output_dir: str = "figures/"
    dpi: int = 300
    figure_format: str = "png"

    # Scatter plot (CV vs mean rho)
    scatter_figsize: tuple = (8, 6)
    scatter_marker: str = "o"
    scatter_s: int = 120
    scatter_color: str = "#3498db"
    scatter_alpha: float = 0.7
    scatter_edgecolor: str = "black"
    scatter_linewidth: float = 0.5
    regression_color: str = "#e74c3c"
    regression_linewidth: float = 2.0
    ci_alpha: float = 0.2
    annotation_fontsize: int = 11

    # Bar chart (per-benchmark CV and rho)
    bar_figsize: tuple = (10, 6)
    bar_width: float = 0.35
    bar_colors: List[str] = field(default_factory=lambda: ["#3498db", "#e67e22"])
    bar_edgecolor: str = "black"
    bar_linewidth: float = 0.8

    # Heatmap (pairwise rho matrix)
    heatmap_figsize: tuple = (10, 8)
    heatmap_cmap: str = "RdYlGn"
    heatmap_vmin: float = -1.0
    heatmap_vmax: float = 1.0
    heatmap_center: float = 0.0
    heatmap_annot: bool = True
    heatmap_fmt: str = ".2f"
    heatmap_linewidths: float = 0.5
    heatmap_linecolor: str = "gray"
    heatmap_cbar_label: str = "Spearman ρ"

    # Gate comparison chart
    gate_figsize: tuple = (8, 5)
    gate_bar_width: float = 0.4
    gate_target_color: str = "#95a5a6"
    gate_actual_pass_color: str = "#2ecc71"
    gate_actual_fail_color: str = "#e74c3c"
    gate_edgecolor: str = "black"
    gate_linewidth: float = 1.0
    gate_threshold_linestyle: str = "--"
    gate_threshold_color: str = "red"
    gate_threshold_linewidth: float = 2.0


@dataclass
class StatisticalConfig:
    """Configuration for statistical analysis parameters."""

    # Validation thresholds
    min_models: int = 10
    min_shared_models: int = 5

    # Hypothesis test settings
    alpha: float = 0.05
    alternative: str = "two-sided"

    # Gate criteria
    target_pearson_r: float = -0.5
    target_p_value: float = 0.05

    # CV computation
    cv_ddof: int = 1


@dataclass
class DataExtractionConfig:
    """Configuration for benchmark data extraction."""

    # Data sources
    trustllm_url: str = "https://trustllmbenchmark.github.io/TrustLLM-Website/leaderboard.html"
    truthfulqa_repo: str = "https://github.com/sylinrl/TruthfulQA"

    # Scraping settings
    timeout_seconds: int = 30
    retry_attempts: int = 3
    retry_backoff: float = 2.0
    user_agent: str = "Mozilla/5.0 (compatible; ResearchBot/1.0)"
    parser: str = "html.parser"
    verify_ssl: bool = True

    # Validation
    min_benchmarks: int = 5
    max_missing_fraction: float = 0.2


@dataclass
class ExperimentConfig:
    """Master configuration for H-E1 meta-analysis."""

    visualization: VisualizationConfig = field(default_factory=VisualizationConfig)
    statistics: StatisticalConfig = field(default_factory=StatisticalConfig)
    data_extraction: DataExtractionConfig = field(default_factory=DataExtractionConfig)

    # Experiment metadata
    hypothesis_id: str = "h-e1"
    output_dir: str = "."
    seed: int = 42

    # Output paths
    results_dir: str = "results/"
    figures_dir: str = "figures/"
    data_dir: str = "data/"
    logs_dir: str = "logs/"


def get_default_config() -> ExperimentConfig:
    """Factory function for default H-E1 configuration."""
    return ExperimentConfig()
