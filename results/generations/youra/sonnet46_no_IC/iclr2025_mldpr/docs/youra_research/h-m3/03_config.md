# Configuration: H-M3 — Categorical Tag Count Dose-Response (NB-2 Monotonic Gate)

Applied: H-E1 flat-script module-level constants pattern (verified from actual code)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (extending H-E1)
**Status**: Config constants verified from actual H-E1 code
**Config Files Found**: `h-e1/code/01_preprocess.py`, `h-e1/code/02_fit_models.py`, `h-e1/code/04_evaluate_gate.py`
**Pattern Used**: module-level ALL_CAPS constants (matching H-E1 pattern exactly)

---

## Inherited Configuration (Base Hypothesis: H-E1)

Constants verified from actual H-E1 code (not specs):

```python
# From: docs/youra_research/h-e1/code/01_preprocess.py
BASE_DIR        = "docs/youra_research/h-e1"
EXPECTED_N      = 5217
REFERENCE_YEAR  = 2026

# From: docs/youra_research/h-e1/code/02_fit_models.py
NB2_METHOD      = "bfgs"
NB2_MAXITER     = 100         # H-M3 increases this to 200 per PRD NFR-01
NB2_DISP        = False
_CONTROLS       = "log_n_instances + log_n_features + age_years + age_sq + C(decade)"

# From: docs/youra_research/h-e1/code/04_evaluate_gate.py
GATE_PVAL_MAX   = 0.05
```

**Verified from**: `docs/youra_research/h-e1/code/` (actual implementation)

---

## A-10: Integration Test & End-to-End Run [Complexity: 9, Budget: 1 subtask]

### C-10-1: Integration Test Configuration

```python
# === 01_preprocess.py constants ===
BASE_DIR          = "docs/youra_research/h-m3"
H_E1_PARQUET      = "docs/youra_research/h-e1/results/preprocessed.parquet"
H_E1_CSV_FALLBACK = "docs/youra_research/h-e1/code/data/h_e1/openml_dataset_corpus.csv"
PREPROCESSED_OUT  = f"{BASE_DIR}/results/preprocessed.parquet"
EXPECTED_N        = 5217
REFERENCE_YEAR    = 2026

# Bin boundaries
BIN_BREAKS = [-1, 0, 2, 5, float('inf')]
BIN_LABELS  = ["0", "1-2", "3-5", "6+"]

# Expected bin "0" count (±100 tolerance acceptable)
EXPECTED_BIN0_COUNT     = 2592
EXPECTED_BIN0_TOLERANCE = 100

# === 02_fit_models.py constants ===
PREPROCESSED  = f"{BASE_DIR}/results/preprocessed.parquet"
MODEL_RESULTS = f"{BASE_DIR}/results/model_results.json"

_CONTROLS        = "log_n_instances + log_n_features + age_years + age_sq + C(decade)"
FORMULA_BASELINE = f"N_tasks ~ {_CONTROLS}"
FORMULA_BINARY   = f"N_tasks ~ has_tags + {_CONTROLS}"
FORMULA_CAT      = f"N_tasks ~ C(tag_count_cat) + {_CONTROLS}"
FORMULA_RC6      = f"N_tasks ~ C(tag_count_cat)*C(decade) + log_n_instances + log_n_features + age_years + age_sq"
FORMULA_RC7      = f"N_tasks ~ C(tag_count_cat) + log_n_instances + log_n_features + age_years + age_sq"

NB2_METHOD  = "bfgs"
NB2_MAXITER = 200   # Non-standard: increased from H-E1's 100; RC-6 decade×category interaction needs more iterations
NB2_DISP    = False

BONF_ALPHA = 0.0167   # Bonferroni α/3 for 3 adjacent contrasts

# === 03_generate_figures.py constants ===
FIGURES_DIR   = f"{BASE_DIR}/figures"
FIGURE_DPI    = 300
FIGURE_FORMAT = "png"

FIG1_SIZE = (8, 5)
FIG2_SIZE = (8, 5)
FIG3_SIZE = (8, 5)
FIG4_SIZE = (10, 5)
FIG5_SIZE = (10, 5)

COLOR_PRIMARY   = "#2196F3"
COLOR_THRESHOLD = "#F44336"
COLOR_CI        = "#90CAF9"
COLOR_PASS      = "#4CAF50"
COLOR_FAIL      = "#F44336"
COLOR_NEUTRAL   = "#9E9E9E"

RC_PARAMS = {
    "font.size": 11,
    "axes.titlesize": 12,
    "axes.labelsize": 11,
    "figure.dpi": 150,
}

# === 04_evaluate_gate.py constants ===
PRIMARY_RESULTS    = f"{BASE_DIR}/results/primary_results.json"
MIN_CONTRASTS_PASS = 2   # ≥2/3 adjacent contrasts must pass Bonferroni threshold

# === Integration test assertions ===
# Run: 01_preprocess.py → 02_fit_models.py → 03_generate_figures.py → 04_evaluate_gate.py

TEST_ASSERTIONS = {
    # After 01_preprocess.py
    "corpus_n":         {"expected": 5217, "tolerance": 0},
    "bin0_count":       {"expected": 2592, "tolerance": 100},
    "n_bins_nonempty":  {"expected": 4,    "tolerance": 0},

    # After 02_fit_models.py
    "nb2_converged":    True,     # result_cat.mle_retvals['converged'] == True
    "model_results_exists": f"{BASE_DIR}/results/model_results.json",

    # After 04_evaluate_gate.py
    "primary_results_exists": f"{BASE_DIR}/results/primary_results.json",
    "primary_results_schema": [
        "gate", "hypothesis", "is_monotonic",
        "n_adjacent_contrasts_passing", "bonferroni_alpha",
        "passed", "result", "irr_by_category",
        "ci_lower", "ci_upper", "pvalues",
        "n_corpus", "bin_counts"
    ],
    "result_values_valid": ["PASS", "INFORMATIVE_NEGATIVE"],
    "n_corpus_in_json":  5217,
}
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-10-1 | Integration test configuration | Path constants, expected values, BFGS convergence assertion, primary_results.json schema validation, gate result validity check |
