# Logic Design: h-m3 SGD Trajectory Directional Bias Analysis

**Hypothesis ID:** h-m3  
**Type:** MECHANISM (Step 3 of 4)  
**Budget:** 18 subtasks (FULL-tier MECHANISM)  
**Date:** 2026-04-24  
**Designer:** Logic Agent  
**Prerequisites:** h-m2 (COMPLETED ✅)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (extends h-m2)  
**Status**: API signatures verified from h-m2 actual code  
**Analyzed Path**: `../h-m2/code/`  
**Critical Finding**: h-m2 used random orthonormal basis (FAILED - all alignments ~1e-06). h-m3 MUST use real Hessian eigenvectors from pytorch-hessian-eigenthings.

**Relevant Symbols from h-m2:**
- `h_m2.code.models.model.get_resnet50(num_classes) -> nn.Module`
- `h_m2.code.data.dataset.get_dataloaders(data_dir, batch_size) -> Dict[str, DataLoader]`
- `h_m2.code.config.load_config(config_path) -> H_M2_Config`

**Note**: h-m3 reuses dataset/model from h-m2 but replaces gradient alignment computation with trajectory logging and real Hessian eigenvectors.

---

## Knowledge Base Patterns Applied

Applied: Real Hessian Eigenvector Computation Pattern (pytorch-hessian-eigenthings)  
Applied: SGD Trajectory Logging Pattern (backward hook-based)  
Applied: Directional Bias Measurement Pattern (bulk vs outlier alignment)  
Applied: Multi-Seed Statistical Validation Pattern

---

## External Dependencies API (from h-m2)

### Dataset and Model (Reuse from h-m2)

```python
# From: ../h-m2/code/ (verified actual implementation)

# Dataset loading
from h_m2.code.data.dataset import get_dataloaders
def get_dataloaders(data_dir: str, batch_size: int = 128) -> Dict[str, DataLoader]:
    """
    Returns:
        loaders: dict with keys 'train', 'val', 'test'
    """
    ...

# Model architecture
from h_m2.code.models.model import get_resnet50
def get_resnet50(num_classes: int = 2, pretrained: bool = True) -> nn.Module:
    """Returns ResNet-50 with modified final layer"""
    ...
```

**Verified from**: h-m2 code structure

---

## C-2: Hessian Eigenvector Computation Module [Complexity: 15, Budget: 4 subtasks]

**Applied**: Real Hessian Eigenvector Pattern (CRITICAL FIX from h-m2)

### API Signatures

```python
# File: hessian_eigenvectors.py

from hessian_eigenthings import compute_hessian_eigenthings
import torch
import torch.nn as nn
import numpy as np
from typing import Tuple, List
from torch.utils.data import DataLoader

def compute_real_hessian_eigenvectors(
    model: nn.Module, 
    train_loader: DataLoader,
    num_eigenthings: int = 50,
    device: str = 'cuda'
) -> Tuple[np.ndarray, List]:
    """
    Compute REAL Hessian eigenvectors using pytorch-hessian-eigenthings
    
    Args:
        model: ResNet-50 model (after epoch 0)
        train_loader: Training data loader
        num_eigenthings: Number of top eigenvectors (50 for h-m3)
        device: Device to run computation on
    
    Returns:
        eigenvalues: (50,) - top eigenvalues (descending order)
        eigenvectors: List[Tensor] - eigenvectors (length 50)
    
    Algorithm:
        1. Call compute_hessian_eigenthings with power iteration
        2. num_eigenthings=50, mode='power_iter', steps=20
        3. loss=nn.CrossEntropyLoss() for classification
        4. Returns eigenvalues as NumPy array, eigenvectors as list
    
    Critical: This REPLACES h-m2's random basis (h-m2 failure fix)
    """
    ...

def separate_bulk_outlier_subspaces(
    eigenvalues: np.ndarray, 
    eigenvectors: List,
    model: nn.Module,
    n_samples: int
) -> Tuple[List, List, float]:
    """
    Separate bulk (flat) vs outlier (sharp) subspaces using Marchenko-Pastur
    
    Args:
        eigenvalues: (50,) Hessian eigenvalues
        eigenvectors: List[Tensor] Hessian eigenvectors
        model: Model (for parameter count p)
        n_samples: Training set size (n)
    
    Returns:
        outlier_evecs: List[Tensor] - sharp direction eigenvectors
        bulk_evecs: List[Tensor] - flat direction eigenvectors
        bulk_edge: float - Marchenko-Pastur threshold λ+
    
    Algorithm:
        1. p = sum(param.numel() for param in model.parameters())
        2. gamma = p / n_samples
        3. sigma_sq = 1.0 (estimate from bulk eigenvalues)
        4. bulk_edge = sigma_sq * (1 + sqrt(gamma))^2
        5. outlier_mask = eigenvalues > bulk_edge
        6. Split eigenvectors into outlier/bulk lists
    """
    ...

def validate_eigenvectors(
    eigenvectors: List,
    expected_count: int = 50
) -> bool:
    """
    Validate eigenvectors are real (not random like h-m2)
    
    Checks:
        - Length matches expected_count
        - No NaN/Inf values
        - Approximate orthonormality (V^T @ V ≈ I)
        - NOT random orthonormal (verify via spectrum structure)
    """
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| model.parameters() | varies | ~23.5M total params for ResNet-50 |
| eigenvalues | [50] | Top 50 eigenvalues |
| eigenvectors[i] | [num_params] or List[Tensor] | Per-eigenvector shape |
| outlier_evecs | List | Length varies (depends on bulk_edge) |
| bulk_evecs | List | Length varies |

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | Install and Configure Library | Setup pytorch-hessian-eigenthings, test on small model |
| L-2-2 | Implement Hessian Computation | compute_real_hessian_eigenvectors() with power iteration |
| L-2-3 | Marchenko-Pastur Separation | Separate bulk (flat) vs outlier (sharp) subspaces |
| L-2-4 | Validation | Verify eigenvectors are real (not random like h-m2) |

---

## C-3: Marchenko-Pastur Bulk Edge Detection [Complexity: 12, Budget: 2 subtasks]

**Applied**: Marchenko-Pastur Theory Pattern

### API Signatures

```python
# Included in hessian_eigenvectors.py

def estimate_marchenko_pastur_params(
    eigenvalues: np.ndarray,
    p: int,
    n: int
) -> Tuple[float, float, float]:
    """
    Estimate Marchenko-Pastur parameters from eigenvalue spectrum
    
    Args:
        eigenvalues: (50,) top eigenvalues
        p: Number of parameters
        n: Number of training samples
    
    Returns:
        sigma_sq: Estimated noise variance
        gamma: Aspect ratio p/n
        bulk_edge: λ+ threshold
    
    Algorithm:
        1. gamma = p / n
        2. Estimate sigma_sq from bulk portion of spectrum
        3. bulk_edge = sigma_sq * (1 + sqrt(gamma))^2
    """
    ...

def visualize_spectrum_with_bulk_edge(
    eigenvalues: np.ndarray,
    bulk_edge: float,
    save_path: str
):
    """
    Plot eigenvalue spectrum with Marchenko-Pastur bulk edge overlay
    
    Figure: Log-scale eigenvalue plot with bulk_edge threshold line
    """
    ...
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | MP Parameter Estimation | Estimate sigma_sq, gamma, bulk_edge from spectrum |
| L-3-2 | Validation | Verify bulk_edge separates outlier/bulk regions |

---

## C-4: Trajectory Logger Module [Complexity: 14, Budget: 4 subtasks]

**Applied**: SGD Trajectory Logging Pattern

### API Signatures

```python
# File: trajectory_logger.py

import torch
import torch.nn as nn
import numpy as np
from typing import List, Dict, Any

class TrajectoryLogger:
    """
    Logs SGD trajectory alignment to Hessian eigenvector subspaces.
    Measures directional bias: bulk (flat) vs outlier (sharp) alignment.
    """
    def __init__(
        self, 
        model: nn.Module, 
        outlier_evecs: List, 
        bulk_evecs: List
    ):
        """
        Args:
            model: ResNet-50 model
            outlier_evecs: Sharp direction eigenvectors
            bulk_evecs: Flat direction eigenvectors
        """
        self.model = model
        self.outlier_evecs = outlier_evecs
        self.bulk_evecs = bulk_evecs
        self.trajectory = []
        
    def log_step(self, epoch: int, step: int, loss: float):
        """
        Log gradient alignment BEFORE optimizer.step()
        
        Computes:
        - bulk_alignment: mean alignment to flat directions
        - outlier_alignment: mean alignment to sharp directions
        - directional_bias: bulk - outlier (positive = prefers flat)
        
        Algorithm:
            1. Flatten all gradients: grad_vector = cat([p.grad.view(-1) for p in model.parameters()])
            2. grad_norm_sq = grad_vector.norm()^2 + epsilon
            3. For each outlier eigenvector: alignment_i = (grad @ evec_i)^2 / grad_norm_sq
            4. outlier_align = mean(alignment_i for i in outlier_evecs)
            5. bulk_align = mean(alignment_i for i in bulk_evecs)
            6. bias = bulk_align - outlier_align
            7. Append to trajectory
        """
        ...
    
    def _flatten_eigenvector(self, evec) -> torch.Tensor:
        """
        Flatten eigenvector to match gradient shape
        
        Returns:
            evec_flat: (num_params,) flattened tensor
        """
        ...
    
    def compute_statistics(self) -> Dict[str, float]:
        """
        Compute aggregate statistics over trajectory
        
        Returns:
            stats: dict with:
                - mean_directional_bias: float
                - std_directional_bias: float
                - mean_bulk_alignment: float
                - mean_outlier_alignment: float
                - final_bias: float (last epoch value)
        """
        ...
    
    def get_trajectory(self) -> List[Dict]:
        """Return full trajectory for visualization"""
        return self.trajectory
    
    def save_trajectory(self, save_path: str):
        """Save trajectory to CSV"""
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| grad_vector | [num_params] | ~23.5M for ResNet-50 |
| evec_flat | [num_params] | Flattened eigenvector |
| alignment_i | scalar | Per-eigenvector alignment |
| outlier_align | scalar | Mean over outlier eigenvectors |
| bulk_align | scalar | Mean over bulk eigenvectors |
| bias | scalar | bulk - outlier |

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | TrajectoryLogger Class | Implement initialization and gradient capture |
| L-4-2 | Alignment Computation | Compute bulk/outlier alignment per step |
| L-4-3 | Statistics Aggregation | compute_statistics() over full trajectory |
| L-4-4 | Trajectory Saving | Save to CSV for visualization |

---

## C-5: Training Loop Integration [Complexity: 13, Budget: 2 subtasks]

**Applied**: 100-Epoch Training with Trajectory Logging

### API Signatures

```python
# File: training.py

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from trajectory_logger import TrajectoryLogger
from typing import Dict, Any

def train_with_trajectory_logging(
    model: nn.Module,
    train_loader: DataLoader,
    val_loader: DataLoader,
    logger: TrajectoryLogger,
    config: Dict[str, Any],
    device: str = 'cuda'
) -> Dict[str, Any]:
    """
    Train model with SGD trajectory logging (100 epochs)
    
    Args:
        model: ResNet-50 model
        train_loader: Training data loader
        val_loader: Validation data loader
        logger: TrajectoryLogger instance
        config: Training configuration dict
        device: Device to train on
    
    Returns:
        training_history: Dict with loss curves and metrics
    
    Algorithm:
        1. Setup optimizer (SGD) and scheduler (StepLR)
        2. For each epoch (100 total):
            a. For each batch:
                - Forward pass
                - Backward pass (compute gradients)
                - logger.log_step(epoch, step, loss) BEFORE optimizer.step()
                - optimizer.step()
            b. scheduler.step()
            c. Validation
            d. Save checkpoint if epoch in [10, 20, 30]
        3. Return training history
    """
    ...

def validate(
    model: nn.Module, 
    val_loader: DataLoader, 
    criterion: nn.Module, 
    device: str
) -> Dict[str, float]:
    """
    Validation loop with group-wise accuracy
    
    Returns:
        metrics: dict with 'loss', 'accuracy', 'worst_group_acc'
    """
    ...

def save_checkpoint(
    model: nn.Module,
    optimizer: optim.Optimizer,
    epoch: int,
    checkpoint_dir: str
):
    """Save model checkpoint for early prediction experiment"""
    ...
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | Training Loop Implementation | 100-epoch training with trajectory logging hooks |
| L-5-2 | Checkpoint Management | Save checkpoints at epochs 10, 20, 30 for early prediction |

---

## C-6: Directional Bias Evaluation [Complexity: 11, Budget: 2 subtasks]

**Applied**: Multi-Seed Statistical Validation Pattern

### API Signatures

```python
# File: directional_bias.py

import numpy as np
from scipy.stats import ttest_1samp
from typing import Dict, Any, List
from trajectory_logger import TrajectoryLogger

def evaluate_directional_bias(
    loggers: List[TrajectoryLogger]
) -> Dict[str, Any]:
    """
    Evaluate gate metric: directional bias across seeds
    
    Args:
        loggers: List of TrajectoryLogger instances (one per seed, length 3)
    
    Returns:
        gate_result: dict with:
            - gate_pass: bool - True if mean_bias > 0 across all seeds (p < 0.05)
            - overall_mean_bias: float
            - std_across_seeds: float
            - p_value: float
            - per_seed_stats: List[Dict] - statistics for each seed
            - t_statistic: float
    
    Algorithm:
        1. For each logger: stats = logger.compute_statistics()
        2. Extract mean_biases = [stats['mean_directional_bias'] for stats in stats_list]
        3. Perform one-sample t-test: t_stat, p_value = ttest_1samp(mean_biases, 0.0)
        4. gate_pass = (mean(mean_biases) > 0) AND (p_value < 0.05)
    """
    ...

def compute_worst_group_accuracy(
    model: nn.Module,
    test_loader: DataLoader,
    device: str
) -> float:
    """
    Compute worst-group accuracy for early prediction experiment
    
    Returns:
        worst_group_acc: float - minimum accuracy across 4 Waterbirds groups
    """
    ...
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-6-1 | Statistical Test Implementation | One-sample t-test for mean_bias vs 0 |
| L-6-2 | Gate Decision Logic | Determine PASS/FAIL based on p-value and mean |

---

## C-7: Early Prediction Experiment [Complexity: 12, Budget: 2 subtasks]

**Applied**: Checkpoint-Based Early Prediction Pattern

### API Signatures

```python
# File: directional_bias.py (continued)

from sklearn.metrics import r2_score

def compute_early_alignment_at_checkpoint(
    checkpoint_path: str,
    train_loader: DataLoader,
    device: str
) -> float:
    """
    Compute A(w) at checkpoint (e.g., epoch 10)
    
    Algorithm:
        1. Load model from checkpoint
        2. Compute Hessian eigenvectors
        3. Separate outlier subspace
        4. Compute minority gradient
        5. Compute alignment A(w) = ||P @ g_minority||^2 / ||g_minority||^2
    
    Returns:
        early_Aw: float - alignment at early checkpoint
    """
    ...

def compute_early_prediction_r2(
    checkpoint_paths: List[str],
    train_loader: DataLoader,
    final_wga_values: List[float]
) -> Dict[str, Any]:
    """
    Compute R² between early A(w) (epoch 10) and final worst-group accuracy
    
    Args:
        checkpoint_paths: Paths to epoch 10 checkpoints (3 seeds)
        train_loader: Training data loader
        final_wga_values: Final worst-group accuracies (3 seeds)
    
    Returns:
        early_prediction_results: dict with:
            - r2_score: float
            - early_Aw_values: List[float] (3 seeds)
            - final_wga_values: List[float] (3 seeds)
            - early_prediction_valid: bool (r2 > 0.1)
    
    Algorithm:
        1. For each checkpoint: early_Aw = compute_early_alignment_at_checkpoint(ckpt)
        2. Compute r2 = r2_score(final_wga_values, early_Aw_values)
        3. Validate: r2 > 0.1 (secondary metric threshold)
    """
    ...
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-7-1 | Early Alignment Computation | Compute A(w) at epoch 10 checkpoints |
| L-7-2 | R² Correlation Analysis | Correlate early A(w) with final WGA |

---

## C-8: Trajectory Visualizations [Complexity: 11, Budget: 1 subtask]

**Applied**: Multi-Seed Trajectory Visualization Pattern

### API Signatures

```python
# File: visualize_trajectory.py

import matplotlib.pyplot as plt
import numpy as np
from typing import List, Dict

def plot_directional_bias_over_time(
    trajectories: List[List[Dict]], 
    save_path: str
):
    """
    Plot directional bias over training epochs (3 seeds + mean ± std)
    
    Args:
        trajectories: List of trajectories (one per seed)
        save_path: Output file path
    
    Figure Elements:
        - 3 individual seed lines (alpha=0.3)
        - Mean line (black, linewidth=2)
        - Std shaded region (gray, alpha=0.2)
        - Threshold line at y=0 (red, dashed)
        - X-axis: Training epoch (0-100)
        - Y-axis: Directional bias (bulk - outlier)
    """
    ...

def plot_bulk_vs_outlier_alignment(
    trajectory: List[Dict], 
    save_path: str
):
    """
    Plot bulk vs outlier alignment over training
    
    Figure Elements:
        - Bulk alignment line (blue)
        - Outlier alignment line (red)
        - X-axis: Training epoch
        - Y-axis: Alignment value
    """
    ...

def plot_gate_metric_comparison(
    eval_results: Dict, 
    save_path: str
):
    """
    Bar chart: Gate metric - directional bias across seeds (MANDATORY)
    
    Figure Elements:
        - 4 bars: Seed 1, Seed 2, Seed 3, Overall Mean
        - Threshold line at y=0
        - P-value annotation in title
    """
    ...
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-8-1 | Generate 5 trajectory visualization figures | Implement all visualization functions |

---

## C-9: Multi-Seed Execution [Complexity: 10, Budget: 1 subtask]

**Applied**: Seed Loop Orchestration Pattern

### API Signatures

```python
# File: run_h_m3_experiment.py

def run_experiment_for_seed(
    seed: int,
    config: Dict[str, Any]
) -> Tuple[TrajectoryLogger, float]:
    """
    Run full experiment for single seed
    
    Args:
        seed: Random seed
        config: Configuration dict
    
    Returns:
        logger: TrajectoryLogger with full trajectory
        final_wga: Final worst-group accuracy
    
    Algorithm:
        1. Set seed
        2. Load data
        3. Create model
        4. Compute Hessian eigenvectors
        5. Create TrajectoryLogger
        6. Train 100 epochs with logging
        7. Compute final worst-group accuracy
        8. Return logger and WGA
    """
    ...

def main():
    """
    Main execution: Run experiment for 3 seeds, evaluate gate metric
    
    Algorithm:
        1. Load config
        2. For each seed in [42, 43, 44]:
            - Run experiment
            - Save logger and final_wga
        3. Evaluate directional bias across seeds
        4. Compute early prediction R²
        5. Generate visualizations
        6. Save results
        7. Report gate decision
    """
    ...
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-9-1 | Implement seed loop and aggregation | Run 3 seeds, aggregate results |

---

## Subtask Budget Summary

| Task | Complexity | Subtasks Allocated | Subtask IDs |
|------|------------|-------------------|-------------|
| C-2 | 15 (High) | 4 | L-2-1, L-2-2, L-2-3, L-2-4 |
| C-3 | 12 (Medium) | 2 | L-3-1, L-3-2 |
| C-4 | 14 (High) | 4 | L-4-1, L-4-2, L-4-3, L-4-4 |
| C-5 | 13 (Medium) | 2 | L-5-1, L-5-2 |
| C-6 | 11 (Medium) | 2 | L-6-1, L-6-2 |
| C-7 | 12 (Medium) | 2 | L-7-1, L-7-2 |
| C-8 | 11 (Medium) | 1 | L-8-1 |
| C-9 | 10 (Medium) | 1 | L-9-1 |
| **Total** | **98** | **18** | |

**Budget Compliance**: 18 subtasks allocated (within 21 available after infrastructure/failsafe)

---

## Critical Implementation Notes

### h-m2 Failure Fix

**h-m2 Problem**: Used random orthonormal basis instead of real Hessian eigenvectors → all alignments collapsed to ~1e-06.

**h-m3 Fix**: Use `pytorch-hessian-eigenthings.compute_hessian_eigenthings()` for REAL Hessian eigenvectors.

**Validation**:
1. Verify eigenvector computation completes without error
2. Check alignment values are NOT near-zero (unlike h-m2)
3. Validate eigenvalue spectrum structure (not uniform like random basis)

### Memory Efficiency

**Gradient Logging**: Log every 10 steps (not every step) to avoid memory overflow during 100-epoch training.

**Projection**: Use on-the-fly projection `(grad @ evec)^2 / grad_norm^2` instead of materializing full projection matrix.

---

*Logic designed for Phase 4 Implementation | h-m3 MECHANISM Hypothesis | Fixes h-m2 random basis with real Hessian eigenvectors*
