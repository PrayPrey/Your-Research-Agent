# Config for h-c1: Temporal Early-Run Robustness Check
# Type: CONDITION (Robustness Check) | Gate: SHOULD_WORK

# --- Temporal filter thresholds (FR-2) ---
MAX_RUNS_EARLY = 50
MAX_DAYS_EARLY = 90

# --- Sample size validation (FR-3) ---
MIN_DATASETS_EARLY = 100
MIN_RUNS_PER_DATASET_EARLY = 5

# --- Statistical analysis (reuse h-e1 settings) ---
N_BOOTSTRAP = 1000
RANDOM_SEED = 42

# --- Effect persistence comparison (FR-6) ---
FULL_SAMPLE_EFFECT_PCT = 42.1   # from h-e1/results/h_e1_effects.json
PERSISTENCE_RATIO_MIN = 0.5
RELATIVE_REDUCTION_MIN = 0.20

# --- Output paths ---
PATHS = {
    "matched_runs_temporal": "data/raw/matched_runs_temporal.parquet",
    "early_runs": "data/processed/early_runs.parquet",
    "effects": "results/h_c1_effects.json",
    "figures_dir": "figures/",
}

# --- Success criteria (mirrors PRD thresholds) ---
SUCCESS_CRITERIA = {
    "relative_iqr_reduction_min": 0.20,
    "persistence_ratio_min": 0.5,
    "p_value_max": 0.05,
}
