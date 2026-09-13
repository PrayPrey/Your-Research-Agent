# Configuration: H-M1 (Static Analysis Detects Structural Errors)

**Applied:** Static-analysis-config pattern (no NN hyperparameters; tool timeouts + gate threshold only)
**Applied:** Dataclass-singleton-CONFIG pattern (from H-E1)

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis (H-E1)
**Status:** Config class verified from actual code (`h-e1/code/config.py`, read directly — Serena unavailable this session)
**Config Files Found:** `h-e1/code/config.py`
**Pattern Used:** dataclass singleton (`CONFIG = ExperimentConfig()`)

**Field verification note:** `exec_timeout_sec` in actual H-E1 code is `10`, not `5` as stated in 02c_experiment_brief.md. H-M1 config below uses the verified actual value.

---

## Inherited Configuration (Base Hypothesis)

```python
# From: h-e1/code/config.py (ACTUAL CODE)
@dataclass
class ExperimentConfig:
    seed: int = 42
    pylint_timeout_sec: int = 30
    mypy_timeout_sec: int = 30
    exec_timeout_sec: int = 10       # verified from actual code (brief said 5)
    output_dir: str = "outputs/"
    figures_dir: str = "../figures/"
    results_file: str = "outputs/results.json"
    # H-E1-only fields not needed by H-M1: model_name, temperature, max_tokens,
    # jaccard_gate, non_overlap_gate
```

Reused unchanged: `pylint_timeout_sec`, `mypy_timeout_sec`, `exec_timeout_sec`, `seed`, `output_dir`, `figures_dir`, `results_file` pattern.
Dropped (not applicable to H-M1, no LLM generation step): `model_name`, `temperature`, `max_tokens`, `jaccard_gate`, `non_overlap_gate`.
New: `structural_gate` (replaces `jaccard_gate`/`non_overlap_gate` as the single H-M1 gate).

---

## A-2: Config setup [Complexity: 3, Budget: 3]

**Applied:** Dataclass singleton, gate-threshold-as-field pattern

### Configuration (Python Dataclass)

```python
"""H-M1 Experiment Configuration."""
from dataclasses import dataclass

@dataclass
class ExperimentConfig:
    seed: int = 42
    pylint_timeout_sec: int = 30
    mypy_timeout_sec: int = 30
    exec_timeout_sec: int = 10
    structural_gate: float = 0.60
    output_dir: str = "outputs/"
    figures_dir: str = "../figures/"
    results_file: str = "outputs/results.json"

CONFIG = ExperimentConfig()
```

### Subtasks [1/1 used]
| ID | Subtask | Description |
|----|---------|-------------|
| C-2-1 | Write config.py | Copy H-E1 pattern, drop LLM fields, add `structural_gate` |

---

## A-3: STRUCTURAL_ERROR_CODES dict [Complexity: 4, Budget: 4]

**Applied:** Constant lookup-table pattern (from 02c_experiment_brief.md core mechanism spec)

### Configuration (Module-level constant)

```python
STRUCTURAL_ERROR_CODES: dict[str, str] = {
    # pylint structural errors
    "E0001": "syntax-error",
    "E0102": "function-redefined",
    "E0602": "undefined-variable",
    "E0603": "undefined-all-variable",
    "E1101": "no-member",
    "E1120": "no-value-for-parameter",
    "E1121": "too-many-function-args",
    "W0612": "unused-variable",
    "W0611": "unused-import",
    # mypy type-error keywords (matched via substring in error line)
    "incompatible-type": "type-mismatch",
    "arg-type": "argument-type-error",
    "return-value": "return-type-error",
    "name-defined": "undefined-name",
}
```

Lives in `structural_errors.py` per architecture; not part of `ExperimentConfig` (fixed mapping, not a runtime parameter).

### Subtasks [1/1 used]
| ID | Subtask | Description |
|----|---------|-------------|
| C-3-1 | Define STRUCTURAL_ERROR_CODES | Verbatim from 02c brief, in structural_errors.py |

---

## Runtime Parameters (Parallelization)

**Applied:** ProcessPoolExecutor worker-count pattern (from H-E1 `run_analysis.py`)

```python
MAX_WORKERS = min(8, os.cpu_count())  # matches H-E1; not a CONFIG field (derived at runtime)
```

- No dataclass field needed — mirrors H-E1's inline `min(8, cpu_count())` call in `run_analysis.py`.
- 563 problems / 8 workers, 30s static-analysis timeout per tool per problem → bounds total runtime well under the 2hr NFR-01 budget.

---

## Existence-Style Note

H-M1 is a MECHANISM hypothesis (not EXISTENCE), but has no hyperparameter sweep — single fixed config, 1 seed, deterministic static analysis (no training loop, no epochs). Only one `ExperimentConfig` instance (`CONFIG`) is needed; no variant configs.
