# Config: H-M1 — Tag-Indexed Search Pathway Mechanism Verification

Applied: standalone-script path-constants pattern (statistical study, no DL config needed)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis extension
**Status**: config constants verified from H-E1 actual code
**Config Files Found**: `docs/youra_research/h-e1/code/02_fit_models.py`, `docs/youra_research/h-e1/code/04_evaluate_gate.py`
**Pattern Used**: module-level constants (dict / inline — no dataclass, no DL config)

---

## Inherited Configuration (Base Hypothesis)

From actual H-E1 code (`docs/youra_research/h-e1/code/02_fit_models.py` and `04_evaluate_gate.py`):

```python
# H-E1 actual field names (verified)
BASE_DIR          = "docs/youra_research/h-e1"
PREPROCESSED      = f"{BASE_DIR}/results/preprocessed.parquet"
MODEL_RESULTS     = f"{BASE_DIR}/results/model_results.json"
PRIMARY_RESULTS   = f"{BASE_DIR}/results/primary_results.json"

NB2_METHOD        = "bfgs"
NB2_MAXITER       = 100
NB2_DISP          = False

GATE_IRR_MIN      = 1.1
GATE_CI_LOWER_MIN = 1.1
GATE_PVAL_MAX     = 0.05

# H-E1 model_results.json keys: 'proposed', 'rc7_age_only'
# proposed['has_tags'] fields: 'irr', 'ci_lower', 'ci_upper', 'pval'
```

---

## A-2: Data Loader [Complexity: 6, Budget: 6]

```python
# 01_load_data.py — path constants (verified against H-E1 actual code)
H_E1_BASE    = "docs/youra_research/h-e1"
PREPROCESSED = f"{H_E1_BASE}/results/preprocessed.parquet"
MODEL_RESULTS = f"{H_E1_BASE}/results/model_results.json"
EXPECTED_N   = 5217
```

### Subtasks [1/1 used]
| ID | Subtask | Description |
|----|---------|-------------|
| C-2-1 | path-constants | Copy constants above into 01_load_data.py; assert len==5217 and has_tags in {0,1} |

---

## A-3: Model Fitter [Complexity: 10, Budget: 10]

```python
# 02_fit_models.py — path + formula constants
H_E1_BASE     = "docs/youra_research/h-e1"
H_M1_BASE     = "docs/youra_research/h-m1"
PREPROCESSED  = f"{H_E1_BASE}/results/preprocessed.parquet"
H_E1_RESULTS  = f"{H_E1_BASE}/results/model_results.json"
MODEL_RESULTS = f"{H_M1_BASE}/results/model_results.json"

_CONTROLS       = "log_n_instances + log_n_features + age_years + age_sq"
FORMULA_WITH_FE = f"N_tasks ~ has_tags + {_CONTROLS} + C(decade)"
FORMULA_NO_FE   = f"N_tasks ~ has_tags + {_CONTROLS}"

NB2_METHOD  = "bfgs"
NB2_MAXITER = 100
NB2_DISP    = False
```

### Subtasks [1/1 used]
| ID | Subtask | Description |
|----|---------|-------------|
| C-3-1 | formula-constants | Copy constants above into 02_fit_models.py; use in fit_nb2 calls |

---

## A-5/A-6: Figure Generator [Complexity: 8+8, Budget: 16]

```python
# 03_generate_figures.py
H_M1_BASE     = "docs/youra_research/h-m1"
MODEL_RESULTS  = f"{H_M1_BASE}/results/model_results.json"
PREPROCESSED   = "docs/youra_research/h-e1/results/preprocessed.parquet"
FIGURES_DIR    = f"{H_M1_BASE}/figures"
FIGURE_DPI     = 300
FIGURE_FORMAT  = "png"
```

---

## A-7: Gate Evaluator [Complexity: 7, Budget: 7]

```python
# 04_evaluate_gate.py
H_M1_BASE       = "docs/youra_research/h-m1"
MODEL_RESULTS   = f"{H_M1_BASE}/results/model_results.json"
PRIMARY_RESULTS = f"{H_M1_BASE}/results/primary_results.json"

GATE_IRR_MIN     = 1.1      # from H-E1 gate (same threshold)
GATE_PVAL_MAX    = 0.05

# H-E1 prerequisite values (from H-E1 Phase 4 actual results)
H_E1_IRR_PREREQ      = 1.2263
H_E1_CI_LOWER_PREREQ = 1.1681
H_E1_GATE_PREREQ     = "PASS"
```

---

## A-8: End-to-End Integration [Complexity: 9, Budget: 9]

**Applied**: standalone-script path-constants pattern

```python
# Integration test expected values (used in 04_evaluate_gate.py assertions)
EXPECTED_N              = 5217
EXPECTED_IRR_WITH_FE    = 1.2263   # tolerance ± 0.05
EXPECTED_IRR_NO_FE      = 1.3758   # tolerance ± 0.05
EXPECTED_ATTENUATION    = 1.122    # tolerance ± 0.02
EXPECTED_CRAMERS_V      = 0.823    # tolerance ± 0.05
EXPECTED_GATE_RESULT    = "PASS"
```

### Subtasks [1/1 used]
| ID | Subtask | Description |
|----|---------|-------------|
| C-8-1 | integration-expected-values | Assert outputs of all 4 scripts match expected values above within tolerance |
