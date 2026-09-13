"""
Configuration for H-E1 Benchmark Data Validation Study
Generated: 2026-07-12
"""

class ValidationConfig:
    """Configuration constants for Papers with Code API data validation."""

    # API Settings
    API_BASE_URL = "https://paperswithcode.com/api/v1/"
    RATE_LIMIT = 1.0  # seconds between requests
    MAX_RETRIES = 3

    # Data Collection Filters
    TASK_FILTER = "classification"
    START_YEAR = 2019
    END_YEAR = 2024

    # Validation Criteria
    MIN_BENCHMARKS = 100  # Primary gate threshold
    MIN_RESULTS_PER_BENCHMARK = 5  # Minimum reproductions

    # Statistical Parameters (from Phase 2B)
    EFFECT_SIZE = 0.57  # Cohen's d (medium effect)
    ALPHA = 0.05  # Two-tailed significance level
    POWER = 0.80  # Statistical power (1 - beta)

    # Output Paths
    RAW_DATA_DIR = "data/raw"
    PROCESSED_DATA_DIR = "data/processed"
    FIGURES_DIR = "../figures"
    OUTPUT_FILE = "../04_validation.md"


class PlotConfig:
    """Styling configuration for visualization."""

    # Figure settings
    DPI = 300
    FIGSIZE_SINGLE = (8, 6)
    FIGSIZE_DOUBLE = (12, 5)

    # Colors
    COLOR_PASS = "green"
    COLOR_FAIL = "red"
    COLOR_WARNING = "orange"
    COLOR_PRIMARY = "#3498db"
    COLOR_SECONDARY = "#95a5a6"

    # Fonts
    FONT_SIZE_TITLE = 14
    FONT_SIZE_LABEL = 12
    FONT_SIZE_TICK = 10
