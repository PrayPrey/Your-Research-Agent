---
hypothesis_id: h-m3
phase: config
generated_at: "2026-08-21"
---

# Config: H-M3 — Permutation Augmentation (PermAug) for Flat-MLP

Applied: flat-module constants pattern (verified from h-m2/code/config.py and h-e1/code/config.py)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis + existing_codebase
**Status**: Config files read directly via file tools (actual code verified)
**Config Files Found**: `h-m2/code/config.py`, `h-e1/code/config.py`
**Pattern Used**: module-level constants (flat, no dataclass — matches base hypothesis style)

---

## Inherited Configuration

### Verified Field Names from Actual Code

| Field | H-E1 | H-M2 | Value |
|-------|-------|-------|-------|
| `SEED` | yes | yes | 42 |
| `EPOCHS` | yes | yes | 100 |
| `BATCH_SIZE` | yes | yes | 64 |
| `BATCH_SIZE_SMALL` | no | yes | 16 |
| `SMALL_SIZE_THRESHOLD` | no | yes | 250 |
| `LR` | yes | yes | 1e-3 |
| `WEIGHT_DECAY` | yes | yes | 1e-4 |
| `N_BOOT` | no | yes | 1000 (H-E1 uses `N_BOOTSTRAP`) |
| `CI_LEVEL` | yes | yes | 0.95 |
| `ZOO_NAMES` | yes | yes | ["cifar10"] |
| `ZOO_ARCH` | yes | yes | "cnn" |
| `GNN_HIDDEN_DIM` | no | yes | 64 |
| `GNN_NUM_LAYERS` | no | yes | 4 |
| `PRIMARY_BUDGET` | no | yes | 200_000 |
| `MZDATASET_CODE_PATH` | yes | yes | (absolute path — copied verbatim) |
| `ZOO_PATHS` | yes | yes | {"cifar10": ...} (absolute path — copied verbatim) |

**Note**: H-E1 uses `N_BOOTSTRAP = 1000`; H-M2 renamed to `N_BOOT = 1000`. H-M3 follows H-M2 (`N_BOOT`).

---

## A-1: Config Setup [Complexity: 5, Budget: 1 subtask]

Applied: flat-module constants pattern

### Configuration (`code/config.py`)

```python
"""Experiment configuration for H-M3: PermAug for Flat-MLP."""
import os

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_H_M3_DIR = os.path.dirname(_THIS_DIR)
_YOURA_DIR = os.path.dirname(_H_M3_DIR)  # docs/youra_research/

# --- Paths to base hypothesis code ---
H_E1_CODE_DIR = os.path.join(_YOURA_DIR, "h-e1", "code")
H_M2_CODE_DIR = os.path.join(_YOURA_DIR, "h-m2", "code")
H_M1_CODE_DIR = os.path.join(_YOURA_DIR, "h-m1", "code")  # needed by H-E1 import chain

# --- Paths to base hypothesis results ---
H_E1_RESULTS_JSON = os.path.join(_YOURA_DIR, "h-e1", "results", "results.json")
H_M2_RESULTS_JSON = os.path.join(_YOURA_DIR, "h-m2", "results", "results.json")

# --- External data paths (verified from h-m2/code/config.py) ---
MZDATASET_CODE_PATH = "/home/PrayPrey/YOURA_camera_ready/YouRA/results/generations/youra/opus45_no_IC/iclr2025_wsl/docs/youra_research/h-m4/data/ModelZooDataset/code"

ZOO_PATHS = {
    "cifar10": "/home/PrayPrey/.cache/model_zoos/cifar10/dataset_cifar_small_hyp_fix.pt",
}

# --- Output dirs ---
FIGURES_DIR = os.path.join(_H_M3_DIR, "figures")
RESULTS_DIR = os.path.join(_H_M3_DIR, "results")

# --- Hyperparameters (inherited from H-M2, verified from actual code) ---
SEED = 42
EPOCHS = 100
BATCH_SIZE = 64
BATCH_SIZE_SMALL = 16
SMALL_SIZE_THRESHOLD = 250
LR = 1e-3
WEIGHT_DECAY = 1e-4
N_BOOT = 1000
CI_LEVEL = 0.95

# --- Experiment scope ---
TRAINING_SIZES = [100, 250, 500, 1000]  # no "full" — H-M3 trains PermAug only
ZOO_NAMES = ["cifar10"]
ZOO_ARCH = "cnn"
NUM_PERMUTATIONS = 10

# --- GNN reference (for loading H-M2 baseline) ---
GNN_HIDDEN_DIM = 64
GNN_NUM_LAYERS = 4

# --- Budget (for gate check reporting) ---
PRIMARY_BUDGET = 200_000

# --- Gate config (used by analysis.check_ordering_gate) ---
GATE_SIZES = [100, 250]
P2_FRACTION_LO = 0.50
P2_FRACTION_HI = 0.80
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-1-1 | config.py | Write the full module above |

---

## A-6: Analysis Config [C-1 subtask — GateConfig and BootstrapConfig]

Applied: flat-module constants pattern (no dataclass — consistent with base hypothesis style)

### C-1: GateConfig and BootstrapConfig structures

These are **not separate dataclass instances** — the analysis functions read directly from `config` module constants. The structures below document the expected call signatures and field mapping.

```python
# analysis.py uses these config fields directly:
#
# bootstrap_ci:
#   n_boot  -> cfg.N_BOOT   (int, default 1000)
#   ci_level -> cfg.CI_LEVEL (float, default 0.95)
#
# check_ordering_gate:
#   gate_sizes       -> cfg.GATE_SIZES       ([100, 250])
#   p2_fraction_lo   -> cfg.P2_FRACTION_LO   (0.50)
#   p2_fraction_hi   -> cfg.P2_FRACTION_HI   (0.80)
#
# If analysis.py needs standalone config objects (e.g., for testing), use:

BOOTSTRAP_CONFIG = {
    "n_boot": N_BOOT,       # 1000
    "ci_level": CI_LEVEL,   # 0.95
}

GATE_CONFIG = {
    "gate_sizes": GATE_SIZES,           # [100, 250]
    "p2_fraction_lo": P2_FRACTION_LO,   # 0.50 — perm_aug must close ≥50% of gap
    "p2_fraction_hi": P2_FRACTION_HI,   # 0.80 — perm_aug closes ≥80% → strong signal
}
```

**Rationale for non-standard values:**
- `P2_FRACTION_LO = 0.50`: minimum threshold for gate pass (PermAug explains ≥50% of equivariance gap)
- `P2_FRACTION_HI = 0.80`: strong-signal threshold (not a standard default — specific to H-M3 gate definition)
- `GATE_SIZES = [100, 250]`: low-data regime where ordering should be most visible

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-1 | Gate/Bootstrap config | Dict structures for GateConfig and BootstrapConfig |
