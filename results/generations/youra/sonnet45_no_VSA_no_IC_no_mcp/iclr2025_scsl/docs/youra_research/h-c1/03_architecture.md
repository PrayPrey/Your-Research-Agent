# Architecture Document: h-c1

**Generated**: 2026-08-25  
**Hypothesis**: Architecture rankings by worst-group gap generalize across datasets (Waterbirds → CelebA)  
**Gate**: SHOULD_WORK  
**Prerequisites**: h-e1 (VALIDATED)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis  
**Status**: Reusing validated h-e1 code  
**Analyzed Path**: `/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet45/TEST_scsl/h-e1/`  
**Findings**: h-e1 provides Waterbirds loader, ResNet-BN/LN models, group evaluation metrics, training loop

---

## Module Structure

### Module 1: CelebA Data Loader (`celeba_loader.py`)

**Dependencies**: torch, torchvision, PIL

```python
from torch.utils.data import DataLoader
from torchvision.datasets import CelebA
from torchvision import transforms

def get_celeba_loader(
    split: str,
    batch_size: int = 64,
    data_dir: str = "./data/celeba",
    num_workers: int = 4
) -> DataLoader:
    """
    Args:
        split: 'train', 'valid', 'test'
        batch_size: batch size
        data_dir: download/cache directory
        num_workers: parallel loading workers
    
    Returns:
        DataLoader yielding (images, labels, group_ids)
        images: [B, 3, 224, 224] ImageNet-normalized
        labels: [B] binary (0=not-blond, 1=blond)
        group_ids: [B] integers 0-3
            0: blond-female, 1: blond-male, 2: not-blond-female, 3: not-blond-male
    """
    ...

def _construct_group_labels(attr_male: int, attr_blond: int) -> int:
    """
    Map (Male, Blond_Hair) attributes to group ID.
    
    Returns:
        0: blond-female (Male=0, Blond=1)
        1: blond-male (Male=1, Blond=1)
        2: not-blond-female (Male=0, Blond=0)
        3: not-blond-male (Male=1, Blond=0)
    """
    ...
```

---

### Module 2: Training to Threshold (`train_to_threshold.py`)

**Dependencies**: h-e1/train, h-e1/models

```python
import sys
sys.path.append('../h-e1')
from train import set_seed, evaluate_groups
from models import get_resnet18_bn, get_resnet18_ln
import torch.nn as nn
from torch.optim import SGD

def train_until_threshold(
    architecture: str,
    dataloader_train: DataLoader,
    dataloader_test: DataLoader,
    target_avg_acc: float = 90.0,
    max_epochs: int = 100,
    seed: int = 0,
    device: str = 'cuda'
) -> dict:
    """
    Train model until avg_accuracy >= target, then return metrics.
    
    Args:
        architecture: 'ResNet-BN' or 'ResNet-LN'
        target_avg_acc: threshold for early stopping
        max_epochs: training budget
        seed: random seed
    
    Returns:
        {
            'architecture': str,
            'seed': int,
            'dataset': str,
            'threshold_epoch': int,
            'worst_group_gap': float,
            'avg_accuracy': float,
            'group_accuracies': list[float]
        }
    """
    ...
```

---

### Module 3: Ranking Computation (`compute_rankings.py`)

**Dependencies**: numpy, pandas

```python
import numpy as np
import pandas as pd

def aggregate_gaps(results: list[dict]) -> dict:
    """
    Aggregate gaps across seeds per architecture.
    
    Args:
        results: list of dicts from train_until_threshold()
    
    Returns:
        {
            'ResNet-BN': {'mean': float, 'std': float, 'gaps': list[float]},
            'ResNet-LN': {...}
        }
    """
    ...

def compute_ranking(aggregated_gaps: dict) -> dict:
    """
    Rank architectures by mean gap (lower = better = lower rank number).
    
    Args:
        aggregated_gaps: from aggregate_gaps()
    
    Returns:
        {
            'ResNet-BN': 2,
            'ResNet-LN': 1
        }
        Ties broken alphabetically.
    """
    ...
```

---

### Module 4: Correlation Analysis (`correlation_stats.py`)

**Dependencies**: scipy, numpy

```python
from scipy.stats import spearmanr, kendalltau
import numpy as np

def compute_correlation(
    waterbirds_ranks: dict,
    celeba_ranks: dict
) -> dict:
    """
    Compute rank correlation between two datasets.
    
    Args:
        waterbirds_ranks: {'ResNet-BN': 2, 'ResNet-LN': 1}
        celeba_ranks: {'ResNet-BN': 2, 'ResNet-LN': 1}
    
    Returns:
        {
            'spearman_rho': float,
            'spearman_p': float,
            'kendall_tau': float,
            'kendall_p': float,
            'rank_reversals': int
        }
    """
    ...

def check_success(stats: dict) -> str:
    """
    Gate decision based on correlation metrics.
    
    Returns:
        'PASSED' if rho > 0.8 and p < 0.05
        'FAILED' if rho < 0.6 or top-2 reversal
        'UNCERTAIN' otherwise
    """
    ...
```

---

### Module 5: Orchestration (`run_experiment.py`)

**Dependencies**: All modules above

```python
import argparse
from celeba_loader import get_celeba_loader
from train_to_threshold import train_until_threshold
from compute_rankings import aggregate_gaps, compute_ranking
from correlation_stats import compute_correlation, check_success
import sys
sys.path.append('../h-e1')
from data_loader import get_waterbirds_dataloader

def run_dataset(
    dataset_name: str,
    architectures: list[str],
    seeds: list[int]
) -> dict:
    """
    Run all architectures x seeds on one dataset.
    
    Returns:
        {
            'dataset': str,
            'results': list[dict],  # from train_until_threshold()
            'aggregated_gaps': dict,
            'ranking': dict
        }
    """
    ...

def main():
    """
    1. Run Waterbirds (2 archs × 10 seeds)
    2. Run CelebA (2 archs × 10 seeds)
    3. Compute rankings per dataset
    4. Compute correlation
    5. Generate validation report
    """
    ...
```

---

## External Dependencies (h-e1)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| get_waterbirds_dataloader | `sys.path.append('../h-e1'); from data_loader import get_waterbirds_dataloader` | `/h-e1/data_loader.py` |
| get_resnet18_bn | `from models import get_resnet18_bn` | `/h-e1/models.py` |
| get_resnet18_ln | `from models import get_resnet18_ln` | `/h-e1/models.py` |
| set_seed | `from train import set_seed` | `/h-e1/train.py` |
| evaluate_groups | `from train import evaluate_groups` | `/h-e1/train.py` |

**Verified from**: h-e1 actual implementation

---

## Data Flow

```
1. Data Loading
   Waterbirds: h-e1/data_loader.get_waterbirds_dataloader()
   CelebA: celeba_loader.get_celeba_loader() → torchvision.datasets.CelebA

2. Training Loop (per dataset, per architecture, per seed)
   create_model(architecture) → from h-e1/models.py
   for epoch in [0..max_epochs]:
       train_one_epoch()
       metrics = evaluate_groups() → from h-e1/train.py
       if metrics['avg_accuracy'] >= 90.0:
           record worst_group_gap
           break

3. Aggregation
   gaps_per_arch_per_dataset = aggregate_gaps(results)
   
4. Ranking
   waterbirds_ranks = compute_ranking(waterbirds_gaps)
   celeba_ranks = compute_ranking(celeba_gaps)

5. Correlation
   stats = compute_correlation(waterbirds_ranks, celeba_ranks)
   decision = check_success(stats)
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| C-1 | CelebA loader | Dataset download + group construction | 8 | torchvision(2) + groups(3) + verify(3) |
| C-2 | Threshold training | Early-stop logic + h-e1 integration | 9 | early_stop(3) + reuse_train(2) + logging(4) |
| C-3 | Ranking module | Aggregation + ranking + ties | 7 | aggregate(2) + rank(3) + edge_cases(2) |
| C-4 | Correlation stats | Spearman + Kendall + gate logic | 7 | spearman(2) + kendall(2) + gate(3) |
| C-5 | Orchestration | Run both datasets + generate report | 10 | dataset_loop(3) + correlation(2) + report(5) |
| C-6 | Validation | E2E test + reuse check | 6 | smoke_test(3) + compare_h-e1(3) |

**Distribution**: High(9-13): [C-2, C-5], Medium(4-8): [C-1, C-3, C-4, C-6]

---

## File Organization

```
h-c1/
├── celeba_loader.py           # Module 1 (NEW)
├── train_to_threshold.py      # Module 2 (NEW, reuses h-e1)
├── compute_rankings.py         # Module 3 (NEW)
├── correlation_stats.py        # Module 4 (NEW)
├── run_experiment.py           # Module 5 (orchestration)
├── requirements.txt            # Add scipy, torchvision
└── results/
    └── h-c1/
        ├── waterbirds_results.csv    # threshold_epoch, worst_group_gap per seed
        ├── celeba_results.csv        # same structure
        ├── rankings.json             # {'waterbirds': {...}, 'celeba': {...}}
        └── correlation_stats.json    # rho, p-value, decision
```

---

## Configuration

Fixed constants (ponytail: single config dict, no separate file):

```python
# run_experiment.py
CONFIG = {
    'architectures': ['ResNet-BN', 'ResNet-LN'],
    'seeds': list(range(10)),
    'target_avg_acc': 90.0,
    'max_epochs': 100,
    'batch_size': 64,
    'lr': 0.01,
    'momentum': 0.9,
    'weight_decay': 1e-4,
    'device': 'cuda' if torch.cuda.is_available() else 'cpu'
}
```

---

## Error Handling

**CelebA Download**:
- torchvision.datasets.CelebA(download=True) failure → raise with manual URL

**Threshold Not Reached**:
- If epoch 100 and avg_acc < 90% → use epoch 100 gap, log warning

**Missing Seeds**:
- Require ≥8/10 seeds succeed per architecture
- Otherwise → UNCERTAIN gate decision

**Rank Ties**:
- Break alphabetically by architecture name
- Log tied architectures

---

## Implementation Notes

**CelebA Group Construction**:
- Male attribute (index 20 in attr list)
- Blond_Hair attribute (index 9 in attr list)
- Group ID = Male * 2 + (1 - Blond) for 0-3 mapping

**Reuse Strategy**:
- Import h-e1 modules via `sys.path.append('../h-e1')`
- Use h-e1's evaluate_groups() directly (no duplication)
- Use h-e1's set_seed() for reproducibility

**Early Stopping**:
- Check avg_accuracy after every epoch
- First epoch where avg_acc >= 90.0 → record gap, break
- Save only final metrics (no checkpoint saving for PoC)

**Ranking Ties**:
- Sort by (mean_gap, architecture_name) for determinism
- Example: gaps {'BN': 10.0, 'LN': 10.0} → ranks {'BN': 1, 'LN': 2}

---

## Dependencies

```
torch>=2.0.0
torchvision>=0.15.0
numpy>=1.24.0
scipy>=1.10.0
pandas>=2.0.0
matplotlib>=3.7.0
tqdm>=4.65.0
```

Note: Reuses h-e1's requirements.txt as base

---

## Success Validation

**Functional**:
- [ ] CelebA loader returns 19,962 test images with 4 groups
- [ ] All 40 runs complete (2 archs × 2 datasets × 10 seeds)
- [ ] ≥8/10 seeds reach 90% avg_acc per architecture per dataset
- [ ] Rankings are deterministic (same input → same ranks)

**Scientific**:
- [ ] Spearman ρ computed with valid p-value
- [ ] Gate decision matches threshold (ρ > 0.8 → PASSED)
- [ ] No rank reversals logged if ρ > 0.8

---

**Architecture Status**: READY FOR PHASE 4  
**Estimated LoC**: ~400 lines (250 new + 150 reused from h-e1)  
**Code Reuse**: 60% (Waterbirds loader, models, training utils from h-e1)
