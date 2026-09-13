---
title: "Config: h-e1 — Spurious/Task Probe Accuracy Ratio Study"
hypothesis_id: h-e1
hypothesis_type: EXISTENCE
date: 2026-08-26
author: yoon303b@gmail.com
---

# Config: h-e1

Applied: Izmailov et al. 2022 LogisticRegression defaults (C=1.0, max_iter=1000, lbfgs)
Applied: ImageNet normalization statistics for ResNet-50 preprocessing (mean=[0.485,0.456,0.406], std=[0.229,0.224,0.225])

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field — no existing code to analyze
**Config Files Found**: None — new config
**Pattern Used**: hardcoded constants (module-level)

---

## config.py

```python
# h-e1/code/config.py

# Experiment
SEEDS = [0, 1, 2, 3, 4]
PARADIGMS = ['erm', 'moco', 'dino', 'barlowtwins']
BATCH_SIZE = 256

# Paths
DATA_ROOT = './data/'
RESULTS_DIR = './docs/youra_research/h-e1/results/'
FIGURES_DIR = './docs/youra_research/h-e1/figures/'
LOG_PATH = './docs/youra_research/h-e1/logs/h-e1_run.log'

# Probe (LogisticRegression)
PROBE_C = 1.0
PROBE_MAX_ITER = 1000
PROBE_SOLVER = 'lbfgs'
FEATURE_DIM = 2048

# Statistics
BONFERRONI_N = 6          # C(4,2) pairs
GATE_ALPHA = 0.05
GATE_MIN_DIFF = 0.02

# Dataset
DATASET_NAME = 'waterbirds'
DATASET_DOWNLOAD = True

# Transform
RESIZE = 256
CROP = 224
IMG_MEAN = [0.485, 0.456, 0.406]
IMG_STD = [0.229, 0.224, 0.225]

# Hub model identifiers
HUB_MOCO = ('facebookresearch/moco-v3:main', 'resnet50')
HUB_DINO = ('facebookresearch/dino:main', 'dino_resnet50')
HUB_BARLOWTWINS = ('facebookresearch/barlowtwins:main', 'resnet50')

# Logging
LOG_FORMAT = '%(asctime)s %(levelname)s %(message)s'
LOG_LEVEL = 'INFO'
```

---

## Output Artifact Schemas

### h-e1_ratios.csv columns

| Column | Type | Example |
|--------|------|---------|
| paradigm | str | 'erm' |
| seed | int | 0 |
| spurious_acc | float | 0.923 |
| task_acc | float | 0.871 |
| ratio | float | 1.0597 |

### h-e1_stats.json fields

```json
{
  "anova": {"f_stat": 0.0, "p_value": 0.0},
  "pairwise": [
    {
      "pair": "erm_vs_moco",
      "t": 0.0,
      "p_raw": 0.0,
      "p_bonf": 0.0,
      "cohens_d": 0.0,
      "mean_diff": 0.0
    }
  ],
  "summary": {
    "erm":         {"mean": 0.0, "std": 0.0},
    "moco":        {"mean": 0.0, "std": 0.0},
    "dino":        {"mean": 0.0, "std": 0.0},
    "barlowtwins": {"mean": 0.0, "std": 0.0}
  },
  "gate": {
    "satisfied": false,
    "passing_pairs": []
  }
}
```
