# Introduction

The most difficult errors to repair are precisely the ones that provide the least actionable feedback. Assertion errors constitute 53% of failures on standard code generation benchmarks and exhibit the lowest repair success rates (~45%), yet their error messages contain near-zero extractable state information. This paradox—that the errors most in need of rich diagnostic feedback are those that provide the least—reveals a fundamental tension in LLM-based code repair.

Recent advances in self-repair demonstrate that iterative refinement with verification feedback can improve pass rates by 4.9–17.1 percentage points on HumanEval \citep{howmanytries2026}. Runtime traces outperform simple error messages \citep{debugrepair2026}, and type constraints improve functional correctness \citep{tyflow2025}. However, these findings describe *which* feedback works better without explaining *why*. What properties of a verification signal enable an LLM to localize bugs and infer correct fixes?

We hypothesize that **Actionable Specificity (AS)** mediates feedback effectiveness. We decompose AS into three measurable components: localization (AS_loc)—whether file:line information is present; state exposure (AS_state)—how many variable values are visible; and causal context (AS_causal)—execution trace depth between assignment and failure. Under this framework, a full runtime trace (high AS) should outperform a bare assertion error (low AS) because it provides the LLM with localization, state, and causal information necessary for targeted repair.

To test whether AS is even measurable from standard verification signals—a necessary precondition for testing its predictive power—we designed an existence test on HumanEval and MBPP (664 problems). We generated 600 signals across 6 conditions (C1–C6) varying in expected AS level, then extracted AS components using regex patterns designed for Python tracebacks.

**Our key finding is negative but informative:** regex-based extraction achieves only 49.5% coverage, with AS_state at 2.7%. The root cause is that assertion errors, which dominate these benchmarks (53.4%), produce minimal output without traceback frames. Standard `AssertionError` messages lack the file:line and variable context that our extraction patterns require.

This negative result constitutes a **boundary condition discovery** rather than a framework failure. We demonstrate that:

1. **The AS framework reveals a hidden barrier**: feedback informativeness research must stratify by error type before operationalizing extraction.
2. **AS ordering is preserved** (C1≥C2≥C3≥C4) even at low absolute values, suggesting the conceptual framework remains valid.
3. **Assertion errors create a mismatch**: the error types that most need actionable feedback are those that structurally cannot provide it in standard output format.

The contribution is methodological: we document what researchers should verify—extraction feasibility by error type—before designing feedback mechanisms for LLM code repair.
