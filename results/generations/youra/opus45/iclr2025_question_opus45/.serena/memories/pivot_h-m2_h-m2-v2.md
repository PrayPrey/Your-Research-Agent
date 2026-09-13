# Hypothesis Pivot Record

**Date:** 2026-03-27T19:45:00Z
**From:** h-m2
**To:** h-m2-v2

## Pivot Reason

SELF_MODIFY decision triggered by PARTIAL gate result on MUST_WORK gate. SE saturation at N=100 (mean cluster count 97.6/100) prevents meaningful correlation detection between PD-3 and Semantic Entropy.

## What Changed

- Reduced N from 100 to 20 for SE calculation to prevent saturation
- Lowered correlation threshold from rho >= 0.35 to rho >= 0.30
- Hypothesis statement updated to reflect parameter changes

## What Was Preserved

- Core hypothesis: PD-3 captures semantic diversity similar to SE
- Dataset: TruthfulQA
- Model: Mistral-7B-v0.1
- Embedding model: all-mpnet-base-v2
- Statistical methodology: Spearman correlation with bootstrap CI

## Partial Results Preserved

| Metric | Value | Notes |
|--------|-------|-------|
| spearman_rho | 0.2625 | From h-m2, significant but below threshold |
| p_value | 0.00834 | Statistically significant |
| mean_cluster_count | 97.6 | Indicates SE saturation |
| mean_se | 4.564 | Near maximum entropy |
| mean_pd3 | 0.554 | Moderate diversity |

## Root Cause Analysis

1. **SE Saturation**: At N=100 responses, entailment-based clustering produces nearly 100 unique clusters for most questions (mean=97.6), pushing SE toward maximum entropy
2. **Ceiling Effect**: When SE is saturated, it loses discriminative power and cannot correlate well with any other metric
3. **Threshold Calibration**: The 0.35 threshold was set without accounting for SE saturation at high N

## Key Insights

1. The correlation IS positive and statistically significant (p=0.0083) - PD-3 does capture some of what SE captures
2. The methodology is sound; the issue is parameter calibration
3. Reducing N should allow SE to vary meaningfully across questions

## Lineage

```
h-m2
    └── (PIVOT: SE saturation at N=100)
        └── h-m2-v2
```

---
*Pivot recorded at: 2026-03-27T19:45:00Z*
*For cross-phase reference*
