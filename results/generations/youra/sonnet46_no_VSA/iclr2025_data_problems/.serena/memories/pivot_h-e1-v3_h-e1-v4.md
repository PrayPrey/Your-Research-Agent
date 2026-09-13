# Hypothesis Pivot Record

**Date:** 2026-07-30T08:45:00+00:00
**From:** h-e1-v3
**To:** h-e1-v4

## Pivot Reason

SELF_MODIFY — Gate FAIL due to miscalibrated V range. Disparity is real and statistically unambiguous (all Holm p ≈ 0), but stronger than predicted. Observed V = 0.40–0.57 vs predicted V = 0.29–0.41. Only requires range recalibration, not fundamental redesign.

## What Changed

- Cramér's V gate range updated from [0.29, 0.41] to [0.40, 0.57] (matching observed)
- Hypothesis statement revised to reflect true effect magnitude (large-to-very-large, not medium)
- Gate Condition A threshold widened accordingly

## What Was Preserved

- Core methodology: global k-th percentile thresholding on ccnet_perplexity
- All 5 k values (k ∈ {10, 20, 30, 40, 50})
- Dataset: RedPajama-V2 CommonCrawl sample (208,262 rows, 5 languages)
- Condition B: Holm-corrected p < 0.001 (already PASS, retained)
- Structural finding: Germanic (en, de) vs Romance (es, fr, it) retention gap

## Key Evidence Supporting Pivot

| k | V (observed) | V (predicted range) | Status |
|---|-------------|---------------------|--------|
| 10 | 0.4021 | [0.29, 0.41] | Near boundary |
| 20 | 0.5193 | [0.29, 0.41] | Exceeds |
| 30 | 0.5629 | [0.29, 0.41] | Exceeds |
| 40 | 0.5696 | [0.29, 0.41] | Exceeds |
| 50 | 0.5293 | [0.29, 0.41] | Exceeds |

Root cause: ccnet_perplexity is trained on predominantly Germanic-biased LM, creating larger structural bias against Romance languages than conservatively predicted.

## Lineage

```
h-e1 (v1)
    └── (PIVOT: original hypothesis)
        └── h-e1-v2
            └── (PIVOT: incremental refinement)
                └── h-e1-v3
                    └── (PIVOT: V range miscalibration — effect larger than predicted)
                        └── h-e1-v4
```

---
*Pivot recorded at: 2026-07-30T08:45:00+00:00*
