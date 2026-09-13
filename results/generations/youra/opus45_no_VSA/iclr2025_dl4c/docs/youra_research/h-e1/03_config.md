# Config: H-E1 (EXISTENCE PoC)

**Applied**: Single fixed hardcoded config, no hyperparameter sweep (EXISTENCE PoC pattern; low KB relevance for RL/refine-specific config, defaults taken from PRD FR-2/FR-3)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new config design, no existing code
**Config Files Found**: None
**Pattern Used**: Dataclass (`config.py`, per architecture)

---

## A-1: Data + Config Setup [Complexity: 5, Budget: 5]

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass, field

@dataclass
class Config:
    # Model
    model_id: str = "Salesforce/codet5p-220m"
    lora_r: int = 16
    lora_target_modules: list = field(default_factory=lambda: ["q_proj", "k_proj", "v_proj"])

    # CE training
    lr: float = 2e-5
    weight_decay: float = 0.05
    warmup_steps: int = 200
    batch_size: int = 8
    ce_epochs: int = 10

    # RL training (runs after CE warmup)
    rl_epochs: int = 5

    # Self-refine inference
    refine_k: int = 3

    # Reproducibility
    seed: int = 42

    # Paths
    cache_dir: str = "h-e1/data_cache"
    checkpoint_dir: str = "h-e1/checkpoints"
    figures_dir: str = "h-e1/figures"
```

No hyperparameter grid, no ablations, single seed — PoC only tests "does interaction effect exist."

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-1-1 | Config dataclass | Implement `Config` in `config.py` per above |
| C-1-2 | Dataset loading + cache | `evalplus.data.get_human_eval_plus()` / `get_mbpp_plus()`, cache to `cfg.cache_dir` |

---

## A-2 through A-7

Reuse `Config` above — no additional config classes needed (single fixed config per EXISTENCE rules). No subtasks allocated to config for these tasks; hyperparameters consumed directly from `Config` instance passed into `model.py`, `train.py`, `refine.py`, `evaluate.py`.
