# Configuration: H-M1

**hypothesis_id:** h-m1
**hypothesis_type:** MECHANISM
**generated_at:** 2026-03-16
**extends:** H-E1 (COMPLETED — PASS)

Applied: Standard PyTorch training defaults (Archon KB low-relevance for this domain)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: config classes verified from actual H-E1 code (`h-e1/code/src/config.py`)
**Config Files Found**: `/home/anonymous/YouRA_results_new_4/TEST_wsl/docs/youra_research/20260316_wsl/h-e1/code/src/config.py`
**Pattern Used**: dataclass (H-E1 pattern) + module-level constants (H-M1 extension)

---

## Inherited Configuration (Base Hypothesis)

### Config Classes (From Actual Code)

```python
# From: h-e1/code/src/config.py (ACTUAL CODE — verified field names)
@dataclass
class DataConfig:
    dataset_url: str = "https://storage.googleapis.com/gresearch/dnn_predict_accuracy/small_mnist_networks.pkl"
    local_path: str = "data/unterthiner_mnist_zoo.pkl"
    min_samples: int = 500
    train_ratio: float = 0.8
    batch_size: int = 64
    seed: int = 42
    severity_levels: List[float] = field(default_factory=lambda: [0.0, 0.25, 0.5, 1.0])

@dataclass
class NFTModelConfig:
    d_model: int = 128
    n_heads: int = 4
    n_layers: int = 2
    dropout: float = 0.0

@dataclass
class FlatMLPConfig:
    hidden_dim: int = 512
    n_hidden_layers: int = 3
    activation: str = "ReLU"

@dataclass
class TrainConfig:
    optimizer: str = "Adam"
    lr: float = 1e-3
    betas: tuple = (0.9, 0.999)
    weight_decay: float = 1e-4
    scheduler: str = "CosineAnnealingLR"
    T_max: int = 100
    eta_min: float = 1e-5
    batch_size: int = 64
    n_epochs: int = 100
    seed: int = 42
    nan_recovery_lr: float = 1e-4

@dataclass
class EvalConfig:
    n_bootstrap: int = 10000
    alpha: float = 0.05
    holm_correction: bool = True
    flat_mlp_delta_threshold: float = 0.10
    nft_delta_threshold: float = 0.02
    severity_levels: List[float] = field(default_factory=lambda: [0.0, 0.25, 0.5, 1.0])

@dataclass
class PathsConfig:
    figures_dir: str = "figures"
    checkpoints_dir: str = "checkpoints"
    results_dir: str = "results"

@dataclass
class ExperimentConfig:
    data: DataConfig = field(default_factory=DataConfig)
    nft_model: NFTModelConfig = field(default_factory=NFTModelConfig)
    flat_mlp: FlatMLPConfig = field(default_factory=FlatMLPConfig)
    train: TrainConfig = field(default_factory=TrainConfig)
    eval: EvalConfig = field(default_factory=EvalConfig)
    paths: PathsConfig = field(default_factory=PathsConfig)
    device: str = "cuda"
    seed: int = 42
```

**Verified from**: `h-e1/code/src/config.py` (actual implementation)

---

## A-1: Data & Config Setup [Complexity: 9, Budget: 2 subtasks]

Applied: Standard PyTorch defaults

### Configuration (Python — module-level constants + dataclass)

```python
# src/config.py  (H-M1)
from dataclasses import dataclass, field
from typing import List, Optional, Union

# ---------------------------------------------------------------------------
# Multi-seed / severity constants
# ---------------------------------------------------------------------------
SEEDS: List[int] = [42, 123, 456]
SEVERITY_LEVELS: List[float] = [0.0, 0.25, 0.5, 1.0]

# ---------------------------------------------------------------------------
# 6-Encoder registry
# ---------------------------------------------------------------------------
ENCODER_NAMES: List[str] = [
    "flat-MLP",
    "flat-MLP+aug",
    "flat-MLP+canon",
    "NFT-base",
    "NFT+aug",
    "Oracle-canon",
]

ENCODER_CONFIG: dict = {
    "flat-MLP":       {"aug_severity": None,  "canon": False,      "model_type": "flat"},
    "flat-MLP+aug":   {"aug_severity": 1.0,   "canon": False,      "model_type": "flat"},
    "flat-MLP+canon": {"aug_severity": None,  "canon": "l2_norm",  "model_type": "flat"},
    "NFT-base":       {"aug_severity": None,  "canon": False,      "model_type": "nft"},
    "NFT+aug":        {"aug_severity": 1.0,   "canon": False,      "model_type": "nft"},
    "Oracle-canon":   {"aug_severity": None,  "canon": "oracle",   "model_type": "flat"},
}

# aug_severity=1.0 applied at 50% probability during training batches
AUG_APPLY_PROB: float = 0.5

# ---------------------------------------------------------------------------
# Data config (extends H-E1 DataConfig — verified field names)
# ---------------------------------------------------------------------------
@dataclass
class DataConfig:
    dataset_url: str = "https://storage.googleapis.com/gresearch/dnn_predict_accuracy/small_mnist_networks.pkl"
    local_path: str = "data/unterthiner_mnist_zoo.pkl"
    min_samples: int = 500
    train_ratio: float = 0.8
    batch_size: int = 64
    seed: int = 42
    severity_levels: List[float] = field(default_factory=lambda: [0.0, 0.25, 0.5, 1.0])

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
DATA_PATH: str = "data/unterthiner_mnist_zoo.pkl"
RESULTS_DIR: str = "results/"
FIGURES_DIR: str = "figures/"
CHECKPOINT_DIR: str = "checkpoints/"
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-1-1 | ENCODER_CONFIG dict | Define 6-entry ENCODER_CONFIG with aug_severity, canon, model_type fields; ENCODER_NAMES list; AUG_APPLY_PROB constant |
| C-1-2 | DataConfig dataclass | Port H-E1 DataConfig verbatim; add path/directory constants for H-M1 output layout |

---

## A-5: Gate v2 & Mechanism Verification [Complexity: 10, Budget: 2 subtasks]

Applied: Standard threshold configuration from Phase 2B gate spec

### Configuration (Python dataclass)

```python
@dataclass
class GateConfig:
    # Primary gate thresholds (H-M1 MUST_WORK)
    nft_delta_rho_threshold: float = 0.02        # NFT-base Δρ must be < this
    mediation_delta_r2_threshold: float = 0.10   # ΔR² must be >= this

    # Secondary / informational thresholds
    aug_partial_delta_rho_min: float = 0.05      # flat-MLP+aug lower bound (partial fix)
    aug_partial_delta_rho_max: float = 0.10      # flat-MLP+aug upper bound (not full fix)
    flat_mlp_delta_rho_threshold: float = 0.10   # flat-MLP reference (H-E1 proven: 0.1595)

    # 5-indicator mechanism check keys (used in verify_mechanism_activated)
    # indicator names: nft_base_robust, mediation_confirmed, aug_partial,
    #                  architecture_sufficient, ranking_correct

    # Gate output path
    gate_result_path: str = "results/gate_result.json"
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-5-1 | GateConfig dataclass | All 5 threshold fields; secondary thresholds for partial-aug and flat-MLP reference; gate_result_path |
| C-5-2 | Mechanism indicator names | Document 5 boolean indicator keys used by verify_mechanism_activated for gate_result.json output |

---

## A-6: Visualization [Complexity: 12, Budget: 2 subtasks]

Applied: Standard matplotlib figure defaults

### Configuration (Python dataclass)

```python
@dataclass
class VizConfig:
    # Output
    figures_dir: str = "figures/"
    dpi: int = 150
    fig_format: str = "png"

    # Figure sizes (width, height) in inches
    bar_figsize: tuple = (10, 6)      # fig1: 6-encoder Δρ bar chart
    curve_figsize: tuple = (10, 6)    # fig2: Δρ vs severity multi-line
    mediation_figsize: tuple = (8, 5) # fig3: ΔR² breakdown bar
    heatmap_figsize: tuple = (10, 6)  # fig4: ρ heatmap 6×4
    bootstrap_figsize: tuple = (10, 5)# fig5: bootstrap dist comparison

    # Style
    style: str = "seaborn-v0_8-whitegrid"
    palette: str = "tab10"            # 6 distinct colors for 6 encoders

    # Gate threshold line styling
    gate_line_color: str = "red"
    gate_line_style: str = "--"
    gate_line_alpha: float = 0.8

    # Figure save paths (relative to figures_dir)
    fig1_name: str = "fig1_delta_rho_bar.png"
    fig2_name: str = "fig2_delta_rho_curves.png"
    fig3_name: str = "fig3_mediation_bar.png"
    fig4_name: str = "fig4_rho_heatmap.png"
    fig5_name: str = "fig5_bootstrap_dist.png"
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-6-1 | VizConfig dataclass | Figure sizes, dpi, format, style, palette for all 5 figure types |
| C-6-2 | Gate line + path constants | Gate threshold line color/style/alpha; per-figure save path names |

---

## A-7: Experiment Runner + Tests [Complexity: 13, Budget: 2 subtasks]

Applied: Standard PyTorch training defaults

### Configuration (Python dataclass)

```python
@dataclass
class ExperimentConfig:
    # Multi-seed orchestration
    seeds: List[int] = field(default_factory=lambda: [42, 123, 456])
    encoder_names: List[str] = field(default_factory=lambda: [
        "flat-MLP", "flat-MLP+aug", "flat-MLP+canon",
        "NFT-base", "NFT+aug", "Oracle-canon",
    ])

    # Training (inherited from H-E1 — verified field names)
    lr: float = 1e-3
    betas: tuple = (0.9, 0.999)
    weight_decay: float = 1e-4
    scheduler: str = "CosineAnnealingLR"
    T_max: int = 100
    eta_min: float = 1e-5
    batch_size: int = 64
    n_epochs: int = 100
    nan_recovery_lr: float = 1e-4

    # Evaluation (inherited from H-E1 — verified field names)
    n_bootstrap: int = 10000
    alpha: float = 0.05
    severity_levels: List[float] = field(default_factory=lambda: [0.0, 0.25, 0.5, 1.0])

    # Sanity check
    sanity_n_samples: int = 10       # models checked per encoder before full run

    # Run flags (CLI overrides)
    run_sanity_check: bool = True
    run_training: bool = True
    run_evaluation: bool = True
    run_visualization: bool = True

    # Paths
    data_path: str = "data/unterthiner_mnist_zoo.pkl"
    results_dir: str = "results/"
    figures_dir: str = "figures/"
    checkpoint_dir: str = "checkpoints/"
    results_file: str = "results/h-m1_results.json"

    # Device
    device: str = "cuda"
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-7-1 | ExperimentConfig dataclass | Multi-seed list, encoder_names list, inherited training/eval fields (verified from H-E1), sanity check settings, run flags, output paths |
| C-7-2 | CLI argument mapping | --encoder, --seed, --data-path, --device, --epochs flags map to ExperimentConfig fields; document override semantics |

---

## Complete H-M1 Config Summary (YAML Reference)

```yaml
# H-M1 experiment configuration reference
# Source of truth: src/config.py (Python dataclasses above)

seeds: [42, 123, 456]
severity_levels: [0.0, 0.25, 0.5, 1.0]
aug_apply_prob: 0.5

encoder_config:
  flat-MLP:       {aug_severity: null, canon: false,     model_type: flat}
  flat-MLP+aug:   {aug_severity: 1.0,  canon: false,     model_type: flat}
  flat-MLP+canon: {aug_severity: null, canon: l2_norm,   model_type: flat}
  NFT-base:       {aug_severity: null, canon: false,     model_type: nft}
  NFT+aug:        {aug_severity: 1.0,  canon: false,     model_type: nft}
  Oracle-canon:   {aug_severity: null, canon: oracle,    model_type: flat}

training:
  optimizer: Adam
  lr: 1.0e-3
  betas: [0.9, 0.999]
  weight_decay: 1.0e-4
  scheduler: CosineAnnealingLR
  T_max: 100
  eta_min: 1.0e-5
  batch_size: 64
  n_epochs: 100
  nan_recovery_lr: 1.0e-4

model:
  flat_mlp:
    hidden_dim: 512
    n_hidden_layers: 3
    activation: ReLU
  nft:
    d_model: 128
    n_heads: 4
    n_layers: 2
    dropout: 0.0

evaluation:
  n_bootstrap: 10000
  alpha: 0.05
  holm_correction: true

gate:
  nft_delta_rho_threshold: 0.02
  mediation_delta_r2_threshold: 0.10
  aug_partial_delta_rho_min: 0.05
  aug_partial_delta_rho_max: 0.10
  flat_mlp_delta_rho_threshold: 0.10

visualization:
  dpi: 150
  fig_format: png
  style: seaborn-v0_8-whitegrid
  palette: tab10

paths:
  data: data/unterthiner_mnist_zoo.pkl
  results: results/
  figures: figures/
  checkpoints: checkpoints/
  results_file: results/h-m1_results.json
  gate_result: results/gate_result.json
```

---

*Generated by Configuration Agent — Phase 3*
*H-E1 config.py verified from actual code: `h-e1/code/src/config.py`*
*All field names match H-E1 implementation (lr, n_epochs, n_bootstrap, etc.)*
