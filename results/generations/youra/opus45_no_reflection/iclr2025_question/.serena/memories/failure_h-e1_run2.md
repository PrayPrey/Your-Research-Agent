# Phase 4 Failure Record: h-e1 (Run 2)

**Date:** 2026-08-19T15:55:00Z
**Hypothesis:** h-e1
**Run:** 2
**Final Status:** FAIL
**Failure Type:** MUST_WORK gate hard fail

## Performance Gap

| Metric | Ours | Baseline | Gap |
|--------|------|----------|-----|
| Best Signal Correlation (Entropy) | 0.131 | 0.75 (threshold) | -0.619 (82.5% below threshold) |
| Learned Router (test) | 0.683 (original) / -0.101 (modified) | 0.75 (threshold) | -0.067 / -0.851 |

## Root Cause Analysis

- **Signal-oracle dimension mismatch:** Heuristic signals (G-NLL, SAR, token entropy) measure token-level uncertainty; oracle measures semantic diversity of outputs → orthogonal dimensions
- **Low ensemble variance:** TruthfulQA factual Q&A generates semantically similar responses (mean variance=0.024, very low absolute magnitude)
- **Dataset characteristics:** TruthfulQA has inherently low semantic variance due to factual nature of questions
- **Insufficient sample size:** n=50 insufficient for learned router training (test set n=15 shows severe overfitting: full r=0.75 vs test r=0.68/−0.10)
- **Oracle metric issue:** Variance of cosine distances not capturing the uncertainty dimension measured by lightweight signals

## Lessons Learned

1. **Match signal and oracle dimensions:** Ensure proxy signals and oracle metric measure the same underlying quantity. Token-level uncertainty signals (G-NLL, entropy) don't correlate with semantic diversity measures (ensemble output variance).

2. **Validate dataset variance characteristics early:** Check oracle variance distribution (mean, CV, range) before implementing full experiment. TruthfulQA mean variance=0.024 is too low for signal-oracle correlation tasks.

3. **Sample size requirements for learned routers:** n=50 insufficient. Need n≥200 for stable learned router with 70/30 split to avoid overfitting.

4. **Modification attempts on flawed foundations fail:** Simplifying oracle metric (variance → max distance) didn't fix fundamental signal-oracle mismatch. Root cause must be addressed, not oracle metric.

## Feedback for Next Phase

### Suggested Modifications

- **Change oracle to supervised labels:** Use TruthfulQA ground-truth correctness labels as supervision signal instead of unsupervised ensemble variance
- **Change dataset to creative generation:** Use tasks with higher semantic variance (story generation, summarization, HaluEval) where ensemble outputs genuinely differ
- **Drop cascade routing approach:** Use single-pass ensemble-free UQ methods (conformal prediction on G-NLL) instead of signal-based routing
- **Scale up pilot:** Increase to n≥200 samples for learned router stability

### What NOT To Do

- Don't use variance-based oracle metrics on factual Q&A datasets (low semantic diversity)
- Don't train learned routers with n<200 samples (severe overfitting risk)
- Don't assume simplifying oracle metric fixes signal-oracle mismatch (root cause is dimensional incompatibility)

### What Showed Promise

- G-NLL, SAR, entropy extraction pipeline works correctly (no implementation bugs)
- Oracle generation pipeline stable and efficient (~30 min for n=50, 5-sample ensemble)
- Modification attempt protocol followed correctly (simplified oracle to max distance)

---
*For cross-phase reference*
*Written at: 2026-08-19T15:55:00Z*
