# Config: H-E1 (EXISTENCE PoC)

**Applied**: contamination-attribution-pipeline pattern (from architecture) — single fixed dataclass, no KB config pattern matched (searched "DL config patterns", no directly relevant hit; using standard PyTorch/HF defaults).

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new config design
**Config Files Found**: None
**Pattern Used**: dataclass

---

## A-1..A-7: Experiment Config [Complexity: N/A, Budget: 1 subtask]

EXISTENCE PoC → single fixed config, no hyperparameter search, 1 seed.

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass, field

@dataclass
class Config:
    # Model
    model_id: str = "EleutherAI/pythia-1b"

    # Injection
    injection_rates: list = field(default_factory=lambda: [0.001, 0.01, 0.05, 0.1])
    ngram_n: int = 13  # Non-standard: 13-gram matches common contamination-detection literature (e.g. GPT-3 paper) for low false-positive rate

    # Optimizer (AdamW, per PRD FR-2.2)
    lr: float = 1e-4
    weight_decay: float = 0.01
    betas: tuple = (0.9, 0.95)

    # Training
    batch_size: int = 512
    grad_accum: int = 8
    train_steps: int = 10_000  # per injection level, per PRD FR-2.3

    # Repro
    seed: int = 42

    # Output
    out_dir: str = "figures/"
```

**Sources**: lr/weight_decay/betas — PRD FR-2.2 (fixed, from Phase 2C brief). injection_rates — PRD FR-1.3. train_steps — PRD FR-2.3. ngram_n — PRD FR-3.1.

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|--------------|
| C-1-1 | config.py | Single `Config` dataclass as above, no variants |
