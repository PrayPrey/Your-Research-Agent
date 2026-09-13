# Config: H-E1 (EXISTENCE PoC)

Applied: sklearn LogisticRegression linear-probe default-config pattern (no hyperparameter search — PoC gate test only)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new config design
**Config Files Found**: None - new config
**Pattern Used**: dataclass

---

## A-1..A-8: Single Fixed Experiment Config [Complexity: 53, Budget: 0 subtasks]

EXISTENCE PoC — one fixed config, no variations, no tuning, single seed.

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass, field

@dataclass
class Config:
    # Data
    dataset_name: str = "Open-Orca/FLAN"
    n_samples: int = 3000                 # PRD range 2K-5K; 3K balances runtime <30min
    prefix_chars: int = 256
    train_val_test_split: tuple = (0.70, 0.15, 0.15)
    random_state: int = 42

    # Oracle labeling
    base_model_name: str = "meta-llama/Llama-2-7b-hf"
    adapter_ids: list[str] = field(default_factory=lambda: [
        "flan-adapter-1", "flan-adapter-2", "flan-adapter-3",
        "flan-adapter-4", "flan-adapter-5", "flan-adapter-6",
        "flan-adapter-7", "flan-adapter-8", "flan-adapter-9",
    ])  # 9 FLAN-family LoRAs; replace with actual HF repo IDs at implementation

    # Encoder + probe
    encoder_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    max_iter: int = 2000
    solver: str = "lbfgs"

    # Evaluation
    top_k: int = 3

# Instantiate once, no variants
CONFIG = Config()
```

### Gate Thresholds (not tunable, from PRD)

```python
TOP1_PASS = 0.70
TOP3_PASS = 0.85
TOP3_FAIL = 0.60
```

### Subtasks [0/0 used]

None — EXISTENCE PoC, no subtask decomposition per budget.
