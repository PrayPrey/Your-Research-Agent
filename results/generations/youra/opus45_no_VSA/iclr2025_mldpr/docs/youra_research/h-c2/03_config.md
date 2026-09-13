# Config: h-c2 (Permutation Control)

**Type**: CONDITION (EXISTENCE-style, minimal) | **Gate**: SHOULD_WORK | **Format**: Hardcoded module-level constants (matches h-e1 pattern)

Applied: Freedman-Lane residual permutation test config (single fixed protocol, no hyperparameter grid)

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (h-e1)
**Status**: Config classes verified from base code — h-e1 uses hardcoded constants, NOT dataclass
**Config Files Found**: `h-e1/code/config.py`
**Pattern Used**: Hardcoded module-level constants (dict for grouped values)

---

## A-1: config.py [Complexity: 4, Budget: 0 subtasks]

**Applied**: Freedman-Lane permutation test — single fixed config, no tuning (statistical analysis, not DL)

### Configuration (Hardcoded constants)

```python
# Config for h-c2: Permutation Control (RandomForest-only)
# Type: CONDITION | Gate: SHOULD_WORK

# --- Data source (reused from h-e1) ---
SOURCE_DATA_PATH = "../h-e1/code/data/processed/analysis.parquet"
FILTER_ALGO = "RandomForest"
MIN_RF_SAMPLES = 20  # minimum rows after filtering to proceed

# --- Permutation test ---
N_PERMUTATIONS = 1000
RANDOM_SEED = 42

# --- Regression formula (algo_family term dropped: constant after RF filter) ---
FORMULA = "iqr ~ metadata_score + stability + log_popularity"
GROUP_COL = "dataset_id"

# --- Output paths ---
PATHS = {
    "results": "results/h_c2_permutation.json",
    "figures_dir": "figures/",
    "hist_fig": "figures/permutation_histogram.png",
    "effect_fig": "figures/effect_comparison.png",
}

# --- Success criteria ---
SUCCESS_CRITERIA = {
    "percentile_rank_min": 95,
    "p_value_max": 0.05,
    "effect_ratio_max": 0.05,
}
```

No subtasks (budget=0, EXISTENCE-style single fixed config).

---

## Inherited Configuration (Base Hypothesis h-e1)

### Reused Fields (Verified from Actual Code)

```python
# From: h-e1/code/config.py (ACTUAL CODE)
RANDOM_SEED = 42          # reused as-is
N_PERMUTATIONS = 100      # h-e1 default; h-c2 overrides to 1000 per PRD FR-3
PATHS = {...}             # pattern reused, paths repointed to h-c2/
SUCCESS_CRITERIA = {...}  # pattern reused, thresholds redefined per h-c2 PRD
```

**Note**: h-e1's `analysis.parquet` columns (`iqr`, `metadata_score`, `stability`, `log_popularity`, `algo_family`, `dataset_id`) are consumed directly — no schema translation needed. h-c2 does not inherit `MIN_DATASETS`, `MIN_TOTAL_RUNS`, `N_BOOTSTRAP`, or `METADATA_SCORE_RANGE` (not applicable to permutation-only analysis).

**Verified from**: `h-e1/code/config.py` (actual implementation, module-level constants — not a dataclass)
