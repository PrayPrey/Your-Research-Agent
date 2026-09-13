# Config: H-M1 (Weight Matrices Encode Behavioral Information)

Applied: config-constants-module pattern (flat module-level constants, no dataclass — matches h-e1 style)

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (h-e1)
**Status**: config classes verified from base code (`h-e1/code/config.py`) via direct read (Serena project not registered for this path; manual file read performed as equivalent)
**Config Files Found**: `h-e1/code/config.py` (flat constants, no dataclass)
**Pattern Used**: flat module-level constants (dict-like), consistent with h-e1

## Inherited Configuration (Base Hypothesis)

```python
# From: h-e1/code/config.py (ACTUAL CODE)
SEED = 42
N_CLASSES = 10
# RESIDUAL_RATIO_THRESHOLD = 0.05  -- h-e1 only, not used in h-m1
```

`CIFAR_ROOT` in base code is an absolute path from a different experiment run — h-m1 repoints to relative `base/data` since base files are copied into `h-m1/code/base/` (per architecture, not cross-repo imported).

## A-1: config.py [Complexity: Low, Budget: n/a]

**Applied**: Standard PyTorch/sklearn defaults; h-e1 constant reuse

### Configuration (flat constants)
```python
import os

SEED = 42
N_CLASSES = 10
TEST_SPLIT = 0.2
RIDGE_ALPHA = 1.0

# Data paths (base files copied into code/base/)
DATA_PATH = os.path.join(os.path.dirname(__file__), "base", "data", "dataset_cifar_small_hyp_rand.pt")
CIFAR_ROOT = os.path.join(os.path.dirname(__file__), "base", "data")

# Output paths
FIGURES_DIR = os.path.join(os.path.dirname(__file__), "..", "figures")
OUTPUTS_DIR = os.path.join(os.path.dirname(__file__), "outputs")
RESULTS_PATH = os.path.join(OUTPUTS_DIR, "results.json")

os.makedirs(FIGURES_DIR, exist_ok=True)
os.makedirs(OUTPUTS_DIR, exist_ok=True)

# Layer keys for weight extraction — verified from actual state_dict (h-e1 model zoo),
# NOT the 4-layer count assumed in PRD FR-4. 5 layers x 5 stats = 25 features.
LAYER_KEYS = [
    "module_list.0.weight",
    "module_list.3.weight",
    "module_list.6.weight",
    "module_list.9.weight",
    "module_list.11.weight",
]
```

No subtasks (Low complexity, single config file, no variations — MECHANISM hypothesis uses one fixed config).
