# PRD: H-C1 Prospective Structural Validity Test

**Date:** 2026-08-08
**Hypothesis:** h-c1
**Type:** CONDITION (SHOULD_WORK gate)

---

## 1. Problem Statement

H-E1 validated that PC1 (λ₁=2.277) explains 60% of variance across 6 benchmarks. But this could be dataset-specific. H-C1 tests whether **new benchmarks not used in PC1 estimation** also load ≥0.3 on frozen PC1.

## 2. Goals

1. Fetch holdout benchmarks (TrustLLM dimensions) for models overlapping with H-E1
2. Apply frozen PC1 from H-E1 to compute loadings
3. Determine if ≥2 holdout benchmarks load ≥0.3

## 3. Success Criteria

- **Primary:** At least 2 holdout benchmarks with loading ≥0.3 on frozen PC1
- **Statistical:** Report 95% CI for each loading via bootstrap

## 4. Non-Goals

- No model training
- No re-fitting PCA (frozen from H-E1)
- No new data collection beyond TrustLLM + existing models

## 5. Data Requirements

| Source | Content | Models |
|--------|---------|--------|
| H-E1 outputs | Residualized matrix, fitted PCA, PC1 scores | ~500+ |
| TrustLLM | Holdout benchmark scores | Subset with overlap |

Minimum 100 models with both H-E1 and TrustLLM scores required.

## 6. Implementation Scope

**Tier 1** (simple statistical validation):
- Load H-E1 artifacts
- Fetch TrustLLM scores
- Match models by name
- Compute correlations with frozen PC1
- Generate figures

## 7. Deliverables

1. `h_c1_results.json` - loadings, p-values, CIs
2. `figures/loading_comparison.png` - bar chart vs 0.3 threshold
3. `04_validation.md` - final report

## 8. Computational Requirements

- Time: <5 minutes
- Memory: <1GB
- GPU: Not required

---

*Phase 3 PRD for h-c1*
