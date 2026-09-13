# Configuration: H-M2

**Applied**: temperature-scaling-nll-lbfgs (gpleiss/temperature_scaling canonical pattern, per-cluster via scipy L-BFGS-B)
**Applied (KB search)**: No project-specific match found in Archon KB ("DL config patterns hyperparameters" returned unrelated SD/PyTorch/latent-diffusion configs) — using standard scipy L-BFGS-B temperature-scaling defaults from PRD/architecture instead.

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (h-e1) + upstream pattern (h-m1)
**Status**: Config classes verified from actual code (h-e1/code/config.py, h-m1/code/config.py)
**Config Files Found**: `docs/youra_research/h-e1/code/config.py`, `docs/youra_research/h-m1/code/config.py`
**Pattern Used**: Flat module-level constants (NOT dataclass) — h-e1 and h-m1 both use plain uppercase module vars + `sys.path.insert` re-export pattern. H-M2 follows the same pattern for consistency.

---

## Inherited Configuration (Base Hypothesis: h-e1)

Re-exported via `sys.path.insert` pattern (same as h-m1/code/config.py):

```python
# From: docs/youra_research/h-e1/code/config.py (ACTUAL CODE, verified)
SEED = 42
MODEL_ID = "meta-llama/Llama-2-7b-hf"
CLUSTER_NAMES = {1: "Health/...", 2: "Law/...", ..., 7: "Misconceptions/..."}  # 7 clusters
CATEGORY_TO_CLUSTER = {...}  # 38 category -> cluster_id mapping
```

Note: `DTYPE`, `DEVICE_MAP`, `DATASET_ID`, `DATASET_CONFIG`, `DATASET_SPLIT`, `BATCH_SIZE` also available from h-e1 but only imported if `data_loader.py` needs to call `load_model_and_tokenizer`/`score_choices` directly (it does, per architecture — full re-export list below).

---

## Configuration (Module-level constants — matches h-e1/h-m1 pattern)

**Applied**: Flat-constants config (not dataclass) — consistent with existing codebase pattern (h-e1, h-m1).

```python
"""H-M2 Configuration: Per-cluster temperature scaling variation."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "h-e1" / "code"))
from config import (
    SEED, MODEL_ID, DTYPE, DEVICE_MAP, DATASET_ID, DATASET_CONFIG,
    DATASET_SPLIT, BATCH_SIZE, CATEGORY_TO_CLUSTER, CLUSTER_NAMES,
)

# Cluster / CV setup
N_CLUSTERS = 7
N_FOLDS = 5
MIN_SAMPLES_PER_FOLD = 80  # PRD FR-2: min 80 samples/cluster/fold

# Temperature optimization (L-BFGS-B)
T_BOUNDS = (0.1, 10.0)   # prevents degenerate T->0 or T->inf
T_INIT = 1.0             # standard neutral starting point

# Statistics
N_BOOTSTRAP = 1000       # PRD FR-4: bootstrap CI resamples
CI = 0.95
CV_GATE_THRESHOLD = 0.1      # PRD: primary gate CV(T) > 0.1
RANGE_GATE_THRESHOLD = 0.3   # PRD: secondary gate range(T) > 0.3
EPS = 1e-10               # numerical stability for log-probs (PRD risk mitigation)

# Output paths
RESULTS_JSON = "outputs/results.json"
VALIDATION_MD = "../04_validation.md"
FIGURES_DIR = "figures/"

# Ablation configs (FR-7)
ABLATION_BOUNDS = [(0.5, 5.0), (0.1, 10.0)]      # A1: bounds sensitivity
ABLATION_T_INIT = [0.5, 1.0, 2.0]                # A2: init sensitivity
```

**Non-standard values**: None — all defaults taken directly from PRD Section 5.2/6/9 (T bounds, gate thresholds, bootstrap count) and h-e1's established `MIN_SAMPLES_PER_FOLD`-equivalent convention.

---

## Experiment Variants (Ablations)

| ID | Variant | Bounds | T_init | Purpose |
|----|---------|--------|--------|---------|
| Base | Primary run | (0.1, 10.0) | 1.0 | Main gate evaluation |
| A1a | Tight bounds | (0.5, 5.0) | 1.0 | Bounds sensitivity |
| A1b | Wide bounds | (0.1, 10.0) | 1.0 | Bounds sensitivity (= base) |
| A2a | Low init | (0.1, 10.0) | 0.5 | Init sensitivity |
| A2b | Mid init | (0.1, 10.0) | 1.0 | Init sensitivity (= base) |
| A2c | High init | (0.1, 10.0) | 2.0 | Init sensitivity |

All variants reuse `optimize_temperature_per_cluster` with swapped `bounds`/`t_init` args (see `ablations.py` in architecture).

---

## A-1: Config setup [Complexity: 4, Budget: 4]

**Applied**: Standard flat-constants re-export pattern (h-m1 precedent).

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| C-1-1 | Re-export h-e1 constants | `sys.path.insert` + import SEED, MODEL_ID, CLUSTER_NAMES, CATEGORY_TO_CLUSTER, DTYPE, DEVICE_MAP, DATASET_* , BATCH_SIZE |
| C-1-2 | CV/optimizer constants | N_CLUSTERS, N_FOLDS, MIN_SAMPLES_PER_FOLD, T_BOUNDS, T_INIT, EPS |
| C-1-3 | Stats/gate constants | N_BOOTSTRAP, CI, CV_GATE_THRESHOLD, RANGE_GATE_THRESHOLD |
| C-1-4 | Paths + ablation lists | RESULTS_JSON, VALIDATION_MD, FIGURES_DIR, ABLATION_BOUNDS, ABLATION_T_INIT |
