# Configuration: H-M2 (Alignment Preprocessing Benefit)

**Applied**: Standard PyTorch dataclass config, extends H-M1 (green-field project)

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (extends H-M1)
**Status**: field names verified from `h-m1/03_config.md` (actual `Config` dataclass, no Serena MCP — no-mcp mode, spec used as ground truth per file read)
**Config Files Found**: `h-m1/03_config.md` (Config dataclass, 03_config.md is source since no `h-m1/code/config.py` exists yet — H-M1 spec doc is authoritative pre-Phase-4)
**Pattern Used**: dataclass

---

## Inherited Configuration (Base Hypothesis)

```python
# From: h-m1/03_config.md (verified field names)
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
    stats_per_layer: int = 4

    # Reproducibility
    seeds: list = field(default_factory=lambda: [0, 1, 2, 3, 4])
    device: str = "cuda"

    # Output
    output_dir: str = "results/"
    figures_dir: str = "figures/"
```

---

## A-1: Alignment Config Extension

**Applied**: Standard PyTorch defaults + dataclass inheritance

### Configuration (Python Dataclass, `h-m2/code/config.py`)

```python
from dataclasses import dataclass, field
from h_m1.config import Config as H_M1_Config

@dataclass
class Config(H_M1_Config):
    # Alignment (Git Re-Basin)
    use_alignment: bool = True          # toggle for baseline vs GRB ablation
    alignment_reference_idx: int = 0    # first model as reference
    alignment_algorithm: str = "greedy" # "greedy" or "hungarian"
    alignment_cache_path: str = "cache/aligned_weights.pt"
    convergence_threshold: float = 0.95 # target GRB convergence rate

    # Output override
    output_dir: str = "h-m2/results/"
    figures_dir: str = "h-m2/figures/"
```

### Default Values Justification

| Field | Value | Justification |
|-------|-------|----------------|
| `use_alignment` | True | Default = proposed method; set False to run H-M1 baseline for comparison |
| `alignment_reference_idx` | 0 | First model in sorted train split (deterministic, per brief) |
| `alignment_algorithm` | "greedy" | PoC default per PRD Non-Goals (Hungarian is ablation-only, FR-8.2) |
| `alignment_cache_path` | "cache/aligned_weights.pt" | Avoid re-computing alignment across seed runs (NFR-2) |
| `convergence_threshold` | 0.95 | Matches gate secondary check (PRD Section 8) |

All other fields inherited unchanged from H-M1 (lr, batch_size, seeds, epochs, etc.).

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|--------------|
| C-1-1 | Baseline run | Train H-M1 Layer-wise encoder with `use_alignment=False` |
| C-1-2 | GRB run | Run alignment preprocessing (`use_alignment=True`), train identical regressor on aligned weights |
| C-1-3 | Ablation config | Separate `Config(alignment_algorithm="hungarian")` and `Config(alignment_reference_idx=...)` instances for FR-8 ablations |

---

## Ablation Configs (FR-8)

```python
# Reference selection ablation
Config(alignment_reference_idx=0)      # first (default)
# random/median/highest handled at runtime by passing computed idx, not new fields

# Algorithm ablation
Config(alignment_algorithm="greedy")   # default
Config(alignment_algorithm="hungarian")

# Partial alignment ablation — reuse existing fields, no new config needed;
# layer subset passed as function arg to compute_alignment_batch(), not config field
```

No environment variables required.
