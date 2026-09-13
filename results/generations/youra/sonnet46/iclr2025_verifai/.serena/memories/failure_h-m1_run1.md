# Phase 4 Failure Record: h-m1 (Run 1)

**Date:** 2026-03-17T00:00:00Z
**Hypothesis:** h-m1
**Run:** 1
**Final Status:** FAIL
**Failure Type:** MUST_WORK_FAIL

## Performance Gap

| Metric | Ours | Baseline | Gap |
|--------|------|----------|-----|
| Best ΔRepair@1 | +0.4pp (combined) | 5pp threshold | -4.6pp |
| Cross-model consistency | 1/5 models | ≥4/5 needed | -3 models |
| LLR p-value | 2.87e-29 | p < 0.05 (signal type) | N/A (model effect only) |

## Root Cause Analysis

- ~85% of FeedbackEval instances contain semantic/logical bugs that pyflakes, mypy, and pylint cannot detect (tools only catch syntax/type/style errors)
- Signal type (compiler-only, type-checker, linter) cannot be a predictor when tools fail to generate meaningful diagnostics for most instances
- LLR p=2.87e-29 is driven by model identity effects (which LLM is used), NOT signal type — signal_type coefficients all p > 0.89
- The Overlap Ratio mechanism cannot operate when static analysis produces no overlap with test execution paths for semantic errors
- This is a fundamental mismatch between the hypothesis mechanism and the nature of FeedbackEval errors (intentionally hard, semantic bugs)

## Lessons Learned

1. FeedbackEval is specifically designed to test LLM code reasoning — bugs are semantic/logical, not syntactic, making static analysis feedback largely ineffective
2. Hypothesis H-M1 (signal type as predictor of Repair@1) fails because the feedback signals contain no meaningful information for ~85% of cases
3. The h-e1 results (low pyflakes/mypy extractability ~9%) already foreshadowed this — those tools simply don't detect the error types in FeedbackEval
4. Pylint achieved 100% extractability (style issues always present) but style warnings don't help repair semantic bugs
5. A new hypothesis should focus on the LLM's own reasoning ability, not static analysis signal quality
6. Future hypotheses must verify that the proposed mechanism can actually operate on the target dataset's error distribution

## Routing Decision

**ROUTED_TO_PHASE_0** — Fundamental flaw: the hypothesis mechanism (static analysis signal type as Repair@1 predictor) cannot work for datasets dominated by semantic/logical bugs. Requires new research direction.

## Feedback for Next Phase

### Suggested Modifications
- Consider hypotheses about LLM self-feedback or chain-of-thought reasoning quality
- Consider focusing on datasets with syntactic/compilation errors where static analysis is effective
- Consider Overlap Ratio as a filter (only apply static analysis feedback when overlap > threshold)

### What NOT To Do
- Do not propose hypotheses that depend on static analysis detecting semantic/logical bugs
- Do not use FeedbackEval for hypotheses requiring high static analysis coverage
- Avoid signal-type ablation studies without first verifying extractability rates

### What Showed Promise
- Model identity (which LLM) is a very strong predictor of Repair@1 (LLR p=2.87e-29)
- Combined feedback (even if noisy) slightly outperforms no-feedback (+0.4pp) suggesting small signal
- The pipeline infrastructure (30,825 calls, 5 models, 5 conditions) worked correctly

---
*For cross-phase reference*
*Written at: 2026-03-17T00:00:00Z*
