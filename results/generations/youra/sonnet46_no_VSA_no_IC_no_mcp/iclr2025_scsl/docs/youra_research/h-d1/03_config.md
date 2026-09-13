---
title: "Config: h-d1 — Directional Paradigm × Dataset Interaction Analysis"
hypothesis_id: h-d1
date: 2026-08-26
author: yoon303b@gmail.com
---

# Config: h-d1

Applied: Standard ML experiment constants + dataclass pattern

---

## Codebase Analysis (Serena)

**Project Type**: green-field (H-E1 code never ran; no base code to inspect)
**Status**: green-field - new config design
**Config Files Found**: None - new config
**Pattern Used**: hardcoded constants module (config.py)

---

## Full config.py

```python
# h-d1/code/config.py
from __future__ import annotations
from dataclasses import dataclass, field

# --- Constants ---

SEEDS: list[int] = [0, 1, 2, 3, 4]
PARADIGMS: list[str] = ['erm', 'moco', 'dino', 'barlowtwins']
PRIMARY_PARADIGMS: list[str] = ['erm', 'moco']
BATCH_SIZE: int = 256
FEATURE_DIM: int = 2048

# Paths
DATA_ROOT: str = './data/'
RESULTS_DIR: str = './docs/youra_research/h-d1/'
FIGURES_DIR: str = './docs/youra_research/h-d1/figures/'
WB_RESULTS_PATH: str = './docs/youra_research/h-e1/results/probe_results_waterbirds.json'
WB_RESULTS_FALLBACK: str = './docs/youra_research/h-e1/h-e1_ratios.csv'
WGA_GAPS_PATH: str = './docs/youra_research/h-e1/results/h-e1_stats.json'

# CelebA
CELEBA_MIN_GROUP_SIZE: int = 500
CELEBA_TASK_ATTR: str = 'Blond_Hair'
CELEBA_SPURIOUS_ATTR: str = 'Male'
CELEBA_SPLIT: str = 'test'
CELEBA_IMG_MEAN: list[float] = [0.485, 0.456, 0.406]
CELEBA_IMG_STD: list[float] = [0.229, 0.224, 0.225]
CELEBA_IMG_SIZE: int = 224

# Probe
PROBE_C: float = 1.0
PROBE_MAX_ITER: int = 1000
PROBE_SOLVER: str = 'lbfgs'

# Statistical thresholds
ALPHA_DIRECTIONAL: float = 0.05   # WB one-tailed gate
ALPHA_NULL: float = 0.1           # CelebA two-sided gate
BOOTSTRAP_N: int = 1000           # Pearson r CI


# --- Dataclasses ---

@dataclass
class CelebAConfig:
    root: str = DATA_ROOT
    min_per_group: int = CELEBA_MIN_GROUP_SIZE
    task_attr: str = CELEBA_TASK_ATTR
    spurious_attr: str = CELEBA_SPURIOUS_ATTR
    split: str = CELEBA_SPLIT
    batch_size: int = BATCH_SIZE
    img_size: int = CELEBA_IMG_SIZE
    img_mean: list[float] = field(default_factory=lambda: CELEBA_IMG_MEAN)
    img_std: list[float] = field(default_factory=lambda: CELEBA_IMG_STD)
    feature_cache_dir: str = RESULTS_DIR


@dataclass
class OrchestrationConfig:
    wb_results_path: str = WB_RESULTS_PATH
    wb_results_fallback: str = WB_RESULTS_FALLBACK
    wga_gaps_path: str = WGA_GAPS_PATH
    results_dir: str = RESULTS_DIR
    figures_dir: str = FIGURES_DIR
    celeba_features_cache: str = RESULTS_DIR  # {dir}/celeba_features_{paradigm}.pt
    celeba_probe_results: str = RESULTS_DIR + 'celeba_probe_results.json'
    h_d1_results: str = RESULTS_DIR + 'h_d1_results.json'
    # Error handling: 'raise' | 'warn_and_skip' | 'abort'
    missing_celeba_mode: str = 'warn_and_skip'
    missing_wb_mode: str = 'raise'
    # Non-standard: abort on WB missing because WB is required for primary test
    device: str = 'cuda'
```

---

## A-2: CelebA Data Pipeline [Complexity: 9, Budget: 1 subtask]

**Applied**: Standard torchvision CelebA group-balance pattern

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-2-1 | CelebA load + group balance | Implement load_celeba_balanced using CelebAConfig; validate min_per_group >= 500 |

### YAML Schema

```yaml
# celeba_config.yaml
celeba:
  root: "./data/"
  min_per_group: 500
  task_attr: "Blond_Hair"
  spurious_attr: "Male"
  split: "test"
  batch_size: 256
  img_size: 224
  img_mean: [0.485, 0.456, 0.406]
  img_std: [0.229, 0.224, 0.225]
  feature_cache_dir: "./docs/youra_research/h-d1/"
```

**Validation rules:**
- `min_per_group >= 100` (hard minimum; 500 is the research default)
- `split in ['train', 'valid', 'test', 'all']`
- `len(img_mean) == 3 and len(img_std) == 3`

---

## A-11: Orchestration [Complexity: 9, Budget: 1 subtask]

**Applied**: Standard cache-check + fallback path pattern

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-11-1 | run_experiment orchestration | Implement main() using OrchestrationConfig; cache checks for .pt files, fallback path for WB JSON, missing_celeba_mode guard |

### YAML Schema

```yaml
# orchestration_config.yaml
orchestration:
  wb_results_path: "./docs/youra_research/h-e1/results/probe_results_waterbirds.json"
  wb_results_fallback: "./docs/youra_research/h-e1/h-e1_ratios.csv"
  wga_gaps_path: "./docs/youra_research/h-e1/results/h-e1_stats.json"
  results_dir: "./docs/youra_research/h-d1/"
  figures_dir: "./docs/youra_research/h-d1/figures/"
  celeba_probe_results: "./docs/youra_research/h-d1/celeba_probe_results.json"
  h_d1_results: "./docs/youra_research/h-d1/h_d1_results.json"
  missing_celeba_mode: "warn_and_skip"
  missing_wb_mode: "raise"
  device: "cuda"
```

**Validation rules:**
- `missing_celeba_mode in ['raise', 'warn_and_skip', 'abort']`
- `missing_wb_mode in ['raise', 'warn_and_skip', 'abort']`
- `wb_results_path` must resolve (primary) or `wb_results_fallback` must exist
- `celeba_features_cache` directory must be writable before extraction
