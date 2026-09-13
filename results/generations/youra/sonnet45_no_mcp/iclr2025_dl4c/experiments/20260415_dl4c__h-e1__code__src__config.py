"""
Configuration for h-e1: Execution Trace Feature Extraction
Based on 03_config.md specifications
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from pathlib import Path


@dataclass
class BenchmarkConfig:
    """Configuration for benchmark dataset loading."""
    name: str
    dataset_path: str
    problem_count: int
    test_cases_per_problem: int
    difficulty_levels: Optional[List[str]] = None


@dataclass
class ModelConfig:
    """Configuration for individual models to evaluate."""
    name: str
    organization: str
    has_humaneval: bool = True
    has_mbpp: bool = False
    has_apps: bool = False
    published_source: Optional[str] = None


@dataclass
class PublishedResultsConfig:
    """Configuration for collecting published benchmark results."""

    # Benchmark definitions
    benchmarks: List[BenchmarkConfig] = field(default_factory=lambda: [
        BenchmarkConfig(
            name="HumanEval",
            dataset_path="openai_humaneval",
            problem_count=164,
            test_cases_per_problem=10
        ),
        BenchmarkConfig(
            name="MBPP",
            dataset_path="mbpp",
            problem_count=974,
            test_cases_per_problem=3
        ),
        BenchmarkConfig(
            name="APPS",
            dataset_path="codeparrot/apps",
            problem_count=10000,
            test_cases_per_problem=20,
            difficulty_levels=["introductory", "interview", "competition"]
        )
    ])

    # Model list (23 models for EXISTENCE validation)
    models: List[ModelConfig] = field(default_factory=lambda: [
        ModelConfig("GPT-3.5-Turbo", "OpenAI", True, True, False, "OpenAI API Docs"),
        ModelConfig("GPT-4", "OpenAI", True, True, True, "OpenAI Technical Report"),
        ModelConfig("CodeLlama-7B", "Meta", True, True, False, "Rozière et al. 2023"),
        ModelConfig("CodeLlama-13B", "Meta", True, True, False, "Rozière et al. 2023"),
        ModelConfig("CodeLlama-34B", "Meta", True, True, True, "Rozière et al. 2023"),
        ModelConfig("StarCoder-15B", "BigCode", True, True, False, "Li et al. 2023"),
        ModelConfig("DeepSeek-Coder-6.7B", "DeepSeek", True, True, False, "DeepSeek AI 2024"),
        ModelConfig("DeepSeek-Coder-33B", "DeepSeek", True, True, True, "DeepSeek AI 2024"),
    ])

    results_directory: str = "data/published_results"
    output_csv: str = "outputs/collected_results.csv"
    min_models_humaneval: int = 20
    min_models_mbpp: int = 15
    min_models_apps: int = 10


@dataclass
class FeatureSchemaConfig:
    """Feature definitions and validation rules."""

    passk_values: List[int] = field(default_factory=lambda: [1, 10, 100])
    runtime_quartiles: List[float] = field(default_factory=lambda: [0.25, 0.50, 0.75])
    error_categories: List[str] = field(default_factory=lambda: ["syntax", "runtime", "timeout"])

    required_features: Dict[str, type] = field(default_factory=lambda: {
        'pass@1': float,
        'pass@10': float,
        'pass@100': float,
        'runtime_q25': float,
        'runtime_q50': float,
        'runtime_q75': float,
        'error_syntax': float,
        'error_runtime': float,
        'error_timeout': float
    })

    completeness_threshold: float = 95.0


@dataclass
class ExecutionConfig:
    """Configuration for code execution sandbox."""
    timeout_per_test: int = 30
    timeout_global: int = 3600
    use_docker: bool = False
    sandbox_python_version: str = "3.10"
    sandbox_memory_limit: str = "2GB"
    enable_runtime_collection: bool = True
    enable_error_categorization: bool = True
    max_retries_per_test: int = 1
    max_concurrent_executions: int = 4
    max_output_size_kb: int = 1024


@dataclass
class ValidationConfig:
    """Configuration for feature completeness validation."""
    completeness_threshold: float = 95.0
    check_standardization: bool = True
    check_missing_patterns: bool = True
    check_outliers: bool = True
    validation_report_path: str = "outputs/validation_report.json"
    missing_data_report_path: str = "outputs/missing_data_analysis.csv"


@dataclass
class VisualizationConfig:
    """Configuration for figure generation."""
    figures_directory: str = "figures"
    figure_dpi: int = 300
    figure_format: str = "png"

    required_figures: List[str] = field(default_factory=lambda: [
        "completeness_comparison.png",
        "feature_coverage_heatmap.png",
        "feature_distributions.png",
        "coverage_matrix.png"
    ])

    colormap: str = "viridis"
    font_size: int = 12
    title_font_size: int = 14


@dataclass
class ExperimentConfig:
    """Master configuration for h-e1 experiment pipeline."""

    published_results: PublishedResultsConfig = field(default_factory=PublishedResultsConfig)
    feature_schema: FeatureSchemaConfig = field(default_factory=FeatureSchemaConfig)
    execution: ExecutionConfig = field(default_factory=ExecutionConfig)
    validation: ValidationConfig = field(default_factory=ValidationConfig)
    visualization: VisualizationConfig = field(default_factory=VisualizationConfig)

    experiment_name: str = "h-e1-execution-trace-extraction"
    random_seed: int = 42
    output_directory: str = "outputs"
    log_level: str = "INFO"
    log_file: str = "outputs/experiment.log"
    datasets_cache_dir: str = "data/datasets_cache"
    results_directory: str = "results"


# Default configuration instance
def get_default_config() -> ExperimentConfig:
    """Returns default configuration for h-e1 experiment."""
    return ExperimentConfig()
