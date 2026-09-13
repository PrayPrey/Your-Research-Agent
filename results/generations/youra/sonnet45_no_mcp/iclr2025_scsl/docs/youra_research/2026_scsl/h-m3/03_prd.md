# Product Requirements Document: h-m3 SGD Trajectory Directional Bias

**Hypothesis ID:** h-m3  
**Type:** MECHANISM (Step 3 of 4)  
**Date:** 2026-04-24  
**Author:** Anonymous
**Source:** Phase 2C Experiment Brief (02c_experiment_brief.md)  
**Prerequisites:** h-m2 (COMPLETED ✅)

---

## Executive Summary

This PRD defines the implementation requirements for validating the third mechanism hypothesis in the causal chain: that SGD dynamics preferentially follow locally flat directions to minimize curvature-induced gradient variance. Building on h-m2's validated minority-gradient alignment to sharp directions, we will track SGD trajectories during training to measure directional bias toward bulk (flat) vs outlier (sharp) subspaces.

**Key Objectives:**
1. Train ResNet-50 on Waterbirds with full 100-epoch protocol (not 5-epoch PoC)
2. Compute real Hessian eigenvectors using pytorch-hessian-eigenthings (fix h-m2 random basis limitation)
3. Log SGD trajectory alignment to bulk (flat) vs outlier (sharp) directions during training
4. Measure directional bias: bulk_alignment - outlier_alignment
5. Validate MECHANISM: SGD prefers flat directions (positive directional bias across training)

**Gate Type:** SHOULD_WORK (mechanism validation - document limitation if fails, continue pipeline)

**Critical Fix from h-m2:** h-m2 used random orthonormal basis and all alignments collapsed to ~1e-06. h-m3 MUST use real Hessian eigenvectors to measure meaningful directional preferences.

---

## Problem Statement

### Research Question
During training, does SGD preferentially follow locally flat directions (Hessian bulk subspace) to minimize curvature-induced gradient variance?

### Hypothesis Statement
During training, if sharp curvature exists in specific directions (H-M2), then SGD dynamics will preferentially follow locally flat directions to minimize curvature-induced gradient variance, because well-documented SGD implicit bias toward flat minima creates directional flow.

### Success Impact
If validated, this provides:
- Evidence that SGD trajectory exhibits geometric bias toward flatness
- Mechanistic explanation for why ERM solutions land in sharp regions (avoid sharp, stay flat)
- Foundation for h-m4 (functional coupling between geometry and robustness)

### Failure Impact
If directional_bias ≤ 0: SGD flatness hypothesis not validated. Document as limitation per SHOULD_WORK protocol. Pipeline continues.

---

## Functional Requirements

### FR-1: Dataset Preparation (Reused from h-m2)
**Priority:** CRITICAL  
**Description:** Use same Waterbirds dataset as h-m2

**Acceptance Criteria:**
- Reuse Waterbirds from h-m2: `/home/anonymous/data/waterbirds_v1.0` (already verified)
- Same preprocessing: resize 224×224, ImageNet normalization
- Same splits: train (4,795), val (1,199), test (5,794)
- Training augmentation: RandomHorizontalFlip (same as h-m2)
- No changes to data pipeline - exact replication for controlled comparison

**Technical Specifications:**
```python
# Reuse from h-m2 data loading
import torchvision.transforms as transforms
from datasets.waterbirds import WaterbirdsDataset

transform_train = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.RandomHorizontalFlip(),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                        std=[0.229, 0.224, 0.225])
])

train_dataset = WaterbirdsDataset(
    basedir='/home/anonymous/data/waterbirds_v1.0',
    split='train',
    transform=transform_train
)
```

**Dependencies:** PyTorch, torchvision, Waterbirds dataset (already exists)

**Reuse from h-m2:**
- Dataset: Waterbirds (same location)
- Preprocessing: Same transforms
- Data loading logic: Reuse h-m2 configuration

---

### FR-2: Model Architecture (Reused from h-m2)
**Priority:** CRITICAL  
**Description:** Use same ResNet-50 architecture as h-m2

**Acceptance Criteria:**
- ResNet-50 with ImageNet pretrained weights
- Modified final FC layer: 2048 → 2 classes (landbird, waterbird)
- Add backward hooks for gradient capture during training
- No architectural changes to core layers (preserves loss landscape structure)

**Technical Specifications:**
```python
import torchvision.models as models
import torch.nn as nn

# Load pretrained ResNet-50 (same as h-m2)
model = models.resnet50(pretrained=True)

# Modify final layer for 2-class classification
num_classes = 2
model.fc = nn.Linear(model.fc.in_features, num_classes)
```

**Dependencies:** PyTorch, torchvision

**Reuse from h-m2:**
- Architecture: ResNet-50
- Pretrained weights: ImageNet
- Output modification: 2 classes

---

### FR-3: Hessian Eigenvector Computation (NEW - Fix h-m2 Limitation)
**Priority:** CRITICAL  
**Description:** Compute REAL Hessian eigenvectors using pytorch-hessian-eigenthings

**Acceptance Criteria:**
- Compute top-50 Hessian eigenvalues and eigenvectors after epoch 0 (initial model)
- Use power iteration method (memory-efficient, O(kp) not O(p²))
- Store eigenvectors for trajectory logging
- Separate outlier (sharp) vs bulk (flat) using Marchenko-Pastur bulk edge
- **CRITICAL:** NO random orthonormal basis (h-m2 failure mode)

**Technical Specifications:**
```python
from hessian_eigenthings import compute_hessian_eigenthings
import numpy as np

def compute_hessian_eigenvectors(model, train_loader, num_eigenthings=50):
    """
    Compute real Hessian eigenvectors (FIX h-m2 random basis limitation)
    
    Args:
        model: ResNet-50 model (after epoch 0)
        train_loader: Training data loader
        num_eigenthings: Number of top eigenvectors (50 for h-m3)
    
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
        use_gpu=True
    )
    
    return eigenvalues, eigenvectors

def separate_subspaces(eigenvalues, eigenvectors):
    """
    Separate outlier (sharp) vs bulk (flat) subspaces using Marchenko-Pastur
    
    Returns:
        outlier_evecs: List[Tensor] - sharp direction eigenvectors
        bulk_evecs: List[Tensor] - flat direction eigenvectors
        bulk_edge: float - Marchenko-Pastur threshold
    """
    # Estimate Marchenko-Pastur parameters
    p = sum(p.numel() for p in model.parameters())
    n = len(train_loader.dataset)
    gamma = p / n
    sigma_sq = 1.0  # Estimate from small eigenvalues
    
    # Compute bulk edge
    bulk_edge = sigma_sq * (1 + np.sqrt(gamma)) ** 2
    
    # Separate subspaces
    outlier_mask = eigenvalues > bulk_edge
    outlier_evecs = [eigenvectors[i] for i in range(len(eigenvalues)) if outlier_mask[i]]
    bulk_evecs = [eigenvectors[i] for i in range(len(eigenvalues)) if not outlier_mask[i]]
    
    return outlier_evecs, bulk_evecs, bulk_edge
```

**Dependencies:** pytorch-hessian-eigenthings, PyTorch, NumPy

**NEW Implementation:** Real Hessian eigenvectors (not random basis)

---

### FR-4: SGD Trajectory Logger (NEW for h-m3)
**Priority:** CRITICAL  
**Description:** Log gradient alignment to bulk (flat) vs outlier (sharp) subspaces during training

**Acceptance Criteria:**
- Register backward hook to capture gradients during training
- Compute gradient alignment to outlier (sharp) eigenvectors
- Compute gradient alignment to bulk (flat) eigenvectors
- Log every 10 steps (memory-efficient, not every step)
- Save directional bias (bulk_alignment - outlier_alignment) per step
- Track trajectory over full 100 epochs

**Technical Specifications:**
```python
class TrajectoryLogger:
    """
    Logs SGD trajectory alignment to Hessian eigenvector subspaces.
    Measures directional bias: bulk (flat) vs outlier (sharp) alignment.
    """
    def __init__(self, model, outlier_evecs, bulk_evecs):
        self.model = model
        self.outlier_evecs = outlier_evecs  # Sharp directions
        self.bulk_evecs = bulk_evecs        # Flat directions
        self.trajectory = []
        
    def log_step(self, epoch, step, loss):
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
            evec_flat = torch.cat([v.view(-1) for v in evec]) if isinstance(evec, list) else evec.view(-1)
            alignment = (grad_vector @ evec_flat) ** 2 / grad_norm_sq
            outlier_alignments.append(alignment.item())
        outlier_align = np.mean(outlier_alignments) if outlier_alignments else 0.0
        
        # Compute alignment to bulk (flat) directions
        bulk_alignments = []
        for evec in self.bulk_evecs:
            evec_flat = torch.cat([v.view(-1) for v in evec]) if isinstance(evec, list) else evec.view(-1)
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
    
    def compute_statistics(self):
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
```

**Dependencies:** PyTorch, NumPy

**NEW Implementation:** Trajectory logging with directional bias measurement

---

### FR-5: Training Protocol (Extended from h-m2)
**Priority:** CRITICAL  
**Description:** Train ResNet-50 with full 100-epoch protocol (not 5-epoch PoC like h-m2)

**Acceptance Criteria:**
- Optimizer: SGD with momentum=0.9, weight_decay=1e-4
- Learning rate: 0.001 (fine-tuning from ImageNet pretrained)
- Schedule: StepLR with step_size=1, gamma=0.96 (decay every epoch)
- Batch size: 128
- **Epochs: 100** (full training, not 5-epoch PoC)
- Loss: CrossEntropyLoss
- Seeds: 3 (verify trajectory consistency across runs)
- Checkpoint saving: epochs 10, 20, 30 (for early prediction experiment)

**Technical Specifications:**
```python
import torch.optim as optim

optimizer = optim.SGD(model.parameters(), 
                      lr=0.001, momentum=0.9, weight_decay=1e-4)
scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=1, gamma=0.96)
criterion = nn.CrossEntropyLoss()

# Training loop with trajectory logging
logger = TrajectoryLogger(model, outlier_evecs, bulk_evecs)

for epoch in range(100):  # Full 100 epochs (not 5 like h-m2)
    for step, (inputs, targets, groups) in enumerate(train_loader):
        # Forward pass
        outputs = model(inputs)
        loss = criterion(outputs, targets)
        
        # Backward pass
        optimizer.zero_grad()
        loss.backward()
        
        # Log trajectory BEFORE optimizer.step()
        if step % 10 == 0:  # Log every 10 steps (memory-efficient)
            logger.log_step(epoch, step, loss.item())
        
        # Update parameters
        optimizer.step()
    
    scheduler.step()
    
    # Save checkpoints for early prediction
    if epoch in [10, 20, 30]:
        save_checkpoint(model, epoch)
```

**Dependencies:** PyTorch

**Extended from h-m2:**
- Same hyperparameters (SGD, LR, batch size)
- **CRITICAL:** 100 epochs (not 5) - trajectory analysis requires full training
- Add trajectory logging hooks

---

### FR-6: Directional Bias Evaluation (NEW for h-m3)
**Priority:** CRITICAL  
**Description:** Evaluate primary gate metric: directional bias

**Acceptance Criteria:**
- Compute mean directional bias over full training trajectory
- **Primary Gate Metric:** mean_directional_bias > 0 (SGD prefers flat directions)
- Statistical validation: paired t-test across 3 seeds (p < 0.05)
- Visualization: directional bias over training epochs

**Technical Specifications:**
```python
def evaluate_directional_bias(logger_seed1, logger_seed2, logger_seed3):
    """
    Evaluate gate metric: directional bias across seeds
    
    Returns:
        gate_result: bool - True if mean_bias > 0 across all seeds (p < 0.05)
        metrics: dict - all statistics
    """
    stats1 = logger_seed1.compute_statistics()
    stats2 = logger_seed2.compute_statistics()
    stats3 = logger_seed3.compute_statistics()
    
    mean_biases = [
        stats1['mean_directional_bias'],
        stats2['mean_directional_bias'],
        stats3['mean_directional_bias']
    ]
    
    # Statistical test: mean > 0 across seeds
    from scipy.stats import ttest_1samp
    t_stat, p_value = ttest_1samp(mean_biases, 0.0)
    
    gate_pass = (np.mean(mean_biases) > 0) and (p_value < 0.05)
    
    return gate_pass, {
        'mean_directional_bias_seed1': stats1['mean_directional_bias'],
        'mean_directional_bias_seed2': stats2['mean_directional_bias'],
        'mean_directional_bias_seed3': stats3['mean_directional_bias'],
        'overall_mean_bias': np.mean(mean_biases),
        'std_across_seeds': np.std(mean_biases),
        'p_value': p_value,
        'gate_pass': gate_pass
    }
```

**Dependencies:** NumPy, SciPy

**NEW Implementation:** Gate metric evaluation

---

### FR-7: Early Prediction Experiment (SECONDARY)
**Priority:** MEDIUM  
**Description:** Test if early A(w) (at 10% training) predicts final worst-group accuracy

**Acceptance Criteria:**
- Save checkpoints at epochs 10, 20, 30 (10%, 20%, 30% of training)
- Compute A(w) at each checkpoint (minority-gradient alignment to outlier subspace)
- Correlate early A(w) with final worst-group accuracy
- **Secondary Metric:** R² > 0.1 (incremental explanatory power)

**Technical Specifications:**
```python
def compute_early_prediction_r2(checkpoint_Aw_values, final_wga_values):
    """
    Compute R² between early A(w) and final worst-group accuracy
    
    Args:
        checkpoint_Aw_values: List[float] - A(w) at epoch 10 for each seed
        final_wga_values: List[float] - Final worst-group accuracy for each seed
    
    Returns:
        r2_score: float - R² correlation
    """
    from sklearn.metrics import r2_score
    return r2_score(final_wga_values, checkpoint_Aw_values)
```

**Dependencies:** scikit-learn

**NEW Implementation:** Early prediction correlation analysis

---

### FR-8: Evaluation Metrics (Standard + h-m3 Specific)
**Priority:** HIGH  
**Description:** Compute standard robustness metrics + directional bias

**Acceptance Criteria:**
- Overall accuracy on test set
- Worst-group accuracy (4 groups)
- Per-group accuracy
- **h-m3 PRIMARY:** Directional bias (bulk - outlier alignment)
- **h-m3 SECONDARY:** Early prediction R²

**Technical Specifications:**
```python
import torchmetrics

def compute_group_accuracy(outputs, targets, groups):
    """Compute per-group and worst-group accuracy"""
    group_accs = []
    for g in range(4):
        mask = (groups == g)
        if mask.sum() > 0:
            preds = outputs[mask].argmax(dim=1)
            acc = (preds == targets[mask]).float().mean().item()
            group_accs.append(acc)
    
    worst_group_acc = min(group_accs)
    avg_acc = np.mean(group_accs)
    return worst_group_acc, avg_acc, group_accs
```

**Dependencies:** torchmetrics, NumPy

**Reuse from h-m2:** Group-wise accuracy computation

---

### FR-9: Visualization Generation (NEW for h-m3)
**Priority:** HIGH  
**Description:** Generate trajectory analysis figures

**Acceptance Criteria:**
- **Figure 1:** Gate Metrics Comparison (directional bias bar chart) **[MANDATORY]**
- **Figure 2:** Directional Bias Over Training (3 seeds, mean ± std)
- **Figure 3:** Bulk vs Outlier Alignment Trajectories (separate lines)
- **Figure 4:** Early Prediction Scatter Plot (early A(w) vs final WGA)
- **Figure 5:** Hessian Eigenvalue Spectrum (with MP bulk edge)
- Save all figures to `{hypothesis_folder}/figures/`

**Technical Specifications:**
```python
import matplotlib.pyplot as plt

def plot_directional_bias_over_time(trajectories_seed1, trajectories_seed2, trajectories_seed3, save_path):
    """Plot directional bias over training epochs"""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Extract bias over epochs for each seed
    epochs1 = [t['epoch'] for t in trajectories_seed1]
    biases1 = [t['directional_bias'] for t in trajectories_seed1]
    
    epochs2 = [t['epoch'] for t in trajectories_seed2]
    biases2 = [t['directional_bias'] for t in trajectories_seed2]
    
    epochs3 = [t['epoch'] for t in trajectories_seed3]
    biases3 = [t['directional_bias'] for t in trajectories_seed3]
    
    # Plot individual seeds
    ax.plot(epochs1, biases1, alpha=0.3, color='blue', label='Seed 1')
    ax.plot(epochs2, biases2, alpha=0.3, color='green', label='Seed 2')
    ax.plot(epochs3, biases3, alpha=0.3, color='red', label='Seed 3')
    
    # Compute mean and std across seeds
    # (assuming synchronized epoch sampling)
    mean_bias = np.mean([biases1, biases2, biases3], axis=0)
    std_bias = np.std([biases1, biases2, biases3], axis=0)
    
    # Plot mean with std shading
    ax.plot(epochs1, mean_bias, linewidth=2, color='black', label='Mean')
    ax.fill_between(epochs1, mean_bias - std_bias, mean_bias + std_bias, 
                     alpha=0.2, color='black', label='±1 std')
    
    # Horizontal line at y=0 (preference threshold)
    ax.axhline(y=0, color='red', linestyle='--', linewidth=1.5, label='Threshold (bias=0)')
    
    ax.set_xlabel('Training Epoch')
    ax.set_ylabel('Directional Bias (bulk - outlier)')
    ax.set_title('SGD Directional Bias Over Training')
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()

def plot_bulk_vs_outlier_alignment(trajectory, save_path):
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
```

**Dependencies:** matplotlib, NumPy

**NEW Implementation:** Trajectory visualization

---

## Non-Functional Requirements

### NFR-1: Reproducibility
**Priority:** CRITICAL  
**Description:** Ensure experiment reproducibility

**Requirements:**
- Fixed seeds: 42, 43, 44 (3 seeds for statistical validation)
- Log all hyperparameters to config file (hardcoded or argparse for FULL tier)
- Save model checkpoints: epochs 10, 20, 30, final
- Save trajectory logs: CSV with epoch, step, bulk_align, outlier_align, bias
- Save Hessian eigenvectors for reuse
- Document exact package versions

---

### NFR-2: Performance
**Priority:** MEDIUM  
**Description:** Efficient execution on single GPU

**Requirements:**
- Single GPU execution (set CUDA_VISIBLE_DEVICES to empty GPU)
- Batch size: 128 (fits in typical GPU memory for ResNet-50)
- Training time: ~8-10 hours per seed × 3 seeds (100 epochs each)
- Hessian computation: ~1-2 hours (50 eigenthings, one-time after epoch 0)
- Memory usage: ≤ 12GB GPU RAM
- Trajectory logging: Memory-efficient (log every 10 steps, not every step)

---

### NFR-3: Logging and Monitoring
**Priority:** MEDIUM  
**Description:** Track training progress and trajectory metrics

**Requirements:**
- CSV logging for trajectory: epoch, step, loss, bulk_alignment, outlier_alignment, directional_bias
- Save checkpoint metrics: epoch, worst_group_acc, avg_acc
- Save final statistics: mean_directional_bias, std, p_value
- Print progress: every 10 epochs

**Technical Specifications:**
```python
import csv

def log_trajectory_to_csv(trajectory, log_file='trajectory_log.csv'):
    """Save trajectory to CSV"""
    with open(log_file, 'w', newline='') as f:
        fieldnames = ['epoch', 'step', 'loss', 'bulk_alignment', 'outlier_alignment', 'directional_bias']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(trajectory)
```

---

### NFR-4: Code Quality
**Priority:** MEDIUM  
**Description:** Clean, readable code with basic testing

**Requirements:**
- Smoke test: Run 1 epoch on small subset (100 samples) to verify no crashes
- Modular structure: separate files for data, model, training, hessian, trajectory logging
- Inline comments for trajectory logger logic
- YAML config file for hyperparameters (FULL tier - no hardcoded configs)

---

## Dependencies and Environment

### Software Dependencies
```
python >= 3.8
torch >= 1.10.0
torchvision >= 0.11.0
numpy >= 1.21.0
scipy >= 1.7.0
matplotlib >= 3.4.0
scikit-learn >= 0.24.0
pytorch-hessian-eigenthings
pyyaml >= 5.4.0
```

### Hardware Requirements
- GPU: NVIDIA GPU with ≥ 12GB VRAM (for ResNet-50 + trajectory logging)
- CPU: Any modern multi-core processor
- RAM: ≥ 16GB
- Storage: ≥ 20GB for dataset, checkpoints, trajectory logs

### Environment Setup
```bash
# Create conda environment
conda create -n h-m3 python=3.8
conda activate h-m3

# Install PyTorch with CUDA
conda install pytorch torchvision cudatoolkit=11.3 -c pytorch

# Install other dependencies
pip install numpy scipy matplotlib scikit-learn pyyaml
pip install git+https://github.com/noahgolmant/pytorch-hessian-eigenthings.git

# Set GPU (use nvidia-smi to find empty GPU)
export CUDA_VISIBLE_DEVICES=1  # Example: GPU 1 is empty
```

---

## Success Criteria

### Primary Success Criteria (SHOULD_WORK Gate)
1. **mean_directional_bias > 0** across all 3 seeds (p < 0.05)
   - Expected: positive bias indicates SGD prefers flat (bulk) directions
   - Statistical validation: one-sample t-test against 0

### Secondary Success Criteria
2. **Early Prediction R² > 0.1**: Early A(w) (epoch 10) correlates with final worst-group accuracy
3. **Code runs without error**: Training completes for all 3 seeds
4. **Trajectory logging stable**: No memory overflow, logging frequency maintains

### Gate Decision
- **PASS (SHOULD_WORK):** mean_directional_bias > 0 (p < 0.05) → Mechanism validated, proceed to h-m4
- **FAIL (SHOULD_WORK):** mean_directional_bias ≤ 0 → Document limitation, continue pipeline per SHOULD_WORK protocol

**Note:** SHOULD_WORK gate means failure is documented as limitation but does not block dependent hypotheses.

---

## Out of Scope

The following are explicitly out of scope for this experiment:

- SAM optimizer comparison (out of hypothesis scope)
- Multiple batch sizes (use 128 only, validated in h-m2)
- CelebA and Colored MNIST cross-validation (Waterbirds only for h-m3)
- Hyperparameter tuning / grid search
- Comparison with other optimization methods (Adam, RMSProp)
- Distributed training / multi-GPU
- Advanced Hessian approximations (KFAC, etc.)
- Full eigenspectrum (use top-50 only for efficiency)

---

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Hessian computation fails (OOM) | LOW | CRITICAL | Use top-50 eigenthings (not 100); test on small subset first |
| Trajectory logging memory overflow | MEDIUM | HIGH | Log every 10 steps (not every step); save to disk periodically |
| Directional bias near zero | MEDIUM | MEDIUM | Valid result - SGD flatness hypothesis not validated (SHOULD_WORK gate) |
| Random basis failure (like h-m2) | LOW | CRITICAL | Use pytorch-hessian-eigenthings (real eigenvectors), not random |
| Training instability with 100 epochs | LOW | MEDIUM | Use validated h-m2 hyperparameters; monitor loss curves |
| Early prediction R² < 0.1 | MEDIUM | LOW | Secondary metric - gate decision based on directional bias only |

---

## Appendix: Reference Information

### A. Phase 2C Source
This PRD is derived from: `{hypothesis_folder}/02c_experiment_brief.md`

Key sections referenced:
- Dataset specification (Waterbirds, reuse from h-m2)
- Model architecture (ResNet-50, reuse from h-m2)
- Training protocol (100 epochs, SGD configuration)
- Core mechanism (Hessian eigenvectors + trajectory logging)
- Evaluation metrics (directional bias, early prediction)
- Visualization requirements

### B. Theoretical Foundation

**SGD Flatness Bias (Foret et al. 2020):**
- SAM demonstrates SGD implicit bias toward flat minima
- Trajectory analysis reveals directional preferences
- Application: Measure bulk vs outlier alignment during training

**Loss Landscape Visualization (Li et al. 2018):**
- SGD trajectories show preference for valley floors (flat) over ridges (sharp)
- Filter normalization enables trajectory comparison
- Application: Directional bias visualization

**Hessian Eigenthings (Golmant et al.):**
- Power iteration provides memory-efficient eigenvector computation
- Real Hessian eigenvectors (not random basis)
- Application: Define bulk (flat) and outlier (sharp) subspaces

### C. Critical Lesson from h-m2

**h-m2 Failure Mode: Random Orthonormal Basis**
- h-m2 used random orthonormal basis instead of real Hessian eigenvectors
- All alignments collapsed to near-zero (~1e-06)
- Result: FAIL (SHOULD_WORK) - random basis does not capture curvature structure

**h-m3 Fix:**
- Use pytorch-hessian-eigenthings for REAL Hessian eigenvectors
- Validate eigenvectors capture loss landscape structure
- Expected: meaningful alignment values (not near-zero)

### D. Baseline Performance Expectations

From h-m2 validation report:
- Overall accuracy: ~97% (ERM without intervention)
- Worst-group accuracy: ~73% (minority groups)
- Group-wise evaluation validated

Expected h-m3 results:
- Directional bias: positive (SGD prefers flat directions)
- Bulk alignment: higher than outlier alignment on average
- Early prediction R²: > 0.1 (incremental explanatory power)

### E. Reuse Summary from h-m2

| Component | Reuse Status | Source |
|-----------|--------------|--------|
| Dataset | ✅ Full Reuse | h-m2 Waterbirds |
| Model Architecture | ✅ Full Reuse | h-m2 ResNet-50 |
| Hyperparameters | ✅ Full Reuse | h-m2 SGD config |
| Epochs | ❌ CHANGED | 5 → 100 (full training) |
| Hessian Computation | ❌ FIXED | Random basis → Real eigenvectors |
| Trajectory Logging | ❌ NEW | h-m3 specific |
| Directional Bias | ❌ NEW | h-m3 specific |
| Early Prediction | ❌ NEW | h-m3 specific |

---

*This PRD generated for Phase 3 Implementation Planning | Anonymous Research Pipeline | h-m3 MECHANISM Hypothesis*
