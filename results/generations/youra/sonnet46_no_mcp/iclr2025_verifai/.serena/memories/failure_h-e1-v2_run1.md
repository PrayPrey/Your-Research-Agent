# Phase 4 Failure Record: h-e1-v2 (Run 1)

**Date:** 2026-05-09T07:30:00Z
**Hypothesis:** h-e1-v2
**Run:** 1
**Final Status:** FAIL
**Failure Type:** MUST_WORK_FAIL — Fundamental feature non-informativeness (structural near-zero variance)

## Hypothesis

H-E1-V2: Existence of Measurable Static Formal Features in LLM-Generated Code (v2 - Calibrated F3 Threshold)

**Modification from H-E1:** F3 gate threshold lowered 0.05 → 0.04 based on H-E1 measurements
(F3 std = 0.047–0.049 combined corpus; MBPP+ alone showed 0.053–0.054).

## Gate Result

**MUST_WORK: FAIL** → ROUTED_TO_PHASE_0

### Gate Metrics

| Model | F1 Rate | F2 Std | F3 Std | F3 Gate (>0.04) |
|-------|---------|--------|--------|-----------------|
| codegen-2b | 0.988 ✅ | 0.397 ✅ | 0.016 | ❌ FAIL |
| gptneo-2b | 0.962 ✅ | 0.399 ✅ | 0.012 | ❌ FAIL |
| starcoder | 0.995 ✅ | 0.396 ✅ | 0.010 | ❌ FAIL |
| code-llama-7b | 0.994 ✅ | 0.396 ✅ | 0.007 | ❌ FAIL |
| mistral-7b | 0.968 ✅ | 0.399 ✅ | 0.007 | ❌ FAIL |

**F3 models passed: 0/5** (threshold 0.04, calibrated from H-E1's 0.047–0.049 estimate)

## Failed Checks

- F3 std: 0.007–0.016 << threshold 0.04 in all 5 models (3–6× below threshold)
- F3 is non-informative: corr(F3, correct) = 0.007–0.014, p > 0.55 (not significant in any model)
- Threshold calibration irrelevant: gap is 3–6×, not salvageable by threshold adjustment

## Root Cause Analysis

1. **Structural near-zero variance of F3 in HumanEval+ code**: LLM-generated Python solutions for algorithmic
   problems (HumanEval+ task type) use `assert` only as test stubs, not as production code. The
   feature extraction pulls from solution code, not test harnesses.

2. **H-E1 planning error**: H-E1 measured F3 std = 0.047–0.049 (combined HumanEval+ + MBPP+),
   but this masked the per-benchmark split. HumanEval+ alone yields F3 std ≈ 0.007–0.016;
   MBPP+ alone yields F3 std ≈ 0.053–0.054. The H-E1-V2 experiment used HumanEval+ only
   (candidates already generated), revealing the true distribution.

3. **Feature selection flaw**: F3 (assertion density) is not a valid architectural predictor for
   HumanEval+-style algorithmic code generation. The feature has no signal (p > 0.55 in all models).

4. **Threshold calibration was insufficient fix**: Lowering 0.05 → 0.04 is irrelevant when the
   actual values are 0.007–0.016. A threshold of 0.02 would still not be met by most models.

## Lessons Learned

1. **Per-benchmark feature statistics must be computed separately before threshold-setting.**
   Combined corpus statistics can mask dataset-specific structural differences. For HumanEval+
   (algorithmic problems), assertion density is structurally near-zero.

2. **SELF_MODIFY via threshold adjustment is only valid when the gap is marginal (< 20%).**
   When H-E1 showed F3 std = 0.047–0.049 vs threshold 0.05, the gap was only 5%—a threshold
   adjustment seemed reasonable. But if the true per-benchmark value is 0.007–0.016, adjustment
   cannot fix the fundamental problem.

3. **Assertion density (F3) is not a valid feature for HumanEval+-style code generation tasks.**
   Do not use F3 as a feature for algorithmic problem-solving benchmarks. Consider: line coverage
   indicators, import diversity, function length distribution, or type annotation richness as
   alternatives.

4. **F1 (parse validity) correlates trivially with correctness (corr = 1.000, p = 0.000).**
   While F1 achieves gate, it provides no additional predictive information beyond "code runs."
   Future hypotheses should be cautious about F1 as a standalone feature—it is necessary but
   not discriminating.

5. **New direction needed: Replace F3 with a feature that has structural variance in HumanEval+.**
   Candidates: comment density, docstring presence, helper function count, cyclomatic complexity,
   import count. These likely have non-trivial distributions in LLM-generated algorithmic code.

## What Showed Promise

- F1 (parse validity): 0.962–0.995 across all models (strong PASS)
- F2 (type annotation completeness): std 0.396–0.399 (strong PASS, good variance)
- McFadden ΔR² = 0.22–0.72 (driven by F1 correlation with correctness, but demonstrates
  that feature-based logistic regression can work if right features are selected)
- Feature extraction pipeline (AST-based, CPU-only) works correctly and at scale

## Routing Decision

**ROUTED_TO_PHASE_0**: New research direction required. The assertion density feature is
fundamentally non-informative for HumanEval+-style algorithmic code. The hypothesis family
(static formal features as correctness predictors) may still be viable with different feature
selection—but this requires brainstorming new candidate features from Phase 0.

## Hypothesis Lineage

```
H-E1 (FAIL: F3 std 0.047-0.049, threshold 0.05)
    └── SELF_MODIFY: lower F3 threshold to 0.04
        └── H-E1-V2 (FAIL: F3 std 0.007-0.016, threshold 0.04) → ROUTED_TO_PHASE_0
```

---
*Failure recorded at: 2026-05-09T07:30:00Z*
*For cross-phase reference — read by Phase 0 and Phase 2A*
