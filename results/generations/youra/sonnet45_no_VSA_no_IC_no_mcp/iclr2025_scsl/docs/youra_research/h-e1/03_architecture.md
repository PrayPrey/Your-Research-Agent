# Architecture Document: h-e1

**Generated**: 2026-08-24  
**Hypothesis**: BN-LN worst-group gap difference exists  
**Type**: EXISTENCE (PoC)  
**Complexity**: Tier 1 (Simple)

---

## Codebase Analysis (Serena)

**Project Type**: green-field  
**Status**: New implementation from scratch  
**Analyzed Path**: N/A  
**Findings**: No existing code to analyze

---

## Module Structure

### Module 1: Data Loader (`data_loader.py`)

**Dependencies**: torch, torchvision, wilds

```python
from torch.utils.data import DataLoader
from wilds import get_dataset

def get_waterbirds_loader(split: str, batch_size: int = 64, data_dir: str = "./data") -> tuple[DataLoader, list[str]]:
    """
    Args:
        split: 'train', 'val', or 'test'
        batch_size: batch size
        data_dir: cache directory for dataset
    
    Returns:
        (dataloader, group_names) where dataloader yields (images, labels, group_ids)
        images: [B, 3, 224, 224] ImageNet-normalized
        labels: [B] binary (0=landbird, 1=waterbird)
        group_ids: [B] integers 0-3
        group_names: list of 4 strings
    """
    ...
```

---

### Module 2: Models (`models.py`)

**Dependencies**: torch, torchvision

```python
import torch.nn as nn
from torchvision.models import resnet18

def get_resnet_bn(num_classes: int = 2) -> nn.Module:
    """ResNet-18 with BatchNorm (default torchvision), He initialization."""
    ...

def get_resnet_ln(num_classes: int = 2) -> nn.Module:
    """ResNet-18 with BatchNorm replaced by LayerNorm, He initialization."""
    ...

def replace_bn_with_ln(module: nn.Module, feature_map_size: tuple[int, int]) -> nn.Module:
    """
    Recursively replace BatchNorm2d with LayerNorm.
    
    Args:
        module: model to modify
        feature_map_size: (H, W) for current layer
    
    Returns:
        modified module
    """
    ...
```

---

### Module 3: Training (`train.py`)

**Dependencies**: torch, numpy, pandas, tqdm

```python
import torch
import torch.nn as nn
from torch.optim import SGD
from torch.utils.data import DataLoader

def set_seed(seed: int) -> None:
    """Set all random seeds for reproducibility."""
    ...

def train_one_epoch(
    model: nn.Module,
    train_loader: DataLoader,
    optimizer: SGD,
    criterion: nn.Module,
    device: str
) -> float:
    """
    Returns:
        average training loss
    """
    ...

def evaluate(
    model: nn.Module,
    test_loader: DataLoader,
    device: str,
    num_groups: int = 4
) -> dict:
    """
    Returns:
        {
            'avg_accuracy': float,
            'worst_group_accuracy': float,
            'group_accuracies': list[float],  # length 4
            'worst_group_gap': float  # avg - worst
        }
    """
    ...

def train_model(
    architecture_name: str,
    seed: int,
    epochs: int = 100,
    lr: float = 0.01,
    output_csv: str = "results/h-e1/training_metrics.csv"
) -> None:
    """
    Train one (architecture, seed) combination and append metrics to CSV.
    
    CSV columns: seed, architecture, epoch, train_loss, avg_acc, worst_group_acc,
                 group_0_acc, group_1_acc, group_2_acc, group_3_acc, worst_group_gap
    """
    ...

def main():
    """Train both architectures across 10 seeds."""
    ...
```

---

### Module 4: Evaluation (`evaluate.py`)

**Dependencies**: numpy, scipy, pandas, matplotlib

```python
import pandas as pd
from scipy.stats import ttest_rel

def extract_gaps_at_threshold(
    csv_path: str,
    accuracy_threshold: float = 0.90
) -> dict:
    """
    Returns:
        {
            'ResNet-BN': list[float],  # 10 gaps (one per seed)
            'ResNet-LN': list[float],  # 10 gaps
            'incomplete_seeds': list[tuple[str, int]]  # (arch, seed) pairs
        }
    """
    ...

def compute_statistics(bn_gaps: list[float], ln_gaps: list[float]) -> dict:
    """
    Returns:
        {
            'mean_bn': float,
            'mean_ln': float,
            'gap_difference': float,  # BN - LN
            'std_error': float,
            't_statistic': float,
            'p_value': float,
            'cohens_d': float
        }
    """
    ...

def check_success(stats: dict) -> bool:
    """Success: gap_diff >= 5.0 AND p < 0.05 AND cohens_d >= 0.8"""
    ...

def plot_gap_comparison(
    bn_gaps: list[float],
    ln_gaps: list[float],
    output_path: str = "results/h-e1/gap_comparison.png"
) -> None:
    """Bar plot with error bars."""
    ...

def main():
    """Load results, run statistical test, generate report."""
    ...
```

---

## Data Flow

```
1. Data Loading (data_loader.py)
   wilds.get_dataset('waterbirds') → cache to ./data/waterbirds/
   → DataLoader yields (images, labels, group_ids)

2. Model Creation (models.py)
   get_resnet_bn() → ResNet-18 with BN
   get_resnet_ln() → ResNet-18 with BN→LN replacement

3. Training Loop (train.py)
   for seed in [0..9]:
       for architecture in [ResNet-BN, ResNet-LN]:
           set_seed(seed)
           model = create_model(architecture)
           for epoch in [0..99]:
               train_loss = train_one_epoch(...)
               metrics = evaluate(...)
               append_to_csv(metrics)

4. Statistical Analysis (evaluate.py)
   read training_metrics.csv
   → extract gaps at 90% accuracy
   → paired t-test
   → plot + report
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Data setup | Waterbirds download + DataLoader | 6 | wilds(2) + loader(2) + verify(2) |
| A-2 | Models | ResNet-BN + BN→LN replacement | 8 | bn_model(2) + ln_replace(4) + init(2) |
| A-3 | Training | 10 seeds × 2 archs × 100 epochs | 10 | seed_mgmt(2) + train_loop(3) + eval(3) + csv_log(2) |
| A-4 | Statistics | Gap extraction + t-test + plot | 7 | extract(3) + stats(2) + plot(2) |

**Distribution**: High(9-13): [A-3], Medium(4-8): [A-1, A-2, A-4]

---

## File Organization

```
h-e1/
├── data_loader.py          # Module 1
├── models.py               # Module 2
├── train.py                # Module 3 (main script)
├── evaluate.py             # Module 4
├── requirements.txt
└── results/
    └── h-e1/
        ├── training_metrics.csv
        ├── statistical_test.txt
        └── gap_comparison.png
```

---

## Error Handling

**Data Loading**:
- wilds download failure → retry with explicit error message
- Missing group metadata → raise ValueError with data path

**Training**:
- CUDA OOM → clear error message suggesting batch_size reduction
- NaN loss → early stop with seed/epoch logged

**Evaluation**:
- 90% threshold never reached → use epoch 100 gap, log warning
- Missing seeds in CSV → report incomplete seeds, continue with available

---

## Configuration

Fixed constants (no config file for PoC):

```python
# train.py
BATCH_SIZE = 64
LEARNING_RATE = 0.01
MOMENTUM = 0.9
WEIGHT_DECAY = 1e-4
EPOCHS = 100
SEEDS = list(range(10))
ACCURACY_THRESHOLD = 0.90
```

---

## Implementation Notes

**BN→LN Replacement**:
- Traverse model recursively
- For each `nn.BatchNorm2d(C)`, infer feature map size from preceding conv layer
- Replace with `nn.LayerNorm([C, H, W], elementwise_affine=True)`
- Feature map sizes: conv2_x=56×56, conv3_x=28×28, conv4_x=14×14, conv5_x=7×7

**Seed Management**:
- Set torch, numpy, random seeds
- Enable `torch.backends.cudnn.deterministic = True`
- Disable cudnn.benchmark for reproducibility

**Metric Logging**:
- Append to CSV after each epoch (not buffered)
- CSV format: seed,architecture,epoch,train_loss,avg_acc,worst_group_acc,group_0_acc,group_1_acc,group_2_acc,group_3_acc,worst_group_gap

**Statistical Test**:
- scipy.stats.ttest_rel (paired t-test)
- Cohen's d = (mean_diff) / sqrt((std1^2 + std2^2) / 2)

---

## Dependencies

```
torch>=2.0.0
torchvision>=0.15.0
wilds>=2.0.0
numpy>=1.24.0
scipy>=1.10.0
pandas>=2.0.0
matplotlib>=3.7.0
tqdm>=4.65.0
```

---

## Success Validation

**Functional**:
- [ ] All 20 runs complete (2 archs × 10 seeds)
- [ ] CSV has 2000 rows (2 × 10 × 100)
- [ ] No NaN values in metrics

**Scientific**:
- [ ] ≥8/10 seeds reach 90% avg accuracy per architecture
- [ ] Gap difference ≥ 5pp
- [ ] p < 0.05
- [ ] Cohen's d ≥ 0.8

---

**Architecture Status**: COMPLETED  
**Estimated LoC**: ~350 lines  
**Ready for Phase 4**: YES
