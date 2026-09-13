# config.py - h-c2 Low-Confidence Dispersion Analysis

# Data Validation (inverted from h-c1)
CONFIDENCE_THRESHOLD = 3  # Low-confidence: <3/5
MIN_SAMPLE_SIZE = 10
VALID_YEAR_RANGE = (2017, 2024)
BENCHMARKS = ["ImageNet", "GLUE", "SQuAD"]

# Data paths
H1_CODE_PATH = '../../h-c1/code'
SURVEY_CSV_PATH = '../data/expert_survey_responses_combined.csv'

# Dispersion calculation
DATE_FORMAT_PRIMARY = "%Y-%m"
DATE_FORMAT_FALLBACK = "%Y"
DECIMAL_YEAR_PRECISION = 2

# Gate thresholds
STD_DEV_PCT_THRESHOLD = 0.30
GATE_TYPE = "BEST_EFFORT"

# Visualization
OUTPUT_FORMATS = ["csv", "json"]
PLOT_DPI = 150
PLOT_FORMATS = ["png"]
STD_DEV_BAR_COLOR = 'steelblue'
THRESHOLD_LINE_COLOR = 'red'
THRESHOLD_LINE_STYLE = '--'

# Output paths
RESULTS_DIR = '../results'
PLOTS_DIR = '../results/plots'
RESULTS_CSV = '../results/dispersion_summary.csv'
RESULTS_JSON = '../results/dispersion_summary.json'

# Reproducibility
RANDOM_SEED = 42

# Logging
LOG_LEVEL = 'INFO'
VERBOSE = True
