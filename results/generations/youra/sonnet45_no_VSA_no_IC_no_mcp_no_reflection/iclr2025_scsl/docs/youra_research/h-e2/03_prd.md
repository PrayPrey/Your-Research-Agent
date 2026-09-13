# Product Requirements Document: h-e2

**Date:** 2026-08-28  
**Author:** Anonymous  
**Hypothesis:** h-e2 - Spurious features exhibit lower gradient variance and forgetting rate  
**Version:** 1.0

---

## Executive Summary

Implement gradient variance tracking and forgetting event measurement to validate that spurious features in deep learning exhibit lower gradient variance (V_spurious/V_core < 0.7) and lower forgetting rate compared to core features. Builds on h-e1's validated temporal ordering foundation by extending the same ablation-trained networks with gradient and prediction tracking infrastructure.

**Key Success Metrics:**
- Gradient variance ratio V_spurious/V_core < 0.7 (F-test, p < 0.05)
- Forgetting rate: spurious < core (paired t-test, p < 0.05)
- Partial correlation significant after controlling for convergence epoch

---

## Problem Statement

Prior work shows spurious features converge earlier than core features (validated in h-e1), but training dynamics beyond convergence timing remain unexplored. Understanding gradient variance and forgetting patterns is critical for:

1. Explaining why models rely on spurious correlations despite their instability
2. Designing early-stopping criteria that avoid spurious feature overfitting
3. Informing bias mitigation strategies based on training dynamics

**Hypothesis Statement:** Spurious features exhibit lower gradient variance (V_spurious < V_core, variance ratio < 0.7) and lower forgetting rate than core features.

**Prerequisites:** h-e1 (COMPLETED) - provides ablation-trained networks and convergence epochs

---

## Functional Requirements

### FR-1: Dataset Infrastructure (Reuse from h-e1)
**Priority:** P0 (Critical)  
**Description:** Use CMNIST dataset with color-digit correlation (95% train, 10% test)

**Acceptance Criteria:**
- Reuse h-e1 CMNIST loader implementation
- 50k train, 10k test splits
- Color augmentation: 10 colors × 10 digits mapping
- Dataset cached at `./data/mnist`

**Data Source:**
- Method: torchvision.datasets.MNIST + color augmentation
- Preprocessing: Normalize [0,1], apply color mapping

### FR-2: Ablation Model Training (Extend h-e1)
**Priority:** P0 (Critical)  
**Description:** Train 3 ablation variants to isolate spurious vs core features

**Ablation Variants:**
1. **Spurious-only:** Color-only cues (masked digit shapes)
2. **Core-only:** Grayscale images (no color)
3. **Baseline:** Standard CMNIST (both features)

**Acceptance Criteria:**
- ResNet-18 architecture (11M params, pretrained=False)
- Modified first conv: 3×28×28 input
- SGD optimizer (lr=0.001, momentum=0.9, weight_decay=0.0001)
- 30 epochs, batch_size=256
- 10 random seeds for statistical tests

### FR-3: Gradient Variance Tracking
**Priority:** P0 (Critical)  
**Description:** Log per-parameter gradients and compute rolling 3-epoch variance

**Implementation Requirements:**
```python
class GradientVarianceTracker:
    - window_size = 3 epochs
    - Store grad_history per parameter
    - Compute variance for spurious vs core feature parameters
    - Filter parameters by feature type using ablation network masks
```

**Acceptance Criteria:**
- Gradient norms logged every batch
- Rolling variance computed at epochs 10, 20, 30
- Separate variance metrics for spurious-only vs core-only networks
- Variance ratio V_spurious/V_core < 0.7 threshold

### FR-4: Forgetting Event Tracking (Toneva et al. 2019)
**Priority:** P0 (Critical)  
**Description:** Track per-sample prediction flips across epochs

**Implementation Requirements:**
```python
class ForgettingTracker:
    - Log predictions per sample per epoch
    - Count forgetting events (correct→incorrect flips)
    - Compute mean forgetting rate per feature type
```

**Acceptance Criteria:**
- Predictions stored for all 50k training samples
- Forgetting events counted across 30 epochs
- Separate forgetting metrics for spurious vs core features
- Forgetting_spurious < Forgetting_core directional check

**Reference:** https://github.com/mtoneva/example_forgetting

### FR-5: Statistical Validation
**Priority:** P0 (Critical)  
**Description:** Run statistical tests to validate hypothesis claims

**Tests Required:**
1. **F-test:** Variance ratio (H0: V_spurious/V_core = 1)
2. **Paired t-test:** Forgetting rates across 10 seeds
3. **Partial correlation:** Control for convergence epoch E_s

**Acceptance Criteria:**
- F-test p-value < 0.05 for variance ratio
- Paired t-test p-value < 0.05 for forgetting difference
- Partial correlation coefficient significant (p < 0.05)
- Results aggregated across 10 seeds

### FR-6: Visualization Generation
**Priority:** P1 (High)  
**Description:** Generate figures for gate metrics and training dynamics

**Required Figures:**
1. **Gate Metrics Comparison:** Bar chart (variance ratio, forgetting rate: spurious vs core)
2. **Rolling Gradient Variance:** Line plot (V_spurious, V_core over epochs 1-30, ±1 std shaded)
3. **Forgetting Events Heatmap:** Samples × epochs, color = flip frequency
4. **Partial Correlation Analysis:** Scatter plot (forgetting vs E_s, controlling for variance)

**Acceptance Criteria:**
- All figures saved to `h-e2/figures/`
- Figure generation logic embedded in experiment code
- Publication-quality formatting (300 DPI, labeled axes)

### FR-7: PoC Validation (Seed 0 Only)
**Priority:** P0 (Critical)  
**Description:** Quick directional check before full 10-seed validation

**PoC Pass Criteria:**
1. Code runs without error (30 epochs × 3 models)
2. V_spurious/V_core < 0.7 (direction-based, no stats)
3. Forgetting_spurious < Forgetting_core (direction-based)

**Acceptance Criteria:**
- PoC completes in <1 hour on single GPU
- Directional confirmation sufficient (no F-test for PoC)
- Full statistical validation runs after PoC pass

---

## Non-Functional Requirements

### NFR-1: Performance
- Training time: ~3 hours total (10 seeds × 3 models × 30 epochs)
- Hardware: 1× GPU (V100/A100)
- Memory: <16GB GPU RAM per model

### NFR-2: Reproducibility
- Fixed random seeds (0-9 for 10 runs)
- Deterministic operations (torch.backends.cudnn.deterministic=True)
- Requirements.txt with exact package versions

### NFR-3: Code Quality
- Reuse h-e1 infrastructure (CMNIST loader, ablation training setup)
- Modular tracker classes (GradientVarianceTracker, ForgettingTracker)
- Documented assumptions (window_size=3, variance computation method)

### NFR-4: Output Artifacts
- CSV: variance_ratio.csv, forgetting_rates.csv (10 seeds × 3 epochs)
- Figures: 4 plots saved to h-e2/figures/
- Logs: Training logs with per-epoch variance and forgetting metrics

---

## Success Criteria

### Gate Condition (SHOULD_WORK)
- **Primary:** V_spurious/V_core < 0.7 AND Forgetting_spurious < Forgetting_core (both p < 0.05)
- **Secondary:** Partial correlation significant (p < 0.05)

**Gate Failure Handling:**
- Failure documented as limitation
- Workflow continues (does not block dependent hypotheses)
- Results inform design of future hypotheses

### Metrics
1. **Quantitative:**
   - Variance ratio: V_spurious/V_core = 0.65 ± 0.05 (target)
   - Forgetting rate difference: Δ = 2.5 ± 0.8 events/sample (target)
   - Statistical power: p < 0.05 across all 3 tests

2. **Qualitative:**
   - Gradient variance stabilizes earlier for spurious features (visual inspection)
   - Forgetting events concentrated in core-only networks (heatmap pattern)

---

## Dependencies & Constraints

### Internal Dependencies
- **h-e1 codebase:**
  - CMNIST data loader
  - Ablation training setup (spurious-only, core-only, baseline)
  - Convergence epochs E_s, E_c (13, 17 from h-e1 PoC)

### External Dependencies
- PyTorch >= 1.10
- torchvision (MNIST dataset)
- NumPy (variance computation)
- SciPy (F-test, t-test, partial correlation)
- Matplotlib (visualization)

### Constraints
- **Scope Limitation:** CMNIST only (Waterbirds/CelebA/NICO++ require manual setup, deferred to future work)
- **Statistical Power:** 10 seeds required for reliable t-test (Cohen's d estimation)
- **Compute Budget:** ~3 GPU-hours total

---

## Out of Scope

- Multi-dataset validation (Waterbirds, CelebA, NICO++)
- Alternative variance metrics (per-layer, per-sample)
- Causal analysis of variance-forgetting relationship
- Online forgetting tracking (batch-level instead of epoch-level)

---

## Implementation Notes

### Reuse from h-e1
- CMNIST loader: `h-e1/data/cmnist_loader.py`
- Ablation training loop: `h-e1/train.py`
- ResNet-18 architecture: `h-e1/models/resnet.py`

### New Components
- `trackers/gradient_variance.py`: GradientVarianceTracker class
- `trackers/forgetting_events.py`: ForgettingTracker class (Toneva et al. 2019 implementation)
- `analysis/statistical_tests.py`: F-test, t-test, partial correlation wrappers

### Configuration
```yaml
# h-e2/config.yaml
dataset: cmnist
model: resnet18
optimizer:
  type: sgd
  lr: 0.001
  momentum: 0.9
  weight_decay: 0.0001
training:
  epochs: 30
  batch_size: 256
  num_seeds: 10
trackers:
  gradient_variance:
    window_size: 3
    checkpoint_epochs: [10, 20, 30]
  forgetting:
    log_interval: 1  # every epoch
thresholds:
  variance_ratio: 0.7
  p_value: 0.05
```

---

## Validation Plan

### Phase 4 PoC (Seed 0)
1. Run single seed (seed=0) for 30 epochs
2. Check V_spurious/V_core < 0.7 (direction only)
3. Check Forgetting_spurious < Forgetting_core (direction only)
4. Expected runtime: <1 hour

### Full Validation (10 Seeds)
1. Run seeds 0-9 in parallel (if compute available)
2. Aggregate variance ratios: F-test across seeds
3. Aggregate forgetting rates: Paired t-test across seeds
4. Compute partial correlation controlling for E_s
5. Expected runtime: ~3 hours (parallel) or ~30 hours (sequential)

---

## Appendix

### Reference Implementations
- **Gradient hooks:** https://pytorch.org/docs/stable/generated/torch.Tensor.register_hook.html
- **Forgetting metric:** https://github.com/mtoneva/example_forgetting
- **Ablation training:** h-e1 implementation (validated)

### Related Hypotheses
- **h-e1 (prerequisite):** Temporal ordering foundation (E_spurious < E_core)
- **Future work:** Extend to Waterbirds/CelebA/NICO++ datasets

---

*This PRD is implementation-ready for Phase 4 Coding. All specifications grounded in Phase 2C experiment design and h-e1 validated infrastructure.*
