"""Configuration for H-E1 MCP Trace Validation."""

from pathlib import Path

class Config:
    """Configuration constants for trace validation."""

    # Paths (will be set by main.py from command-line args)
    TRACE_FOLDER = None
    HYPOTHESIS_FOLDER = None
    FIGURES_DIR = None
    RESULTS_FILE = None

    # Validation thresholds
    COMPLETENESS_THRESHOLD = 0.95
    MIN_WORD_COUNT = 10

    # Required fields in tool call
    REQUIRED_FIELDS = ['tool_name', 'parameters', 'result']

    # Figure settings
    FIGURE_DPI = 300
    FIGURE_SIZE = (10, 6)

    @classmethod
    def setup(cls, trace_folder: str, output_folder: str):
        """Setup paths from command-line arguments."""
        cls.TRACE_FOLDER = Path(trace_folder)
        cls.HYPOTHESIS_FOLDER = Path(output_folder)
        cls.FIGURES_DIR = cls.HYPOTHESIS_FOLDER / "figures"
        cls.RESULTS_FILE = cls.HYPOTHESIS_FOLDER / "h_e1_results.json"

        # Create directories
        cls.FIGURES_DIR.mkdir(parents=True, exist_ok=True)
