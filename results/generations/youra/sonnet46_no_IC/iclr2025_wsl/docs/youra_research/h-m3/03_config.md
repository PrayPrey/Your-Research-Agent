# Configuration: H-M3
# Latent Space Interpolation via EquiSSL-perm Decoder

**Hypothesis ID:** H-M3
**Type:** MECHANISM (SHOULD_WORK / PoC)
**Date:** 2026-08-05

Applied: nested-dataclass evaluation config pattern (frozen-model, no training hyperparameters)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (incremental on H-M1 + H-E1)
**Status**: config classes verified from actual base code
**Config Files Found**: `docs/youra_research/h-m1/code/config.py`
**Pattern Used**: module-level constants + dataclass (matching H-M1 style)

---

## Inherited Configuration (Base Hypothesis)

### Config Constants (From Actual H-M1 Code)

```python
# From: docs/youra_research/h-m1/code/config.py (ACTUAL CODE)
HIDDEN_DIM   = 256   # EquiSSLEncoder hidden_dim
LATENT_DIM   = 128   # encoder output latent_dim
NUM_LAYERS   = 4     # encoder num_layers
TEMPERATURE  = 0.07
LAMBDA_REC   = 0.1
```

### Verified Model Init Args (From Actual Code)

```python
# EquiSSLEncoder.__init__: node_in_dim=4, edge_in_dim=4, hidden_dim=256,
#                           latent_dim=128, num_layers=4, symmetry='monomial', pool='mean'
# GraphDecoder.forward(z, structure) -> (B, max_edge_dim) vector
```

**Verified from**: `docs/youra_research/h-m1/code/config.py` + architecture doc

---

## A-2: Pair Builder + Task Loader Config [Complexity: 2, Budget: 2 subtasks]

Applied: standard-dataclass-with-validation pattern

### C-2-1: PairConfig

```python
from dataclasses import dataclass, field
from typing import List

@dataclass
class PairConfig:
    min_pairs: int = 500
    seed: int = 42
    tasks: List[str] = field(default_factory=lambda: ['mnist', 'svhn', 'cifar10'])
    pair_json_path: str = "docs/youra_research/h-m3/code/outputs/pairs.json"

    def validate(self):
        assert self.min_pairs >= 1, "min_pairs must be >= 1"
        assert all(t in {'mnist', 'svhn', 'cifar10'} for t in self.tasks), \
            f"Unknown task in tasks: {self.tasks}"
```

### C-2-2: TaskConfig

```python
@dataclass
class MLPArchConfig:
    in_dim: int
    hidden_dims: List[int]
    out_dim: int

@dataclass
class TaskConfig:
    batch_size: int = 256  # eval-only, no gradient accumulation needed
    data_root: str = "data/multizoo"
    mlp_arch: dict = field(default_factory=lambda: {
        'mnist':   MLPArchConfig(in_dim=784,  hidden_dims=[256, 256], out_dim=10),
        'svhn':    MLPArchConfig(in_dim=3072, hidden_dims=[256, 256], out_dim=10),
        'cifar10': MLPArchConfig(in_dim=3072, hidden_dims=[256, 256], out_dim=10),
    })
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-2-1 | PairConfig | Pair builder params: min_pairs, seed, tasks, output path |
| C-2-2 | TaskConfig | Per-task MLP arch dims + eval batch size + data root |

---

## A-5: Evaluation + Master Config [Complexity: 2, Budget: 2 subtasks]

Applied: master-config composition pattern (sub-configs as nested dataclass fields)

### C-5-1: EvalConfig

```python
import torch

@dataclass
class EvalConfig:
    device: str = "cuda" if torch.cuda.is_available() else "cpu"
    batch_size: int = 256
    data_root: str = "data/multizoo"
```

### C-5-2: HM3Config (Master)

```python
import os
from dataclasses import dataclass, field

PROJECT_ROOT = os.environ.get(
    'PROJECT_ROOT', '/home/PrayPrey/YouRA_no_IC_sonnet46/TEST_wsl'
)
H_M1_CODE = os.path.join(PROJECT_ROOT, 'docs/youra_research/h-m1/code')
H_E1_CODE = os.path.join(PROJECT_ROOT, 'docs/youra_research/h-e1/code')
H_M3_ROOT = os.path.join(PROJECT_ROOT, 'docs/youra_research/h-m3')

@dataclass
class HM3Config:
    # Frozen model checkpoints (from H-M1 / H-E1)
    encoder_ckpt: str = os.path.join(
        PROJECT_ROOT, 'docs/youra_research/h-m1/checkpoints/equi_perm_seed0.pt'
    )
    decoder_ckpt: str = os.path.join(
        PROJECT_ROOT, 'docs/youra_research/h-e1/checkpoints/decoder_seed0.pt'
    )

    # Encoder architecture (must match H-M1 training — verified from actual code)
    hidden_dim: int = 256   # HIDDEN_DIM from h-m1/config.py
    latent_dim: int = 128   # LATENT_DIM from h-m1/config.py
    num_layers: int = 4     # NUM_LAYERS from h-m1/config.py

    # Output paths
    results_dir: str = os.path.join(H_M3_ROOT, 'code/results')
    figures_dir: str = os.path.join(H_M3_ROOT, 'figures')
    data_dir:    str = os.path.join(PROJECT_ROOT, 'data/multizoo')

    # Sub-configs
    pair:  PairConfig  = field(default_factory=PairConfig)
    task:  TaskConfig  = field(default_factory=TaskConfig)
    eval:  EvalConfig  = field(default_factory=EvalConfig)

    def validate(self):
        assert os.path.exists(self.encoder_ckpt), \
            f"Encoder checkpoint not found: {self.encoder_ckpt}"
        assert os.path.exists(self.decoder_ckpt), \
            f"Decoder checkpoint not found: {self.decoder_ckpt}"
        self.pair.validate()
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-5-1 | EvalConfig | Device selection, batch size, data root |
| C-5-2 | HM3Config | Master config: checkpoint paths, output dirs, nested sub-configs |

---

## YAML Reference Schema

For documentation / reproducibility only. Python dataclasses above are the authoritative source.

```yaml
# h-m3/code/config.yaml (reference schema)
encoder_ckpt: "docs/youra_research/h-m1/checkpoints/equi_perm_seed0.pt"
decoder_ckpt: "docs/youra_research/h-e1/checkpoints/decoder_seed0.pt"
hidden_dim: 256
latent_dim: 128
num_layers: 4
results_dir: "docs/youra_research/h-m3/code/results"
figures_dir: "docs/youra_research/h-m3/figures"
data_dir: "data/multizoo"

pair:
  min_pairs: 500
  seed: 42
  tasks: [mnist, svhn, cifar10]
  pair_json_path: "docs/youra_research/h-m3/code/outputs/pairs.json"

task:
  batch_size: 256
  data_root: "data/multizoo"
  mlp_arch:
    mnist:   {in_dim: 784,  hidden_dims: [256, 256], out_dim: 10}
    svhn:    {in_dim: 3072, hidden_dims: [256, 256], out_dim: 10}
    cifar10: {in_dim: 3072, hidden_dims: [256, 256], out_dim: 10}

eval:
  device: "cuda"   # auto-detected at runtime
  batch_size: 256
  data_root: "data/multizoo"
```

---

## Self-Validation

- [x] ONE format (dataclass only; YAML is reference schema, not a second config)
- [x] No ASCII diagrams
- [x] No KB search logs (only "Applied: X" lines)
- [x] Rationale only for non-standard values (none needed here)
- [x] Subtask count within budget (4 total: C-2-1, C-2-2, C-5-1, C-5-2)
- [x] "Codebase Analysis (Serena)" section included
- [x] Field names verified from actual h-m1/code/config.py
- [x] Inherited Configuration section included
- [x] No training hyperparameters (frozen models — evaluation only)
