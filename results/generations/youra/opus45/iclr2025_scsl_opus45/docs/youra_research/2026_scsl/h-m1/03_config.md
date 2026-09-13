# Configuration Design: H-M1 (Curvature Timing Analysis)

**Hypothesis:** H-M1 - Minority samples exhibit delayed curvature stabilization
**Type:** MECHANISM (extends H-E1)
**Date:** 2026-04-14

Applied: Standard PyTorch dataclass config pattern (Archon KB: no domain-specific match; using research-standard defaults)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Config fields verified from H-E1 actual code (provided in task brief)
**Config Files Found**: `docs/youra_research/20260414_scsl/h-e1/code/config.py`
**Pattern Used**: dataclass

---

## Inherited Configuration (Base Hypothesis)

### Config Classes (From Actual H-E1 Code)

```python
# From: docs/youra_research/20260414_scsl/h-e1/code/config.py (ACTUAL CODE)
@dataclass
class Config:
    # Dataset
    data_root: str = "./data/waterbirds"
    dataset: str = "waterbirds"
    num_workers: int = 4
    pin_memory: bool = True

    # Preprocessing
    train_crop_size: int = 224
    eval_resize: int = 256
    eval_crop_size: int = 224
    img_mean: Tuple[float, float, float] = (0.485, 0.456, 0.406)
    img_std: Tuple[float, float, float] = (0.229, 0.224, 0.225)

    # Model
    model_name: str = "resnet50"
    num_classes: int = 2

    # Training
    seed: int = 42
    epochs: int = 20
    trajectory_epochs: int = 5   # H-E1 default (CHANGED to 20 in H-M1)
    batch_size: int = 128
    lr: float = 0.001
    momentum: float = 0.9
    weight_decay: float = 0.0001

    # Evaluation
    n_folds: int = 5
    auroc_threshold: float = 0.75
    lr_clf_max_iter: int = 1000

    # Output
    output_dir: str = "./outputs"
    figures_dir: str = "./figures"
    fig_dpi: int = 300
```

### H-E1 Fields: Kept vs Modified

| Field | H-E1 Default | H-M1 | Change |
|-------|-------------|------|--------|
| data_root | `"./data/waterbirds"` | same | kept |
| dataset | `"waterbirds"` | same | kept |
| num_workers | 4 | same | kept |
| pin_memory | True | same | kept |
| train_crop_size | 224 | same | kept |
| eval_resize | 256 | same | kept |
| eval_crop_size | 224 | same | kept |
| img_mean | (0.485, 0.456, 0.406) | same | kept |
| img_std | (0.229, 0.224, 0.225) | same | kept |
| model_name | `"resnet50"` | same | kept |
| num_classes | 2 | same | kept |
| seed | 42 | removed (replaced by seeds list) | modified |
| epochs | 20 | 20 | kept |
| trajectory_epochs | 5 | **20** | CHANGED |
| batch_size | 128 | same | kept |
| lr | 0.001 | same | kept |
| momentum | 0.9 | same | kept |
| weight_decay | 0.0001 | same | kept |
| n_folds | 5 | removed (not used in H-M1) | dropped |
| auroc_threshold | 0.75 | removed (not used in H-M1) | dropped |
| lr_clf_max_iter | 1000 | removed (not used in H-M1) | dropped |
| output_dir | `"./outputs"` | same | kept |
| figures_dir | `"./figures"` | same | kept |
| fig_dpi | 300 | same | kept |

---

## A-2: Extend Config [Complexity: 6, Budget: 4 subtasks]

Applied: multi-seed list pattern, curvature analysis config pattern

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass, field
from typing import List, Tuple


@dataclass
class Config:
    # ── Dataset (unchanged from H-E1) ────────────────────────────────────────
    data_root: str = ".data_cache/datasets/waterbirds/waterbird_complete95_forest2water2"
    dataset: str = "waterbirds"
    num_workers: int = 4
    pin_memory: bool = True

    # ── Preprocessing (unchanged from H-E1) ──────────────────────────────────
    train_crop_size: int = 224
    eval_resize: int = 256
    eval_crop_size: int = 224
    img_mean: Tuple[float, float, float] = (0.485, 0.456, 0.406)
    img_std: Tuple[float, float, float] = (0.229, 0.224, 0.225)

    # ── Model (unchanged from H-E1) ───────────────────────────────────────────
    model_name: str = "resnet50"
    num_classes: int = 2

    # ── Training (extended from H-E1) ────────────────────────────────────────
    epochs: int = 20
    # trajectory_epochs: CHANGED 5 → 20 to track ALL epochs for curvature
    trajectory_epochs: int = 20
    batch_size: int = 128
    lr: float = 0.001
    momentum: float = 0.9
    weight_decay: float = 0.0001

    # ── Multi-seed (NEW) ─────────────────────────────────────────────────────
    # Replaces single `seed: int = 42` from H-E1; 5 seeds for ≥70% pass-rate test
    seeds: List[int] = field(default_factory=lambda: [42, 123, 456, 789, 1011])

    # ── Curvature Parameters (NEW) ────────────────────────────────────────────
    # Default sigma=1.0 per FR-3.3 (PRD); balances noise reduction vs. temporal resolution
    smoothing_sigma: float = 1.0
    # Threshold -0.002 per FR-4.1; marks transition from convex to stable curvature
    curvature_threshold: float = -0.002
    # consecutive_epochs=2 per FR-4.2; reduces false positives from transient sign flips
    consecutive_epochs: int = 2

    # ── Gate Parameters (NEW) ────────────────────────────────────────────────
    # timing_gap_threshold=3.0 per success criterion (FR-5, FR-6)
    timing_gap_threshold: float = 3.0
    # pass_rate_threshold=0.70 per gate criterion (FR-6.1)
    pass_rate_threshold: float = 0.70

    # ── Output (unchanged from H-E1) ─────────────────────────────────────────
    output_dir: str = "./outputs"
    figures_dir: str = "./figures"
    fig_dpi: int = 300


def get_config() -> Config:
    return Config()
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-2-1 | Remove unused H-E1 fields | Drop n_folds, auroc_threshold, lr_clf_max_iter, seed (single) |
| C-2-2 | Add multi-seed field | seeds: List[int] with factory default [42, 123, 456, 789, 1011] |
| C-2-3 | Add curvature params | smoothing_sigma, curvature_threshold, consecutive_epochs |
| C-2-4 | Add gate params | timing_gap_threshold, pass_rate_threshold |

---

## YAML Schema Representation

```yaml
# H-M1 Config Schema
dataset:
  data_root: ".data_cache/datasets/waterbirds/waterbird_complete95_forest2water2"
  dataset: "waterbirds"
  num_workers: 4
  pin_memory: true

preprocessing:
  train_crop_size: 224
  eval_resize: 256
  eval_crop_size: 224
  img_mean: [0.485, 0.456, 0.406]
  img_std: [0.229, 0.224, 0.225]

model:
  model_name: "resnet50"
  num_classes: 2

training:
  epochs: 20
  trajectory_epochs: 20    # extended from H-E1's 5
  batch_size: 128
  lr: 0.001
  momentum: 0.9
  weight_decay: 0.0001

multi_seed:
  seeds: [42, 123, 456, 789, 1011]

curvature:
  smoothing_sigma: 1.0
  curvature_threshold: -0.002
  consecutive_epochs: 2

gate:
  timing_gap_threshold: 3.0
  pass_rate_threshold: 0.70

output:
  output_dir: "./outputs"
  figures_dir: "./figures"
  fig_dpi: 300
```

---

## Ablation Parameter Variants

Ablation varies `smoothing_sigma` only; all other parameters remain at defaults.

| Variant | smoothing_sigma | curvature_threshold | consecutive_epochs |
|---------|----------------|--------------------|--------------------|
| sigma_05 | 0.5 | -0.002 | 2 |
| sigma_10 (default) | 1.0 | -0.002 | 2 |
| sigma_15 | 1.5 | -0.002 | 2 |
| sigma_20 | 2.0 | -0.002 | 2 |

Usage in code (A-10):
```python
# Run ablation over sigma values
ABLATION_SIGMAS = [0.5, 1.0, 1.5, 2.0]

for sigma in ABLATION_SIGMAS:
    cfg = Config(smoothing_sigma=sigma)
    # run analysis with cfg
```

---

## Default Values Rationale (Non-Standard Only)

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| trajectory_epochs | 20 | Changed from H-E1's 5; must cover all training epochs for curvature analysis |
| smoothing_sigma | 1.0 | Per FR-3.3 PRD specification; standard Gaussian noise reduction for numerical derivatives |
| curvature_threshold | -0.002 | Per FR-4.1 PRD specification; empirically tuned boundary for convex-to-stable transition |
| consecutive_epochs | 2 | Per FR-4.2 PRD specification; prevents false positives from single-epoch fluctuations |
| timing_gap_threshold | 3.0 | Gate criterion from H-M1 hypothesis statement (≥3 epoch gap) |
| pass_rate_threshold | 0.70 | Gate criterion from H-M1 hypothesis statement (≥70% of seeds) |
| seeds | [42, 123, 456, 789, 1011] | 5 seeds minimum for percentage-based criterion (need 4/5 = 80% to pass at 70% threshold) |

---

*Generated by Phase 3 Configuration Planning*
*Base: H-E1 config.py (verified from actual code)*
*Next: Phase 4 Implementation*
