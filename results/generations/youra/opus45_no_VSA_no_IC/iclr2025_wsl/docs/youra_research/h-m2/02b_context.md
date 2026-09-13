# H-M2 Context (JIT Generated)

**Generated**: 2026-08-24
**Source**: 02b_verification_plan.md + H-M1 validation results

---

## Hypothesis Information

- **ID**: H-M2
- **Type**: MECHANISM
- **Statement**: At N=500 training models, NFN R² exceeds MLP R² by at least 0.1 (p < 0.05)
- **Gate**: MUST_WORK
- **Prerequisites**: H-M1 (COMPLETED)

---

## Experimental Setup (from Phase 2B)

- **Dataset**: Model Zoo ResNet-20/CIFAR-10 weights
- **Training Sizes**: N=500 (primary focus for this hypothesis)
- **Test Size**: 500 held-out models (fixed)
- **Methods**: NFN vs MLP baseline
- **Seeds**: 10 per (N, method) pair for statistical significance

---

## Previous Hypothesis Results (H-M1)

- **NFN R²**: 0.9952 (target was 0.85)
- **Equivariance**: 100% pass rate (max error 8.94e-08)
- **Statistics baseline R²**: 0.9996
- **Status**: NFN architecture validated, training stable

---

## Gate Condition

**Success Criteria**: NFN R² - MLP R² ≥ 0.1 at N=500 with p < 0.05 (paired t-test or similar)

**Rationale**: If NFN's architectural equivariance provides data efficiency, it should outperform data-hungry MLP baselines at low sample counts.

---

## Controlled Variables

- Fixed architecture: ResNet-20
- Fixed test set: 500 models
- Same preprocessing, features, training protocol as H-M1
