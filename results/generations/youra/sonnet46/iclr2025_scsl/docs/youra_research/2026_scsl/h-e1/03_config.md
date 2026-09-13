---
hypothesis_id: H-E1
hypothesis_type: EXISTENCE
phase: Phase 3
generated_at: '2026-03-16'
---

# Configuration: H-E1
## Normalized Gradient Norm as Minority Group Proxy (Existence PoC)

**Applied: Standard argparse/PyTorch patterns used (Archon KB returned diffusion model content only, similarity 0.45-0.58 — no domain match)**

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: Green-field project — no existing codebase to analyze
**Config Files Found**: None — new config design
**Pattern Used**: Hardcoded dict (EXISTENCE PoC, LIGHT infrastructure tier)

---

## Configuration Format

EXISTENCE PoC with LIGHT infrastructure tier. All constants are hardcoded directly in `run_experiment.py` and `src/visualize.py`. No dataclass, no YAML.

---

## A-5: Visualization [Complexity: 9, Budget: 2 subtasks]

### Configuration (Hardcoded dict in `src/visualize.py`)

```python
# ---- Training Hyperparameters (inline constants in run_experiment.py) ----

LR                = 0.001
MOMENTUM          = 0.9
WEIGHT_DECAY      = 1e-4
BATCH_SIZE        = 128
TOTAL_EPOCHS      = 10
SEED              = 1
COLLECTION_EPOCHS = [1, 3, 5, 10]
PRIMARY_EPOCH     = 5          # T_id (FR-5)

# ---- Gate Thresholds (inline constants in run_experiment.py / evaluate.py) ----

GATE_RATIO     = 3.0        # minority/majority mean g_tilde ratio >= 3x
GATE_AUC       = 0.70       # AUC(g_tilde -> minority) > 0.70
GATE_BALANCE   = 0.10       # max within-class deviation <= 10%
TOP_K_FRACTION = 0.25       # top 25% high-norm subset
EPSILON        = 1e-8       # numerical stability in g_tilde = g_raw / (h_norm + eps)

FC_INPUT_DIM   = 2048       # ResNet-50 FC input dimension

# ---- Visualization Config (src/visualize.py) ----

VIZ_CONFIG = {
    "dpi": 300,
    "format": "png",
    # Group colors: G0=landbird/land, G1=landbird/water, G2=waterbird/land, G3=waterbird/water
    # Colorblind-safe palette
    "group_colors": {
        0: "#4477AA",
        1: "#EE6677",
        2: "#228833",
        3: "#CCBB44",
    },
    # Gate threshold line style
    "threshold_linestyle": "--",
    "threshold_color": "red",
    "threshold_alpha": 0.7,
    # Figure sizes
    "figsize_gate_metrics":  (12, 4),   # 3-panel gate chart
    "figsize_trajectory":    (8, 5),    # per-group g_tilde trajectory
    "figsize_distribution":  (8, 5),    # KDE minority vs majority at epoch 5
    "figsize_heatmap":       (8, 6),    # 4x2 balance heatmap
    "figsize_feature_norms": (8, 5),    # h_norm box plots per group
}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| S-A-5-1 | Figure Layout Config | figsize, DPI, colorblind-safe color scheme for G0-G3 groups |
| S-A-5-2 | Threshold Annotations | Dashed-red gate threshold lines and axis labels for gate metrics figure |

---

## Output Path Configuration

All paths are relative to `--output-dir` (default: `outputs/h-e1/`).

```python
# In run_experiment.py — derived from args.output_dir

def get_paths(output_dir: str) -> dict:
    return {
        "checkpoints":    f"{output_dir}/checkpoints/epoch_{{N}}.pt",
        "gradnorm":       f"{output_dir}/gradnorm_epoch_{{N}}.npz",
        "results":        f"{output_dir}/results.json",
        "train_log":      f"{output_dir}/train_log.csv",
        "fig_gate":       f"{output_dir}/figures/gate_metrics.png",
        "fig_trajectory": f"{output_dir}/figures/trajectory.png",
        "fig_dist":       f"{output_dir}/figures/distribution_epoch5.png",
        "fig_heatmap":    f"{output_dir}/figures/balance_heatmap.png",
        "fig_fnorms":     f"{output_dir}/figures/feature_norms.png",
    }
```

---

## argparse Configuration (`run_experiment.py`)

```python
import argparse
import torch

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="H-E1: Gradient norm minority proxy existence PoC"
    )
    parser.add_argument(
        "--data-root", type=str,
        default=".data_cache/datasets/waterbirds/",
        help="Root path to Waterbirds dataset (must contain metadata.csv)",
    )
    parser.add_argument(
        "--output-dir", type=str,
        default="outputs/h-e1/",
        help="Directory for checkpoints, gradnorm arrays, figures, results.json",
    )
    parser.add_argument(
        "--seed", type=int, default=1,
        help="Random seed (fixed for EXISTENCE PoC reproducibility)",
    )
    parser.add_argument(
        "--smoke-test", action="store_true",
        help="Run only 10 batches per epoch to verify hook fires correctly",
    )
    parser.add_argument(
        "--device", type=str,
        default="cuda" if torch.cuda.is_available() else "cpu",
        help="Compute device (cuda or cpu)",
    )
    parser.add_argument(
        "--num-workers", type=int, default=4,
        help="DataLoader num_workers",
    )
    return parser.parse_args()
```

---

## Hyperparameter Table

| Parameter | Value | Source |
|-----------|-------|--------|
| lr | 0.001 | Phase 2B CV |
| momentum | 0.9 | Phase 2B CV |
| weight_decay | 1e-4 | Phase 2B CV |
| batch_size | 128 | Phase 2B CV |
| epochs | 10 | Phase 2B protocol |
| seed | 1 | EXISTENCE PoC |
| collection_epochs | [1, 3, 5, 10] | FR-4.1 |
| primary_epoch (T_id) | 5 | FR-5 |
| GATE_RATIO | 3.0 | FR-5.1 |
| GATE_AUC | 0.70 | FR-5.2 |
| GATE_BALANCE | 0.10 | FR-5.3 |
| TOP_K_FRACTION | 0.25 | FR-5.3 |
| EPSILON | 1e-8 | FR-4.2 |
| FC_INPUT_DIM | 2048 | FR-2.2 |
| dpi | 300 | FR-6.3 |
| num_workers | 4 | FR-1.4 |

---

*Configuration for H-E1 | EXISTENCE PoC | Green-field | LIGHT infrastructure | Hardcoded dict*
