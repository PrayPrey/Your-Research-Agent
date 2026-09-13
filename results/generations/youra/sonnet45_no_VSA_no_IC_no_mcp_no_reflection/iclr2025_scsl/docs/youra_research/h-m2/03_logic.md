# Logic Specification: h-m2

**Date:** 2026-08-29  
**Hypothesis:** CNNs show larger temporal gaps than Vision Transformers (Δ_ResNet > Δ_ViT by ≥2 epochs)  
**Phase:** 3 (Logic Design)  
**Specification Level:** EXISTENCE (PoC)

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis  
**Status:** API signatures verified from h-e1 actual code  
**Analyzed Path:** `/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP_no_Reflection/sonnet45/TEST_scsl/docs/youra_research/h-e1/code/`  
**Relevant Symbols:**
- `AblationTrainer.train_variant()` - Convergence detection logic (accuracy-based)
- `get_baseline_model()` - Model factory (ResNet-18/50)
- `run_single_experiment()` - Multi-variant training orchestration

---

## External Dependencies (Base Hypothesis h-e1)

### API Signatures (From Actual Code)

Convergence detection and training logic reused from h-e1:

```python
# From: h-e1/code/model_v2.py (ACTUAL CODE)
class AblationTrainer:
    def __init__(
        self,
        model: nn.Module,
        dataset_name: str,
        lr: float,
        weight_decay: float,
        device: str = 'cuda',
        target_accuracy: float = 0.90
    ):
        """Initialize trainer with accuracy-based convergence."""
        ...

    def train_variant(
        self,
        variant: Literal['spurious', 'core', 'baseline'],
        dataloader,
        max_epochs: int
    ) -> int | None:
        """Train until target accuracy. Returns: convergence epoch or None."""
        ...

    def compute_accuracy(
        self,
        dataloader,
        variant: Literal['spurious', 'core', 'baseline']
    ) -> float:
        """Compute accuracy with variant-specific masking."""
        ...

# From: h-e1/code/train.py (ACTUAL CODE)
def run_single_experiment(config: TrainConfig) -> dict:
    """
    Run ablation training for one seed.
    Returns: {
        'dataset': str,
        'seed': int,
        'E_spurious': int | None,
        'E_core': int | None,
        'E_baseline': int | None,
        'delta': float | None
    }
    """
    ...
```

**Verified from:** h-e1 actual implementation (accuracy-based convergence at 90%)

---

## Task A-1: Multi-Architecture Training Loop [Complexity: 2, Budget: 5]

**Applied:** h-e1 training orchestration pattern

### API Signatures

```python
from dataclasses import dataclass
import torch
import torch.nn as nn
from typing import Literal

@dataclass
class ArchitectureConfig:
    """Configuration for one architecture experiment."""
    arch_name: Literal['resnet50', 'vit_b16']
    lr: float
    weight_decay: float
    batch_size: int
    max_epochs: int = 50
    seed: int = 0

def run_architecture_experiment(
    config: ArchitectureConfig,
    train_loader,
    device: str = 'cuda'
) -> dict:
    """
    Run ablation training for one architecture on one seed.
    
    Args:
        config: Architecture-specific hyperparameters
        train_loader: DataLoader with (images, labels)
        device: 'cuda' or 'cpu'
    
    Returns:
        {
            'arch_name': str,
            'seed': int,
            'E_spurious': int | None,
            'E_core': int | None,
            'delta': float | None
        }
    
    Tensor shapes:
        images: [B, 3, 224, 224]
        labels: [B]
        logits: [B, 2]
    """
    # Create spurious/core models
    model_spurious = create_model(config.arch_name, num_classes=2)
    model_core = create_model(config.arch_name, num_classes=2)
    
    # Train spurious-only variant
    trainer_spurious = AblationTrainer(
        model_spurious, 'Waterbirds', config.lr, config.weight_decay, device
    )
    E_spurious = trainer_spurious.train_variant('spurious', train_loader, config.max_epochs)
    
    # Train core-only variant
    trainer_core = AblationTrainer(
        model_core, 'Waterbirds', config.lr, config.weight_decay, device
    )
    E_core = trainer_core.train_variant('core', train_loader, config.max_epochs)
    
    # Compute temporal gap
    delta = (E_core - E_spurious) if (E_spurious and E_core) else None
    
    return {
        'arch_name': config.arch_name,
        'seed': config.seed,
        'E_spurious': E_spurious,
        'E_core': E_core,
        'delta': delta
    }
```

### Pseudo-code

```
FOR seed IN [0..9]:
    FOR arch IN ['resnet50', 'vit_b16']:
        config = ArchitectureConfig(arch, lr[arch], wd[arch], bs[arch], seed)
        results[arch][seed] = run_architecture_experiment(config, train_loader)
        RECORD: E_spurious[arch][seed], E_core[arch][seed], delta[arch][seed]
```

### Subtasks [4/5 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | Architecture factory | Model creation (ResNet-50, ViT-B/16) |
| L-1-2 | Config management | Architecture-specific hyperparameters |
| L-1-3 | Training orchestration | 2 architectures × 2 ablations × 10 seeds loop |
| L-1-4 | Result aggregation | Collect E_spurious, E_core, delta per arch/seed |

---

## Task A-2: Architecture-Specific Model Factory [Complexity: 1, Budget: 3]

**Applied:** timm library standard API

### API Signatures

```python
import timm

def create_model(arch_name: Literal['resnet50', 'vit_b16'], num_classes: int = 2) -> nn.Module:
    """
    Create architecture model from scratch (no pretraining).
    
    Args:
        arch_name: 'resnet50' or 'vit_b16'
        num_classes: Output classes (2 for binary)
    
    Returns:
        Model with binary classification head
    
    Tensor shapes:
        ResNet-50: [B, 3, 224, 224] → [B, 2]
        ViT-B/16:  [B, 3, 224, 224] → [B, 2]
    """
    if arch_name == 'resnet50':
        model = timm.create_model('resnet50', pretrained=False, num_classes=num_classes)
    elif arch_name == 'vit_b16':
        model = timm.create_model('vit_base_patch16_224', pretrained=False, num_classes=num_classes)
    else:
        raise ValueError(f"Unknown architecture: {arch_name}")
    
    return model
```

### Subtasks [2/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | ResNet-50 factory | timm.create_model('resnet50') |
| L-2-2 | ViT-B/16 factory | timm.create_model('vit_base_patch16_224') |

---

## Task A-3: Convergence Detection (Reused from h-e1) [Complexity: 0, Budget: 0]

**Applied:** h-e1 accuracy-based convergence criterion (no modification)

### API Signatures

```python
# REUSED FROM h-e1 (no changes)
# AblationTrainer.train_variant() already implements:
#   - Convergence criterion: accuracy >= 0.90 (90%)
#   - Returns: convergence epoch or None
#   - Works for any architecture (architecture-agnostic)
```

**Note:** No new logic required. h-e1's `AblationTrainer` works for both ResNet and ViT.

### Subtasks [0/0 used]

Fully reused from h-e1.

---

## Task A-4: Temporal Gap Computation [Complexity: 1, Budget: 2]

**Applied:** Standard subtraction with null handling

### API Signatures

```python
def compute_temporal_gap(E_spurious: int | None, E_core: int | None) -> float | None:
    """
    Compute temporal gap Δ = E_core - E_spurious.
    
    Args:
        E_spurious: Spurious-only convergence epoch (or None)
        E_core: Core-only convergence epoch (or None)
    
    Returns:
        Temporal gap in epochs, or None if either model didn't converge
    """
    if E_spurious is None or E_core is None:
        return None
    return E_core - E_spurious

def aggregate_gaps_per_architecture(results: list[dict]) -> dict:
    """
    Aggregate temporal gaps per architecture across seeds.
    
    Args:
        results: List of experiment results from run_architecture_experiment()
    
    Returns:
        {
            'resnet50': [delta_seed0, delta_seed1, ..., delta_seed9],
            'vit_b16': [delta_seed0, delta_seed1, ..., delta_seed9]
        }
    """
    gaps = {'resnet50': [], 'vit_b16': []}
    for result in results:
        if result['delta'] is not None:
            gaps[result['arch_name']].append(result['delta'])
    return gaps
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | Gap computation | Δ = E_core - E_spurious |
| L-4-2 | Per-architecture aggregation | Group gaps by architecture |

---

## Task A-5: Statistical Test (Independent t-test) [Complexity: 1, Budget: 2]

**Applied:** scipy.stats.ttest_ind (standard two-sample test)

### API Signatures

```python
from scipy.stats import ttest_ind

def test_architecture_difference(
    gaps_resnet: list[float],
    gaps_vit: list[float],
    alpha: float = 0.05
) -> dict:
    """
    Test if ResNet gaps are larger than ViT gaps.
    
    Args:
        gaps_resnet: Temporal gaps for ResNet-50 across seeds
        gaps_vit: Temporal gaps for ViT-B/16 across seeds
        alpha: Significance level (default 0.05)
    
    Returns:
        {
            'mean_delta_resnet': float,
            'mean_delta_vit': float,
            'diff': float,  # mean_delta_resnet - mean_delta_vit
            'p_value': float,
            'significant': bool,  # p < alpha
            'gate_passed': bool   # diff >= 2 AND significant
        }
    """
    import numpy as np
    
    mean_resnet = np.mean(gaps_resnet)
    mean_vit = np.mean(gaps_vit)
    diff = mean_resnet - mean_vit
    
    # One-tailed test: H1: ResNet > ViT
    t_stat, p_value_two_tailed = ttest_ind(gaps_resnet, gaps_vit)
    p_value = p_value_two_tailed / 2 if t_stat > 0 else 1 - p_value_two_tailed / 2
    
    significant = p_value < alpha
    gate_passed = (diff >= 2.0) and significant
    
    return {
        'mean_delta_resnet': mean_resnet,
        'mean_delta_vit': mean_vit,
        'diff': diff,
        'p_value': p_value,
        'significant': significant,
        'gate_passed': gate_passed
    }
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | t-test computation | scipy.stats.ttest_ind() |
| L-5-2 | Gate evaluation | diff >= 2 AND p < 0.05 |

---

## Task A-6: Waterbirds Dataset Loading [Complexity: 1, Budget: 2]

**Applied:** WILDS package standard API

### API Signatures

```python
from wilds import get_dataset
from torch.utils.data import DataLoader

def get_waterbirds_dataloader(batch_size: int = 256, split: str = 'train') -> DataLoader:
    """
    Load Waterbirds dataset from WILDS.
    
    Args:
        batch_size: Batch size
        split: 'train', 'val', or 'test'
    
    Returns:
        DataLoader yielding (images, labels)
        images: [B, 3, 224, 224]
        labels: [B] (0=landbird, 1=waterbird)
    """
    dataset = get_dataset(dataset='waterbirds', download=True)
    subset = dataset.get_subset(split)
    
    loader = DataLoader(
        subset,
        batch_size=batch_size,
        shuffle=(split == 'train'),
        num_workers=4,
        pin_memory=True
    )
    return loader
```

### Subtasks [1/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-6-1 | WILDS loading | get_dataset('waterbirds') |

---

## Task A-7: Architecture-Specific Hyperparameters [Complexity: 1, Budget: 2]

**Applied:** Standard hyperparameters from research

### API Signatures

```python
# Architecture-specific training configs
ARCH_CONFIGS = {
    'resnet50': {
        'lr': 0.001,
        'weight_decay': 1e-4,
        'batch_size': 256
    },
    'vit_b16': {
        'lr': 0.0003,  # ViT typically needs lower LR
        'weight_decay': 0.05,  # ViT typically needs higher WD
        'batch_size': 512  # ViT benefits from larger batches
    }
}

def get_arch_config(arch_name: str) -> dict:
    """Get hyperparameters for architecture."""
    return ARCH_CONFIGS[arch_name]
```

### Subtasks [1/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-7-1 | Config lookup | Dictionary-based hyperparameter selection |

---

## Summary

### Budget Allocation (Total: 16/16 used)

| Task | Complexity | Budget | Used |
|------|-----------|--------|------|
| A-1: Multi-arch training loop | 2 | 5 | 4 |
| A-2: Model factory | 1 | 3 | 2 |
| A-3: Convergence (h-e1) | 0 | 0 | 0 |
| A-4: Temporal gap | 1 | 2 | 2 |
| A-5: Statistical test | 1 | 2 | 2 |
| A-6: Dataset loading | 1 | 2 | 1 |
| A-7: Hyperparameter config | 1 | 2 | 1 |
| **Total** | **8** | **16** | **12** |

### Key Design Decisions

1. **Convergence criterion:** Reuse h-e1's accuracy-based method (90% threshold) - already architecture-agnostic
2. **Model factory:** timm library for both ResNet-50 and ViT-B/16 (standardized implementations)
3. **Statistical test:** Independent t-test (scipy.stats.ttest_ind) for cross-architecture comparison
4. **Training protocol:** Architecture-specific hyperparameters (LR, batch size, weight decay)
5. **Dataset:** Waterbirds from WILDS (standard spurious correlation benchmark)

### Control Flow

```
SETUP:
    - Load Waterbirds dataset (train split)
    - Initialize 2 architectures × 10 seeds = 20 experiment runs

MAIN LOOP:
    FOR seed IN [0..9]:
        FOR arch IN ['resnet50', 'vit_b16']:
            config = get_arch_config(arch) + {seed: seed}
            
            # Spurious-only training
            model_spurious = create_model(arch)
            E_spurious = AblationTrainer(model_spurious).train_variant('spurious', ...)
            
            # Core-only training
            model_core = create_model(arch)
            E_core = AblationTrainer(model_core).train_variant('core', ...)
            
            # Record gap
            delta = E_core - E_spurious
            results[arch][seed] = delta

STATISTICAL ANALYSIS:
    gaps_resnet = [results['resnet50'][s] for s in [0..9]]
    gaps_vit = [results['vit_b16'][s] for s in [0..9]]
    test_result = test_architecture_difference(gaps_resnet, gaps_vit)
    
    GATE_CONDITION: test_result['gate_passed']
        - diff >= 2 epochs AND p < 0.05
```

---

*Logic specification complete. Phase 4 Coder can implement from these signatures.*
