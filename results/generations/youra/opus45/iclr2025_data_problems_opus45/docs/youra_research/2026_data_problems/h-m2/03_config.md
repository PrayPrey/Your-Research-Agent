# Configuration: H-M2 Deep Network Metric Decoupling

**Date:** 2026-03-26
**Hypothesis:** H-M2 (MECHANISM, INCREMENTAL)
**Gate:** MUST_WORK
**Prerequisites:** H-M1 (VALIDATED), H-E1 (VALIDATED)

Applied: mechanism-verification-incremental (reuse base infrastructure, extend analysis layer)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (extends H-E1 and H-M1)
**Status**: config classes verified from actual base code
**Config Files Found**:
- `h-e1/code/config.py` — `ExperimentConfig` dataclass (verified)
- `h-m1/code/config.py` — `HM1Config` dataclass (verified)
**Pattern Used**: dataclass

---

## Inherited Configuration (Base Hypothesis)

### Config Classes (From Actual Code)

```python
# From: h-e1/code/config.py (ACTUAL CODE)
@dataclass
class ExperimentConfig:
    data_root: str = './data'
    train_subset_size: int = 5000
    loo_test_size: int = 100          # field name: loo_test_size (not test_subset_size)
    subset_seed: int = 42
    train_batch_size: int = 128
    test_batch_size: int = 256
    epochs: int = 200
    lr: float = 0.1
    momentum: float = 0.9
    weight_decay: float = 5e-4
    lr_milestones: List[int] = field(default_factory=lambda: [100, 150])
    lr_gamma: float = 0.1
    n_loo_retrains: int = 10
    methods: List[str] = field(default_factory=lambda: ['TRAK', 'TracIn', 'IF', 'FastIF'])
    compute_budgets: List[int] = field(default_factory=lambda: [10, 25, 50, 75, 100])
    method_seeds: List[int] = field(default_factory=lambda: [0, 1, 2])  # field: method_seeds
    n_bootstrap: int = 1000
    confidence_level: float = 0.95
    results_dir: str = './results'
    figures_dir: str = './figures'
    checkpoint_dir: str = './checkpoints'

# From: h-m1/code/config.py (ACTUAL CODE)
@dataclass
class HM1Config:
    data_root: str = './data'
    he1_checkpoint: str = '../../h-e1/code/checkpoints/model_seed0_final.pt'
    he1_code_path: str = '../../h-e1/code'
    train_subset_size: int = 5000
    test_subset_size: int = 100       # field name: test_subset_size
    subset_seed: int = 42
    feature_dim: int = 512
    n_classes: int = 10
    C: float = 100.0
    lr_solver: str = 'lbfgs'
    lr_max_iter: int = 1000
    methods: List[str] = field(default_factory=lambda: ['TRAK', 'TracIn', 'IF', 'FastIF'])
    compute_budgets: List[int] = field(default_factory=lambda: [10, 25, 50, 75, 100])
    seeds: List[int] = field(default_factory=lambda: [0, 1, 2])  # field: seeds (not method_seeds)
    n_bootstrap: int = 1000
    partial_corr_threshold: float = 0.95  # H-M1 gate: MUST be >= 0.95
    r2_threshold: float = 0.95            # H-M1 gate: MUST be >= 0.95
    results_dir: str = './results'
    figures_dir: str = './figures'
```

**Verified from**: `h-e1/code/config.py` and `h-m1/code/config.py` actual implementation.

**Key differences from specs**:
- H-E1 uses `loo_test_size` (not `test_subset_size`) and `method_seeds` (not `seeds`)
- H-M1 uses `test_subset_size` and `seeds`
- H-M2 follows H-M1 naming convention (`test_subset_size`, `seeds`) for consistency

---

## A-1: Project Setup [Complexity: 6, Budget: 1 subtask]

Applied: Standard PyTorch defaults

### Configuration

```python
# h-m2/code/config.py
from dataclasses import dataclass, field
from typing import List
import os


@dataclass
class HM2Config:
    # Data (matching H-M1 naming conventions, verified from h-m1/code/config.py)
    data_root: str = './data'
    train_subset_size: int = 5000
    test_subset_size: int = 100
    subset_seed: int = 42

    # External paths
    he1_code_path: str = '../../h-e1/code'
    hm1_code_path: str = '../../h-m1/code'
    he1_checkpoint: str = '../../h-e1/code/checkpoints/model_seed0_final.pt'
    loo_cache_path: str = '../../h-e1/code/results/loo_cache.npy'
    hm1_results_path: str = '../../h-m1/results/metrics.csv'

    # Experiment (matching H-E1/H-M1 exactly)
    methods: List[str] = field(default_factory=lambda: ['TRAK', 'TracIn', 'IF', 'FastIF'])
    compute_budgets: List[int] = field(default_factory=lambda: [10, 25, 50, 75, 100])
    seeds: List[int] = field(default_factory=lambda: [0, 1, 2])

    # Gate thresholds (H-M2 MUST_WORK: deep network must show LOWER values)
    # Non-standard: inverted from H-M1 — H-M2 passes when values DROP below threshold
    r2_threshold: float = 0.80        # R²_deep must be BELOW this (vs H-M1's 0.95 floor)
    partial_corr_threshold: float = 0.85  # corr must be BELOW this (vs H-M1's 0.95 floor)
    delta_r2_threshold: float = 0.15  # Δ_R² = R²_convex - R²_deep must exceed this

    # H-M1 convex baseline (hardcoded from validated H-M1 results)
    hm1_r2_rho_r: float = 0.95
    hm1_r2_rho_m: float = 0.95
    hm1_partial_corr: dict = field(default_factory=lambda: {
        10: 0.9961, 25: 0.9945, 50: 0.9899, 75: 0.9905, 100: 0.9916
    })

    # I/O
    results_dir: str = './results'
    figures_dir: str = './figures'


def get_config() -> HM2Config:
    """Get configuration, create output directories."""
    cfg = HM2Config()
    os.makedirs(cfg.results_dir, exist_ok=True)
    os.makedirs(cfg.figures_dir, exist_ok=True)
    return cfg
```

### Subtasks [1/1 used]
| ID | Subtask | Description |
|----|---------|-------------|
| C-1-1 | HM2Config | Implement config.py with HM2Config dataclass and get_config() |

---

## A-2 through A-12: Shared Configuration

All tasks A-2 through A-12 consume `HM2Config` from `config.py`. No additional config classes are needed. Key parameter groups:

### Data & Model Parameters
| Parameter | Value | Source |
|-----------|-------|--------|
| `train_subset_size` | 5000 | Matched to H-E1/H-M1 |
| `test_subset_size` | 100 | Matched to H-E1/H-M1 |
| `subset_seed` | 42 | Matched to H-E1/H-M1 |

### Experiment Parameters
| Parameter | Value | Source |
|-----------|-------|--------|
| `methods` | ['TRAK','TracIn','IF','FastIF'] | Matched to H-E1/H-M1 |
| `compute_budgets` | [10, 25, 50, 75, 100] | Matched to H-E1/H-M1 |
| `seeds` | [0, 1, 2] | Matched to H-M1 `seeds` field |

### Gate Thresholds
| Parameter | Value | Direction | Comparison |
|-----------|-------|-----------|------------|
| `r2_threshold` | 0.80 | BELOW (deep must drop) | H-M1 floor: 0.95 |
| `partial_corr_threshold` | 0.85 | BELOW (deep must drop) | H-M1 floor: 0.95 |
| `delta_r2_threshold` | 0.15 | ABOVE (contrast must exceed) | H-M1 minus H-M2 |

### Subtasks [4/4 used]
| ID | Subtask | Description |
|----|---------|-------------|
| C-2-1 | Data/Model Loading | Wire HM2Config into load_deep_model and load_loo_cache |
| C-3-1 | Attribution Compute | Wire HM2Config.methods/budgets/seeds into compute_deep_attribution_scores |
| C-4-1 | Metrics Builder | Wire HM2Config into build_deep_metrics_df delegating to h-m1 |
| C-5-1 | Gate Evaluation | Wire r2_threshold/partial_corr_threshold/delta_r2_threshold into evaluate_gate |

---

## Gate Condition Summary

```python
# Pass conditions (all must hold)
gate_pass = (
    r2_deep['r2_rho_r'] < cfg.r2_threshold        # < 0.80
    or r2_deep['r2_rho_m'] < cfg.r2_threshold      # < 0.80
) and (
    min(partial_corr_deep.values()) < cfg.partial_corr_threshold  # < 0.85
) and (
    (cfg.hm1_r2_rho_r - r2_deep['r2_rho_r']) > cfg.delta_r2_threshold  # > 0.15
    or (cfg.hm1_r2_rho_m - r2_deep['r2_rho_m']) > cfg.delta_r2_threshold
)
```
