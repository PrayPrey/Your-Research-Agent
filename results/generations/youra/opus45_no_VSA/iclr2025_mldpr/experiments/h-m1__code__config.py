# Config for h-m1: Preprocessing Entropy Mediation Analysis
# Type: MECHANISM | Gate: MUST_WORK

# --- Data collection ---
MIN_DATE = "2019-01-01"
MAX_DATE = "2024-12-31"
TASK_TYPE = "Supervised Classification"

# --- Matching thresholds ---
MIN_RUNS_PER_GROUP = 10

# --- Entropy binning ---
N_BINS = 10

# --- Statistical analysis ---
N_BOOTSTRAP = 1000
RANDOM_SEED = 42

# --- Data-quality thresholds ---
MIN_DATASETS = 200
METADATA_SCORE_RANGE = (0, 5)

# --- Output paths ---
PATHS = {
    "raw_metadata": "data/raw/metadata.parquet",
    "matched_runs": "data/raw/matched_runs.parquet",
    "flow_components": "data/raw/flow_components.parquet",
    "hyperparams": "data/raw/hyperparams.parquet",
    "analysis": "data/processed/analysis.parquet",
    "mediation_results": "results/h_m1_mediation.json",
    "subprediction_results": "results/h_m1_subpredictions.json",
    "figures_dir": "figures/",
}

# --- Success criteria (Primary Gate: MUST_WORK) ---
SUCCESS_CRITERIA = {
    "proportion_mediated_min": 0.30,
    "p_value_max": 0.05,
    "sobel_z_min": 1.96,
}

# --- Sub-prediction thresholds (P2a/P2b) ---
SUBPREDICTION_CRITERIA = {
    "p2a_p_value_max": 0.05,
    "p2b_p_value_min": 0.10,
}
