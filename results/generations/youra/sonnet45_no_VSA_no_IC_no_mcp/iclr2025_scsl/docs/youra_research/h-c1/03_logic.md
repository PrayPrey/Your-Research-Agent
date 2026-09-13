# Logic Design: h-c1

**Hypothesis**: Architectural rankings generalize across datasets (Waterbirds → CelebA)  
**Type**: CONDITION (SHOULD_WORK)  
**Complexity**: Tier 1 (Moderate - extends h-e1)  
**Generated**: 2026-08-25

---

## Codebase Analysis (Serena)

**Project Type**: green-field (extends h-e1)  
**Status**: New implementation with h-e1 reuse  
**Analyzed Path**: N/A (h-e1 has no code yet, only specs)  
**Relevant Symbols**: Will reuse h-e1 signatures from 03_logic.md

---

## Knowledge Base Patterns Applied

**Applied**: scipy.stats.spearmanr for rank correlation, pandas ranking with ties, early stopping callback pattern from PyTorch

---

## Module C1: CelebA Data Loader

### API Signatures

```python
def get_celeba_loader(
    split: str = 'train',
    batch_size: int = 64,
    data_dir: str = './data/celeba/'
) -> DataLoader:
    """
    CelebA loader with Blond-Gender spurious groups.
    Returns DataLoader yielding (images, labels, group_ids).
    """
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| images | [64, 3, 224, 224] | Center crop 178→224, ImageNet norm |
| labels | [64] | Binary (0=not-blond, 1=blond) |
| group_ids | [64] | Group IDs (0-3: blond-male, blond-female, etc.) |

### Pseudo-code

```
1. dataset = torchvision.datasets.CelebA(root=data_dir, split=split)
2. Extract attributes: Blond_Hair (label), Male (spurious)
3. Group mapping: (label, gender) → group_id
4. Preprocessing: CenterCrop(178), Resize(224), ImageNet normalize
5. Augmentation: RandomHorizontalFlip (training only)
6. Return DataLoader(dataset, batch_size=64, shuffle=(split=='train'))
```

---

## Module C2: Training to Threshold

### API Signatures

```python
def train_until_threshold(
    model: nn.Module,
    train_loader: DataLoader,
    test_loader: DataLoader,
    target_avg_acc: float = 0.90,
    max_epochs: int = 100,
    seed: int = 0,
    arch_name: str = 'ResNet-BN',
    device: str = 'cuda'
) -> dict:
    """
    Train until average accuracy >= target_avg_acc, record gap at threshold epoch.
    
    Returns:
        {
            'threshold_epoch': int,  # First epoch reaching target_avg_acc
            'threshold_gap': float,  # Worst-group gap at that epoch (percentage)
            'converged': bool  # True if threshold reached, False if max_epochs hit
        }
    """
    ...
```

### Threshold Detection Algorithm

```python
def train_until_threshold(model, train_loader, test_loader, target_avg_acc=0.90, max_epochs=100, seed=0, arch_name='ResNet-BN', device='cuda'):
    set_seed(seed)
    optimizer = SGD(model.parameters(), lr=0.01, momentum=0.9, weight_decay=1e-4)
    criterion = nn.CrossEntropyLoss()
    
    for epoch in range(max_epochs):
        # Training phase
        train_loss = train_one_epoch(model, train_loader, optimizer, criterion, device)
        
        # Evaluation phase
        metrics = evaluate_groups(model, test_loader, device)
        avg_acc = metrics['avg_accuracy'] / 100.0  # Convert to [0, 1]
        worst_gap = metrics['worst_group_gap']
        
        # Threshold check
        if avg_acc >= target_avg_acc:
            return {
                'threshold_epoch': epoch,
                'threshold_gap': worst_gap,
                'converged': True
            }
    
    # Fallback: max_epochs reached without convergence
    return {
        'threshold_epoch': max_epochs - 1,
        'threshold_gap': worst_gap,
        'converged': False
    }
```

**Note**: Reuse `train_one_epoch()` and `evaluate_groups()` from h-e1 Module 3.

---

## Module C3: Ranking Computation

### API Signatures

```python
def compute_rankings(
    gaps_dict: dict[str, list[float]]
) -> dict[str, int]:
    """
    Rank architectures by mean worst-group gap (lower gap = better = rank 1).
    
    Args:
        gaps_dict: {architecture_name: [gap_seed0, gap_seed1, ..., gap_seed9]}
    
    Returns:
        {architecture_name: rank}
        e.g., {'ResNet-BN': 2, 'ResNet-LN': 1}
    
    Ties broken alphabetically (deterministic).
    """
    ...

def extract_rank_vector(
    rankings: dict[str, int],
    architecture_order: list[str]
) -> list[int]:
    """
    Convert rankings dict to ordered rank vector.
    
    Args:
        rankings: {arch: rank}
        architecture_order: ['ResNet-BN', 'ResNet-LN']
    
    Returns:
        [rank_bn, rank_ln]
    """
    ...
```

### Ranking Algorithm

```python
def compute_rankings(gaps_dict):
    import pandas as pd
    
    # Compute mean gaps
    mean_gaps = {arch: np.mean(gaps) for arch, gaps in gaps_dict.items()}
    
    # Convert to Series and rank (lower gap = rank 1)
    series = pd.Series(mean_gaps).sort_values()
    
    # Assign ranks (1-based)
    rankings = {}
    for rank, arch in enumerate(series.index, start=1):
        rankings[arch] = rank
    
    return rankings
```

**Tie-breaking**: pandas `.sort_values()` is stable, uses index order (alphabetical) for ties.

---

## Module C4: Correlation Analysis

### API Signatures

```python
def compute_correlation(
    waterbirds_ranks: list[int],
    celeba_ranks: list[int]
) -> dict:
    """
    Compute Spearman rank correlation and Kendall's tau.
    
    Args:
        waterbirds_ranks: [2, 1] (example: BN=rank2, LN=rank1)
        celeba_ranks: [2, 1]
    
    Returns:
        {
            'spearman_rho': float,  # Primary metric
            'spearman_p': float,
            'kendall_tau': float,  # Secondary metric
            'kendall_p': float,
            'rank_reversals': int  # Count of reversed positions
        }
    """
    ...

def check_gate_decision(
    spearman_rho: float,
    spearman_p: float
) -> str:
    """
    Returns: 'PASSED', 'FAILED', or 'UNCERTAIN'
    
    PASSED: rho > 0.8 and p < 0.05
    FAILED: rho < 0.6
    UNCERTAIN: 0.6 <= rho <= 0.8
    """
    ...
```

### Correlation Computation

```python
def compute_correlation(waterbirds_ranks, celeba_ranks):
    from scipy.stats import spearmanr, kendalltau
    
    # Spearman rank correlation
    spearman_rho, spearman_p = spearmanr(waterbirds_ranks, celeba_ranks)
    
    # Kendall's tau (alternative, more robust to ties)
    kendall_tau, kendall_p = kendalltau(waterbirds_ranks, celeba_ranks)
    
    # Rank reversal detection
    reversals = 0
    for i in range(len(waterbirds_ranks)):
        for j in range(i + 1, len(waterbirds_ranks)):
            # Check if rank order flipped
            wb_order = waterbirds_ranks[i] < waterbirds_ranks[j]
            ca_order = celeba_ranks[i] < celeba_ranks[j]
            if wb_order != ca_order:
                reversals += 1
    
    return {
        'spearman_rho': spearman_rho,
        'spearman_p': spearman_p,
        'kendall_tau': kendall_tau,
        'kendall_p': kendall_p,
        'rank_reversals': reversals
    }
```

### Gate Decision Logic

```python
def check_gate_decision(spearman_rho, spearman_p):
    if spearman_rho > 0.8 and spearman_p < 0.05:
        return 'PASSED'
    elif spearman_rho < 0.6:
        return 'FAILED'
    else:
        return 'UNCERTAIN'
```

---

## Module C5: Validation Orchestration

### API Signatures

```python
def run_full_experiment(
    datasets: list[str] = ['waterbirds', 'celeba'],
    architectures: list[str] = ['ResNet-BN', 'ResNet-LN'],
    seeds: list[int] = list(range(10)),
    output_dir: str = './results/h-c1/'
) -> None:
    """
    Orchestrate full cross-dataset ranking experiment.
    
    Steps:
        1. Train each (dataset, architecture, seed) to 90% avg_acc
        2. Collect threshold gaps
        3. Compute rankings per dataset
        4. Compute correlation between datasets
        5. Generate validation report (04_validation.md)
    """
    ...
```

### Orchestration Pseudo-code

```
1. For each dataset in ['waterbirds', 'celeba']:
    2. For each architecture in ['ResNet-BN', 'ResNet-LN']:
        3. gaps = []
        4. For each seed in range(10):
            5. model = get_model(architecture)
            6. result = train_until_threshold(model, dataset, seed)
            7. gaps.append(result['threshold_gap'])
        8. Store: dataset_gaps[dataset][architecture] = gaps

9. For each dataset:
    10. rankings[dataset] = compute_rankings(dataset_gaps[dataset])

11. waterbirds_ranks = extract_rank_vector(rankings['waterbirds'], architectures)
12. celeba_ranks = extract_rank_vector(rankings['celeba'], architectures)

13. correlation = compute_correlation(waterbirds_ranks, celeba_ranks)
14. gate = check_gate_decision(correlation['spearman_rho'], correlation['spearman_p'])

15. Generate validation report with:
    - Mean gaps per (dataset, architecture)
    - Rankings table
    - Correlation metrics
    - Gate decision
```

---

## Reused h-e1 APIs

The following functions from h-e1 Module 3 are reused without modification:

```python
# From h-e1/03_logic.md Module 3

def set_seed(seed: int):
    """Set all random seeds."""
    ...

def train_one_epoch(
    model: nn.Module,
    train_loader: DataLoader,
    optimizer: SGD,
    criterion: nn.Module,
    device: str
) -> float:
    """Returns: avg training loss."""
    ...

def evaluate_groups(
    model: nn.Module,
    dataloader: DataLoader,
    device: str
) -> dict:
    """
    Returns:
        {
            'avg_accuracy': float,  # Percentage
            'group_accuracies': [float] × 4,
            'worst_group_acc': float,
            'worst_group_gap': float
        }
    """
    ...
```

**Note**: These functions are identical for both datasets (Waterbirds and CelebA) since both have 4 spurious groups.

---

## Reused h-e1 Models

```python
# From h-e1/03_logic.md Module 2

def get_resnet18_bn(num_classes: int = 2) -> nn.Module:
    """ResNet-18 with BatchNorm."""
    ...

def get_resnet18_ln(num_classes: int = 2) -> nn.Module:
    """ResNet-18 with LayerNorm."""
    ...
```

Both architectures work for binary classification on Waterbirds and CelebA.

---

## Edge Cases and Validation

### Module C1 (CelebA Data)
- **Download failure**: Use `torchvision.datasets.CelebA(download=True)` with retry logic
- **Attribute missing**: Verify `Blond_Hair` and `Male` columns exist in `list_attr_celeba.txt`
- **Test split size**: Assert `len(test_set) == 19962` to catch corrupted downloads

### Module C2 (Training to Threshold)
- **Never converges**: If `converged=False` after 100 epochs, log warning and use final gap
- **Require ≥8/10 seeds converge**: Flag experiment if <8 seeds reach 90% threshold
- **NaN loss**: Same handling as h-e1 (stop and log)

### Module C3 (Ranking)
- **Tied gaps**: pandas `.sort_values()` uses alphabetical order (deterministic)
- **Single architecture**: If only 1 arch, rank=1 (correlation undefined)
- **Empty gaps list**: Raise ValueError if gaps_dict is empty

### Module C4 (Correlation)
- **Perfect correlation**: ρ=1.0 when ranks identical (expected if hypothesis holds)
- **Anti-correlation**: ρ=-1.0 indicates reversed rankings (hypothesis fails)
- **Small sample**: p-value may be non-significant for N=2 architectures (flag as UNCERTAIN)

### Module C5 (Orchestration)
- **Missing dataset results**: If Waterbirds fails, reuse h-e1 results if available
- **Partial failures**: Continue experiment if some seeds fail, require ≥8/10 succeed

---

## Output Files

### dataset_gaps.csv
```
dataset,architecture,seed,threshold_epoch,threshold_gap,converged
waterbirds,ResNet-BN,0,28,18.5,True
waterbirds,ResNet-BN,1,31,19.2,True
...
celeba,ResNet-LN,9,22,8.7,True
```

### rankings.csv
```
dataset,architecture,mean_gap,std_gap,rank
waterbirds,ResNet-LN,9.2,1.8,1
waterbirds,ResNet-BN,18.9,2.3,2
celeba,ResNet-LN,8.5,1.5,1
celeba,ResNet-BN,17.1,2.9,2
```

### correlation_results.txt
```
Hypothesis h-c1: Cross-Dataset Ranking Generalization

Waterbirds Rankings:
  ResNet-BN: rank 2 (18.9 ± 2.3 pp gap)
  ResNet-LN: rank 1 (9.2 ± 1.8 pp gap)

CelebA Rankings:
  ResNet-BN: rank 2 (17.1 ± 2.9 pp gap)
  ResNet-LN: rank 1 (8.5 ± 1.5 pp gap)

Rank Vectors:
  Waterbirds: [2, 1]
  CelebA:     [2, 1]

Correlation Metrics:
  Spearman ρ: 1.00
  p-value: 0.000
  Kendall's τ: 1.00
  Rank reversals: 0

Gate Decision: PASSED (ρ > 0.8, p < 0.05)
```

---

## Implementation Notes

### Efficiency Optimization

Since h-c1 trains same architectures on 2 datasets:
1. **Reuse Waterbirds results from h-e1** if available (save 30 GPU-hours)
2. **Parallelize seeds**: Train 10 seeds in parallel if multi-GPU available
3. **Early stopping**: Stop immediately after reaching 90% threshold (no over-training)

### Reproducibility

```python
# Critical: Set seed before model creation AND data loading
set_seed(seed)
model = get_resnet18_bn()
train_loader = get_celeba_loader('train')
```

### Statistical Power

**Limitation**: With only 2 architectures, correlation test has low power (N=2 data points).
- **Mitigation**: Defer full power analysis to Phase 5
- **Acceptance**: PoC only tests direction (ρ > 0.8 vs ρ < 0.6), not precise effect size

---

## Dependencies

```python
import torch
import torch.nn as nn
from torch.optim import SGD
from torch.utils.data import DataLoader
import torchvision.datasets
import numpy as np
import pandas as pd
from scipy.stats import spearmanr, kendalltau
```

---

**Logic Design Status**: COMPLETED  
**Total Lines**: ~480  
**Ready for Phase 4 (Coding)**: YES
