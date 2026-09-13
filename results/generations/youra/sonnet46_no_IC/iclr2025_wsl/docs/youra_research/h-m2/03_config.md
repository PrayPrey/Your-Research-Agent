# Configuration: H-M2
# Scale vs Permutation Equivariance Ablation

**Applied**: Standard dataclass flat-config pattern (incremental from H-M1)

---

## Inherited Configuration (Base Hypothesis)

Verified from `/docs/youra_research/h-m1/code/config.py` (actual code):

```python
# Verified field names and defaults from h-m1/code/config.py
HIDDEN_DIM   = 256
LATENT_DIM   = 128
NUM_LAYERS   = 4
LR           = 1e-3
WEIGHT_DECAY = 1e-4
BETAS        = (0.9, 0.999)
BATCH_SIZE   = 64
EPOCHS       = 100
T_MAX        = 100
ETA_MIN      = 1e-5
TEMPERATURE  = 0.07
LAMBDA_REC   = 0.1
VAL_FRACTION = 0.1
RIDGE_ALPHAS   = [0.1, 1.0, 10.0, 100.0]
PROBE_TEST_FRAC = 0.2

# H-M1 dataclass (actual field names):
@dataclass
class EquiSSLPermConfig:
    symmetry: str = "permutation"
    node_dim: int = 64
    edge_dim: int = 64
    hidden_dim: int = 256
    latent_dim: int = 128
    num_layers: int = 4
    lr: float = 1e-3
    weight_decay: float = 1e-4
    batch_size: int = 64
    epochs: int = 100
    temperature: float = 0.07
    lambda_rec: float = 0.1
    seeds: List[int] = field(default_factory=lambda: [0, 1, 2])
```

**Verified from**: `h-m1/code/config.py` actual implementation.

---

## A-1: H-M2 Experiment Config [Complexity: 1, Budget: 1]

**Applied**: Standard dataclass flat-config pattern

### Configuration

```python
"""H-M2 configuration: scale vs permutation equivariance ablation."""
import os
from dataclasses import dataclass, field
from typing import List

# ── Inherited from H-M1 (do not change — controlled ablation) ──────────────
HIDDEN_DIM   = 256
LATENT_DIM   = 128
NUM_LAYERS   = 4
LR           = 1e-3
WEIGHT_DECAY = 1e-4
BETAS        = (0.9, 0.999)
BATCH_SIZE   = 64
EPOCHS       = 100
T_MAX        = 100
ETA_MIN      = 1e-5
TEMPERATURE  = 0.07
LAMBDA_REC   = 0.1
VAL_FRACTION = 0.1
RIDGE_ALPHAS    = [0.1, 1.0, 10.0, 100.0]
PROBE_TEST_FRAC = 0.2

# ── H-M2 specific ──────────────────────────────────────────────────────────
EXPERIMENT_ID   = "h-m2"
ABLATION_MODE   = True
SEEDS           = [0, 1, 2, 3, 4]   # 5 seeds; seed 0 from H-M1, seeds 1-4 new
GATE_THRESHOLD  = 0.05              # ΔR² SHOULD_WORK gate
GATE_TYPE       = "SHOULD_WORK"

# Paths
PROJECT_ROOT   = os.environ.get('PROJECT_ROOT',
                    '/home/PrayPrey/YouRA_no_IC_sonnet46/TEST_wsl')
H_E1_CKPT_DIR  = os.path.join(PROJECT_ROOT, 'docs/youra_research/h-e1/checkpoints')
H_M1_ROOT      = os.path.join(PROJECT_ROOT, 'docs/youra_research/h-m1')
H_M2_ROOT      = os.path.join(PROJECT_ROOT, 'docs/youra_research/h-m2')

CHECKPOINT_DIR  = os.path.join(H_M2_ROOT, 'checkpoints')
FIGURES_DIR     = os.path.join(H_M2_ROOT, 'figures')
RESULTS_DIR     = os.path.join(H_M2_ROOT, 'results')

VIT_ZOO_ROOT  = os.path.join(PROJECT_ROOT,
    'data/vit_zoo/vit-modelzoo/vit_imagenet_pretrained')
MULTIZOO_ROOT = os.environ.get('MULTIZOO_ROOT',
    os.path.join(PROJECT_ROOT, 'data/multizoo'))

# Checkpoint path patterns
EQUISSL_CKPT_PATTERN     = os.path.join(H_E1_CKPT_DIR, 'equissl_best_seed{seed}.pt')
EQUI_PERM_SEED0_CKPT     = os.path.join(H_M1_ROOT, 'checkpoints/equi_perm_seed0.pt')
EQUI_PERM_OUTPUT_PATTERN = os.path.join(CHECKPOINT_DIR, 'equi_perm_seed{seed}.pt')


@dataclass
class EquiSSLPermConfig:
    """EquiSSL-perm training config for seeds 1-4. Mirrors H-M1 EquiSSLPermConfig exactly."""
    symmetry: str = "permutation"
    node_dim: int = 64
    edge_dim: int = 64
    hidden_dim: int = HIDDEN_DIM
    latent_dim: int = LATENT_DIM
    num_layers: int = NUM_LAYERS
    lr: float = LR
    weight_decay: float = WEIGHT_DECAY
    batch_size: int = BATCH_SIZE
    epochs: int = EPOCHS
    temperature: float = TEMPERATURE
    lambda_rec: float = LAMBDA_REC
    perm_augment: bool = True
    scale_augment: bool = False   # CRITICAL: must be False for ablation validity
    seeds: List[int] = field(default_factory=lambda: [1, 2, 3, 4])  # seed 0 from H-M1


@dataclass
class EvalConfig:
    """Linear probe evaluation config (same as H-M1)."""
    test_frac: float = PROBE_TEST_FRAC
    ridge_alphas: List[float] = field(default_factory=lambda: list(RIDGE_ALPHAS))
    gate_threshold: float = GATE_THRESHOLD
    gate_type: str = GATE_TYPE
```

### Subtasks [5/5 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-1-1 | EquiSSL-perm training config | `EquiSSLPermConfig` for seeds 1-4 |
| C-1-2 | Eval config | `EvalConfig` with gate threshold |
| C-1-3 | Path constants | Checkpoint patterns, output dirs |
| C-1-4 | Inherited constants | All H-M1 hyperparams carried over unchanged |
| C-1-5 | Ablation flags | `ablation_mode`, `scale_augment=False` guard |

---

## Known Seed 0 Values (Reference Constants)

```python
# Pre-observed from H-M1 seed 0 — do not recompute, use as sanity check target
SEED0_EQUISSL_R2     = 0.2098
SEED0_EQUI_PERM_R2   = 0.2305
SEED0_DELTA_R2       = -0.0207
SANE_R2_BASELINE     = 0.0721
```
