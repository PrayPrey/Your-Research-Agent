# Hypothesis Context: H-M1

**Generated from:** Phase 2B Verification Plan (JIT)
**Date:** 2026-05-12
**Main Hypothesis:** Residual Instability as an Orthogonal Trust-Failure Predictor in LLMs
**Phase 2B Source:** 02b_verification_plan.md

---

## Hypothesis Information

### Statement
Under the ≥30 LLM model set with computed RI scores, if Spearman partial correlation ρ(RI, ECE | PC1, mean_confidence) is computed, then ρ ≥ 0.4 with Holm-corrected p < 0.05 and consistent positive sign across ≥2 of 3 family subgroups, because sharp decision boundaries cause overconfident predictions in brittle regions, producing calibration error.

### Type
MECHANISM (MUST_WORK gate)

### Rationale
This is the primary mechanism test and the most critical MUST_WORK gate. The causal story hinges on RI → ECE being the first downstream coupling: models fragile under adversarial perturbation overcommit confidence to brittle predictions. Failure here invalidates the entire RI construct.

---

## Verification Protocol

### Conceptual Test
Test whether Residual Instability (RI), after controlling for general capability (PC1) and mean confidence, significantly predicts Expected Calibration Error (ECE) across a diverse set of ≥30 LLMs, with consistent positive direction across model families.

### Success Criteria
- Primary: Spearman partial ρ(RI, ECE | PC1, mean_confidence) ≥ 0.4, Holm-corrected p < 0.05
- Secondary: Consistent positive sign in ≥2 of 3 family subgroups (LLaMA, Mistral, GPT/Qwen); no significant PC1 interaction that eliminates main effect

### Verification Steps
1. Compute ECE for all models via p-lambda/verified_calibration library on QA benchmarks; collect bootstrap CIs (10,000 resamples).
2. Compute Spearman partial correlation ρ(RI, ECE | PC1, mean_confidence) with Holm-Bonferroni correction across full model set.
3. Run split-sample Fisher z-test: divide by median PC1; compute ρ_high and ρ_low; test for significant interaction.
4. Compute within-family partial correlations for LLaMA, Mistral, and GPT/Qwen subsets separately.
5. Report VIF < 5 for multicollinearity check; Cook's distance for outlier sensitivity.

### Variables
- **Independent Variable:** Residual Instability (RI) — OLS residual of AdvGLUE_drop ~ PC1 + mean_confidence
- **Dependent Variable:** Expected Calibration Error (ECE) via p-lambda/verified_calibration on QA benchmarks
- **Controlled Variables:** Capability-PC1, Mean model confidence, Model family (covariate in within-family analysis)

---

## Experimental Setup (from Phase 2A via Phase 2B)

> **Note:** Dataset and model were selected in Phase 2A Dialogue based on hypothesis Variables.
> Phase 2C experiment design MUST use this selection.

### Selected Dataset
- **Name:** ECE via p-lambda/verified_calibration on QA benchmarks (TrustLLM + lm-evaluation-harness multi-benchmark matrix)
- **Type:** standard
- **Source:** TrustLLM (HowieHwong/TrustLLM); EleutherAI/lm-evaluation-harness; p-lambda/verified_calibration library
- **Path:** Scores available via TrustLLM toolkit for 16 models; additional open-source models via lm-evaluation-harness public results
- **Hypothesis Fit:** ECE scores measure calibration quality per model — exactly the dependent variable for ρ(RI, ECE) test. The multi-benchmark matrix provides RI (from H-E1 pipeline) and ECE for the same model set.

### Selected Model
- **Name:** ≥30 LLMs (same set as H-E1): LLaMA-series, Mistral-series, Qwen-series, GPT-series
- **Type:** Autoregressive transformer LLMs (evaluation/inference only — no training)
- **Source:** TrustLLM 16 models + additional open-source from lm-evaluation-harness; Open LLM Leaderboard v2 capability data
- **Hypothesis Fit:** Same diverse model set used for H-E1 RI computation — enables reuse of validated RI scores and DataAssembler pipeline. Family diversity (9 families) enables within-family subgroup analysis.

---

## Baseline & Comparison Targets

### Baseline Methods
- **Capability-only predictor**: OLS/Spearman ρ(PC1, ECE) — ECE predicted by general capability alone, no RI term
- **TrustLLM independent scoring**: Reports ECE per model independently without cross-dimension predictive correlation
- **DecodingTrust**: Evaluates calibration independently, no RI construct or partial correlation framework

### Baseline Performance
- TrustLLM (ICML 2024): 16 LLMs benchmarked; higher-capability models (GPT-4) show lower ECE but data is model-family-specific
- Prior partial correlation studies: ρ(capability, ECE) ≈ 0.3–0.5 (capability partially predicts calibration)
- Expected ρ(RI, ECE) before capability control: ~0.4–0.6 (from TrustLLM cross-dimension analysis)

### Gap Analysis
- Gap to fill: No study has shown ρ(RI, ECE | PC1) ≥ 0.4 — i.e., adversarial fragility predicts calibration AFTER controlling for capability
- If gap confirmed: RI is an orthogonal predictor of calibration error beyond capability

---

## Dependencies and Gate Conditions

### Prerequisites
- **H-E1**: COMPLETED (PASS) — RI construct validated; SD(AdvGLUE_drop)=0.1212, R²=0.5285
- Reuse: `code/compute_ri.py`, `code/data_assembly.py`, `code/evaluate.py` from H-E1 environment `youra-h-e1`

### Gate Information

**Gate Type:** MUST_WORK
- MUST_WORK: Failure stops entire workflow

**Consequence if Fails:** ABANDON construct claim; pivot to descriptive correlation paper without RI as predictive construct. Invalidates H-M2, H-M3, H-M4.

**Phase Assignment:** Phase 2C → 3 → 4

**Estimated Duration:** ~15-20 minutes (data extension + partial correlation pipeline)

---

## Dependency Context

### Relationship to Other Hypotheses
- **Depends on H-E1**: Uses RI scores computed in H-E1; reuses validated pipeline
- **Gates H-M2**: If H-M1 fails, H-M2 (HaluEval) is blocked (RI construct invalidated)
- **Gates H-M3, H-M4**: Downstream hypotheses depend on H-M1 PASS
- **MUST_WORK**: This is the critical causal link — RI → ECE is the first trust-failure coupling

---

## Verification State Reference

**State File:** verification_state.yaml
**Current Status:** IN_PROGRESS
**Workflow Status:** ACTIVE

---

## Phase 2C Usage Notes

**This context file provides:**
1. Complete hypothesis specification for experiment design
2. Gate conditions for prerequisite validation
3. Dependency information for controlled experiments (reuse H-E1 pipeline)
4. Success criteria for evaluation design
5. Continuation context: H-E1 proven components available

**Phase 2C will:**
1. Load this file instead of full Phase 2B roadmap (91% smaller)
2. Search for ECE computation and partial correlation implementations (Archon, Exa MCP)
3. Design concrete experiment specification extending H-E1 pipeline with ECE data
4. Output: h-m1/02c_experiment_brief.md

---

*Generated by Phase 2C Workflow (JIT)*
*Optimized for single-hypothesis experiment design*
