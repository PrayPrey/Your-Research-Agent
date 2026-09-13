# Config: h-c1

**Type**: CONDITION (Robustness Check) — reuses h-e1 statistical functions, adds temporal filtering

Applied: flat-module-constants pattern (matches h-e1's config.py style — module-level constants, no dataclass)

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: config classes verified from base code
**Config Files Found**: `docs/youra_research/h-e1/code/config.py` (module-level constants, not a dataclass)
**Pattern Used**: Flat module constants (dict for PATHS/thresholds) — same pattern reused for h-c1

---

## B-1..B-8: Temporal Robustness Config [Complexity: 10+6+4+6+7+5+3+6=47, Budget: 2 subtasks]

**Applied**: Standard PyTorch/scientific-computing config defaults (fixed seed, minimal iteration counts) — no KB match specific to OpenML robustness checks

### Configuration (Python module — hardcoded constants, matches h-e1 style)

```python
# config.py — h-c1: Temporal Early-Run Robustness Check

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
FULL_SAMPLE_EFFECT_PCT = 42.1   # from h-e1/results/h_e1_effects.json, loaded not recomputed
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
```

No non-standard values — all thresholds taken directly from PRD (FR-2, FR-3, FR-6) and h-e1's existing `N_BOOTSTRAP`/`RANDOM_SEED` for consistency.

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-1 | Temporal collection + filter config | Wire `MAX_RUNS_EARLY`, `MAX_DAYS_EARLY`, `PATHS["matched_runs_temporal"]`, `PATHS["early_runs"]` into `collect_temporal.py`/`filter_early.py` (covers B-1, B-2, B-3, B-4) |
| C-2 | Effect + export config | Wire `N_BOOTSTRAP`, `RANDOM_SEED`, `FULL_SAMPLE_EFFECT_PCT`, `PERSISTENCE_RATIO_MIN`, `RELATIVE_REDUCTION_MIN`, `SUCCESS_CRITERIA`, `PATHS["effects"]`/`PATHS["figures_dir"]` into `analysis.py`/`run.py` (covers B-5, B-6, B-7, B-8) |

---

## Inherited Configuration (Base Hypothesis)

### Config Constants (From Actual Code: `h-e1/code/config.py`)

h-e1 uses flat module constants, **not** a dataclass. h-c1 directly reuses two values verbatim:

```python
# From: docs/youra_research/h-e1/code/config.py (ACTUAL CODE)
N_BOOTSTRAP = 1000      # ← verified, reused as-is in h-c1
RANDOM_SEED = 42        # ← verified, reused as-is in h-c1
```

h-e1's other constants (`MIN_DATE`, `MAX_DATE`, `TASK_TYPE`, `MIN_RUNS_PER_GROUP`, `N_PERMUTATIONS`, `MIN_DATASETS`, `MIN_TOTAL_RUNS`, `METADATA_SCORE_RANGE`) are **not reused** — h-c1 defines its own temporal-specific thresholds (`MAX_RUNS_EARLY`, `MAX_DAYS_EARLY`, `MIN_DATASETS_EARLY`, `MIN_RUNS_PER_DATASET_EARLY`) per PRD FR-2/FR-3.

h-e1's `results/h_e1_effects.json` value `full_sample_effect_pct = 42.1` is loaded at runtime by `run.py` and mirrored in h-c1's `FULL_SAMPLE_EFFECT_PCT` constant (not recomputed).

**Verified from**: `docs/youra_research/h-e1/code/config.py` (actual implementation, read directly)
</content>
