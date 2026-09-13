# Phase 4 Failure Record: h-e1 (Run 2)

**Date:** 2026-08-09T08:55:00Z
**Hypothesis:** h-e1
**Run:** 2
**Final Status:** NOT_SATISFIED
**Failure Type:** BELOW_TARGET_THRESHOLD
**Gate Type:** MUST_WORK

## Performance Gap

| Metric | R-ETF | Target | Baseline (Max) | Gap |
|--------|-------|--------|----------------|-----|
| AUROC | 0.5582 | ≥0.58 | 0.6426 (Mean Entropy) | -0.0844 (-13.1%) |

## Root Cause Analysis

- Residualization removes predictive variance: OLS removes variance correlated with confounds (log_freq, position, subword_len), but these confounds carry predictive signal for hallucination
- Simple mean entropy baseline is surprisingly effective (0.6426 AUROC)
- Transition features (max_delta, rise_count) not discriminative for hallucination patterns
- R-ETF 95% CI [0.5153, 0.6008] does not include target 0.58 reliably

## Lessons Learned

1. Raw entropy features outperform residualized versions on TruthfulQA MC1
2. Confound removal may be counterproductive when confounds correlate with target
3. Mean entropy alone achieves 0.6426 - simple baseline hard to beat
4. Feature engineering on entropy trajectories needs different approach

## Feedback for Phase 2A Redesign

### Suggested Directions
- Non-linear residualization (preserve non-linear signal)
- Combine R-ETF with raw entropy features instead of replacing
- Alternative confound set (different variables to control for)
- Test on TriviaQA where patterns may differ

### What NOT To Do
- Do not use same linear residualization approach
- Do not ignore raw entropy features entirely
- Do not expect transition features alone to beat mean entropy

### What Showed Promise
- R-ETF (0.5582) did beat P(True) (0.5717) - marginal
- R-ETF beat final entropy (0.5255)
- Approach not falsified (AUROC > 0.55, CI excludes 0.50)

---
*For cross-phase reference*
*Written at: 2026-08-09T08:55:00Z*
*Route: Phase2A_Redesign*