# Config: H-M2
# Percentile-Normalized Monotonicity Attenuation

**Version:** 1.0
**Date:** 2026-03-24
**Hypothesis ID:** h-m2
**Type:** MECHANISM (EXISTENCE phase)

Applied: standard-bootstrap-CI (percentile method, n=1000, seed=42)
Applied: sklearn-logistic-regression (C=1e6, lbfgs, max_iter=1000)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: config classes verified from base code (h-m1/code/config.py read directly)
**Config Files Found**: `h-m1/code/config.py`
**Pattern Used**: module-level constants (not dataclass) - matches h-m1 implementation

---

## Inherited Configuration (Base Hypothesis)

### Config Constants (From Actual h-m1/code/config.py)

```python
# Verified field names and defaults from h-m1/code/config.py:
SEED: int = 42
PERMUTATION_N: int = 9999        # h-m1 specific - NOT inherited
BOOTSTRAP_N: int = 1000          # inherited
N_KL_BINS: int = 100             # h-m1 specific - NOT inherited
FAMILIES: list[str] = ["qwen", "mistral"]
GATE_TYPE: str = "MUST_WORK"
P_VALUE_THRESHOLD: float = 0.05

# Path resolution pattern (verified):
CODE_DIR: Path = Path(__file__).parent
HYPOTHESIS_DIR: Path = CODE_DIR.parent
H_E1_CACHE_DIR: Path = H_E1_CODE_DIR.parent / "cache"   # h-m1 resolves via h-e1/code then parent
```

**Note**: H-M1 resolves H-E1 cache as `HYPOTHESIS_DIR.parent / "h-e1" / "code"` parent `/cache`.
H-M2 architecture spec simplifies to `HYPOTHESIS_DIR.parent / "h-e1" / "cache"` directly.

**Verified from**: `/home/anonymous/YouRA_results_new_4_sonnet45/TEST_buildingtrust_opus45/docs/youra_research/20260323_buildingtrust/h-m1/code/config.py`

---

## A-1: Project Setup [Complexity: 5, Budget: 1 subtask]

**Applied**: module-level constants pattern (mirrors h-m1 flat layout)

### Configuration (Python - `code/config.py`)

```python
"""
Configuration for H-M2 Percentile-Normalized Monotonicity Analysis.
Statistical reanalysis of H-E1 data - no model inference required.
"""

from pathlib import Path

# Reproducibility
SEED: int = 42

# Statistical parameters
BOOTSTRAP_N: int = 1000          # bootstrap CI iterations
P_VALUE_THRESHOLD: float = 0.05  # significance threshold

# Model families to analyze (llama excluded - gated in H-E1)
FAMILIES: list[str] = ["qwen", "mistral"]

# Gate configuration
GATE_TYPE: str = "MUST_WORK"

# Logistic regression parameters
LR_C: float = 1e6        # effectively unregularized
LR_MAX_ITER: int = 1000  # convergence iterations
LR_SOLVER: str = "lbfgs"

# H-E1 path resolution (resolved at import time)
CODE_DIR: Path = Path(__file__).parent
HYPOTHESIS_DIR: Path = CODE_DIR.parent
H_E1_CACHE_DIR: Path = HYPOTHESIS_DIR.parent / "h-e1" / "cache"

# H-M2 output paths
FIGURES_DIR: Path = HYPOTHESIS_DIR / "figures"
RESULTS_YAML: Path = HYPOTHESIS_DIR / "experiment_results.yaml"
VALIDATION_MD: Path = HYPOTHESIS_DIR / "04_validation.md"


def ensure_directories() -> None:
    """Create output directories if they don't exist."""
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-1-1 | config.py | Write module-level constants with H-E1 path resolution and ensure_directories() |

---

## A-2 through A-12: Analysis, Visualization, Reporting Tasks

All tasks share the same config constants defined in A-1. No per-task config overrides needed.

### Key Config Values for Phase 4 Reference

```python
# Analysis (analysis.py)
BOOTSTRAP_N = 1000          # iterations for bootstrap_beta() and bootstrap_difference_test()
SEED = 42                   # passed as seed= arg to all bootstrap functions
LR_C = 1e6                  # LogisticRegression(C=LR_C, solver=LR_SOLVER, max_iter=LR_MAX_ITER)
LR_SOLVER = "lbfgs"
LR_MAX_ITER = 1000
P_VALUE_THRESHOLD = 0.05    # gate_pass: p_value < P_VALUE_THRESHOLD

# Data loading (data_loader.py)
FAMILIES = ["qwen", "mistral"]
# Expected samples per model:
EXPECTED_N: int = 14042     # used in validate_arrays(expected_n=14042)

# Visualization (visualize.py)
FIGURE_DPI: int = 300
FIGURE_FONTSIZE: int = 12

# Paths (resolved from config)
# H_E1_CACHE_DIR / {family} / *.npy  <- glob for array files
# FIGURES_DIR / *.png                 <- figure outputs
# RESULTS_YAML                        <- experiment_results.yaml
# VALIDATION_MD                       <- 04_validation.md
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-2-1 | Analysis constants | Document BOOTSTRAP_N, SEED, LR_* usage in analysis.py |
| C-2-2 | Output paths | Document FIGURES_DIR, RESULTS_YAML, VALIDATION_MD usage in report.py |

---

## Gate Evaluation Constants

```python
# Gate logic (report.py / analysis.py)
# gate_pass per family: beta_instruct < beta_base AND p_value < P_VALUE_THRESHOLD
# overall gate: ALL families must gate_pass == True -> "PASS" else "FAIL"
GATE_TYPE: str = "MUST_WORK"
P_VALUE_THRESHOLD: float = 0.05
```

---

## H-E1 Cache Path Resolution

```python
# Verified pattern from h-m1/code/config.py (adapted for h-m2):
CODE_DIR = Path(__file__).parent          # h-m2/code/
HYPOTHESIS_DIR = CODE_DIR.parent          # h-m2/
H_E1_CACHE_DIR = HYPOTHESIS_DIR.parent / "h-e1" / "cache"
# -> h-m2/../h-e1/cache/ = 20260323_buildingtrust/h-e1/cache/

# File glob per family (verified from h-m1 data_loader pattern):
# H_E1_CACHE_DIR / {family} / *.npy
# Stem classification:
#   "instruct" or "chat" in stem -> instruct variant; else base
#   "margin" in stem -> margins array; "correct" in stem -> correctness array
```

---

## Self-Validation

- [x] ONE format only (module-level constants - matches h-m1 actual code)
- [x] No ASCII diagrams
- [x] No KB search logs (only "Applied: X" lines)
- [x] Rationale only for non-standard values (LR_C=1e6 documented inline)
- [x] Subtask count within budget (3 total: C-1-1, C-2-1, C-2-2)
- [x] Total length < 400 lines
- [x] "Codebase Analysis (Serena)" section included
- [x] Base hypothesis actual code verified (h-m1/code/config.py read)
- [x] Field names verified from actual implementation
- [x] "Inherited Configuration" section included
