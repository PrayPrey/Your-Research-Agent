# Phase 2B Context: H-E1

**Hypothesis ID:** H-E1
**Type:** EXISTENCE (MUST_WORK)
**Generated:** JIT from 02b_verification_plan.md

---

## Hypothesis Statement

The 134 h-e1 Run 2 EvalPlus failures (34 HE+ + 100 MBPP+) are recoverable as a fixed problem set with stored GPT-4o-mini incorrect outputs, enabling Conditions B and C prompt construction without new baseline API calls.

## Rationale

The entire experiment depends on existing h-e1 Run 2 outputs. If the failure set or incorrect outputs are lost or corrupted, neither Condition B nor C prompts can be constructed. This must be verified before any API calls.

## Gate Condition

**MUST_WORK** — failure blocks all downstream sub-hypotheses (H-M1, H-M2, H-C1).

## Prerequisites

None (first in chain)

## Verification Method

1. Load h-e1 Run 2 results file; confirm 134 problem IDs present (34 HE+ + 100 MBPP+)
2. Confirm stored incorrect outputs exist for all 134 problems
3. Confirm EvalPlus augmented test suite accessible via `evalplus.data.get_human_eval_plus()` / `get_mbpp_plus()`
4. Confirm first failing test case is deterministically selectable for each problem

## Success Criterion

All 134 problem IDs + incorrect outputs loadable; EvalPlus API accessible.

## Experimental Setup

**Dataset:**
- Name: EvalPlus HumanEval+ + MBPP+ (h-e1 Run 2 failure subset)
- Type: programmatic-api (real data via evalplus package)
- Source: EvalPlus benchmark suite + h-e1 Run 2 result files
- Path: h-e1 Run 2 results file (local) + evalplus.data API (package)
- Hypothesis Fit: The 134 failures ARE the dataset — the experiment verifies their recoverability and integrity

**Model:**
- Name: GPT-4o-mini (stored outputs only — no new API calls in H-E1)
- Type: Stored inference results
- Source: h-e1 Run 2 output files
- Hypothesis Fit: H-E1 only verifies that previous model outputs exist and are accessible; no new model calls needed

## Baseline & Comparison Targets

- N/A for H-E1 (existence/data-verification sub-hypothesis)
- Downstream: Conditions A/B/C defined in H-M1

## Dependencies

- None upstream
- H-M1 and H-M2 depend on H-E1 passing
