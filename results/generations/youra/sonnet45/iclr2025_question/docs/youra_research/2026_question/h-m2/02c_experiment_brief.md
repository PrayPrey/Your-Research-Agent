# Experiment Design: h-m2

**Date:** 2026-03-21
**Author:** Anonymous
**Hypothesis Statement:** SGD with fixed hyperparameters produces finite-variance test accuracy distribution with Gaussian-like tails, validated through excess kurtosis 95% CI ∈ [−2, +2].
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Verification Template** - Validates causal mechanism through trajectory analysis.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** h-m1 (PASSED)
**Gate Status:** MUST_WORK (failure stops workflow)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-m2
- **Type:** MECHANISM
- **Prerequisites:** h-m1 (Seed Independence)

### Gate Condition
MUST_WORK - Failure stops entire workflow. If different initializations do NOT lead to different optimization trajectories, the causal mechanism breaks down.

---

## Continuation Context

h-m2 builds on h-m1 by validating that the different initial weight configurations (proven in h-m1) actually lead to different optimization trajectories and final model states.

### Previous Hypothesis Results (h-m1)

**Status:** PASSED ✅
**Key Finding:** All 4 experimental conditions demonstrate statistically significant seed independence (p < 0.05). Mean pairwise weight distances:
- 1layer_mnist: 9.599
- 1layer_fashion_mnist: 9.599
- 2layer_mnist: 16.227
- 2layer_fashion_mnist: 16.227

All p-values < 0.000001, confirming different random seeds create truly independent weight initializations.

**Implication for h-m2:** Initial weights are confirmed different. Now we must prove these different starting points lead to different optimization paths.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Limited Direct Relevance** - Archon KB primarily contains diffusion model training code, not statistical analysis of NN training variance.

**Relevant Finding:**
- **PyTorch Seed Control:** `torch.manual_seed()` documentation confirms deterministic training control (used in h-m1)
- **Training Loop Patterns:** Standard loss tracking patterns identified in HuggingFace examples

**Assessment:** This is a specialized statistical validation hypothesis. Implementation will rely more on standard scientific Python libraries (scipy, numpy) than deep learning-specific KB entries.

### Archon Code Examples

**Query 1: Pairwise Distance Calculation**
- No directly relevant examples found (distributed training code returned instead)
- Will use standard scipy implementation: `scipy.spatial.distance.pdist(weight_matrix, metric='euclidean')`

**Query 2: Training Trajectory Loss Tracking**
- **Example:** Standard PyTorch training loop (HuggingFace Diffusers)
  ```python
  # Training loop pattern
  optimizer.zero_grad()
  loss = compute_loss(model_output, target)
  loss.backward()
  optimizer.step()
  # Track loss: loss_history.append(loss.item())
  ```
  - **Pattern Insight:** Loss tracking done via `.item()` after each epoch
  - **Application:** h-m1 already tracked losses, h-m2 will load and analyze them

**Implementation Path:** Standard scientific Python stack (scipy.spatial.distance, numpy statistics) for post-hoc analysis of h-m1 training artifacts.

### Exa GitHub Implementations

**Query 1: Neural Network Weight Pairwise Distance Analysis**

**Repository 1**: PyTorch Official Documentation - PairwiseDistance
- **URL**: https://docs.pytorch.org/docs/stable/generated/torch.nn.PairwiseDistance.html
- **Relevance**: Standard PyTorch implementation for computing pairwise distances
- **Implementation**:
  ```python
  import torch
  import torch.nn as nn

  # For pairwise distances between vectors
  pdist = nn.PairwiseDistance(p=2)  # L2 norm (Euclidean)
  input1 = torch.randn(100, 128)  # 100 samples, 128 dimensions
  input2 = torch.randn(100, 128)
  output = pdist(input1, input2)  # Returns (100,) distances
  ```
- **Key Pattern**: Use `torch.nn.PairwiseDistance` for L2 distance between weight vectors
- **Application to h-m2**: Can flatten weight tensors and compute distances between final model weights

**Repository 2**: Scipy Pairwise Distance Matrix (from StackOverflow)
- **URL**: https://stackoverflow.com/questions/20089007/calculate-weighted-pairwise-distance-matrix-in-python
- **Relevance**: Computing all pairwise distances for N weight configurations
- **Implementation**:
  ```python
  from scipy.spatial.distance import pdist, squareform

  # X: (30, n_params) - 30 weight configurations
  distances = pdist(X, metric='euclidean')  # Returns (30 choose 2) = 435 distances
  distance_matrix = squareform(distances)   # Convert to 30x30 matrix
  ```
- **Key Pattern**: `pdist` returns condensed distance array, `squareform` converts to full matrix
- **Application to h-m2**: Compute all pairwise distances between 30 final weight configs per condition

**Repository 3**: ArXiv Paper - Information Theory & Weight Distance Analysis
- **URL**: https://arxiv.org/pdf/2102.00396
- **Relevance**: Validates using weight distance to track network training dynamics
- **Key Insight**: "Distance between the neural network weights in different training stages can be used to estimate the information accumulated by the network in the training process"
- **Method**: Multidimensional Scaling (MDS) to visualize weight distances
- **Application to h-m2**: Confirms validity of using weight distance as metric for trajectory divergence

**Query 2: Training Loss Trajectory Divergence Analysis**

**Repository 1**: ArXiv - Hallmarks of Optimization Trajectories in Neural Networks
- **URL**: https://arxiv.org/html/2403.07379v1
- **Relevance**: Comprehensive analysis of optimization trajectory structure
- **Key Metrics**:
  - Cosine similarity between parameter checkpoints
  - Mean directional similarity (MDS) for trajectory characterization
  - Trajectory maps showing directional (dis)similarity
- **Key Finding**: "Increasing momentum, weight decay, batch size, and learning rate increase the extent of directional exploration"
- **Application to h-m2**: Validates using trajectory divergence metrics (CV of loss) to characterize optimization dynamics

**Repository 2**: ArXiv - Analyzing Multi-Stage Loss Curves
- **URL**: https://arxiv.org/html/2410.20119v1
- **Relevance**: Loss curve analysis methodology
- **Key Metric**: Wasserstein distance to capture weight distribution evolution
- **Pattern**: Three stages identified - initial plateau, descent, secondary plateau
- **Application to h-m2**: Methodology for analyzing loss trajectory patterns

**Repository 3**: Weights & Biases - Learning Curves Deep Dive
- **URL**: https://wandb.ai/mostafaibrahim17/ml-articles/reports/A-Deep-Dive-Into-Learning-Curves-in-Machine-Learning--Vmlldzo0NjA1ODY0
- **Relevance**: Practical guide to loss curve interpretation
- **Key Pattern**: Coefficient of Variation (CV) for measuring trajectory stability
- **Code Pattern**:
  ```python
  # Track loss per epoch
  loss_history = []
  for epoch in range(num_epochs):
      # Training loop
      loss_history.append(loss.item())

  # Analyze CV
  cv = (np.std(loss_history) / np.mean(loss_history)) * 100
  ```
- **Application to h-m2**: CV calculation for final epoch losses across 30 seeds

**Serena Analysis Needed**: False ℹ️
- Code patterns are clear and well-documented
- Standard scientific Python libraries (scipy, numpy) sufficient
- No complex custom architectures requiring deep analysis

### 🎯 Implementation Priority Assessment

**CRITICAL: This is an analysis-only hypothesis - no new training needed**

**Implementation Priority:** Statistical analysis using standard scientific Python libraries

**Recommended Implementation Path:**
- Primary: scipy.spatial.distance.pdist for pairwise weight distances + numpy for CV calculation
- Fallback: torch.nn.PairwiseDistance (less efficient for all-pairs computation)
- Justification: scipy.pdist efficiently computes all pairwise distances in one call (optimized C implementation). torch.nn.PairwiseDistance requires manual loops for all-pairs, slower for 30×30 comparisons.

### Code Analysis (Serena MCP)

**Skipped** - Code from search results was sufficiently clear. Standard PyTorch and scipy implementations are well-documented and do not require semantic analysis.

---

## Experiment Specification

### Dataset

**Reuse h-m1 training data** - no new training required. This is an ANALYSIS-ONLY hypothesis.

**Data Source:** h-m1 experiment outputs
- Training loss trajectories (all 30 runs × 4 conditions)
- Final model weights (all 30 runs × 4 conditions)
- Initial model weights (all 30 runs × 4 conditions)

**Loading Information** (for Phase 4 download):
- Method: Load from h-m1 experiment artifacts
- Identifier: h-m1/results/
- Code: `torch.load(f"h-m1/results/{condition}/seed_{seed}/final_weights.pt")`

### Models

#### Baseline Model

Same as h-m1:
- 1-layer MLP (784→128→10): ~196K params
- 2-layer MLP (784→256→128→10): ~400K params

**No new models needed** - reuse h-m1 trained models.

**Loading Information** (for Phase 4 download):
- Method: N/A (analysis only)
- Identifier: N/A
- Code: N/A

#### Analysis Implementation

**Core Mechanism Validation:**

```python
# Pseudo-code for h-m2 validation (10-30 lines)

def validate_trajectory_divergence(h_m1_results_path):
    """
    Validate that different initializations → different trajectories.

    Tests:
    1. Final weight configurations differ (pairwise distance > 0, p < 0.05)
    2. Loss trajectories diverge (CV of final loss ≥ 1%)
    """

    # Load h-m1 training artifacts
    conditions = ['1layer_mnist', '1layer_fashion_mnist',
                  '2layer_mnist', '2layer_fashion_mnist']
    results = {}

    for condition in conditions:
        # Load data for 30 seeds
        initial_weights = load_weights(condition, stage='initial')  # shape: (30, n_params)
        final_weights = load_weights(condition, stage='final')      # shape: (30, n_params)
        loss_trajectories = load_losses(condition)                  # shape: (30, 10_epochs)

        # TEST 1: Final weight configuration divergence
        final_distances = compute_pairwise_distances(final_weights)  # (30 choose 2) pairs
        mean_final_dist = np.mean(final_distances)
        t_stat, p_value = scipy.stats.ttest_1samp(final_distances, 0, alternative='greater')

        # TEST 2: Loss trajectory divergence
        final_epoch_losses = loss_trajectories[:, -1]  # Last epoch for all 30 runs
        cv_final_loss = np.std(final_epoch_losses) / np.mean(final_epoch_losses) * 100

        # Store results
        results[condition] = {
            'mean_final_distance': mean_final_dist,
            'final_distance_p_value': p_value,
            'cv_final_loss_percent': cv_final_loss,
            'test1_passed': p_value < 0.05 and mean_final_dist > 0,
            'test2_passed': cv_final_loss >= 1.0
        }

    # Gate validation
    all_conditions_pass = all(
        r['test1_passed'] and r['test2_passed']
        for r in results.values()
    )

    return results, all_conditions_pass
```

### Training Protocol

**No new training required.** This hypothesis performs post-hoc analysis on h-m1 training artifacts.

### Evaluation

**Success Criteria (from Phase 2B):**

**Primary (MUST satisfy for gate pass):**
- Final weight configurations differ significantly across seeds for all 4 conditions
  - Metric: Mean pairwise Euclidean distance > 0
  - Statistical test: One-sample t-test, p < 0.05
  - Conditions: 1layer_mnist, 1layer_fashion_mnist, 2layer_mnist, 2layer_fashion_mnist

**Secondary (SHOULD satisfy):**
- Loss trajectories show measurable divergence
  - Metric: Coefficient of variation (CV) of final epoch loss ≥ 1%
  - All 4 conditions

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Statistical analysis (pairwise distances, CV calculation)
- Library: scipy.stats, numpy
- Code:
```python
from scipy.spatial.distance import pdist, squareform
from scipy.stats import ttest_1samp
import numpy as np

# Pairwise distances
distances = pdist(weight_matrix, metric='euclidean')

# CV calculation
cv = (np.std(values) / np.mean(values)) * 100

# Statistical test
t_stat, p_value = ttest_1samp(distances, 0, alternative='greater')
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**:
  - 4-panel figure (one per condition)
  - Panel A: Final weight distance distribution (histogram + mean line)
  - Panel B: Loss trajectory fan chart (all 30 runs overlaid, final epoch CV annotated)

#### Additional Figures (LLM Autonomous)

**Recommended visualizations:**
1. **Initial vs Final Distance Correlation**: Scatter plot showing relationship between initial weight distance and final weight distance
2. **Trajectory Divergence Timeline**: Plot showing how CV of loss increases over epochs (demonstrates when divergence occurs)
3. **Weight Space Projection**: 2D PCA/t-SNE projection of final weight configurations (visualizes clustering/separation)

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 Mechanism Verification Check

**Gate Pass Condition (MUST_WORK):**
1. Primary criterion satisfied for all 4 conditions (p < 0.05, distance > 0)
2. At least 2/4 conditions satisfy secondary criterion (CV ≥ 1%)

**If fails:**
- EXPLORE action: MNIST MLP may have dominant attractor despite different initializations
- Document: "Optimization converges to similar solutions regardless of initialization"
- Implication: CLT assumption violated, h-m3 cannot proceed

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions (Must be TRUE before experiment)

| Check | Description | Status |
|-------|-------------|--------|
| Mechanism Exists | h-m1 training artifacts exist (weights, losses) | TRUE (prerequisite h-m1 PASSED) |
| Mechanism Isolatable | Can analyze with/without mechanism (N/A for analysis-only) | N/A (analysis validates mechanism post-hoc) |
| Baseline Measurable | h-m1 data provides baseline measurements | TRUE (h-m1 completed successfully) |

### Architecture Compatibility Check

**Analysis Requirements:**
- h-m1 must have saved:
  - Initial weights for all 30 seeds × 4 conditions
  - Final weights for all 30 seeds × 4 conditions
  - Loss trajectories (10 epochs) for all 30 seeds × 4 conditions

**Required Files:**
- `h-m1/results/{condition}/seed_{i}/initial_weights.pt` (120 files total)
- `h-m1/results/{condition}/seed_{i}/final_weights.pt` (120 files total)
- `h-m1/results/{condition}/seed_{i}/loss_history.npy` (120 files total)

> ⚠️ If h-m1 artifacts missing, Phase 4 MUST fail early with clear error message!

### Mechanism Activation Indicators

**How to detect if mechanism validation actually executed:**

| Indicator Type | Expected Signal | Code Location |
|---------------|-----------------|---------------|
| File Existence | All 120 weight/loss files loaded successfully | analysis.py:load_artifacts() |
| Distance Calculation | Pairwise distances computed for all 4 conditions | analysis.py:compute_distances() |
| Statistical Tests | t-test + CV computed for all conditions | analysis.py:run_statistical_tests() |

**Activation Verification Code:**

```python
def verify_h_m2_analysis_complete(results):
    """Verify h-m2 mechanism validation completed all required tests."""
    indicators = {
        "artifacts_loaded": all(
            len(results[cond]['initial_weights']) == 30 and
            len(results[cond]['final_weights']) == 30 and
            len(results[cond]['loss_trajectories']) == 30
            for cond in results.keys()
        ),
        "distances_computed": all(
            'mean_final_distance' in results[cond]
            for cond in results.keys()
        ),
        "tests_executed": all(
            'final_distance_p_value' in results[cond] and
            'cv_final_loss_percent' in results[cond]
            for cond in results.keys()
        ),
        "all_conditions_tested": len(results) == 4
    }
    return all(indicators.values()), indicators
```

### Mechanism Failure Detection

| Failure Mode | Detection Method | Action |
|--------------|------------------|--------|
| Missing h-m1 data | File not found errors during artifact load | FAIL: h-m1 prerequisite incomplete, cannot proceed |
| Zero distances | All pairwise distances == 0 | FAIL: Weights identical across seeds (determinism error) |
| p-value >= 0.05 | Statistical test fails significance (any condition) | FAIL: Primary criterion not met, mechanism not validated |
| CV < 1% all conditions | Loss trajectories too similar across all conditions | WARNING: Secondary criterion weak (document but continue) |

### Success Criteria (Mechanism Level)

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Artifacts Loaded | 120/120 files exist and loadable | File existence + torch.load() success |
| Primary Gate (MUST_WORK) | p < 0.05 for ALL 4 conditions | One-sample t-test (distances > 0) |
| Secondary | CV ≥ 1% for ≥2/4 conditions | Coefficient of variation of final epoch losses |
| Overall Gate | Primary satisfied | MUST_WORK gate determines hypothesis pass/fail |

---

## Appendix: Reference Implementations

**PyTorch Pairwise Distance:**
- URL: https://docs.pytorch.org/docs/stable/generated/torch.nn.PairwiseDistance.html
- Purpose: Standard L2 distance computation

**Scipy Pairwise Distances:**
- URL: https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.distance.pdist.html
- Purpose: Efficient all-pairs distance matrix computation

**ArXiv - Optimization Trajectories Analysis:**
- URL: https://arxiv.org/html/2403.07379v1
- Purpose: Methodology for analyzing training trajectory divergence

**ArXiv - Weight Distance Information Theory:**
- URL: https://arxiv.org/pdf/2102.00396
- Purpose: Validates using weight distance to measure training dynamics

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-03-21T00:00:00Z

### Workflow History for This Hypothesis
- 2026-03-21: Phase 2C started
- Prerequisite h-m1 PASSED (2026-03-21T02:22:07Z)

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
