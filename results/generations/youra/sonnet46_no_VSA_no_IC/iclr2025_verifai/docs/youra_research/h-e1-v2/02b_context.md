# Per-Hypothesis Context: H-E1-v2

**Generated:** 2026-08-22 (JIT from 02b_verification_plan.md)
**Hypothesis ID:** H-E1-v2
**Version:** 2 (self-modification of H-E1)

---

## Hypothesis Information

**Statement:** The 134 h-e1 Run 2 EvalPlus failures (34 HE+ + 100 MBPP+) are recoverable as a fixed problem set with stored GPT-4o-mini incorrect outputs, enabling Conditions B and C prompt construction without new baseline API calls.

**Type:** EXISTENCE (MUST_WORK gate)

**Rationale:** The entire experiment depends on the existing h-e1 Run 2 outputs. If the failure set or incorrect outputs are lost or corrupted, neither Condition B nor C prompts can be constructed. This must be verified before any API calls.

**Success Criteria:** All 134 problem IDs + incorrect outputs loadable; EvalPlus API accessible.

**Gate:** MUST_WORK — failure blocks all downstream sub-hypotheses (H-M1, H-M2, H-C1).

**Prerequisites:** None

---

## Experimental Setup (Phase 2A Selection)

**Dataset:**
- Name: EvalPlus HumanEval+ + MBPP+ (h-e1 Run 2 failure subset)
- Type: programmatic-api (real data via EvalPlus API + cached results)
- Source: evalplus package + h-e1 archive results
- Path: `docs/youra_research/_archive/20260822T150921_routing_recovery/h-e1/results/`
- Hypothesis Fit: Failure subset is the exact target population for the repair experiment; EvalPlus provides augmented test suites for strict evaluation

**Model:**
- Name: GPT-4o-mini (stored outputs only — no new API calls for this hypothesis)
- Type: Stored solution cache
- Source: `solutions_cache.jsonl`, `humaneval_samples.jsonl`, `mbpp_completions.jsonl`
- Hypothesis Fit: The stored incorrect outputs are the data to be verified; model access is not needed for H-E1-v2

---

## Baseline & Comparison Targets

- Baseline (Condition A): 134 h-e1 Run 2 failures (all fail = pass/fail = 0 by definition)
- No model training or new generation needed for H-E1-v2

---

## Dependencies and Gate Conditions

- Gate: MUST_WORK
- Downstream blocked if failed: H-M1, H-M2, H-C1
- No prerequisites for H-E1-v2 itself

---

## Phase 2B Notes

- h-e1 (v1) failed its MUST_WORK gate due to incomplete verification
- h-e1-v2 is a self-modification: same hypothesis, focused purely on data accessibility verification
- Key verification steps: (1) load 134 task IDs, (2) confirm stored incorrect solutions, (3) confirm EvalPlus API accessible, (4) confirm first failing test deterministically selectable
