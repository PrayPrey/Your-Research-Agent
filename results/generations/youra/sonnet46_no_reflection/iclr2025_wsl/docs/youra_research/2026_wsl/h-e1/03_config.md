# Config: H-E1 — Canonical Channel Permutation Invariance & Orbit-PE Computability

**Hypothesis Type**: EXISTENCE (PoC)
**Applied**: Standard Python dataclass evaluation-only config pattern

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new config design
**Config Files Found**: None - new config
**Pattern Used**: dataclass

---

## A-5: Evaluation Loop [Complexity: 11, Budget: 1 subtask]

**Applied**: Standard evaluation-only dataclass config (no training params)

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass, field
from typing import List

@dataclass
class ExperimentConfig:
    # Data paths
    cnn_zoo_dir: str = "data/cnn_zoo/"
    transformer_zoo_dir: str = "data/transformer_zoo/"
    figures_dir: str = "h-e1/figures/"
    results_path: str = "h-e1/results.json"

    # Checkpoint counts
    n_cnn_checkpoints: int = 500
    n_transformer_checkpoints: int = 500  # 250 MNIST + 250 AG-News

    # Permutation settings
    n_permutations: int = 10
    perm_seeds: List[int] = field(default_factory=lambda: list(range(10)))

    # Evaluation settings
    sample_seed: int = 42
    eval_batch_size: int = 256

    # Non-standard: small threshold to detect meaningful accuracy drops under permutation
    delta_acc_threshold: float = 0.001

    # Device (auto-detected; override with CUDA_VISIBLE_DEVICES env var)
    device: str = "cuda"
```

### Config File (config.yaml)

```yaml
cnn_zoo_dir: "data/cnn_zoo/"
transformer_zoo_dir: "data/transformer_zoo/"
figures_dir: "h-e1/figures/"
results_path: "h-e1/results.json"

n_cnn_checkpoints: 500
n_transformer_checkpoints: 500

n_permutations: 10
perm_seeds: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

sample_seed: 42
eval_batch_size: 256
delta_acc_threshold: 0.001

device: "cuda"
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-5-1 | EvalConfig dataclass | Implement `ExperimentConfig` dataclass in `code/config.py` with all fields above; add `load_config()` helper that reads config.yaml and overrides dataclass defaults |
