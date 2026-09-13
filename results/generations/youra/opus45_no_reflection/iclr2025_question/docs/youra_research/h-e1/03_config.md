# Configuration: H-E1 (EXISTENCE PoC)

**Applied**: Standard PyTorch/HF defaults (KB had no direct dataclass config match; used venator/linear-probe conventions)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new config design
**Config Files Found**: None - new config
**Pattern Used**: dataclass

---

## A-1: Data Pipeline Config [Complexity: 10, Budget: 10]

**Applied**: Standard HF datasets loading pattern; single fixed config (EXISTENCE PoC — no variations)

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass, field

@dataclass
class Config:
    # Reproducibility
    seed: int = 42

    # Model
    model_name: str = "meta-llama/Meta-Llama-3-8B-Instruct"
    torch_dtype: str = "bfloat16"
    device_map: str = "auto"
    target_layer: int = 19          # 60% depth of 32 layers
    hidden_dim: int = 4096

    # Data
    dataset_name: str = "trivia_qa"
    dataset_config: str = "rc"
    train_size: int = 95000
    val_size: int = 17000
    max_new_tokens: int = 32        # greedy decoding for answer generation

    # Training (linear probe)
    lr: float = 1e-3
    epochs: int = 10
    batch_size: int = 256
    optimizer: str = "adam"
    loss: str = "bce"

    # Evaluation
    auroc_gate: float = 0.60
    auroc_baseline: float = 0.50

    # Paths
    figures_dir: str = "figures/"
    cache_dir: str = "cache/"
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|--------------|
| C-1-1 | Config module | Single `Config` dataclass in `config.py`, instantiated once as `CFG = Config()`, imported by all other modules |

---

## Environment Variable Mapping

| Env Var | Config Field | Default |
|---------|-------------|---------|
| `HF_TOKEN` | (used by `from_pretrained` for gated Llama-3 weights) | required, no default |
| `HF_HOME` | HF cache location (not a Config field) | HF default |

No other env vars required — all hyperparameters are fixed in `Config` per EXISTENCE PoC rules.

---

## Reproducibility Settings

```python
import random, numpy as np, torch

def set_seed(seed: int = 42):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
```

Call `set_seed(CFG.seed)` at top of `train.py::main()` before any data loading or model init.

---

## YAML Example (reference only — dataclass is source of truth)

```yaml
seed: 42
model_name: meta-llama/Meta-Llama-3-8B-Instruct
torch_dtype: bfloat16
target_layer: 19
hidden_dim: 4096
dataset_name: trivia_qa
dataset_config: rc
train_size: 95000
val_size: 17000
lr: 0.001
epochs: 10
batch_size: 256
auroc_gate: 0.60
auroc_baseline: 0.50
```
