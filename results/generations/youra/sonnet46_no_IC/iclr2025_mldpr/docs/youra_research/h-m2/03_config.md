# Configuration: H-M2 — Tag Count Dose-Response (NB-2 Mechanism PoC)

Applied: No matching KB pattern (KB contains diffusion model domain content only)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (extending H-E1)
**Status**: Config constants verified from actual H-E1 code
**Config Files Found**: `h-e1/code/01_preprocess.py`, `h-e1/code/02_fit_models.py`, `h-e1/code/03_generate_figures.py`
**Pattern Used**: module-level constants (hardcoded dict style, matching H-E1 pattern)

---

## Inherited Configuration (Base Hypothesis: H-E1)

Constants verified from actual H-E1 code (not specs):

```python
# From: docs/youra_research/h-e1/code/01_preprocess.py
EXPECTED_N      = 5217        # H-E1 full corpus
REFERENCE_YEAR  = 2026

# From: docs/youra_research/h-e1/code/02_fit_models.py
NB2_METHOD      = "bfgs"
NB2_MAXITER     = 100
NB2_DISP        = False
GATE_PVAL_MAX   = 0.05

# From: docs/youra_research/h-e1/code/03_generate_figures.py
FIGURE_DPI      = 300
FIGURE_FORMAT   = "png"
COLOR_PRIMARY   = "#2196F3"
COLOR_THRESHOLD = "#F44336"
COLOR_CI        = "#90CAF9"
COLOR_PASS      = "#4CAF50"
COLOR_FAIL      = "#F44336"
```

**Verified from**: `docs/youra_research/h-e1/code/` (actual implementation)

---

## A-5: Figure Generation [Complexity: 11, Budget: 2 subtasks]

### C-5-1: Figure Configuration

```python
# === FIGURE CONFIG ===
FIGURE_DPI    = 300          # inherited from H-E1
FIGURE_FORMAT = "png"        # inherited from H-E1

# === FIGURE SIZES ===
FIG1_SIZE = (8, 5)           # gate bar chart (single bar + CI)
FIG2_SIZE = (8, 5)           # tag count histogram
FIG3_SIZE = (8, 5)           # partial regression scatter
FIG4_SIZE = (10, 5)          # forest plot (2 models side-by-side)

# === FIGURE FILENAMES ===
FIG1_NAME = "fig1_gate_metrics.png"
FIG2_NAME = "fig2_tag_count_distribution.png"
FIG3_NAME = "fig3_partial_regression.png"
FIG4_NAME = "fig4_attenuation_forest.png"

# === COLORS — inherited from H-E1 palette ===
COLOR_PRIMARY   = "#2196F3"  # bar / scatter points
COLOR_THRESHOLD = "#F44336"  # dashed threshold line at 1.05
COLOR_CI        = "#90CAF9"  # error bar / CI band
COLOR_PASS      = "#4CAF50"  # PASS annotation
COLOR_FAIL      = "#F44336"  # INFORMATIVE_NEGATIVE annotation
COLOR_NEUTRAL   = "#9E9E9E"  # null reference line at 1.0

# === rcParams (apply once at module top) ===
RC_PARAMS = {
    "font.size": 11,
    "axes.titlesize": 12,
    "axes.labelsize": 11,
    "figure.dpi": 150,       # screen preview; save uses FIGURE_DPI=300
}
```

### C-5-2: Model Constants

```python
# === PATHS ===
from pathlib import Path
PROJECT_ROOT   = Path(__file__).resolve().parents[4]
H_E1_PARQUET   = PROJECT_ROOT / "docs/youra_research/h-e1/results/preprocessed.parquet"
H_E1_CSV       = PROJECT_ROOT / "docs/youra_research/h-e1/code/data/h_e1/openml_dataset_corpus.csv"
TAGGED_PARQUET = PROJECT_ROOT / "docs/youra_research/h-m2/results/tagged_subset.parquet"
MODEL_RESULTS  = PROJECT_ROOT / "docs/youra_research/h-m2/results/model_results.json"
PRIMARY_RESULTS= PROJECT_ROOT / "docs/youra_research/h-m2/results/primary_results.json"
FIGURES_DIR    = PROJECT_ROOT / "docs/youra_research/h-m2/figures"

# === SUBSET CONSTANTS ===
EXPECTED_N_TAGGED = 2625     # ±100 acceptable; has_tags=1 subset of H-E1 N=5217
REFERENCE_YEAR    = 2026     # inherited from H-E1

# === NB-2 OPTIMIZER — inherited from H-E1 ===
NB2_METHOD  = "bfgs"
NB2_MAXITER = 100
NB2_DISP    = False

# === FORMULAS ===
_CONTROLS        = "log_n_instances + log_n_features + age_years + age_sq + C(decade)"
FORMULA_BASELINE = f"N_tasks ~ {_CONTROLS}"
FORMULA_PROPOSED = f"N_tasks ~ log_tag_count_p1 + {_CONTROLS}"
FORMULA_NO_FE    = "N_tasks ~ log_tag_count_p1 + log_n_instances + log_n_features + age_years + age_sq"

# === GATE THRESHOLDS — h-m2 specific (different from H-E1's 1.1!) ===
GATE_CI_LOWER_MIN = 1.05     # Non-standard: H-E1 used 1.1; h-m2 uses 1.05 (SHOULD_WORK tier)
GATE_PVAL_MAX     = 0.05     # inherited from H-E1
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-5-1 | Figure configuration | matplotlib rcParams, figure sizes, DPI, color scheme for 4 figures |
| C-5-2 | Model constants | NB-2 optimizer constants, gate thresholds, path constants, formulas |
