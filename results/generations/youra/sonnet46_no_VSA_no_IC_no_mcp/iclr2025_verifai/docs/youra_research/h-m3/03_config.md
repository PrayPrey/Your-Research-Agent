# Config: h-m3

Applied: dataclass-extension pattern, YAML-loadable config pattern, multi-dataset list pattern

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (extending h-m2)
**Status**: Config classes verified from actual h-m2 code
**Config Files Found**: `docs/youra_research/h-m2/code/config.py`
**Pattern Used**: dataclass

---

## Inherited Configuration (Base Hypothesis)

Verified from `docs/youra_research/h-m2/code/config.py` (actual implementation):

```python
# Actual h-m2 ExperimentConfig fields (verified)
model: str = "gpt-4o-mini"
initial_temperature: float = 0.8
repair_temperature: float = 0.0
max_tokens: int = 2048
seed: int = 42                  # ← singular in h-m2; h-m3 extends to seeds: list
k_max: int = 5
benchmark: str = "humaneval+"   # ← singular in h-m2; h-m3 extends to datasets: list
mypy_flags: list = ["--ignore-missing-imports", "--no-strict-optional"]
mypy_timeout: int = 10
max_retries: int = 3
retry_base_delay: float = 1.0
results_dir: str = "docs/youra_research/h-m2/results"
figures_dir: str = "docs/youra_research/h-m2/figures"
checkpoint_path: str = "docs/youra_research/h-m2/results/checkpoint.json"
```

Key changes for h-m3:
- `seed` (int) → `seeds` (list of int) for multi-seed runs
- `benchmark` (str) → `datasets` (list of str) for multi-benchmark support
- Added `conditions`, `output_dir`, `--no-error-summary` mypy flag, `wandb_project`

---

## A-5: MBPP+ Integration [Complexity: 9, Budget: 1 subtask]

Applied: multi-dataset config list pattern

### Configuration

```python
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
import yaml


@dataclass
class ExperimentConfig:
    # Model
    model: str = "gpt-4o-mini"
    initial_temperature: float = 0.8
    repair_temperature: float = 0.0
    max_tokens: int = 2048

    # Multi-seed, multi-dataset (h-m3 extensions of h-m2 singular fields)
    seeds: list = field(default_factory=lambda: [42, 123, 456])
    datasets: list = field(default_factory=lambda: ["humaneval+", "mbpp+"])
    conditions: list = field(default_factory=lambda: ["A", "B"])

    # Repair loop (inherited from h-m2)
    k_max: int = 5
    max_retries: int = 3
    retry_base_delay: float = 1.0

    # Mypy (added --no-error-summary vs h-m2)
    mypy_flags: list = field(default_factory=lambda: [
        "--ignore-missing-imports",
        "--no-strict-optional",
        "--no-error-summary",
    ])
    mypy_timeout: int = 10

    # Paths
    output_dir: str = "docs/youra_research/h-m3/results"
    figures_dir: str = "docs/youra_research/h-m3/figures"
    checkpoint_path: str = "docs/youra_research/h-m3/results/checkpoint.json"

    # Optional WandB
    wandb_project: Optional[str] = None

    @classmethod
    def from_yaml(cls, path: str) -> "ExperimentConfig":
        with open(path) as f:
            data = yaml.safe_load(f)
        return cls(**data)
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-5-1 | Dataset config extension | `datasets` list field covering humaneval+ and mbpp+; YAML-loadable |

---

## A-6: Visualization [Complexity: 11, Budget: 2 subtasks]

Applied: figure layout schema pattern, output path config pattern

### Configuration

```python
# Figure layout schema — hardcoded dict (no tuning needed)
FIGURE_CONFIG = {
    "f1_pass_at_1_comparison": {
        "figsize": (8, 5),
        "filename": "f1_pass_at_1_comparison.png",
        "dpi": 150,
    },
    "f2_repair_trajectory": {
        "figsize": (8, 5),
        "filename": "f2_repair_trajectory.png",
        "dpi": 150,
    },
    "f3_delta_distribution": {
        "figsize": (7, 5),
        "filename": "f3_delta_distribution.png",
        "dpi": 150,
    },
    "f4_mypy_error_by_round": {
        "figsize": (8, 5),
        "filename": "f4_mypy_error_by_round.png",
        "dpi": 150,
    },
    "f5_token_count_comparison": {
        "figsize": (8, 5),
        "filename": "f5_token_count_comparison.png",
        "dpi": 150,
    },
}
```

Output paths derive from `ExperimentConfig.figures_dir` at runtime:
```python
# In visualize.py
out_path = Path(cfg.figures_dir) / FIGURE_CONFIG[name]["filename"]
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-6-1 | Figure layout schema | `FIGURE_CONFIG` dict with figsize/filename/dpi per figure |
| C-6-2 | Output path config | `figures_dir` field in `ExperimentConfig`; path resolved at runtime |

---

## YAML Config Template

```yaml
# config.yaml — h-m3
model: "gpt-4o-mini"
initial_temperature: 0.8
repair_temperature: 0.0
max_tokens: 2048

seeds: [42, 123, 456]
datasets: ["humaneval+", "mbpp+"]
conditions: ["A", "B"]

k_max: 5
max_retries: 3
retry_base_delay: 1.0

mypy_flags:
  - "--ignore-missing-imports"
  - "--no-strict-optional"
  - "--no-error-summary"
mypy_timeout: 10

output_dir: "docs/youra_research/h-m3/results"
figures_dir: "docs/youra_research/h-m3/figures"
checkpoint_path: "docs/youra_research/h-m3/results/checkpoint.json"

wandb_project: null
```
