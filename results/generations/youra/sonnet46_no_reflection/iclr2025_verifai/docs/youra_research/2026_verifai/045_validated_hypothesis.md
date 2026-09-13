# 045_validated_hypothesis.md — Phase 4.5 Synthesis
# Formal Feedback as Local Logical Oracle — H-E1 Synthesis

**Version:** 2.0
**Generated:** 2026-05-20
**Phase:** 4.5 (Hypothesis Synthesis)
**Hypothesis Loop:** H-E1 (EXISTENCE / MUST_WORK)
**Pipeline Project:** 9919f77e-9c2f-4516-8106-6ad2c64aac73

---

## Executive Summary

Phase 4 execution of H-E1 (Formal Feedback as Local Logical Oracle) produced a MUST_WORK gate FAIL. The oracle mechanism — whereby semantically grounded Lean4 compiler feedback used as DPO negatives concentrates probability mass on premise-consistent tactics (locality score LS_A > LS_P, p < 0.05) — was **not empirically tested**. All locality score measurements returned 0.0 because LeanDojo was not installed on the H100 cluster, causing `leandojo_tracing.py` to silently fall back to synthetic (hardcoded) proof state triples. The DPO training infrastructure (β=10, lr 5e-6→5e-7, 1-epoch, state alignment at 100%) was implemented correctly. The hypothesis is **not falsified** — it is blocked by an infrastructure failure. Routing recommendation: fix the LeanDojo installation, remove the synthetic fallback, and retry Phase 4 for H-E1 (counts as modification_attempt = 1).

---

## Prediction-Result Matrix

| Prediction | Scope | Tested? | Result | Evidence |
|---|---|---|---|---|
| **P1:** ≥10pp hard-stratum pass@1 advantage (A over D) | H-M3 | No | NOT_TESTED | H-E1 tests only locality (P3); P1 deferred to H-M3 |
| **P2:** α-interaction monotonically decreasing Δ(A-D), Cohen's d ≥ 0.3 | H-M4 | No | NOT_TESTED | No α sweep in H-E1; deferred to H-M4 |
| **P3:** LS_A > LS_P (p < 0.05) — oracle mechanism detectable via locality | H-E1 | Yes | INCONCLUSIVE | LS_A = LS_P = 0.0; p = 1.0. Null result from synthetic data — not a valid test |

### Planned vs. Actual Task Execution (03_tasks.yaml → 04_validation.md)

| Task | Planned | Actual | Gap |
|---|---|---|---|
| dp-1 | 488 miniF2F problems loaded | Completed (HuggingFace) | None |
| dp-2 | Vericoding downloaded | Attempted; fallback triggered | LeanDojo absent |
| env-1 | LeanDojo imports verified | NOT verified — ImportError | **Critical gap** |
| E2 | Real (state, tactic, compiler_error) triples | **Synthetic** — `_generate_synthetic_triples()` | **Critical gap** |
| E3 | State-aligned pairs from real Lean4 errors | Built on synthetic triples | Downstream of E2 failure |
| E4 | DPO training (β=10, 3 conditions) | Ran correctly | Implementation correct |
| E5 | LS_A > LS_P meaningful measurement | All zeros — synthetic artifact | Downstream of E2 failure |
| E6 | Statistical gate evaluation | p = 1.0; gate FAIL recorded | Correctly recorded failure |
| failsafe | 04_validation.md with informative result | Gate FAIL written | Correctly executed |

**Root cause:** Task E2 (LeanDojo tracing) failed silently due to absent Lean4 installation, triggering a synthetic data fallback that was not detected until post-run mock data check.

---

## Hypothesis Refinement

### Original Statement (from 03_refinement.yaml)

> Under fixed BFS geometry (BFS with length normalization α, fixed expansion width and tactic budget)
> and high formalization fidelity (≥85% audit threshold), if LLM policy training uses semantically
> grounded step-local formal feedback signals (Lean4 compiler errors or Z3 SMT counterexamples via
> DSL bridge) as DPO negative examples, then correctness recovery on hard benchmark instances
> (cold-start SFT baseline pass rate <20%) will be significantly greater (≥10pp, non-overlapping 95% CIs)
> compared to episode-level or semantically ungrounded feedback, because step-local grounded signals
> function as "local logical oracles" rather than "policy regularizers".

### Refined Statement (v2.0)

The existence of a step-local oracle mechanism — whereby semantically grounded Lean4 compiler
feedback used as DPO negatives produces concentrated probability mass shift toward premise-consistent
tactics (locality score LS_A > LS_P, p < 0.05) — **remains empirically untested**. The Phase 4
execution of H-E1 substituted synthetic proof state triples for real LeanDojo-extracted triples due
to an absent Lean4/LeanDojo installation, rendering all locality score measurements uninformative
(LS_A = LS_P = 0.0 by construction, not by finding).

The hypothesis retains its full theoretical grounding:
- The oracle/regularizer distinction remains a novel, testable, and well-motivated causal claim
- The experimental design (3-condition DPO: grounded A, ungrounded B, permuted P; locality score metric; pre-specified tactic taxonomy) remains valid and correct
- The DPO training infrastructure was implemented correctly (β=10, lr 5e-6→5e-7, 1-epoch)
- The state alignment protocol (100% state_id matching) was implemented correctly

**The hypothesis is NOT falsified. It is BLOCKED by infrastructure failure.**

### Scope of Claims

**Claims that survive Phase 4:**
- The oracle/regularizer mechanistic distinction is novel (no prior controlled comparison exists)
- The 2×2 factorial design (granularity × semantic groundedness) is appropriate for testing the claim
- BFS-Prover's operational success with Lean4 compiler feedback (72.95% miniF2F) is consistent with the oracle hypothesis (though not discriminating evidence for it)

**Claims suspended pending re-execution:**
- Whether LS_A > LS_P at p < 0.05 (P3 — primary gate for H-E1)
- Whether the oracle mechanism is detectable via locality score in the hard-instance regime

**Claims explicitly not made:**
- No conclusion about the oracle vs. regularizer distinction can be drawn from Phase 4 results
- The 0.0 locality scores do not indicate mechanism absence — they are synthetic artifacts

---

## Theoretical Interpretation

### What Was Actually Tested

Nothing meaningful regarding the oracle mechanism. The locality score computation
(`compute_locality_score`) ran on synthetic (state, tactic, compiler_error) triples generated
from hardcoded error strings. The probability mass shifts computed were over randomly constructed
proof state representations, not real Lean4 compiler outputs.

### Infrastructure Findings (Valid Outputs of Phase 4)

1. **DPO training loop is correct:** β=10.0, lr 5e-6→5e-7 linear decay, 1-epoch, concatenated forward pass (average_log_prob=False) — matches eric-mitchell/DPO reference implementation.

2. **State alignment logic is correct:** 100% state alignment rate confirmed for the DPO pair builder (s_w == s_l via state_id). The protocol works; it just ran on synthetic state IDs.

3. **Tactic taxonomy is pre-specified:** {type_error, undefined_name, tactic_failure} defined before any training — assumption A4 satisfied.

4. **Mock detection works:** External LLM verification correctly identified the synthetic data substitution at lines 50-51, 62-64, 114-137 of leandojo_tracing.py. Pipeline monitoring is functioning.

### Causal Chain Status

| Step | Theoretical Status | Empirical Status |
|---|---|---|
| 1. Lean4 verifier produces step-local grounded rejection | Confirmed by BFS-Prover (external) | Not tested in this run |
| 2. Step-local rejection → state-aligned DPO pair | Design correct; infrastructure valid | Executed on synthetic triples only |
| 3. DPO → probability mass concentrates on premise-consistent tactics | Core untested claim (P3) | Not measured |
| 4. α-interaction: oracle advantage maximized at α=0 | Core untested claim (P2) | Not measured |

### Literature Context

**BFS-Prover [Xin et al. 2025, arXiv:2502.03438]:** 72.95% miniF2F with Lean4 compiler feedback + DPO — strong evidence that step-local grounded feedback *works*, but does not isolate oracle vs. regularizer mechanism. Provides the ground truth for our training setup (β=10, lr schedule, tactic budget).

**PropertyGPT [Liu et al. 2024]:** 87% vs. 63% compilation success with structured PSL compiler feedback (inference-time, no training). Supports the inference-time oracle interpretation.

**Proof of Thought [Ganguly et al. 2024]:** 14.6% → 0% compilation errors with Z3+DSL feedback loop (inference-time). Convergent evidence for oracle framing.

**Convergent evidence pattern:** Three independent systems achieving significant improvements with structured formal feedback, zero systems demonstrating the mechanism via controlled ablation. The gap our hypothesis targets remains open.

### Competing Interpretations of the Gate FAIL

1. **Infrastructure failure (most likely):** LeanDojo absent → synthetic data → null result. No scientific content.

2. **Methodological fragility (secondary):** The locality score metric requires a functioning LeanDojo environment, which is non-trivial to install on GPU clusters (Lean4 toolchain, elan, compiled Lean4 core). This is a practical limitation of the experimental design.

3. **Null hypothesis correct (not supported by this run):** The gate fail could in principle reflect a true null result (LS_A ≈ LS_P). But this interpretation requires evidence from a valid experiment — the synthetic run provides no support for this interpretation.

---

## Experiment Results

### Gate Condition

PoC PASS requires: `LS_A > LS_P` (locality score of Condition A > Permutation Control, p < 0.05)

**Gate Result: FAIL**

### miniF2F Hard Subset Results

| Metric | Value |
|--------|-------|
| Condition A (Grounded) LS | 0.0000 |
| Condition B (Ungrounded) LS | 0.0000 |
| Condition P (Permuted) LS | 0.0000 |
| t-statistic | 0.0000 |
| p-value (one-sided) | 1.0000 |
| Gate Pass | False |
| Secondary (LS_A > LS_B) | False |

### Vericoding Hard Subset Results

| Metric | Value |
|--------|-------|
| Condition A (Grounded) LS | 0.0000 |
| Condition B (Ungrounded) LS | 0.0000 |
| Condition P (Permuted) LS | 0.0000 |
| t-statistic | 0.0000 |
| p-value (one-sided) | 1.0000 |
| Gate Pass | False |
| Secondary (LS_A > LS_B) | False |

### DPO Training Configuration (Correctly Executed)

| Parameter | Value |
|-----------|-------|
| Model | ByteDance-Seed/BFS-Prover-V2-7B |
| DPO β | 10.0 |
| Learning rate | 5e-06 → 5e-07 (linear decay) |
| Epochs | 1 |
| State alignment rate | 100% |
| Tactic taxonomy | Pre-specified (type_error, undefined_name, tactic_failure) |

### Failure Diagnosis

All zero locality scores are a direct artifact of synthetic data generation:
- `_generate_synthetic_triples()` in `leandojo_tracing.py` (lines 50-51, 62-64, 114-137) returned hardcoded error strings
- No real Lean4 compiler invocations were made
- No real proof state transitions were measured
- The DPO training ran correctly but on meaningless inputs

### Synthesis Confidence Assessment

| Dimension | Assessment | Rationale |
|---|---|---|
| Hypothesis validity | HIGH (0.78, unchanged) | No scientific evidence against; infrastructure failure does not bear on mechanism |
| Experimental design validity | HIGH | 03_tasks.yaml and 02c_experiment_brief.md are correct; design is sound |
| Implementation correctness | MIXED | DPO loop correct; LeanDojo tracing incorrect (fallback) |
| Re-run success probability | MEDIUM | Depends on LeanDojo installation success on H100 |
| Oracle mechanism prior probability | MODERATE-HIGH | Convergent evidence from 3 independent systems; no contradicting results |

---

## Limitations

| ID | Limitation | Root Cause | Scientific Impact | Infrastructure Impact |
|---|---|---|---|---|
| L1 | LeanDojo installation absent | Lean4 toolchain (elan + compiler) not pre-installed on H100 cluster | None — hypothesis not tested | **Hard blocker** — all H-E1 locality measurements require real LeanDojo |
| L2 | Silent synthetic data fallback | `_generate_synthetic_triples()` in production path (leandojo_tracing.py:50-51, 62-64, 114-137) | Masked failure; results appeared to run | Medium — easy to fix: remove fallback from non-test paths |
| L3 | Hard subset not constructed | Cold-start SFT evaluation requires functioning BFS-Prover inference pipeline; model.verified = false | No valid hard subset defined | Medium — requires BFS-Prover model download + evaluation |
| L4 | Vericoding not retrieved | Manual download required from arXiv:2509.22908 paper release | H-E1 would be miniF2F-only without it | Low — simple download task |

**None of L1–L4 reflect on the scientific validity of the oracle/regularizer hypothesis.** All are infrastructure and implementation failures specific to this Phase 4 run.

---

## Future Work

### Immediate Actions (Required for H-E1 Completion)

**FW1 — Install Lean4 toolchain and verify LeanDojo:**
```bash
curl -sSf https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh | sh
source ~/.profile
lean --version
python -c "import lean_dojo; print('LeanDojo OK')"
```
Estimated effort: 1-2 days (environment setup, dependency resolution on H100).

**FW2 — Remove synthetic data fallback from production code:**
- Move `_generate_synthetic_triples()` to `tests/` only
- Add hard abort: if `len(real_triples) == 0`, raise `RuntimeError("No real triples extracted — LeanDojo not functioning")`
- Add pre-run sanity check: verify at least 10 real triples before DPO training

**FW3 — Construct cold-start SFT hard subset:**
- Download ByteDance-Seed/BFS-Prover-V2-7B from HuggingFace
- Run 16-rollout evaluation on full miniF2F (488 problems) and Vericoding Lean4 subset
- Freeze problems with pass@1 < 20% as the hard subset

### Scientific Extensions (Conditional on H-E1 Gate Pass)

**FW4 — Cross-formalism oracle test:** Test whether the locality effect holds for Verus and Dafny formalisms in Vericoding, or whether it is Lean4-specific.

**FW5 — Inference-time oracle (Experiment A, frozen policy):** Measure whether the oracle effect appears at inference time (structured feedback loop, no DPO) as well as training time.

**FW6 — Minimum fidelity threshold:** Test what formalization fidelity level is required before the oracle mechanism breaks down. The 85% threshold (A1) is empirically motivated but not validated.

### Pipeline Design Lessons

**FW7 — Pre-run environment validation gate:** Before any Phase 4 experiment with external tool dependencies (LeanDojo, Z3, etc.), add an explicit environment check step that must pass before the coder agent begins implementation.

---

## Implications for Phase 6

**Current status:** H-E1 MUST_WORK gate FAIL (infrastructure, not scientific)

**Routing recommendation:**
- **DO NOT** route to Phase 0 (hypothesis not falsified — infrastructure failure)
- **DO NOT** route to Phase 2A-Dialogue (hypothesis not contradicted)
- **ROUTE TO:** Phase 4 retry after infrastructure fix (install LeanDojo, remove synthetic fallback, construct hard subset)

**Routing justification:**
Per verification_state.yaml failure routing rules:
- `phase4_must_work_partial` → max 1 attempt → route to Phase 2A-Dialogue
- `phase4_must_work_fail` → route to Phase 0

However, the standard routing logic assumes a scientific failure. This is an infrastructure failure (return_reason = mock_data_detected). The appropriate action:
1. Fix leandojo_tracing.py (remove fallback)
2. Install Lean4 toolchain
3. Retry Phase 4 for H-E1 (counts as the modification_attempt = 1)
4. If real data run also fails gate → then route to Phase 2A-Dialogue

**If H-E1 gate passes on re-run:** Proceed with H-M1 → H-M2 → H-M3 → H-M4 → H-C1 sub-hypothesis chain per verification_state.yaml prerequisites. Phase 6 paper writing can incorporate the oracle/regularizer mechanistic distinction as a novel contribution with controlled ablation evidence.

**If H-E1 gate fails on re-run (with real data):** The oracle mechanism (LS_A > LS_P) is not detectable at the 3-condition DPO level. Route to Phase 2A-Dialogue to revise the locality score operationalization or the granularity hypothesis.

---

*Generated by Phase 4.5 Hypothesis Synthesis — Anonymous Pipeline*
*Date: 2026-05-20*
*Sources: verification_state.yaml, h-e1/04_validation.md, h-e1/03_tasks.yaml*
