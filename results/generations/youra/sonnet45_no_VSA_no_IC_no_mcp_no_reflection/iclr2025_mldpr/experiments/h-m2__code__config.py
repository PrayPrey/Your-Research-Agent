"""
Configuration for h-m2 temporal lead time validation.
LIGHT tier: Hardcoded constants for citation analysis.
"""
from pathlib import Path

# Data Sources
BASE_DIR = Path(__file__).parent.parent
H1_RESULTS_PATH = BASE_DIR / "data" / "convergence_results.json"
DATA_DIR = BASE_DIR / "data"
CACHE_DIR = DATA_DIR / "citations"

# Output Directories
OUTPUT_DIR = BASE_DIR / "results"
FIGURES_DIR = BASE_DIR / "figures"

# Paradigm Shift Papers (Semantic Scholar IDs)
PAPERS = {
    'gpt3': 'e0d2a0e9f3f4c4e4d1d3c4f3e3e1d0a0e9f3f4c4',  # Placeholder - use actual S2 ID
    'vit': 'd0a0e9f3f4c4e4d1d3c4f3e3e1d0a0e9f3f4c4e4',   # Placeholder - use actual S2 ID
    'llama': 'f4c4e4d1d3c4f3e3e1d0a0e9f3f4c4e4d1d3c4'     # Placeholder - use actual S2 ID
}

# Benchmark-Shift Mapping
BENCHMARK_SHIFT_PAIRS = [
    ('imagenet', 'vit'),
    ('glue', 'gpt3'),
    ('squad', 'gpt3')
]

# Semantic Scholar API
RATE_LIMIT = (100, 300)  # 100 requests per 300 seconds

# Adoption Detection
ADOPTION_THRESHOLD = 50  # citations/month
ADOPTION_WINDOW = 3  # months sustained

# Lead Time Analysis
LEAD_TIME_THRESHOLD = 6  # months
PRECEDE_FRACTION_TARGET = 0.6  # 60% must precede

# Statistical Validation
SIGNIFICANCE_LEVEL = 0.05
PERMUTATION_ITERATIONS = 1000
RANDOM_SEED = 42

# Visualization
DPI = 300
FIGSIZE = (10, 6)
