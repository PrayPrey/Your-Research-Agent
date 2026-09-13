# Config: H-M2 (Weighted Ensemble SA Metric Correlation)

**Type**: MECHANISM | **Budget**: 0 subtasks (all Low complexity)

Applied: Standard PyTorch/Python frozen-dataclass singleton pattern (KB search returned no domain-relevant hits — dataset/LaTeX/unrelated results only; reused h-m1's existing config convention instead).

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (h-m1)
**Status**: Serena tool unavailable (no active project registered) — used Read tool directly on actual h-m1 code, per architecture doc's documented fallback.
**Config Files Found**: `docs/youra_research/h-m1/code/config.py` (actual implementation)
**Pattern Used**: `@dataclass(frozen=True)` singleton instantiated as module-level `CONFIG = Config()`

## Inherited Configuration (Base Hypothesis)

```python
# From: docs/youra_research/h-m1/code/config.py (ACTUAL CODE, verified)
@dataclass(frozen=True)
class Config:
    sa_timeout_sec: int = 30
    test_timeout_sec: int = 5
    results_dir: str = "results"
    figures_dir: str = "figures"
    completions_path: str = "data/completions.jsonl"
    corr_threshold: float = 0.35
    alpha: float = 0.05
    min_samples: int = 400
    seed: int = 42
```

H-M2 does not subclass this — it is a sibling experiment reusing only `results_dir`, `figures_dir`, `alpha`, `seed` field names/values for consistency. No direct import (separate hypothesis folder).

## A-1: Config Module [Complexity: Low, Budget: 0]

**Applied**: Standard frozen-dataclass singleton (matches h-m1 convention)

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Config:
    h_m1_data_path: str = "../h-m1/results/h_m1_data.csv"
    results_dir: str = "results"
    figures_dir: str = "figures"
    weight_grid_step: float = 0.1
    weight_min: float = 0.1
    weight_max: float = 0.9
    max_r_individual: float = 0.873  # pylint r from h-m1, gate baseline
    alpha: float = 0.05
    seed: int = 42

CONFIG = Config()
```

**Non-standard**: `h_m1_data_path` points to `results/h_m1_data.csv` (not PRD's `data/sa_metrics_combined.csv`) — verified actual h-m1 output path/filename from base code, per architecture doc's Serena finding. `max_r_individual` fixed at h-m1's validated pylint correlation (0.873), used directly as gate threshold, not tuned.

### Subtasks [0/0 used]

No subtasks — Low complexity, single fixed config, no decomposition needed.
