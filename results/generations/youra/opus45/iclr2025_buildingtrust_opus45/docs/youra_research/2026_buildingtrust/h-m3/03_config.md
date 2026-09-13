# Config: H-M3
# Geometric vs Scalar Distortion via Brier Decomposition

**Version:** 1.0
**Date:** 2026-03-24
**Hypothesis ID:** h-m3
**Type:** MECHANISM | SHOULD_WORK gate

Applied: flat-module statistical-reanalysis config pattern (from h-m2 base hypothesis)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: config classes verified from base code
**Config Files Found**: `h-m2/code/config.py`
**Pattern Used**: module-level constants (no dataclass — matches h-m2 style)

---

## Inherited Configuration (Base Hypothesis)

### Config Constants (From Actual Code: h-m2/code/config.py)

```python
# Verified field names and defaults from actual h-m2 implementation:
SEED: int = 42
BOOTSTRAP_N: int = 1000
LR_C: float = 1e6           # h-m2 only — not inherited
LR_MAX_ITER: int = 1000     # h-m2 only — not inherited
FAMILIES: list[str] = ["qwen", "mistral"]
GATE_TYPE: str = "MUST_WORK"    # h-m2 uses MUST_WORK
P_VALUE_THRESHOLD: float = 0.05
CODE_DIR: Path = Path(__file__).parent
HYPOTHESIS_DIR: Path = CODE_DIR.parent
H_E1_CACHE_DIR: Path = HYPOTHESIS_DIR.parent / "h-e1" / "cache"
FIGURES_DIR: Path = HYPOTHESIS_DIR / "figures"
RESULTS_YAML: Path = HYPOTHESIS_DIR / "experiment_results.yaml"
VALIDATION_MD: Path = HYPOTHESIS_DIR / "04_validation.md"
```

**Verified from**: `h-m2/code/config.py` (actual implementation)

---

## A-1: Project Setup [Complexity: 5, Budget: 1 subtask]

Applied: flat-module constants pattern (h-m2 style)

### Configuration (Python module-level constants)

```python
# code/config.py
from pathlib import Path

# Reproducibility
SEED: int = 42

# Bootstrap parameters
BOOTSTRAP_N: int = 1000

# Brier decomposition parameters
N_BINS: int = 15

# Decomposition verification tolerance
DECOMP_TOLERANCE: float = 1e-6  # Non-standard: strict verification per Murphy (1973)

# Model families
FAMILIES: list[str] = ["qwen", "mistral"]

# Gate configuration
GATE_TYPE: str = "SHOULD_WORK"  # Non-standard: h-m3 uses SHOULD_WORK vs h-m2's MUST_WORK
P_VALUE_THRESHOLD: float = 0.05

# Path resolution
CODE_DIR: Path = Path(__file__).parent
HYPOTHESIS_DIR: Path = CODE_DIR.parent
H_E1_CACHE_DIR: Path = HYPOTHESIS_DIR.parent / "h-e1" / "cache"
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
| C-1-1 | config.py | Write module-level constants with path resolution and ensure_directories() |

---

## A-3 / A-4: Brier Decomposition + Bootstrap Engine [Complexity: 13+12, Budget: 1 subtask]

Applied: bootstrap-CI paired difference test pattern (h-m2 analysis.py)

### Configuration (function defaults — no separate config needed)

Key parameter values used as function defaults:

```python
# brier_decomp.py function defaults
def murphy_brier_decomposition(
    logits: np.ndarray,
    labels: np.ndarray,
    n_bins: int = N_BINS,           # 15
) -> dict[str, float]: ...

def bootstrap_decomposition(
    logits: np.ndarray,
    labels: np.ndarray,
    n_iterations: int = BOOTSTRAP_N,  # 1000
    n_bins: int = N_BINS,             # 15
    seed: int = SEED,                 # 42
) -> dict[str, np.ndarray]: ...

def compute_ci(
    bootstrap_values: np.ndarray,
    alpha: float = 0.05,
) -> tuple[float, float, float]: ...
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-3-1 | decomp+bootstrap defaults | All function-level defaults reference config constants; no additional config needed |

---

## A-5 / A-2: Analysis + Data Loading [Complexity: 10+8, Budget: 1 subtask]

### Configuration (function defaults)

```python
# data_loader.py
EXPECTED_N: int = 14042   # Non-standard: fixed sample count from H-E1
N_CLASSES: int = 4        # MMLU has 4 answer options

def validate_cache(
    data: dict[str, np.ndarray],
    expected_n: int = EXPECTED_N,
    n_classes: int = N_CLASSES,
) -> None: ...

# analysis.py
def paired_bootstrap_difference(
    base_logits: np.ndarray,
    inst_logits: np.ndarray,
    labels: np.ndarray,
    component: str,
    n_iterations: int = BOOTSTRAP_N,  # 1000
    n_bins: int = N_BINS,             # 15
    seed: int = SEED,                 # 42
) -> dict[str, float]: ...
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-5-1 | analysis+loader defaults | EXPECTED_N=14042, N_CLASSES=4; all bootstrap params reference config constants |

---

## Cache File Naming Convention

```python
# H-E1 cache flat layout (differs from h-m2 per-family subdirectories)
CACHE_FILES = {
    "qwen": {
        "base":    "qwen_base_logits.npy",
        "instruct": "qwen_instruct_logits.npy",
    },
    "mistral": {
        "base":    "mistral_base_logits.npy",
        "instruct": "mistral_instruct_logits.npy",
    },
    "labels": "labels.npy",
}
```

Non-standard: H-M3 loads from cache root directly (not per-family subdirectories like H-M2).

---

*Generated by Phase 3 Configuration Agent*
*Base hypothesis code verified from: h-m2/code/config.py (actual implementation)*
