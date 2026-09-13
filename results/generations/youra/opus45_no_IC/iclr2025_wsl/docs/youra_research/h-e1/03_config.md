# Config: H-E1 (EXISTENCE / PoC)

Applied: Standard PyTorch dataclass config pattern (single fixed config, no HP grid)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new config design, H-E1 is foundation hypothesis
**Config Files Found**: None
**Pattern Used**: dataclass

---

## A-1..A-7: Global Config [Complexity: 1, Budget: 1]

PoC scope — single fixed config, no variations, no ablations, one seed.

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass

@dataclass
class Config:
    # Reproducibility
    seed: int = 0

    # Data
    n_models: int = 1000
    train_frac: float = 0.8

    # Optimization
    lr: float = 1e-3
    weight_decay: float = 1e-4
    epochs: int = 50
    batch_size: int = 32

    # NFN model
    nfn_channels: int = 32

    # MLP-Matched model
    mlp_hidden_dim: int = 256
    mlp_num_layers: int = 3

    # Scheduler (CosineAnnealingLR)
    scheduler_t_max: int = 50       # = epochs
    scheduler_eta_min: float = 1e-6

    # Paths
    checkpoint_dir: str = "h-e1/checkpoints"
    figure_dir: str = "h-e1/figures"
    results_path: str = "h-e1/results.json"

    # Success criterion
    r2_diff_threshold: float = 0.05
```

### YAML Equivalent

```yaml
seed: 0
n_models: 1000
train_frac: 0.8
lr: 0.001
weight_decay: 0.0001
epochs: 50
batch_size: 32
nfn_channels: 32
mlp_hidden_dim: 256
mlp_num_layers: 3
scheduler_t_max: 50
scheduler_eta_min: 0.000001
checkpoint_dir: h-e1/checkpoints
figure_dir: h-e1/figures
results_path: h-e1/results.json
r2_diff_threshold: 0.05
```

### Experiment Tracking

No external tracker (W&B/MLflow) for PoC — `train_model()` returns
`{"train_loss": [...], "val_loss": [...]}` per FR, persisted via
`evaluate.save_results_json()` to `results_path`. Sufficient for
EXISTENCE verdict (hypothesis_supported bool + R² values).

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|--------------|
| C-1-1 | config.py | Single `Config` dataclass, all defaults above, no variants |
