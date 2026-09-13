---
hypothesis_id: H-E1
hypothesis_type: EXISTENCE
phase: 3
date: 2026-08-26
author: yoon303@ust.ac.kr
---

# Config: H-E1 — Type Error Prevalence in LLM-Generated Python Code

Applied: observational-pipeline-config (single fixed config, no hyperparameter tuning)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new config design
**Config Files Found**: None - new config
**Pattern Used**: dataclass + config.yaml

---

## C-E5-1: Experiment Configuration [Complexity: 2, Budget: 1 subtask]

### Configuration (Python Dataclass)

```python
# code/config.py
from dataclasses import dataclass, field
from pathlib import Path
import yaml


@dataclass
class ExperimentConfig:
    # Model
    model: str = "gpt-4o-mini"
    temperature: float = 0.8
    max_tokens: int = 1024

    # Seeds
    seeds: list = field(default_factory=lambda: [42, 123, 456])

    # Benchmarks
    benchmarks: list = field(default_factory=lambda: ["mbpp+", "humaneval+"])

    # mypy
    mypy_timeout: int = 30
    mypy_flags: list = field(default_factory=lambda: [
        "--ignore-missing-imports",
        "--no-strict-optional",
    ])

    # Paths
    results_dir: Path = Path("docs/youra_research/h-e1/results")
    figures_dir: Path = Path("docs/youra_research/h-e1/figures")

    # Gate thresholds
    gate_pass: float = 0.10
    gate_borderline: float = 0.05

    @classmethod
    def from_yaml(cls, path: str = "docs/youra_research/h-e1/config.yaml") -> "ExperimentConfig":
        with open(path) as f:
            data = yaml.safe_load(f)
        data["results_dir"] = Path(data["results_dir"])
        data["figures_dir"] = Path(data["figures_dir"])
        return cls(**data)
```

### config.yaml

```yaml
# docs/youra_research/h-e1/config.yaml
model: "gpt-4o-mini"
temperature: 0.8
max_tokens: 1024

seeds: [42, 123, 456]
benchmarks: ["mbpp+", "humaneval+"]

mypy_timeout: 30
mypy_flags:
  - "--ignore-missing-imports"
  - "--no-strict-optional"

results_dir: "docs/youra_research/h-e1/results"
figures_dir: "docs/youra_research/h-e1/figures"

gate_pass: 0.10
gate_borderline: 0.05
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-E5-1 | ExperimentConfig | Dataclass + config.yaml with all defaults; `from_yaml()` loader |

---

## C-E5-2: Figure Configuration [Complexity: 2, Budget: 1 subtask]

### Configuration (Python Dataclass)

```python
# Inline in code/visualize.py — no separate file needed
from dataclasses import dataclass


@dataclass
class FigureConfig:
    figsize: tuple = (8, 5)
    dpi: int = 150
    gate_threshold: float = 0.10  # horizontal threshold line in gate_metrics plot

    # Output filenames (relative to figures_dir)
    gate_metrics:     str = "gate_metrics.png"
    error_type_dist:  str = "error_type_dist.png"
    error_count_hist: str = "error_count_hist.png"
    seed_consistency: str = "seed_consistency.png"


FIG = FigureConfig()  # module-level singleton; override in tests if needed
```

**Figure specs:**

| Filename | Chart type | Key detail |
|----------|------------|------------|
| `gate_metrics.png` | Bar chart | std error bars; horizontal line at y=0.10 |
| `error_type_dist.png` | Bar chart | mypy error categories |
| `error_count_hist.png` | Histogram | error counts per failing solution |
| `seed_consistency.png` | Box plot | type_error_fraction across 3 seeds |

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-E5-2 | FigureConfig | Dataclass with size/DPI/paths; module-level singleton `FIG` |
