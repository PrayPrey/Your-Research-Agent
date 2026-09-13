# Configuration: H-M1 — RI → ECE Mechanism Verification

**Applied: flat-constants-module (matching H-E1 pattern — module-level constants, no dataclass)**

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Config classes verified from actual H-E1 code
**Config Files Found**: `h-e1/code/config.py` (actual implementation read directly)
**Pattern Used**: Flat module constants (hardcoded dict style, consistent with H-E1)

---

## Inherited Configuration (Base Hypothesis: H-E1)

The following constants are inherited from H-E1 actual code (`h-e1/code/config.py`):

```python
# From: h-e1/code/config.py (ACTUAL CODE — verified field names)
SEED: int = 42
N_BOOTSTRAP: int = 10000
VIF_THRESHOLD: float = 5.0
SD_THRESHOLD: float = 0.05       # H-E1 gate (not reused in H-M1)
R2_THRESHOLD: float = 0.80       # H-E1 gate (not reused in H-M1)
PC1_VAR_THRESHOLD: float = 0.70  # H-E1 guard (not reused in H-M1)
MIN_MODELS: int = 30
MIN_FAMILIES: int = 3
CAP_COLS: list[str] = ["bbh", "arc_challenge", "mmlu_pro", "math_hard", "gpqa", "musr"]
RESULTS_DIR: str = "outputs"
FIGURES_DIR: str = "../figures"
```

**Verified from**: `h-e1/code/config.py` (actual implementation)

---

## H-M1 config.py (Complete)

```python
"""
config.py — Fixed constants for H-M1 RI→ECE Mechanism Verification pipeline.

Extends H-E1 constants; no hyperparameter tuning performed.
Environment: youra-h-e1 + uncertainty-calibration
"""

from __future__ import annotations

# ── Inherited from H-E1 (verified field names) ────────────────────────────────
SEED: int = 42
N_BOOTSTRAP: int = 10000
VIF_THRESHOLD: float = 5.0
MIN_MODELS: int = 30
CAP_COLS: list[str] = ["bbh", "arc_challenge", "mmlu_pro", "math_hard", "gpqa", "musr"]

# ── H-M1 gate thresholds ──────────────────────────────────────────────────────
RHO_THRESHOLD: float = 0.4        # Minimum |ρ| to PASS gate
P_THRESHOLD: float = 0.05         # Significance threshold (Holm-corrected)
FAMILY_SIGN_THRESHOLD: int = 2    # Min families with positive ρ for PASS

# ── Family analysis ───────────────────────────────────────────────────────────
TARGET_FAMILIES: list[str] = ["LLaMA", "Mistral", "Qwen"]
MIN_FAMILY_SIZE: int = 5          # Minimum n per family for per-family analysis

# ── I/O paths (relative to h-m1/code/) ───────────────────────────────────────
H_E1_OUTPUTS_DIR: str = "../h-e1/code/outputs"
RESULTS_DIR: str = "results"
FIGURES_DIR: str = "figures"

# ── Visualizer constants ──────────────────────────────────────────────────────
FIGURE_DPI: int = 300
FIGURE_SIZE_SCATTER: tuple[float, float] = (6.0, 5.0)   # Single scatter plots
FIGURE_SIZE_FAMILY: tuple[float, float] = (12.0, 4.0)   # 3-panel family subplot
FIGURE_SIZE_BAR: tuple[float, float] = (5.0, 4.5)       # Bar comparison
FIGURE_SIZE_RELIABILITY: tuple[float, float] = (7.0, 5.5)
SEABORN_THEME: str = "whitegrid"
COLOR_PALETTE: list[str] = ["#4C72B0", "#DD8452", "#55A868"]  # LLaMA/Mistral/Qwen

# Figure filename conventions
FIG1_FILENAME: str = "fig1_ri_ece_scatter.png"
FIG2_FILENAME: str = "fig2_residuals_scatter.png"
FIG3_FILENAME: str = "fig3_family_subplots.png"
FIG4_FILENAME: str = "fig4_reliability_diagram.png"
FIG5_FILENAME: str = "fig5_rho_comparison_bar.png"
FIG6_FILENAME: str = "fig6_gate_summary.png"

# ── Test suite constants ──────────────────────────────────────────────────────
TEST_N_MODELS: int = 30
TEST_SEED: int = 42
TEST_MODEL_FAMILIES: list[str] = ["LLaMA"] * 12 + ["Mistral"] * 10 + ["Qwen"] * 8
TEST_COVERAGE_MIN: float = 0.80   # 80% line coverage target
```

---

## YAML Schemas

### `results/gate_results.yaml`

```yaml
# gate_results.yaml schema
gate: "PASS"          # One of: PASS, PARTIAL, FAIL
rho: 0.52             # Full Spearman partial ρ(RI, ECE | PC1, mean_confidence)
p_val: 0.003          # Holm-corrected p-value
ci95_lower: 0.28      # Bootstrap 95% CI lower bound
ci95_upper: 0.71      # Bootstrap 95% CI upper bound
n: 30                 # Sample size
consistent_positive_families: 3   # Count of families with positive ρ
family_results:
  LLaMA:
    rho: 0.61
    p_val: 0.031
    n: 12
  Mistral:
    rho: 0.48
    p_val: 0.078
    n: 10
  Qwen:
    rho: 0.43
    p_val: 0.091
    n: 8
secondary:
  baseline_rho: 0.31        # ρ(PC1, ECE) — capability-only null model
  baseline_p: 0.094
  vif:
    RI: 1.8
    PC1: 2.1
    mean_confidence: 1.6
  cooks_flagged_models: []
  fisher_z_stat: 1.23
  fisher_z_p: 0.218
```

### `results/partial_corr_results.yaml`

```yaml
# partial_corr_results.yaml schema
full:
  rho: 0.52
  p_val: 0.003
  ci95_lower: 0.28
  ci95_upper: 0.71
  n: 30
  covariates: ["PC1", "mean_confidence"]
  method: "spearman"
family:
  LLaMA:
    rho: 0.61
    p_val: 0.031
    p_val_holm: 0.093
    n: 12
  Mistral:
    rho: 0.48
    p_val: 0.078
    p_val_holm: 0.156
    n: 10
  Qwen:
    rho: 0.43
    p_val: 0.091
    p_val_holm: 0.156
    n: 8
holm_corrected_p_values: [0.093, 0.156, 0.156]
n_families_significant: 1
```

---

## A-6: Visualizer Configuration [Complexity: 12, Budget: 2 subtasks]

**Applied: flat-constants-module**

### Configuration (in config.py above)

Key constants for Visualizer:
- `FIGURE_DPI = 300`, sizes vary per figure type
- `SEABORN_THEME = "whitegrid"`, `COLOR_PALETTE` maps to LLaMA/Mistral/Qwen
- Output path: `FIGURES_DIR = "figures"` (relative to `h-m1/code/`)

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-6-1 | Figure configuration | DPI, figure sizes per plot type, seaborn theme, color palette — all in config.py |
| C-6-2 | Output paths config | `FIGURES_DIR` constant + per-figure filename constants `FIG1_FILENAME`...`FIG6_FILENAME` in config.py |

---

## A-9: Test Suite Configuration [Complexity: 10, Budget: 2 subtasks]

**Applied: flat-constants-module**

### Test Fixture Schema (mock DataFrame columns)

```python
# Mock DataFrame for 30 models — required column schema
MOCK_DF_COLUMNS = [
    "model_id",          # str: unique model identifier
    "model_family",      # str: one of LLaMA / Mistral / Qwen
    "scale",             # float: parameter count in billions
    "training_regime",   # str: e.g. "RLHF", "SFT"
    "PC1",               # float: PCA component 1 from H-E1
    "mean_confidence",   # float: mean softmax confidence in [0,1]
    "advglue_drop",      # float: AdvGLUE accuracy drop
    "RI",                # float: residual instability score
    "ECE",               # float: expected calibration error in [0,1]
]
```

### `pytest.ini` / `pyproject.toml` Coverage Config

```ini
# pytest.ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = --cov=. --cov-report=term-missing --cov-fail-under=80

# .coveragerc
[run]
source = .
omit = tests/*, run_experiment.py

[report]
fail_under = 80
show_missing = True
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-9-1 | Test fixtures | Mock data generation: 30-row DataFrame with `TEST_MODEL_FAMILIES` distribution, `TEST_SEED=42`, columns per `MOCK_DF_COLUMNS` schema |
| C-9-2 | Coverage configuration | `pytest.ini` with `--cov-fail-under=80`, test discovery for `tests/test_*.py`, omit `run_experiment.py` from coverage |

---

## Summary

| Task | Subtasks | Key Constants |
|------|----------|---------------|
| A-6 Visualizer | C-6-1, C-6-2 | `FIGURE_DPI`, `FIGURE_SIZE_*`, `SEABORN_THEME`, `COLOR_PALETTE`, `FIG*_FILENAME` |
| A-9 Test Suite | C-9-1, C-9-2 | `TEST_N_MODELS=30`, `TEST_SEED=42`, `TEST_COVERAGE_MIN=0.80`, `MOCK_DF_COLUMNS` |
