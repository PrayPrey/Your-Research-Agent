"""Fixed constants for H-E1 benchmark correlation analysis."""

# Data source
DATA_SOURCE = "open-llm-leaderboard/results"
BENCHMARKS = ["truthfulqa", "halueval", "factscore"]
BASELINE_PAIR = ("mmlu_physics", "halueval")

# Data quality thresholds (FR-1.1, NFR-3)
MIN_MODELS = 30

# Hypothesis gate threshold (FR-2.3)
CORR_UPPER_BOUND = 0.7

# Statistical validation (FR-3.2, FR-3.3)
ALPHA = 0.05
CI_LEVEL = 0.95

# Output paths
FIGURES_DIR = "figures/"
RESULTS_DIR = "results/"
