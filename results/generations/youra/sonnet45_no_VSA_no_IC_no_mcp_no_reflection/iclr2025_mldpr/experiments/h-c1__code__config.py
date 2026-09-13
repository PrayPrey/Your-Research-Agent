# Configuration: Expert Consensus Validation System (h-c1)

# Data Validation
CONFIDENCE_THRESHOLD = 4  # High-confidence responses only (>=4/5)
MIN_SAMPLE_SIZE = 30  # Statistical power threshold
VALID_YEAR_RANGE = (2017, 2024)  # Saturation date bounds
BENCHMARKS = ["ImageNet", "GLUE", "SQuAD"]

# Statistical Thresholds
AGREEMENT_WINDOW_MONTHS = 12  # ±1 year from modal date
AGREEMENT_THRESHOLD = 0.70  # Primary success criterion (70%)
KAPPA_THRESHOLD = 0.60  # Fleiss' kappa threshold (substantial agreement)

# Statistical Testing
BOOTSTRAP_ITERATIONS = 1000  # 95% CI estimation
PERMUTATION_ITERATIONS = 1000  # Null hypothesis test
RANDOM_SEED = 42  # Reproducibility

# Domain Balance
MIN_DOMAIN_RATIO = 0.4
MAX_DOMAIN_RATIO = 0.6

# Visualization
OUTPUT_FORMATS = ["csv", "json", "md"]
PLOT_DPI = 150
PLOT_FORMATS = ["png"]
