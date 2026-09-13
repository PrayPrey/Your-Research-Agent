# Product Requirements Document: H-E1

**Date:** 2026-03-26
**Author:** Anonymous
**Hypothesis ID:** H-E1
**Hypothesis Type:** EXISTENCE (FOUNDATION)
**Gate:** MUST_WORK
**Phase 2C Source:** 02c_experiment_brief.md

---

## Executive Summary

This PRD defines the implementation requirements for validating hypothesis H-E1: demonstrating that under finite-compute constraints (<=100 gradient-equivalent operations), at least one method pair among data attribution methods (TRAK, TracIn, IF, FastIF) exhibits statistically significant metric crossings. Specifically, one method may outperform another on rank preservation (rho_r) while underperforming on magnitude fidelity (rho_m), with non-overlapping 95% bootstrap confidence intervals at two or more compute levels.

**Objective:** Implement a proof-of-concept experiment comparing four data attribution methods on CIFAR-10/ResNet-18, computing Leave-One-Out (LOO) ground truth, and detecting Pareto trade-offs across quality metrics to validate the multi-objective framing of data attribution evaluation.

**Success Criteria:**
- Code runs without error for all 4 methods × 5 compute budgets × 3 seeds
- At least 1 method pair shows CI-separated metric crossings (e.g., TRAK > TracIn on rho_r but TRAK < TracIn on rho_m)
- Crossings appear at >=2 compute budget levels with non-overlapping 95% bootstrap CIs
- LOO ground truth computed successfully with R=10 retraining seeds

---

## Problem Statement

### Context
Data attribution methods assign influence scores to training examples, indicating how each example affected a model's predictions. Various methods exist (TRAK, TracIn, Influence Functions, FastIF), each with different computational profiles and approximation strategies. Practitioners must choose among these methods, but no principled framework exists for understanding trade-offs across different quality dimensions.

### Hypothesis
Under finite-compute constraints (<=100 gradient-equivalent operations), if we compare multiple data attribution methods across standardized quality dimensions (rank preservation, magnitude fidelity, stability), then non-degenerate Pareto trade-offs emerge where Method A > B on one metric but A < B on another, because different approximation strategies prioritize different aspects of the ground truth.

### Gap Being Addressed
Existing data attribution benchmarks focus on single metrics (typically LOO correlation). This experiment establishes whether multiple quality dimensions create Pareto trade-offs, validating the multi-objective optimization framing for data attribution method selection.

---

## Functional Requirements

### FR-1: Data Pipeline

**FR-1.1: Dataset Loading**
- Load CIFAR-10 from torchvision.datasets
- Identifier: `CIFAR10`
- Total: 60,000 images (50,000 train + 10,000 test)
- Subset for LOO feasibility: 5,000 training examples (randomly sampled, seed=42)
- Test subset for LOO: 100 test examples (for LOO retraining target)
- Full test set (10,000) for method evaluation

**FR-1.2: Preprocessing**
- Standard CIFAR-10 normalization:
  ```python
  transforms.Compose([
      transforms.ToTensor(),
      transforms.Normalize(mean=[0.4914, 0.4822, 0.4465],
                          std=[0.2470, 0.2435, 0.2616])
  ])
  ```
- No augmentation (for LOO consistency)

**FR-1.3: Data Loading**
```python
from torchvision.datasets import CIFAR10
from torch.utils.data import DataLoader, Subset
import numpy as np

train_dataset = CIFAR10(root='./data', train=True, download=True, transform=transform)
test_dataset = CIFAR10(root='./data', train=False, download=True, transform=transform)

# LOO-feasible subset
np.random.seed(42)
subset_indices = np.random.choice(len(train_dataset), size=5000, replace=False)
train_subset = Subset(train_dataset, subset_indices)

train_loader = DataLoader(train_subset, batch_size=128, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=256, shuffle=False)
```

### FR-2: Model Pipeline

**FR-2.1: Base Model - ResNet-18**
- Load from torchvision.models
- Identifier: `resnet18`
- Parameters: ~11M
- Modifications for CIFAR-10:
  ```python
  from torchvision.models import resnet18
  import torch.nn as nn

  model = resnet18(weights=None)  # Random init for fair LOO
  model.fc = nn.Linear(model.fc.in_features, 10)  # 10 CIFAR classes
  model.conv1 = nn.Conv2d(3, 64, kernel_size=3, stride=1, padding=1, bias=False)
  model.maxpool = nn.Identity()  # Remove maxpool for 32x32 images
  ```

**FR-2.2: Training Configuration**
- Optimizer: SGD with momentum=0.9, weight_decay=5e-4
- Learning rate: 0.1 with MultiStepLR(milestones=[100, 150], gamma=0.1)
- Batch size: 128
- Epochs: 200
- Loss: CrossEntropyLoss
- Seeds: 1 primary seed (42) for base model

**FR-2.3: LOO Retraining Protocol**
- For R=10 retraining seeds, train model from scratch
- For 100 test examples, compute LOO influence via retraining without each training example
- LOO influence = E_xi[L(z_test; theta^(-i)) - L(z_test; theta)]
- Store LOO ground truth as reference for method evaluation

### FR-3: Data Attribution Methods

**FR-3.1: TRAK (MadryLab/trak)**
- Install: `pip install traker[fast]`
- Random projection-based attribution using Neural Tangent Kernel approximation
- Configuration: 3-5 checkpoints, CUDA acceleration
- Compute budgets: Map to projection dimensions
```python
from trak import TRAKer

traker = TRAKer(model=model, task='image_classification', train_set_size=5000)
traker.load_checkpoint(checkpoint, model_id=0)
for batch in train_loader:
    traker.featurize(batch=batch, num_samples=batch[0].shape[0])
traker.finalize_features()
scores = traker.finalize_scores(exp_name='test')
```

**FR-3.2: TracIn (Captum)**
- Use Captum's TracInCPFast for efficient computation
- Gradient dot-product across checkpoints
- Configuration: Variable checkpoint count per budget
```python
from captum.influence import TracInCPFast

tracin = TracInCPFast(model, checkpoints, checkpoints_load_func, loss_fn)
scores = tracin.influence(test_inputs, train_loader)
```

**FR-3.3: Influence Functions (pytorch_influence_functions)**
- LISSA algorithm for Hessian-vector product approximation
- Configuration: recursion_depth, damping for compute budget control
```python
from pytorch_influence_functions import calc_influence_single

influence_scores = []
for train_idx in range(len(train_subset)):
    score = calc_influence_single(model, train_loader, test_loader, train_idx)
    influence_scores.append(score)
```

**FR-3.4: FastIF (Captum TracInCPFast with last-layer)**
- Last-layer influence function approximation
- Faster computation via gradient restriction
- Configuration: Similar to TracIn but last-layer only

### FR-4: Compute Budget Management

**FR-4.1: Budget Levels**
| Budget | Gradient-Equivalents | TRAK Projections | TracIn Checkpoints | IF Iterations |
|--------|---------------------|------------------|-------------------|---------------|
| 10 | 10 | 10 | 1 | 10 |
| 25 | 25 | 25 | 2 | 25 |
| 50 | 50 | 50 | 3 | 50 |
| 75 | 75 | 75 | 4 | 75 |
| 100 | 100 | 100 | 5 | 100 |

**FR-4.2: Budget Normalization**
- All methods normalized to gradient-equivalent operations
- Ensure fair comparison across different algorithmic approaches

### FR-5: Evaluation Metrics

**FR-5.1: Rank Preservation (rho_r)**
- Spearman correlation between method scores and LOO ground truth
- Formula: spearmanr(pred_scores, loo_ground_truth).correlation
- Range: [-1, 1], higher is better

**FR-5.2: Magnitude Fidelity (rho_m)**
- Pearson correlation between method scores and LOO ground truth
- Formula: pearsonr(pred_scores, loo_ground_truth)[0]
- Range: [-1, 1], higher is better

**FR-5.3: Normalized Stability (S)**
- Variance ratio: Var(method_scores across seeds) / Var(LOO_ground_truth)
- Lower is better (more stable)

**FR-5.4: Metric Computation**
```python
from scipy.stats import spearmanr, pearsonr

def compute_metrics(pred_scores, ground_truth):
    rho_r = spearmanr(pred_scores, ground_truth).correlation
    rho_m = pearsonr(pred_scores, ground_truth)[0]
    return {'rho_r': rho_r, 'rho_m': rho_m}
```

### FR-6: Statistical Analysis

**FR-6.1: Bootstrap Confidence Intervals**
```python
from scipy.stats import bootstrap

def compute_ci(samples, statistic, n_resamples=1000, confidence_level=0.95):
    result = bootstrap((samples,), statistic, n_resamples=n_resamples,
                       confidence_level=confidence_level, method='BCa')
    return result.confidence_interval
```

**FR-6.2: Metric Crossing Detection**
- For each method pair (m1, m2) at each budget level:
  - Compute bootstrap CI for (rho_r_m1 - rho_r_m2)
  - Compute bootstrap CI for (rho_m_m1 - rho_m_m2)
  - Crossing detected if: CI(rho_r diff) doesn't contain 0 AND CI(rho_m diff) doesn't contain 0 AND signs are opposite

**FR-6.3: Pareto Front Identification**
- Identify non-dominated methods at each budget level
- Method is dominated if another method is better on ALL metrics
- Report Pareto front size (target: >=2 methods)

### FR-7: Experiment Orchestration

**FR-7.1: Configuration Management**
- YAML-based experiment configuration
- Hyperparameter specification
- Seed management: 3 method seeds × 5 budget levels × 4 methods

**FR-7.2: Logging**
- Log metrics for all method-budget-seed combinations
- Store in structured format (CSV/JSON)
- Track: method, budget, seed, rho_r, rho_m, S, CI_low, CI_high

**FR-7.3: Checkpointing**
- Save LOO ground truth for reuse
- Save method scores for each configuration
- Enable resumable experiments

### FR-8: Visualization

**FR-8.1: Required Figure (Mandatory)**
- Gate metrics comparison: Bar chart showing rho_r and rho_m for each method at each compute budget

**FR-8.2: Additional Figures**
1. **Pareto Front Visualization**: 2D scatter (rho_r vs rho_m) with frontier highlighted per budget
2. **Metric Crossing Heatmap**: Matrix showing which pairs exhibit crossings at which budgets
3. **Bootstrap CI Plot**: Error bars showing 95% CIs for each metric-method-budget
4. **Compute-Performance Curves**: Line plots of metrics vs budget for each method

---

## Non-Functional Requirements

### NFR-1: Performance
- Single GPU execution (CUDA_VISIBLE_DEVICES)
- LOO retraining: ~10-20 hours total (R=10 seeds × subset training)
- Method evaluation: ~1-2 hours per method per budget
- Memory: Fit within 16GB GPU (ResNet-18 + CIFAR-10)

### NFR-2: Reproducibility
- Fixed random seeds for all stochastic operations
- Deterministic CUDA operations where possible
- Version-pinned dependencies

### NFR-3: Modularity
- Separable components for reuse in H-M1, H-M2, H-M3
- Clean interfaces between data/model/attribution/evaluation modules
- Extensible for additional methods or metrics

---

## Success Criteria

### Gate: MUST_WORK

| Criterion | Description | Threshold |
|-----------|-------------|-----------|
| **SC-1** | Code executes without error | 100% completion |
| **SC-2** | Method pair with metric crossing | >=1 pair with CI-separated crossing |
| **SC-3** | Crossing at multiple budgets | >=2 compute levels |
| **SC-4** | Statistical validity | Non-overlapping 95% bootstrap CIs |

### PoC Validation
1. LOO ground truth computed for 5000 train × 100 test examples
2. All 4 methods evaluated at all 5 budget levels
3. Bootstrap CIs computed for all metric comparisons
4. At least one metric crossing detected with statistical significance
5. Visualizations generated (4+ figures)

### Failure Response
IF fails -> STOP pipeline (foundational Pareto claim invalid - no trade-offs exist between attribution methods)

---

## Dependencies

### External Dependencies
- PyTorch >= 2.0
- torchvision (ResNet-18, CIFAR-10)
- traker (TRAK implementation)
- captum (TracIn, FastIF)
- pytorch_influence_functions (IF)
- scipy (bootstrap, correlations)
- numpy, matplotlib, pandas

### Internal Dependencies
- None (H-E1 is foundation hypothesis)

### Reference Implementations
- Primary: MadryLab/trak (TRAK, Park et al. ICML 2023)
- Secondary: Captum TracInCPFast (Meta production)
- Tertiary: nimarb/pytorch_influence_functions (Koh & Liang 2017)

---

## Data Specifications

### Dataset: CIFAR-10
| Split | Size | Usage |
|-------|------|-------|
| Train (full) | 50,000 | Source for LOO subset |
| Train (subset) | 5,000 | LOO retraining pool |
| Test (LOO targets) | 100 | LOO influence computation |
| Test (full) | 10,000 | Method evaluation |

### Experiment Parameters (from Phase 2C)
| Parameter | Value |
|-----------|-------|
| Model | ResNet-18 (11M params) |
| Dataset | CIFAR-10 (5,000 subset) |
| Methods | TRAK, TracIn, IF, FastIF |
| Compute budgets | 10, 25, 50, 75, 100 |
| LOO retraining seeds | 10 |
| Method seeds | 3 |
| Bootstrap resamples | 1000 |
| Confidence level | 95% |
| Primary metrics | rho_r (Spearman), rho_m (Pearson) |
| Secondary metric | S (Stability) |

---

## Acceptance Criteria

### Phase 4 Deliverables
1. Working experiment codebase with all 4 methods
2. LOO ground truth computation
3. Method evaluation at all budget levels
4. Bootstrap CI computation for all comparisons
5. Metric crossing detection results
6. Results CSV with all metrics
7. Visualization figures (4+ total)
8. 04_validation.md report

### Quality Gates
- Code passes linting/type checks
- Unit tests for metric computation functions
- Results reproducible with fixed seeds
- CIs computed correctly (verified against manual calculation)

---

## Appendix: Traceability

| Requirement | Source |
|-------------|--------|
| Dataset (CIFAR-10 subset) | Phase 2C - LOO feasibility constraint |
| Model (ResNet-18) | Phase 2C - TRAK paper standard |
| Methods (4 total) | Phase 2C - Implementation research |
| Compute budgets | Phase 2B - controlled variables |
| LOO retraining | Phase 2C - ground truth computation |
| rho_r metric | Phase 2B - rank preservation definition |
| rho_m metric | Phase 2B - magnitude fidelity definition |
| Bootstrap CIs | Phase 2C - scipy.stats.bootstrap |
| Success threshold | Phase 2B - metric crossing with CI separation |
| Method references | Phase 2C Appendix B - GitHub implementations |

---

*Generated by Phase 3 Implementation Planning*
*Source: Phase 2C Experiment Brief (02c_experiment_brief.md)*
*Next: Architecture Design (03_architecture.md)*
