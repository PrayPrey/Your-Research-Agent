# Phase 4 Failure: h-m2

**Date:** 2026-07-12  
**Hypothesis:** h-m2 (MECHANISM - Binary Classification)  
**Gate:** MUST_WORK - FAILED  
**Routing:** Phase 2A (Hypothesis Redesign)

## Failure Summary

H-m2 failed MUST_WORK gate: only 1 significant feature (target: >= 3) despite perfect AUC (0.9978).

**Gate Results:**
- ✅ Test AUC > 0.65: 0.9978
- ❌ Significant features >= 3: 1 < 3 (FAILED)
- ✅ Test recall >= 0.50: 1.0000
- ✅ DeLong p-value < 0.05: 0.0000

## Root Cause: Circular Dependency

**Critical Mistake:** Synthetic labels generated FROM the same features used for prediction.

```python
# Label generation (WRONG - circular dependency)
complexity_proxy = mean(normalized[
    recursion_depth,      # Used in classifier
    loop_iterations,      # Used in classifier
    branching_frequency   # Used in classifier
])
revision_needed = complexity_proxy > percentile(60%)

# Classifier training (uses same features!)
LogisticRegression(X=execution_features, y=revision_needed)
```

**Result:** Model learns to predict labels derived from features (tautology), not real correlation.

## Lessons Learned

**Never generate synthetic labels from the feature space being predicted.**

**Overfitting Indicators:**
- AUC > 0.99 (suspiciously perfect)
- Only 1-2 significant features despite many available
- Baseline gap > 100%
- Perfect recall on real data

→ Check for data leakage or circular dependencies

## Recommendation for Redesign

**Options:**
1. Acquire real code review labels (independent ground truth)
2. Use external quality proxy (bug density, NOT derived from execution features)
3. Pivot to different correlation hypothesis

**Avoid:** ANY label generation from execution features themselves

## Files

- `docs/youra_research/h-m2/04_validation.md` - Full failure report
- `docs/youra_research/h-m2/04_checkpoint.yaml` - State with reflection_outcome
- `docs/youra_research/h-m2/code/` - Working implementation (6 modules)

## Status

**Routed to:** Phase 2A for hypothesis redesign  
**Memory created:** 2026-07-12
