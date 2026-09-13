# Config: H-M1

**Hypothesis**: Capability-independent calibration-hallucination mechanistic link
**Type**: MECHANISM (pure statistical analysis, no neural network training)
**Date**: 2026-04-30

Applied: BCa-bootstrap-statistical-analysis pattern (domain expertise)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: config verified from actual H-E1 code (Read tool — Serena MCP unavailable)
**Config Files Found**: `h-e1/code/config.py` — flat module-level constants (no dataclass)
**Pattern Used**: hardcoded module-level constants (consistent with H-E1 style)

---

## Inherited Configuration (Base Hypothesis)

### Verified from H-E1 Actual Code (`h-e1/code/config.py`)

Fields directly reused or referenced in H-M1:

```python
# From h-e1/code/config.py (verified field names)
COVARIATE: str = "MMLU_acc"          # reused as partial-corr covariate
MIN_MODELS: int = 25                  # reused for data validation
N_BOOTSTRAP: int = 10000             # reused (same value)
FIGURE_DPI: int = 150                # reused
FIGURE_FORMAT: str = "png"           # reused
RESULTS_DIR: str = "h-e1/results/"  # SOURCE path for score matrix
```

Fields NOT reused (H-E1 specific): `MODELS`, `TASKS`, `BATCH_SIZE`, `GREEDY_SEED`,
`STOCHASTIC_SEEDS`, `STOCHASTIC_TEMPERATURE`, `ECE_BINS`, `GATE_PAIRS`, `GATE_THRESHOLD`,
`N_FACTORS`, `FA_METHOD`, `FA_ROTATION`, `TUCKER_CONGRUENCE_THRESHOLD`, `INDICATORS`.

---

## H-M1 Configuration

### A-1: Project Setup — config.py [Complexity: 1, Budget: 1]

Applied: Standard (flat constants matching H-E1 pattern)

```python
# h-m1/code/config.py
from __future__ import annotations
import os

# --- Paths ---
_BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

SCORE_MATRIX_PATH: str = os.path.join(_BASE, "h-e1", "results", "score_matrix.csv")
SCORE_MATRIX_T07_PATH: str = os.path.join(_BASE, "h-e1", "results", "score_matrix_t07.csv")
RESULTS_DIR: str = os.path.join(_BASE, "h-m1", "results") + "/"
FIGURES_DIR: str = os.path.join(_BASE, "h-m1", "figures") + "/"

# --- Bootstrap ---
N_BOOTSTRAP: int = 10000
BOOTSTRAP_SEED: int = 42

# --- Column names ---
PRIMARY_X: str = "ECE"
PRIMARY_Y: str = "TruthfulQA_pct"
DISCRIMINANT_Y: str = "HumanEval_pass1"
COVARIATE: str = "MMLU_acc"          # inherited from H-E1 (verified)
INTERNAL_X: str = "ECE"
INTERNAL_Y: str = "Brier"

REQUIRED_COLS: list[str] = [
    "ECE", "Brier", "TruthfulQA_pct", "MMLU_acc",
    "HumanEval_pass1", "ANLI_drop", "model_id"
]
MIN_MODELS: int = 25                  # inherited from H-E1 (verified)

# --- Thresholds ---
PRIMARY_THRESHOLD: float = 0.40
INTERNAL_THRESHOLD: float = 0.30
DISCRIMINANT_THRESHOLD: float = 0.20
DECODING_INVARIANCE_THRESHOLD: float = 0.30

# --- Figure settings ---
FIGURE_DPI: int = 150                 # inherited from H-E1 (verified)
FIGURE_FORMAT: str = "png"            # inherited from H-E1 (verified)
FIGURE_NAMES: dict = {
    "partial_corr_matrix":     "fig1_partial_corr_matrix.png",
    "bootstrap_ci_primary":    "fig2_bootstrap_ci_primary.png",
    "discriminant_scatter":    "fig3_discriminant_scatter.png",
    "internal_consistency":    "fig4_internal_consistency.png",
    "decoding_invariance":     "fig5_decoding_invariance.png",
}
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-1-1 | Write config.py | Flat constants as above, create results/figures dirs |

---

## A-2: Data Loader — score matrix paths [Complexity: 1, Budget: 1]

Applied: Standard (no additional config needed beyond A-1 paths)

Config consumed by `data_loader.py` from `config.py`:

```python
# data_loader.py imports these from config
# SCORE_MATRIX_PATH, SCORE_MATRIX_T07_PATH, REQUIRED_COLS, MIN_MODELS
```

No separate config block needed — all values defined in `config.py` above.

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-2-1 | Verify path resolution | Confirm absolute path construction works from code/ subdir |

---

## A-3: BCa Bootstrap Core [Complexity: 2, Budget: 1]

Applied: Standard BCa bootstrap parameters

```python
# Consumed from config.py
N_BOOTSTRAP: int = 10000   # standard for stable CI estimation
BOOTSTRAP_SEED: int = 42
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-3-1 | Bootstrap config | N_BOOTSTRAP and BOOTSTRAP_SEED already in config.py |

---

## A-5: Partial Correlation Analyzer [Complexity: 2, Budget: 1]

Applied: Standard partial-correlation threshold convention

```python
# Consumed from config.py
PRIMARY_THRESHOLD: float = 0.40           # primary mechanistic link gate
INTERNAL_THRESHOLD: float = 0.30          # ECE-Brier internal consistency
DISCRIMINANT_THRESHOLD: float = 0.20      # non-significance upper bound
DECODING_INVARIANCE_THRESHOLD: float = 0.30

COVARIATE: str = "MMLU_acc"
PRIMARY_X: str = "ECE"
PRIMARY_Y: str = "TruthfulQA_pct"
DISCRIMINANT_Y: str = "HumanEval_pass1"
INTERNAL_X: str = "ECE"
INTERNAL_Y: str = "Brier"
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-5-1 | Threshold config | All thresholds defined in config.py; analyzer imports directly |

---

## A-7/A-8: Visualization [Complexity: 2, Budget: 1]

Applied: Standard matplotlib figure config

```python
# Consumed from config.py
FIGURE_DPI: int = 150
FIGURE_FORMAT: str = "png"
FIGURE_NAMES: dict = {
    "partial_corr_matrix":     "fig1_partial_corr_matrix.png",
    "bootstrap_ci_primary":    "fig2_bootstrap_ci_primary.png",
    "discriminant_scatter":    "fig3_discriminant_scatter.png",
    "internal_consistency":    "fig4_internal_consistency.png",
    "decoding_invariance":     "fig5_decoding_invariance.png",
}
FIGURES_DIR: str = "h-m1/figures/"
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-78-1 | Figure naming | FIGURE_NAMES dict maps logical keys to filenames for visualizer.py |

---

## A-9: Reporter — output paths [Complexity: 1, Budget: 1]

Applied: Standard (output directory config)

```python
# Consumed from config.py
RESULTS_DIR: str = "h-m1/results/"
FIGURES_DIR: str = "h-m1/figures/"
```

Reporter creates both directories at startup with `os.makedirs(..., exist_ok=True)`.

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-9-1 | Output dirs | RESULTS_DIR and FIGURES_DIR; reporter ensures dirs exist before writing |

---

## Subtask Summary

| ID | Task | Subtask | Description |
|----|------|---------|-------------|
| C-1-1 | A-1 | Write config.py | All constants, absolute path construction |
| C-2-1 | A-2 | Path verification | Confirm paths resolve from code/ subdir |
| C-3-1 | A-3 | Bootstrap config | N_BOOTSTRAP=10000, BOOTSTRAP_SEED=42 in config.py |
| C-5-1 | A-5 | Threshold config | Four thresholds + column names in config.py |
| C-78-1 | A-7/8 | Figure naming | FIGURE_NAMES dict + DPI/format settings |
| C-9-1 | A-9 | Output dirs | RESULTS_DIR / FIGURES_DIR with makedirs |

**Total subtasks**: 6/6 used
