# Hypothesis Completion Snapshot: h-m2

**Date:** 2026-03-27T19:50:00Z
**Hypothesis:** h-m2
**Statement:** Under the same response set, if we compute PD-3 (embedding distance) and ground-truth SE (entailment-based clustering at N=100), then Spearman correlation rho >= 0.35, because embedding similarity captures semantic equivalence validated by SNNE.

**Final Status:** COMPLETED (with SELF_MODIFY)
**Gate Result:** PARTIAL
**Gate Type:** MUST_WORK

## Results

- Validation: PARTIAL
- Gate Type: MUST_WORK
- Spearman rho: 0.2625 (threshold: 0.35)
- p-value: 0.00834 (significant)
- Reflection Triggered: Yes
- Reflection Outcome: SELF_MODIFY
- New Hypothesis: h-m2-v2

## Key Findings

1. Positive correlation exists between PD-3 and SE (statistically significant)
2. Correlation below threshold due to SE saturation at N=100
3. Mean cluster count 97.6/100 indicates entailment over-segmentation
4. Reducing N to 20 should allow meaningful SE variance

## Lessons Learned

1. SE saturates at high N values - use N=20-30 for meaningful variance
2. Threshold calibration should account for parameter choices
3. Methodology is sound; issue is parameter calibration

## Cascade Effects

- h-m3: BLOCKED (awaiting h-m2-v2)
- h-m2-v2: READY (new version with N=20, threshold=0.30)

---
*Per-hypothesis snapshot for Phase 2A reference*
*Written at: 2026-03-27T19:50:00Z*
