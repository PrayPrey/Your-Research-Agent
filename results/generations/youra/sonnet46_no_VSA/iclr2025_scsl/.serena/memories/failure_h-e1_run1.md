# Phase 4 Failure Record: h-e1 (Run 1)

**Date:** 2026-08-03T17:35:00+00:00
**Hypothesis:** h-e1
**Run:** 1
**Final Status:** FAIL
**Failure Type:** MUST_WORK_FAIL — CV_time AUROC far below threshold

## Hypothesis Statement

CV_time (temporal CV of per-sample last-layer gradient norms, full-batch, epochs 16-20) achieves AUROC >= 0.90 for minority membership prediction, DELTA-AUROC >= 0.05 over loss_epoch20, Spearman rho < 0.9, and conditional AUROC > 0.55 within >= 3/5 loss-quantile bins in >= 4/5 seeds on Waterbirds 95% spuriosity.

## Performance Gap

| Metric | Ours (seed avg) | Target | Gap |
|--------|-----------------|--------|-----|
| AUROC_cvtime | ~0.603 (0.573–0.633) | ≥ 0.90 | −0.297 |
| DELTA_AUROC vs loss | ~−0.289 | ≥ +0.05 | −0.339 |
| Spearman rho | ~0.243 | < 0.9 | ✓ PASS |
| Conditional AUROC bins pass | ~50% (seed0), ~43% (seed1) | ≥ 3/5 bins in ≥4/5 seeds | FAIL |
| Seeds passed | 0/2 tested | ≥ 4/5 | FAIL |

Per-epoch loss AUROC was consistently high (~0.897), confirming loss IS discriminative.
CV_time (temporal variance) was not discriminative at all — minority/majority means nearly identical:
- Seed 0: minority=0.140, majority=0.117 (18% difference, insufficient)
- Seed 1: minority=0.115, majority=0.104 (10% difference, insufficient)

## Root Cause Analysis

1. **Fundamental signal weakness**: Temporal coefficient of variation of gradient norms (epochs 16-20) provides insufficient minority-membership signal. The variance across epochs is too small and noisy to discriminate membership.
2. **Wrong feature for membership**: Full-batch gradient norm CV captures global training dynamics, not per-sample membership. The minority/majority gradient norm distributions heavily overlap.
3. **Threshold too ambitious**: AUROC ≥ 0.90 requires near-perfect discriminability; CV_time achieves only ~0.60, which is barely above chance (0.50).
4. **DELTA_AUROC negative**: CV_time is strictly *worse* than plain loss_epoch20 as a membership signal, not better as hypothesized.

## Lessons Learned

1. Temporal CV of gradient norms is not a strong membership signal on Waterbirds 95% spuriosity — loss value alone is far superior.
2. The gap between minority/majority gradient norm CV is too small (~10-18%) to achieve AUROC ≥ 0.90.
3. If the mechanism is gradient-based, consider per-sample gradient *magnitude* at single epoch rather than *temporal variance* — less noise.
4. Alternative: Use loss trajectory variance (not gradient norm variance) as the temporal signal.
5. The 0.90 AUROC threshold for membership prediction is very high — consider whether a lower threshold (e.g., 0.75) combined with a different signal could be more realistic.
6. Dataset Waterbirds 95% spuriosity: minority group is small and the gradient norm distribution appears not cleanly separated from majority by temporal variance alone.

## Feedback for Next Phase (Phase 0 / Redesign)

### What NOT To Do
- Do not use temporal CV of last-layer gradient norms as primary membership signal
- Do not target AUROC ≥ 0.90 for a gradient-based variance signal without strong prior evidence
- Do not assume temporal variance will outperform loss value for membership prediction

### What Showed Promise
- Per-epoch loss AUROC was consistently ~0.897 → loss itself is a powerful membership signal
- Spearman rho was low (~0.24) showing CV_time and loss are NOT redundant
- Conditional AUROC per bin was sometimes >0.55, suggesting partial signal in specific loss regions

### Suggested Modifications for New Hypothesis
- Explore **loss trajectory variance** (not gradient norm variance) as temporal signal
- Explore combining CV_time with loss as a composite signal
- Consider lower AUROC threshold (0.75–0.80) for new existence hypothesis
- Consider per-sample gradient direction change (angle between epochs) rather than norm CV
- Alternative existence check: AUROC ≥ 0.75 for any gradient-based temporal feature

---
*Failure recorded at: 2026-08-03T17:35:00+00:00*
*For cross-phase reference*
