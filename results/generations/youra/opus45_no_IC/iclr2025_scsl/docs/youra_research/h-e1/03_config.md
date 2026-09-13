# Config: H-E1 (EXISTENCE PoC)

**Applied**: Standard PyTorch dataclass config (Archon KB had no direct config-pattern match)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new config design
**Config Files Found**: None - new config
**Pattern Used**: dataclass

---

## A-1..A-8: Single PoC Config [Complexity: total 45, Budget: 2 subtasks]

EXISTENCE PoC — single fixed config, no sweeps/ablations.

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass

@dataclass
class Config:
    # Reproducibility
    seed: int = 42

    # Data
    data_url: str = "https://nlp.stanford.edu/data/dro/waterbird_complete95_forest2water2.tar.gz"
    data_root: str = "./data/waterbirds"
    img_size: int = 224
    norm_mean: tuple = (0.485, 0.456, 0.406)
    norm_std: tuple = (0.229, 0.224, 0.225)
    batch_size: int = 64
    num_workers: int = 4

    # Model
    num_classes: int = 2
    pretrained: bool = True

    # Training (SGD, per PRD NFR-2)
    n_epochs: int = 100
    lr: float = 1e-3
    momentum: float = 0.9
    weight_decay: float = 1e-4
    device: str = "cuda"

    # OnsetDelayTracker
    onset_threshold: float = 0.9   # d_i = first epoch L_i(t) < 0.9 * L_i(0)
    t_early: int = 20              # minority prediction threshold

    # Evaluation
    pr_curve_t_range: tuple = (1, 50)   # T_early sweep for PR curve
    loss_traj_sample_n: int = 20        # samples plotted in trajectory figure
    alpha: float = 0.05                 # significance level for Mann-Whitney U

    # Paths
    output_dir: str = "./outputs/h-e1"
    figures_dir: str = "./outputs/h-e1/figures"
    metrics_path: str = "./outputs/h-e1/metrics.json"
    checkpoint_path: str = "./outputs/h-e1/model.pt"
```

### YAML Schema Example

```yaml
seed: 42

data:
  url: "https://nlp.stanford.edu/data/dro/waterbird_complete95_forest2water2.tar.gz"
  root: "./data/waterbirds"
  img_size: 224
  norm_mean: [0.485, 0.456, 0.406]
  norm_std: [0.229, 0.224, 0.225]
  batch_size: 64
  num_workers: 4

model:
  num_classes: 2
  pretrained: true

train:
  n_epochs: 100
  lr: 0.001
  momentum: 0.9
  weight_decay: 0.0001
  device: "cuda"

tracker:
  onset_threshold: 0.9
  t_early: 20

eval:
  pr_curve_t_range: [1, 50]
  loss_traj_sample_n: 20
  alpha: 0.05

paths:
  output_dir: "./outputs/h-e1"
  figures_dir: "./outputs/h-e1/figures"
  metrics_path: "./outputs/h-e1/metrics.json"
  checkpoint_path: "./outputs/h-e1/model.pt"
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| C-1 | Config dataclass | Implement `Config` dataclass in `config.py` with defaults above |
| C-2 | Path setup | Ensure `output_dir`/`figures_dir` created at run start; wire config into train.py/evaluate.py |
