---
hypothesis_id: H-M1
hypothesis_type: EXISTENCE
phase: 3
date: 2026-08-26
author: yoon303@ust.ac.kr
---

# Config: H-M1 — Mypy-Guided Repair Loop

Applied: observational-pipeline-config (extended for repair loop)

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-E1 extension)
**Status**: Config classes verified from H-E1 base code (Read tool)
**Config Files Found**: `docs/youra_research/h-e1/03_config.md`
**Pattern Used**: dataclass

---

## Inherited Configuration (Base Hypothesis)

```python
# From: docs/youra_research/h-e1/03_config.md (verified field names)
@dataclass
class BaseExperimentConfig:
    model: str = "gpt-4o-mini"
    temperature: float = 0.8          # initial generation temperature
    max_tokens: int = 1024
    seeds: list = field(default_factory=lambda: [42, 123, 456])
    benchmarks: list = field(default_factory=lambda: ["mbpp+", "humaneval+"])
    mypy_timeout: int = 30
    mypy_flags: list = field(default_factory=lambda: [
        "--ignore-missing-imports",
        "--no-strict-optional",
    ])
    results_dir: Path = Path("docs/youra_research/h-e1/results")
    figures_dir: Path = Path("docs/youra_research/h-e1/figures")
    gate_pass: float = 0.10
    gate_borderline: float = 0.05
```

**Verified from**: `docs/youra_research/h-e1/03_config.md`

---

## C-A3-1: Experiment Runner Config [Complexity: Medium, Budget: 1]

### Configuration

```python
# docs/youra_research/h-m1/code/config.py
from dataclasses import dataclass, field
from pathlib import Path
import yaml


@dataclass
class ExperimentConfig:
    # Model settings
    model: str = "gpt-4o-mini"
    initial_temperature: float = 0.8    # inherited from H-E1 temperature
    repair_temperature: float = 0.0     # deterministic for repair rounds
    max_tokens: int = 2048              # non-standard: repair prompts are longer than generation prompts

    # Single seed (EXISTENCE — not sweeping seeds)
    seed: int = 42

    # Repair loop settings
    k_max: int = 5
    benchmarks: list = field(default_factory=lambda: ["mbpp+", "humaneval+"])

    # mypy settings (inherited from H-E1, timeout reduced for throughput)
    mypy_flags: list = field(default_factory=lambda: [
        "--ignore-missing-imports",
        "--no-strict-optional",
    ])
    mypy_timeout: int = 10              # non-standard: 10s vs H-E1's 30s — repair runs many more mypy calls

    # API retry settings
    max_retries: int = 3
    retry_base_delay: float = 1.0       # seconds, exponential backoff base

    # Paths
    results_dir: str = "docs/youra_research/h-m1/results"
    figures_dir: str = "docs/youra_research/h-m1/figures"

    @classmethod
    def from_yaml(cls, path: str = "docs/youra_research/h-m1/config.yaml") -> "ExperimentConfig":
        with open(path) as f:
            data = yaml.safe_load(f)
        return cls(**data)
```

### YAML Schema

```yaml
# docs/youra_research/h-m1/config.yaml
model: "gpt-4o-mini"
initial_temperature: 0.8
repair_temperature: 0.0
max_tokens: 2048

seed: 42

k_max: 5
benchmarks: ["mbpp+", "humaneval+"]

mypy_flags:
  - "--ignore-missing-imports"
  - "--no-strict-optional"
mypy_timeout: 10

max_retries: 3
retry_base_delay: 1.0

results_dir: "docs/youra_research/h-m1/results"
figures_dir: "docs/youra_research/h-m1/figures"
```

### Validation Notes

- `k_max`: int in [1, 10]
- `initial_temperature`: float in [0.0, 2.0]; must be > 0 for generation diversity
- `repair_temperature`: must be 0.0 (deterministic repair is the hypothesis design)
- `benchmarks`: subset of `["mbpp+", "humaneval+"]`
- `mypy_timeout`: int > 0; 10s is sufficient for single-file snippets
- `max_retries`: int in [1, 5]

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-A3-1 | ExperimentConfig | Dataclass + config.yaml for repair loop runner |

---

## C-A5-1: Visualization Config [Complexity: Medium, Budget: 1]

### Configuration

```python
# docs/youra_research/h-m1/code/config.py  (append to same file)
@dataclass
class VisualizationConfig:
    figures_dir: str = "docs/youra_research/h-m1/figures"
    dpi: int = 150
    figsize_bar: tuple = (10, 6)        # gate_metrics.png
    figsize_line: tuple = (10, 6)       # error trajectory per round
    figsize_heatmap: tuple = (14, 8)    # per-problem heatmap
    figsize_box: tuple = (12, 6)        # distribution box plots
    color_mbpp: str = "#2196F3"         # blue
    color_humaneval: str = "#FF9800"    # orange
    rounds: list = field(default_factory=lambda: [1, 2, 3, 4, 5])
```

### YAML Schema

```yaml
# append to config.yaml under key "visualization"
visualization:
  figures_dir: "docs/youra_research/h-m1/figures"
  dpi: 150
  figsize_bar: [10, 6]
  figsize_line: [10, 6]
  figsize_heatmap: [14, 8]
  figsize_box: [12, 6]
  color_mbpp: "#2196F3"
  color_humaneval: "#FF9800"
  rounds: [1, 2, 3, 4, 5]
```

### Validation Notes

- `dpi`: int in [72, 300]; 150 balances file size and legibility
- `figsize_*`: tuple of two positive floats (inches)
- `color_*`: valid CSS hex color string
- `rounds`: must be `list(range(1, k_max+1))` — matches ExperimentConfig.k_max

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-A5-1 | VisualizationConfig | Dataclass + YAML block for figure generation |

---

## C-A6-1: Results Schema + Environment Config [Complexity: Medium, Budget: 1]

### Output Schemas

```python
# docs/youra_research/h-m1/code/config.py  (append)
from typing import TypedDict


class PerRoundRecord(TypedDict):
    task_id: str
    benchmark: str
    round: int          # 1..k_max
    mypy_error_count: int
    exec_passed: bool
    repaired: bool      # True if round > 1


class BenchmarkSummary(TypedDict):
    benchmark: str
    n_problems: int
    n_with_initial_mypy_errors: int
    mean_errors_by_round: dict      # {1: {"mean": float, "std": float, "n": int}, ...}
    spearman_rho: float
    p_value: float
    round5_less_than_round1: bool
    gate_passed: bool
```

### File Layout

| File | Format | Schema |
|------|--------|--------|
| `results/{benchmark}_rounds.jsonl` | JSONL, one `PerRoundRecord` per line | per-round records |
| `results/summary.json` | JSON, list of `BenchmarkSummary` | aggregated stats |

### .env.example

```
# docs/youra_research/h-m1/.env.example
OPENAI_API_KEY=sk-...
```

### requirements.txt

```
# docs/youra_research/h-m1/requirements.txt
openai>=1.30.0
evalplus>=0.3.0
mypy>=1.9.0
scipy>=1.12.0
matplotlib>=3.8.0
python-dotenv>=1.0.0
```

### Validation Notes

- `PerRoundRecord.round`: int in [1, k_max]; round=1 is initial generation (repaired=False)
- `BenchmarkSummary.mean_errors_by_round`: keys are str(int) after JSON round-trip — parse accordingly
- `gate_passed`: True iff `spearman_rho < 0` and `p_value < 0.05` and `round5_less_than_round1 == True`
- `scipy` required for `spearmanr`; `python-dotenv` for loading `OPENAI_API_KEY` from `.env`

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-A6-1 | Results schema + env | TypedDict schemas, .env.example, requirements.txt |
