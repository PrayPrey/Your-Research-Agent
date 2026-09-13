# H-M1: Per-Hypothesis Context (JIT Generated from Phase 2B)

**Generated:** 2026-08-03
**Source:** 02b_verification_plan.md
**Hypothesis ID:** H-M1

---

## Hypothesis Information

**ID:** H-M1
**Type:** MECHANISM
**Gate:** MUST_WORK

**Statement:**
Under ContractEval's 364 tasks, if test-passing LLM programs are evaluated on EvalPlus's published 764-test static inputs simultaneously under differential oracle and contract oracle, then the mean oracle-isolation gap (contract-failure rate minus differential-failure rate) ≥ 0.10 absolute with ≥ 0.05 contract-unique mass (output-equal-to-gt but contract-failing), because ContractEval pre/post-conditions encode relational invariants and quantified conditions that ground-truth equality cannot check.

**Rationale:**
This is Experiment A — the key oracle isolation design. Tests whether contracts are semantically richer than dense differential testing using zero new data (reuses EvalPlus's published inputs). The contract-unique failure category isolates oracle strength from input generation strategy. Primary contribution of the study.

---

## Experimental Setup (from Phase 2A via Phase 2B)

### Dataset Selection

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | ContractEval (HumanEval+/MBPP+ subset) + EvalPlus static inputs | ContractEval provides contracts; EvalPlus provides the 764-test static inputs for oracle isolation — same tasks, zero new data |

**Dataset Details:**
- **Name:** ContractEval + EvalPlus (HumanEval+Plus.jsonl.gz / MBPPPlus.jsonl.gz)
- **Type:** standard
- **Source:** github.com/suhanmen/ContractEval (5★, ACL 2026) + github.com/evalplus/evalplus (1789★, NeurIPS 2023)
- **Path:** 364 ContractEval tasks (strict subset of HumanEval+/MBPP+); EvalPlus publishes all 764 static inputs per task as JSON
- **Hypothesis Fit:** Oracle isolation requires identical inputs evaluated under two oracles; EvalPlus's published static inputs (base_input + plus_input fields) provide the fixed input set without adaptive search — cleanly separates oracle semantics from search strategy

### Model Selection

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Model** | LLM-generated code samples from H-E1 (5 model families, n=10 samples/task) | Reuse code already generated in H-E1; no new generation needed — controlled experiment where only oracle changes |

**Model Details:**
- **Type:** Reused from H-E1 (API + open-source LLM code samples)
- **Source:** H-E1 Phase 4 output (test-passing programs per model per task)
- **Models:** GPT-4o-mini, Claude-3-haiku, DeepSeek-Coder-V2-Lite, CodeLlama-13B, CodeLlama-34B (same 5 families)
- **Hypothesis Fit:** Controlled comparison requires same programs evaluated under both oracles; reusing H-E1's test-passing programs ensures oracle is the only variable

---

## Variables

- **IV:** Oracle type (differential equality oracle `f(x)==gt(x)` vs. contract oracle `assert pre(x); post(f(x))`) applied to identical EvalPlus static inputs
- **DV:** Oracle-isolation gap = mean(contract-failure rate) − mean(differential-failure rate) on same 764 EvalPlus static inputs per task; contract-unique failure mass = fraction where `f(x)==gt(x)` AND `post(f(x))` fails
- **CV:** EvalPlus 764 static inputs per task (fixed, published), same LLM programs evaluated under both oracles

---

## Verification Protocol (from Phase 2B)

1. Load EvalPlus published JSON inputs (764 tests/task for all ContractEval tasks — HumanEvalPlus.jsonl.gz + MBPPPlus.jsonl.gz; fields: `base_input`, `plus_input`).
2. Verify task ID overlap between ContractEval and EvalPlus (expect ≥90% match); generate fresh matched inputs for unmatched tasks as fallback.
3. For each test-passing LLM program (from H-E1), evaluate all 764 inputs under:
   - (a) Differential oracle: `f(x) == gt(x)` (ground-truth equality check)
   - (b) Contract oracle: `assert pre(x)` satisfied AND `post(f(x))` holds (icontract decorators)
4. Classify each failure:
   - Contract-unique: `f(x)==gt(x)` AND `post(f(x))` fails
   - Redundant: both oracles detect failure
   - Differential-only: `f(x)!=gt(x)` AND `post(f(x))` holds (rare edge case)
5. Compute oracle-isolation gap per task = contract_failure_rate − differential_failure_rate.
6. Wilcoxon signed-rank test across tasks with Holm correction; bootstrap 95% CI on oracle-isolation gap and contract-unique mass.

---

## Success Criteria

- **Primary:** mean oracle-isolation gap ≥ 0.10, Wilcoxon p < 0.01 after Holm correction
- **Secondary:** contract-unique failure mass ≥ 0.05 with bootstrap 95% CI lower bound > 0.03

---

## Failure Response

IF fails (gap ≤ 0.02 or p > 0.05) → PIVOT: investigate contract richness stratification (AST analysis); consider whether EvalPlus inputs systematically under-sample contract-failure-inducing states.

---

## Dependencies

- **H-E1** (VALIDATED): Existence of contract-strength gap confirmed (97/155 tasks, 62.6% show ≥1 violation; mean gap 0.471). H-E1's test-passing code samples reused as the program corpus for Experiment A.

---

## Key Assumptions Relevant to H-M1

| ID | Assumption | Mitigation |
|----|------------|------------|
| A3 | EvalPlus static inputs (764 tests/task) map to ContractEval tasks (strict subset) | Verify task ID overlap before starting; fallback to fresh generated inputs |
| A5 | Contract-unique failure category (output-equal-to-gt but contract-failing) is non-empty (≥5%) | h-e1 confirmed 27 such violations in tractable subset; pre-check on first 50 tasks |

---

## Baseline & Comparison Targets

- **Oracle A (Differential):** EvalPlus dense differential testing — `f(x)==gt(x)` on 764 static inputs per task
- **Oracle B (Contract):** ContractEval icontract decorators — `post(f(x))` on same 764 inputs
- **Key Comparison:** ContractEval SMT-based (Lim et al. 2025) — 0% CSR for 5 open LLMs; our execution-based approach is 100% tractable
- **EvalPlus Baseline:** Up to 23.1% additional pass@1 reduction from dense testing vs. original HumanEval
