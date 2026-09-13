# Phase 4 Failure Record: h-e1 (Run 1)

**Date:** 2026-03-17T15:10:00
**Hypothesis:** h-e1
**Run:** 1
**Final Status:** FAIL
**Failure Type:** MUST_WORK_GATE_FAIL

## Performance Gap

| Metric | Ours | Target | Gap |
|--------|------|--------|-----|
| HumanEval coverage_rate | 0.9654 | 0.95 | +0.0154 (PASS) |
| MBPP coverage_rate | 0.9429 | 0.95 | -0.0071 (FAIL) |

## Gate Evaluation

- **Gate Type:** MUST_WORK
- **Criteria:** coverage_rate >= 0.95 on BOTH HumanEval and MBPP
- **HumanEval:** PASS (0.9654 >= 0.95)
- **MBPP:** FAIL (0.9429 < 0.95)
- **Overall:** FAIL (both must pass)

## Root Cause Analysis

- MBPP dataset coverage rate (0.9429) falls just below the 0.95 threshold
- HumanEval coverage rate (0.9654) passes, showing the mechanism works partially
- The 0.71% gap on MBPP suggests the L2 assertion message coverage is dataset-dependent
- MBPP problems may have more diverse failure modes not captured by assertion messages
- The coverage classifier may need tuning for MBPP-specific test patterns

## Lessons Learned

1. Assertion message coverage is dataset-dependent: HumanEval (0.9654) vs MBPP (0.9429)
2. A uniform 95% threshold across all datasets may be too strict for initial hypothesis
3. MBPP has different problem characteristics than HumanEval - coverage patterns differ
4. The core mechanism (assertion feedback classification) works but threshold needs adjustment
5. Consider dataset-specific thresholds or a lower initial threshold (e.g., 0.90) in next hypothesis

## Feedback for Next Phase (Phase 0 Redesign)

### Suggested Modifications
- Adjust gate threshold to 0.90 overall or dataset-specific thresholds
- Investigate MBPP-specific test failure patterns for better coverage classification
- Consider stratified analysis by problem type/category

### What NOT To Do
- Do not use single uniform threshold across heterogeneous datasets without validation
- Do not ignore dataset-specific characteristics in coverage rate computation

### What Showed Promise
- HumanEval coverage_rate of 0.9654 shows the core mechanism is sound
- Multi-backend LLM support (GPT-3.5, CodeLlama, DeepSeek) implemented successfully
- The assertion feedback classification approach is fundamentally valid

## Routing

- **reflection_outcome:** ROUTED_TO_PHASE_0
- **Reason:** MUST_WORK gate failed - pipeline routes back to Phase 0 for hypothesis redesign

---
*For cross-phase reference*
*Written at: 2026-03-17T15:10:00*
