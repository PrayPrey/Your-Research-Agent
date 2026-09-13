# Configuration: H-M2 (Execution Detects Behavioral Errors)

**Applied:** Static-analysis-config pattern (no NN hyperparameters; tool timeouts + gate threshold only)
**Applied:** Dataclass-singleton-CONFIG pattern (from H-M1)

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis (H-M1)
**Status:** Config class verified from actual code (`h-m1/code/config.py`, read directly — Serena unavailable this session)
**Config Files Found:** `h-m1/code/config.py`
**Pattern Used:** dataclass singleton (`CONFIG = ExperimentConfig()`)

---

## Inherited Configuration (Base Hypothesis)

```python
# From: h-m1/code/config.py (ACTUAL CODE)
@dataclass
class ExperimentConfig:
    seed: int = 42
    pylint_timeout_sec: int = 30
    mypy_timeout_sec: int = 30
    exec_timeout_sec: int = 10       # verified from actual code
    structural_gate: float = 0.60    # H-M1 specific
    output_dir: str = "outputs/"
    figures_dir: str = "../figures/"
    results_file: str = "outputs/results.json"
```

Reused unchanged: `pylint_timeout_sec`, `mypy_timeout_sec`, `exec_timeout_sec`, `seed`, `output_dir`, `figures_dir`, `results_file` pattern.
Replaced: `structural_gate` (H-M1) → `behavioral_gate` (H-M2)

---

## A-2: Config setup [Complexity: 3, Budget: 3]

**Applied:** Dataclass singleton, gate-threshold-as-field pattern

### Configuration (Python Dataclass)

```python
"""H-M2 Experiment Configuration."""
from dataclasses import dataclass

@dataclass
class ExperimentConfig:
    seed: int = 42
    pylint_timeout_sec: int = 30
    mypy_timeout_sec: int = 30
    exec_timeout_sec: int = 10
    behavioral_gate: float = 0.40
    output_dir: str = "outputs/"
    figures_dir: str = "../figures/"
    results_file: str = "outputs/results.json"

CONFIG = ExperimentConfig()
```

### Subtasks [1/1 used]
| ID | Subtask | Description |
|----|---------|-------------|
| C-2-1 | Write config.py | Copy H-M1 pattern, replace `structural_gate` with `behavioral_gate` |

---

## A-4: BEHAVIORAL_CATEGORIES dict [Complexity: 4, Budget: 4]

**Applied:** Constant lookup-table pattern

### Configuration (Module-level constant)

```python
# In behavioral_errors.py
BEHAVIORAL_CATEGORIES: dict[str, list[str]] = {
    "wrong_output": [
        "AssertionError",
        "Expected",
        "expected",
        "!=",
        "assert"
    ],
    "runtime_exception": [
        "TypeError",
        "ValueError", 
        "IndexError",
        "KeyError",
        "AttributeError",
        "ZeroDivisionError",
        "RuntimeError",
        "NameError"
    ],
    "timeout": [
        "timeout",
        "Timeout",
        "TimeoutError",
        "time limit",
        "timed out"
    ],
    "edge_case": []  # default fallback category
}
```

Lives in `behavioral_errors.py` per architecture; not part of `ExperimentConfig` (fixed mapping, not a runtime parameter).

### Subtasks [1/1 used]
| ID | Subtask | Description |
|----|---------|-------------|
| C-4-1 | Define BEHAVIORAL_CATEGORIES | Category -> keyword list mapping |

---

## Runtime Parameters (Parallelization)

**Applied:** ProcessPoolExecutor worker-count pattern (from H-M1 `run_analysis.py`)

```python
MAX_WORKERS = min(8, os.cpu_count())  # matches H-M1; not a CONFIG field (derived at runtime)
```

- No dataclass field needed — mirrors H-M1's inline `min(8, cpu_count())` call in `run_analysis.py`.
- 563 problems / 8 workers, 30s static-analysis timeout per tool per problem + 10s exec timeout → bounds total runtime well under the 2hr NFR-01 budget.

---

## Gate Configuration

| Parameter | Value | Source |
|-----------|-------|--------|
| behavioral_gate | 0.40 | Phase 2C experiment brief |
| Gate Type | SHOULD_WORK | verification_state.yaml |
| Pass Condition | behavioral_rate > 0.40 | >40% of static-clean code fails tests |
| Fail Action | Document as limitation | SHOULD_WORK gate |

---

## Existence-Style Note

H-M2 is a MECHANISM hypothesis (not EXISTENCE), but has no hyperparameter sweep — single fixed config, 1 seed, deterministic static analysis (no training loop, no epochs). Only one `ExperimentConfig` instance (`CONFIG`) is needed; no variant configs.
