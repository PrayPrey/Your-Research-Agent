# Architecture Design: h-c1 Gradient-Aware Training

**Date:** 2026-08-29  
**Hypothesis:** h-c1 (CONDITION)  
**Author:** Architecture Agent  
**Input:** 03_prd.md, 02c_experiment_brief.md

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis  
**Status:** Patterns found from h-m1 code  
**Analyzed Path:** docs/youra_research/h-m1/code/  
**Findings:** Flat module structure, config-driven experiment scripts, direct imports from local modules.

**Import Patterns from h-m1:**
```python
# h-m1 uses direct local imports
from data_loader import get_dataloader
from layer_analyzer import LayerNeuronAnalyzer
```

**Reuse Strategy for h-c1:** Adopt same flat structure. Add custom optimizer wrapper and training loop modules.

---

## Applied: DL Experiment Training Pattern

**Source:** Standard supervised learning with custom optimizer  
**Pattern:** Modular training script with pluggable optimizer wrapper  
**Justification:** Gradient-aware LR modulation requires optimizer-level intervention.

---

## Module Structure

```
h-c1/
├── code/
│   ├── train.py                    # Main training script
│   ├── data/
│   │   └── waterbirds_loader.py   # Waterbirds dataset wrapper
│   ├── models/
│   │   └── resnet.py              # ResNet-50 wrapper
│   ├── optimizers/
│   │   ├── gradient_aware.py      # GradientAwareOptimizer wrapper
│   │   └── jtt_optimizer.py       # JTT two-stage training wrapper
│   ├── training/
│   │   ├── trainer.py             # Training loop abstraction
│   │   └── evaluator.py           # Worst-group accuracy metrics
│   ├── utils/
│   │   ├── rho_loader.py          # Load ρ_j from h-m1 results
│   │   └── checkpoint.py          # Model checkpoint utilities
│   └── visualize.py                # 4 required plots
├── config.yaml                     # Hyperparameters
├── figures/                        # Output plots
└── 04_validation.md                # Generated report
```

---

## Core Modules

### GradientAwareOptimizer (`optimizers/gradient_aware.py`)

**Dependencies:** torch.optim, rho_loader

```python
class GradientAwareOptimizer:
    def __init__(self, base_optimizer, rho_j_dict: Dict[str, float], base_lr: float): ...
    def step(self): ...
    def zero_grad(self): ...
    def state_dict(self) -> dict: ...
    def load_state_dict(self, state_dict: dict): ...
```

### WaterbirdDataset (`data/waterbirds_loader.py`)

**Dependencies:** torchvision.datasets, PIL

```python
class WaterbirdDataset(Dataset):
    def __init__(self, root: str, split: str, transform): ...
    def __getitem__(self, idx: int) -> Tuple[Tensor, int, int]: ...
    def __len__(self) -> int: ...

def get_waterbirds_loader(config: dict, split: str) -> DataLoader: ...
```

### Trainer (`training/trainer.py`)

**Dependencies:** models, optimizers, evaluator

```python
class Trainer:
    def __init__(self, model, optimizer, train_loader, val_loader, config): ...
    def train_epoch(self, epoch: int) -> float: ...
    def validate(self) -> Dict[str, float]: ...
    def run(self, epochs: int) -> Dict[str, List[float]]: ...
```

### Evaluator (`training/evaluator.py`)

**Dependencies:** torch

```python
def worst_group_accuracy(preds: Tensor, labels: Tensor, groups: Tensor) -> float: ...
def per_group_accuracy(preds: Tensor, labels: Tensor, groups: Tensor) -> np.ndarray: ...
def evaluate_model(model, dataloader, device: str) -> Dict[str, float]: ...
```

### RhoLoader (`utils/rho_loader.py`)

**Dependencies:** h-m1 validation results

```python
def load_rho_j_from_h_m1(h_m1_validation_path: str) -> Dict[str, float]: ...
def map_rho_j_to_resnet50_params(rho_j_dict: Dict, model) -> Dict[str, float]: ...
```

---

## External Dependencies

### From h-m1 (Prerequisite)

**ρ_j values source:** h-m1/04_validation.md or h-m1/results/layer_rho_j.npy

```python
# Import path for ρ_j loading
from pathlib import Path
h_m1_path = Path("../h-m1/results/layer_rho_j.npy")
rho_j_dict = np.load(h_m1_path, allow_pickle=True).item()
```

**Note:** h-m1 provided layer-wise ρ_j on CMNIST. h-c1 must map these to Waterbirds ResNet-50 parameters (see utils/rho_loader.py).

### Python Packages

```python
import torch
import torchvision.models as models
from torchvision import transforms
import numpy as np
import pandas as pd
from scipy.stats import ttest_rel
import matplotlib.pyplot as plt
import seaborn as sns
import yaml
```

**Versions:**
- PyTorch >= 2.0
- torchvision >= 0.15
- scipy >= 1.7

---

## Epic Tasks

**Hypothesis Type:** CONDITION  
**Tier:** FULL  
**Epic Range:** 6-12 tasks  
**Target:** 8 Epics

**Complexity Scoring:** Module_Size (1-8) + Dependencies (1-4) + Algorithm (1-4) + Integration (1-4) = Total (4-20)

---

### Epic 1: Waterbirds Dataset Setup

**Complexity:** 7 (Module=3, Dependencies=2, Algorithm=1, Integration=1)

**Description:** Download Waterbirds dataset, implement loader with group labels for worst-group accuracy.  
**Deliverable:** `data/waterbirds_loader.py`, test script verifying 4795 train / 1199 val / 5794 test splits.

---

### Epic 2: ResNet-50 Baseline Model

**Complexity:** 5 (Module=2, Dependencies=2, Algorithm=0, Integration=1)

**Description:** Wrap torchvision ResNet-50 with final layer modified for 2-class Waterbirds.  
**Deliverable:** `models/resnet.py`, test loading pretrained weights.

---

### Epic 3: ρ_j Loading from h-m1

**Complexity:** 9 (Module=3, Dependencies=3, Algorithm=2, Integration=1)

**Description:** Load h-m1 layer-wise ρ_j values, map CMNIST ResNet-18 neurons to Waterbirds ResNet-50 parameters.  
**Deliverable:** `utils/rho_loader.py` with mapping logic, test ρ_j dict for ResNet-50 layers.

**Risk:** ρ_j transfer from CMNIST to Waterbirds may not hold. Mitigation: Document fallback to uniform ρ_j if performance degrades.

---

### Epic 4: GradientAwareOptimizer

**Complexity:** 11 (Module=4, Dependencies=2, Algorithm=3, Integration=2)

**Description:** Implement optimizer wrapper applying lr_j = base_lr * (1 - ρ_j) per parameter group.  
**Deliverable:** `optimizers/gradient_aware.py`, unit test verifying LR modulation for sample ρ_j dict.

**Core Formula:**
```python
modulated_lr = base_lr * (1 - rho_j)
param_group['lr'] = max(modulated_lr, 1e-5)  # Floor
```

---

### Epic 5: JTT Baseline Implementation

**Complexity:** 12 (Module=5, Dependencies=3, Algorithm=3, Integration=1)

**Description:** Two-stage training: (1) 100 epochs ERM, (2) 200 epochs upweighted misclassified examples.  
**Deliverable:** `optimizers/jtt_optimizer.py`, training script running JTT baseline across 10 seeds.

**Expected Result:** ~87% worst-group accuracy (literature benchmark).

---

### Epic 6: Training Pipeline

**Complexity:** 10 (Module=4, Dependencies=4, Algorithm=1, Integration=1)

**Description:** Unified training loop for ERM, JTT, Gradient-Aware with worst-group validation.  
**Deliverable:** `training/trainer.py`, `training/evaluator.py`, config-driven main script `train.py`.

---

### Epic 7: Statistical Validation (Test 9)

**Complexity:** 8 (Module=3, Dependencies=2, Algorithm=2, Integration=1)

**Description:** Paired t-test comparing Gradient-Aware vs JTT across 10 seeds.  
**Deliverable:** Function in `train.py` running scipy.stats.ttest_rel, reporting p-value and Cohen's d.

**Success Criterion:** mean(Gradient-Aware) >= mean(JTT) - 1% AND p < 0.05.

---

### Epic 8: Visualization and Reporting

**Complexity:** 9 (Module=4, Dependencies=2, Algorithm=2, Integration=1)

**Description:** Generate 4 plots: (1) Gate metrics bar chart, (2) LR modulation heatmap, (3) Training curves, (4) Per-group accuracy.  
**Deliverable:** `visualize.py`, auto-generated `04_validation.md`.

---

## Total Complexity

**Epic Count:** 8  
**Total Complexity:** 71 points  
**Average:** 8.9 (Medium)

**Distribution:**
- Very High (16-20): 0
- High (11-15): 2 (Epics 4, 5)
- Medium (6-10): 5 (Epics 1, 3, 6, 7, 8)
- Low (1-5): 1 (Epic 2)

**Compliance:** ✅ Within FULL tier (6-12 Epics)

---

## Data Flow

```
[h-m1 ρ_j values]
       ↓
[RhoLoader] → {layer1: 0.45, layer2: 0.38, ...}
       ↓
[GradientAwareOptimizer]
       ↓
[Waterbirds Train Loader] → [ResNet-50] → [Training Loop]
       ↓
[Validation Loader] → [Worst-Group Accuracy]
       ↓
[10 seeds × 3 methods] → [Statistical Test 9]
       ↓
[Visualizations] → [04_validation.md]
```

---

## Risk Mitigation

**Risk 1: ρ_j Transfer Failure**  
**Mitigation:** Compute ρ_j directly on Waterbirds if h-m1 values don't transfer. Requires re-running h-m1 analysis on Waterbirds dataset.

**Risk 2: Training Instability**  
**Mitigation:** LR floor (1e-5), gradient clipping (max_norm=1.0).

**Risk 3: JTT Baseline Lower than Literature**  
**Mitigation:** Document actual baseline, adjust target threshold to JTT_actual - 1%.

---

**Version:** 1.0  
**Status:** Ready for Logic Agent (Step 5)
