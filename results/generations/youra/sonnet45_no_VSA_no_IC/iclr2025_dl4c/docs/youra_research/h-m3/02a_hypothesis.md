# Phase 2A Hypothesis: h-m3

**Hypothesis ID:** h-m3  
**Type:** MECHANISM  
**Gate:** SHOULD_WORK  
**Date:** 2026-08-19  
**Prerequisites:** h-e1 (VALIDATED), h-m2 (VALIDATED)

---

## Hypothesis Statement

**Full Statement:**  
Test coverage quality moderates feedback granularity requirements: comprehensive test suites enable binary sufficiency while weak coverage benefits from error-type semantic hints.

**Testable Claim:**  
Under small model capacity constraints (350M-1B parameters), if we measure test coverage quality (branch coverage %) for HumanEval and MBPP problems and correlate with per-problem feedback-type advantage, then test coverage explains ≥60% of variance (Pearson r ≥ 0.77) in feedback-type advantage (error-type gain over binary), because comprehensive test suites enable binary sufficiency while weak coverage benefits from error-type semantic hints.

---

## Variables

**Independent Variable:**  
- Test coverage quality (branch coverage %, measured via coverage.py)

**Dependent Variable:**  
- Per-problem feedback-type advantage (Δ = error-type pass@1 - binary pass@1)

**Controlled Variables:**  
- Model architecture (CodeGen-350M, StarCoder-1B, reused from h-e1)
- Training setup (binary vs error-type feedback, from h-e1)
- Benchmarks (HumanEval: 164 problems, MBPP: 974 problems)
- Evaluation protocol (20 samples/problem, pass@1 estimator)

---

## Success Criteria

1. **Coverage Correlation:** Pearson r ≥ 0.77 (R² ≥ 0.6) between branch coverage and feedback-type advantage
2. **Coverage Variance:** HumanEval and MBPP differ by ≥10 pp average coverage (sufficient variance to test hypothesis)

**Statistical Test:**  
- Two-tailed Pearson correlation test, α = 0.05
- Expected pattern: Negative correlation (higher coverage → lower feedback advantage)

---

## Expected Outcome

**Hypothesis-Confirming:**  
- Strong negative correlation (r ≤ -0.77): High coverage problems show minimal feedback advantage (binary ≈ error-type), low coverage problems show larger advantage (error-type > binary)
- Interpretation: Test suite quality IS a design factor for feedback granularity

**Hypothesis-Refuting:**  
- Null correlation (|r| < 0.5): Coverage does not explain feedback advantage
- Alternative factors dominate (problem difficulty, error types, model capacity)
- Action: Report null result (SHOULD_WORK gate allows), explore alternative moderators

---

## Relation to Research Question

This mechanism hypothesis tests **how** test coverage quality moderates feedback effectiveness, building on h-e1's finding that error-type feedback outperforms binary feedback. Understanding this moderation helps optimize feedback design per benchmark characteristics.
