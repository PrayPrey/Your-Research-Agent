"""
Configuration for H-M1 Artifact Quality Assessment Study
Generated: 2026-07-12
"""

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class QualityStudyConfig:
    """Configuration for artifact quality assessment observational study."""

    # API Settings
    API_BASE_URL: str = "https://paperswithcode.com/api/v1/"
    RATE_LIMIT: float = 1.0
    MAX_RETRIES: int = 3
    TIMEOUT: int = 30

    # Sampling Parameters
    SAMPLE_SIZE: int = 20
    STRATIFICATION: Dict[str, int] = field(default_factory=lambda: {"CV": 10, "NLP": 10})
    START_YEAR: int = 2019
    END_YEAR: int = 2024
    MIN_ARTIFACT_COUNT: int = 2

    # Rubric Dimensions
    RUBRIC_DIMENSIONS: List[str] = field(default_factory=lambda: [
        "preprocessing", "data_splits", "evaluation_protocol", "hyperparameters"
    ])
    SCORE_LEVELS: List[int] = field(default_factory=lambda: [0, 5, 10])

    # Gate Thresholds
    MIN_KAPPA: float = 0.8
    MIN_QUALITY: float = 7.0

    # Output Paths
    RAW_DATA_DIR: str = "data/raw"
    ARTIFACTS_DIR: str = "data/artifacts"  # For retrieved GitHub artifacts
    ARTIFACT_CONTENT_DIR: str = "data/artifacts"
    RATER_SCORES_DIR: str = "data/scores"
    RESULTS_DIR: str = "outputs"
    FIGURES_DIR: str = "../figures"
    OUTPUT_FILE: str = "../04_validation.md"


class PlotConfig:
    """Styling configuration for visualization."""

    DPI = 300
    FIGSIZE_SINGLE = (8, 6)
    FIGSIZE_DOUBLE = (12, 5)

    COLOR_PASS = "green"
    COLOR_FAIL = "red"
    COLOR_WARNING = "orange"
    COLOR_PRIMARY = "#3498db"
    COLOR_SECONDARY = "#95a5a6"

    FONT_SIZE_TITLE = 14
    FONT_SIZE_LABEL = 12
    FONT_SIZE_TICK = 10
