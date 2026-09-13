# Product Requirements Document: h-c1 Gradient-Aware Training

**Hypothesis:** Gradient-aware training (lr_j = lr_base * (1 - ρ_j)) matches or exceeds JTT worst-group accuracy on Waterbirds (within 1%)

**Type:** CONDITION  
**Prerequisites:** h-m1 (ρ_j values from feature complexity mechanism)  
**Date:** 2026-08-29

---

## Executive Summary

Implement gradient-aware learning rate modulation mechanism to validate whether per-neuron spurious correlation can be leveraged for practical debiasing. System modulates learning rates based on ρ_j values from h-m1, targeting JTT-level worst-group accuracy (≥86%) on Waterbirds benchmark.

**Success Criterion:** Statistical Test 9 - paired t-test across 10 seeds showing mean(Gradient-Aware) ≥ mean(JTT) - 1% with p < 0.05.

---

## Problem Statement

### Context
H-m1 validated feature complexity mechanism (early layers learn spurious features faster). h-c1 tests whether this insight enables practical intervention via gradient-aware learning rate modulation.

### Objective
Implement and evaluate gradient-aware training that suppresses spurious feature learning by reducing learning rates for high-ρ_j neurons, achieving competitive worst-group accuracy vs JTT baseline.

---

## Functional Requirements

### FR-1: Dataset Loading
**Description:** Load Waterbirds dataset with group labels for worst-group accuracy computation.

**Specifications:**
- Dataset: Waterbirds (Sagawa et al. 2020)
- Splits: 4795 train, 1199 val, 5794 test
- Groups: 4 (landbird/waterbird × land/water background)
- Preprocessing: Resize(256) → CenterCrop(224) → ImageNet normalization
- Augmentation: Random horizontal flip (train only)

**Source:** https://github.com/kohpangwei/group_DRO

### FR-2: Baseline Models
**Description:** Implement three baseline training methods for comparison.

**FR-2.1: ERM (Empirical Risk Minimization)**
- Standard ResNet-50 training without debiasing
- Expected worst-group accuracy: ~72%

**FR-2.2: JTT (Just Train Twice)**
- Two-stage training:
  - Stage 1: 100 epochs standard ERM
  - Stage 2: 200 epochs with upweighted misclassified examples
- Expected worst-group accuracy: ~86-89%
- Configuration: SGD(lr=1e-3, momentum=0.9), cosine decay, batch 128

**FR-2.3: Layer-wise Regularization**
- Penalize early-layer representations to reduce spurious feature reliance
- Expected worst-group accuracy: ~80-84%

### FR-3: Proposed Model - Gradient-Aware Training
**Description:** Implement gradient-aware learning rate modulation based on neuron-spurious correlation.

**Core Mechanism:**
```python
class GradientAwareOptimizer:
    """Modulate per-neuron learning rates based on ρ_j from h-m1."""
    
    def __init__(self, base_optimizer, rho_j_dict, base_lr=1e-3):
        self.optimizer = base_optimizer
        self.rho_j = rho_j_dict  # From h-m1 validation results
        self.base_lr = base_lr
    
    def step(self):
        for param_group in self.optimizer.param_groups:
            param_name = param_group['name']
            rho = self.rho_j.get(param_name, 0.0)
            
            # Core formula: suppress high-ρ_j (spurious) neurons
            modulated_lr = self.base_lr * (1 - rho)
            param_group['lr'] = max(modulated_lr, 1e-5)  # Floor
        
        self.optimizer.step()
```

**Specifications:**
- Base model: ResNet-50 (torchvision, pretrained on ImageNet)
- Optimizer: SGD wrapped by GradientAwareOptimizer
- Base learning rate: 1e-3
- Schedule: Cosine decay over 300 epochs
- ρ_j source: h-m1 validation results (layer-wise spurious correlation)
- ρ_j update frequency: Every 10 epochs (track changing correlations)

### FR-4: Training Protocol
**Description:** Unified training configuration across all methods.

**Specifications:**
- Optimizer: SGD (momentum=0.9, weight_decay=1e-4)
- Learning rate: 1e-3 with cosine annealing
- Batch size: 128
- Epochs: 300
- Seeds: 10 random seeds for statistical validation
- Loss: Cross-entropy

### FR-5: Evaluation Metrics
**Description:** Compute worst-group accuracy and supporting metrics.

**FR-5.1: Primary Metric - Worst-Group Accuracy**
```python
def worst_group_accuracy(preds, labels, groups):
    """Min accuracy over 4 groups."""
    group_accs = []
    for g in range(4):
        mask = (groups == g)
        if mask.sum() > 0:
            acc = (preds[mask] == labels[mask]).float().mean()
            group_accs.append(acc)
    return min(group_accs)
```

**FR-5.2: Secondary Metrics**
- Average accuracy (all test samples)
- Per-group accuracy (4 groups individually)
- Worst-group loss

### FR-6: Statistical Validation
**Description:** Statistical Test 9 from Phase 2B verification plan.

**Specifications:**
- Test: Paired t-test on worst-group accuracy across 10 seeds
- H0: mean(Gradient-Aware) < mean(JTT) - 1%
- Ha: mean(Gradient-Aware) ≥ mean(JTT) - 1%
- Significance: p < 0.05
- Pass condition: Non-inferiority demonstrated

### FR-7: Visualization
**Description:** Generate 4 required figures.

**FR-7.1: Gate Metrics Comparison (Mandatory)**
- Bar chart: Target (86%) vs actual worst-group accuracy

**FR-7.2: Learning Rate Modulation Heatmap**
- Visualize per-layer ρ_j values and resulting learning rates

**FR-7.3: Training Curves**
- Worst-group accuracy over epochs (ERM, JTT, Gradient-Aware)

**FR-7.4: Per-Group Accuracy Bars**
- Final test accuracy for all 4 groups (3 methods)

---

## Non-Functional Requirements

### NFR-1: Performance
- Training time: ≤48 hours per method per seed on single GPU
- Memory: ≤16GB GPU memory (ResNet-50 batch 128)

### NFR-2: Reproducibility
- Fixed random seeds for each run (0-9)
- Deterministic training (torch.backends.cudnn.deterministic=True)
- Checkpoint saving: Best validation worst-group accuracy

### NFR-3: Code Quality
- Type hints for all function signatures
- Docstrings for core mechanism (GradientAwareOptimizer)
- Logging: Epoch-level metrics (train loss, val worst-group accuracy)

### NFR-4: Experiment Tracking
- Log hyperparameters: lr, batch size, epochs, seed
- Save results: CSV with per-seed worst-group accuracy for all methods
- Checkpoint: Best model based on validation worst-group accuracy

---

## Dependencies

### Technical Dependencies
- PyTorch ≥2.0
- torchvision (ResNet-50, transforms)
- NumPy, Pandas (data handling)
- Matplotlib/Seaborn (visualization)

### Data Dependencies
- Waterbirds dataset (download from kohpangwei/group_DRO)
- Group labels file for 4-group worst-group accuracy

### Prerequisite Dependencies
- **h-m1 validation results:** ρ_j values (neuron-spurious correlation)
  - Source: h-m1/04_validation.md
  - Required fields: Layer-wise ρ_j values from ablation training
  - Used for: GradientAwareOptimizer learning rate modulation

---

## Success Criteria

### Gate Condition (SHOULD_WORK)
Statistical Test 9 passes:
- mean(Gradient-Aware worst-group accuracy) ≥ mean(JTT worst-group accuracy) - 1%
- p < 0.05 (paired t-test across 10 seeds)

**Target:** ≥86% worst-group accuracy (JTT baseline ~87%)

### Minimum Viable Success
- Code runs without error
- Gradient-Aware worst-group accuracy > ERM baseline (~72%)

### Deliverables
1. 03_prd.md (this document)
2. 03_architecture.md (system design, Epic tasks)
3. 03_logic.md (API signatures, tensor shapes)
4. 03_config.md (hyperparameter schemas)
5. Working code passing validation
6. 04_validation.md with statistical test results
7. 4 figures in h-c1/figures/

---

## Out of Scope

- Other debiasing methods beyond ERM, JTT, Layer-wise Regularization
- Other datasets (h-c1 targets Waterbirds only)
- Architecture search (ResNet-50 fixed)
- Hyperparameter tuning beyond Phase 2C specifications
- Deployment or production integration

---

## Assumptions

1. h-m1 ρ_j values transfer to Waterbirds (different dataset from h-m1's CMNIST)
2. ρ_j stability: Correlations remain consistent enough for 10-epoch update frequency
3. JTT baseline results from literature are reproducible (~87% worst-group)
4. GPU availability for 30 training runs (3 methods × 10 seeds)

---

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| ρ_j values don't transfer to Waterbirds | High | Compute ρ_j on Waterbirds if h-m1 values fail |
| Gradient-aware training unstable | Medium | Add learning rate floor (1e-5), gradient clipping |
| JTT baseline lower than literature | Medium | Document actual baseline, adjust target threshold |
| Training time exceeds budget | Low | Reduce seeds from 10 to 5 if necessary |

---

## Phase 2C Traceability

| Phase 2C Element | PRD Section |
|------------------|-------------|
| Dataset: Waterbirds | FR-1 |
| Baseline: ERM | FR-2.1 |
| Baseline: JTT | FR-2.2 |
| Baseline: Layer-wise Regularization | FR-2.3 |
| Proposed: Gradient-Aware | FR-3 |
| Training protocol | FR-4 |
| Evaluation: Worst-group accuracy | FR-5.1 |
| Statistical Test 9 | FR-6 |
| Visualizations | FR-7 |
| ρ_j dependency on h-m1 | Dependencies |

---

**Approval Status:** Draft  
**Next Phase:** Architecture Design (Step 3)
