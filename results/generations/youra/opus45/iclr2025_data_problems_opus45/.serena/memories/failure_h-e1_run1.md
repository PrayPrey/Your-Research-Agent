# Phase 4 Failure Record: h-e1 (Run 1)

**Date:** 2026-03-23T03:25:00+00:00
**Hypothesis:** h-e1
**Run:** 1
**Final Status:** FAIL
**Failure Type:** METHODOLOGY_NOT_DEMONSTRATED

## Performance Gap

| Metric | Ours | Baseline | Gap |
|--------|------|----------|-----|
| Real-First Drift | 0.0838 | 0.0838 (Real-Last) | 0.0% |
| Cohen's d | 0.0 | - | negligible |
| Seeds Correct | 1/3 | 3/3 needed | 33% vs 70% threshold |

## Root Cause Analysis

- No true synthetic data generation (model.generate() not used)
- Both "real" and "synthetic" groups used real data samples - eliminating distributional differences
- Missing model collapse dynamics that temporal ordering hypothesis requires
- AdamW optimizer produced NaN parameters, SGD workaround may have different optimization behavior
- Simplified experiment design lost the core mechanism being tested

## Lessons Learned

1. **Synthetic data generation is essential**: The hypothesis specifically tests how temporal ordering affects model collapse, which requires actual model-generated text that degrades over generations
2. **Cannot substitute real data for synthetic data**: Even random sampling from real data doesn't exhibit collapse dynamics
3. **AdamW compatibility**: Need to investigate NaN issue or use stable optimizer alternatives from the start
4. **Effect size negligible**: Cohen's d = 0.0 indicates no effect, not just a small one

## Feedback for Next Phase

### Suggested Modifications
- Implement actual `model.generate()` for synthetic data production
- Use nucleus sampling (top_p=0.95) as specified in original design
- Verify model collapse occurs across generations before testing ordering effects
- Consider alternative optimizers or investigate AdamW NaN root cause

### What NOT To Do
- Do not use real data samples as proxy for synthetic data
- Do not skip the generation step due to complexity
- Do not assume ordering effects without verifiable collapse dynamics

### What Showed Promise
- Code infrastructure ran successfully (3 conditions x 3 seeds x 5 generations)
- Parameter drift and perplexity tracking worked correctly
- Visualization pipeline produced all 4 required figures
- The experimental framework is sound, just missing the core synthetic generation

## Gate Details

- **Gate Type:** MUST_WORK
- **Gate Result:** FAIL
- **Routing:** Phase 0 (per failure_routing policy for MUST_WORK FAIL)

## Key Insight

The hypothesis "temporal ordering affects model collapse" cannot be tested without actual model collapse occurring. The simplified experiment proved the infrastructure works but did not test the actual hypothesis mechanism.

---
*For cross-phase reference*
*Written at: 2026-03-23T03:25:00+00:00*
