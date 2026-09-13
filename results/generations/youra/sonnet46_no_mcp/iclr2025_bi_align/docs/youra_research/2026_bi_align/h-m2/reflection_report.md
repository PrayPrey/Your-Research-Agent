# Reflection Report: h-m2
**Generated:** 2026-05-03T10:35:00Z
**Mode:** UNATTENDED self-recovery
**Gate Type:** SHOULD_WORK
**Outcome:** LIMITATION_RECORDED

---

## 1. Experiment Summary

| Field | Value |
|-------|-------|
| Hypothesis | h-m2 (Round-Stratified Label-Distribution Coefficient Shift) |
| Dataset | Anthropic HH-RLHF, 160,800 rows, 3 rounds |
| Gate Result | PARTIAL (n_directional=1/3) |
| Bootstrap Iters | 2000 (stratified resamples) |
| Runtime | ~2.5 min |

**Coefficient Results:**

| Feature | Early β | Late β | Δ | Non-Overlap |
|---------|---------|--------|---|-------------|
| β_L (verbosity) | -0.0248 | +0.0555 | +0.0803 | **YES** ✓ |
| β_H (hedging) | -0.0290 | -0.0081 | +0.0210 | no |
| β_S (structured) | -0.0022 | +0.0095 | +0.0116 | no |

Gate threshold: n_directional ≥ 2. Achieved: 1/3. → **PARTIAL**

---

## 2. Self-Recovery Analysis

**Attempt:** 0 of max 3

**Question: Can code modification improve n_directional from 1 → 2?**

### 2a. β_H Analysis (Δ = +0.021)
- Early 95% CI: [-0.048, -0.011]
- Late 95% CI: [-0.024, +0.007]
- Overlap: early upper (-0.011) > late lower (-0.024) → overlap confirmed
- The late CI includes negative values — hedging coefficient direction is not stable
- Signal noise ratio insufficient for non-overlap with 2000 bootstrap resamples
- **Verdict: Data-level limitation. Not fixable by code change.**

### 2b. β_S Analysis (Δ = +0.012)
- Early 95% CI: [-0.021, +0.010]
- Late 95% CI: [+0.004, +0.016]
- Overlap: early upper (+0.010) > late lower (+0.004) → marginal overlap
- β_S late CI is positive (supports direction) but barely overlaps with early CI
- Increasing bootstrap_iters would not widen CIs; more data could narrow them
- The HH-RLHF dataset is fully used (160K rows); no more data available
- **Verdict: Marginal overlap is a real scientific result, not a bug.**

### 2c. Root Cause Assessment
The core issue is identical to that documented in H-E1 and H-M1:
- HH-RLHF lacks genuine temporal metadata (round numbers are index partitions, not timestamps)
- Round 1 vs Round 3 stratification by index position creates pseudo-temporal signal
- The verbosity feature (β_L) captures the strongest stylistic signal and shows clear shift
- Hedging and structured-reasoning features have weaker stylistic loading in short HH-RLHF texts
- **No code modification can create temporal signal that is absent in the data**

---

## 3. Decision

**LIMITATION_RECORDED** — No improvement path identified.

The PARTIAL result (n_directional=1/3) is a genuine scientific finding:
- β_L shows directional shift consistent with H-AAI-v1 hypothesis
- β_H and β_S shifts are positive in direction but not statistically robust
- This is consistent with H-E1's null result on interaction effects
- The data limitation (index-based round partitioning) is a cross-hypothesis finding

---

## 4. Limitation Record

```yaml
hypothesis_id: h-m2
gate_type: SHOULD_WORK
gate_result: PARTIAL
n_directional: 1
n_directional_target: 2
limitation_type: DATA_SIGNAL_WEAKNESS
limitation_description: >
  Round stratification by index partition (not genuine temporal metadata) produces
  insufficient signal for β_H and β_S non-overlap. β_L (verbosity) shows significant
  directional shift, consistent with H-E1 findings. This is a shared data limitation
  across H-E1, H-M1, and H-M2.
improvement_path: null
retry_recommended: false
continue_to_phase5: true
```

---

## 5. Implications for Downstream Hypotheses

- **H-M3** (prerequisite: h-m2): h-m2 completes as LIMITATION_RECORDED (SHOULD_WORK partial). Pipeline continues — SHOULD_WORK partial does not block dependents.
- The β_L finding provides partial empirical support for H-M3's reward model training hypothesis.
- H-M3 should focus on verbosity (β_L) as the primary coefficient signal.

---

## 6. Lessons Learned

1. **Index-based temporal proxies are weak:** HH-RLHF round partitioning by index produces marginal signal for hedging and structured-reasoning features.
2. **β_L (verbosity) is the most robust stylistic signal:** Consistent across H-E1 and H-M2, verbosity captures the clearest preference shift.
3. **SHOULD_WORK gates are appropriate here:** The partial success is scientifically meaningful and does not warrant pipeline termination.
4. **Bootstrap CI width is data-driven:** 2000 resamples with 160K rows already provides stable CI estimates; the overlap is real.
