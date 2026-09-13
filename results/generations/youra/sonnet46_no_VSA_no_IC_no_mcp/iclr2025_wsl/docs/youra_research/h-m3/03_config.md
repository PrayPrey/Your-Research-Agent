# Configuration Design: H-M3
# SymCanon-WSL — NFT with Weight Symmetry Canonicalization

**Hypothesis:** H-M3
**Generated:** 2026-08-27
**Source:** 03_architecture.md, 03_prd.md, 03_logic.md

Applied: dataclass-config pattern (single ExperimentConfig dataclass, CLI overrides via argparse)
Applied: seed-sweep pattern (list of seeds, outer loop in main.py)

---

## ExperimentConfig Dataclass

```python
from dataclasses import dataclass, field
from typing import Literal

@dataclass
class ExperimentConfig:
    # ── Experiment Identity ────────────────────────────────────────────
    hypothesis_id: str = "h-m3"
    conditions: list[str] = field(default_factory=lambda: ['A', 'B', 'C', 'D', 'E', 'F'])
    seeds: list[int] = field(default_factory=lambda: [42, 123, 456])

    # ── Data ───────────────────────────────────────────────────────────
    weight_dim: int = 51850          # EXPECTED_DIM from h-m1/code/data_loader.py
    n_labels: int = 3                # test_accuracy, generalization_gap, learning_rate
    label_names: list[str] = field(default_factory=lambda: [
        "test_accuracy", "generalization_gap", "learning_rate"
    ])
    # Zoo splits (standard; do not change without re-validating baseline)
    val_fraction: float = 0.1        # ~5k val from total ~50k
    test_fraction: float = 0.1       # ~5k test (held out)

    # ── NFT Architecture ───────────────────────────────────────────────
    embed_dim: int = 256             # NFT embedding dimension
    n_layers: int = 4                # Transformer encoder layers
    nhead: int = 8                   # Attention heads
    dim_feedforward: int = 512       # FF dim in transformer
    dropout: float = 0.1             # Dropout rate

    # ── Training ───────────────────────────────────────────────────────
    lr: float = 1e-3                 # Adam learning rate (H-M1 validated)
    weight_decay: float = 1e-4       # Adam weight decay (H-M1 validated)
    adam_betas: tuple = (0.9, 0.999) # Adam betas
    batch_size: int = 64             # Models per batch (H-M1 validated)
    max_epochs: int = 100            # Max training epochs
    es_patience: int = 10            # Early stopping patience (on val ρ)
    lr_patience: int = 5             # ReduceLROnPlateau patience
    lr_factor: float = 0.5           # LR reduction factor
    min_lr: float = 1e-5             # Minimum LR

    # ── Evaluation ─────────────────────────────────────────────────────
    n_boot: int = 1000               # Bootstrap resamples for CI
    boot_seed: int = 42              # Bootstrap RNG seed
    delta_threshold: float = 0.05    # P1 gate: Δρ ≥ 0.05
    p2_fraction: float = 2/3         # P2 gate: ρ_D > ρ_E on ≥2/3 tasks

    # ── Canonicalization ───────────────────────────────────────────────
    canon_eps: float = 1e-8          # Numerical stability epsilon in norm computation
    signflip_tie_value: float = 1.0  # Tie-breaking sign (+1 for positive)

    # ── Paths ──────────────────────────────────────────────────────────
    results_path: str = "results.json"
    figures_dir: str = "../figures"
    checkpoint_dir: str = "checkpoints"

    # ── Frozen-Encoder Sub-Experiment ──────────────────────────────────
    run_frozen_experiment: bool = True
    frozen_conditions: list[str] = field(default_factory=lambda: ['B', 'C', 'D'])

DEFAULT_CONFIG = ExperimentConfig()
```

---

## YAML Schema (for CLI / config file override)

```yaml
# h-m3/code/config.yaml — override defaults selectively
hypothesis_id: "h-m3"
conditions: ["A", "B", "C", "D", "E", "F"]
seeds: [42, 123, 456]

weight_dim: 51850
n_labels: 3
label_names: ["test_accuracy", "generalization_gap", "learning_rate"]
val_fraction: 0.1
test_fraction: 0.1

# NFT architecture
embed_dim: 256
n_layers: 4
nhead: 8
dim_feedforward: 512
dropout: 0.1

# Training
lr: 0.001
weight_decay: 0.0001
adam_betas: [0.9, 0.999]
batch_size: 64
max_epochs: 100
es_patience: 10
lr_patience: 5
lr_factor: 0.5
min_lr: 0.00001

# Evaluation
n_boot: 1000
boot_seed: 42
delta_threshold: 0.05

# Paths
results_path: "results.json"
figures_dir: "../figures"
checkpoint_dir: "checkpoints"

# Frozen encoder
run_frozen_experiment: true
frozen_conditions: ["B", "C", "D"]
```

---

## Configuration Subtask C1: Hyperparameter Rationale

| Parameter | Value | Source | Rationale |
|-----------|-------|--------|-----------|
| `lr` | 1e-3 | H-M1 validated | Adam default; confirmed optimal on this task |
| `weight_decay` | 1e-4 | H-M1 validated | Mild regularization; prevents overfitting on ~40k train |
| `batch_size` | 64 | H-M1 validated | GPU memory compatible with 51850-dim vectors |
| `es_patience` | 10 | H-M1 validated | Allows LR schedule to kick in before stopping |
| `n_boot` | 1000 | Standard | Sufficient for stable 95% CI on ρ |
| `delta_threshold` | 0.05 | Phase 2B | Hypothesis gate criterion |
| `embed_dim` | 256 | H-E1/H-M1 | NFT architecture default; reasonable for weight-space |
| `n_layers` | 4 | H-E1/H-M1 | Sufficient depth for weight-space features |
| `seeds` | [42,123,456] | Phase 2C | 3 seeds for CI; more robust than 1-seed PoC |

---

## Inherited Configuration (from h-m2)

From `h-m2/code/data_prep.py` (verified actual code):

```python
# Layer boundary indices (verified from SPLITS)
W1_SLICE = slice(0, 50176)       # W1 flat: 784×64
B1_SLICE = slice(50176, 50240)   # b1: 64
W2_SLICE = slice(50240, 50880)   # W2 flat: 64×10
B2_SLICE = slice(50880, 51850)   # b2: 10
EXPECTED_DIM = 51850

# Inherited from h-m2/code/data_prep.py
CANON_EPS = 1e-8                 # numerical epsilon for norm computation
SIGNFLIP_TIE = 1.0               # tie-breaking value for sign (positive)
```

---

## Config Subtask C2: CLI Argument Parser

```python
def parse_args() -> ExperimentConfig:
    """
    argparse interface for main.py.
    Key flags:
        --condition A|B|C|D|E|F  (default: run all)
        --seed INT                (default: run all 3)
        --no-frozen               (skip frozen encoder experiment)
        --results-path PATH
        --figures-dir PATH
        --config PATH             (load YAML override)
    """
```

---

## Environment Setup

```
# requirements.txt
torch>=2.0
numpy>=1.24
scipy>=1.10
scikit-learn>=1.3
matplotlib>=3.7
tqdm>=4.65
```

Python: 3.10+. CUDA optional (experiment runs on CPU for small zoo; GPU recommended for full 6-condition run).
