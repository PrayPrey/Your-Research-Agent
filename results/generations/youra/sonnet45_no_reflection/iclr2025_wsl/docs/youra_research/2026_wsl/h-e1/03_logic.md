---
hypothesis_id: h-e1
hypothesis_type: EXISTENCE
document_type: logic
created_at: 2026-05-12
author: Phase 3 Logic Agent
version: 1.0
---

# Logic Design: H-E1 Quotient Space Existence

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: New implementation from scratch
**Analyzed Path**: N/A
**Relevant Symbols**: None - designing new APIs

---

## A-1: Dataset Infrastructure [Complexity: 14, Budget: 3 subtasks]

**Applied**: Standard PyTorch Dataset pattern

### API Signatures

```python
from typing import Dict, List, Tuple, Optional
import torch
from torch.utils.data import Dataset, DataLoader

class ModelZooDataset(Dataset):
    """Dataset for pretrained model weights from HuggingFace."""
    
    def __init__(self, model_ids: List[str], cache_dir: str, split: str):
        """Initialize dataset. model_ids: list of HF model names."""
        ...
    
    def __len__(self) -> int:
        """Return number of models."""
        ...
    
    def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]:
        """Return: {'weights': [N, D], 'arch_label': int, 'model_id': str}"""
        ...
    
    def _load_and_preprocess_weights(self, model_id: str) -> torch.Tensor:
        """Load model, flatten weights, normalize. Returns: [N, D]"""
        ...

def download_modelzoo_14k(
    cache_dir: str,
    architectures: List[str],
    size_range: Tuple[int, int]
) -> Dict[str, List[str]]:
    """Download models from HuggingFace. Returns: {'train': [...], 'val': [...], 'test': [...]}"""
    ...

def create_dataloaders(
    train_ids: List[str],
    val_ids: List[str],
    test_ids: List[str],
    batch_size: int,
    cache_dir: str
) -> Tuple[DataLoader, DataLoader, DataLoader]:
    """Create train/val/test dataloaders."""
    ...
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | HuggingFace download | Download and filter 14K models with retry logic |
| L-1-2 | Weight preprocessing | Flatten, normalize, pad/truncate weight vectors |
| L-1-3 | Dataset splitting | 70/15/15 split with architecture stratification |

---

## A-2: Baseline Model [Complexity: 11, Budget: 2 subtasks]

**Applied**: Deep Sets (Zaheer et al. 2017) encoder-decoder

### API Signatures

```python
import torch.nn as nn
from torch import Tensor

class DeepSetsEncoder(nn.Module):
    """Standard Deep Sets encoder without equivariance."""
    
    def __init__(self, weight_dim: int, hidden_dim: int = 128, output_dim: int = 32):
        """Initialize encoder. weight_dim: flattened weight size."""
        ...
    
    def forward(self, weights: Tensor) -> Tensor:
        """Forward pass. weights: [B, N, D] -> [B, K]"""
        ...
    
    def reconstruct(self, z: Tensor) -> Tensor:
        """Reconstruct weights from quotient space. z: [B, K] -> [B, D]"""
        ...

class PerElementEncoder(nn.Module):
    """Phi function: per-element MLP."""
    
    def __init__(self, input_dim: int, hidden_dim: int):
        """MLP: input_dim -> 512 -> 256 -> hidden_dim."""
        ...
    
    def forward(self, x: Tensor) -> Tensor:
        """x: [B, N, D] -> [B, N, H]"""
        ...

class PostAggregationDecoder(nn.Module):
    """Rho function: post-aggregation MLP."""
    
    def __init__(self, hidden_dim: int, output_dim: int):
        """MLP: hidden_dim -> 256 -> output_dim."""
        ...
    
    def forward(self, x: Tensor) -> Tensor:
        """x: [B, H] -> [B, K]"""
        ...
```

### Pseudo-code

```
1. phi = PerElementEncoder(weights)      # [B, N, D] -> [B, N, H]
2. aggregated = phi.sum(dim=1)           # [B, H] (permutation-invariant)
3. z = rho(aggregated)                   # [B, K] (quotient space)
4. weights_recon = reconstruct(z)        # [B, D] (for loss)
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | Encoder architecture | Implement phi/rho with sum pooling |
| L-2-2 | Reconstruction decoder | MLP mapping K-dim back to weight space |

---

## A-3: Proposed Model [Complexity: 16, Budget: 3 subtasks]

**Applied**: Deep Sets + architecture embeddings + equivariance loss

### API Signatures

```python
import torch.nn as nn
from torch import Tensor

class SlotEquivariantEncoder(nn.Module):
    """Deep Sets encoder with equivariance constraints."""
    
    def __init__(
        self,
        weight_dim: int,
        K: int = 32,
        hidden_dim: int = 256,
        num_arch_classes: int = 3,
        arch_embed_dim: int = 64
    ):
        """Initialize encoder. K: quotient space dimension."""
        ...
    
    def forward(self, weights: Tensor, arch_labels: Tensor) -> Tensor:
        """Forward pass. weights: [B, N, D], arch_labels: [B] -> z: [B, K]"""
        ...
    
    def reconstruct_weights(self, z: Tensor) -> Tensor:
        """Reconstruct from quotient space. z: [B, K] -> [B, D]"""
        ...

class ArchitectureEmbedder(nn.Module):
    """Embed architecture family (CNN/Transformer/RNN)."""
    
    def __init__(self, num_classes: int = 3, embed_dim: int = 64):
        """Embedding: 3 classes -> 64-dim vectors."""
        ...
    
    def forward(self, arch_labels: Tensor) -> Tensor:
        """arch_labels: [B] -> [B, 64]"""
        ...
```

### Pseudo-code

```
1. arch_embed = ArchitectureEmbedder(arch_labels)  # [B, 64]
2. arch_embed = arch_embed.unsqueeze(1).expand(-1, N, -1)  # [B, N, 64]
3. x = concat([weights, arch_embed], dim=-1)  # [B, N, D+64]
4. x = phi(x)  # [B, N, H] - per-element encoding
5. x = x.mean(dim=1)  # [B, H] - permutation-invariant aggregation
6. z = rho(x)  # [B, K] - quotient space representation
7. weights_recon = reconstruct(z)  # [B, D] - for reconstruction loss
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| weights | [B, N, D] | Batch of weight sets |
| arch_labels | [B] | Architecture family (0=CNN, 1=Transformer, 2=RNN) |
| arch_embed | [B, N, 64] | Architecture context |
| x | [B, N, D+64] | Concatenated input |
| z | [B, K] | Quotient space embedding |
| weights_recon | [B, D] | Reconstructed weights |

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | Architecture embedding | Inject arch-specific context before encoding |
| L-3-2 | Slot-equivariant encoder | Extend Deep Sets with LayerNorm for stability |
| L-3-3 | Reconstruction decoder | K-dim -> weight space mapping |

---

## A-4: Training Pipeline [Complexity: 12, Budget: 3 subtasks]

**Applied**: Standard PyTorch training loop with early stopping

### API Signatures

```python
import torch.optim as optim
from torch.optim.lr_scheduler import CosineAnnealingLR
from torch.utils.data import DataLoader

class Trainer:
    """Training orchestrator."""
    
    def __init__(
        self,
        model: nn.Module,
        train_loader: DataLoader,
        val_loader: DataLoader,
        config: dict
    ):
        """Initialize trainer with model and data."""
        ...
    
    def train_epoch(self, epoch: int) -> Dict[str, float]:
        """Train one epoch. Returns: {'loss': x, 'recon_loss': y, 'equiv_loss': z}"""
        ...
    
    def validate(self) -> Dict[str, float]:
        """Validate on val set. Returns: {'val_loss': x, 'val_recon_error': y}"""
        ...
    
    def train(self, num_epochs: int) -> Dict[str, List[float]]:
        """Full training loop. Returns: history dict."""
        ...
    
    def save_checkpoint(self, path: str, metrics: dict) -> None:
        """Save model checkpoint with metrics."""
        ...
    
    def load_checkpoint(self, path: str) -> None:
        """Load model checkpoint."""
        ...

def setup_optimizer(
    model: nn.Module,
    lr: float = 1e-3,
    weight_decay: float = 1e-4
) -> optim.Optimizer:
    """Create Adam optimizer."""
    ...

def setup_scheduler(
    optimizer: optim.Optimizer,
    T_max: int = 100
) -> CosineAnnealingLR:
    """Create cosine annealing scheduler."""
    ...
```

### Pseudo-code

```
For each epoch:
    1. Train phase:
        - Forward pass: model(weights, arch_labels) -> z
        - Compute loss: L_recon + λ_equiv * L_equiv
        - Backward pass and optimizer step
        - Log metrics
    
    2. Validation phase:
        - Forward pass on val set
        - Compute reconstruction error
        - Check early stopping (patience=10)
        - Save checkpoint if best
    
    3. Scheduler step
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | Training loop | Epoch iteration with loss computation |
| L-4-2 | Validation and early stopping | Monitor val loss, save best checkpoint |
| L-4-3 | Checkpointing | Save/load model state with metrics |

---

## A-5: Evaluation Metrics [Complexity: 15, Budget: 3 subtasks]

**Applied**: Custom metric computation for weight space evaluation

### API Signatures

```python
import torch
from typing import Dict
from torch.utils.data import DataLoader

class Evaluator:
    """Metric computation for hypothesis validation."""
    
    def __init__(self, model: nn.Module, test_loader: DataLoader):
        """Initialize evaluator with model and test data."""
        ...
    
    def compute_reconstruction_error(self) -> float:
        """Compute reconstruction error on test set. Returns: percentage."""
        ...
    
    def compute_frozen_k_generalization(self, rnn_loader: DataLoader) -> float:
        """Compute R_RNN on held-out RNN test set. Returns: percentage."""
        ...
    
    def compute_kernel_robustness(self, num_permutations: int = 1000) -> float:
        """Compute % of permutations with D<0.01. Returns: percentage."""
        ...
    
    def evaluate_all(self) -> Dict[str, float]:
        """Compute all metrics. Returns: {'recon_error': x, 'r_rnn': y, 'robustness': z}"""
        ...

def relative_mse(original: Tensor, reconstructed: Tensor) -> float:
    """Compute MSE / ||original||^2 as percentage."""
    ...

def measure_output_divergence(z_original: Tensor, z_permuted: Tensor) -> float:
    """Compute ||z_original - z_permuted||_1 normalized."""
    ...
```

### Pseudo-code

**Reconstruction Error:**
```
1. For each batch in test_loader:
    - z = model(weights, arch_labels)
    - weights_recon = model.reconstruct(z)
    - error = MSE(weights, weights_recon) / ||weights||^2
2. Return mean error * 100 (percentage)
```

**Frozen-K Generalization:**
```
1. Freeze model (no gradients)
2. For each batch in rnn_loader (RNN-only test set):
    - z = model(weights, arch_labels)
    - weights_recon = model.reconstruct(z)
    - error = MSE(weights, weights_recon) / ||weights||^2
3. Return mean error * 100
```

**Kernel Robustness:**
```
1. For each test sample:
    - z_original = model(weights, arch_labels)
    - For i in 1..1000:
        - perm_idx = random_permutation(N)
        - weights_perm = weights[:, perm_idx, :]
        - z_perm = model(weights_perm, arch_labels)
        - divergence = ||z_original - z_perm||_1
        - if divergence < 0.01: robust_count += 1
2. Return (robust_count / 1000) * 100 (percentage)
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | Reconstruction error | MSE-based reconstruction metric |
| L-5-2 | Frozen-K generalization | Cross-architecture generalization test |
| L-5-3 | Kernel robustness | Permutation invariance validation |

---

## A-6: Ablation Studies [Complexity: 9, Budget: 2 subtasks]

**Applied**: Standard hyperparameter sweep

### API Signatures

```python
from typing import List, Dict

def run_ablation_lambda_equiv(
    config: dict,
    lambda_values: List[float]
) -> Dict[float, Dict[str, float]]:
    """Run ablation over λ_equiv values. Returns: {lambda: metrics}"""
    ...

def run_ablation_k_dim(
    config: dict,
    k_values: List[int]
) -> Dict[int, Dict[str, float]]:
    """Run ablation over K values. Returns: {K: metrics}"""
    ...

def compare_baseline_vs_proposed(
    baseline_metrics: Dict[str, float],
    proposed_metrics: Dict[str, float]
) -> Dict[str, float]:
    """Compute performance gaps. Returns: {metric: gap}"""
    ...
```

### Pseudo-code

```
λ_equiv ablation:
1. For each λ in {0.0, 0.25, 0.5, 0.75, 1.0}:
    - Train model with λ_equiv = λ
    - Evaluate all metrics
    - Store results

K dimensionality ablation:
1. For each K in {16, 32, 64}:
    - Train model with output_dim = K
    - Evaluate all metrics
    - Store results

2. Identify minimal K with recon_error < 10%
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-6-1 | λ_equiv sweep | Train 5 models with different equivariance weights |
| L-6-2 | K dimensionality sweep | Train 3 models with different quotient space dimensions |

---

## A-7: Visualization [Complexity: 10, Budget: 2 subtasks]

**Applied**: Matplotlib + scikit-learn (t-SNE/UMAP)

### API Signatures

```python
import matplotlib.pyplot as plt
import numpy as np
from sklearn.manifold import TSNE

def plot_gate_metrics(
    targets: Dict[str, float],
    actuals: Dict[str, float],
    save_path: str
) -> None:
    """Bar chart: target vs actual for gate metrics."""
    ...

def plot_quotient_space_tsne(
    embeddings: np.ndarray,
    arch_labels: np.ndarray,
    save_path: str
) -> None:
    """t-SNE projection colored by architecture family. embeddings: [N, K]"""
    ...

def plot_reconstruction_error_distribution(
    errors: np.ndarray,
    save_path: str
) -> None:
    """Histogram of reconstruction errors across test set."""
    ...

def plot_k_dimensionality_analysis(
    k_values: List[int],
    errors: List[float],
    save_path: str
) -> None:
    """Line plot: K vs reconstruction error."""
    ...

def plot_training_curves(
    history: Dict[str, List[float]],
    save_path: str
) -> None:
    """Training/val loss curves over epochs."""
    ...
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-7-1 | Gate metrics figure | Mandatory bar chart for hypothesis validation |
| L-7-2 | Analysis figures | t-SNE, error distribution, K-analysis, training curves |

---

**Document Status**: Complete
**Total Subtasks**: 20 (within LIGHT tier budget ≤15 per Epic)
**Next Phase**: Phase 4 - Implementation using these API signatures
