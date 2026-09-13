# Config for h-c2: Permutation Control (RandomForest-only)
# Type: CONDITION | Gate: SHOULD_WORK

import os

# Data source (reused from h-e1)
SOURCE_DATA_PATH = os.path.join(os.path.dirname(__file__), "../../h-e1/code/data/processed/analysis.parquet")
FILTER_ALGO = "RandomForest"
MIN_RF_SAMPLES = 20

# Permutation test
N_PERMUTATIONS = 1000
RANDOM_SEED = 42

# Regression formula (algo_family dropped: constant after RF filter)
FORMULA = "iqr ~ metadata_score + stability + log_popularity"
GROUP_COL = "dataset_id"

# Output paths
BASE_DIR = os.path.dirname(__file__)
PATHS = {
    "results": os.path.join(BASE_DIR, "results/h_c2_permutation.json"),
    "figures_dir": os.path.join(BASE_DIR, "figures"),
    "hist_fig": os.path.join(BASE_DIR, "figures/permutation_histogram.png"),
    "effect_fig": os.path.join(BASE_DIR, "figures/effect_comparison.png"),
}

# Success criteria
SUCCESS_CRITERIA = {
    "percentile_rank_min": 95,
    "p_value_max": 0.05,
    "effect_ratio_max": 0.05,
}
