# Config: H-E1 (EXISTENCE PoC)

**Applied**: dataclass-config-pattern (single frozen config, no grid)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new config design (matches architecture's Codebase Analysis)
**Config Files Found**: None
**Pattern Used**: dataclass

---

## A-1: Config + IFEval Data Loading [Complexity: 9, Budget: 1 subtask]

**Applied**: DL config patterns — single fixed dataclass for PoC (no hyperparameter sweep, no CLI overrides needed)

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass

@dataclass
class Config:
    dataset_id: str = "google/IFEval"
    model_id: str = "mistralai/Mistral-7B-Instruct-v0.2"
    dataset_split: str = "train"
    num_prompts: int = 541          # full IFEval set, per PRD FR-1
    temperature: float = 0.7        # PRD FR-2 standard inference setting
    max_new_tokens: int = 512       # enough for constraint-bearing responses
    seed: int = 1                   # PRD NFR-2 reproducibility
    soft_margin: float = 0.1        # tolerance band for soft length/keyword checks
    batch_size: int = 8             # generation batching, memory-bound default
    output_dir: str = "h-e1/figures"
    device: str = "cuda"            # falls back to cpu in load_generator if unavailable
```

No hyperparameter grid — EXISTENCE PoC uses one fixed run to verify: score range, variance, grad flow (per PRD Success Criteria).

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|--------------|
| C-1-1 | Define Config dataclass + wire into data.py/model.py/train.py | Single `config.py` with defaults above; imported by all modules per architecture file structure |
