# Config: H-M2

**Applied**: Feedback-granularity ablation config pattern (extends H-E1 ExperimentConfig, dataclass format)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Config class verified from actual H-E1 code (`h-e1/code/config.py`), not spec
**Config Files Found**: `h-e1/code/config.py` (single `ExperimentConfig` dataclass, no separate edit-metrics/viz config)
**Pattern Used**: dataclass

---

## Inherited Configuration (Base Hypothesis)

```python
# From: h-e1/code/config.py (ACTUAL CODE, verified)
@dataclass
class ExperimentConfig:
    seed: int = 42
    model_id: str = "codellama/CodeLlama-7b-Instruct-hf"
    max_iterations: int = 3
    temperature: float = 0.2
    max_tokens: int = 512
    top_p: float = 0.95
    timeout_sec: int = 10
    mem_limit_mb: int = 512
    datasets: list[str] = field(default_factory=lambda: ["humaneval", "mbpp"])
    feedback_types: list[str] = field(default_factory=lambda: ["execution", "random"])
    results_path: str = "results.json"
    figures_dir: str = "../figures/"
```

All field names identical to H-E1; only `feedback_types` values change for H-M2. No subclassing needed — same shape, new defaults.

---

## A-2: Config setup [Complexity: 3, Budget: 2 subtasks]

**Applied**: Direct copy of H-E1's `ExperimentConfig`, override `feedback_types` only.

### Configuration (Python Dataclass)

```python
# h-m2/code/config.py
from dataclasses import dataclass, field

@dataclass
class ExperimentConfig:
    seed: int = 42
    model_id: str = "codellama/CodeLlama-7b-Instruct-hf"
    max_iterations: int = 3
    temperature: float = 0.2
    max_tokens: int = 512
    top_p: float = 0.95
    timeout_sec: int = 10
    mem_limit_mb: int = 512
    datasets: list[str] = field(default_factory=lambda: ["humaneval", "mbpp"])
    # Non-standard: H-M2 IV is feedback granularity, not execution vs random
    feedback_types: list[str] = field(default_factory=lambda: ["detailed", "binary"])
    results_path: str = "results.json"
    figures_dir: str = "../figures/"

CONFIG = ExperimentConfig()
```

No separate config needed for edit metrics (difflib is stateless, thresholds are literals in `evaluate.py`) or visualization (fixed 3 required figures, `figures_dir` from config covers output path). Adding config knobs for these would be speculative — skipped.

Edit-scope thresholds used directly in `edit_metrics.py`/`evaluate.py` (not configurable, per architecture):
- `is_global_rewrite`: `change_ratio > 0.5`
- Gate check: `edit_scope_ratio < 0.9`

### Subtasks [1/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| C-2-1 | Write config.py | Copy H-E1 config.py, override `feedback_types` to `["detailed", "binary"]` |
