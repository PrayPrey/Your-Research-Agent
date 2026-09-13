# Config: h-m2
# Differential Advantage of Permutation-Equivariant Encoders (gap vs. test_acc)

**Date:** 2026-08-31
**Author:** yoon303@etri.re.kr

Applied: Dataclass composition pattern (verified from h-e1/code/config.py)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Config classes verified from h-e1/code/config.py (actual implementation)
**Config Files Found**: `h-e1/code/config.py` — ZooConfig, AuditConfig, DataLoaderConfig, EncoderConfig, ExperimentConfig
**Pattern Used**: dataclass

---

## Inherited Configuration (Base Hypothesis)

```python
# From: h-e1/code/config.py (ACTUAL CODE — field names verified)
@dataclass
class EncoderConfig:
    lr_candidates: list        # e.g. [5e-4, 1e-3, 2e-3]
    batch_size: int            # 64 for FlatMLP in h-m2
    epochs: int                # 100
    lr_schedule: str           # "none" or "cosine"
    hidden_dim: int            # 256

@dataclass
class ExperimentConfig:
    zoo: ZooConfig             # zoo_path, osf_url, expected_n_models
    encoders: dict             # ENCODER_CONFIGS dict
    loader: DataLoaderConfig   # batch_size=64, shuffle=True, num_workers=0
    audit: AuditConfig         # spearman_threshold=0.95, seed=42, split_ratios=[0.8,0.1,0.1]
    n_trials: int = 3
    gate_threshold: float = 0.5
    figures_dir: str = "figures"
    seed: int = 42
    device: str = "cuda:0"
```

**Verified from**: `h-e1/code/config.py` (actual implementation)

---

## A-3: FlatMLP Training Config [Complexity: 1, Budget: 1]

**Applied**: Dataclass composition pattern

### C-3-1: H_M2Config

```python
from dataclasses import dataclass, field
from typing import Tuple

FLAT_MLP_TESTACC_ENCODER = {
    "FlatMLP_testacc": {
        "lr_candidates": [5e-4, 1e-3, 2e-3],
        "batch_size": 64,
        "epochs": 100,
        "lr_schedule": "none",
        "hidden_dim": 256,
    }
}

@dataclass
class H_M2Config:
    # Inherited fields (matching ExperimentConfig field names exactly)
    seed: int = 42
    n_trials: int = 3
    device: str = "cuda:0"
    figures_dir: str = "h-m2/figures/"
    checkpoint_dir: str = "h-m2/checkpoints/"

    # Training — FlatMLP on test_acc (h-m2 new target)
    lr_range: Tuple[float, float] = (5e-4, 2e-3)
    batch_size: int = 64
    epochs: int = 100

    # Gate config (h-m2 differential gate, distinct from h-e1 gate_threshold=0.5)
    gate_threshold: float = 0.02   # non-standard: Δ(gap - test_acc) threshold
    gate_min_pass: int = 2         # ≥2 encoders must exceed threshold

    # Bootstrap
    bootstrap_n: int = 1000

    # Checkpoint filenames
    checkpoint_files_gap: dict = field(default_factory=lambda: {
        "FlatMLP": "flat_mlp_best.pt",
        "DWSNet":  "dws_net_best.pt",
        "NFT":     "nft_best.pt",
        "GNN":     "gnn_best.pt",
    })
    checkpoint_files_testacc: dict = field(default_factory=lambda: {
        "FlatMLP": "flat_mlp_testacc_best.pt",
        "DWSNet":  "dws_net_testacc_best.pt",
        "NFT":     "nft_testacc_best.pt",
        "GNN":     "gnn_testacc_best.pt",
    })
```

### Subtasks [1/1 used]
| ID | Subtask | Description |
|----|---------|-------------|
| C-3-1 | H_M2Config dataclass | All experiment params; extends h-e1 field naming convention |

---

## A-8: Visualization Config [Complexity: 3, Budget: 3]

**Applied**: Hardcoded dict pattern (visualization-only, no inheritance needed)

### C-8-1: Figure Specs

```python
FIGURE_SPECS = {
    "fig1_gate_delta": {
        "filename": "fig1_gate_delta.png",
        "figsize": (7, 5),
        "dpi": 150,
    },
    "fig2_dual_target": {
        "filename": "fig2_dual_target.png",
        "figsize": (8, 5),
        "dpi": 150,
    },
    "fig3_delta_distribution": {
        "filename": "fig3_delta_distribution.png",
        "figsize": (7, 5),
        "dpi": 150,
    },
    "fig4_partial_corr": {
        "filename": "fig4_partial_corr.png",
        "figsize": (6, 5),
        "dpi": 150,
    },
    "fig5_bootstrap_ci": {
        "filename": "fig5_bootstrap_ci.png",
        "figsize": (7, 5),
        "dpi": 150,
    },
}

# Color palette per encoder (consistent across all figures)
ENCODER_COLORS = {
    "FlatMLP": "#4C72B0",
    "DWSNet":  "#DD8452",
    "NFT":     "#55A868",
    "GNN":     "#C44E52",
}
```

### C-8-2: Bar Chart Config (fig1 gate delta, fig2 dual-target)

```python
BAR_CONFIG = {
    "bar_width": 0.35,
    "alpha": 0.85,
    "edge_color": "white",
    "axis_labels": {
        "fig1": {"xlabel": "Encoder", "ylabel": "Δ Spearman (gap − test_acc)"},
        "fig2": {"xlabel": "Encoder", "ylabel": "Spearman ρ"},
    },
    "threshold_line": {
        "color": "#E74C3C",
        "linestyle": "--",
        "linewidth": 1.5,
        "label": f"gate_threshold=0.02",
    },
    "legend_loc": "upper right",
    "grid": {"axis": "y", "alpha": 0.3},
}
```

### C-8-3: Scatter / Error Bar Config (fig4 partial corr, fig5 bootstrap CI)

```python
SCATTER_CONFIG = {
    "marker": "o",
    "markersize": 7,
    "alpha": 0.75,
    "linewidth": 1.2,
}

ERRORBAR_CONFIG = {
    "capsize": 4,
    "capthick": 1.2,
    "elinewidth": 1.2,
    "alpha": 0.85,
    "fmt": "o",
    "markersize": 6,
}
```

### Subtasks [3/3 used]
| ID | Subtask | Description |
|----|---------|-------------|
| C-8-1 | Figure specs | 5 figures: filename, figsize, dpi, shared encoder color palette |
| C-8-2 | Bar chart config | fig1 (gate delta) + fig2 (dual-target): bar width, colors, threshold line |
| C-8-3 | Scatter/error bar config | fig4 (partial corr) + fig5 (bootstrap CI): marker, cap, alpha |
