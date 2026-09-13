# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-08-19T00:00:00Z
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Contained Tikitaka Loop
- **Gap ID**: gap1-static-vs-execution
- **Gap Title**: No Controlled Comparison of Static-Only vs Execution-Only Feedback
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 12

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 12

**Convergence Reason**: All convergence criteria met (SPECIFIC, MECHANISM, PREDICTIONS, NOVELTY, FEASIBILITY, OBJECTIONS)

### Key Insights
- Orthogonality can be tested quantitatively using additive vs max improvement model
- No new rubrics needed - existing pylint codes and test outcomes suffice
- All outcomes (orthogonal, redundant, interference) are publishable findings

### Breakthrough Moments
- Dr. Nova's framing of orthogonality as additive improvement (Δ_combined ≈ Δ_static + Δ_exec)
- Prof. Vera's 2×2 factorial experimental design
- Prof. Rex's stress-testing that sharpened the hypothesis

---

## Final Hypothesis

### Title
Orthogonality of Static Analysis and Execution Feedback in LLM Code Generation

### Core Claim
Under iterative code refinement using Self-Refine on HumanEval+/MBPP+, if we provide combined static+execution feedback versus single-source feedback, then the combined condition achieves pass@k improvement that exceeds the maximum of individual improvements (Δ_combined > max(Δ_static, Δ_exec)), because static analysis captures structural errors (pylint/mypy detectable) while execution captures behavioral errors (test failures) - orthogonal signal classes.

### Mechanism
1. LLM generates initial code with potential structural and behavioral errors
2. Static analysis (pylint/mypy) detects structural errors (type mismatches, undefined variables)
3. Execution feedback (test results) detects behavioral errors (wrong output, runtime exceptions)
4. Combined feedback provides orthogonal information, enabling LLM to fix both error classes

---

## Predictions

**P1 (Primary):** Combined feedback achieves higher pass@1 than the maximum of static-only or exec-only
- Test: 2×2 factorial experiment, one-tailed t-test
- Success: Δ_combined > max(Δ_static, Δ_exec) with p < 0.05

**P2:** Static-only feedback reduces more pylint E/W codes than exec-only
- Test: Count pylint errors before/after refinement
- Success: Static-only error reduction > Exec-only error reduction

**P3:** Exec-only feedback reduces more test failures than static-only
- Test: Count test failures before/after refinement
- Success: Exec-only test-fix rate > Static-only test-fix rate

---

## Novelty

**Key Innovation:** First systematic 2×2 factorial decomposition of feedback types with quantitative orthogonality test

**Differentiation from Prior Work:**
- vs "Static Analysis as Feedback Loop": Shows static works; we show *how* it works relative to execution
- vs "Helping LLMs Improve Code Generation": Combines feedback; we decompose contributions
- vs "Self-Refine": Single feedback source; we use 2×2 factorial design

---

## Experimental Design

**Datasets:**
- HumanEval+ (164 problems, 80x more tests than original)
- MBPP+ (399 problems, 35x more tests than original)

**Model:** GPT-4 or CodeLlama-70B (fixed across conditions)

**Conditions:**
1. Baseline (no feedback)
2. Static-only (pylint + mypy)
3. Exec-only (test results)
4. Combined (concatenated feedback)

**Controls:** Temperature 0.0, max 5 iterations, fixed prompt template

**Compute:** ~11,000 LLM calls total

---

## Limitations

- Results may not generalize beyond tested LLM
- Feedback prompt formatting may affect results
- HumanEval+ and MBPP+ patterns may differ
- Python only (cross-language is future work)

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | All criteria met in 12 exchanges |
| **Clarity Verified** | Yes |
| **Remaining Objections** | None (scope limitations acknowledged) |

---

*Phase 2A Complete | Ready for Phase 2B*
