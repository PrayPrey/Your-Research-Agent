# Product Requirements Document: H-C2

**Hypothesis:** Crossing point N* where NFN matches Statistics R² exists at N* < 2500
**Type:** CONDITION
**Gate:** SHOULD_WORK
**Date:** 2026-08-24

---

## 1. Objective

Find the sample size N* at which Neural Functional Networks (NFN) achieve equivalent R² performance to Statistics baseline for model accuracy prediction. Validate that N* < 2500.

## 2. Success Criteria

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Crossing point found | N* < 2500 | |NFN R² - Stats R²| < 0.03 |
| Statistical significance | p < 0.05 | Overlapping 95% CIs at N* |
| All runs complete | 100/100 | 5 N values × 2 methods × 10 seeds |

## 3. Scope

### In Scope
- NFN accuracy predictor training at N ∈ {100, 250, 500, 1000, 2500}
- Statistics baseline (linear regressor on weight features)
- 10 seeds per (N, method) pair
- R², Kendall's τ, MSE metrics
- Crossing point visualization

### Out of Scope
- N > 2500 (beyond hypothesis boundary)
- Other architectures (focus on Model Zoo CNN)
- Hyperparameter search (use paper defaults)

## 4. Data Requirements

- **Source:** Model Zoo CIFAR-10 (Zenodo 5645138)
- **Size:** 1000 CNN models
- **Split:** Variable train (100-2500), fixed test (500)
- **Labels:** Test accuracy per model

## 5. Technical Requirements

- Python 3.10+
- PyTorch 2.0+
- `pip install nfn` (official NFN library)
- scikit-learn, scipy for metrics
- matplotlib for visualization

## 6. Deliverables

1. `h-c2/experiment.py` - Main experiment script
2. `h-c2/results.json` - All metrics by N and seed
3. `h-c2/figures/crossing_point.png` - N* visualization
4. `h-c2/04_validation.md` - Validation report

## 7. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| No crossing point < 2500 | Medium | Gate fails | Log as limitation, hypothesis fails gracefully |
| NFN installation issues | Low | Blocks experiment | Fallback to local implementation |
| Model Zoo download failure | Low | Blocks experiment | Mirror data to local storage |

## 8. Dependencies

- H-M2 VALIDATED (prerequisite satisfied)
- NFN library (PyPI)
- Model Zoo dataset (Zenodo)

---

*Phase 3 Document - Implementation Planning*
