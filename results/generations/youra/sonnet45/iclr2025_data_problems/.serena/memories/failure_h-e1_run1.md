# Phase 4 Failure Record: h-e1 (Run 1)

**Date:** 2026-03-17T04:00:00Z
**Hypothesis:** h-e1
**Run:** 1
**Final Status:** FAIL
**Failure Type:** MUST_WORK_FAIL

## Experiment Results

| Check | Actual | Threshold | Passed |
|-------|--------|-----------|--------|
| ANOVA interaction p-value | 0.8844 | < 0.01 | ❌ |
| Source-TracIn LDS gap (High-KL) | 0.022 | ≥ 0.05 | ❌ |
| LoRIF non-inferiority | -0.0118 | ≤ 0.02 | ✅ |
| Storage ratio | 0.4733 | ≤ 0.20 | ❌ |

**Pass Rate:** 1/4 (0.25) — FAIL (needed ≥ 3/4 for PARTIAL)

## LDS Results by Method and Regime

| Method | Low-KL | High-KL |
|--------|--------|---------|
| Source | 0.0647 | 0.0362 |
| TracIn | 0.0607 | 0.0077 |
| LoRIF | 0.0763 | 0.0116 |
| TrackStar | 0.0663 | 0.0142 |

## Root Cause Analysis

1. **Regime simulation insufficient**: KL=1.2244 between OLMo-1B-hf and OLMo-1B-0724-hf is too small to produce regime-conditional effects detectable at PoC scale (n=1000 train samples, 500 queries)
2. **Small effect size**: Source > TracIn direction is confirmed (High-KL: 0.0362 vs 0.0077), but gap = 0.0285 is far below the required 0.05 threshold
3. **Storage ratio measurement bug**: LoRIF storage was ~47% of Source reference, not the claimed 5× (0.2×) reduction. Reference baseline computation is incorrect.
4. **Scale too small for ANOVA**: With n=1000/500 PoC scale, ANOVA interaction variance is overwhelmed by noise (p=0.8844)

## Lessons Learned

1. Need much larger KL divergence between regimes (>>1.22) — consider OLMo-7B multi-stage checkpoints with KL > 2.0
2. PoC scale (n=1000) is insufficient for ANOVA Method×Regime interaction detection — need at least n=5000-10000
3. Storage ratio computation must use consistent reference (LoRIF compressed vectors vs. Source full gradients)
4. Direction of effect is correct (Source > TracIn in High-KL regime, LoRIF non-inferior in Low-KL) — phenomenon may exist but requires proper experimental scale
5. Real data confirmed (real OLMo checkpoints, real T-REx, real TracIn) — failure is NOT a data quality issue

## Feedback for Phase 0 Redesign

### What Showed Promise
- LoRIF non-inferiority confirmed in Low-KL regime (gap = -0.0118 LDS, within tolerance)
- Source > TracIn directional trend confirmed in High-KL (direction correct, magnitude insufficient)
- Real dataset pipeline works (WikiText-103, T-REx, OLMo checkpoints)

### What NOT To Do
- Do not use OLMo-1B checkpoints for regime stratification — KL difference too small
- Do not test at n=1000 PoC scale for interaction effects — statistical power too low
- Do not use arbitrary storage ratio reference — define explicit reference baseline

### Suggested Modifications for Redesign
- Use OLMo-7B with KL > 2.0 between stages (or explicitly trained multi-stage with distinct checkpoints)
- Scale to n=5000+ training samples, 1000+ queries for adequate ANOVA power
- Fix storage ratio: measure LoRIF (rank-64 SVD vectors) vs Source (full gradient vectors) per sample

## Routing Decision

- **Outcome:** ROUTED_TO_PHASE_0
- **Reason:** FOUNDATION hypothesis failed MUST_WORK gate — methodology doesn't work at PoC scale; Phase 0 redesign required
- **Dependents cascade-failed:** h-m1 (CASCADE_FAILED, prerequisite h-e1 failed)

---
*For cross-phase reference*
*Written at: 2026-03-17T04:00:00Z*
