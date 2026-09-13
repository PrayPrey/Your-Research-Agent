# Config: H-E1 (Static Analysis Tool Coverage Validation)

**Type**: EXISTENCE (PoC) — single fixed config, no hyperparameter search.

Applied: PoC-fixed-dataclass-config (KB match low-relevance; standard practice for EXISTENCE tests)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new config design
**Config Files Found**: None
**Pattern Used**: dataclass

---

## A-1: Setup & config [Complexity: 5, Budget: 5]

**Applied**: Standard PyTorch/Python defaults — fixed values, no seed needed (deterministic tool calls, no randomness).

### Configuration (Python Dataclass)

```python
# code/config.py
from dataclasses import dataclass

@dataclass(frozen=True)
class Config:
    # Timeouts
    TIMEOUT_SEC: int = 30

    # Dataset sizes
    HUMANEVAL_N: int = 164
    MBPP_N: int = 500
    TOTAL_N: int = 664  # HUMANEVAL_N + MBPP_N

    # Dataset sources
    HUMANEVAL_SOURCE: str = "openai/human-eval"
    MBPP_SOURCE: str = "mbpp"          # HF dataset name
    MBPP_SPLIT: str = "test"
    MBPP_TASK_ID_MIN: int = 11
    MBPP_TASK_ID_MAX: int = 510

    # Paths
    RESULTS_DIR: str = "results"
    TEMP_DIR: str = "/tmp/h_e1_samples"

    # Output files
    COVERAGE_FILE: str = "h_e1_coverage.json"
    SUMMARY_FILE: str = "h_e1_summary.json"
    FAILURES_FILE: str = "h_e1_failures.json"

    # Tool commands
    PYLINT_CMD: tuple = ("pylint", "--output-format=json")
    MYPY_CMD: tuple = ("mypy", "--output=json")
    RADON_CMD: tuple = ("radon", "cc", "--json")

    # Success threshold (NFR / success criteria)
    VALID_RATE_THRESHOLD: float = 0.95

CONFIG = Config()
```

### Subtasks [1/1 used within A-1 budget]
| ID | Subtask | Description |
|----|---------|-------------|
| C-1-1 | requirements.txt | Pin pylint>=2.17, mypy>=1.0, radon>=6.0, datasets, python>=3.9 |

---

## A-2: Dataset loading [Complexity: 9, Budget: 9]

**Applied**: Standard HF `datasets.load_dataset` + local clone pattern. No config variation — EXISTENCE test uses fixed dataset slices only.

### Configuration

Reuses `CONFIG` from A-1 (`HUMANEVAL_SOURCE`, `MBPP_SOURCE`, `MBPP_SPLIT`, `MBPP_TASK_ID_MIN/MAX`). No additional dataclass needed — `Sample` is a data model (defined in architecture, not config).

### Subtasks [2/2 used — dataset configuration budget]
| ID | Subtask | Description |
|----|---------|-------------|
| C-2-1 | HumanEval loader config | Clone/load `openai/human-eval`, extract `task_id`, `prompt`+`canonical_solution` as `code`, tag `source="humaneval"` |
| C-2-2 | MBPP loader config | HF `load_dataset("mbpp", split="test")`, filter `task_id` in [11,510], extract `code` field, tag `source="mbpp"` |

---

## requirements.txt (pinned versions)

```
pylint>=2.17,<3.0
mypy>=1.0,<2.0
radon>=6.0,<7.0
datasets>=2.14
```

---

## Self-Validation
- [x] ONE format only (dataclass)
- [x] No ASCII diagrams
- [x] No KB search logs beyond "Applied" line
- [x] Rationale only for non-standard notes
- [x] Subtask count within budget (2 subtasks for dataset config: C-2-1, C-2-2)
- [x] Codebase Analysis (Serena) section included — green-field, Serena skipped
- [x] Total length < 400 lines
