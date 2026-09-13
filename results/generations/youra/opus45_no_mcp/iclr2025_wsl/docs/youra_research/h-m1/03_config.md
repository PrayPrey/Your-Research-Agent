# Configuration: H-M1 (Layer-wise Structure Advantage)

**Applied**: Standard PyTorch dataclass config, single-file (green-field project)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new config design (matches `03_architecture.md` config.py spec)
**Config Files Found**: None
**Pattern Used**: dataclass

---

## Config Dataclass (`h-m1/code/config.py`)

```python
from dataclasses import dataclass, field

@dataclass
class Config:
    # Data
    data_path: str = "data/dataset_cifar_small_hyp_fix.pt"
    zenodo_doi: str = "10.5281/zenodo.6620869"
    batch_size: int = 256

    # Optimization
    lr: float = 1e-3
    weight_decay: float = 1e-4
    max_epochs: int = 50
    early_stop_patience: int = 10
    lr_scheduler_factor: float = 0.5
    lr_scheduler_patience: int = 5

    # Model dims
    hidden_dim: int = 256
    embed_dim: int = 128
    predictor_hidden: int = 64
    stats_per_layer: int = 4  # mean, std, min, max

    # Reproducibility
    seeds: list = field(default_factory=lambda: [0, 1, 2, 3, 4])
    device: str = "cuda"

    # Output
    output_dir: str = "results/"
    figures_dir: str = "figures/"
```

This is the **only** config format used (no YAML file needed — Phase 4 imports `Config` directly).

---

## Default Values Justification

| Field | Value | Justification |
|-------|-------|----------------|
| `lr` | 1e-3 | Conservative default for AdamW regression (per brief) |
| `weight_decay` | 1e-4 | Standard mild regularization |
| `batch_size` | 256 | Memory/speed balance for variable-shape weight tensors |
| `max_epochs` | 50 | Early stopping governs actual length |
| `early_stop_patience` | 10 | Prevent overfitting on val loss plateau |
| `lr_scheduler_factor/patience` | 0.5 / 5 | ReduceLROnPlateau, adaptive convergence |
| `hidden_dim` / `embed_dim` | 256 / 128 | Matches both encoders per brief pseudo-code |
| `stats_per_layer` | 4 | mean, std, min, max (fixed, not tunable — PoC scope) |
| `seeds` | [0,1,2,3,4] | Required for paired t-test (N=5) |

All other fields are standard defaults, no tuning performed (MECHANISM test, not HPO).

---

## Environment Variables

None required. `device` defaults to `"cuda"`; Phase 4 code should fall back to `"cpu"` if unavailable (runtime check, not config field).
