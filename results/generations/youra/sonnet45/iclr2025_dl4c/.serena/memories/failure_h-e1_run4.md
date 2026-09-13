# Phase 4 Failure Record: h-e1 (Run 4)

**Date:** 2026-03-18T16:28:49Z
**Hypothesis:** h-e1
**Run:** 4
**Final Status:** FAIL
**Failure Type:** MUST_WORK_FAIL

## Performance Gap

| Metric | Ours | Baseline | Gap |
|--------|------|----------|-----|
| Best Metric (R²) | 0.2938 | 0.5582 | -0.2644 (-47.4%) |
| Median Ratio | NaN | N/A | N/A |
| Task Coverage >0.4 | 0.0% | N/A | N/A |
| Delta R² | 0.0000 | N/A | N/A |
| Max VIF | 29.20 | N/A | N/A |

## Root Cause Analysis

- **Dataset mismatch:** CoverageEval provides one canonical solution per task, hypothesis requires diverse code solutions
- Structural features are constant for all tests of same task (no variation to explain)
- Proposed model underperformed baseline significantly (R²=0.29 vs 0.56)
- High multicollinearity (VIF=29.20) indicates feature redundancy
- Coverage variation comes from different TESTS on same code, not different CODE
- Hypothesis requires diverse CODE solutions to test structural complexity effects

## Lessons Learned

1. CoverageEval has only ONE canonical solution per task - not suitable for hypothesis testing code diversity
2. Coverage variation comes from different TESTS on same code, not different CODE
3. Hypothesis requires diverse CODE solutions to test structural complexity effects
4. Real data experiment confirms hypothesis mismatch with dataset structure
5. Need to generate diverse LLM solutions using CodeLlama/StarCoder/DeepSeek (as specified in experiment brief) OR reformulate hypothesis to focus on test-level variation

## Alternative Approaches

- Generate diverse LLM solutions using CodeLlama/StarCoder/DeepSeek (as specified in experiment brief)
- Use different dataset that provides multiple solutions per task
- Reformulate hypothesis to focus on test-level variation (not code-level variation)

## Recommended Action

Route to Phase 0 for fundamental rethinking - hypothesis design incompatible with dataset structure

---
*For cross-phase reference*
*Written at: 2026-03-18T16:28:49Z*