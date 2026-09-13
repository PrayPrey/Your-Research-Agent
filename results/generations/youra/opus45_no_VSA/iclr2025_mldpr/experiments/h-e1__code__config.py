# Config for h-e1: Metadata Completeness vs Reproducibility Variance
# Type: EXISTENCE (PoC) | Gate: MUST_WORK

# --- Data collection ---
MIN_DATE = "2019-01-01"
MAX_DATE = "2024-12-31"
TASK_TYPE = "Supervised Classification"

# --- Matching thresholds ---
MIN_RUNS_PER_GROUP = 10

# --- Statistical analysis ---
N_PERMUTATIONS = 100
N_BOOTSTRAP = 1000
RANDOM_SEED = 42

# --- Success/data-quality thresholds ---
MIN_DATASETS = 200
MIN_TOTAL_RUNS = 5000
METADATA_SCORE_RANGE = (0, 5)

# --- Output paths ---
PATHS = {
    "raw_metadata": "data/raw/metadata.parquet",
    "matched_runs": "data/raw/matched_runs.parquet",
    "analysis": "data/processed/analysis.parquet",
    "model_results": "results/h_e1_model.json",
    "effects": "results/h_e1_effects.json",
    "figures_dir": "figures/",
}

# --- Success criteria ---
SUCCESS_CRITERIA = {
    "relative_iqr_reduction_min": 0.20,
    "absolute_iqr_reduction_min": 0.01,
    "ci_lower_bound_min": 0.10,
    "p_value_max": 0.05,
}
