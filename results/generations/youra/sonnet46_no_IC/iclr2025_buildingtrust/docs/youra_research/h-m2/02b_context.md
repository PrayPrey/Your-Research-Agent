# Phase 2B Context: H-M2
## RLHF Representation Rigidity Reduces Adversarial Robustness

**Generated:** JIT by Phase 2C step-01-init (from 02b_verification_plan.md)
**Date:** 2026-08-04
**Hypothesis ID:** h-m2

---

## Hypothesis Information

**Statement:** Under the TrustLLM 16-model setting, if RLHF-induced conservative refusal patterns create representation-level rigidity that is brittle to adversarial perturbations, then ρ_partial(safety, robustness) < -0.4 (p < 0.0033), and RLHF Chat variants should score EQUAL OR LOWER on adversarial robustness compared to size-matched base models, because the same pattern-matching representations that avoid harmful outputs via conservative prediction are brittle to adversarial input perturbations.

**Type:** MECHANISM (Step 2 of 3-step RLHF causal chain)
**Gate:** SHOULD_WORK
**Prerequisites:** H-M1 (COMPLETED, PASS)

**Rationale:** Tests the safety-robustness anti-correlation that produces the negative cross-cluster partial ρ. Grounded in AQUA-LLM accuracy-robustness tradeoff and Know Thy Judge safety judge brittleness evidence. The negative sign is the mechanistic signature of RLHF's dual effect.

---

## Experimental Setup (from Phase 2A via Phase 2B)

### Dataset
- **Name:** TrustLLM Published Score Tables (adversarial robustness dimension) + Pythia scaling series
- **Type:** standard + derived
- **Source:** https://github.com/HowieHwong/TrustLLM (results/ folder, robustness dimension scores) + EleutherAI/pythia lm-eval-harness scores
- **Path:** HowieHwong/TrustLLM repository / results/*.json (robustness column); Pythia scores via lm-eval-harness on AdvGLUE/ANLI
- **Hypothesis Fit:** The TrustLLM dataset directly provides the adversarial robustness dimension scores needed to compute ρ_partial(safety, robustness) and within-family Δ_robustness comparisons. The existing 16×6 score matrix (reused from H-E1/H-M1) already contains the robustness column.

### Model
- **Name:** TrustLLM 16-model evaluation set + Pythia scaling series (70M–12B, EleutherAI)
- **Type:** convenience sample (TrustLLM 16) + controlled natural experiment (Pythia pure-scale baseline, RLHF=False for all)
- **Source:** TrustLLM: 16 models from published evaluation (pre-computed scores reused from H-E1); Pythia: EleutherAI/pythia-70m through pythia-12b via HuggingFace
- **Hypothesis Fit:** TrustLLM 16 models span RLHF vs base variants (LLaMA-2 7B/13B/70B family). Pythia series provides RLHF=False baseline to distinguish scale effect from alignment effect. Key test: Pythia within-series robustness correlation should be near-zero (scale only, no RLHF), whereas TrustLLM negative ρ indicates RLHF-specific effect.

---

## Verification Protocol

1. Extract adversarial robustness dimension scores for all 16 models from TrustLLM JSON (already in h-e1/experiment_results_phase3.json)
2. Compute Δ_robustness for LLaMA-2 family (3 within-family pairs: 7B, 13B, 70B): Δ_robustness = Chat_robustness − Base_robustness
3. Test sign: Δ_robustness ≤ 0 in ≥2/3 pairs (RLHF does not improve robustness)
4. Verify ρ_partial(safety, robustness) < -0.4 from H-E1 correlation matrix (pre-computed)
5. Pythia baseline: within-Pythia ρ(safety, robustness) should be near zero (RLHF=False, scale only)

---

## Success Criteria (PoC)

- **Primary:** ρ_partial(safety, robustness) < -0.4 AND p < 0.0033
- **Secondary:** ≥2/3 LLaMA-2 within-family Δ_robustness ≤ 0

**Gate Type:** SHOULD_WORK (failure = EXPLORE, not STOP)

---

## Failure Response

- IF primary fails (ρ_partial > 0): EXPLORE — report positive correlation as null finding; does not stop pipeline (SHOULD_WORK gate)
- IF Pythia shows same structure: EXPLORE — structure may be scale-driven, not RLHF-driven

---

## Dependencies

- **H-M1 (COMPLETED, PASS):** Establishes positive RLHF cluster (safety-ethics ρ=0.841). H-M2 establishes the negative cross-cluster link (safety-robustness < -0.4).
- **H-E1 (COMPLETED, PASS):** Pre-computed ρ_partial matrix (h-e1/experiment_results_phase3.json). Robustness column already extracted.

---

## Previous Hypothesis Results (H-M1 Context)

From H-M1 Phase 4 validation (h-m1/04_validation.md):
- ρ_partial(safety, machine_ethics) = 0.841 (PASS — positive RLHF cluster confirmed)
- 3/3 LLaMA-2 pairs: Δ_safety > 0 AND Δ_ethics > 0 simultaneously
- Dataset reuse: h-e1/experiment_results_phase3.json (16×6 rho_partial matrix + raw scores)
- Conda env: youra-h-m1, Python 3.10, scipy 1.11.0

**Continuation note:** H-M2 reuses the same TrustLLM 16×6 score matrix from H-E1. Only the robustness column and the ρ_partial(safety, robustness) value need to be extracted from already-computed results. The Pythia comparison requires lm-eval-harness scores (new data component).

---

## Key Assumptions for H-M2

| ID | Assumption | If Violated |
|----|------------|-------------|
| A1 | TrustLLM robustness dimension scores are available per-model in results/*.json | Extract from raw benchmark; SHOULD_WORK gate means pipeline continues |
| A2 | LLaMA-2 Chat models show lower robustness than base variants | Negative result publishable as EXPLORE finding |
| A3 | Pythia RLHF=False series provides clean scale-only control | Skip Pythia component; report TrustLLM result only |

---

*JIT-generated from 02b_verification_plan.md H-M2 section*
