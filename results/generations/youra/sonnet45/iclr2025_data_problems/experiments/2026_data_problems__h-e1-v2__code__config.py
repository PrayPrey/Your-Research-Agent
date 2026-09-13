# ============================================================
# H-E1-V2 Configuration — Hardcoded constants, LIGHT tier
# SCOPE_REFINEMENT of h-e1: only DATA_DIR, FIGURES_DIR, CHECKPOINT_DIR changed
# ============================================================

# --- Data Sources ---
LEADERBOARD_DATASET: str = "open-llm-leaderboard/contents"

# --- Column Definitions ---
# Raw leaderboard column names (v2 dataset — open-llm-leaderboard/contents)
BENCHMARK_COLS_RAW: list = [
    "IFEval",
    "BBH",
    "MATH Lvl 5",
    "GPQA",
    "MUSR",
    "MMLU-PRO",
]

# Normalized column names (used in registry_df and downstream analysis)
BENCHMARK_COLS: list = [
    "ifeval",
    "bbh",
    "math_lvl5",
    "gpqa",
    "musr",
    "mmlu_pro",
]

FEATURE_COLS: list = [
    "dedup_documented",
    "perplexity_filter_documented",
    "domain_composition_documented",
    "decontamination_documented",
]

# --- Keyword Regex Patterns (pre-registered, do NOT modify post-run) ---
# These patterns are fixed before data collection to prevent HARKing.
REGEX_PATTERNS: dict = {
    "dedup_documented": r"dedup|near.?dup|minhash|exact.?dedup",
    "perplexity_filter_documented": r"perplexity.{0,20}filter|ppl.{0,10}filter",
    "domain_composition_documented": r"domain.{0,30}(%|percent|composition)|data.{0,30}mix",
    "decontamination_documented": r"decontaminat|n.?gram.{0,20}overlap|benchmark.{0,20}holdout",
}

# --- Architecture Family Patterns ---
ARCH_FAMILY_PATTERNS: dict = {
    "LLaMA": r"llama|llama2|llama-2",
    "Mistral": r"mistral|mixtral",
    "Falcon": r"falcon",
    "Pythia": r"pythia|eleuther",
    "OLMo": r"olmo",
    # Models not matching any pattern → assigned "Other"
}

# --- Parameter Count Map (hardcoded fallback) ---
PARAM_COUNT_MAP: dict = {
    r"llama.*7b": 7e9,
    r"llama.*13b": 13e9,
    r"llama.*70b": 70e9,
    r"falcon.*7b": 7e9,
    r"falcon.*40b": 40e9,
    r"mistral.*7b": 7e9,
    r"pythia.*1b": 1e9,
    r"pythia.*7b": 7e9,
    r"pythia.*12b": 12e9,
}

# --- Gate Thresholds ---
MIN_BENCHMARK_COVERAGE: int = 4    # min non-null benchmark scores to retain a model
MIN_REGISTRY_SIZE: int = 200       # MUST_WORK gate: n_analyzable >= 200
MIN_FEATURES_WITH_VARIANCE: int = 3  # MUST_WORK gate: >=3 of 4 features have variance > 0

# --- API / Checkpointing ---
API_BACKOFF_BASE: float = 2.0   # exponential backoff base (seconds)
API_MAX_RETRIES: int = 5        # max retries per HF API call
CHECKPOINT_INTERVAL: int = 100  # save checkpoint every N models retrieved

# --- Reproducibility ---
RANDOM_STATE: int = 42

# --- Output Paths (CHANGED from h-e1) ---
DATA_DIR: str = "h-e1-v2/data"
FIGURES_DIR: str = "h-e1-v2/figures"
CHECKPOINT_DIR: str = "h-e1-v2/data/checkpoints"

# ============================================================
# Statistical Analysis Parameters
# ============================================================

# --- OLS Formula Specifications ---
# Dependent variable: avg_score (Average of 6 v2 benchmarks)
# Baseline: scale controls only (no documentation signal)
OLS_FORMULA_BASELINE: str = (
    "avg_score ~ log_params + log_tokens + C(arch_family)"
)

# Proposed: adds doc_score (sum of 4 binary curation features, 0-4)
OLS_FORMULA_PROPOSED: str = (
    "avg_score ~ log_params + log_tokens + doc_score + C(arch_family)"
)

# --- Inference Parameters ---
ALPHA: float = 0.05          # significance level for beta_docs p-value test
PERMUTATION_SAMPLES: int = 1000  # permutation test iterations for delta_R2 null distribution
POWER_TARGET: float = 0.80   # minimum acceptable statistical power (informational, not a gate)
