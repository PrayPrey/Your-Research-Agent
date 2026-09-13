# Configuration: H-M3 Dose-Response Analysis

## Codebase Analysis (Serena)

**Project Type**: green-field (analysis module; no `h-m3/code/` exists yet)
**Status**: green-field - new config design; task list pattern reused from `h-m2/code/config.py::EvalConfig.tasks`
**Config Files Found**: None - new config
**Pattern Used**: dataclass

---

## A-1: Dose-Response Analysis Config [Complexity: 3, Budget: 3]

**Applied**: Standard dataclass config (matches H-M2 sibling pattern)

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass, field
from typing import Tuple

@dataclass
class SweepConfig:
    thresholds: Tuple[int, ...] = (0, 10, 20, 30, 40, 50, 60, 70, 80, 90)
    n_seeds: int = 3
    benchmark_tasks: Tuple[str, ...] = ("hellaswag", "arc_easy", "piqa", "winogrande")

@dataclass
class ModelSelectionConfig:
    polynomial_degrees: Tuple[int, ...] = (1, 2, 3)
    model_selection_criterion: str = "bic"  # "bic" or "aic"

@dataclass
class BootstrapConfig:
    n_bootstrap: int = 1000
    ci_level: float = 0.95
    seed: int = 42

@dataclass
class SuccessCriteria:
    min_threshold: int = 20   # peak must be >= p20 (internal, not lower boundary)
    max_threshold: int = 80   # peak must be <= p80 (internal, not upper boundary)
    max_ci_width: float = 30.0  # percentile points

@dataclass
class PathConfig:
    sweep_data_path: str = "data/sweep_results.csv"
    output_dir: str = "output/"
    figures_dir: str = "output/figures/"

@dataclass
class DoseResponseConfig:
    sweep: SweepConfig = field(default_factory=SweepConfig)
    model_selection: ModelSelectionConfig = field(default_factory=ModelSelectionConfig)
    bootstrap: BootstrapConfig = field(default_factory=BootstrapConfig)
    success: SuccessCriteria = field(default_factory=SuccessCriteria)
    paths: PathConfig = field(default_factory=PathConfig)
```

### Subtasks [1/3 used]

| ID | Subtask | Description |
|----|---------|--------------|
| C-1-1 | Config module | Single `DoseResponseConfig` composite dataclass as above |
