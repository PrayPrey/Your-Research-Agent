# Config: H-M1

**Applied**: PyTorch dataclass config pattern (no matching KB hit for DL config patterns; used standard ERM/SGD defaults from group_DRO paper)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new config design (matches architecture.md analysis; no base_hypothesis or existing code)
**Config Files Found**: None - new config
**Pattern Used**: dataclass

---

## A-1/A-2/A-5: Training Config [Complexity: 13, Budget: 13]

**Applied**: Standard ERM SGD+StepLR defaults (group_DRO paper conventions)

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass

@dataclass
class Config:
    seed: int = 0
    lr: float = 1e-3
    momentum: float = 0.9
    weight_decay: float = 1e-4
    batch_size: int = 128
    epochs: int = 50
    step_size: int = 10          # StepLR: decay every 10 epochs
    gamma: float = 0.1           # StepLR decay factor
    num_workers: int = 4
    image_size: int = 224
    num_classes: int = 2
    majority_groups: tuple = (0, 3)
    minority_groups: tuple = (1, 2)
    device: str = "cuda"
    data_root: str = "./data/waterbirds"
    results_dir: str = "./results/h-m1"
```

### Seed Management

```python
SEEDS = [0, 1, 2, 3, 4]  # 5 seeds for 95% CI (per PRD FR-5)

def set_seed(seed: int) -> None:
    import random, numpy as np, torch
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| C-1-1 | Data loading config | Waterbirds paths, group labels, transforms |
| C-1-2 | Model config | ResNet-50 fc replacement, num_classes |
| C-1-3 | Training loop config | SGD/StepLR params, per-epoch logging |
| C-1-4 | Multi-seed runner | Loop SEEDS, call set_seed, save per-seed r_t/SR_t to results_dir |

---

## A-6: Cross-Correlation Config [Complexity: 10, Budget: within A-1 allocation]

**Applied**: scipy lagged cross-correlation + bootstrap CI (standard defaults, no non-standard values)

### Configuration (Python Dataclass)

```python
@dataclass
class AnalysisConfig:
    max_lag: int = 5             # epochs, per PRD FR-5
    confidence: float = 0.95     # 95% CI per PRD success criteria
    n_bootstrap: int = 10000
    tau_pass_threshold: float = 0.0  # gate: CI must exclude zero (tau > 0)
```

No additional subtasks — covered by A-6 in architecture task table (out of this agent's 4-subtask budget scope; analysis config only).

---

## Data Preprocessing Defaults (referenced by A-1)

```python
IMAGENET_MEAN = (0.485, 0.456, 0.406)
IMAGENET_STD = (0.229, 0.224, 0.225)
# Train: RandomResizedCrop(224), RandomHorizontalFlip, Normalize
# Val/Test: Resize(256), CenterCrop(224), Normalize
```

**Default value sources**:
- lr, momentum, weight_decay, batch_size, StepLR params — group_DRO paper (arXiv:1911.08731), standard ResNet-50 ERM baseline
- epochs=50, max_lag=5, seeds=5, confidence=0.95 — PRD FR-5, FR-6, Section 5
- ImageNet mean/std — torchvision pretrained ResNet-50 standard
