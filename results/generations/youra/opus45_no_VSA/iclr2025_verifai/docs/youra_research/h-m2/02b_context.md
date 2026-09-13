# Phase 2B Context: H-M2

**Generated**: 2026-08-09
**Hypothesis**: h-m2
**Type**: MECHANISM
**Prerequisites**: h-e1 (VALIDATED)

---

## Hypothesis Statement

Regression Rate₁₂(cascade) < Regression Rate₁₂(reverse) — fewer test regressions in static-first condition (p<0.05)

---

## Rationale

This is a MECHANISM hypothesis that explains WHY static-first ordering works (proven in h-e1). The hypothesis posits that static-first ordering reduces "regression churn" — cases where a fix for one test breaks another test that was previously passing.

**Mechanism**: Static analysis feedback addresses syntactic/structural issues first. These fixes are less likely to introduce semantic side-effects that break passing tests. In contrast, execution-first feedback may lead to narrow patches that fix one test but introduce regressions.

---

## Success Criteria

- Regression Rate₁₂(cascade) < Regression Rate₁₂(reverse)
- p < 0.05 (statistical significance)

**Definition**: Regression Rate₁₂ = (# tests that passed at iteration 1 but failed at iteration 2) / (# tests that passed at iteration 1)

---

## Experimental Setup

### Dataset
- Same as h-e1: HumanEval (164) + MBPP (500) = 664 problems
- Uses h-e1 iteration logs (no new API calls needed)

### Analysis Method
1. Load h-e1 iteration logs
2. For each problem, track test outcomes across iterations 1→2
3. Calculate Regression Rate₁₂ for each condition
4. Compare using appropriate statistical test (McNemar or paired proportion test)

---

## Dependency on H-E1

This hypothesis reuses h-e1 experiment logs. It does NOT require new experiments — only analysis of existing data.

**Input Files**:
- `h-e1/code/results/h-e1_iteration_logs.jsonl`

**Output Files**:
- `h-m2/regression_analysis.json`
- `h-m2/figures/regression_rate_comparison.png`

---

## Gate Condition

**Gate Type**: SHOULD_WORK
- If PASS: Supports scaffolding mechanism
- If FAIL: Effect exists but mechanism explanation needs revision

---

## Previous Hypothesis Results (h-e1)

| Metric | Result |
|--------|--------|
| Relative Improvement | 29.02% |
| 95% CI Lower Bound | 15.74% |
| McNemar p-value | 6.31e-06 |

**Verdict**: PASS (MUST_WORK satisfied)
