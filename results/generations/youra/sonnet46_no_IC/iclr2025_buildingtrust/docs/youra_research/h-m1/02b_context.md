# H-M1 Context: RLHF Directly Co-Optimizes Safety and Ethics

**Generated:** 2026-08-04 (JIT by Phase 2C step-01)
**Source:** 02b_verification_plan.md
**Hypothesis ID:** h-m1

---

## Hypothesis

**ID:** H-M1
**Type:** MECHANISM
**Gate:** MUST_WORK
**Prerequisites:** H-E1 (SATISFIED — ρ_partial(safety, machine_ethics)=0.841, ρ_partial(safety, fairness)=0.859 confirmed)

**Statement:**
Under the TrustLLM 16-model setting with partial Spearman controls, if RLHF fine-tuning directly rewards safe and ethics-aligned outputs via preference learning, then RLHF Chat/Instruct models will outscore size-matched base models on BOTH safety AND ethics simultaneously, and ρ_partial(safety, ethics) > 0.5 (p < 0.0033), because RLHF reward signals penalize harmful outputs and reward value-aligned responses — jointly optimizing both safety and ethics dimensions.

## Experimental Setup (from Phase 2A via Phase 2B)

**Dataset:**
- Name: TrustLLM Published Score Tables (LLaMA-2 family: 7B/13B/70B base+Chat)
- Type: standard
- Source: HowieHwong/TrustLLM GitHub — results/*.json
- Path: https://github.com/HowieHwong/TrustLLM
- Hypothesis Fit: Provides exact per-model per-dimension scores for 16 models including LLaMA-2 family with base and Chat variants at 3 scales

**Model:**
- Name: TrustLLM 16-model set (LLaMA-2 family within-family pairs)
- Type: Pre-computed score analysis (no neural model training)
- Source: TrustLLM published evaluation
- Hypothesis Fit: LLaMA-2 7B/13B/70B base+Chat pairs provide natural experiment: same architecture, same pretraining, only RLHF differs

## Verification Protocol (from Phase 2B)

1. Extract LLaMA-2 7B, 13B, 70B base and Chat variant scores from TrustLLM JSON
2. Compute within-family signed differences: Δ_safety = Chat_safety - Base_safety; Δ_ethics = Chat_ethics - Base_ethics for each scale
3. Test sign: all 3 Δ_safety > 0 AND all 3 Δ_ethics > 0 (both improve with RLHF)
4. Verify ρ_partial(safety, ethics) > 0.5 from H-E1 correlation matrix
5. HELM replication: compute same correlation on HELM subset

## Success Criteria

- **Primary:** ρ_partial(safety, ethics) > 0.5 AND p < 0.0033
- **Secondary:** ≥2/3 within-family pairs show Δ_safety > 0 AND Δ_ethics > 0 simultaneously

## Gate Condition

**MUST_WORK:** If ρ_partial(safety, ethics) > 0.5 fails → PIVOT (check RLHF classification; DPO/SFT mis-labeling)

## Previous Hypothesis Results

**H-E1 (PASS):** 8 significant partial Spearman pairs confirmed. Key relevant result:
- ρ_partial(safety, machine_ethics) = 0.841, p=1.63e-04 ✅
- ρ_partial(safety, fairness) = 0.859, p=8.37e-05 ✅
- ρ_partial(safety, privacy) = 0.971, p=8.77e-09 ✅
- These are the within-H-E1 rho_partial matrix values — h-m1 primary gate (ρ_partial(safety, ethics)>0.5) is already satisfied from H-E1 results.

**Key implication:** H-M1 primary criterion is ALREADY confirmed by H-E1 output. H-M1 adds the within-family directional test (Δ_safety > 0, Δ_ethics > 0 for LLaMA-2 pairs) as the mechanistic evidence.
