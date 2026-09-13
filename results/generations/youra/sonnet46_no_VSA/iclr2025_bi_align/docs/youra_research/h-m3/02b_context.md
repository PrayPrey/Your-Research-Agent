# H-M3 Per-Hypothesis Context (JIT Generated from 02b_verification_plan.md)

**Generated:** 2026-07-30
**Source:** docs/youra_research/02b_verification_plan.md → Section 2.2 H-M3

---

## Hypothesis Information

**ID:** H-M3
**Type:** MECHANISM
**Gate:** SHOULD_WORK
**Status:** NOT_STARTED → IN_PROGRESS (Phase 2C)

**Statement:**
Under the partial Spearman residuals from H-M2, the partial_rho value for TruthfulQA MC2 × BBQ accuracy will be assignable to one of three pre-specified scenarios: (a) |partial_rho| < 0.20 (independent constructs), (b) partial_rho > 0.40 (scale-free coherence), or (c) partial_rho < -0.20 (scale-masked tradeoff), because these three outcomes exhaustively characterize the possible dimensional relationships between factuality and bias in the alignment-specific benchmark space.

**Rationale:**
Each of the three scenarios produces a distinct publishable narrative about alignment construct dimensionality. Scenario (a) supports the "multi-dimensional alignment" framing; (b) supports "coherent alignment signal"; (c) reveals a hidden tradeoff masked by scale. Tier 2 (HarmBench) extends this to the safety dimension if N≥20.

---

## Variables

- **IV:** partial_rho output from H-M2 (scale-free correlation)
- **DV:** Scenario assignment (a/b/c) based on partial_rho magnitude and sign; BCa CI range
- **CV:** Tier 2 (HarmBench, N≥20) as extension; Tier 3 (ΔBBQ sign test, OPTIONAL)

---

## Verification Protocol

1. Use partial_rho and BCa CI from H-M2; assign to scenario (a), (b), or (c)
2. If CI overlaps 0 AND overlaps 0.40: report "underpowered — scenario ambiguous" (not a gate failure)
3. Tier 2 (if N_harmbench ≥ 20): repeat partial Spearman for TruthfulQA×HarmBench and BBQ×HarmBench pairs; assign each to a/b/c
4. Tier 3 (OPTIONAL): sign test for ΔBBQ (chat-base) on 321 pairs from h-m1 dataset; scipy.stats.binomtest
5. Write summary table: all computed pairs × scenario assignment × CI

---

## Success Criteria

- **Primary:** partial_rho (TruthfulQA×BBQ) assigned to scenario with non-ambiguous BCa CI (SHOULD_WORK)
- **Secondary:** Tier 2 pairs characterized if N≥20; Tier 3 RLHF effect direction reported if significant

**Failure Response:**
- IF CI ambiguous (overlaps both 0 and 0.40): report "N insufficient for scenario characterization"; SHOULD_WORK gate — does not block Phase 4.5

---

## Experimental Setup (from Phase 2A)

**Dataset:**
- Name: Open LLM LB v1 × lighteval/bbq_helm × HarmBench Table 2 (tiered)
- Type: programmatic-api
- Source: H-M2 output (h_m2_results.json) + hardcoded HarmBench Table 2 data
- Path: `docs/youra_research/h-e1/code/data/llm_leaderboard_v1/llm.csv` (Tier 1 via H-M2)
  - Tier 2: HarmBench Table 2 hardcoded (33 models, arXiv:2402.04249)
  - Tier 3: 321 base/chat pairs from h-m1 dataset
- Hypothesis Fit: H-M3 is purely a downstream analysis of H-M2 partial_rho output; all data is inherited

**Model:**
- Type: Observational cross-section (open-weight LLMs are study subjects, no training)
- Source: H-M2 computed results
- Hypothesis Fit: No ML model training; statistical analysis only

---

## Dependencies

- **H-M2** (MUST be VALIDATED): partial_rho value and BCa CI from H-M2 are the primary inputs
- **H-E1**, **H-M1**: Transitively satisfied via H-M2

---

## Gate Condition

**SHOULD_WORK**: partial_rho (TruthfulQA×BBQ) assignable to scenario (a/b/c) with non-ambiguous BCa CI.
Does NOT block the pipeline if ambiguous — report "underpowered" as a valid outcome.

---

## Baseline Methods

| Method | Description |
|--------|-------------|
| Raw Spearman (uncontrolled) | rho(AlpacaEval-LC, TruthfulQA MC1) = +0.661 (historical) |
| H-M2 raw_rho | Uncontrolled Spearman(TruthfulQA×BBQ) from same dataset |
| H-M2 partial_rho | MMLU-controlled partial Spearman (this is the input to H-M3) |

---

## Risks

| Risk | Mitigation |
|------|-----------|
| R3: Llama clustering bias | Family-clustered BCa CI from H-M2 |
| R4: HarmBench N < 20 | Tier 2 SHOULD_WORK only; does not block Tier 1 |
| CI ambiguity | Report "underpowered" — valid SHOULD_WORK outcome |
