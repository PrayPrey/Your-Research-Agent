# Config: h-e1

**Type**: EXISTENCE (PoC) | Format: Hardcoded dict/constants

Applied: single fixed config, no hyperparameter grid (PoC minimal config pattern)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new config design (matches architecture.md finding)
**Config Files Found**: None - new config
**Pattern Used**: module-level constants + dict (matches `config.py` in architecture)

---

## config.py

```python
# --- Data collection ---
MIN_DATE = "2019-01-01"          # FR-1.1: OpenML datasets uploaded 2019-2024
MAX_DATE = "2024-12-31"
TASK_TYPE = "Supervised Classification"  # FR-1.2

# --- Matching thresholds ---
MIN_RUNS_PER_GROUP = 10          # FR-1.3: min matched runs per (dataset, flow, setup)

# --- Statistical analysis ---
N_PERMUTATIONS = 100             # FR-6.1: null baseline permutation test
N_BOOTSTRAP = 1000                # FR-5.3: bootstrap 95% CI
RANDOM_SEED = 42

# --- Success/data-quality thresholds (NFR-1) ---
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
```

**Non-standard**: `MIN_RUNS_PER_GROUP=10` and `MIN_DATASETS=200` are hard PoC thresholds from FR-1.3/NFR-1, not tunable defaults — relax to `MIN_RUNS_PER_GROUP=5` only per PRD risk mitigation if dataset count falls short.

## Success Criteria (from PRD Section 5, used by analysis.py/baselines.py)

```python
SUCCESS_CRITERIA = {
    "relative_iqr_reduction_min": 0.20,   # ≥20%
    "absolute_iqr_reduction_min": 0.01,   # ≥0.01
    "ci_lower_bound_min": 0.10,           # 95% CI lower bound >10%
    "p_value_max": 0.05,                  # β1 significance
}
```

## Subtasks

None (budget: 0 — config.py is single low-complexity module, no decomposition needed).
