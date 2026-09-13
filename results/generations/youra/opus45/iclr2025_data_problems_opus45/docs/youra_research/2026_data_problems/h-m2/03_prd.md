# Product Requirements Document: H-M2

**Date:** 2026-03-26
**Author:** Anonymous
**Hypothesis ID:** H-M2
**Hypothesis Type:** MECHANISM (INCREMENTAL)
**Gate:** MUST_WORK
**Prerequisites:** H-M1 (VALIDATED)
**Phase 2C Source:** 02c_experiment_brief.md

---

## Executive Summary

This PRD defines the implementation requirements for validating hypothesis H-M2: demonstrating that in non-convex deep networks (ResNet-18), R² from regressing metrics on approximation error norm ||φ_hat - φ||_2 drops from ~1.0 (convex baseline established in H-M1) to <0.80, proving structural decoupling beyond approximation quality differences. This hypothesis tests the mechanistic claim that metric decoupling in deep networks is structural (due to non-convex geometry) rather than an artifact of approximation quality.

**Objective:** Implement a mechanism verification experiment that applies the R² regression analysis from H-M1 to deep network (ResNet-18) attribution outputs, demonstrating that the single-error-axis model breaks down in non-convex settings.

**Success Criteria:**
- Code runs without error for all 4 methods × 5 compute budgets × 3 seeds
- R²_deep < 0.80 for at least one metric (rho_r or rho_m)
- Cross-metric partial correlation < 0.85 in deep regime
- Clear contrast with H-M1 convex baseline (R² >= 0.95)

---

## Problem Statement

### Context
H-M1 established that in convex settings (logistic regression on CIFAR-10 features), metrics are tightly coupled with partial correlations >= 0.95 at all compute levels. This provides a theoretical baseline: when model geometry is convex, all attribution methods converge to the same target, and metrics correlate perfectly. H-M2 tests whether this coupling breaks down specifically due to non-convex deep network geometry.

### Hypothesis
In non-convex deep networks (ResNet-18), R² from regressing metrics on approximation error norm ||φ_hat - φ||_2 drops from ~1.0 (convex baseline) to <0.80, proving structural decoupling beyond approximation quality differences.

**Mechanistic Reasoning:**
1. Non-convex models have multiple local minima (loss landscape complexity)
2. Different attribution methods approximate different "effective targets"
3. Approximation error alone cannot explain metric variance
4. The "single error axis" assumption that holds in convex settings fails

### Gap Being Addressed
H-M1 showed metrics couple tightly in convex settings; H-M2 demonstrates they decouple in non-convex settings. Together, they establish that the Pareto trade-offs observed in H-E1 are due to deep network geometry, not definitional problems with the metrics or uniform approximation quality issues.

---

## Functional Requirements

### FR-1: Data Pipeline (Reuse from H-E1)

**FR-1.1: CIFAR-10 Dataset**
- Source: torchvision.datasets.CIFAR10
- Training subset: 5,000 samples (matching H-E1/H-M1)
- Test subset: 100 samples (for LOO ground truth computation)
- Preprocessing: Normalize with mean=[0.4914, 0.4822, 0.4465], std=[0.2023, 0.1994, 0.2010]

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
```

**FR-1.2: LOO Ground Truth (Reuse from H-E1)**
- Load cached LOO ground truth: `../h-e1/code/results/loo_cache.npy`
- Shape: (5000, 100) - influence of each training sample on each test sample
- Computed via R=10 retraining seeds

### FR-2: Deep Network Model (Reuse from H-E1)

**FR-2.1: Pre-trained ResNet-18**
- Load from H-E1: `../h-e1/code/checkpoints/model_seed0_final.pt`
- Architecture: ResNet-18 (11.7M parameters)
- Output: 10 classes (CIFAR-10)

```python
import torch
import torchvision.models as models
import torch.nn as nn

# Load ResNet-18 checkpoint from H-E1
model = models.resnet18(pretrained=False)
model.fc = nn.Linear(model.fc.in_features, 10)
model.load_state_dict(torch.load('../h-e1/code/checkpoints/model_seed0_final.pt'))
model.eval()
```

### FR-3: Attribution Methods (Reuse from H-E1)

**FR-3.1: Methods Configuration**
| Method | Source | Key Parameter |
|--------|--------|---------------|
| TRAK | MadryLab/trak | proj_dim varies with budget |
| TracIn | H-E1/attribution.py | checkpoint aggregation |
| IF | H-E1/attribution.py | CG iterations |
| FastIF | H-E1/attribution.py | last-layer only |

**FR-3.2: Compute Budget Mapping**
| Budget | Gradient-Equivalents | Method Configuration |
|--------|---------------------|---------------------|
| 10 | 10 | Low approximation |
| 25 | 25 | Medium-low |
| 50 | 50 | Medium |
| 75 | 75 | Medium-high |
| 100 | 100 | Full approximation |

### FR-4: Metrics Analysis (PRIMARY - Extended from H-M1)

**FR-4.1: Rank Preservation (rho_r) and Magnitude Fidelity (rho_m)**
```python
from scipy.stats import spearmanr, pearsonr

def compute_rho_r_rho_m(pred_scores, loo_ground_truth):
    """
    Compute rank (Spearman) and magnitude (Pearson) fidelity.
    Reused from H-M1/metrics_analysis.py
    """
    pred_flat = pred_scores.flatten()
    truth_flat = loo_ground_truth.flatten()

    rho_r = spearmanr(pred_flat, truth_flat).correlation
    rho_m = pearsonr(pred_flat, truth_flat)[0]

    return {'rho_r': rho_r, 'rho_m': rho_m}
```

**FR-4.2: Approximation Error Norm**
```python
import numpy as np

def compute_error_norm(pred_scores, loo_ground_truth):
    """
    Compute ||φ_hat - φ||_2 (Frobenius norm for matrices).
    """
    return np.linalg.norm(pred_scores - loo_ground_truth)
```

**FR-4.3: Single-Error-Axis R² Regression (GATE METRIC)**
```python
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score

def compute_single_error_axis_r2(metrics_df):
    """
    Regress rho_r and rho_m on error_norm via sklearn LinearRegression.
    Tests single-error-axis hypothesis: metrics explained by approx error.

    Args:
        metrics_df: DataFrame with columns [method, budget, seed, rho_r, rho_m, error_norm]

    Returns:
        dict: {'r2_rho_r': float, 'r2_rho_m': float, 'r2_avg': float}

    Gate Condition: R²_deep < 0.80 for at least one metric
    """
    X = metrics_df['error_norm'].values.reshape(-1, 1)

    # Regress rho_r on error_norm
    model_r = LinearRegression().fit(X, metrics_df['rho_r'])
    r2_rho_r = r2_score(metrics_df['rho_r'], model_r.predict(X))

    # Regress rho_m on error_norm
    model_m = LinearRegression().fit(X, metrics_df['rho_m'])
    r2_rho_m = r2_score(metrics_df['rho_m'], model_m.predict(X))

    return {
        'r2_rho_r': r2_rho_r,
        'r2_rho_m': r2_rho_m,
        'r2_avg': (r2_rho_r + r2_rho_m) / 2
    }
```

**FR-4.4: Cross-Metric Partial Correlation**
```python
import pingouin as pg

def compute_partial_correlation(metrics_df):
    """
    Compute partial correlation between rho_r and rho_m
    conditioned on compute budget.

    Gate Condition: corr < 0.85 in deep regime (vs >= 0.95 in convex)
    """
    result = pg.partial_corr(
        data=metrics_df,
        x='rho_r',
        y='rho_m',
        covar='budget'
    )
    return result['r'].values[0]
```

### FR-5: Comparison with H-M1 Baseline

**FR-5.1: Load H-M1 Results**
```python
def load_hm1_baseline():
    """Load convex baseline results from H-M1 for comparison."""
    # H-M1 results: R² >= 0.95, partial_corr >= 0.95
    hm1_results = {
        'r2_rho_r': 0.95,  # Expected from H-M1
        'r2_rho_m': 0.95,
        'partial_corr_by_budget': {
            10: 0.9961, 25: 0.9945, 50: 0.9899, 75: 0.9905, 100: 0.9916
        }
    }
    return hm1_results
```

**FR-5.2: Statistical Comparison**
- Compute difference: Δ_R² = R²_convex - R²_deep
- Expected: Δ_R² > 0.15 (significant drop)
- Report 95% CI for R² difference

### FR-6: Visualization Requirements

**FR-6.1: Gate Metrics Comparison (MANDATORY)**
- Bar chart: R² convex (H-M1) vs R² deep (H-M2)
- X-axis: Metric type (rho_r, rho_m)
- Y-axis: R² value
- Bars: Convex (H-M1 blue), Deep (H-M2 orange)
- Horizontal line at 0.80 (gate threshold)

**FR-6.2: Additional Figures (LLM Autonomous)**

1. **Scatter Plot: Metrics vs Error Norm**
   - Separate subplots for rho_r and rho_m
   - X: error_norm, Y: metric value
   - Color by method (TRAK, TracIn, IF, FastIF)
   - Regression line overlaid
   - Compare spread (convex: tight, deep: dispersed)

2. **Cross-Metric Correlation Matrix**
   - Heatmap of corr(rho_r, rho_m) by budget level
   - Side-by-side: Convex vs Deep

3. **Method Comparison**
   - Bar chart of R² by method
   - Shows if decoupling is method-specific or universal

4. **Budget-wise Analysis**
   - Line plot of R² across budget levels [10, 25, 50, 75, 100]
   - Separate lines: Convex vs Deep

### FR-7: Experiment Orchestration

**FR-7.1: Configuration**
```yaml
# h-m2/config.yaml
experiment:
  name: h-m2-deep-decoupling
  hypothesis_type: MECHANISM
  gate: MUST_WORK
  base_hypothesis: h-m1

data:
  dataset: cifar10
  train_subset: 5000
  test_subset: 100
  loo_cache: ../h-e1/code/results/loo_cache.npy

model:
  name: resnet18
  checkpoint: ../h-e1/code/checkpoints/model_seed0_final.pt
  type: non-convex

evaluation:
  methods: [trak, tracin, if, fastif]
  budgets: [10, 25, 50, 75, 100]
  seeds: 3

success_criteria:
  r2_threshold: 0.80  # Must be BELOW this
  partial_corr_threshold: 0.85  # Must be BELOW this
```

**FR-7.2: Output Files**
- `h-m2/results/metrics.csv`: All metrics per method/budget/seed
- `h-m2/results/r2_analysis.csv`: R² regression results
- `h-m2/figures/gate_r2_comparison.png`: Gate figure
- `h-m2/figures/scatter_*.png`: Scatter plots
- `h-m2/figures/correlation_heatmap.png`: Correlation matrix

---

## Non-Functional Requirements

### NFR-1: Performance
- Single GPU execution (reuse H-E1 attribution scores if available)
- Total runtime: <3 hours (attribution computation + analysis)
- Memory: <16GB GPU RAM

### NFR-2: Reproducibility
- Fixed random seeds matching H-E1 and H-M1
- Reuse H-E1 data indices for exact consistency
- Version-pinned dependencies

### NFR-3: Reusability
- Metric analysis utilities shared with H-M1
- R² regression code reusable for H-M3
- Comparison framework for convex vs non-convex

---

## Success Criteria

### Gate: MUST_WORK

| Criterion | Description | Threshold |
|-----------|-------------|-----------|
| **SC-1** | Code executes without error | 100% completion |
| **SC-2** | R² drop from convex baseline | R²_deep < 0.80 for at least one metric |
| **SC-3** | Cross-metric partial correlation | corr < 0.85 in deep regime |
| **SC-4** | Clear convex/deep contrast | Δ_R² > 0.15 |

### Mechanism Verification Checklist
- [ ] H-M1 baseline loaded (convex R² >= 0.95)
- [ ] All 4 methods × 5 budgets × 3 seeds computed
- [ ] Error norm computed for each configuration
- [ ] R² regression analysis completed
- [ ] Partial correlation computed per budget
- [ ] Gate condition (R² < 0.80) verified
- [ ] Comparison figures generated

### Failure Response
IF R² >= 0.80 for both metrics → EXPLORE: Single-error-axis holds in deep networks; trade-offs may be approximation artifacts

---

## Dependencies

### External Dependencies
- PyTorch >= 2.0
- torchvision (CIFAR-10, ResNet-18)
- scikit-learn (LinearRegression, r2_score, StandardScaler)
- scipy (correlations)
- pingouin (partial correlations)
- numpy, pandas, matplotlib, seaborn

### Internal Dependencies (from Previous Hypotheses)
- **H-E1:**
  - Pre-trained ResNet-18: `h-e1/code/checkpoints/model_seed0_final.pt`
  - LOO ground truth: `h-e1/code/results/loo_cache.npy`
  - Attribution implementations: `h-e1/code/attribution.py`
  - Data loading: `h-e1/code/data.py`

- **H-M1:**
  - R² regression code: `h-m1/code/metrics_analysis.py`
  - Partial correlation code: `h-m1/code/metrics_analysis.py`
  - Visualization utilities: `h-m1/code/visualize.py`
  - Convex baseline results: `h-m1/results/metrics.csv`

### Reference Implementations
- Primary: Li et al. (2025) - "Natural Geometry of Robust Data Attribution"
- Secondary: Basu et al. (2020) - "Influence Functions in Deep Learning Are Fragile"
- Tertiary: TRAIS-Lab/dattri - Unified TDA evaluation library

---

## Data Specifications

### Input Data (from H-E1)
| Component | Shape | Source |
|-----------|-------|--------|
| LOO ground truth | (5000, 100) | h-e1/code/results/loo_cache.npy |
| Model checkpoint | - | h-e1/code/checkpoints/model_seed0_final.pt |
| CIFAR-10 train | (5000, 3, 32, 32) | torchvision |
| CIFAR-10 test | (100, 3, 32, 32) | torchvision |

### Experiment Parameters (from Phase 2C)
| Parameter | Value |
|-----------|-------|
| Model | ResNet-18 (non-convex) |
| Methods | TRAK, TracIn, IF, FastIF |
| Compute budgets | 10, 25, 50, 75, 100 |
| Seeds | 3 |
| Primary metric | R² from single-error-axis regression |
| Secondary metric | Cross-metric partial correlation |
| Gate threshold | R² < 0.80, corr < 0.85 |

### Output Data
| File | Description |
|------|-------------|
| metrics.csv | Method, budget, seed, rho_r, rho_m, error_norm |
| r2_analysis.csv | R² results for rho_r, rho_m |
| comparison.csv | H-M1 vs H-M2 comparison |
| figures/*.png | All visualization outputs |

---

## Acceptance Criteria

### Phase 4 Deliverables
1. Data loading pipeline (reusing H-E1 utilities)
2. Attribution score computation for all methods/budgets
3. Metrics computation (rho_r, rho_m, error_norm)
4. R² regression analysis
5. Partial correlation computation
6. Comparison with H-M1 baseline
7. Results CSV with all metrics
8. Visualization figures (4+ total)
9. 04_validation.md report with gate assessment

### Quality Gates
- Attribution scores match H-E1 outputs (if reusing cached)
- R² computation numerically stable
- Comparison with H-M1 baseline accurate
- All figures generated correctly

---

## Appendix: Traceability

| Requirement | Source |
|-------------|--------|
| ResNet-18 model | Phase 2C - H-E1 checkpoint reuse |
| LOO ground truth | Phase 2C - H-E1 cache reuse |
| R² regression analysis | Phase 2C - H-M1 code reuse |
| Error norm computation | Phase 2C - Frobenius norm |
| Gate threshold (0.80) | Phase 2B - verification plan |
| Methods | H-E1 - controlled comparison |
| Compute budgets | H-E1 - matched for comparison |
| Partial correlation | H-M1 - analysis reuse |

---

*Generated by Phase 3 Implementation Planning*
*Source: Phase 2C Experiment Brief (02c_experiment_brief.md)*
*Next: Architecture Design (03_architecture.md)*
