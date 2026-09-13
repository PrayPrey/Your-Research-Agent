# Logic Design: h-e1 Curvature Subspace Alignment

**Hypothesis ID:** h-e1  
**Type:** EXISTENCE (PoC)  
**Budget:** 6 subtasks (High-complexity algorithmic design)  
**Date:** 2026-04-24  
**Designer:** Logic Agent  

---

## Codebase Analysis (Serena)

**Project Type**: Green-field  
**Status**: New implementation from scratch - designing new APIs  
**Analyzed Path**: N/A  
**Relevant Symbols**: None - foundation hypothesis with no existing code

---

## Knowledge Base Patterns Applied

Applied: PyTorch Training Loop Pattern  
Applied: Hessian Eigendecomposition Pattern  
Applied: Marchenko-Pastur Distribution Fitting Pattern  

---

## A-4: Hessian Analysis Module [Complexity: 14, Budget: 4 subtasks]

**Applied**: Hessian Eigendecomposition Pattern, Marchenko-Pastur Distribution Fitting Pattern

### API Signatures

```python
# File: hessian_analysis.py

import torch
import torch.nn as nn
from torch import Tensor
from torch.utils.data import DataLoader
import numpy as np
from typing import Tuple
from hessian_eigenthings import compute_hessian_eigenthings
from scipy.optimize import minimize

def compute_hessian_spectrum(
    model: nn.Module,
    data_loader: DataLoader,
    num_eigenthings: int = 100,
    device: str = 'cuda'
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Compute Hessian eigenvalues and eigenvectors.
    
    Returns:
        eigenvalues: (num_eigenthings,) - descending order
        eigenvectors: (P, num_eigenthings) - P = num_parameters
    """
    ...

def fit_marchenko_pastur(eigenvalues: np.ndarray) -> Tuple[float, float, float]:
    """
    Fit MP distribution to eigenvalue spectrum.
    
    Returns:
        bulk_edge: float - λ_+ = σ²(1 + √γ)²
        sigma_sq: float - noise variance estimate
        gamma: float - aspect ratio estimate
    """
    ...

def compute_minority_gradient(
    model: nn.Module,
    minority_loader: DataLoader,
    device: str = 'cuda'
) -> Tensor:
    """
    Compute average gradient on minority groups.
    
    Returns:
        g_minority: (P,) - flattened parameter gradient
    """
    ...

def compute_alignment(
    g_minority: Tensor,
    eigenvectors: np.ndarray,
    eigenvalues: np.ndarray,
    bulk_edge: float
) -> float:
    """
    Compute A(w) = ||P_S_out g_minority||² / ||g_minority||².
    
    Returns:
        alignment: float - fraction of gradient in outlier subspace
    """
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| eigenvalues | (100,) | Descending order |
| eigenvectors | (P, 100) | P = total parameters |
| g_minority | (P,) | Flattened gradient |
| outlier_eigenvectors | (P, K) | K = num outliers (λ > λ_+) |
| projection | (P,) | P_S_out g_minority |

### Pseudo-code

#### L-4-1: Hessian Computation (using library)
```
1. eigenvalues, eigenvectors = compute_hessian_eigenthings(
       model, data_loader, loss=CrossEntropyLoss,
       num_eigenthings=100, power_iter_steps=20
   )
2. return eigenvalues, eigenvectors
```

#### L-4-2: Marchenko-Pastur Fitting
```
1. bulk_eigs = eigenvalues[20:80]  # Filter obvious outliers
2. Define MP likelihood:
   - λ_min = σ²(1 - √γ)²
   - λ_max = σ²(1 + √γ)²
   - density = √((λ_max - λ)(λ - λ_min)) / (2πσ²γλ)
   - neg_log_likelihood = -Σ log(density + ε)
3. Optimize (σ², γ) via scipy.minimize:
   - Initial: σ² = 1.0, γ = 0.1
   - Bounds: σ² ∈ [0.01, 10], γ ∈ [0.01, 1]
4. bulk_edge = σ²(1 + √γ)²
5. return bulk_edge, σ², γ
```

#### L-4-3: Minority Gradient Computation
```
1. Initialize total_grad = None, count = 0
2. For batch in minority_loader:
   a. outputs = model(inputs)  # [B, 2]
   b. loss = CrossEntropyLoss(outputs, labels)
   c. loss.backward()
   d. Accumulate gradients: total_grad += [p.grad for p in parameters]
   e. count += 1
3. Average: total_grad = [g / count for g in total_grad]
4. Flatten: g_minority = cat([g.flatten() for g in total_grad])  # [P]
5. return g_minority
```

#### L-4-4: Alignment Computation
```
1. outlier_mask = (eigenvalues > bulk_edge)  # [100] -> [K] True values
2. outlier_eigenvectors = eigenvectors[:, outlier_mask]  # [P, K]
3. projection = outlier_eigenvectors @ (outlier_eigenvectors.T @ g_minority)  # [P]
4. alignment = ||projection||² / ||g_minority||²
5. return alignment
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | Hessian Spectrum | Call pytorch-hessian-eigenthings library with power iteration |
| L-4-2 | MP Fitting | Fit Marchenko-Pastur distribution via scipy optimization |
| L-4-3 | Minority Gradient | Accumulate and average gradients on minority samples |
| L-4-4 | Alignment Metric | Project gradient onto outlier subspace, compute norm ratio |

---

## A-3: Model Training Module [Complexity: 12, Budget: 2 subtasks]

**Applied**: PyTorch Training Loop Pattern

### API Signatures

```python
# File: train.py

import torch
import torch.nn as nn
import torch.optim as optim
from torch import Tensor
from torch.utils.data import DataLoader
from typing import Dict, Any, Optional

class Trainer:
    def __init__(
        self,
        model: nn.Module,
        mode: str,  # 'erm' or 'dro'
        device: str = 'cuda',
        lr: float = 0.001,
        momentum: float = 0.9,
        weight_decay: float = 1e-4
    ):
        """Initialize trainer with model and optimizer."""
        ...
    
    def train_epoch(
        self,
        train_loader: DataLoader,
        optimizer: optim.Optimizer
    ) -> float:
        """
        Train one epoch.
        
        Returns:
            avg_loss: float - average training loss
        """
        ...
    
    def validate(
        self,
        val_loader: DataLoader
    ) -> Dict[str, float]:
        """
        Validate model.
        
        Returns:
            metrics: dict with keys 'val_loss', 'val_acc', 'worst_group_acc'
        """
        ...
    
    def train(
        self,
        train_loader: DataLoader,
        val_loader: DataLoader,
        epochs: int = 100,
        patience: int = 10
    ) -> Dict[str, Any]:
        """
        Full training loop with early stopping.
        
        Returns:
            history: dict with training curves and best checkpoint
        """
        ...

class GroupDROLoss(nn.Module):
    def __init__(self, num_groups: int = 4):
        """Initialize Group-DRO loss with group weights."""
        super().__init__()
        self.num_groups = num_groups
        self.register_buffer('group_weights', torch.ones(num_groups) / num_groups)
    
    def forward(
        self,
        outputs: Tensor,  # [B, 2]
        labels: Tensor,   # [B]
        groups: Tensor    # [B]
    ) -> Tensor:
        """
        Compute worst-group weighted loss.
        
        Returns:
            loss: scalar
        """
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| outputs | [B, 2] | Class logits |
| labels | [B] | True labels |
| groups | [B] | Group indices (0-3) |
| group_weights | [4] | Per-group weights for DRO |
| group_losses | [4] | Per-group loss values |

### Pseudo-code

#### L-3-1: ERM Training Loop
```
1. For epoch in range(epochs):
   a. train_loss = 0
   b. For batch in train_loader:
      - outputs = model(inputs)  # [B, 2]
      - loss = CrossEntropyLoss(outputs, labels)
      - optimizer.zero_grad()
      - loss.backward()
      - optimizer.step()
      - train_loss += loss.item()
   c. val_metrics = validate(val_loader)
   d. If val_metrics['worst_group_acc'] improved:
      - Save checkpoint
      - patience_counter = 0
   e. Else: patience_counter += 1
   f. If patience_counter >= patience: break
2. Load best checkpoint
3. Return history
```

#### L-3-2: Group-DRO Training Loop
```
1. Initialize group_weights = [0.25, 0.25, 0.25, 0.25]
2. For epoch in range(epochs):
   a. For batch in train_loader:
      - outputs = model(inputs)  # [B, 2]
      - For g in range(4):
          * mask = (groups == g)
          * group_losses[g] = CrossEntropyLoss(outputs[mask], labels[mask])
      - loss = Σ(group_weights[g] × group_losses[g])
      - optimizer.zero_grad()
      - loss.backward()
      - optimizer.step()
      - Update group_weights based on group_losses (exponential weighting)
   b. Validate and checkpoint (same as ERM)
3. Return history
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | ERM Training | Standard training loop with CrossEntropyLoss |
| L-3-2 | Group-DRO Training | Worst-group weighted loss with dynamic group weights |

---

## Supporting Module APIs (No Budget Required)

### Data Module (data.py)

```python
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from typing import Tuple, Dict

class WaterbirdsDataset(Dataset):
    def __init__(self, root_dir: str, split: str, transform: Optional[transforms.Compose] = None):
        """Load Waterbirds dataset with group labels."""
        ...
    
    def __getitem__(self, idx: int) -> Tuple[Tensor, int, int]:
        """
        Returns:
            image: [3, 224, 224]
            label: int (0=landbird, 1=waterbird)
            group: int (0-3)
        """
        ...
    
    def __len__(self) -> int: ...

def get_dataloaders(data_dir: str, batch_size: int = 128) -> Dict[str, DataLoader]:
    """Returns train, val, test loaders."""
    ...

def get_minority_loader(data_dir: str, batch_size: int = 32) -> DataLoader:
    """Returns loader for minority groups (1, 2)."""
    ...
```

### Model Module (model.py)

```python
import torchvision.models as models

def get_resnet50(num_classes: int = 2, pretrained: bool = True) -> nn.Module:
    """Load ResNet-50 with modified final layer. Output: [B, num_classes]"""
    model = models.resnet50(pretrained=pretrained)
    model.fc = nn.Linear(2048, num_classes)
    return model
```

### Evaluation Module (evaluate.py)

```python
def compute_group_accuracies(model: nn.Module, test_loader: DataLoader) -> Dict[int, float]:
    """Compute per-group accuracies. Returns: {0: acc0, 1: acc1, 2: acc2, 3: acc3}"""
    ...

def compute_worst_group_accuracy(group_accs: Dict[int, float]) -> float:
    """Return min(group_accs.values())"""
    ...

def evaluate_alignment_comparison(erm_alignment: float, dro_alignment: float) -> Dict[str, Any]:
    """
    Returns:
        success: bool (erm_alignment > dro_alignment)
        metrics: dict with alignment values, difference, ratio
    """
    ...
```

### Visualization Module (visualize.py)

```python
import matplotlib.pyplot as plt

def plot_alignment_comparison(erm_alignment: float, dro_alignment: float, save_path: str):
    """Bar chart: A(w)_ERM vs A(w)_DRO"""
    ...

def plot_hessian_spectrum(eigenvalues: np.ndarray, bulk_edge: float, save_path: str):
    """Eigenvalue spectrum with MP bulk edge overlay"""
    ...

def plot_training_curves(history: Dict[str, list], save_path: str):
    """Loss and accuracy over epochs"""
    ...

def plot_group_accuracy_heatmap(erm_accs: Dict, dro_accs: Dict, save_path: str):
    """4 groups × 2 methods heatmap"""
    ...
```

### Configuration Module (config.py)

```python
# Hardcoded configuration for LIGHT tier
SEED = 42
DATA_DIR = './data/waterbird_complete95_forest2water2/'
BATCH_SIZE = 128
LEARNING_RATE = 0.001
MOMENTUM = 0.9
WEIGHT_DECAY = 1e-4
EPOCHS = 100
PATIENCE = 10
NUM_EIGENTHINGS = 100
NUM_CLASSES = 2
NUM_GROUPS = 4
```

---

## Main Experiment Script (run_experiment.py)

```python
from data import get_dataloaders, get_minority_loader
from model import get_resnet50
from train import Trainer
from hessian_analysis import (
    compute_hessian_spectrum,
    fit_marchenko_pastur,
    compute_minority_gradient,
    compute_alignment
)
from evaluate import compute_group_accuracies, evaluate_alignment_comparison
from visualize import plot_alignment_comparison, plot_hessian_spectrum
from config import *

def main():
    # Setup
    torch.manual_seed(SEED)
    np.random.seed(SEED)
    
    # Data
    dataloaders = get_dataloaders(DATA_DIR, BATCH_SIZE)
    minority_loader = get_minority_loader(DATA_DIR)
    
    # Train ERM
    erm_model = get_resnet50(NUM_CLASSES, pretrained=True).cuda()
    erm_trainer = Trainer(erm_model, mode='erm')
    erm_history = erm_trainer.train(dataloaders['train'], dataloaders['val'], EPOCHS, PATIENCE)
    
    # Train DRO
    dro_model = get_resnet50(NUM_CLASSES, pretrained=True).cuda()
    dro_trainer = Trainer(dro_model, mode='dro')
    dro_history = dro_trainer.train(dataloaders['train'], dataloaders['val'], EPOCHS, PATIENCE)
    
    # Hessian analysis - ERM
    erm_evals, erm_evecs = compute_hessian_spectrum(erm_model, dataloaders['train'], NUM_EIGENTHINGS)
    erm_bulk_edge, _, _ = fit_marchenko_pastur(erm_evals)
    erm_g_min = compute_minority_gradient(erm_model, minority_loader)
    erm_alignment = compute_alignment(erm_g_min, erm_evecs, erm_evals, erm_bulk_edge)
    
    # Hessian analysis - DRO
    dro_evals, dro_evecs = compute_hessian_spectrum(dro_model, dataloaders['train'], NUM_EIGENTHINGS)
    dro_bulk_edge, _, _ = fit_marchenko_pastur(dro_evals)
    dro_g_min = compute_minority_gradient(dro_model, minority_loader)
    dro_alignment = compute_alignment(dro_g_min, dro_evecs, dro_evals, dro_bulk_edge)
    
    # Evaluation
    results = evaluate_alignment_comparison(erm_alignment, dro_alignment)
    
    # Visualization
    plot_alignment_comparison(erm_alignment, dro_alignment, 'figures/fig1_alignment.png')
    plot_hessian_spectrum(erm_evals, erm_bulk_edge, 'figures/fig2_spectrum_erm.png')
    
    # Save results
    print(f"ERM Alignment: {erm_alignment:.4f}")
    print(f"DRO Alignment: {dro_alignment:.4f}")
    print(f"PoC Success: {results['success']}")
    
    return results

if __name__ == '__main__':
    main()
```

---

## Implementation Notes

### Hessian Computation
- Use `pytorch-hessian-eigenthings` library (stable implementation)
- Power iteration with 20 steps per eigenvalue
- Compute on full training set or subset (2000 samples if OOM)
- Memory: eigenvectors stored as (P, 100) where P ≈ 25M for ResNet-50

### Marchenko-Pastur Fitting
- Use middle 60% of eigenvalues (indices 20:80) to avoid outliers
- Optimize (σ², γ) via maximum likelihood
- Bulk edge λ_+ separates signal (outliers) from noise (bulk)
- Visual inspection required to validate fit quality

### Minority Gradient
- Minority groups: groups 1 (landbird-water) and 2 (waterbird-land)
- Average gradients across all minority samples
- Flatten parameter gradients to single vector (P dimensions)
- No normalization before projection (alignment metric handles ratio)

### Alignment Computation
- Outlier subspace S_out = eigenvectors with λ > λ_+
- Projection: P_S_out g = V_out (V_out^T g) where V_out is [P, K]
- Alignment = ||P_S_out g||² / ||g||² ∈ [0, 1]
- Higher alignment → gradient aligned with high-curvature directions

### Training Considerations
- Use ImageNet pretrained weights (faster convergence)
- Early stopping on worst-group accuracy (patience=10)
- Save best checkpoint (not final epoch)
- MultiStepLR schedule: milestones=[60, 80], gamma=0.1

---

*Logic design for Phase 4 Implementation | h-e1 EXISTENCE Hypothesis | 6 subtasks allocated*
