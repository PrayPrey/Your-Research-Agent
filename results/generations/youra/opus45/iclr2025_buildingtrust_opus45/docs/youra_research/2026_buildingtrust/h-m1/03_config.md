# Configuration Design: H-M1 Conditional Margin Inflation Analysis

**Hypothesis:** H-M1 (MECHANISM)
**Date:** 2026-03-24
**Type:** Statistical reanalysis — no training config required

Applied: flat-constants module pattern (analysis-only hypothesis, no dataclass needed)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Config classes verified from base code via direct file read
**Config Files Found**: `h-e1/code/config.py`
**Pattern Used**: flat module-level constants (matches H-E1 style for consistency)

---

## Inherited Configuration (Base Hypothesis)

### Config Constants (From Actual H-E1 Code)

```python
# From: h-e1/code/config.py (ACTUAL CODE - verified)
SEED: int = 42
BOOTSTRAP_N: int = 1000
CHECKPOINT_INTERVAL: int = 500     # H-E1 only, not inherited
DTYPE = torch.float16              # H-E1 only (inference), not inherited
DEVICE: str = "cuda"               # H-E1 only (inference), not inherited
MODEL_PAIRS: dict = {...}          # H-E1 only (inference), not inherited

# Paths (H-E1 actual field names):
CODE_DIR = Path(__file__).parent
HYPOTHESIS_DIR = CODE_DIR.parent
RESULTS_DIR = HYPOTHESIS_DIR / "results"
FIGURES_DIR = HYPOTHESIS_DIR / "figures"
CACHE_DIR = HYPOTHESIS_DIR / "cache"   # ← h-e1/cache/{family}/
```

**Inherited into H-M1**: `SEED`, `BOOTSTRAP_N` values only. Path pattern reused.

---

## A-1: Project Setup [Complexity: 5, Budget: 1 subtask]

### Configuration (`h-m1/code/config.py`)

```python
"""
Configuration for H-M1 Conditional Margin Inflation Analysis.
Statistical reanalysis of H-E1 data — no model inference required.
"""

from pathlib import Path

# Reproducibility
SEED: int = 42

# Statistical test parameters
PERMUTATION_N: int = 9999   # n_resamples for scipy.stats.permutation_test
BOOTSTRAP_N: int = 1000     # bootstrap CI iterations

# Model families to analyze (llama excluded — gated in H-E1)
FAMILIES: list[str] = ["qwen", "mistral"]

# Gate configuration
GATE_TYPE: str = "MUST_WORK"
P_VALUE_THRESHOLD: float = 0.05

# H-E1 cache path resolution (resolved at import time, not hardcoded)
H_E1_CODE_DIR: Path = Path(__file__).parent.parent.parent / "h-e1" / "code"
H_E1_CACHE_DIR: Path = H_E1_CODE_DIR.parent / "cache"
H_E1_RESULTS_JSON: Path = H_E1_CODE_DIR.parent / "experiment_results.json"

# H-M1 output paths
CODE_DIR: Path = Path(__file__).parent
HYPOTHESIS_DIR: Path = CODE_DIR.parent
FIGURES_DIR: Path = HYPOTHESIS_DIR / "figures"


def ensure_directories() -> None:
    """Create output directories if they don't exist."""
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-1-1 | config.py | Write flat constants module with path resolution and ensure_directories |

---

## A-2: Data Loader [Complexity: 8, Budget: 1 subtask]

No additional config required. Data loader reads from `H_E1_CACHE_DIR` defined in config.

**Cache file naming convention (verified from H-E1 actual code):**
- `h-e1/cache/{family}/{family}_base_margins.npy`
- `h-e1/cache/{family}/{family}_base_correctness.npy`
- `h-e1/cache/{family}/{family}_instruct_margins.npy`
- `h-e1/cache/{family}/{family}_instruct_correctness.npy`

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-2-1 | data_loader constants | Cache filename template: `"{family}_{variant}_{array}.npy"` |

---

## A-3 / A-4 / A-5: Analysis [Complexity: 7/10/9, Budget: 1 subtask]

All statistical parameters sourced from top-level config constants. No per-function config needed.

**Key defaults (non-standard rationale):**
- `PERMUTATION_N = 9999`: Standard odd number for permutation test to avoid tie at exact p=0.05 boundary
- `BOOTSTRAP_N = 1000`: Matches H-E1 value for methodological consistency

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-3-1 | analysis constants | KL divergence bin count: `N_KL_BINS: int = 100` (add to config.py) |

---

## Complete config.py (Final)

```python
"""
Configuration for H-M1 Conditional Margin Inflation Analysis.
Statistical reanalysis of H-E1 data — no model inference required.
"""

from pathlib import Path

# Reproducibility
SEED: int = 42

# Statistical test parameters
PERMUTATION_N: int = 9999
BOOTSTRAP_N: int = 1000
N_KL_BINS: int = 100

# Model families to analyze
FAMILIES: list[str] = ["qwen", "mistral"]

# Gate configuration
GATE_TYPE: str = "MUST_WORK"
P_VALUE_THRESHOLD: float = 0.05

# H-E1 path resolution (absolute, resolved at import time)
H_E1_CODE_DIR: Path = Path(__file__).parent.parent.parent / "h-e1" / "code"
H_E1_CACHE_DIR: Path = H_E1_CODE_DIR.parent / "cache"
H_E1_RESULTS_JSON: Path = H_E1_CODE_DIR.parent / "experiment_results.json"

# H-M1 output paths
CODE_DIR: Path = Path(__file__).parent
HYPOTHESIS_DIR: Path = CODE_DIR.parent
FIGURES_DIR: Path = HYPOTHESIS_DIR / "figures"


def ensure_directories() -> None:
    """Create output directories if they don't exist."""
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
```

---

## Subtask Budget Summary

| Task | Subtasks Used | Budget |
|------|--------------|--------|
| A-1 (Project Setup) | 1 | 1 |
| A-2 (Data Loader) | 1 | 1 |
| A-3/4/5 (Analysis) | 1 | 1 |
| A-6 through A-11 | 1 (reserved) | 1 |
| **Total** | **4** | **4** |
