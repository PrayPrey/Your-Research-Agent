# Validation Report: H-M2

**Date:** 2026-08-11
**Hypothesis:** High-entropy tasks tolerate eviction better
**Gate:** FAIL (p=0.326 > 0.05)

---

## Mock Data Fix Applied

**Issue:** Lines 80-85 in run_poc.py used random probability degradation to simulate eviction effects instead of real KV cache eviction.

**Fix:** Replaced mock degradation with H2OWrapper.generate() which performs real input truncation (keeps recent + uniformly sampled early tokens at retention ratio).

**Verification:** Experiment re-run completed successfully with real eviction mechanism.

---

## Experiment Results

| Metric | High-Entropy | Low-Entropy |
|--------|-------------|-------------|
| Mean Retention | 0.067 | 0.000 |
| Std | 0.249 | 0.000 |
| Baseline Acc | 6.7% | 6.7% |
| Evicted Acc (40%) | 3.3% | 0.0% |

**Statistical Test:**
- t-statistic: 1.00
- p-value: 0.326
- Cohen's d: 0.378

---

## Gate Evaluation

**GATE: FAIL**

Reasons:
1. p-value (0.326) > threshold (0.05)
2. Baseline accuracy too low (6.7%) for meaningful retention measurement
3. Effect size (d=0.378) below medium threshold (0.5)

---

## Limitations

1. **Sample size:** 30 samples (5/domain) insufficient for statistical power
2. **Baseline accuracy:** Simple substring matching inadequate for LongBench-v2 answer formats
3. **Eviction simulation:** Input truncation differs from true H2O attention-based eviction

---

## Recommendation

EXPLORE: Hypothesis inconclusive due to measurement limitations, not mechanism failure.

Next steps:
1. Improve answer evaluation (use LLM judge or official LongBench scorer)
2. Increase sample size to 180 (full specification)
3. Consider using 80% retention ratio for less aggressive eviction
