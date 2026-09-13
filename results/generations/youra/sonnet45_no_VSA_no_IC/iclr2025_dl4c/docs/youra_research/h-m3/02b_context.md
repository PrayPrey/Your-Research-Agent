# Phase 2B Context: h-m3

**Hypothesis ID:** h-m3  
**Type:** MECHANISM  
**Gate:** SHOULD_WORK  
**Date:** 2026-08-19

---

## Hypothesis Statement

Test coverage quality moderates feedback granularity requirements: comprehensive test suites enable binary sufficiency while weak coverage benefits from error-type semantic hints.

**Testable Claim:**  
Under small model capacity constraints (350M-1B parameters), if we measure test coverage quality (branch coverage %) for HumanEval and MBPP problems and correlate with per-problem feedback-type advantage, then test coverage explains ≥60% of variance (Pearson r ≥ 0.77) in feedback-type advantage (error-type gain over binary).

---

## Prerequisites

**h-e1 (VALIDATED):**  
- Status: VALIDATED
- Result: Error-type feedback outperforms binary feedback on HumanEval
- Key findings:
  - Error-type feedback provides +8.5% pass@1 advantage over binary
  - Small models (350M-1B) benefit from semantic error hints
  - Models trained with binary and error-type feedback available for reuse

**h-m2 (VALIDATED):**  
- Status: VALIDATED
- Result: Feedback granularity requirements validated
- Relevance: Establishes baseline feedback effectiveness, h-m3 tests moderation by coverage quality

---

## Research Context

**Source:** Verification Plan 02b_verification_plan.md (Section 2.2, H-M3)

**Rationale:**  
Test suite quality varies widely across benchmarks. HumanEval provides comprehensive test suites (avg 7.5 tests/problem), while MBPP provides minimal coverage (3 tests/problem). If coverage moderates feedback requirements, this explains when binary feedback suffices vs when error-type semantic hints are needed.

**Key Insight:**  
- **High coverage:** Test suites exercise most branches → binary pass/fail signal is sufficient → error-type feedback adds minimal value
- **Low coverage:** Weak test suites miss edge cases → binary signal is noisy → error-type hints guide model toward correct error reasoning

---

## Experimental Approach

**Three-Stage Design:**

1. **Coverage Measurement (Offline):**  
   - Instrument reference solutions with coverage.py (branch mode)
   - Execute against test suites, extract branch coverage %
   - Compute coverage statistics per benchmark

2. **Per-Problem Evaluation (Reuse h-e1 models):**  
   - Load binary and error-type trained models from h-e1
   - Evaluate per-problem pass@1 (20 samples/problem)
   - Generate pass@1 results for HumanEval (164) and MBPP (974)

3. **Correlation Analysis:**  
   - Compute per-problem feedback advantage: Δ = error-type pass@1 - binary pass@1
   - Test Pearson correlation: coverage vs advantage
   - Robustness checks: control for difficulty, stratify by benchmark

---

## Success Criteria

**Primary:**  
- Pearson r ≥ 0.77 (R² ≥ 0.6) between branch coverage and feedback advantage
- p < 0.05 (statistically significant)

**Secondary:**  
- HumanEval vs MBPP coverage difference ≥10 pp (sufficient variance)
- Negative correlation pattern (high coverage → low advantage)

**Gate Evaluation (SHOULD_WORK):**  
- PASS: Coverage explains ≥60% variance → moderation hypothesis validated
- FAIL: Null result (r < 0.5) → alternative moderators needed (not blocking)

---

## Limitations & Risks

**Coverage Proxy Validity:**  
- Branch coverage is a proxy for test quality, not complete measure
- High coverage with weak assertions still provides false confidence
- Mitigation: Test multiple coverage types (branch, statement, path)

**Problem Difficulty Confound:**  
- Harder problems may have lower coverage AND lower baseline pass@1
- Mitigation: Partial correlation controlling for SFT baseline performance

**Sample Size (HumanEval):**  
- Only 164 problems (vs MBPP's 974)
- Mitigation: Pooled analysis (n=1138), stratified as robustness check

---

## Expected Outcomes

**Hypothesis-Confirming (r ≥ 0.77):**  
- Coverage explains majority of feedback advantage variance
- HumanEval (high coverage) shows minimal advantage
- MBPP (low coverage) shows larger advantage
- Implication: Test quality IS a design factor for feedback granularity

**Hypothesis-Refuting (r < 0.5):**  
- Coverage does not explain advantage
- Other factors dominate (difficulty, error types)
- Action: Report null result, explore alternative moderators
