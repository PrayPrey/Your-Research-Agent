"""Experiment Configuration for H-E1 Data Extraction

This module defines configuration constants for the data extraction experiment,
including model families, benchmarks, report URLs, and success thresholds.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Union
from pathlib import Path


@dataclass
class ExperimentConfig:
    """Configuration for H-E1 data extraction experiment."""

    # Model families to analyze
    MODEL_FAMILIES: List[str] = field(default_factory=lambda: ["GPT", "Claude", "Llama"])

    # Benchmarks to extract
    BENCHMARKS: List[str] = field(default_factory=lambda: ["TruthfulQA", "MMLU"])

    # Timepoints to compare
    TIMEPOINTS: List[str] = field(default_factory=lambda: ["baseline", "current"])

    # Technical report URLs (updated URLs for 2024)
    REPORT_URLS: Dict[str, Dict[str, str]] = field(default_factory=lambda: {
        "GPT": {
            "baseline": "https://arxiv.org/pdf/2303.08774.pdf",  # GPT-4 technical report
            "current": "https://cdn.openai.com/papers/gpt-4-system-card.pdf"
        },
        "Claude": {
            "baseline": "https://www-cdn.anthropic.com/files/4zrzovbb/website/1adf000c8f675958c2ee23805d91aaade1cd4613-claude_2_model_card.pdf",
            "current": "https://www-cdn.anthropic.com/de8ba9b01c9ab7cbabf5c33b80b7bbc618857627/Model_Card_Claude_3.pdf"
        },
        "Llama": {
            "baseline": "https://arxiv.org/pdf/2307.09288.pdf",  # Llama 2
            "current": "https://arxiv.org/pdf/2407.21783.pdf"     # Llama 3
        }
    })

    # Success thresholds for gate condition
    SUCCESS_THRESHOLDS: Dict[str, Union[int, float]] = field(default_factory=lambda: {
        "min_families": 3,        # Minimum model families with data
        "min_categories": 10,     # Minimum categories per benchmark
        "min_completeness": 90.0  # Minimum data completeness percentage
    })

    # Output schema
    OUTPUT_SCHEMA: List[str] = field(default_factory=lambda: [
        "model_family", "timepoint", "benchmark", "category", "error_rate"
    ])

    # Directory paths (will be set at runtime)
    data_dir: Path = field(default_factory=lambda: Path("data"))
    reports_dir: Path = field(default_factory=lambda: Path("data/reports"))
    extracted_dir: Path = field(default_factory=lambda: Path("data/extracted"))
    figures_dir: Path = field(default_factory=lambda: Path("figures"))
    logs_dir: Path = field(default_factory=lambda: Path("logs"))


@dataclass
class VisualizationConfig:
    """Configuration for figure generation."""

    # Figure sizes (width, height in inches)
    DEFAULT_FIGSIZE: tuple = (10, 6)
    HEATMAP_FIGSIZE: tuple = (12, 8)
    TIMELINE_FIGSIZE: tuple = (14, 4)

    # DPI for publication quality
    DPI: int = 300

    # Color schemes
    COLORS: Dict[str, str] = field(default_factory=lambda: {
        "primary": "#2E86AB",
        "secondary": "#A23B72",
        "success": "#06A77D",
        "warning": "#F18F01",
        "error": "#C73E1D"
    })

    # Output format
    OUTPUT_FORMAT: str = "png"


@dataclass
class TestConfig:
    """Configuration for testing and validation."""

    # Mock data parameters for testing
    MOCK_FAMILIES: int = 3
    MOCK_TIMEPOINTS: int = 2
    MOCK_TRUTHFULQA_CATEGORIES: int = 12
    MOCK_MMLU_CATEGORIES: int = 15

    # Validation thresholds
    MIN_FAMILIES: int = 3
    MIN_CATEGORIES: int = 10
    MIN_COMPLETENESS: float = 90.0

    # Test mode flag
    USE_MOCK_DATA: bool = False


@dataclass
class IntegrationConfig:
    """Configuration for end-to-end pipeline integration."""

    # Pipeline stages
    PIPELINE_STAGES: List[str] = field(default_factory=lambda: [
        "setup",
        "collect",
        "parse",
        "validate",
        "metrics",
        "visualize",
        "save"
    ])

    # Retry configuration
    MAX_RETRIES: int = 3
    RETRY_DELAY: int = 2  # seconds

    # Logging configuration
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/extraction.log"

    # File operations
    ATOMIC_WRITE: bool = True  # Use temp file + rename for atomic writes


def get_config() -> ExperimentConfig:
    """Get default experiment configuration."""
    return ExperimentConfig()


def get_visualization_config() -> VisualizationConfig:
    """Get default visualization configuration."""
    return VisualizationConfig()


def get_test_config() -> TestConfig:
    """Get default test configuration."""
    return TestConfig()


def get_integration_config() -> IntegrationConfig:
    """Get default integration configuration."""
    return IntegrationConfig()
