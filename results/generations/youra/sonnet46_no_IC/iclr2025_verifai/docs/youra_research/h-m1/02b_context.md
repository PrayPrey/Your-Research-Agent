# Phase 2B Context: h-m1

**Generated:** 2026-08-05 (JIT from 02b_verification_plan.md)
**Hypothesis ID:** h-m1
**Source:** docs/youra_research/02b_verification_plan.md

---

## Hypothesis Information

**ID:** H-M1
**Type:** MECHANISM
**Gate:** MUST_WORK
**Prerequisites:** H-E1 (COMPLETED, gate PASS)

**Statement:**
Under HumanEval and MBPP benchmarks, if execution test feedback is applied in iterative repair mode at B=1000 output tokens per problem using Llama 3.1 8B (compared to pylint/mypy at identical budget), then execution test feedback achieves a statistically significantly larger pass@1 improvement delta over no-feedback baseline (McNemar's test, α=0.05), because execution feedback reveals the full distribution of code errors (expected vs. actual output for failing tests) while pylint/mypy reveals only a subset (syntax, type annotations, style).

**Rationale:**
This is the core mechanism hypothesis: the information-theoretic superiority of execution feedback (complete program semantics) over static analysis (subset of pre-execution errors) should translate into a larger repair success rate. The causal mechanism is operationalized as the pass@1 delta comparison at equal token budget. Step 2 of the causal chain — the informativeness of the feedback signal determines repair success — is directly tested here.

---

## Experimental Setup (from Phase 2A via Phase 2B)

**Dataset:**
- Primary: HumanEval (164 problems) + MBPP (374 problems) — full standard test sets
- Source: HumanEval: Chen et al. 2021 (openai/human-eval repo); MBPP: Austin et al. 2021 (google-research/mbpp repo)
- Loading: HuggingFace datasets / evalplus package
- Hypothesis Fit: Canonical Python code generation benchmarks with unit test oracles — required for execution feedback condition. Full test sets used (not subsets).

**Model:**
- Primary: Llama 3.1 8B Instruct (meta-llama/Llama-3.1-8B-Instruct)
- Replication: Qwen2.5-Coder-7B-Instruct (Qwen/Qwen2.5-Coder-7B-Instruct)
- Type: Open-source instruction-tuned decoder-only transformer
- Source: HuggingFace model hub
- Hypothesis Fit: 7B-scale instruction-tuned; sufficient instruction-following capability for repair tasks (validated by Arimbur 2026); feasible local inference; two different training regimes for replication diversity

---

## Variables

- **Independent:** Feedback Type = execution_test vs. pylint_mypy (both at B=1000 tokens)
- **Dependent:** pass@1 improvement delta difference (Δ_execution - Δ_pylint), statistical significance via McNemar's test
- **Controlled:** Llama 3.1 8B Instruct, HumanEval (164 problems) + MBPP (374 problems), B=1000 tokens per problem, temperature=0, same prompt template

---

## Baseline & Comparison

**H-E1 Results (prerequisite — COMPLETED):**
- Δ_pylint HumanEval: -0.0427 (finite, measurable — MUST_WORK gate PASS)
- Δ_pylint MBPP: +0.1825 (finite, measurable — MUST_WORK gate PASS)
- Pylint coverage: 100% of baseline failures flagged (unexpected — informs H-M2)
- Pylint loop runs end-to-end without systematic failure

**Infrastructure from H-E1 (reuse):**
- Same dataset loading (HumanEval 164 + MBPP 374 via evalplus)
- Same model (Llama 3.1 8B Instruct, greedy decoding)
- Same no-feedback baseline pass@1 values already computed
- Same token budget B=1000 per problem
- Add: execution repair loop (generate → execute unit tests → format test failures → repair) replacing pylint layer

---

## Verification Protocol (from Phase 2B)

1. Run execution repair condition: generate code → run unit test suite → format test failures as structured feedback → generate repair → repeat until B=1000 total output tokens consumed; record final pass/fail for all HumanEval (164) and MBPP (374) problems.
2. Compute Δ_execution = pass@1(execution_condition) - pass@1(no_feedback_baseline) for each benchmark.
3. Run McNemar's test on paired binary outcomes (each problem: pass=1/fail=0): compare (pylint_pass, baseline_fail) vs. (execution_pass, baseline_fail) counts for HumanEval and MBPP separately.
4. Report Δ_execution, Δ_pylint, their difference (Δ_execution - Δ_pylint), McNemar's test statistic and p-value, and 95% CI on the difference.
5. Replicate steps 1-4 with Qwen2.5-Coder-7B-Instruct as replication check.

---

## Success Criteria

**Primary (MUST_WORK gate):**
- Δ_execution > Δ_pylint with p<0.05 (McNemar's test) on HumanEval AND on MBPP for Llama 3.1 8B

**Secondary:**
- Qwen2.5-Coder-7B shows same directional ranking (replication consistency)

**Failure Response:**
- IF fails: EXPLORE — null result (Δ_execution ≈ Δ_pylint) is publishable as "pylint achieves parity with execution at equal token budget"; document as main finding, not failure

---

## Dependencies & Gate Logic

- **Prerequisite:** H-E1 — COMPLETED, gate PASS ✅
  - MUST_WORK gate satisfied: Δ_pylint is finite and computable on both benchmarks
  - H-E1 results provide: baseline pass@1 values, infrastructure, and pylint delta reference values
- **Gate Type:** MUST_WORK
- **Gate Condition:** Δ_execution > Δ_pylint with McNemar p<0.05 on HumanEval AND MBPP for Llama 3.1 8B

---

## Known Reference Points (from H-E1 + Literature)

- HumanEval no-feedback baseline (Llama 3.1 8B): ~67.1% pass@1 (Arimbur 2026)
- MBPP no-feedback baseline (Llama 3.1 8B): ~55.6% pass@1 (Arimbur 2026 sanitized 257; full 374 may differ)
- HumanEval execution self-repair (Llama 3.1 8B, 4 rounds): 76.8% → Δ_execution ≈ +9.8pp (Arimbur 2026)
- MBPP execution self-repair (Llama 3.1 8B, 4 rounds): 71.6% → Δ_execution ≈ +16.0pp (Arimbur 2026 sanitized)
- H-E1 Δ_pylint: HumanEval -4.27pp, MBPP +18.25pp
- **Key question:** Does execution feedback at B=1000 significantly outperform pylint at same budget? Arimbur uses 4 rounds; our budget may allow 2-3 rounds.

---

*Status: Generated JIT from 02b_verification_plan.md*
*Phase 2C: h-m1 experiment design*
