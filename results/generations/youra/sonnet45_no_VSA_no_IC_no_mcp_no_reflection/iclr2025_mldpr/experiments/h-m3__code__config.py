"""
Configuration for h-m3 citation velocity correlation detection.
LIGHT tier: Hardcoded constants for velocity spike analysis.
"""
from pathlib import Path

# Data Sources
BASE_DIR = Path(__file__).parent.parent
H1_RESULTS_PATH = BASE_DIR.parent / "h-m1" / "results" / "convergence_results.json"
H2_CITATION_CACHE = BASE_DIR / "data" / "h2_citations"
GROUND_TRUTH_PATH = BASE_DIR / "data" / "paradigm_shifts.json"

# Output Directories
OUTPUT_DIR = BASE_DIR / "results"
FIGURES_DIR = BASE_DIR / "figures"
DATA_DIR = BASE_DIR / "data"

# Benchmarks (only 3 with saturation data from h-m1)
BENCHMARKS = ["imagenet", "glue", "squad"]

# Velocity Detection Parameters
VELOCITY_WINDOW = 3  # months (rolling window for velocity computation)
SPIKE_THRESHOLD = 2.0  # σ above mean (2σ = 95% confidence)

# Correlation Parameters
CORRELATION_LEAD_TIME = 6  # months (saturation to paradigm shift)
SEARCH_WINDOW_PRE = 3  # months before saturation
SEARCH_WINDOW_POST = 6  # months after saturation

# Gate Success Criteria
TARGET_PRECISION = 0.8
TARGET_RECALL = 0.7
MIN_SAMPLE_SIZE = 3  # Reduced from 15 (only 3 benchmarks available)

# Visualization
DPI = 300
FIGSIZE = (10, 6)
