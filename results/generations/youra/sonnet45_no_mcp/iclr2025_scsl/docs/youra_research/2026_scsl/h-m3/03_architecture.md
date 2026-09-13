# System Architecture: h-m3 SGD Trajectory Directional Bias Analysis

**Hypothesis ID:** h-m3  
**Type:** MECHANISM (Step 3 of 4)  
**Gate:** SHOULD_WORK  
**Date:** 2026-04-24  
**Architect:** Architecture Agent  
**Prerequisites:** h-m2 (COMPLETED ✅)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (extends h-m2)  
**Status**: patterns found from base code  
**Analyzed Path**: `../h-m2/code/`  
**Findings**: h-m2 implements gradient alignment computation to outlier subspace. **CRITICAL FIX NEEDED:** h-m2 used random orthonormal basis (all alignments ~1e-06). h-m3 MUST use real Hessian eigenvectors from pytorch-hessian-eigenthings. Reuse dataset/model configuration from h-m2, but replace 5-epoch PoC with 100-epoch full training and add trajectory logging with real eigenvectors.

---

## Knowledge Base Patterns Applied

Applied: Incremental Hypothesis Pattern (extends h-m2 with trajectory analysis)  
Applied: Real Hessian Eigenvector Pattern (fix h-m2 random basis limitation)  
Applied: Trajectory Logging Pattern (SGD dynamics analysis)  
Applied: Directional Bias Measurement Pattern (bulk vs outlier alignment)

---

## System Overview

**Purpose**: Validate that SGD dynamics preferentially follow locally flat directions (bulk subspace) to minimize curvature-induced gradient variance during training.

**Core Components**:
- Hessian eigenvector computation (REAL eigenvectors, not random basis)
- Marchenko-Pastur bulk edge detection (separate flat vs sharp subspaces)
- SGD trajectory logger (backward hook for gradient capture)
- Directional bias measurement (bulk_alignment - outlier_alignment)
- Full 100-epoch training protocol (not 5-epoch PoC)
- Early prediction experiment (checkpoint analysis)

**Infrastructure Tier**: FULL (30 tasks for MECHANISM with 100-epoch training)

**Critical Fix from h-m2**: Use pytorch-hessian-eigenthings for real Hessian eigenvectors, not random orthonormal basis.

---

## External Dependencies (h-m2)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| Dataset Loading | Reuse: `../h-m2/code/data/dataset.py` | h-m2 data loading |
| Model Architecture | `from h_m2.code.models.model import get_resnet50` | `h-m2/code/models/model.py` |
| Training Config | `from h_m2.code.config import load_config` | `h-m2/code/config.py` |

**Verified from**: `h-m2/code/` actual implementation

**Note**: h-m3 reuses dataset/model configuration from h-m2, but **DOES NOT** reuse gradient computation (h-m2 used random basis). New Hessian computation required.

---

## Module Structure

### 1. Hessian Eigenvector Computation Module (`hessian_eigenvectors.py`) [NEW]

**Dependencies**: pytorch-hessian-eigenthings, PyTorch, NumPy

```python
from hessian_eigenthings import compute_hessian_eigenthings
import torch
import torch.nn as nn
import numpy as np
from typing import Tuple, List

def compute_real_hessian_eigenvectors(model: nn.Module, 
                                     train_loader: DataLoader,
                                     num_eigenthings: int = 50,
                                     device: str = 'cuda') -> Tuple[np.ndarray, List]:
    """
    Compute REAL Hessian eigenvectors (FIX h-m2 random basis)
    
    Args:
        model: ResNet-50 model (after epoch 0)
        train_loader: Training data loader
        num_eigenthings: Number of top eigenvectors (50 for h-m3)
        device: Device to run computation on
    
    Returns:
        eigenvalues: (50,) - top eigenvalues (descending)
        eigenvectors: List[Tensor] - eigenvectors (length 50)
    """
    eigenvalues, eigenvectors = compute_hessian_eigenthings(
        model, 
        train_loader, 
        loss=nn.CrossEntropyLoss(),
        num_eigenthings=num_eigenthings,
        mode='power_iter',
        power_iter_steps=20,
        use_gpu=(device == 'cuda')
    )
    
    return np.array(eigenvalues), eigenvectors

def separate_bulk_outlier_subspaces(eigenvalues: np.ndarray, 
                                   eigenvectors: List,
                                   model: nn.Module,
                                   n_samples: int) -> Tuple[List, List, float]:
    """
    Separate bulk (flat) vs outlier (sharp) subspaces using Marchenko-Pastur
    
    Args:
        eigenvalues: Hessian eigenvalues
        eigenvectors: Hessian eigenvectors
        model: Model (for parameter count)
        n_samples: Training set size
    
    Returns:
        outlier_evecs: Sharp direction eigenvectors
        bulk_evecs: Flat direction eigenvectors
        bulk_edge: Marchenko-Pastur threshold
    """
    # Estimate Marchenko-Pastur parameters
    p = sum(param.numel() for param in model.parameters())
    gamma = p / n_samples
    sigma_sq = 1.0  # Estimate from small eigenvalues
    
    # Compute bulk edge
    bulk_edge = sigma_sq * (1 + np.sqrt(gamma)) ** 2
    
    # Separate subspaces
    outlier_mask = eigenvalues > bulk_edge
    outlier_evecs = [eigenvectors[i] for i in range(len(eigenvalues)) if outlier_mask[i]]
    bulk_evecs = [eigenvectors[i] for i in range(len(eigenvalues)) if not outlier_mask[i]]
    
    return outlier_evecs, bulk_evecs, bulk_edge
```

---

### 2. Trajectory Logger Module (`trajectory_logger.py`) [NEW]

**Dependencies**: PyTorch, NumPy

```python
import torch
import torch.nn as nn
import numpy as np
from typing import List, Dict, Any

class TrajectoryLogger:
    """
    Logs SGD trajectory alignment to Hessian eigenvector subspaces.
    Measures directional bias: bulk (flat) vs outlier (sharp) alignment.
    """
    def __init__(self, model: nn.Module, outlier_evecs: List, bulk_evecs: List):
        self.model = model
        self.outlier_evecs = outlier_evecs  # Sharp directions
        self.bulk_evecs = bulk_evecs        # Flat directions
        self.trajectory = []
        
    def log_step(self, epoch: int, step: int, loss: float):
        """
        Log gradient alignment BEFORE optimizer.step()
        
        Computes:
        - bulk_alignment: mean alignment to flat directions
        - outlier_alignment: mean alignment to sharp directions
        - directional_bias: bulk - outlier (positive = prefers flat)
        """
        # Flatten all gradients
        grad_list = []
        for p in self.model.parameters():
            if p.grad is not None:
                grad_list.append(p.grad.view(-1))
        grad_vector = torch.cat(grad_list)
        grad_norm_sq = grad_vector.norm() ** 2 + 1e-12
        
        # Compute alignment to outlier (sharp) directions
        outlier_alignments = []
        for evec in self.outlier_evecs:
            evec_flat = self._flatten_eigenvector(evec)
            alignment = (grad_vector @ evec_flat) ** 2 / grad_norm_sq
            outlier_alignments.append(alignment.item())
        outlier_align = np.mean(outlier_alignments) if outlier_alignments else 0.0
        
        # Compute alignment to bulk (flat) directions
        bulk_alignments = []
        for evec in self.bulk_evecs:
            evec_flat = self._flatten_eigenvector(evec)
            alignment = (grad_vector @ evec_flat) ** 2 / grad_norm_sq
            bulk_alignments.append(alignment.item())
        bulk_align = np.mean(bulk_alignments) if bulk_alignments else 0.0
        
        # Directional bias: positive = prefers flat
        bias = bulk_align - outlier_align
        
        self.trajectory.append({
            'epoch': epoch,
            'step': step,
            'loss': loss,
            'bulk_alignment': bulk_align,
            'outlier_alignment': outlier_align,
            'directional_bias': bias
        })
    
    def _flatten_eigenvector(self, evec) -> torch.Tensor:
        """Flatten eigenvector to match gradient shape"""
        if isinstance(evec, list):
            return torch.cat([v.view(-1) for v in evec])
        else:
            return evec.view(-1)
    
    def compute_statistics(self) -> Dict[str, float]:
        """
        Compute aggregate statistics over trajectory
        
        Returns:
            stats: dict with mean directional bias, bulk/outlier alignments
        """
        biases = [t['directional_bias'] for t in self.trajectory]
        bulk_aligns = [t['bulk_alignment'] for t in self.trajectory]
        outlier_aligns = [t['outlier_alignment'] for t in self.trajectory]
        
        return {
            'mean_directional_bias': np.mean(biases),
            'std_directional_bias': np.std(biases),
            'mean_bulk_alignment': np.mean(bulk_aligns),
            'mean_outlier_alignment': np.mean(outlier_aligns),
            'final_bias': biases[-1] if biases else 0.0
        }
    
    def get_trajectory(self) -> List[Dict]:
        """Return full trajectory for visualization"""
        return self.trajectory
```

---

### 3. Training Module (`training.py`) [EXTENDED from h-m2]

**Dependencies**: PyTorch, trajectory_logger

```python
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from trajectory_logger import TrajectoryLogger
from typing import Dict, Any

def train_with_trajectory_logging(model: nn.Module,
                                  train_loader: DataLoader,
                                  val_loader: DataLoader,
                                  logger: TrajectoryLogger,
                                  config: Dict[str, Any],
                                  device: str = 'cuda') -> Dict[str, Any]:
    """
    Train model with SGD trajectory logging (100 epochs, not 5)
    
    Args:
        model: ResNet-50 model
        train_loader: Training data loader
        val_loader: Validation data loader
        logger: TrajectoryLogger instance
        config: Training configuration
        device: Device to train on
    
    Returns:
        training_history: Dict with loss curves and metrics
    """
    model.to(device)
    
    # Optimizer and scheduler (same as h-m2)
    optimizer = optim.SGD(model.parameters(), 
                          lr=config['lr'], 
                          momentum=config['momentum'], 
                          weight_decay=config['weight_decay'])
    scheduler = optim.lr_scheduler.StepLR(optimizer, 
                                          step_size=config['step_size'], 
                                          gamma=config['gamma'])
    criterion = nn.CrossEntropyLoss()
    
    training_history = {'train_loss': [], 'val_loss': [], 'val_acc': []}
    
    for epoch in range(config['epochs']):  # 100 epochs (not 5 like h-m2)
        model.train()
        epoch_loss = 0.0
        
        for step, (inputs, targets, groups) in enumerate(train_loader):
            inputs, targets = inputs.to(device), targets.to(device)
            
            # Forward pass
            outputs = model(inputs)
            loss = criterion(outputs, targets)
            
            # Backward pass
            optimizer.zero_grad()
            loss.backward()
            
            # Log trajectory BEFORE optimizer.step()
            if step % config['log_frequency'] == 0:  # Log every 10 steps
                logger.log_step(epoch, step, loss.item())
            
            # Update parameters
            optimizer.step()
            
            epoch_loss += loss.item()
        
        scheduler.step()
        
        # Validation
        val_metrics = validate(model, val_loader, criterion, device)
        training_history['train_loss'].append(epoch_loss / len(train_loader))
        training_history['val_loss'].append(val_metrics['loss'])
        training_history['val_acc'].append(val_metrics['accuracy'])
        
        # Save checkpoints for early prediction
        if epoch in config['checkpoint_epochs']:  # [10, 20, 30]
            save_checkpoint(model, optimizer, epoch, config['checkpoint_dir'])
        
        # Print progress
        if epoch % 10 == 0:
            print(f"Epoch {epoch}/{config['epochs']}: "
                  f"Train Loss {training_history['train_loss'][-1]:.4f}, "
                  f"Val Acc {val_metrics['accuracy']:.4f}")
    
    return training_history

def validate(model: nn.Module, val_loader: DataLoader, 
            criterion: nn.Module, device: str) -> Dict[str, float]:
    """Validation loop with group-wise accuracy"""
    model.eval()
    total_loss = 0.0
    correct = 0
    total = 0
    
    with torch.no_grad():
        for inputs, targets, groups in val_loader:
            inputs, targets = inputs.to(device), targets.to(device)
            outputs = model(inputs)
            loss = criterion(outputs, targets)
            
            total_loss += loss.item()
            _, predicted = outputs.max(1)
            total += targets.size(0)
            correct += predicted.eq(targets).sum().item()
    
    return {
        'loss': total_loss / len(val_loader),
        'accuracy': correct / total
    }
```

---

### 4. Directional Bias Evaluation Module (`directional_bias.py`) [NEW]

**Dependencies**: NumPy, SciPy

```python
import numpy as np
from scipy.stats import ttest_1samp
from typing import Dict, Any, List
from trajectory_logger import TrajectoryLogger

def evaluate_directional_bias(loggers: List[TrajectoryLogger]) -> Dict[str, Any]:
    """
    Evaluate gate metric: directional bias across seeds
    
    Args:
        loggers: List of TrajectoryLogger instances (one per seed)
    
    Returns:
        gate_result: bool - True if mean_bias > 0 across all seeds (p < 0.05)
        metrics: dict - all statistics
    """
    stats_list = [logger.compute_statistics() for logger in loggers]
    
    mean_biases = [stats['mean_directional_bias'] for stats in stats_list]
    
    # Statistical test: mean > 0 across seeds
    t_stat, p_value = ttest_1samp(mean_biases, 0.0)
    
    gate_pass = (np.mean(mean_biases) > 0) and (p_value < 0.05)
    
    return {
        'gate_pass': gate_pass,
        'overall_mean_bias': np.mean(mean_biases),
        'std_across_seeds': np.std(mean_biases),
        'p_value': p_value,
        'per_seed_stats': stats_list,
        't_statistic': t_stat
    }

def compute_early_prediction_r2(checkpoint_paths: List[str],
                               train_loader: DataLoader,
                               final_wga_values: List[float]) -> Dict[str, Any]:
    """
    Compute R² between early A(w) and final worst-group accuracy
    
    Args:
        checkpoint_paths: Paths to epoch 10 checkpoints (3 seeds)
        train_loader: Training data loader
        final_wga_values: Final worst-group accuracies (3 seeds)
    
    Returns:
        early_prediction_results: dict with R² score
    """
    from sklearn.metrics import r2_score
    
    # Load checkpoints and compute early A(w) at epoch 10
    early_Aw_values = []
    for ckpt_path in checkpoint_paths:
        # Load model, compute Hessian, compute minority gradient alignment
        # (Implementation details omitted for brevity)
        early_Aw = 0.0  # Placeholder
        early_Aw_values.append(early_Aw)
    
    r2 = r2_score(final_wga_values, early_Aw_values)
    
    return {
        'r2_score': r2,
        'early_Aw_values': early_Aw_values,
        'final_wga_values': final_wga_values,
        'early_prediction_valid': r2 > 0.1
    }
```

---

### 5. Visualization Module (`visualize_trajectory.py`) [NEW]

**Dependencies**: matplotlib, NumPy

```python
import matplotlib.pyplot as plt
import numpy as np
from typing import List, Dict

def plot_directional_bias_over_time(trajectories: List[List[Dict]], 
                                    save_path: str):
    """Plot directional bias over training epochs (3 seeds)"""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    colors = ['blue', 'green', 'red']
    for i, trajectory in enumerate(trajectories):
        epochs = [t['epoch'] for t in trajectory]
        biases = [t['directional_bias'] for t in trajectory]
        ax.plot(epochs, biases, alpha=0.3, color=colors[i], label=f'Seed {i+1}')
    
    # Compute mean and std across seeds
    mean_bias = np.mean([[t['directional_bias'] for t in traj] for traj in trajectories], axis=0)
    std_bias = np.std([[t['directional_bias'] for t in traj] for traj in trajectories], axis=0)
    epochs = [t['epoch'] for t in trajectories[0]]
    
    # Plot mean with std shading
    ax.plot(epochs, mean_bias, linewidth=2, color='black', label='Mean')
    ax.fill_between(epochs, mean_bias - std_bias, mean_bias + std_bias, 
                     alpha=0.2, color='black', label='±1 std')
    
    # Threshold line
    ax.axhline(y=0, color='red', linestyle='--', linewidth=1.5, label='Threshold (bias=0)')
    
    ax.set_xlabel('Training Epoch')
    ax.set_ylabel('Directional Bias (bulk - outlier)')
    ax.set_title('SGD Directional Bias Over Training')
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()

def plot_bulk_vs_outlier_alignment(trajectory: List[Dict], save_path: str):
    """Plot bulk vs outlier alignment over training"""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    epochs = [t['epoch'] for t in trajectory]
    bulk_aligns = [t['bulk_alignment'] for t in trajectory]
    outlier_aligns = [t['outlier_alignment'] for t in trajectory]
    
    ax.plot(epochs, bulk_aligns, linewidth=2, color='blue', label='Bulk (Flat) Alignment')
    ax.plot(epochs, outlier_aligns, linewidth=2, color='red', label='Outlier (Sharp) Alignment')
    
    ax.set_xlabel('Training Epoch')
    ax.set_ylabel('Alignment Value')
    ax.set_title('Bulk vs Outlier Alignment Trajectories')
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()

def plot_gate_metric_comparison(eval_results: Dict, save_path: str):
    """Bar chart: Gate metric - directional bias across seeds (MANDATORY)"""
    fig, ax = plt.subplots(figsize=(8, 6))
    
    per_seed_biases = [stats['mean_directional_bias'] 
                       for stats in eval_results['per_seed_stats']]
    seeds = [f'Seed {i+1}' for i in range(len(per_seed_biases))]
    seeds.append('Overall Mean')
    values = per_seed_biases + [eval_results['overall_mean_bias']]
    
    colors = ['blue', 'green', 'red', 'black']
    ax.bar(seeds, values, color=colors, alpha=0.7)
    
    # Add threshold line
    ax.axhline(y=0, color='darkred', linestyle='--', linewidth=2, label='Threshold (bias=0)')
    
    ax.set_ylabel('Mean Directional Bias')
    ax.set_title(f'Gate Metric: Directional Bias (p={eval_results["p_value"]:.4f})')
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()
```

---

### 6. Main Experiment Script (`run_h_m3_experiment.py`) [NEW]

**Dependencies**: All modules above

```python
from hessian_eigenvectors import compute_real_hessian_eigenvectors, separate_bulk_outlier_subspaces
from trajectory_logger import TrajectoryLogger
from training import train_with_trajectory_logging
from directional_bias import evaluate_directional_bias, compute_early_prediction_r2
from visualize_trajectory import plot_directional_bias_over_time, plot_bulk_vs_outlier_alignment, plot_gate_metric_comparison
import torch
import sys
from pathlib import Path

def main():
    """Run h-m3 SGD trajectory experiment"""
    
    # Load configuration
    config = {
        'lr': 0.001,
        'momentum': 0.9,
        'weight_decay': 1e-4,
        'step_size': 1,
        'gamma': 0.96,
        'epochs': 100,  # Full training (not 5 like h-m2)
        'batch_size': 128,
        'log_frequency': 10,  # Log every 10 steps
        'checkpoint_epochs': [10, 20, 30],  # Early prediction checkpoints
        'seeds': [42, 43, 44],
        'checkpoint_dir': './checkpoints/'
    }
    
    # Load Waterbirds dataset (reuse h-m2)
    sys.path.insert(0, str(Path('../h-m2/code')))
    from data.dataset import get_dataloaders
    
    loggers_all_seeds = []
    final_wga_all_seeds = []
    
    for seed in config['seeds']:
        print(f"\n{'='*60}")
        print(f"Running experiment with seed {seed}")
        print(f"{'='*60}\n")
        
        # Set seed
        torch.manual_seed(seed)
        
        # Load data
        dataloaders = get_dataloaders(
            data_dir='/home/anonymous/data/waterbirds_v1.0',
            batch_size=config['batch_size']
        )
        
        # Create model (ResNet-50)
        from models.model import get_resnet50
        model = get_resnet50(num_classes=2)
        
        # Compute Hessian eigenvectors AFTER epoch 0
        print("Computing real Hessian eigenvectors...")
        eigenvalues, eigenvectors = compute_real_hessian_eigenvectors(
            model, dataloaders['train'], num_eigenthings=50, device='cuda'
        )
        
        # Separate bulk (flat) vs outlier (sharp) subspaces
        outlier_evecs, bulk_evecs, bulk_edge = separate_bulk_outlier_subspaces(
            eigenvalues, eigenvectors, model, len(dataloaders['train'].dataset)
        )
        
        print(f"Hessian analysis: {len(outlier_evecs)} outlier, {len(bulk_evecs)} bulk eigenvectors")
        print(f"Marchenko-Pastur bulk edge: {bulk_edge:.4f}")
        
        # Create trajectory logger
        logger = TrajectoryLogger(model, outlier_evecs, bulk_evecs)
        
        # Train with trajectory logging
        print("Training with trajectory logging (100 epochs)...")
        training_history = train_with_trajectory_logging(
            model, dataloaders['train'], dataloaders['val'], 
            logger, config, device='cuda'
        )
        
        # Compute final worst-group accuracy
        final_wga = compute_worst_group_accuracy(model, dataloaders['test'], device='cuda')
        
        loggers_all_seeds.append(logger)
        final_wga_all_seeds.append(final_wga)
        
        print(f"Seed {seed} complete: Final WGA = {final_wga:.4f}")
    
    # Evaluate directional bias across seeds
    print("\n" + "="*60)
    print("GATE METRIC EVALUATION")
    print("="*60 + "\n")
    
    eval_results = evaluate_directional_bias(loggers_all_seeds)
    
    print(f"Overall Mean Directional Bias: {eval_results['overall_mean_bias']:.6f}")
    print(f"Std Across Seeds: {eval_results['std_across_seeds']:.6f}")
    print(f"p-value: {eval_results['p_value']:.4f}")
    print(f"Gate Pass (SHOULD_WORK): {eval_results['gate_pass']}")
    
    # Early prediction experiment
    checkpoint_paths = [f"./checkpoints/seed{seed}_epoch10.pth" for seed in config['seeds']]
    early_pred_results = compute_early_prediction_r2(
        checkpoint_paths, dataloaders['train'], final_wga_all_seeds
    )
    
    print(f"\nEarly Prediction R²: {early_pred_results['r2_score']:.4f}")
    print(f"Early Prediction Valid (R² > 0.1): {early_pred_results['early_prediction_valid']}")
    
    # Generate visualizations
    print("\nGenerating visualizations...")
    trajectories = [logger.get_trajectory() for logger in loggers_all_seeds]
    
    plot_gate_metric_comparison(eval_results, './figures/fig1_gate_metric.png')
    plot_directional_bias_over_time(trajectories, './figures/fig2_bias_over_time.png')
    plot_bulk_vs_outlier_alignment(trajectories[0], './figures/fig3_bulk_vs_outlier.png')
    
    print("All figures saved to ./figures/")
    
    # Save results
    save_results(eval_results, early_pred_results, './results/')
    
    return eval_results['gate_pass']

if __name__ == '__main__':
    gate_pass = main()
    sys.exit(0 if gate_pass else 1)
```

---

## File Structure

```
h-m3/
├── code/
│   ├── hessian_eigenvectors.py          # Real Hessian computation (NEW, FIX h-m2)
│   ├── trajectory_logger.py             # SGD trajectory logging (NEW)
│   ├── training.py                      # Training with logging (EXTENDED from h-m2)
│   ├── directional_bias.py              # Gate metric evaluation (NEW)
│   ├── visualize_trajectory.py          # Trajectory visualizations (NEW)
│   ├── run_h_m3_experiment.py           # Main execution script (NEW)
│   ├── config.yaml                      # Hyperparameters (YAML for FULL tier)
│   ├── data/
│   │   └── dataset.py                   # Dataset loading (REUSE h-m2)
│   ├── models/
│   │   └── model.py                     # ResNet-50 (REUSE h-m2)
│   └── requirements.txt                 # Dependencies (add pytorch-hessian-eigenthings)
├── checkpoints/                         # Model checkpoints for early prediction
│   ├── seed42_epoch10.pth
│   ├── seed42_epoch20.pth
│   └── ... (3 seeds × 4 checkpoints each)
├── results/                             # Analysis outputs
│   ├── directional_bias_results.json
│   ├── trajectory_logs_seed42.csv
│   └── early_prediction_results.json
└── figures/                             # Visualizations
    ├── fig1_gate_metric.png            (GATE METRIC - MANDATORY)
    ├── fig2_bias_over_time.png
    ├── fig3_bulk_vs_outlier.png
    ├── fig4_early_prediction.png
    └── fig5_eigenvalue_spectrum.png
```

**Note**: Full 100-epoch training required (not 5-epoch PoC like h-m2). Real Hessian eigenvectors critical (fix h-m2 random basis failure).

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| C-1 | Environment Setup | Install pytorch-hessian-eigenthings, verify h-m2 dataset | 5 | 1+1+2+1 |
| C-2 | Hessian Eigenvector Computation | Implement real Hessian computation (FIX h-m2) | 15 | 4+3+5+3 |
| C-3 | Marchenko-Pastur Subspace Separation | Separate bulk (flat) vs outlier (sharp) | 12 | 3+3+4+2 |
| C-4 | Trajectory Logger Implementation | Implement SGD trajectory logging class | 14 | 4+3+4+3 |
| C-5 | Training Loop Integration | Integrate logger into 100-epoch training | 13 | 3+3+4+3 |
| C-6 | Directional Bias Evaluation | Implement gate metric across 3 seeds | 11 | 3+2+4+2 |
| C-7 | Early Prediction Experiment | Checkpoint analysis and R² computation | 12 | 3+3+3+3 |
| C-8 | Trajectory Visualizations | Generate 5 figures (gate metric + analysis) | 11 | 3+2+4+2 |
| C-9 | Multi-Seed Execution | Run experiment for 3 seeds (42, 43, 44) | 10 | 2+2+4+2 |

**Total Epic Complexity**: 103  
**Distribution**: VeryHigh(18-20): [], High(14-17): [C-2, C-4], Medium(9-13): [C-3, C-5, C-6, C-7, C-8, C-9], Low(4-8): [C-1]

**Complexity Scoring** (Module + Dependencies + Algorithm + Integration):
- C-1: 1+1+2+1 = 5
- C-2: 4+3+5+3 = 15 (Critical fix from h-m2)
- C-3: 3+3+4+2 = 12
- C-4: 4+3+4+3 = 14
- C-5: 3+3+4+3 = 13
- C-6: 3+2+4+2 = 11
- C-7: 3+3+3+3 = 12
- C-8: 3+2+4+2 = 11
- C-9: 2+2+4+2 = 10

---

## Task Breakdown Details

### C-1: Environment Setup (Complexity: 5)

**Subtasks**:
1. Install pytorch-hessian-eigenthings library
2. Verify h-m2 dataset path exists (`/home/anonymous/data/waterbirds_v1.0`)
3. Create h-m3 directory structure (code, checkpoints, results, figures)
4. Verify GPU availability (select empty GPU)

**Deliverables**:
- pytorch-hessian-eigenthings installed
- Dataset verified
- Directory structure created
- GPU selected

---

### C-2: Hessian Eigenvector Computation (Complexity: 15)

**Subtasks**:
1. Implement `compute_real_hessian_eigenvectors()` function
2. Integrate pytorch-hessian-eigenthings library
3. Configure power iteration parameters (num_eigenthings=50, steps=20)
4. Test on small subset (verify no OOM)
5. Compute eigenvectors for full training set
6. Validate eigenvector shapes and orthogonality
7. **CRITICAL:** Verify eigenvectors are NOT random (h-m2 failure fix)

**Deliverables**:
- `hessian_eigenvectors.py` module
- Real Hessian eigenvectors (not random basis)
- Eigenvalues (50,) array
- Eigenvectors list (length 50)
- Validation tests passing

**Critical Fix**: This replaces h-m2's random orthonormal basis with real Hessian eigenvectors.

---

### C-3: Marchenko-Pastur Subspace Separation (Complexity: 12)

**Subtasks**:
1. Implement `separate_bulk_outlier_subspaces()` function
2. Estimate Marchenko-Pastur parameters (γ, σ²)
3. Compute bulk edge threshold
4. Separate eigenvectors into outlier (sharp) and bulk (flat) lists
5. Validate separation (outlier count reasonable, bulk count > 0)
6. Visualize eigenvalue spectrum with bulk edge

**Deliverables**:
- Outlier eigenvectors list (sharp directions)
- Bulk eigenvectors list (flat directions)
- Bulk edge threshold
- Spectrum visualization

---

### C-4: Trajectory Logger Implementation (Complexity: 14)

**Subtasks**:
1. Implement `TrajectoryLogger` class
2. Implement `log_step()` method (gradient capture)
3. Implement gradient flattening logic
4. Compute alignment to outlier subspace
5. Compute alignment to bulk subspace
6. Compute directional bias (bulk - outlier)
7. Implement `compute_statistics()` method
8. Unit tests for trajectory logger

**Deliverables**:
- `trajectory_logger.py` module
- TrajectoryLogger class
- Alignment computation validated
- Unit tests passing

---

### C-5: Training Loop Integration (Complexity: 13)

**Subtasks**:
1. Extend h-m2 training loop for 100 epochs (not 5)
2. Integrate TrajectoryLogger into training loop
3. Call `logger.log_step()` BEFORE optimizer.step()
4. Log every 10 steps (memory-efficient)
5. Save checkpoints at epochs 10, 20, 30
6. Monitor training progress (loss, accuracy)
7. Validate training completes without OOM

**Deliverables**:
- `training.py` module (extended from h-m2)
- 100-epoch training loop
- Trajectory logging integrated
- Checkpoints saved

---

### C-6: Directional Bias Evaluation (Complexity: 11)

**Subtasks**:
1. Implement `evaluate_directional_bias()` function
2. Aggregate trajectory statistics across 3 seeds
3. Perform one-sample t-test (mean_bias vs 0)
4. Compute p-value and effect size
5. Determine gate pass/fail (mean_bias > 0, p < 0.05)
6. Save evaluation results to JSON

**Deliverables**:
- `directional_bias.py` module
- Gate metric evaluation function
- Statistical test results
- Gate decision (SHOULD_WORK)

---

### C-7: Early Prediction Experiment (Complexity: 12)

**Subtasks**:
1. Load epoch 10 checkpoints for all 3 seeds
2. Compute A(w) at epoch 10 (minority-gradient alignment)
3. Collect final worst-group accuracies
4. Compute R² correlation
5. Validate R² > 0.1 (secondary metric)
6. Save early prediction results

**Deliverables**:
- Early prediction R² score
- Early A(w) values (3 seeds)
- Final WGA values (3 seeds)
- Validation of secondary metric

---

### C-8: Trajectory Visualizations (Complexity: 11)

**Subtasks**:
1. Implement `plot_gate_metric_comparison()` (MANDATORY)
2. Implement `plot_directional_bias_over_time()` (3 seeds + mean)
3. Implement `plot_bulk_vs_outlier_alignment()` (trajectory comparison)
4. Implement early prediction scatter plot
5. Implement eigenvalue spectrum with bulk edge
6. Generate all 5 figures and save to `figures/`

**Deliverables**:
- `visualize_trajectory.py` module
- 5 figures in `figures/` directory
- Figure 1 (gate metric) clearly labeled

---

### C-9: Multi-Seed Execution (Complexity: 10)

**Subtasks**:
1. Implement seed loop in main script
2. Run experiment for seed 42
3. Run experiment for seed 43
4. Run experiment for seed 44
5. Aggregate results across seeds
6. Verify consistency (all 3 runs complete)
7. Save aggregated results

**Deliverables**:
- Results for all 3 seeds
- Aggregated statistics
- Consistency validation
- All runs completed successfully

---

## Integration with h-m2

**Critical Differences from h-m2:**

1. **Hessian Eigenvectors**: h-m2 used random orthonormal basis (FAILED, all alignments ~1e-06). h-m3 uses REAL Hessian eigenvectors from pytorch-hessian-eigenthings.
2. **Training Duration**: h-m2 used 5 epochs (PoC). h-m3 uses 100 epochs (full training for trajectory analysis).
3. **Trajectory Logging**: h-m2 had no trajectory logging. h-m3 logs gradient alignment at every 10th step.
4. **Gate Metric**: h-m2 measured static alignment. h-m3 measures dynamic directional bias during training.

**Reused Components from h-m2:**
- Dataset loading (Waterbirds)
- Model architecture (ResNet-50)
- Training hyperparameters (SGD, LR, schedule)
- Group-wise evaluation logic

**Verification Strategy:**
- Hessian eigenvectors → Verify NOT random (h-m2 fix)
- Trajectory logging → Verify alignment values NOT near-zero (h-m2 fix)
- 100 epochs → Full training completes without OOM
- Gate metric → Statistical test across 3 seeds

---

## Configuration Schema

```yaml
# h-m3 Configuration (YAML for FULL tier)

project:
  hypothesis_id: h-m3
  hypothesis_type: MECHANISM
  tier: FULL
  base_hypothesis: h-m2
  gate_type: SHOULD_WORK

paths:
  data_dir: /home/anonymous/data/waterbirds_v1.0
  checkpoint_dir: ./checkpoints/
  results_dir: ./results/
  figures_dir: ./figures/

training:
  epochs: 100  # Full training (not 5 like h-m2)
  batch_size: 128
  lr: 0.001
  momentum: 0.9
  weight_decay: 0.0001
  step_size: 1
  gamma: 0.96
  seeds: [42, 43, 44]
  log_frequency: 10  # Log every 10 steps
  checkpoint_epochs: [10, 20, 30]

hessian:
  num_eigenthings: 50
  mode: power_iter
  power_iter_steps: 20
  use_random_basis: false  # CRITICAL: must be false (h-m2 fix)

trajectory:
  log_gradients: true
  compute_bulk_alignment: true
  compute_outlier_alignment: true
  save_full_trajectory: true

gate_metric:
  metric_name: mean_directional_bias
  threshold: 0.0
  statistical_test: one_sample_ttest
  alpha: 0.05
  min_seeds: 3
```

---

*Architecture designed for Phase 4 Implementation | h-m3 MECHANISM Hypothesis | Fixes h-m2 random basis limitation with real Hessian eigenvectors*
