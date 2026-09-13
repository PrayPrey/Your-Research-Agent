---
hypothesis_id: h-m2
generated_at: "2026-08-21T15:00:00+00:00"
---

# Config: H-M2 — Sample Efficiency Learning Curve Experiment

Applied: flat-constants module style (matching H-E1/H-M1 actual code)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Config classes verified from base code (H-E1, H-M1)
**Config Files Found**:
- `/home/PrayPrey/YOURA_no_VSA_no_IC/sonnet46/TEST_wsl/docs/youra_research/h-e1/code/config.py`
- `/home/PrayPrey/YOURA_no_VSA_no_IC/sonnet46/TEST_wsl/docs/youra_research/h-m1/code/config.py`
**Pattern Used**: flat module-level constants (NOT dataclass)

---

## Inherited Configuration (Base Hypothesis)

Verified field names and defaults from actual H-E1 and H-M1 code:

| Constant | H-E1 Actual Value | Notes |
|----------|-------------------|-------|
| `ZOO_PATHS` key | `"cifar10"` | NOT `"cifar-10"` |
| `ENCODER_NAMES` | `["flat_mlp", "flat_mlp_perm_aug", "gnn_nfn"]` | Exact list |
| `TRAINING_SIZES` | `[100, 250, 500, 1000, "full"]` | Mixed int/str list |
| `SEED` | `42` | H-E1 uses single seed |
| `LR` | `1e-3` | |
| `WEIGHT_DECAY` | `1e-4` | |
| `EPOCHS` | `100` | |
| `BATCH_SIZE` | `64` | |
| `N_BOOTSTRAP` | `1000` | field name in H-E1 |
| `CI_LEVEL` | `0.95` | |
| `GNN_HIDDEN_DIM` | `64` | from H-M1 actual code (NOT 128) |
| `GNN_NUM_LAYERS` | `4` | from H-M1 actual code |

---

## A-5: get_results Orchestration Config [Complexity: 2, Budget: 1]

Applied: flat-constants style matching H-E1/H-M1

### C-5-1: Full config.py implementation

```python
"""Experiment configuration for H-M2: Sample Efficiency Learning Curve."""
import os

# --- Paths ---
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_H_M2_DIR = os.path.dirname(_THIS_DIR)
_REPO_ROOT = os.path.dirname(os.path.dirname(_H_M2_DIR))

H_E1_CODE_DIR = os.path.join(_REPO_ROOT, "h-e1", "code")
H_M1_CODE_DIR = os.path.join(_REPO_ROOT, "h-m1", "code")
H_E1_RESULTS_DIR = os.path.join(_REPO_ROOT, "h-e1", "results")

# Primary input: H-E1 learning curve results (load if exists, else re-run)
H_E1_RESULTS_JSON = os.path.join(H_E1_RESULTS_DIR, "learning_curve_results.json")

MZDATASET_CODE_PATH = "/home/PrayPrey/YOURA_camera_ready/YouRA/results/generations/youra/opus45_no_IC/iclr2025_wsl/docs/youra_research/h-m4/data/ModelZooDataset/code"

ZOO_PATHS = {
    "cifar10": "/home/PrayPrey/.cache/model_zoos/cifar10/dataset_cifar_small_hyp_fix.pt",
    "mnist":   "/home/PrayPrey/.cache/model_zoos/mnist/dataset_mnist_hyp_fix.pt",
}

FIGURES_DIR = os.path.join(_H_M2_DIR, "figures")
RESULTS_DIR = os.path.join(_H_M2_DIR, "results")

# --- Training hyperparameters (inherited from H-E1) ---
SEED = 42
EPOCHS = 100
BATCH_SIZE = 64
BATCH_SIZE_SMALL = 16       # used when training_size <= 250
SMALL_SIZE_THRESHOLD = 250  # training sizes <= this use BATCH_SIZE_SMALL
LR = 1e-3
WEIGHT_DECAY = 1e-4

# --- Experiment grid ---
TRAINING_SIZES = [100, 250, 500, 1000, "full"]
SEEDS = [0, 1, 2, 3, 4]
ZOO_NAMES = ["cifar10"]  # "mnist" added when zoo file available locally
ENCODER_NAMES = ["flat_mlp", "flat_mlp_perm_aug", "gnn_nfn"]

# Zoo architecture (CNN for ModelZooDataset)
ZOO_ARCH = "cnn"

# --- GNN config (verified from H-M1 actual code) ---
GNN_HIDDEN_DIM = 64    # H-M1 actual value (NOT 128)
GNN_NUM_LAYERS = 4     # H-M1 actual value

# --- Analysis constants ---
PEAK_FRACTION = 0.90   # 90% of per-encoder peak R² threshold
EFFICIENCY_GATE = 2.0  # minimum ratio N_plain / N_equiv to support hypothesis
N_BOOT = 1000          # bootstrap resamples for CI

CI_LEVEL = 0.95

# --- Parameter budget tiers ---
BUDGET_TIERS = {"small": 50_000, "medium": 200_000, "large": 1_000_000}
PRIMARY_TIER = "medium"
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-5-1 | config.py implementation | Full flat-constants config matching H-E1/H-M1 style |

---

## Results JSON Schema (learning_curve_results.json)

```yaml
# learning_curve_results.json — output written by get_results.py
# Schema: {encoder_name: {zoo_name: {training_size: r2_score}}}
# training_size keys are strings: "100", "250", "500", "1000", "full"

type: object
patternProperties:
  "^(flat_mlp|flat_mlp_perm_aug|gnn_nfn|dwsnets_.*)$":
    type: object
    patternProperties:
      "^(cifar10|mnist)$":
        type: object
        patternProperties:
          "^(100|250|500|1000|full)$":
            type: number   # R² score, float
required: []

# Example structure:
# {
#   "flat_mlp": {"cifar10": {"100": 0.42, "250": 0.61, "500": 0.73, "1000": 0.81, "full": 0.88}},
#   "gnn_nfn":  {"cifar10": {"100": 0.71, "250": 0.83, "500": 0.89, "1000": 0.91, "full": 0.93}}
# }
```
