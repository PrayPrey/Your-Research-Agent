# Phase 4 Failure Record: h-m-integrated (Run 1)

**Date:** 2026-07-12T16:25:30+00:00
**Hypothesis:** h-m-integrated
**Run:** 1
**Final Status:** FAIL
**Failure Type:** MECHANISM_FAILED

## Performance Gap

| Metric | Ours | Baseline | Gap |
|--------|------|----------|-----|
| Memorization Rate | 0.0% | N/A (threshold: 30%) | -30.0 percentage points |
| Correlation (ρ) | NaN | N/A (threshold: 0.40) | undefined |

## Root Cause Analysis

- Selective memorization mechanism does NOT explain h-e1 variance signature
- Wrong prediction direction: Exposed models have HIGHER (not lower) within-category variance
- Zero categories show memorization signal (0/57 categories)
- Correlation analysis undefined due to constant memorization array (all zeros)

## Lessons Learned

1. The h-e1 variance signature (VR = 0.185 vs 0.030) is NOT caused by selective memorization creating heterogeneous variance patterns
2. Exposed models exhibit HIGHER within-category variance, contradicting the selective memorization hypothesis
3. Alternative mechanisms must be explored: uniform memorization, task difficulty interaction, or training corpus diversity
4. Statistical implementation was correct (Mann-Whitney U tests, Spearman correlation), but the underlying mechanism hypothesis was fundamentally wrong

## Feedback for Next Phase (Phase 2A)

### Suggested Modifications
- Explore uniform memorization hypothesis: all categories memorized equally → different memorization strengths inflate cross-category variance
- Investigate task difficulty interaction: exposed models excel on hard categories → variance ratio inflated by difficulty patterns
- Consider training corpus diversity mechanism: exposed models trained on more diverse data → higher category spread

### What NOT To Do
- Do not pursue selective memorization mechanisms further (empirically disproven)
- Do not assume within-category variance will be lower for exposed models

### What Showed Promise
- Variance decomposition methodology works correctly
- Data collection from h-e1 is valid and complete (30 models, 57 categories)
- Statistical testing framework (Mann-Whitney U) is appropriate

---
*For cross-phase reference*
*Written at: 2026-07-12T16:25:30+00:00*
