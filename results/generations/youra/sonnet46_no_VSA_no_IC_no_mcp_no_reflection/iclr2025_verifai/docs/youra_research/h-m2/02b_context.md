# Hypothesis Context: H-M2

**Generated from:** Phase 2B Verification Plan
**Date:** 2026-08-31
**Main Hypothesis:** Verifier Feedback Specificity Gradient
**Phase 2B Source:** 02b_verification_plan.md

---

## Hypothesis Information

### Statement

Under the same set of failing LLM-generated solutions, if four feedback categories (execution monitoring, static analysis, type checking, SMT solving) are applied independently, then the feedback signals will exhibit a measurable specificity gradient (SMT > static analysis/type checking > execution monitoring) as operationalized by the information content of the feedback string (character count and error-field count of structured output) because higher formalism levels produce more detailed diagnostic information.

### Type

MECHANISM

### Rationale

Causal chain step 2 — the efficiency mechanism requires that feedback specificity actually varies across categories in a measurable way. If all signals are equally informative (or equally uninformative) to the LLM, the proposed efficiency trade-off mechanism is broken.

---

## Verification Protocol

### Conceptual Test

1. Apply all 4 verifiers to the same set of failing solutions from H-M1.
2. Measure feedback specificity: character count of feedback string; number of distinct error fields in structured output (e.g., JSON keys for Pyright; counterexample variable bindings for Z3).
3. Rank categories by mean specificity; verify ordering matches prediction (SMT ≥ static/type > execution).

### Success Criteria

- Primary: Specificity ordering SMT ≥ {static analysis, type checking} > execution monitoring confirmed (Kruskal-Wallis p<0.05)
- Secondary: Pairwise differences between adjacent categories are non-trivial (>20% difference in mean character count)

### Variables (if applicable)
- **Independent Variable:** Formal Feedback Category (4 levels: execution monitoring, static analysis, type checking, SMT solving)
- **Dependent Variable:** Feedback specificity proxy (mean character count of feedback string, mean number of structured error fields per problem)
- **Controlled Variables:** Same failing solutions from H-M1, standardized output format

---

## Experimental Setup (from Phase 2A via Phase 2B)

> **Note:** Dataset and model were selected in Phase 2A Dialogue based on hypothesis Variables.
> Phase 2C experiment design MUST use this selection.

### Selected Dataset
- **Name:** HumanEval + MBPP (538 problems combined)
- **Type:** standard
- **Source:** openai/human-eval (GitHub); google-research/mbpp (GitHub)
- **Path:** auto (download from public GitHub repos via datasets library)
- **Hypothesis Fit:** Standard LLM code generation benchmarks with ground-truth test suites; used by all prior formal feedback papers enabling comparison; failing solutions from H-M1 already generated on these problems

### Selected Model
- **Name:** GPT-4o-mini (OpenAI API)
- **Type:** API-based LLM
- **Source:** OpenAI API
- **Hypothesis Fit:** Same backbone used in H-M1 and H-E1 for controlled comparison; failing solutions are already available from H-M1 run; no additional generation needed

---

## Baseline & Comparison Targets

### Baseline Methods

| Method | Performance | Dataset |
|--------|-------------|---------|
| No feedback (vanilla generation) | GPT-4o-mini baseline ~75-80% pass@1 | HumanEval + MBPP |
| Self-Repair / Execution monitoring (Olausson et al., 2023) | ~5-10% pass@1 improvement (GPT-4) | HumanEval, MBPP |
| Reflexion (Shinn et al., 2023) | HumanEval ~80% → ~91% with GPT-4 | HumanEval |

### Baseline Performance

Expected feedback string lengths (from literature and tool characteristics):
- Execution monitoring: short traceback strings (~100-500 chars)
- Static analysis (Pyright): structured JSON output with error codes (~200-800 chars)
- Type checking: similar to static analysis (~150-600 chars)
- SMT (Z3): counterexample bindings with variable names and values (~300-1500 chars, when triggered)

### Gap Analysis

No prior work measures feedback information content systematically across these four categories on the same problem set. This is novel measurement work validating a core causal mechanism.

---

## Dependencies and Gate Conditions

### Prerequisites

- H-E1 (VALIDATED) — Existence of distinct feedback signals confirmed
- H-M1 (VALIDATED) — Bug-type distribution confirmed; failing solutions available

### Gate Information

**Gate Type:** SHOULD_WORK
- MUST_WORK: Failure stops entire workflow
- SHOULD_WORK: Failure documented as limitation, workflow continues
- DETERMINES_SUCCESS: Final validation gate

**Consequence if Fails:** If specificity ordering does not hold, H-M3 (repair quality correlation) is compromised. Document as limitation; explore whether LLM parsing of structured vs. natural language feedback explains anomaly.

**Phase Assignment:** Phase 2C → 3 → 4

**Estimated Duration:** 2-4 hours compute (re-running 4 verifiers on ~100-200 failing solutions from H-M1)

---

## Dependency Context

### Relationship to Other Hypotheses

- **Depends on:** H-M1 (failing solutions already generated, bug-type distribution known)
- **Enables:** H-M3 (repair quality correlation requires specificity gradient established here)
- H-M2 is the measurement validation step — it confirms that the IV (formal feedback category) actually produces measurably different feedback signals before testing downstream effects on repair quality

---

## Verification State Reference

**State File:** verification_state.yaml
**Current Status:** IN_PROGRESS
**Workflow Status:** ACTIVE

---

## Phase 2C Usage Notes

**This context file provides:**
1. Complete hypothesis specification for experiment design
2. Gate conditions for prerequisite validation
3. Dependency information for controlled experiments
4. Success criteria for evaluation design

**Phase 2C will:**
1. Load this file instead of full Phase 2B roadmap (91% smaller)
2. Search for implementation patterns (Archon, Exa MCP)
3. Design concrete experiment specification for specificity measurement
4. Output: docs/youra_research/h-m2/02c_experiment_brief.md

---

*Optimized for single-hypothesis experiment design*
