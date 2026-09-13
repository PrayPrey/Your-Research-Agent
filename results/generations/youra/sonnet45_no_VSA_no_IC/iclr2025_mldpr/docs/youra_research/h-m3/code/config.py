"""Configuration for h-m3 validation experiment."""

from pathlib import Path

# Paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
RESULTS_DIR = DATA_DIR / "results"

# Sample sizes (matching h-m2 validation report)
SAMPLE_SIZES = {
    "HF": 6500,
    "OpenML": 2990,
    "UCI": 500,
}

# Parsing rules
LICENSE_KEYWORDS = ["CC-BY", "MIT", "Apache", "GPL", "BSD", "Public Domain", "Creative Commons"]
VERSION_KEYWORDS = ["version", "v1", "v2", "release", "updated"]

# Statistical thresholds
CHI2_P_THRESHOLD = 0.10  # p > 0.10 for PASS (no friction effect)
CV_THRESHOLD = 0.20  # CV < 0.20 for stable required fields
MEAN_PRESENCE_THRESHOLD = 0.80  # Mean ≥80% for high absolute presence
CV_RATIO_THRESHOLD = 0.25  # required CV / optional CV < 0.25

# Validation
VALIDATION_SAMPLE_SIZE = 100
VALIDATION_STRATIFICATION = {"HF": 50, "OpenML": 30, "UCI": 20}
PARSING_ACCURACY_THRESHOLD = 0.85
SEMANTIC_ACCURACY_THRESHOLD = 0.80

# Random seed
RANDOM_SEED = 42

# h-m2 reference values (optional field CVs)
H_M2_OPTIONAL_CV = {
    "preprocessing_code": 2.45,  # High variance (HF 61%, OpenML/UCI 0%)
    "data_source_url": 0.50,
    "collection_date": 0.65,
}
