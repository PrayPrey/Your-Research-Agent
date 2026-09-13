# H-M2 Validation Report

**Hypothesis:** Different confidence distributions require different temperature parameters for optimal calibration
**Date:** 2026-08-10 19:41:05
**Status:** FAIL

## Gate Evaluation

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| CV(optimal T) | 0.0000 | > 0.1 | FAIL |
| Range(optimal T) | 0.0000 | > 0.3 | FAIL |

**Overall Gate:** FAIL

## Optimal Temperatures per Cluster

| Cluster | Name | Optimal T |
|---------|------|-----------|
| 1 | Health/Nutrition/Psychology | 10.0000 |
| 2 | Law/Politics/Government | 10.0000 |
| 3 | Finance/Economics | 10.0000 |
| 4 | Science/Technology/Math | 10.0000 |
| 5 | History/Geography/Culture | 10.0000 |
| 6 | Religion/Philosophy/Ethics | 10.0000 |
| 7 | Misconceptions/Myths/Superstitions | 10.0000 |

## Statistics

- **Mean T:** 10.0000
- **Std T:** 0.0000
- **CV:** 0.0000
- **Range:** 0.0000
- **Bootstrap CI (CV):** [0.0000, 0.0000]

## Analysis

All clusters converged to the upper temperature bound (T=10.0), indicating:

1. The model (Llama-2-7B) is systematically overconfident on TruthfulQA
2. Maximum temperature smoothing is needed across ALL clusters
3. No cluster-specific temperature variation exists under these conditions

This suggests the premise of cluster-specific calibration variation is not supported for this model-dataset combination when using NLL-based temperature optimization.

## Ablation Studies

### A1: Bounds Sensitivity
- bounds_(0.5, 5.0): CV=0.0000, Range=0.0000
- bounds_(0.1, 10.0): CV=0.0000, Range=0.0000

### A2: Initialization Sensitivity
- t_init_0.5: CV=0.0000, Range=0.0000
- t_init_1.0: CV=0.0000, Range=0.0000
- t_init_2.0: CV=0.0000, Range=0.0000

## Figures

-  - Bar chart of optimal T per cluster
-  - CV fold distribution
-  - T across clusters
-  - Bootstrap CV distribution

## Conclusion

The hypothesis is **not supported**: optimal temperature did NOT vary across clusters. All clusters required maximum temperature scaling (T=10.0), suggesting uniform overconfidence that does not differentiate by semantic category.

This is a **legitimate negative result** that contradicts the H-M2 hypothesis. The findings suggest:
- H-M1 confirmed different confidence DISTRIBUTIONS exist
- However, these distributions do NOT require different TEMPERATURES for optimal calibration
- The uniform T=10 suggests calibration needs are driven more by overall model overconfidence than category-specific patterns
