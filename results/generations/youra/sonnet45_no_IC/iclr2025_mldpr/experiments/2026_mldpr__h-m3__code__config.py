"""
Configuration for H-M2 Protocol Consistency Study
Generated: 2026-07-12
"""

from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class ProtocolStudyConfig:
    """Master configuration for protocol consistency observational study."""

    # API Settings (inherited from H-M1)
    PWC_API_URL: str = "https://paperswithcode.com/api/v1/"
    S2_API_URL: str = "https://api.semanticscholar.org/v1/"
    RATE_LIMIT: float = 1.0
    MAX_RETRIES: int = 3
    TIMEOUT: int = 30

    # Sampling Parameters
    BENCHMARK_COUNT: int = 10
    PAPERS_PER_BENCHMARK: int = 5
    INTER_RATER_SAMPLE_SIZE: int = 10

    # Protocol Dimensions (from H-M1 rubric)
    PROTOCOL_DIMENSIONS: List[str] = field(default_factory=lambda: [
        "data_splits", "preprocessing", "evaluation_protocol", "hyperparameters"
    ])

    # Gate Thresholds
    MIN_KAPPA: float = 0.8
    PRIMARY_THRESHOLD: float = 0.70
    SECONDARY_RHO_THRESHOLD: float = 0.4
    SECONDARY_P_THRESHOLD: float = 0.05

    # Quality Stratification
    QUALITY_STRATA: Dict[str, tuple] = field(default_factory=lambda: {
        "High": (7.0, 10.0),
        "Medium": (4.0, 7.0),
        "Low": (0.0, 4.0)
    })

    # Consistency Definition
    MIN_DIMENSIONS_IDENTICAL: int = 3

    # Paths (H-M1 dependency)
    H_M1_QUALITY_FILE: str = "../../h-m1/code/outputs/artifact_quality.csv"

    # Data Directories
    RAW_PAPERS_DIR: str = "data/citing_papers"
    BENCHMARK_SPECS_DIR: str = "data/benchmark_specs"

    # Output Paths
    SELECTED_BENCHMARKS_FILE: str = "data/selected_benchmarks.csv"
    PROTOCOL_CODING_FILE: str = "data/protocol_coding.csv"
    RATER_VALIDATION_DIR: str = "data/rater_validation"
    CONSISTENCY_RESULTS_FILE: str = "results/consistency_by_stratum.csv"
    HYPOTHESIS_TEST_FILE: str = "results/hypothesis_test.json"
    FIGURES_DIR: str = "../figures"
    OUTPUT_FILE: str = "../04_validation.md"


@dataclass
class PlotConfig:
    """Visualization styling configuration (inherited from H-M1)."""

    DPI: int = 300
    FIGSIZE_SINGLE: tuple = (8, 6)
    FIGSIZE_DOUBLE: tuple = (12, 5)

    COLOR_PASS: str = "green"
    COLOR_FAIL: str = "red"
    COLOR_WARNING: str = "orange"
    COLOR_PRIMARY: str = "#3498db"
    COLOR_SECONDARY: str = "#95a5a6"

    FONT_SIZE_TITLE: int = 14
    FONT_SIZE_LABEL: int = 12
    FONT_SIZE_TICK: int = 10
