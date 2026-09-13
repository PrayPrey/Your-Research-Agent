# Configuration: H-M1 — Error Traces Contain Counterfactual Information

Applied: pipeline-stage config pattern (single dataclass, stage-scoped fields)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new config design (matches architecture's green-field finding)
**Config Files Found**: None - new config
**Pattern Used**: dataclass (Python), matches `config.py` module in architecture

---

## Format Decision

**Dataclass** — architecture specifies `config.py` with module-level constants consumed by all pipeline stages (A-1..A-8). A single dataclass instance replaces the flat constants for type safety and dot-access consistency across modules.

## Configuration (`h-m1/code/config.py`)

```python
from dataclasses import dataclass, field

@dataclass
class Config:
    # Reproducibility
    seed: int = 42

    # Data
    data_dir: str = "h-m1/data"
    results_dir: str = "h-m1/results"
    humaneval_n: int = 164
    mbpp_n: int = 500

    # Bug injection (FR-1)
    bug_types: tuple = ("syntax", "logic", "type", "off_by_one")

    # Sandbox execution (FR-2, NFR-1, NFR-3)
    timeout_s: int = 10
    memory_mb: int = 512
    network_disabled: bool = True

    # CF annotation (FR-3)
    cf_threshold: float = 0.4   # PRD success criterion: CF_score >= 0.4

    # Human validation (FR-5)
    human_sample_n: int = 100
    kappa_target: float = 0.7

    # Hypothesis test (metrics.py)
    hypothesis_test_threshold: float = 0.4  # one-sample t-test vs this value
```

**Rationale (non-standard values only)**:
- `timeout_s=10`, `memory_mb=512`, `cf_threshold=0.4` — directly specified by PRD NFR-1 and Success Criteria, not tunable defaults.
- `human_sample_n=100` — fixed by FR-5.1, not a hyperparameter to sweep.

### Subtasks
No subtask decomposition — config is a single flat dataclass consumed as-is by A-1 through A-9; no config-specific implementation work beyond this file.

---

## Usage Note

All modules (`bug_injector.py`, `sandbox_executor.py`, `cf_annotator.py`, `metrics.py`, `run_pipeline.py`) import a single shared instance:

```python
CFG = Config()
```

No YAML needed — architecture's `run_pipeline.py` lists `pyyaml` as a dependency, but PRD has no runtime-tunable settings requiring external override (single fixed experimental run, not a sweep). If future ablations require CLI overrides, extend with `dataclasses.replace(CFG, **overrides)`.
