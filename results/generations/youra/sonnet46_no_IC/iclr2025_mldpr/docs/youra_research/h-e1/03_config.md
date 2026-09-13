# Configuration: H-E1 — Binary Tag Presence → Task Count (NB-2 Existence Test)

**Hypothesis ID:** H-E1
**Type:** EXISTENCE (PoC)
**Date:** 2026-08-05

Applied: flat-constants pattern (module-level constants, no class overhead for single-run deterministic pipeline)

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze
**Config Files Found**: None - new config
**Pattern Used**: hardcoded dict (flat constants per script)

---

## Configuration Overview

What is configurable:
- File paths (shared across all 4 scripts)
- NB-2 model formula strings and optimizer settings
- Gate thresholds (IRR, CI, p-value cutoffs)
- Robustness check parameters
- Figure aesthetics (DPI, colors, sizes)

What is NOT configurable (deterministic by design):
- Random seeds (MLE has no randomness)
- Train/test split (census study, full N=5,217)
- Model family (NB-2 confirmed by CT LR=2222.68 in prior episode)

---

## Path Configuration

Paste into each script header:

```python
# === PATHS ===
BASE_DIR        = "docs/youra_research/h-e1"
CORPUS_PATH     = f"{BASE_DIR}/code/data/h_e1/openml_dataset_corpus.csv"
PREPROCESSED    = f"{BASE_DIR}/results/preprocessed.parquet"
MODEL_RESULTS   = f"{BASE_DIR}/results/model_results.json"
PRIMARY_RESULTS = f"{BASE_DIR}/results/primary_results.json"
FIGURES_DIR     = f"{BASE_DIR}/figures"
```

Script-specific path aliases (use the shared constants above):

| Script | Reads | Writes |
|--------|-------|--------|
| 01_preprocess.py | CORPUS_PATH | PREPROCESSED |
| 02_fit_models.py | PREPROCESSED | MODEL_RESULTS |
| 03_generate_figures.py | MODEL_RESULTS, PREPROCESSED | FIGURES_DIR/*.png |
| 04_evaluate_gate.py | MODEL_RESULTS | PRIMARY_RESULTS |

---

## Model Configuration

```python
# === NB-2 OPTIMIZER ===
NB2_METHOD  = "bfgs"
NB2_MAXITER = 100      # default=35; increased for safety on decade FE dummies
NB2_DISP    = False

# === FORMULAS ===
_CONTROLS        = "log_n_instances + log_n_features + age_years + age_sq + C(decade)"
FORMULA_BASELINE = f"N_tasks ~ {_CONTROLS}"
FORMULA_PROPOSED = f"N_tasks ~ has_tags + {_CONTROLS}"
FORMULA_AGE_ONLY = f"N_tasks ~ has_tags + log_n_instances + log_n_features + age_years + age_sq"
# FORMULA_AGE_ONLY: RC-7 — drops C(decade) to isolate era-confounding risk

# === GATE THRESHOLDS ===
GATE_IRR_MIN      = 1.1
GATE_CI_LOWER_MIN = 1.1
GATE_PVAL_MAX     = 0.05
PARTIAL_CI_MIN    = 1.05   # partial pass floor

# === DATA CONSTANTS ===
EXPECTED_N              = 5217
REFERENCE_YEAR          = 2026
RC4_WINSORIZE_PCT       = 99
```

---

## Figure Configuration

```python
# === MATPLOTLIB GLOBAL ===
FIGURE_DPI    = 300
FIGURE_FORMAT = "png"

# === COLORS ===
COLOR_PRIMARY   = "#2196F3"   # primary model bar
COLOR_THRESHOLD = "#F44336"   # threshold hline at 1.1
COLOR_RC        = "#FF9800"   # robustness check bars
COLOR_CI        = "#90CAF9"   # CI error bar caps

# === FIGURE SIZES (width, height in inches) ===
FIG1_SIZE = (8, 5)    # gate metrics: IRR + CI bar
FIG2_SIZE = (10, 8)   # forest plot: all covariates
FIG3_SIZE = (8, 5)    # decade adoption: mean has_tags by decade
FIG4_SIZE = (10, 6)   # RC comparison: primary/RC-4/RC-5/RC-7
FIG5_SIZE = (8, 6)    # obs vs pred scatter (log scale)

# === FIGURE FILENAMES ===
FIG1_NAME = "fig1_gate_metrics.png"
FIG2_NAME = "fig2_forest_plot.png"
FIG3_NAME = "fig3_decade_adoption.png"
FIG4_NAME = "fig4_rc_comparison.png"
FIG5_NAME = "fig5_obs_vs_pred.png"
```

---

## Requirements

File: `docs/youra_research/h-e1/code/requirements.txt`

```
statsmodels>=0.14
numpy>=1.24
pandas>=2.0
scipy>=1.10
matplotlib>=3.7
patsy>=0.5
pyarrow>=12.0
openml>=0.14
```

`openml` is fallback-only (if CSV cache missing). `pyarrow` required for parquet I/O.

---

## Subtasks

Budget: 1 subtask (Epic E3 only, per task allocation)

### Subtask C-E3-1: Figure Generation Constants and Layout
**Parent Epic:** E3 — Generate Figures (`03_generate_figures.py`)
**Description:** Implement the figure configuration block (colors, DPI, sizes, filenames) at the top of `03_generate_figures.py` and wire each `figN_*` function to save using `FIGURES_DIR / FIG{N}_NAME` at `FIGURE_DPI`. All 5 figure functions use the shared constants; no hardcoded values inside function bodies.
**Acceptance Criteria:**
- `FIGURES_DIR` created with `os.makedirs(FIGURES_DIR, exist_ok=True)` before first save
- All 5 figures saved as PNG at 300 DPI using shared constants
- Threshold line in Fig 1 and Fig 4 uses `GATE_IRR_MIN = 1.1` (not hardcoded `1.1`)
- Color constants used consistently across all figures
- Script runs end-to-end from `model_results.json` + `preprocessed.parquet` to 5 PNG files
