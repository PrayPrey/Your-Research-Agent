# Architecture: h-e1 Temporal Convergence Validation

**Hypothesis:** h-e1  
**Type:** EXISTENCE (PoC)  
**Date:** 2026-08-28  
**Author:** yoon303@ust.ac.kr  

---

## Knowledge Base Patterns

Applied: Minimal PoC structure (data, model, train, evaluate)

---

## Codebase Analysis (Serena)

**Project Type**: green-field  
**Status**: New implementation from scratch  
**Analyzed Path**: N/A  
**Findings**: No existing codebase - minimal PoC architecture for EXISTENCE validation

---

## Module Structure

### DataModule (`h-e1/code/data.py`)

**Dependencies**: None (stdlib + PyTorch only)

```python
class DatasetConfig:
    name: str
    batch_size: int
    num_workers: int

def get_dataloader(config: DatasetConfig, split: str) -> DataLoader:
    """Load CMNIST, Waterbirds, CelebA, or NICO++"""
    ...

def apply_spurious_mask(images: Tensor, dataset_name: str) -> Tensor:
    """Blur/mask to isolate spurious feature (color, background)"""
    ...

def apply_core_mask(images: Tensor, dataset_name: str) -> Tensor:
    """Grayscale/segment to isolate core feature (shape, foreground)"""
    ...
```

---

### ModelModule (`h-e1/code/model.py`)

**Dependencies**: DataModule

```python
def get_baseline_model(dataset_name: str, pretrained: bool = True) -> nn.Module:
    """ResNet-18 for CMNIST, ResNet-50 for others"""
    ...

class AblationTrainer:
    def __init__(self, model: nn.Module, dataset_name: str, device: str): ...
    
    def train_variant(self, variant: str, dataloader: DataLoader, max_epochs: int) -> int:
        """variant in ['spurious', 'core', 'baseline']. Returns convergence epoch."""
        ...
    
    def compute_gradient_norm(self) -> float:
        """L2 norm of all model gradients"""
        ...
    
    def check_convergence(self) -> bool:
        """True if grad_norm < 10% peak for 3 consecutive epochs"""
        ...
```

---

### TrainModule (`h-e1/code/train.py`)

**Dependencies**: DataModule, ModelModule

```python
class TrainConfig:
    dataset: str
    lr: float
    max_epochs: int
    weight_decay: float
    seed: int

def run_single_experiment(config: TrainConfig) -> dict:
    """
    Returns {'E_spurious': int, 'E_core': int, 'E_baseline': int}
    """
    ...

def run_all_seeds(dataset: str, num_seeds: int = 10) -> list[dict]:
    """Run 10 seeds per dataset"""
    ...
```

---

### EvaluationModule (`h-e1/code/evaluate.py`)

**Dependencies**: TrainModule (results only)

```python
def compute_temporal_gap(results: list[dict]) -> dict:
    """
    Returns {
        'mean_delta': float,
        'std_delta': float,
        't_stat': float,
        'p_value': float
    }
    """
    ...

def check_poc_pass(all_results: dict[str, list]) -> bool:
    """E_s < E_c for >5/10 seeds on all 4 datasets"""
    ...

def save_results(results: dict, output_dir: str):
    """Export CSV + JSON summary"""
    ...

def plot_convergence_comparison(results: dict, output_path: str):
    """MANDATORY: Bar chart mean(E_s) vs mean(E_c) per dataset"""
    ...
```

---

## File Organization

```
h-e1/
├── code/
│   ├── data.py          # 200 lines - loaders + masking
│   ├── model.py         # 150 lines - ResNet + AblationTrainer
│   ├── train.py         # 100 lines - experiment runner
│   └── evaluate.py      # 150 lines - stats + plots
├── results/
│   ├── convergence_data.csv
│   └── stats_summary.json
└── figures/
    └── convergence_comparison.png
```

Total: ~600 lines implementation code

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Data Infrastructure | Loaders for 4 datasets + masking | 11 | 3+2+4+2 |
| A-2 | Baseline Model | ResNet + binary head | 6 | 2+1+2+1 |
| A-3 | Ablation Trainer | Gradient tracking + convergence | 13 | 3+3+5+2 |
| A-4 | Multi-Seed Runner | 40 experiments (4×10 seeds) | 8 | 2+2+2+2 |
| A-5 | Statistical Eval | t-test + PoC gate check | 10 | 2+2+4+2 |
| A-6 | Visualization | Bar chart + save results | 7 | 2+1+2+2 |

**Total Complexity**: 55  
**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-1, A-3, A-5], Low(4-8): [A-2, A-4, A-6]

### Complexity Breakdown

**A-1 (11):** Module_Size=3 (4 datasets × 2 masks), Dependencies=2 (torchvision+wilds), Algorithm=4 (dataset-specific masking), Integration=2

**A-2 (6):** Module_Size=2 (simple wrapper), Dependencies=1 (torchvision), Algorithm=2 (FC replacement), Integration=1

**A-3 (13):** Module_Size=3 (trainer class), Dependencies=3 (data+model+optimizer), Algorithm=5 (convergence detection), Integration=2

**A-4 (8):** Module_Size=2 (loop wrapper), Dependencies=2 (train config), Algorithm=2 (seed management), Integration=2

**A-5 (10):** Module_Size=2 (stats functions), Dependencies=2 (scipy), Algorithm=4 (paired t-test logic), Integration=2

**A-6 (7):** Module_Size=2 (plot functions), Dependencies=1 (matplotlib), Algorithm=2 (bar chart), Integration=2

---

## Configuration

```python
# h-e1/code/config.py
DATASET_CONFIGS = {
    'CMNIST': {'lr': 0.001, 'batch': 128, 'epochs': 50, 'model': 'resnet18'},
    'Waterbirds': {'lr': 0.001, 'batch': 64, 'epochs': 100, 'model': 'resnet50'},
    'CelebA': {'lr': 0.0001, 'batch': 64, 'epochs': 80, 'model': 'resnet50'},
    'NICO++': {'lr': 0.001, 'batch': 64, 'epochs': 100, 'model': 'resnet50'}
}

CONVERGENCE_THRESHOLD = 0.1  # 10% of peak
CONVERGENCE_WINDOW = 3  # epochs
NUM_SEEDS = 10
```

---

## Validation Checklist

- [x] No ASCII diagrams
- [x] Module sections = interface code only
- [x] 6 Epic tasks with complexity
- [x] Total length < 500 lines
- [x] Codebase Analysis section included
- [x] Green-field status noted (no Serena needed)
- [x] EXISTENCE rules: 3-6 tasks (actual: 6)
- [x] Minimal file structure (4 files)
