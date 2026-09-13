# Experiment Design: H-M2

**Date:** 2026-03-26
**Author:** Anonymous
**Hypothesis Statement:** In non-convex deep networks (ResNet-18), R^2 from regressing metrics on approximation error norm ||phi_hat - phi||_2 drops from ~1.0 (convex baseline) to <0.80, proving structural decoupling beyond approximation quality differences.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> **MECHANISM Hypothesis** - Tests whether metric decoupling in deep networks is structural.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (H-M1 VALIDATED)
**Gate Status:** MUST_WORK (pending validation)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M2
- **Type:** MECHANISM
- **Prerequisites:** H-M1 (VALIDATED)

### Gate Condition
R^2_deep < 0.80 for at least one metric (vs R^2_convex >= 0.95)

---

## Continuation Context

This hypothesis builds on H-M1 (Convex Baseline Coupling) which established that in convex settings (logistic regression), cross-metric partial correlations >= 0.95 at all compute levels. H-M2 tests whether this coupling breaks down in non-convex deep networks.

### Previous Hypothesis Results (H-M1)
- **Status:** VALIDATED (PASS)
- **Gate Result:** Minimum partial correlation 0.9899 (>= 0.95 threshold)
- **Key Insight:** Convex settings show tight metric coupling - R^2 baseline for comparison
- **Convexity Verified:** Positive-definite Hessian (eigenvalues 0.01-0.03)

---

## Implementation Research Summary

### Archon Knowledge Base Findings

> **Note:** Archon MCP unavailable. Findings sourced from Semantic Scholar academic search.

**1. "Influence Functions in Deep Learning Are Fragile" (Basu et al., 2020)** - 302 citations
- **Key Finding:** Network architecture, depth, and width strongly affect IF accuracy
- **Shallow vs Deep:** IF estimates accurate for shallow networks; often erroneous for deeper networks
- **Regularization:** Weight-decay regularization important for quality IF estimates
- **Implication for H-M2:** Supports expectation that deep network geometry disrupts standard IF analysis

**2. "Revisit, Extend, and Enhance Hessian-Free Influence Functions" (Yang et al., 2024)** - 9 citations
- **TracIn Insight:** Substitutes inverse Hessian with identity matrix - simple but effective
- **Why It Works:** Non-convex loss landscapes make exact Hessian inversion infeasible; identity approximation captures gradient similarity
- **Relevance:** TracIn's success despite ignoring Hessian supports metric decoupling in non-convex settings

**3. "Natural Geometry of Robust Data Attribution: From Convex to Deep" (Li et al., 2025)** - DIRECTLY RELEVANT
- **Spectral Amplification:** Deep representations inflate Lipschitz bounds by >10,000x
- **TRAK Fragility:** Standard TRAK scores are "geometrically fragile" - naive Euclidean certification yields 0%
- **Natural Wasserstein:** Reduces worst-case sensitivity by 76x
- **CIFAR-10 + ResNet-18:** Certifies 68.7% ranking pairs vs 0% Euclidean baseline
- **Self-Influence = Lipschitz:** Theoretical grounding for attribution stability

**4. "Quanda: Interpretability Toolkit for TDA Evaluation" (Bareeva et al., 2024)** - 6 citations
- **Benchmarking Framework:** Unified evaluation for TDA methods
- **Metrics Available:** Multiple quality metrics for attribution evaluation

**5. "LoRIF: Low-Rank Influence Functions" (Li et al., 2026)** - Recent
- **Scalability:** Addresses storage bottleneck in random projection methods
- **Quality-Scalability Tradeoff:** Higher projection dimension D improves quality but increases cost

### Archon Code Examples

> **Note:** Archon MCP unavailable. Code patterns derived from academic literature.

**Pattern 1: Influence Function Computation (from Basu et al.)**
```python
# Standard IF computation (fragile in deep networks)
def influence_function(model, train_loader, test_sample):
    # 1. Compute test gradient
    test_grad = compute_gradient(model, test_sample)

    # 2. Compute inverse Hessian-vector product (IHVP)
    # This step is where convex vs non-convex diverges
    ihvp = compute_ihvp(model, train_loader, test_grad)

    # 3. For each training sample, compute influence
    influences = []
    for train_sample in train_loader:
        train_grad = compute_gradient(model, train_sample)
        influence = torch.dot(ihvp, train_grad)
        influences.append(influence)
    return influences
```

**Pattern 2: TracIn (Hessian-Free)**
```python
# TracIn: Uses identity instead of inverse Hessian
def tracin_influence(checkpoints, train_sample, test_sample, lr):
    total_influence = 0
    for ckpt in checkpoints:
        model.load_state_dict(ckpt)
        train_grad = compute_gradient(model, train_sample)
        test_grad = compute_gradient(model, test_sample)
        # Simple dot product - no Hessian inversion
        total_influence += lr * torch.dot(train_grad, test_grad)
    return total_influence
```

**Pattern 3: Error Norm Computation**
```python
# Compute approximation error norm ||phi_hat - phi||_2
def compute_error_norm(phi_approx, phi_exact):
    """
    phi_approx: Estimated influence scores from method
    phi_exact: Ground truth LOO influence scores
    """
    return torch.norm(phi_approx - phi_exact, p=2)
```

### Exa GitHub Implementations

**Repository 1: MadryLab/trak** (⭐ Official TRAK Implementation)
- **URL:** https://github.com/madrylab/trak
- **License:** MIT
- **Relevance:** Official implementation of TRAK - random projection method for data attribution
- **Key Features:**
  - Fast CUDA kernels for JL projection
  - Pre-computed TRAK scores for CIFAR-10 available
  - API for custom tasks (image classification, BERT, CLIP)
- **Installation:** `pip install traker` or `pip install traker[fast]`
- **Usage Pattern:**
  ```python
  from trak import TRAKer
  traker = TRAKer(model=model, task='image_classification', train_set_size=N)
  # Featurize training data
  for batch in loader_train:
      traker.featurize(batch=batch, ...)
  traker.finalize_features()
  # Score test samples
  traker.score(batch=batch, ...)
  ```

**Repository 2: TRAIS-Lab/dattri** (⭐ Comprehensive TDA Library)
- **URL:** https://github.com/TRAIS-Lab/dattri
- **Relevance:** Unified library implementing IF, TracIn, TRAK, and more
- **Key Features:**
  - Multiple methods: Influence Function (CG, LiSSA, Arnoldi, EK-FAC), TracIn, TRAK, KNN-Shapley
  - Standard benchmarks: MNIST-10+LR/MLP, CIFAR-10/2+ResNet-9
  - Built-in metrics: LOO correlation, LDS (Linear Datamodeling Score)
- **Usage:**
  ```python
  from dattri.algorithm import IFAttributorCG
  from dattri.task import AttributionTask
  task = AttributionTask(model, train_loader, test_loader)
  attributor = IFAttributorCG(task)
  scores = attributor.attribute()
  ```

**Repository 3: nimarb/pytorch_influence_functions** (344 ⭐)
- **URL:** https://github.com/nimarb/pytorch_influence_functions
- **Relevance:** Classic PyTorch IF implementation
- **Training Config:**
  - Default params: `r=10`, `recursion_depth=5000` (for CIFAR-10)
  - CIFAR-10 compatible (50,000 training items)
- **Usage:**
  ```python
  import pytorch_influence_functions as ptif
  influences, harmful, helpful = ptif.calc_img_wise(config, model, trainloader, testloader)
  ```

**Repository 4: alstonlo/torch-influence**
- **URL:** https://github.com/alstonlo/torch-influence
- **Relevance:** Clean implementation with multiple IHVP methods
- **Methods:** AutogradInfluenceModule, CGInfluenceModule, LiSSAInfluenceModule
- **Associated Paper:** "If Influence Functions are the Answer, Then What is the Question?"

**Repository 5: code-philia/Empirical-Influence-Function**
- **URL:** https://github.com/code-philia/Empirical-Influence-Function
- **Relevance:** Implements EmpiricalIF (single-checkpoint), TracIn, BaseInfluenceFunction
- **Usage:** Lightweight variants for speed

**Serena Analysis Needed:** Yes - H-E1 existing code requires review for reuse

### Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

| Priority | Implementation | Justification |
|----------|---------------|---------------|
| **1st** | TRAIS-Lab/dattri | Comprehensive library with all methods (IF, TracIn, TRAK), built-in benchmarks for CIFAR-10+ResNet, standardized evaluation metrics (LOO, LDS) |
| **2nd** | MadryLab/trak | Official TRAK implementation with CUDA acceleration, pre-computed CIFAR-10 scores |
| **3rd** | nimarb/pytorch_influence_functions | Mature IF implementation with CIFAR-10 defaults |

**Recommended Implementation Path:**
- Primary: TRAIS-Lab/dattri (unified API, all methods, built-in metrics)
- Fallback: Individual method repositories (trak, pytorch_influence_functions)
- Justification: dattri provides standardized evaluation (LOO correlation, LDS) matching our hypothesis metrics (R^2 regression), and supports the exact benchmark (CIFAR-10 + ResNet) specified in Phase 2B

### Code Analysis (Serena MCP)

**Project Activated:** TEST_data_problems_opus45

#### Existing Code for Reuse

**H-E1 Code Structure (docs/youra_research/20260323_data_problems/h-e1/code/):**
- `attribution.py` - Attribution method implementations (TRAK, TracIn, IF, FastIF)
- `model.py` - ResNet-18 model loading
- `data.py` - CIFAR-10 data loading
- `train.py` - Model training
- `evaluate.py` - Metrics evaluation
- `config.py` - Configuration

**H-M1 Code Structure (docs/youra_research/20260323_data_problems/h-m1/code/):**
- `metrics_analysis.py` - **CRITICAL for H-M2** - Contains R^2 regression code
- `convex_model.py` - Logistic regression model
- `loo_influence.py` - LOO ground truth computation
- `attribution_convex.py` - Attribution for convex models
- `visualize.py` - Plotting functions

#### Key Functions to Reuse for H-M2

**1. `compute_rho_r_rho_m` (h-m1/code/metrics_analysis.py:16-44)**
```python
def compute_rho_r_rho_m(pred_scores, loo_ground_truth):
    """Compute rank (Spearman) and magnitude (Pearson) fidelity."""
    pred_flat = pred_scores.flatten()
    truth_flat = loo_ground_truth.flatten()
    rho_r = spearmanr(pred_flat, truth_flat).correlation
    rho_m = pearsonr(pred_flat, truth_flat)[0]
    return {'rho_r': rho_r, 'rho_m': rho_m}
```

**2. `compute_single_error_axis_r2` (h-m1/code/metrics_analysis.py:131-165)** - **PRIMARY GATE METRIC**
```python
def compute_single_error_axis_r2(metrics_df):
    """
    Regress rho_r and rho_m on error_norm via sklearn LinearRegression.
    Tests single-error-axis hypothesis: metrics explained by approx error.
    Returns: {'r2_rho_r': float, 'r2_rho_m': float, 'r2_avg': float}
    """
    X = metrics_df['error_norm'].values.reshape(-1, 1)
    # LinearRegression fit and r2_score for both metrics
```

**3. Error Norm Computation (h-m1/code/metrics_analysis.py:62)**
```python
error_norm = np.linalg.norm(scores - loo_exact)  # Frobenius norm
```

#### Integration Strategy for H-M2

1. **Copy H-M1 code structure** - metrics_analysis.py provides the exact R^2 regression needed
2. **Reuse H-E1 attribution methods** - TRAK, TracIn, IF, FastIF implementations
3. **Use H-E1 deep network setup** - ResNet-18, CIFAR-10 data, LOO ground truth
4. **Key modification**: Run R^2 analysis on **deep network outputs** (H-E1 setup) instead of convex outputs (H-M1 setup)

#### Expected Comparison
- **H-M1 (Convex):** R^2 ~ 0.95+ (metrics explained by single error axis)
- **H-M2 (Deep):** R^2 < 0.80 (metrics decoupled from error axis) - **Gate condition**

---

## Experiment Specification

### Dataset

**Name:** CIFAR-10
**Type:** standard (REAL dataset - not synthetic)
**Source:** torchvision (primary) or HuggingFace datasets

**Statistics:**
- Total samples: 60,000 (50,000 train + 10,000 test)
- **H-M2 Subset:** 5,000 train samples (matching H-E1/H-M1 for controlled comparison)
- **Test samples:** 100 (for LOO ground truth computation)
- Classes: 10
- Image size: 32x32x3

**Preprocessing:**
- Normalize: mean=[0.4914, 0.4822, 0.4465], std=[0.2023, 0.1994, 0.2010]
- ToTensor() transform

**Augmentation (Training):**
- None (matching H-E1 for controlled comparison)

**Continuation Note:** CIFAR-10 data and cached LOO ground truth available from H-E1 at `h-e1/code/results/loo_cache.npy`

**Loading Information** (for Phase 4 download):
- Method: torchvision
- Identifier: `CIFAR10`
- Code:
```python
import torchvision
from torchvision import transforms

transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.4914, 0.4822, 0.4465],
        std=[0.2023, 0.1994, 0.2010]
    )
])
train_dataset = torchvision.datasets.CIFAR10(
    root='./data', train=True, download=True, transform=transform
)
test_dataset = torchvision.datasets.CIFAR10(
    root='./data', train=False, download=True, transform=transform
)
```

### Models

#### Baseline Model

**Name:** ResNet-18 (non-convex deep network)
**Type:** CNN
**Source:** torchvision

**Configuration:**
- Architecture: ResNet-18 (11.7M parameters)
- Output: 10 classes (CIFAR-10)
- Pretrained: No (train from scratch for controlled attribution analysis)

**Continuation Note:** Trained ResNet-18 checkpoints available from H-E1 at `h-e1/code/checkpoints/model_seed0_final.pt`

**Why ResNet-18 (not convex logistic regression):**
- H-M2 requires **non-convex** deep network to contrast with H-M1's convex baseline
- ResNet-18 exhibits non-convex loss landscape (multiple local minima)
- Same architecture used in H-E1 enables controlled comparison

**Loading Information** (for Phase 4 download):
- Method: torchvision
- Identifier: `resnet18`
- Code:
```python
import torchvision.models as models
import torch.nn as nn

# ResNet-18 for CIFAR-10 (10 classes)
model = models.resnet18(pretrained=False)
model.fc = nn.Linear(model.fc.in_features, 10)  # Adjust for CIFAR-10

# Load trained checkpoint (reuse from H-E1)
checkpoint_path = '../h-e1/code/checkpoints/model_seed0_final.pt'
model.load_state_dict(torch.load(checkpoint_path))
```

#### Proposed Model

**Architecture:** ResNet-18 (non-convex deep network)

**Core Mechanism Implementation:**

```python
# Core Analysis: R^2 Regression for Metric Decoupling
# Based on: H-M1 metrics_analysis.py (Serena analysis)
# Purpose: Test if single-error-axis model breaks in deep networks

import numpy as np
from scipy.stats import spearmanr, pearsonr
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score

def compute_metrics_and_error(scores, loo_ground_truth):
    """
    Compute rank preservation (rho_r), magnitude fidelity (rho_m),
    and approximation error norm for attribution scores.

    Args:
        scores: (N_train, N_test) predicted attribution scores
        loo_ground_truth: (N_train, N_test) exact LOO influences
    Returns:
        dict with rho_r, rho_m, error_norm
    """
    pred = scores.flatten()
    truth = loo_ground_truth.flatten()

    rho_r = spearmanr(pred, truth).correlation  # Rank preservation
    rho_m = pearsonr(pred, truth)[0]             # Magnitude fidelity
    error_norm = np.linalg.norm(scores - loo_ground_truth)

    return {'rho_r': rho_r, 'rho_m': rho_m, 'error_norm': error_norm}

def compute_r2_single_axis(metrics_df):
    """
    Regress metrics on error norm to test single-axis hypothesis.
    Gate: R^2 < 0.80 in deep networks (vs >= 0.95 in convex)
    """
    X = metrics_df['error_norm'].values.reshape(-1, 1)

    r2_rho_r = r2_score(metrics_df['rho_r'],
                        LinearRegression().fit(X, metrics_df['rho_r']).predict(X))
    r2_rho_m = r2_score(metrics_df['rho_m'],
                        LinearRegression().fit(X, metrics_df['rho_m']).predict(X))

    return {'r2_rho_r': r2_rho_r, 'r2_rho_m': r2_rho_m}
```

### Training Protocol

**From Previous Hypotheses (H-E1, H-M1):**

This is a MECHANISM hypothesis testing metric decoupling in deep networks. The experiment reuses infrastructure from H-E1 (non-convex) and compares results with H-M1 (convex baseline).

**Attribution Methods (Reused from H-E1):**
- TRAK (random projection)
- TracIn (gradient similarity)
- IF (Influence Functions)
- FastIF (efficient IF)

**Compute Budgets:** 10, 25, 50, 75, 100 gradient-equivalents

**LOO Ground Truth:**
- Reuse from H-E1: `h-e1/code/results/loo_cache.npy`
- R=10 retraining seeds

**Seeds:** 3 method seeds per budget level (matching H-E1)

**Rationale:** Controlled comparison requires matching H-E1 setup exactly, changing only the analysis (R^2 regression vs Pareto analysis).

### Evaluation

**Primary Gate Metric:**
- **R^2 from single-axis regression** (metrics ~ error_norm)
- **Gate Condition:** R^2_deep < 0.80 for at least one metric

**Comparison Baseline (from H-M1 VALIDATED):**
- H-M1 convex R^2: ~0.21 average (lower than expected due to bimodal distribution)
- H-M1 partial correlation: >= 0.95 at all budgets

**Success Criteria (MUST_WORK Gate):**
| Criterion | Threshold | Source |
|-----------|-----------|--------|
| R^2_rho_r (deep) < | 0.80 | Phase 2B gate |
| R^2_rho_m (deep) < | 0.80 | Phase 2B gate |
| Cross-metric corr (deep) < | 0.85 | Phase 2B secondary |

**Expected Outcome:**
- H-M1 (Convex): High metric coupling (partial corr >= 0.95)
- H-M2 (Deep): Metric decoupling (R^2 drop, corr < 0.85)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Regression analysis (R^2 computation)
- Library: sklearn.linear_model, sklearn.metrics, scipy.stats
- Code:
```python
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from scipy.stats import spearmanr, pearsonr
import pandas as pd

# Build metrics DataFrame (method, budget, seed, rho_r, rho_m, error_norm)
# Then compute R^2 via LinearRegression().fit(X, y).predict(X)
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: R^2 convex (H-M1) vs R^2 deep (H-M2) bar chart
  - X-axis: Metric type (rho_r, rho_m)
  - Y-axis: R^2 value
  - Bars: Convex (H-M1), Deep (H-M2)
  - Horizontal line at 0.80 (gate threshold)

#### Additional Figures (LLM Autonomous)

1. **Scatter Plot: Metrics vs Error Norm**
   - Separate subplots for rho_r and rho_m
   - X: error_norm, Y: metric value
   - Color by method
   - Regression line overlaid
   - Shows whether single-axis model fits

2. **Cross-Metric Correlation Matrix**
   - Heatmap of corr(rho_r, rho_m) by budget level
   - Compare convex vs deep

3. **Method Comparison**
   - Bar chart of R^2 by method
   - Shows if decoupling is method-specific or universal

4. **Budget-wise Analysis**
   - Line plot of R^2 across budget levels
   - Separate lines for convex vs deep

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-m2/figures/`.

---

## PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. R^2_deep < 0.80 for at least one metric

---

## Appendix: Reference Implementations

### Academic References

1. **Basu et al. (2020)** - "Influence Functions in Deep Learning Are Fragile"
   - 302 citations
   - Key finding: IF accuracy degrades with network depth
   - Relevance: Theoretical support for metric decoupling in deep networks

2. **Li et al. (2025)** - "Natural Geometry of Robust Data Attribution"
   - Spectral amplification in deep networks inflates Lipschitz bounds >10,000x
   - CIFAR-10 + ResNet-18 benchmark included
   - Directly supports H-M2 hypothesis

3. **Park et al. (2023)** - "TRAK: Attributing Model Behavior at Scale"
   - Official TRAK implementation
   - CIFAR-10 pre-computed scores available

### Code Repositories

| Repository | URL | Use Case |
|------------|-----|----------|
| MadryLab/trak | https://github.com/madrylab/trak | TRAK attribution |
| TRAIS-Lab/dattri | https://github.com/TRAIS-Lab/dattri | Unified TDA library |
| nimarb/pytorch_influence_functions | https://github.com/nimarb/pytorch_influence_functions | IF implementation |
| alstonlo/torch-influence | https://github.com/alstonlo/torch-influence | Clean IF with IHVP methods |

### Previous Hypothesis Code (Reusable)

| File | Source | Purpose |
|------|--------|---------|
| `h-e1/code/attribution.py` | H-E1 | TRAK, TracIn, IF, FastIF implementations |
| `h-e1/code/results/loo_cache.npy` | H-E1 | LOO ground truth (reuse) |
| `h-e1/code/checkpoints/model_seed0_final.pt` | H-E1 | Trained ResNet-18 |
| `h-m1/code/metrics_analysis.py` | H-M1 | R^2 regression code (primary reuse) |
| `h-m1/code/visualize.py` | H-M1 | Plotting functions |

### Serena Code Analysis

**Analysis Performed:** Yes
**Project Activated:** TEST_data_problems_opus45
**Tools Used:**
- `list_dir`: Explored H-E1 and H-M1 code structure
- `get_symbols_overview`: Analyzed attribution.py, metrics_analysis.py
- `find_symbol`: Extracted compute_single_error_axis_r2, compute_rho_r_rho_m

**Key Findings:**
- H-M1's `metrics_analysis.py` contains exact R^2 regression code needed
- Error norm computed as Frobenius norm: `np.linalg.norm(scores - loo_exact)`
- Direct reuse path: Copy H-M1 analysis, apply to H-E1's deep network outputs

### Traceability Matrix

| Specification | Source Type | Source Reference |
|---------------|-------------|------------------|
| Dataset (CIFAR-10) | Phase 2A via 02b_context.md | Standard torchvision |
| Model (ResNet-18) | Phase 2A via 02b_context.md + H-E1 | torchvision + H-E1 checkpoint |
| Attribution methods | GitHub (Exa) + H-E1 | MadryLab/trak, dattri, H-E1/attribution.py |
| R^2 regression | Serena analysis + H-M1 | H-M1/metrics_analysis.py:131-165 |
| Gate threshold (0.80) | Phase 2B | 02b_verification_plan.md |
| LOO ground truth | H-E1 reuse | h-e1/code/results/loo_cache.npy |
| Metric decoupling theory | Academic | Basu 2020, Li 2025 |
| Visualization | H-M1 reuse | h-m1/code/visualize.py |

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-03-26T09:04:00+00:00

### Workflow History for This Hypothesis
- H-M2 set to IN_PROGRESS (2026-03-26)
- Phase 2C experiment design started

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
