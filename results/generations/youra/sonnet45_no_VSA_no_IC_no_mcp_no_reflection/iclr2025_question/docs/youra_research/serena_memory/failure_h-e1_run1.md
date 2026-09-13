# Phase 4 Failure Record: h-e1 (Run 1)

**Date:** 2026-08-28T10:05:00Z
**Hypothesis:** h-e1
**Run:** 1
**Final Status:** FAIL
**Failure Type:** MUST_WORK_FAIL

## Performance Gap

| Metric | Result | Threshold | Status |
|--------|--------|-----------|--------|
| Extraction Rate | 1.0000 | >0.95 | ✓ PASS |
| Spearman Correlation | NaN | p<0.05 | ✗ FAIL |
| Q3 Population | 0.0820 | >0.05 | ✓ PASS |

## Root Cause Analysis

- **Constant correctness array**: GPT-2 model failed all (or nearly all) TriviaQA examples, producing zero variance in correctness labels
- **Zero variance prevents correlation**: Spearman correlation requires variance in both variables; constant correctness → undefined correlation (NaN)
- **Model-dataset mismatch**: GPT-2 (1.5B params, trained 2019) insufficient for factual QA task (TriviaQA requires world knowledge)
- **Infrastructure technically works**: Entropy extraction succeeded (100% rate), but underlying assumption (model produces correct/incorrect predictions) violated

## Gate Evaluation

**Gate Type:** MUST_WORK
**Gate Result:** FAIL
**Criteria:**
1. Extraction rate >95%: ✓ PASSED (100%)
2. Significant correlation (p<0.05): ✗ FAILED (NaN - undefined)
3. Q3 population >5%: ✓ PASSED (8.20%)

**Conclusion:** ABANDON research per MUST_WORK gate policy.

## Lessons Learned

1. **Model selection critical**: Frozen LLM must have baseline capability on target task; GPT-2 too weak for TriviaQA factual QA
2. **Validation before hypothesis testing**: Should verify model produces non-trivial accuracy (>10%) before entropy analysis
3. **Zero-variance edge case**: Correlation analysis requires variance in both variables; constant labels break statistical tests
4. **Gate design assumption violation**: EXISTENCE hypothesis assumes "model makes predictions with varying correctness" — violated by complete failure

## Routing Decision

**Route to:** Phase 0 (Brainstorm)
**Reason:** Fundamental methodology flaw — base assumption (model competence) violated
**New Hypothesis Required:** Yes (requires different model, task, or approach)

---
*For cross-phase reference*
*Written at: 2026-08-28T10:05:00Z*
