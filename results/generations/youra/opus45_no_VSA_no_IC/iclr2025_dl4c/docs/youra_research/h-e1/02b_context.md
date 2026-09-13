# Phase 2B Context: H-E1

**Generated:** 2026-08-24 (JIT by Phase 2C step-01)

---

## Hypothesis Information

- **ID:** H-E1
- **Type:** EXISTENCE
- **Statement:** Different model scales (7B/70B/proprietary) exhibit statistically different FP/FN error ratios when judging code correctness
- **Rationale:** Scale may affect error pattern distribution in code correctness judgment
- **Success Criteria:** Chi-square p < 0.05 for scale × error_type independence test

---

## Experimental Setup

**Datasets:**
- **Primary:** HumanEval+ (164 problems, 80x test coverage)
- **Secondary:** MBPP+ (378 problems, augmented tests)

**Models:**
- 7B tier: DeepSeek-Coder-7B-Instruct, CodeLlama-7B-Instruct
- 70B tier: CodeLlama-70B-Instruct
- Proprietary: GPT-4

**Baselines:**
- Random (50% expected)
- CodeBERTScore (~58%)

**Controlled Variables:**
- Fixed zero-shot prompt
- Temperature = 0
- EvalPlus execution ground truth

---

## Gate Condition

**Gate Type:** MUST_WORK
**Test:** Chi-square test for independence (scale × error_type)
**Pass:** p < 0.05
**Fail:** p > 0.10; FP/FN ratios identical across scales

---

## Dependencies

**Prerequisites:** None (entry point)
**Dependents:** H-M1, H-M2 (both depend on H-E1 passing)

---

## Falsification Criteria

- p > 0.10 for chi-square test
- FP/FN ratios statistically identical across all scales
