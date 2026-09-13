# Config: H-M2 (Layer-wise Probe Sweep)

**Applied**: No directly relevant KB pattern found (diffusers/UNet results only) — used architecture-specified dataclass + H-E1/H-M1 conventions instead.

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-E1, H-M1)
**Status**: Config classes verified from base code (direct file reads; Serena project not registered for this workspace, same as H-M1/H-E1 precedent)
**Config Files Found**: `h-e1/code/config.py`, `h-m1/code/config.py`
**Pattern Used**: dataclass

---

## S-1: Config & Layer Index Mapping [Complexity: 5, Budget: 5]

**Applied**: Architecture-specified `Config` dataclass (h-m2/03_architecture.md) — single fixed config, PoC mode (1 seed).

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass, field
import random
import numpy as np
import torch


@dataclass
class Config:
    seed: int = 42
    model_name: str = "meta-llama/Meta-Llama-3-8B-Instruct"
    torch_dtype: str = "float16"
    device_map: str = "auto"
    num_layers: int = 32
    hidden_dim: int = 4096

    # 8 layer depths: 12.5% -> 100%
    layer_depths: list = field(
        default_factory=lambda: [0.125, 0.25, 0.375, 0.5, 0.6, 0.75, 0.875, 1.0]
    )
    # Gate comparison layers (depth keys used by verify_inverted_u_pattern)
    early_depth: float = 0.25
    middle_depth: float = 0.6
    final_depth: float = 1.0

    n_train: int = 9500
    n_val: int = 1700
    max_new_tokens: int = 32

    lr: float = 1e-2
    weight_decay: float = 1e-4
    epochs: int = 15
    batch_size: int = 256
    optimizer: str = "adamw"
    loss: str = "bce"

    n_bootstrap: int = 1000

    figures_dir: str = "figures/"
    cache_dir: str = "cache/"
    outputs_dir: str = "outputs/"


def get_layer_indices(num_layers: int, depths: list) -> list:
    """Depth fraction -> 0-indexed layer index. For 32 layers: [3,7,11,15,18,23,27,31]."""
    return [max(0, int(d * num_layers) - 1) for d in depths]


def set_seed(seed: int = 42) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


CFG = Config()
LAYER_INDICES = get_layer_indices(CFG.num_layers, CFG.layer_depths)
# -> [3, 7, 11, 15, 18, 23, 27, 31]
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| C-1-1 | Define Config dataclass | Fields per architecture spec above |
| C-1-2 | Implement `get_layer_indices` | Depth-fraction to 0-indexed layer index, verify against `[3,7,11,15,18,23,27,31]` |
| C-1-3 | Implement `set_seed` | Deterministic seeding (random/numpy/torch/cuda) |
| C-1-4 | Instantiate `CFG` + `LAYER_INDICES` module globals | Ready-to-import singletons |

---

## Inherited Configuration (Base Hypothesis)

### Config Classes (From Actual Code)

```python
# From: h-e1/code/config.py (ACTUAL CODE)
@dataclass
class Config:
    seed: int = 42
    model_name: str = "meta-llama/Meta-Llama-3-8B-Instruct"
    torch_dtype: str = "bfloat16"      # NOTE: H-E1 uses bfloat16, H-M2 uses float16 (per PRD 5.1)
    device_map: str = "auto"
    target_layer: int = 19
    hidden_dim: int = 4096
    dataset_name: str = "trivia_qa"
    dataset_config: str = "rc"
    train_size: int = 9500
    val_size: int = 1700
    max_new_tokens: int = 32
    lr: float = 1e-3                   # NOTE: H-M2 overrides to 1e-2 per PRD FR-2
    epochs: int = 10                   # NOTE: H-M2 overrides to 15 per PRD FR-2
    batch_size: int = 256
    optimizer: str = "adam"            # NOTE: H-M2 uses "adamw" per PRD FR-2
    loss: str = "bce"
    auroc_gate: float = 0.60
    auroc_baseline: float = 0.50
    figures_dir: str = "figures/"
    cache_dir: str = "cache/"

# From: h-m1/code/config.py (ACTUAL CODE)
@dataclass
class Config:
    seed: int = 42
    model_name: str = "meta-llama/Meta-Llama-3-8B-Instruct"
    torch_dtype: str = "float16"
    device_map: str = "auto"
    target_layer: int = 19
    n_samples: int = 500
    max_new_tokens: int = 128
    identity_gate: float = 1.0
    overhead_gate_pct: float = 10.0
    figures_dir: str = "figures/"
    cache_dir: str = "cache/"
    outputs_dir: str = "outputs/"
```

### Field Mapping Notes

- Dataset names (`dataset_name="trivia_qa"`, `dataset_config="rc"`), `n_train`/`n_val` (H-E1: `train_size`/`val_size`), and prompt/labeling logic reused from `h-e1/code/data.py` — H-M2's `Config.n_train`/`n_val` field names differ intentionally to match `03_architecture.md` spec; adapt callers accordingly.
- `HiddenStateExtractor` (from `h-m1/code/hooks.py`) is reused verbatim — no config field changes needed; it takes `layer_indices: list[int]` directly (use `LAYER_INDICES` above).
- `torch_dtype`: H-M2 follows H-M1/PRD (`float16`), not H-E1's `bfloat16`.

**Verified from**: `h-e1/code/config.py`, `h-m1/code/config.py` (actual implementation)
