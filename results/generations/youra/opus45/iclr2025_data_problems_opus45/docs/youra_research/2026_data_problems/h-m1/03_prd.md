# Product Requirements Document: H-M1

**Date:** 2026-03-26
**Author:** Anonymous
**Hypothesis ID:** H-M1
**Hypothesis Type:** MECHANISM (INCREMENTAL)
**Gate:** MUST_WORK
**Prerequisites:** H-E1 (VALIDATED)
**Phase 2C Source:** 02c_experiment_brief.md

---

## Executive Summary

This PRD defines the implementation requirements for validating hypothesis H-M1: demonstrating that in convex settings (logistic regression), cross-metric partial correlations corr(rho_r, rho_m | budget) >= 0.95 at all compute levels, establishing baseline metric coupling. This hypothesis establishes the theoretical baseline that metrics ARE correlated when model geometry is convex (simple), making the non-convex decoupling observed in H-E1 (ResNet-18) meaningful by contrast.

**Objective:** Implement a mechanism verification experiment that computes exact Leave-One-Out (LOO) influence for a convex logistic regression classifier trained on CIFAR-10 features (extracted from ResNet-18), evaluates attribution method approximations, and demonstrates high cross-metric correlation in the convex setting.

**Success Criteria:**
- Code runs without error for all 4 methods × 5 compute budgets × 3 seeds
- Partial correlation corr(rho_r, rho_m | budget) >= 0.95 at ALL 5 compute levels
- R^2 from single-error-axis regression >= 0.95 (approximation error explains all metrics)
- Closed-form LOO computed via exact Hessian inversion

---

## Problem Statement

### Context
H-E1 demonstrated that data attribution methods (TRAK, TracIn, IF, FastIF) exhibit Pareto trade-offs in non-convex deep networks (ResNet-18), where different methods excel on different quality metrics (rank preservation vs magnitude fidelity). However, this observation alone doesn't explain WHY the trade-offs occur. H-M1 tests the mechanistic hypothesis that convex model geometry leads to metric coupling, which is absent in non-convex settings.

### Hypothesis
In convex settings (logistic regression), cross-metric partial correlations corr(rho_r, rho_m | budget) >= 0.95 at all compute levels, establishing baseline coupling. This coupling occurs because:
1. Convex models have a unique global minimum (positive definite Hessian)
2. LOO influence has a closed-form solution (no approximation needed)
3. All attribution methods converge to the same target, creating a "single error axis"

### Gap Being Addressed
H-E1 showed metric crossings exist; H-M1 establishes that these crossings are specific to non-convex geometry. If convex settings show high metric correlation, then the H-E1 crossings are due to non-convex loss landscape properties, not definitional inconsistencies in the metrics.

---

## Functional Requirements

### FR-1: Data Pipeline

**FR-1.1: Feature Extraction from H-E1 Model**
- Load pre-trained ResNet-18 from H-E1: `h-e1/code/checkpoints/model_seed0_final.pt`
- Extract 512-dimensional features from penultimate layer (before FC)
- Extract features for training subset (5,000 samples) and test subset (100 samples)

```python
import torch
from torchvision.models import resnet18

def extract_features(model, dataloader):
    """Extract penultimate layer features from ResNet-18."""
    model.eval()
    # Remove final FC layer for feature extraction
    feature_extractor = torch.nn.Sequential(*list(model.children())[:-1])

    features = []
    labels = []
    with torch.no_grad():
        for images, targets in dataloader:
            feats = feature_extractor(images.cuda())
            feats = feats.view(feats.size(0), -1)  # (N, 512)
            features.append(feats.cpu())
            labels.append(targets)

    return torch.cat(features), torch.cat(labels)
```

**FR-1.2: Dataset Specification**
| Component | Specification |
|-----------|---------------|
| Source | CIFAR-10 via torchvision |
| Training subset | 5,000 samples (from H-E1 indices) |
| Test subset | 100 samples (from H-E1 LOO targets) |
| Feature dimension | 512 (ResNet-18 penultimate) |
| Classes | 10 |

**FR-1.3: Feature Preprocessing**
```python
from sklearn.preprocessing import StandardScaler

# Normalize features
scaler = StandardScaler()
X_train = scaler.fit_transform(features_train.numpy())
X_test = scaler.transform(features_test.numpy())
```

### FR-2: Convex Model Pipeline

**FR-2.1: Logistic Regression (Convex Classifier)**
- Type: Multinomial logistic regression with L2 regularization
- Source: scikit-learn LogisticRegression
- Configuration:
  - C = 100 (L2 regularization strength = 0.01)
  - solver = 'lbfgs' (convex optimizer)
  - max_iter = 1000
  - multi_class = 'multinomial'

```python
from sklearn.linear_model import LogisticRegression

model = LogisticRegression(
    C=100,  # lambda = 0.01
    solver='lbfgs',
    max_iter=1000,
    multi_class='multinomial',
    random_state=42
)
model.fit(X_train, y_train)
```

**FR-2.2: Convexity Verification**
- Verify Hessian is positive definite (all eigenvalues > 0)
- Confirm unique global minimum reached

```python
import numpy as np

def verify_convexity(X, theta, lambda_reg=0.01):
    """Verify model is convex by checking Hessian eigenvalues."""
    N, D = X.shape
    probs = softmax(X @ theta)

    # Compute Hessian: H = X^T @ diag(p*(1-p)) @ X / N + lambda*I
    weights = probs * (1 - probs)
    H = X.T @ np.diag(weights.mean(axis=1)) @ X / N
    H += lambda_reg * np.eye(D)

    eigenvalues = np.linalg.eigvalsh(H)
    assert all(eigenvalues > 0), "Hessian not positive definite!"
    print(f"✓ Convexity verified: min eigenvalue = {eigenvalues.min():.6f}")
    return H
```

### FR-3: Closed-Form LOO Influence (Ground Truth)

**FR-3.1: Exact LOO via Hessian Inversion**
- For convex models, LOO influence has closed-form solution
- Based on: Koh & Liang (ICML 2017), Cook & Weisberg (1982)

```python
from scipy.linalg import inv

def compute_exact_loo_influence(X, y, theta, H_inv, x_test, y_test):
    """
    Compute EXACT leave-one-out influence for convex logistic regression.

    I(z_i, z_test) = grad_test^T @ H_inv @ grad_i

    Args:
        X: (N, D) training features
        y: (N,) training labels
        theta: (D, C) learned parameters
        H_inv: (D, D) inverse Hessian (precomputed)
        x_test: (D,) test sample features
        y_test: (,) test sample label

    Returns:
        influences: (N,) exact LOO influence scores
    """
    # Compute gradient at test point
    p_test = softmax(x_test @ theta)  # (C,)
    grad_test = x_test * (p_test - one_hot(y_test))  # (D,)

    # Compute s_test = H_inv @ grad_test
    s_test = H_inv @ grad_test  # (D,)

    # Compute influence for each training point
    probs = softmax(X @ theta)  # (N, C)
    grad_train = X * (probs - one_hot_matrix(y))  # (N, D)

    influences = grad_train @ s_test  # (N,)

    return influences
```

**FR-3.2: Ground Truth Computation**
- Compute exact LOO for all 5,000 training × 100 test pairs
- Store as reference matrix (5000, 100)

### FR-4: Attribution Method Evaluation

**FR-4.1: Methods (Reused from H-E1)**
| Method | Implementation | Adaptation for Convex |
|--------|----------------|----------------------|
| TRAK | MadryLab/trak | Use same projections |
| TracIn | Captum | Single checkpoint (converged) |
| IF | pytorch_influence_functions | Should match exact LOO |
| FastIF | Captum (last-layer) | Minimal benefit in linear model |

**FR-4.2: Compute Budget Mapping**
| Budget | Gradient-Equivalents | IF Iterations | Note |
|--------|---------------------|---------------|------|
| 10 | 10 | 10 | Low approximation |
| 25 | 25 | 25 | |
| 50 | 50 | 50 | |
| 75 | 75 | 75 | |
| 100 | 100 | 100 | Should converge to exact |

### FR-5: Evaluation Metrics

**FR-5.1: Primary Metrics (per method, per budget)**
```python
from scipy.stats import spearmanr, pearsonr

def compute_metrics(pred_scores, ground_truth):
    """Compute rank preservation and magnitude fidelity."""
    rho_r = spearmanr(pred_scores, ground_truth).correlation  # Rank
    rho_m = pearsonr(pred_scores, ground_truth)[0]  # Magnitude
    return {'rho_r': rho_r, 'rho_m': rho_m}
```

**FR-5.2: Cross-Metric Partial Correlation (SUCCESS CRITERION)**
```python
import pingouin as pg
import pandas as pd

def compute_partial_correlation(metrics_df):
    """
    Compute partial correlation between rho_r and rho_m
    conditioned on compute budget.

    Args:
        metrics_df: DataFrame with columns [method, budget, seed, rho_r, rho_m]

    Returns:
        partial_corr: float, partial correlation coefficient
    """
    result = pg.partial_corr(
        data=metrics_df,
        x='rho_r',
        y='rho_m',
        covar='budget'
    )
    return result['r'].values[0]
```

**FR-5.3: Single-Error-Axis R^2**
```python
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score

def compute_single_error_axis_r2(methods_df):
    """
    Regress metrics on approximation error norm.
    If R^2 >= 0.95, single error axis explains all metric variance.
    """
    # Compute approximation error: ||phi_hat - phi_exact||_2
    error_norms = np.linalg.norm(
        methods_df['pred_scores'] - methods_df['exact_loo'],
        axis=1
    )

    # Regress rho_r and rho_m on error_norms
    reg_r = LinearRegression().fit(error_norms.reshape(-1, 1), methods_df['rho_r'])
    reg_m = LinearRegression().fit(error_norms.reshape(-1, 1), methods_df['rho_m'])

    r2_r = r2_score(methods_df['rho_r'], reg_r.predict(error_norms.reshape(-1, 1)))
    r2_m = r2_score(methods_df['rho_m'], reg_m.predict(error_norms.reshape(-1, 1)))

    return {'r2_rho_r': r2_r, 'r2_rho_m': r2_m, 'r2_avg': (r2_r + r2_m) / 2}
```

### FR-6: Visualization Requirements

**FR-6.1: Gate Metrics Figure (MANDATORY)**
- Bar chart: Partial correlation at each budget level
- X-axis: Compute budget [10, 25, 50, 75, 100]
- Y-axis: corr(rho_r, rho_m | budget)
- Horizontal line at 0.95 (success threshold)

**FR-6.2: Additional Figures (LLM Autonomous)**
1. **Scatter Plot**: rho_r vs rho_m colored by method, faceted by budget
2. **R^2 Regression**: Metrics vs approximation error norm with regression line
3. **Method Comparison**: Bar chart of rho_r and rho_m per method at each budget
4. **Convexity Visualization**: Hessian eigenvalue spectrum

### FR-7: Experiment Orchestration

**FR-7.1: Configuration**
```yaml
# h-m1/config.yaml
experiment:
  name: h-m1-convex-coupling
  hypothesis_type: MECHANISM
  gate: MUST_WORK

data:
  source: h-e1/code/checkpoints/model_seed0_final.pt
  train_subset: 5000
  test_subset: 100
  feature_dim: 512

model:
  type: logistic_regression
  C: 100  # lambda = 0.01
  solver: lbfgs
  max_iter: 1000

evaluation:
  methods: [trak, tracin, if, fastif]
  budgets: [10, 25, 50, 75, 100]
  seeds: 3
  bootstrap_resamples: 1000

success_criteria:
  partial_correlation_threshold: 0.95
  r2_threshold: 0.95
```

**FR-7.2: Logging**
- Log partial correlation at each budget level
- Log R^2 from single-error-axis regression
- Store all metrics in CSV: `h-m1/results/metrics.csv`

---

## Non-Functional Requirements

### NFR-1: Performance
- Single GPU execution (primarily CPU for logistic regression)
- Exact Hessian inversion: O(D^3) = O(512^3) = ~134M operations (fast)
- Total runtime: <2 hours (no LOO retraining needed - closed form!)

### NFR-2: Reproducibility
- Fixed random seeds for feature extraction and evaluation
- Reuse H-E1 data indices for consistency
- Version-pinned dependencies

### NFR-3: Reusability
- Feature extraction utilities for H-M2, H-M3
- Metric computation shared with H-E1
- Closed-form LOO as baseline for H-M2 comparison

---

## Success Criteria

### Gate: MUST_WORK

| Criterion | Description | Threshold |
|-----------|-------------|-----------|
| **SC-1** | Code executes without error | 100% completion |
| **SC-2** | Partial correlation | corr(rho_r, rho_m \| budget) >= 0.95 at ALL 5 budgets |
| **SC-3** | Single-error-axis R^2 | R^2 >= 0.95 |
| **SC-4** | Hessian positive definite | All eigenvalues > 0 |

### Mechanism Verification Checklist
- [ ] Convexity verified (Hessian eigenvalues)
- [ ] Closed-form LOO computed
- [ ] All methods evaluated at all budgets
- [ ] Partial correlations computed per budget
- [ ] R^2 from error-axis regression computed
- [ ] Success criteria satisfied

### Failure Response
IF partial correlation < 0.90 at any budget level → PIVOT: Redefine metrics (metrics are definitionally inconsistent if they don't couple in convex settings)

---

## Dependencies

### External Dependencies
- PyTorch >= 2.0 (feature extraction)
- scikit-learn (logistic regression, StandardScaler)
- scipy (Hessian inversion, correlations)
- pingouin (partial correlations)
- numpy, pandas, matplotlib

### Internal Dependencies
- H-E1: Pre-trained ResNet-18 model (`h-e1/code/checkpoints/model_seed0_final.pt`)
- H-E1: CIFAR-10 subset indices (5,000 train, 100 test)
- H-E1: Attribution method implementations (TRAK, TracIn, IF, FastIF)
- H-E1: Metric computation utilities (rho_r, rho_m)

### Reference Implementations
- Primary: Koh & Liang (ICML 2017) - Influence Functions
- Secondary: pingouin-stats - Partial correlations
- Tertiary: alstonlo/torch-influence - Direct Hessian computation

---

## Data Specifications

### Feature Dataset (from CIFAR-10)
| Component | Size | Shape |
|-----------|------|-------|
| X_train | 5,000 × 512 | (5000, 512) |
| y_train | 5,000 | (5000,) |
| X_test | 100 × 512 | (100, 512) |
| y_test | 100 | (100,) |

### Experiment Parameters (from Phase 2C)
| Parameter | Value |
|-----------|-------|
| Model | Logistic Regression (convex) |
| Features | ResNet-18 penultimate (512-dim) |
| Regularization | L2 with lambda=0.01 |
| Methods | TRAK, TracIn, IF, FastIF |
| Compute budgets | 10, 25, 50, 75, 100 |
| Seeds | 3 |
| Bootstrap resamples | 1000 |
| Primary metric | corr(rho_r, rho_m \| budget) |
| Secondary metric | R^2 from error-axis regression |
| Success threshold | >= 0.95 |

---

## Acceptance Criteria

### Phase 4 Deliverables
1. Feature extraction pipeline from H-E1 model
2. Convex logistic regression training
3. Closed-form LOO influence computation
4. Attribution method evaluation at all budgets
5. Partial correlation computation per budget
6. Single-error-axis R^2 computation
7. Results CSV with all metrics
8. Visualization figures (4+ total)
9. 04_validation.md report

### Quality Gates
- Convexity verification passes
- Exact LOO matches IF at high budget (r > 0.99)
- Partial correlations computed correctly
- R^2 regression analysis complete

---

## Appendix: Traceability

| Requirement | Source |
|-------------|--------|
| Convex model choice | Phase 2C - Koh & Liang 2017 |
| Feature extraction | Phase 2C - H-E1 model reuse |
| Closed-form LOO | Phase 2C - Cook & Weisberg 1982 |
| Partial correlation | Phase 2C - pingouin implementation |
| L2 regularization (0.01) | Phase 2C - Koh & Liang standard |
| Success threshold (0.95) | Phase 2B - verification plan |
| Compute budgets | H-E1 - matched for comparison |
| Methods | H-E1 - controlled comparison |

---

*Generated by Phase 3 Implementation Planning*
*Source: Phase 2C Experiment Brief (02c_experiment_brief.md)*
*Next: Architecture Design (03_architecture.md)*
