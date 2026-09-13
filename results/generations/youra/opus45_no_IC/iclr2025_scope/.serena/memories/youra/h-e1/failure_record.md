# H-E1 Failure Record

**Hypothesis ID:** h-e1
**Phase:** Phase 4
**Gate Type:** MUST_WORK
**Gate Result:** FAIL
**Date:** 2026-08-10

## Experiment Summary

- **Model:** Llama-3.1-8B
- **Analysis:** SVD effective rank on attention outputs
- **Distributions:** web, code, math, dialogue, longform (100 samples each)

## Results

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Low-rank heads | >50% | 100% | PASS |
| Mean CV | <0.3 | 0.8439 | FAIL |

## Root Causes

1. Rank values vary significantly across text distributions
2. CV threshold (0.3) may be too strict for natural variation
3. Stability criterion assumes rank consistency that doesn't exist

## Lessons Learned

1. All attention heads ARE low-rank (100% classification) - core premise validated
2. Rank VALUES are distribution-dependent - heads adapt to input content
3. Consider distribution-adaptive rank selection rather than fixed per-head rank
4. CV threshold may need relaxation (0.5-0.8) for practical use

## Recommendations

1. Revise stability criterion to percentile-based or max-min range
2. Investigate per-layer stability patterns
3. Consider dynamic rank selection based on input distribution

## Routing

**Next Action:** Phase 0 (fundamental redesign)
**Reason:** MUST_WORK gate failure requires approach reconsideration
