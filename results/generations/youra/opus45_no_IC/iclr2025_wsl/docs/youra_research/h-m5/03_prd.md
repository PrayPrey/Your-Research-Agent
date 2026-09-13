# Product Requirements Document: H-M5

**Hypothesis:** At N=50K, MLP probe invariance > 0.8 (learned from data diversity)
**Type:** MECHANISM
**Date:** 2026-08-12
**Status:** Phase 3 Implementation Planning

---

## Executive Summary

H-M5 tests whether MLP can learn permutation invariance from large-scale data diversity. Building on H-M4's finding that MLP learns nothing from N=1K (R²≈0), this experiment scales to N=50K to test if sufficient data exposure teaches the MLP to produce consistent outputs under weight permutations.

**Gate Condition:** MLP probe invariance > 0.8 at N=50K training scale.

---

## Problem Statement

H-M4 demonstrated that at small scale (N=1K), MLP achieves R²≈0 and the invariance metric is misleading (artificially high due to constant predictions). The question remains: can large-scale training (N=50K) enable MLP to both learn meaningful predictions AND achieve permutation invariance through data diversity alone?

---

## Functional Requirements

### FR-1: Data Pipeline
- **FR-1.1:** Load Model Zoo CIFAR-10 CNN dataset (42,547 train models)
- **FR-1.2:** Flatten CNN state_dict to weight vectors
- **FR-1.3:** Normalize weights (zero mean, unit variance)
- **FR-1.4:** Extract test_acc as regression target
- **FR-1.5:** Reserve 2,000 models for invariance testing

### FR-2: Model Implementation
- **FR-2.1:** Implement MLP-Matched architecture (Linear-ReLU-Linear-ReLU-Linear)
- **FR-2.2:** Hidden dimensions: [512, 256]
- **FR-2.3:** Input: flattened CNN weights (~50K dimensions)
- **FR-2.4:** Output: single accuracy prediction

### FR-3: Training Pipeline
- **FR-3.1:** Train with AdamW optimizer (lr=1e-3, weight_decay=1e-4)
- **FR-3.2:** CosineAnnealingLR scheduler
- **FR-3.3:** MSELoss for regression
- **FR-3.4:** 50 epochs, batch size 64
- **FR-3.5:** 10 random seeds for statistical significance

### FR-4: Invariance Evaluation
- **FR-4.1:** Compute predictions on original test weights
- **FR-4.2:** Compute predictions under 10 random permutations per model
- **FR-4.3:** Calculate correlation between original and permuted predictions
- **FR-4.4:** Report mean invariance score across test set

### FR-5: Metrics Computation
- **FR-5.1:** Test R² (sklearn.metrics.r2_score)
- **FR-5.2:** Mean probe invariance score
- **FR-5.3:** Standard deviation of invariance scores
- **FR-5.4:** Comparison with H-M4 baseline (N=1K)

### FR-6: Visualization
- **FR-6.1:** Gate metrics comparison bar chart (N=1K vs N=50K)
- **FR-6.2:** R² vs training scale curve
- **FR-6.3:** Invariance distribution histogram
- **FR-6.4:** Prediction scatter (original vs permuted)

---

## Non-Functional Requirements

### NFR-1: Reproducibility
- Fixed random seeds across all runs
- Deterministic data loading order
- Version-pinned dependencies

### NFR-2: Performance
- Training completes within 2 hours on single GPU
- Batch inference for invariance testing

### NFR-3: Code Quality
- Reuse H-M4 infrastructure where possible
- Clear separation: data_gen, model, train, evaluate

---

## Success Criteria

### Primary Gate
| Metric | Threshold | Source |
|--------|-----------|--------|
| Probe Invariance | > 0.8 | Mean across test set |

### Secondary Criteria
| Metric | Condition | Interpretation |
|--------|-----------|----------------|
| Test R² | > 0.1 | MLP must learn (unlike H-M4) |
| R² improvement | >> H-M4 | Scale enables learning |

### Gate Logic
```python
if test_r2 < 0.1:
    return "INCONCLUSIVE - MLP didn't learn"
elif mean_invariance > 0.8:
    return "PASS - MLP learned invariance from data"
else:
    return "FAIL - MLP learns but NOT invariance"
```

---

## Dependencies

### Prerequisites
- **H-M4:** COMPLETED (gate passed via mechanism confirmation)
  - Provided: MLP-Matched architecture, data loading code
  - Result: R²≈0 at N=1K, invariance metric misleading

### External Dependencies
- Model Zoo CIFAR-10 CNN dataset (Zenodo DOI: 10.5281/zenodo.6620868)
- PyTorch, sklearn, numpy, matplotlib

### Internal Dependencies
- H-M4 codebase: `h-m4/code/` (data_gen.py, mlp_model.py, test_invariance.py)

---

## Out of Scope

- NFN comparison (already validated in H-E1, H-M1, H-M2)
- Multiple architecture variants
- Hyperparameter search beyond fixed protocol

---

## Risk Assessment

| Risk | Severity | Mitigation |
|------|----------|------------|
| Dataset < 50K models | MEDIUM | Use max available (42K) |
| Memory constraints | LOW | Batch processing |
| Overfitting at large N | LOW | Weight decay, validation monitoring |

---

*Generated for Phase 3 Implementation Planning*
*Source: h-m5/02c_experiment_brief.md*
