# Config: h-m1 (MECHANISM - Mediation Analysis)

Applied: hardcoded-dict config module pattern (h-e1 style, module-level constants)

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (h-e1 VALIDATED)
**Status**: Config classes verified from base code — `h-e1/code/config.py` uses module-level constants (not dataclass), dict-based `PATHS`/`SUCCESS_CRITERIA`
**Config Files Found**: `docs/youra_research/h-e1/code/config.py`
**Pattern Used**: Hardcoded dict/module constants (no dataclass in base code — h-m1 follows same pattern for consistency)

---

## M-1: Config setup [Complexity: 4, Budget: 4]

**Applied**: h-e1 module-constant config pattern, extended with mediation-specific thresholds (proportion_mediated, sobel_z)

### Configuration (Module Constants / Dict)

```python
# Config for h-m1: Preprocessing Entropy Mediation Analysis
# Type: MECHANISM | Gate: MUST_WORK

# --- Data collection ---
MIN_DATE = "2019-01-01"
MAX_DATE = "2024-12-31"
TASK_TYPE = "Supervised Classification"

# --- Matching thresholds ---
MIN_RUNS_PER_GROUP = 10

# --- Entropy binning ---
N_BINS = 10  # for continuous hyperparameter discretization

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
    "p2a_p_value_max": 0.05,   # H_prep Q4 vs Q1 expected significant
    "p2b_p_value_min": 0.10,   # H_hyp Q4 vs Q1 expected NOT significant
}
```

### Subtasks [1/1 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-M1-1 | config.py | Write full module above to `h-m1/code/config.py` |

---

## M-6: Analysis Dataset Build [Data Processing Config]

**Applied**: Same `config.py` module (no separate config needed — M-6 consumes constants above)

### Relevant Fields Used by `build_analysis_dataset`
- `PATHS["matched_runs"]`, `PATHS["flow_components"]`, `PATHS["hyperparams"]` — merge inputs
- `PATHS["analysis"]` — output path
- `N_BINS` — passed to `bin_continuous()` for hyperparameter entropy
- `METADATA_SCORE_RANGE` — validates quartile split range (0-5 → quartiles via `pd.qcut`)

No additional subtask allocated — covered within M-1's config file (budget: 1 subtask total per task allocation).

---

## Inherited Configuration (Base Hypothesis)

### Config Pattern (From Actual Code)

```python
# From: docs/youra_research/h-e1/code/config.py (ACTUAL CODE)
MIN_DATE = "2019-01-01"
MAX_DATE = "2024-12-31"
MIN_RUNS_PER_GROUP = 10
N_BOOTSTRAP = 1000
RANDOM_SEED = 42
MIN_DATASETS = 200
PATHS = {...}          # dict, not dataclass
SUCCESS_CRITERIA = {...}  # dict, not dataclass
```

**Verified from**: `docs/youra_research/h-e1/code/config.py` — h-m1 is a standalone folder (no cross-import per Phase 2C), pattern replicated with mediation-specific additions (`N_BINS`, `SUBPREDICTION_CRITERIA`, `sobel_z_min`).
