# Phase 4 Failure Record: h-e2 (Run 2)

**Date:** 2026-03-20T12:30:00
**Hypothesis:** h-e2
**Run:** 2
**Final Status:** FAIL
**Failure Type:** MUST_WORK_FAIL

## Performance Gap

| Metric | Ours | Baseline | Gap |
|--------|------|----------|-----|
| partial_rho (max) | 0.0507 | 0.10 (threshold) | -0.0493 |

## Experiment Results (5 model-benchmark pairs)

| Pair | partial_rho | p_perm | Status |
|------|------------|--------|--------|
| llama3_humaneval | -0.0186 | 0.5915 | FAIL |
| llama3_mbpp | -0.0231 | 0.6782 | FAIL |
| deepseek_humaneval | -0.1050 | 0.9106 | FAIL |
| deepseek_mbpp | +0.0507 | 0.1592 | FAIL |
| codellama_mbpp | -0.0041 | 0.5321 | FAIL |

**Gate:** MUST_WORK — 0/5 pairs pass (rho>=0.10 AND p_perm<0.05), 0/3 architectures pass (rho>=0.15)

## Root Cause Analysis

- A_p (mean pairwise n-gram Jaccard) does NOT positively predict pass@1 after controlling for LOOM difficulty
- Partial rhos near-zero or negative across ALL 5 model-benchmark pairs
- Core mechanism is invalid: high structural agreement among k=5 solutions does NOT reflect a concentrated probability mass on correct solutions
- A_p conflates surface-level syntactic similarity with semantic correctness — models can repeatedly generate syntactically similar but functionally incorrect solutions
- LOOM difficulty adjustment does not reveal hidden signal; the signal was absent, not confounded

## Lessons Learned

1. N-gram Jaccard similarity between code solutions (A_p) is NOT a reliable predictor of pass@1 correctness
2. High agreement among LLM solutions for a problem means the model is "confident" but not necessarily "correct"
3. Controlling for difficulty (LOOM) did not rescue the signal — the mechanism is fundamentally wrong
4. The H-AgreePredict-v11 research direction (n-gram agreement → pass@1) should be abandoned
5. Future hypotheses should avoid surface-level string similarity metrics as predictors of code correctness
6. The h-e1 PASS (A_p is non-degenerate) was necessary but not sufficient — A_p varies but doesn't predict correctness

## Feedback for Next Phase

### What NOT To Do
- Do NOT use n-gram Jaccard or similar surface-level string similarity as a pass@1 predictor
- Do NOT assume that agreement/consensus among LLM solutions implies correctness
- Do NOT try partial Spearman approaches with A_p — the signal is genuinely absent

### What Showed Promise
- h-e1 PASS confirmed A_p is non-degenerate (IQR>0.05 in 4/5 pairs) — the metric can be computed but does not predict
- LOOM difficulty is a useful covariate for future difficulty-adjusted analyses
- EvalPlus 5-pair setup (llama3, deepseek, codellama × HumanEval+/MBPP+) is a valid experimental setup

### Route
- ROUTED_TO_PHASE_0: Fundamental mechanism failure. A new research direction needed.
- h-m1, h-m2, h-m3 CASCADE_FAILED as prerequisites broken.

---
*For cross-phase reference*
*Written at: 2026-03-20T12:30:00*
