# Config: H-E2

**Date:** 2026-08-26
**Hypothesis:** H-E2 — CelebA replication of H-E1 paradigm effect

Applied: plain-module-constants pattern (matching H-E1 actual code)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-E1)
**Status**: config classes verified from base code (direct file read)
**Config Files Found**: `docs/youra_research/h-e1/code/config.py`
**Pattern Used**: plain module-level constants (no dataclass)

---

## Inherited Configuration (Base Hypothesis)

Fields read verbatim from `docs/youra_research/h-e1/code/config.py` (actual code):

```python
# Inherited verbatim (same field names, same defaults)
SEEDS = [0, 1, 2, 3, 4]
PARADIGMS = ['erm', 'moco', 'dino', 'barlowtwins']
BATCH_SIZE = 256

PROBE_C = 1.0
PROBE_MAX_ITER = 1000
PROBE_SOLVER = 'lbfgs'
FEATURE_DIM = 2048

BONFERRONI_N = 6
GATE_ALPHA = 0.05
GATE_MIN_DIFF = 0.02

RESIZE = 256
CROP = 224
IMG_MEAN = [0.485, 0.456, 0.406]
IMG_STD = [0.229, 0.224, 0.225]

HUB_MOCO = ('facebookresearch/moco-v3:main', 'resnet50')
HUB_DINO = ('facebookresearch/dino:main', 'dino_resnet50')
HUB_BARLOWTWINS = ('facebookresearch/barlowtwins:main', 'resnet50')

LOG_FORMAT = '%(asctime)s %(levelname)s %(message)s'
LOG_LEVEL = 'INFO'
```

**Changed from H-E1**: `DATA_ROOT`, `CACHE_DIR`, `RESULTS_DIR`, `FIGURES_DIR`, `LOG_DIR`, `LOG_PATH`, `DATASET_NAME`

**New fields**: `BLOND_ATTR`, `MALE_ATTR`, `N_PER_GROUP`

---

## A-1: Config [Complexity: 4, Budget: 0 subtasks]

Applied: plain-module-constants pattern (matching H-E1 actual code)

### Configuration (`config.py`)

```python
import os

# Experiment
SEEDS = [0, 1, 2, 3, 4]
PARADIGMS = ['erm', 'moco', 'dino', 'barlowtwins']
BATCH_SIZE = 256
N_PER_GROUP = 180  # minimum group size in CelebA test split

# CelebA attribute indices (verified: Liu et al. 2015 attribute ordering)
BLOND_ATTR = 9   # Blond_Hair
MALE_ATTR = 20   # Male

# Paths — resolve relative to this file so script runs from any cwd
_CODE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_ROOT = os.path.join(_CODE_DIR, '..', 'data')  # torchvision downloads here
RESULTS_DIR = os.path.join(_CODE_DIR, '..', 'results')
FIGURES_DIR = os.path.join(_CODE_DIR, '..', 'figures')
LOG_DIR = os.path.join(_CODE_DIR, '..', 'logs')
LOG_PATH = os.path.join(LOG_DIR, 'h-e2_run.log')

# Separate cache from H-E1 to avoid key collisions
CACHE_DIR = '/tmp/h-e2-cache'

# Probe (LogisticRegression) — identical to H-E1
PROBE_C = 1.0
PROBE_MAX_ITER = 1000
PROBE_SOLVER = 'lbfgs'
FEATURE_DIM = 2048

# Statistics — identical to H-E1
BONFERRONI_N = 6
GATE_ALPHA = 0.05
GATE_MIN_DIFF = 0.02

# Dataset
DATASET_NAME = 'celeba'
DATASET_DOWNLOAD = True  # Non-standard: True (H-E1 was False); CelebA not pre-downloaded

# Transform — identical to H-E1
RESIZE = 256
CROP = 224
IMG_MEAN = [0.485, 0.456, 0.406]
IMG_STD = [0.229, 0.224, 0.225]

# Hub model identifiers — identical to H-E1
HUB_MOCO = ('facebookresearch/moco-v3:main', 'resnet50')
HUB_DINO = ('facebookresearch/dino:main', 'dino_resnet50')
HUB_BARLOWTWINS = ('facebookresearch/barlowtwins:main', 'resnet50')

# Logging
LOG_FORMAT = '%(asctime)s %(levelname)s %(message)s'
LOG_LEVEL = 'INFO'
```

**Non-standard values:**
- `N_PER_GROUP = 180`: constrained by smallest CelebA test group (Blond+Male ~180); yields 720 balanced total
- `DATASET_DOWNLOAD = True`: CelebA not pre-downloaded unlike Waterbirds; torchvision auto-download via Google Drive mirror
- `DATA_ROOT`: points to `../data` relative to code dir; torchvision places CelebA at `DATA_ROOT/celeba/`
- `CACHE_DIR = '/tmp/h-e2-cache'`: separate from `/tmp/h-e1-cache` to avoid stale feature collisions across datasets
