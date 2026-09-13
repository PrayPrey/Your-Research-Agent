# Experiment Design: h-m1

**Date:** 2026-03-26
**Author:** Anonymous
**Hypothesis Statement:** In convex settings (logistic regression), cross-metric partial correlations corr(rho_r, rho_m | budget) >= 0.95 at all compute levels, establishing baseline coupling.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🔬 **MECHANISM Hypothesis** - Testing the mechanistic claim that metrics ARE coupled in convex settings.

---

## Workflow Status

**Verification State:** ACTIVE
**Prerequisites Satisfied:** h-e1 VALIDATED (PASS) - Demonstrated metric crossings exist in non-convex (ResNet-18) setting
**Gate Status:** MUST_WORK - Failure triggers PIVOT (redefine metrics)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-m1
- **Type:** MECHANISM
- **Prerequisites:** h-e1 (VALIDATED)

### Gate Condition
**MUST_WORK Gate:** corr(rho_r, rho_m | budget) >= 0.95 at all 5 compute levels
- If PASS: Proceed to H-M2 (deep network decoupling test)
- If FAIL (correlation < 0.90): PIVOT - redefine metrics (definitionally inconsistent)

---

## Continuation Context

### Previous Hypothesis Results (h-e1)

**Validated Finding:** IF vs FastIF shows metric crossings at 5 budget levels (10, 25, 50, 75, 100)
- IF achieves higher rank preservation (rho_r)
- FastIF achieves higher magnitude fidelity (rho_m)
- Demonstrates clear Pareto trade-off in non-convex ResNet-18 setting

**Relevance to H-M1:** H-M1 tests whether this decoupling is unique to non-convex settings. In convex (logistic regression), we expect HIGH correlation (>=0.95), establishing baseline coupling.

**Reusable Components from h-e1:**
- Attribution methods: TRAK, TracIn, IF, FastIF (same implementations)
- Compute budget levels: [10, 25, 50, 75, 100] gradient-equivalents
- Metric computation: Spearman rho_r (rank), Pearson rho_m (magnitude)
- Bootstrap CI method: 1000 resamples

---

## Implementation Research Summary

### Archon Knowledge Base Findings

*Note: Archon MCP not available in this session. Using Semantic Scholar and existing research.*

**Finding 1: Influence Functions in Convex Settings**
- Source: Koh & Liang (ICML 2017) "Understanding Black-box Predictions via Influence Functions"
- Key Insight: For convex models with L2 regularization, influence functions have closed-form solution
- Formula: I_up,params(z) = -H^{-1} * grad_theta L(z, theta_hat)
- Hessian is positive definite (invertible) due to convexity
- Closed-form LOO influence is EXACT (not approximated) in convex settings

**Finding 2: LOO for Logistic Regression**
- Source: Multiple papers on leave-one-out cross-validation
- For logistic regression: LOO influence has closed-form via Sherman-Morrison formula
- No need for HVP approximation or conjugate gradient iteration
- This provides ground truth for all metrics

**Finding 3: Expected Metric Coupling**
- In convex settings, all approximation methods converge to the SAME target
- Single error axis theory predicts: ||phi_hat - phi||_2 determines ALL metrics
- Therefore: corr(rho_r, rho_m | budget) should be very high (>= 0.95)

### Archon Code Examples

*Using findings from Exa code search instead.*

### Exa GitHub Implementations

**Repository 1:** kohpangwei/influence-release (⭐ 792)
- **URL:** https://github.com/kohpangwei/influence-release
- **Relevance:** Official implementation from Koh & Liang ICML 2017 paper
- **Key Code:** TensorFlow implementation of influence functions
- **Note:** Reference for understanding influence function math, not for direct use

**Repository 2:** nimarb/pytorch_influence_functions (⭐ 344)
- **URL:** https://github.com/nimarb/pytorch_influence_functions
- **Relevance:** PyTorch reimplementation of Koh & Liang paper
- **Architecture:** Supports conjugate gradient and LiSSA for HVP approximation
- **Key Code:**
  ```python
  import pytorch_influence_functions as ptif
  influences, harmful, helpful = ptif.calc_img_wise(config, model, trainloader, testloader)
  ```
- **Used For:** Reference for PyTorch influence function structure

**Repository 3:** alstonlo/torch-influence (⭐ 86)
- **URL:** https://github.com/alstonlo/torch-influence
- **Relevance:** Clean PyTorch implementation with multiple inverse HVP methods
- **Key Feature:** AutogradInfluenceModule for direct Hessian computation (exact for small convex models)
- **Used For:** Direct computation approach for convex logistic regression

**Repository 4:** pingouin-stats/pingouin
- **URL:** https://pingouin-stats.org/
- **Relevance:** Python package for partial correlation computation
- **Key Code:**
  ```python
  import pingouin as pg
  result = pg.partial_corr(data=df, x='rho_r', y='rho_m', covar='budget')
  ```
- **Used For:** Computing cross-metric partial correlations conditioned on budget

### Implementation Priority Assessment

**CRITICAL: For convex LOO ground truth, use CLOSED-FORM solution, not approximation**

**Recommended Implementation Path:**
- Primary: Implement closed-form LOO influence for logistic regression using Sherman-Morrison
- Fallback: Use torch-influence AutogradInfluenceModule with direct Hessian inversion
- Justification: Convex models allow EXACT influence computation; approximations unnecessary

### Code Analysis (Serena MCP)

*Skipped* - Code from search results was sufficiently clear for convex LOO implementation.

---

## Experiment Specification

### Dataset

**Dataset 1: CIFAR-10 Features**
- **Name:** CIFAR-10 (feature-extracted)
- **Type:** standard
- **Source:** torchvision.datasets.CIFAR10 → ResNet-18 feature extraction
- **Statistics:**
  - Training: 5,000 samples (subset for tractable LOO computation)
  - Test: 100 samples (for influence scoring)
  - Features: 512-dimensional (ResNet-18 penultimate layer)
  - Classes: 10
- **Preprocessing:**
  1. Load CIFAR-10 images
  2. Pass through pre-trained ResNet-18 (from h-e1) without final FC layer
  3. Extract 512-dim feature vectors
  4. Normalize features (StandardScaler)
- **Augmentation:** None (using extracted features)

**Loading Information** (for Phase 4 download):
- Method: torchvision + custom feature extraction
- Identifier: `torchvision.datasets.CIFAR10`
- Code:
  ```python
  # Feature extraction from h-e1 model
  model = load_model('h-e1/code/checkpoints/model_seed0_final.pt')
  features = extract_features(model, cifar10_data)  # Remove FC layer
  ```

### Models

#### Baseline Model

**Architecture:** Logistic Regression (convex)
**Type:** Linear classifier with L2 regularization
**Source:** scikit-learn or PyTorch Linear layer

**Configuration:**
- Input: 512-dimensional features
- Output: 10 classes (CIFAR-10)
- Regularization: L2 (lambda = 0.01)
- Optimizer: L-BFGS (convex optimization)

**Loading Information** (for Phase 4 download):
- Method: scikit-learn
- Identifier: `sklearn.linear_model.LogisticRegression`
- Code:
  ```python
  from sklearn.linear_model import LogisticRegression
  model = LogisticRegression(C=100, solver='lbfgs', max_iter=1000, multi_class='multinomial')
  ```

**Why Convex:**
- Logistic regression with L2 regularization is strongly convex
- Unique global minimum exists
- Hessian is positive definite → invertible
- Closed-form LOO influence available

#### Proposed Model

**Architecture:** Same logistic regression (this hypothesis tests metrics, not new mechanism)

**Core Mechanism Implementation:**

```python
# Core Mechanism: Closed-Form LOO Influence for Convex Models
# Based on: Koh & Liang (2017), Cook & Weisberg (1982)

import numpy as np
from scipy.linalg import inv

def compute_loo_influence_convex(X, y, theta, lambda_reg=0.01):
    """
    Compute EXACT leave-one-out influence for logistic regression.

    Args:
        X: (N, D) feature matrix
        y: (N,) labels
        theta: (D, C) learned parameters
        lambda_reg: L2 regularization strength

    Returns:
        influences: (N, N_test) influence scores
    """
    N, D = X.shape

    # Compute Hessian: H = (1/N) * X^T @ diag(p*(1-p)) @ X + lambda*I
    probs = softmax(X @ theta)  # (N, C)

    # For each class, compute Hessian block
    H = np.zeros((D, D))
    for i in range(N):
        p = probs[i]
        w = p * (1 - p)  # diagonal weight
        H += w * np.outer(X[i], X[i])
    H = H / N + lambda_reg * np.eye(D)

    # Invert Hessian (exact for convex)
    H_inv = inv(H)

    # Compute influence: I(z_i, z_test) = grad_test^T @ H_inv @ grad_i
    grad_train = compute_gradients(X, y, theta)  # (N, D)

    def influence_on_test(x_test, y_test):
        grad_test = compute_gradient(x_test, y_test, theta)  # (D,)
        s_test = H_inv @ grad_test  # (D,)
        influences = grad_train @ s_test  # (N,)
        return influences

    return influence_on_test

# Integration: Replace approximate HVP methods with exact Hessian inversion
```

### Training Protocol

**Optimizer:** L-BFGS (convex solver)
- Parameters: max_iter=1000, tol=1e-8
- **Source:** Standard for convex logistic regression

**Learning Rate:** N/A (L-BFGS is second-order)

**Regularization:** L2 with lambda=0.01
- **Source:** Koh & Liang (2017) used 0.01 for influence function experiments

**Batch Size:** Full batch (convex optimization)

**Epochs:** Until convergence (L-BFGS)

**Loss Function:** Cross-entropy with L2 penalty

**Seeds:** 3 (for variance estimation across method initializations)

### Evaluation

**Primary Metrics:**

1. **Cross-Metric Partial Correlation:** corr(rho_r, rho_m | budget)
   - Pearson correlation between rank preservation and magnitude fidelity
   - Conditioned on compute budget level
   - Computed using pingouin.partial_corr()

2. **Rank Preservation (rho_r):** Spearman correlation with ground truth LOO ranking
   - For each attribution method at each budget
   - Range: [-1, 1], higher is better

3. **Magnitude Fidelity (rho_m):** Pearson correlation with ground truth LOO magnitudes
   - For each attribution method at each budget
   - Range: [-1, 1], higher is better

4. **R^2 from Single-Error-Axis Regression:**
   - Regress metrics on ||phi_hat - phi||_2
   - Expected: R^2 >= 0.95 in convex (single error axis explains all metrics)

**Success Criteria:**
- **Primary (MUST_WORK Gate):** corr(rho_r, rho_m | budget) >= 0.95 at ALL 5 compute levels
- **Secondary:** R^2 from single-error-axis regression >= 0.95

**Expected Baseline Performance:**
- In convex logistic regression: correlation should be very high (>0.95)
- If correlation < 0.90: Metrics are definitionally inconsistent → PIVOT

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: correlation analysis
- Library: scipy.stats + pingouin
- Code:
  ```python
  from scipy.stats import spearmanr, pearsonr
  import pingouin as pg

  # Per-method metrics
  rho_r = spearmanr(loo_ground_truth, method_scores).correlation
  rho_m = pearsonr(loo_ground_truth, method_scores)[0]

  # Partial correlation across methods/budgets
  result = pg.partial_corr(data=metrics_df, x='rho_r', y='rho_m', covar='budget')
  partial_corr = result['r'].values[0]
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Partial correlation values at each budget level (bar chart)
- X-axis: Compute budget [10, 25, 50, 75, 100]
- Y-axis: Partial correlation corr(rho_r, rho_m | budget)
- Horizontal line at 0.95 (success threshold)

#### Additional Figures (LLM Autonomous)
Based on hypothesis type (MECHANISM) and evaluation metrics:
1. **Scatter plot:** rho_r vs rho_m colored by method, faceted by budget
2. **R^2 regression plot:** Metrics vs approximation error norm
3. **Method comparison:** rho_r and rho_m bar chart per method at each budget

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-m1/figures/`.

---

## Mechanism Verification Protocol

### Pre-conditions
- [ ] **mechanism_exists:** Closed-form LOO computation is implemented
- [ ] **mechanism_isolatable:** Can compare exact LOO vs approximate methods
- [ ] **baseline_measurable:** Can compute metrics for all attribution methods

### Architecture Compatibility
**Logistic regression is compatible because:**
- Strongly convex with L2 regularization
- Unique minimum → Hessian is positive definite
- Closed-form influence via matrix inversion

### Activation Indicators
- **mechanism_log_message:** "Computing exact LOO influence via Hessian inversion"
- **tensor_shape_change:** H_inv shape = (D, D) where D=512
- **metric_delta_expected:** All metrics highly correlated (r > 0.95)

### Mechanism Verification Code
```python
def verify_convex_mechanism():
    """Verify convex model satisfies assumptions for exact LOO."""
    # Check 1: Hessian is positive definite
    H = compute_hessian(model, X, y)
    eigenvalues = np.linalg.eigvalsh(H)
    assert all(eigenvalues > 0), "Hessian not positive definite!"

    # Check 2: LOO ground truth matches approximate methods at high budget
    loo_exact = compute_exact_loo(model, X, y)
    loo_approx = compute_approx_loo(model, X, y, budget=100)
    correlation = np.corrcoef(loo_exact, loo_approx)[0, 1]
    assert correlation > 0.99, f"Exact vs approx LOO correlation too low: {correlation}"

    # Check 3: Cross-metric correlation is high
    metrics = compute_all_metrics(loo_exact, method_scores)
    partial_corr = pg.partial_corr(metrics, x='rho_r', y='rho_m', covar='budget')
    assert partial_corr['r'].values[0] >= 0.95, "Metrics not coupled in convex!"

    print("Convex mechanism verification PASSED")
```

### Success Criteria for Mechanism
- **hypothesis_support_metric:** corr(rho_r, rho_m | budget)
- **hypothesis_support_threshold:** >= 0.95 at all 5 budget levels

---

## PoC Success Check

**This is a MECHANISM hypothesis (not PoC/EXISTENCE)**

**Gate Pass Condition:**
1. Code runs without error
2. Partial correlation corr(rho_r, rho_m | budget) >= 0.95 at ALL 5 compute levels
3. R^2 from single-error-axis regression >= 0.95

**Gate Fail Condition:**
- If correlation < 0.90 at any budget level: PIVOT to redefine metrics

---

## Appendix: Reference Implementations

### A. Academic Sources

**Source 1:** Koh, P.W. & Liang, P. (2017)
- Title: "Understanding Black-box Predictions via Influence Functions"
- Venue: ICML 2017 (Best Paper)
- URL: https://proceedings.mlr.press/v70/koh17a.html
- Key Insight: Influence functions scale to deep learning; convex case is exact
- Used For: Theoretical foundation, closed-form derivation

**Source 2:** Lo, A. (2022)
- Title: "If Influence Functions are the Answer, Then What is the Question?"
- URL: https://arxiv.org/abs/2209.05364
- Key Insight: Convex case aligns well with LOO retraining
- Used For: Validation that convex setting should show high metric correlation

### B. GitHub Implementations (Exa)

**Repository 1:** kohpangwei/influence-release (⭐ 792)
- URL: https://github.com/kohpangwei/influence-release
- Used For: Reference implementation structure

**Repository 2:** nimarb/pytorch_influence_functions (⭐ 344)
- URL: https://github.com/nimarb/pytorch_influence_functions
- Used For: PyTorch influence function API design

**Repository 3:** alstonlo/torch-influence (⭐ 86)
- URL: https://github.com/alstonlo/torch-influence
- Used For: Direct Hessian computation for small convex models

**Repository 4:** pingouin-stats/pingouin
- URL: https://pingouin-stats.org/
- Used For: Partial correlation computation

### C. Code Analysis (Serena)

*Skipped* - Code from search results was sufficiently clear

### D. Previous Hypothesis Context

**Source:** h-e1 Validation Report (PASS)
- File: `h-e1/04_validation.md`
- Reused Components:
  - Pre-trained ResNet-18 model (for feature extraction)
  - Attribution method implementations (TRAK, TracIn, IF, FastIF)
  - Metric computation functions (rho_r, rho_m)
  - Bootstrap CI methodology (1000 resamples)
- Why Reused: Controlled experiment - only model type changes (non-convex → convex)

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Convex model choice | Academic | Koh & Liang 2017 |
| Closed-form LOO | Academic | Cook & Weisberg 1982 |
| Feature extraction | Previous | h-e1 checkpoint |
| Attribution methods | Previous + GitHub | h-e1 + nimarb/pytorch_influence_functions |
| Partial correlation | GitHub | pingouin-stats |
| L2 regularization (0.01) | Academic | Koh & Liang 2017 |
| Success threshold (0.95) | Phase 2B | 02b_verification_plan.md |
| Compute budgets | Previous | h-e1 (matched for comparison) |

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-03-26T08:35:00+00:00

### Workflow History for This Hypothesis
- 2026-03-26T08:34:03: h-m1 set to IN_PROGRESS (Hypothesis Loop)
- 2026-03-26T08:35:00: Phase 2C experiment design started

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: Semantic Scholar, Exa (GitHub + Code), Serena (skipped)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
