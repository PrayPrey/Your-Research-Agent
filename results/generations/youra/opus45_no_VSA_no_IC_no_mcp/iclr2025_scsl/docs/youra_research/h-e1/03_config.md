# Config: H-E1 (EXISTENCE / PoC)

Applied: single fixed dataclass config (no grid/ablation, PoC pattern)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new config design
**Config Files Found**: None
**Pattern Used**: dataclass

---

## A-CONFIG: Fixed Experiment Config [Complexity: 1, Budget: 1]

**Applied**: Standard PyTorch ERM training defaults (single seed, PoC)

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass

@dataclass
class Config:
    seed: int = 42
    batch_size: int = 128
    lr: float = 0.01
    momentum: float = 0.9
    weight_decay: float = 1e-4
    step_size: int = 20
    gamma: float = 0.1
    epochs: int = 50
    attribution_subset_size: int = 500
    data_root: str = "./data/waterbirds_v1.0"
    output_dir: str = "./h-e1/results"
```

No hyperparameter tuning — values fixed per PRD FR-2/FR-3/NFR-2. Single seed only (PoC, no ablation).

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|--------------|
| C-CONFIG-1 | Config dataclass | Implement `Config` in `config.py` as specified above |
