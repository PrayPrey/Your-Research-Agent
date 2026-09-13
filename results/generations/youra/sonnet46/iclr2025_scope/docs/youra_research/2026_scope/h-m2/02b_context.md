# Phase 2B Context: H-M2

**Generated:** 2026-05-08 (JIT from 02b_verification_plan.md by Phase 2C step-01)
**Hypothesis ID:** H-M2
**Type:** MECHANISM
**Prerequisites:** H-E1 (PASS)

---

## Hypothesis Statement

Layer-wise MLP activation sparsity variation in LLaMA-3-8B (CV > 0.3) is robust to epsilon threshold choice, holding for at least 3 of 4 epsilon values in {0.001, 0.01, 0.05, 0.1}, and the layer rank ordering is stable across epsilon values (Kendall's tau between epsilon conditions >= 0.7), because the relative sparsity ordering reflects layer structural differences that persist across threshold choices.

## Gate Condition

**Type:** MUST_WORK
**Satisfied:** Not yet (pending experiment)
**Failure Response:** IF CV collapses for most epsilon values → PIVOT — try activation magnitude (L1 norm per layer) as alternative proxy

## Experimental Setup

### Dataset
- **Name:** Alpaca 512 samples (primary) — reuse from H-E1
- **Type:** standard
- **Source:** tatsu-lab/alpaca (HuggingFace)
- **Path:** `load_dataset("tatsu-lab/alpaca")` — 512 random samples
- **Hypothesis Fit:** Provides the exact sparsity measurement data used in H-E1; epsilon sweep requires no new data collection, only re-analysis of existing hook outputs

### Model
- **Name:** LLaMA-3-8B (meta-llama/Meta-Llama-3-8B)
- **Type:** Decoder-only LLM, SiLU MLP gating
- **Source:** HuggingFace `meta-llama/Meta-Llama-3-8B`
- **Hypothesis Fit:** 32 MLP layers provide per-layer diversity; SiLU soft-sparsity is the exact mechanism being characterized; model already validated in H-E1

## Variables

- **Independent:** Epsilon threshold ∈ {0.001, 0.01, 0.05, 0.1}
- **Dependent:** CV per epsilon; Kendall's tau between epsilon conditions; Kendall's tau (Alpaca vs. WikiText) per epsilon
- **Controlled:** LLaMA-3-8B inference mode; Alpaca 512 samples; same hook pipeline as H-E1

## Success Criteria

- **Primary:** CV > 0.3 for ≥ 3 of 4 epsilon values; Kendall's tau ≥ 0.7 between epsilon conditions (e.g., 0.01 vs. 0.05)
- **Secondary:** Kendall's tau ≥ 0.6 for Alpaca vs. WikiText at optimal epsilon

## Continuation Context

- **Previous Hypothesis:** H-E1 (PASS) and H-M1 (PASS)
- **Reuse:** Full hook pipeline from H-E1; raw sparsity data for all 4 epsilon values already collected
- **Key Findings from H-E1:** CV=0.544 at epsilon=0.01; tau_calibration=0.786; all 4 epsilon values yield CV > 0.3 and tau >= 0.6

## Dependencies

- H-E1: Sparsity pipeline established, CV > 0.3 confirmed, raw data available for all epsilon values
