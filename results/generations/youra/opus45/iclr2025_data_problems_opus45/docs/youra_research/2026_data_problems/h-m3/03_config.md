# Configuration: H-M3 Method Disagreement Analysis

**Date:** 2026-03-26
**Hypothesis:** H-M3 (MECHANISM, INCREMENTAL)
**Gate:** SHOULD_WORK
**Prerequisites:** H-M2 (VALIDATED), H-E1 (VALIDATED)

Applied: mechanism-verification-incremental (reuse base infrastructure, extend analysis layer)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (extends H-E1)
**Status**: config classes verified from actual base code via direct file read
**Config Files Found**:
- `h-e1/code/config.py` — `ExperimentConfig` dataclass (verified, ACTUAL CODE)
- `h-m2/03_config.md` — `HM2Config` (reference only)
**Pattern Used**: dataclass

---

## Inherited Configuration (Base Hypothesis)

```python
# From: h-e1/code/config.py (ACTUAL CODE - verified)
@dataclass
class ExperimentConfig:
    data_root: str = './data'
    train_subset_size: int = 5000
    loo_test_size: int = 100          # field name: loo_test_size (not test_subset_size)
    subset_seed: int = 42
    train_batch_size: int = 128
    test_batch_size: int = 256
    methods: List[str] = field(default_factory=lambda: ['TRAK', 'TracIn', 'IF', 'FastIF'])
    compute_budgets: List[int] = field(default_factory=lambda: [10, 25, 50, 75, 100])
    method_seeds: List[int] = field(default_factory=lambda: [0, 1, 2])  # field: method_seeds
    results_dir: str = './results'
    figures_dir: str = './figures'
    checkpoint_dir: str = './checkpoints'
```

**Verified from**: `h-e1/code/config.py` (actual implementation)
**Key field names**: `loo_test_size` (not `test_subset_size`), `method_seeds` (not `seeds`)

---

## A-1: Setup & Config [Complexity: 6, Budget: 1 subtask]

Applied: Standard PyTorch dataclass config pattern

### Configuration

```python
# h-m3/code/config.py
from dataclasses import dataclass, field
from typing import List
import os


@dataclass
class H3Config:
    # Data (matching H-E1 naming conventions - verified from h-e1/code/config.py)
    data_root: str = './data'
    train_subset_size: int = 5000
    loo_test_size: int = 100           # matches H-E1 field name exactly
    subset_seed: int = 42

    # Attribution (matching H-E1 exactly)
    methods: List[str] = field(default_factory=lambda: ['TRAK', 'TracIn', 'IF', 'FastIF'])
    compute_budgets: List[int] = field(default_factory=lambda: [10, 25, 50, 75, 100])
    method_seeds: List[int] = field(default_factory=lambda: [0, 1, 2])  # matches H-E1 field name

    # Jaccard Analysis (gate metric)
    top_k: int = 50
    jaccard_threshold: float = 0.70    # gate: min(Jaccard) must be BELOW this

    # Persistence Analysis
    persistence_threshold: float = 0.60  # Non-standard: method must lead >60% of budgets

    # External Paths
    base_code_dir: str = '../h-e1/code'
    checkpoint_path: str = '../h-e1/code/checkpoints/model_seed0_final.pt'
    loo_cache_path: str = '../h-e1/code/results/loo_cache.npy'

    # I/O
    results_dir: str = './results'
    figures_dir: str = './figures'


def get_config() -> H3Config:
    """Get configuration, create output directories."""
    cfg = H3Config()
    os.makedirs(cfg.results_dir, exist_ok=True)
    os.makedirs(cfg.figures_dir, exist_ok=True)
    return cfg
```

### Subtasks [1/1 used]
| ID | Subtask | Description |
|----|---------|-------------|
| C-1-1 | H3Config | Implement config.py with H3Config dataclass and get_config() |

---

## A-2 through A-10: Shared Configuration

All tasks A-2 through A-10 consume `H3Config` from `config.py`. No additional config classes needed.

### Key Parameter Groups

**Data & Model**
| Parameter | Value | Source |
|-----------|-------|--------|
| `train_subset_size` | 5000 | Matched to H-E1 |
| `loo_test_size` | 100 | Matched to H-E1 (field name verified) |
| `subset_seed` | 42 | Matched to H-E1 |

**Attribution**
| Parameter | Value | Source |
|-----------|-------|--------|
| `methods` | ['TRAK','TracIn','IF','FastIF'] | Matched to H-E1 |
| `compute_budgets` | [10, 25, 50, 75, 100] | Matched to H-E1 |
| `method_seeds` | [0, 1, 2] | Matched to H-E1 (field name: `method_seeds`) |

**Gate & Analysis**
| Parameter | Value | Direction |
|-----------|-------|-----------|
| `top_k` | 50 | Fixed (from Phase 2C spec) |
| `jaccard_threshold` | 0.70 | BELOW (gate passes if min(Jaccard) < 0.70) |
| `persistence_threshold` | 0.60 | ABOVE (method must lead >60% of budgets) |

### Subtasks [4/4 used]
| ID | Subtask | Description |
|----|---------|-------------|
| C-2-1 | Data/Model Loading | Wire H3Config into load_model and load_data using H-E1 indices |
| C-3-1 | Attribution Compute | Wire H3Config.methods/compute_budgets/method_seeds into load_or_compute_scores |
| C-4-1 | Jaccard Analyzer | Wire H3Config.top_k/jaccard_threshold into JaccardAnalyzer |
| C-5-1 | Gate + Results | Wire jaccard_threshold/persistence_threshold into gate check and serialization |

---

## Gate Condition Summary

```python
# Pass condition: any budget achieves min pairwise Jaccard below threshold
gate_pass = any(
    jaccard_by_budget[b]['min'] < cfg.jaccard_threshold  # < 0.70
    for b in cfg.compute_budgets
)
```
