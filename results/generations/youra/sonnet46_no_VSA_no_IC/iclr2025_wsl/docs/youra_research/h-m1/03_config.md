---
hypothesis_id: h-m1
hypothesis_type: MECHANISM
config_author: yoon303@etri.re.kr
generated_at: "2026-08-21"
---

# Config: H-M1 — Permutation Equivariance Verification

Applied: flat module-level constants (matches H-E1 style; verification-only, no training loop)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Config verified from H-E1 actual code
**Config Files Found**: `docs/youra_research/h-e1/code/config.py`
**Pattern Used**: flat module-level constants (dict-style, no dataclass)

---

## Inherited Configuration (Base Hypothesis)

Field names and defaults verified from `/home/PrayPrey/YOURA_no_VSA_no_IC/sonnet46/TEST_wsl/docs/youra_research/h-e1/code/config.py` (actual code):

```python
# From: h-e1/code/config.py (ACTUAL CODE — verified)
ZOO_PATHS = {"cifar10": "/home/PrayPrey/.cache/model_zoos/cifar10/dataset_cifar_small_hyp_fix.pt"}
SEED = 42
ENCODER_NAMES = ["flat_mlp", "flat_mlp_perm_aug", "gnn_nfn"]
ZOO_ARCH = "cnn"
# GNN-NFN actual hidden_dim=64, num_layers=4 (from encoders.py — NOT 128 as PRD states)
```

**Critical**: `GNNNFNEncoder` was trained with `hidden_dim=64`. Loading `gnn_nfn_best.pt` requires matching this value exactly.

---

## Main Config (`code/config.py`)

```python
"""Config for H-M1: Permutation Equivariance Verification (inference-only)."""
import os

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_H_M1_DIR = os.path.dirname(_THIS_DIR)
_H_E1_DIR = os.path.join(os.path.dirname(_H_M1_DIR), "h-e1")

# ── Paths ──────────────────────────────────────────────────────────────────────
MZDATASET_CODE_PATH = "/home/PrayPrey/YOURA_camera_ready/YouRA/results/generations/youra/opus45_no_IC/iclr2025_wsl/docs/youra_research/h-m4/data/ModelZooDataset/code"

ZOO_PT_PATH = "/home/PrayPrey/.cache/model_zoos/cifar10/dataset_cifar_small_hyp_fix.pt"
H_E1_RESULTS_DIR = os.path.join(_H_E1_DIR, "results")
GNN_CKPT  = os.path.join(H_E1_RESULTS_DIR, "gnn_nfn_best.pt")
FLAT_CKPT = os.path.join(H_E1_RESULTS_DIR, "flat_mlp_best.pt")

FIGURES_DIR = os.path.join(_H_M1_DIR, "figures")
RESULTS_DIR = os.path.join(_H_M1_DIR, "results")

# ── Reproducibility ────────────────────────────────────────────────────────────
SEED = 42

# ── Data loader ────────────────────────────────────────────────────────────────
N_MODELS   = 200        # models drawn from zoo testset
ZOO_SPLIT  = "testset"  # key in .pt file: "trainset" | "valset" | "testset"

# ── Verification ───────────────────────────────────────────────────────────────
N_PERMS      = 50       # random permutations per model
TOL_EQUIV    = 1e-5     # max abs diff to call "equivariant"
TOL_NON_EQUIV = 1e-3    # min abs diff to call "non-equivariant" (FlatMLP baseline)

# ── GNN-NFN encoder (must match h-e1 checkpoint) ──────────────────────────────
GNN_HIDDEN_DIM  = 64    # verified from h-e1/code/encoders.py (PRD says 128 — wrong)
GNN_NUM_LAYERS  = 4

# ── FlatMLP encoder ────────────────────────────────────────────────────────────
FLAT_HIDDEN     = 512
FLAT_OUTPUT_DIM = 128

# ── Visualization ──────────────────────────────────────────────────────────────
FIG_SIZE_BAR  = (8, 5)   # (width, height) inches — gate_metrics_bar.png
FIG_SIZE_CDF  = (7, 5)   # cdf_comparison.png
FIG_SIZE_HIST = (10, 4)  # diff_histograms.png (1×3 subplots)
FIG_DPI       = 150
ENCODER_COLORS = {
    "gnn_nfn":  "#2196F3",   # blue
    "flat_mlp": "#F44336",   # red
    "dwsnets":  "#4CAF50",   # green (new encoder in H-M1)
}
```

---

## A-3: Data Loader [Complexity: 2, Budget: 2 subtasks]

Applied: flat module-level constants (H-E1 style)

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-3-1 | ZooLoaderConfig | Paths, N_MODELS, SEED, ZOO_SPLIT — maps directly to constants in config.py above |
| C-3-2 | VerificationConfig | N_PERMS, TOL_EQUIV, TOL_NON_EQUIV — thresholds consumed by verify.py |

**C-3-1 values** (copy-paste ready):
```python
ZOO_PT_PATH = "/home/PrayPrey/.cache/model_zoos/cifar10/dataset_cifar_small_hyp_fix.pt"
ZOO_SPLIT   = "testset"
N_MODELS    = 200
SEED        = 42
```

**C-3-2 values**:
```python
N_PERMS       = 50
TOL_EQUIV     = 1e-5
TOL_NON_EQUIV = 1e-3
```

---

## A-8: Visualization [Complexity: 1, Budget: 1 subtask]

Applied: flat module-level constants (H-E1 style)

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-8-1 | VisualizationConfig | Figure sizes, DPI, per-encoder colors, output paths |

**C-8-1 values** (copy-paste ready):
```python
FIG_SIZE_BAR  = (8, 5)
FIG_SIZE_CDF  = (7, 5)
FIG_SIZE_HIST = (10, 4)
FIG_DPI       = 150
ENCODER_COLORS = {
    "gnn_nfn":  "#2196F3",
    "flat_mlp": "#F44336",
    "dwsnets":  "#4CAF50",
}
FIGURES_DIR = os.path.join(_H_M1_DIR, "figures")   # set by _H_M1_DIR above
```

Output files (consumed by visualize.py):
- `{FIGURES_DIR}/gate_metrics_bar.png`
- `{FIGURES_DIR}/cdf_comparison.png`
- `{FIGURES_DIR}/diff_histograms.png`
