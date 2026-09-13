# Product Requirements Document: H-M4

**Hypothesis:** At N=1K, MLP probe invariance < 0.5 (insufficient data diversity)
**Type:** MECHANISM
**Gate:** SHOULD_WORK
**Date:** 2026-08-12

---

## Executive Summary

H-M4 tests whether MLP trained on limited data (N=1K) fails to learn permutation invariance. This validates the mechanism that NFN's sample efficiency advantage stems from architectural invariance rather than learnable invariance from data.

**Success Criteria:** MLP probe invariance < 0.5 at N=1K

---

## Problem Statement

H-M3 established untrained MLP lacks built-in invariance (CV=0.194). H-M4 determines whether training on 1K samples enables MLP to learn permutation invariance from data. If MLP invariance remains low (<0.5), this confirms NFN's architectural advantage cannot be replicated through data alone at small scales.

---

## Functional Requirements

### FR-1: Data Loading and Preprocessing
- Load Model Zoo CIFAR-10 CNN subset
- Sample N=1,000 models for training
- Hold out 200 models for test (20%)
- Flatten CNN weights to vector representation

### FR-2: MLP Training Pipeline
- Initialize MLP-Matched architecture (256-128-1)
- Train with AdamW optimizer, lr=1e-3
- 50 epochs, batch size 32, MSE loss
- Support 10 random seeds for statistical power

### FR-3: Probe Invariance Measurement
- For each test model: generate 10 random permutations
- Compute predictions on original and permuted weights
- Calculate coefficient of variation (CV)
- Compute invariance score: 1 - min(CV, 1.0)

### FR-4: NFN Control Measurement
- Load NFN model (pip install nfn)
- Measure probe invariance on same test set
- Expected: invariance > 0.95 (architectural guarantee)

### FR-5: Statistical Analysis
- Mean invariance across 10 seeds
- Standard deviation and confidence intervals
- Comparison: MLP invariance vs NFN invariance

### FR-6: Visualization
- Bar chart: MLP vs NFN probe invariance
- Scatter plot: permuted vs original predictions
- Histogram: invariance distribution across test models

---

## Non-Functional Requirements

### NFR-1: Reproducibility
- Fixed random seeds (0-9)
- Deterministic data loading order
- Version-pinned dependencies

### NFR-2: Performance
- Training completion < 10 minutes per seed
- Full experiment < 2 hours total

### NFR-3: Code Quality
- Modular design reusing H-M3 components
- Clear separation: data, model, training, evaluation

---

## Success Criteria

| Metric | Threshold | Expected |
|--------|-----------|----------|
| MLP Probe Invariance | < 0.5 | ~0.2-0.4 |
| NFN Probe Invariance | > 0.95 | ~0.99 |
| MLP CV | > 0.2 | ~0.3-0.5 |
| Seeds Passing | 10/10 | 10/10 |

---

## Dependencies

### Prerequisites
- H-M3 COMPLETED: Established MLP lacks built-in invariance

### Code Reuse
- H-M3: MLPMatched class, permutation generation
- H-E1: Data loading, training loop patterns

### External
- PyTorch >= 2.0
- nfn library (pip install nfn)
- Model Zoo dataset access

---

## Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| MLP learns invariance faster than expected | HIGH | Revise mechanism theory |
| NFN shows imperfect invariance | LOW | Verify NFN implementation |
| Insufficient test models | MEDIUM | Verify 200+ available |

---

## Timeline

- Epic 1: Data pipeline setup (reuse H-M3)
- Epic 2: MLP training implementation
- Epic 3: Probe invariance measurement
- Epic 4: NFN control measurement
- Epic 5: Statistical analysis and reporting
- Epic 6: Visualization generation

---

*Generated for Phase 3 Implementation Planning*
*Source: h-m4/02c_experiment_brief.md*
