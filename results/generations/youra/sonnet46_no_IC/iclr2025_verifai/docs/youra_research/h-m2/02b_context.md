# Phase 2B Context: H-M2

**Generated:** 2026-08-05 (JIT generation from 02b_verification_plan.md by Phase 2C step-01)
**Hypothesis ID:** h-m2
**Type:** MECHANISM
**Gate:** SHOULD_WORK

---

## Hypothesis Information

**Statement:**
Under the HumanEval baseline failure cases (problems that fail in no-feedback single-pass generation with Llama 3.1 8B), if pylint+mypy is run on the failing code without execution, then fewer than 50% of failure cases receive at least one pylint/mypy warning or error, because HumanEval failures are predominantly logic/runtime errors (wrong algorithm, off-by-one, incorrect data structure usage) that pylint cannot detect without executing the code.

**Type:** MECHANISM
**Rationale:**
This mechanism hypothesis operationalizes the causal explanation for H-M1: if pylint's lower pass@1 delta is caused by lower error coverage, the coverage analysis should show pylint misses >50% of baseline failures pre-execution. This automated measurement converts the mechanism claim from a post-hoc narrative into a testable prediction. The result directly explains WHY execution feedback outperforms pylint (if H-M1 is supported) or challenges the explanation (if pylint coverage is actually high).

**Success Criteria (PoC: Direction-based):**
- Primary: coverage < 0.50 (pylint flags <50% of HumanEval baseline failures pre-execution)
- Secondary: Dominant pylint categories are style/convention (not error), supporting the informativeness gap claim

---

## Experimental Setup

**Dataset:**
- Name: HumanEval baseline failures (subset of HumanEval)
- Type: standard (derived from HumanEval — openai/human-eval)
- Source: HumanEval failing solutions from no-feedback baseline (Llama 3.1 8B)
- Path: Reuse h-e1/results/baseline_results.json or h-m1/results/baseline_results.json (already collected)
- Hypothesis Fit: HumanEval failures are the target population; this dataset tests the coverage fraction directly

**Model:**
- Name: N/A (no LLM inference required — static analysis only)
- Pretrained: N/A
- Source: pylint + mypy tools only
- Hypothesis Fit: Hypothesis is about static analysis tool coverage, not model output quality

---

## Variables

- **Independent Variable:** Feedback signal type (pylint+mypy applied without execution)
- **Dependent Variable:** Fraction of HumanEval baseline failures that pylint/mypy flags with ≥1 warning/error
- **Controlled:** HumanEval failing solutions from no-feedback baseline, default pylint checkers, Llama 3.1 8B generated code

---

## Verification Protocol

1. Collect all HumanEval problems where no-feedback baseline fails (code generates incorrect output for ≥1 test case) — these are already available from H-E1/H-M1 baseline runs.
2. For each failing solution, run pylint+mypy on the code file without executing against test cases; record whether ≥1 warning or error is flagged.
3. Compute coverage = (number of failing solutions with ≥1 pylint/mypy flag) / (total failing solutions).
4. Report coverage fraction with 95% CI (bootstrap), distribution of pylint rule categories triggered (error vs. warning vs. convention), and comparison to 100% (execution catches all test failures by definition).
5. Perform sub-analysis: identify which pylint rule categories correlate most with functional failures.

---

## Gate Condition

**Gate Type:** SHOULD_WORK
**Satisfaction:** null (not yet evaluated)
**Result:** null

Gate logic: Coverage <50% supports main hypothesis mechanism. Coverage >80% challenges the causal explanation. Neither outcome stops pipeline — SHOULD_WORK gates allow continuation.

---

## Prerequisites

- H-M1: COMPLETED (PASS) — execution condition run, baseline failures already collected
- Baseline failure list available from h-e1/results/ or h-m1/results/

---

## Continuation Context

H-M2 is a continuation experiment that:
1. **Reuses the baseline failure dataset** from H-E1/H-M1 runs (no new LLM inference needed)
2. **Adds static analysis measurement** on already-collected code artifacts
3. **Provides mechanistic explanation** for why execution feedback (H-M1) outperformed pylint

**Key insight from H-M1 (prerequisite results):**
- HumanEval: Δ_execution=+0.0488 vs Δ_pylint=−0.0427 → execution passes 15 problems pylint misses
- MBPP: Δ_execution=+0.4021 vs Δ_pylint=+0.1825 → execution passes 85 problems pylint misses
- H-M2 explains WHY: pylint likely misses >50% of HumanEval failures because they are logic/runtime errors
