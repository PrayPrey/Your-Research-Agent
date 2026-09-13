# Phase 2B: PoC Verification Plan

**Generated:** 2026-08-20T02:27:19Z  
**Workflow:** phase2b-planning  
**Mode:** UNATTENDED (batch processing)  
**Main Hypothesis:** H-ParetoUQ-v1

---

## Executive Summary

**Research Question:** Can single-pass uncertainty quantification methods achieve meaningful selective prediction performance (AUROC ≥ 0.70) on TruthfulQA while exhibiting cost-performance trade-offs that enable budget-aware method selection?

**Verification Strategy:** 3-hypothesis PoC validation testing existence (H-E1), mechanism pipeline (H-M-integrated), and Pareto frontier construction (H-M-pareto). Baseline comparison deferred to Phase 5.

**Scope Reduction:** 57% of conceptual groundwork already established (BUILD_ON claims from Phase 2A). Only 3 PROVE_NEW claims require empirical validation.

**Total Sub-Hypotheses:** 3 (H-E1, H-M-integrated, H-M-pareto)

---

## Main Hypothesis

**ID:** H-ParetoUQ-v1  
**Confidence:** 0.85

**Statement:**  
Under selective prediction on TruthfulQA (817 human-annotated questions) using Llama-3.1-8B-Instruct, if we compare temperature scaling (0× cost), conformal prediction (0× cost), and MC dropout (k-dependent cost), then at least 2 methods will occupy distinct positions on the empirical Pareto frontier (no method strictly dominates another), because different UQ mechanisms trade off calibration quality vs computational cost at different efficiency zones.

**Alternative Hypothesis (H0):**  
There is no cost-performance trade-off: a single method (e.g., MC dropout k=5) strictly dominates all others by achieving both higher AUROC and equal-or-lower inference cost, collapsing the Pareto frontier to one optimal point.

**Null Hypothesis Rejection Criteria:**
- Reject H0 if |Pareto set| ≥ 2 (H3 confirmed)
- Reject H0 if temp scaling achieves AUROC within Δ=0.05 of MC dropout k=5 AND MC k=5 has highest AUROC (H2 + H1 confirmed)

---

## Controlled Variables (Phase 2A Section 1.2)

**Independent Variable:**
- UQ_method (categorical): temperature_scaling, conformal_prediction, mc_dropout_k1, mc_dropout_k3, mc_dropout_k5, mc_dropout_k10

**Dependent Variable (Primary):**
- AUROC_selective_prediction: Area Under ROC Curve for binary classification (correct vs incorrect). Range [0.0, 1.0]. Success threshold ≥0.70.

**Controlled Variables:**
- model_architecture: Llama-3.1-8B-Instruct (fixed)
- calibration_dataset: HaluEval (~10k samples) for temp scaling and conformal prediction
- test_dataset: TruthfulQA (817 questions, human-annotated truthfulness labels)
- random_seed: Seeds 42, 123, 456 (n=3 runs)
- evaluation_protocol: Official TruthfulQA eval script (sylinrl/TruthfulQA)

---

## Established Facts (BUILD_ON - Skip Re-Verification)

From Phase 2A Section 0, these claims are pre-validated and do NOT require new hypotheses:

1. **Temperature scaling** is single-parameter post-hoc calibration with 0× inference overhead (Guo et al. 2017, 9294 citations)
2. **Conformal prediction** provides distribution-free coverage guarantees (Kumar et al. 2023, 148 citations)
3. **MC dropout** approximates Bayesian inference via k forward passes (Gal & Ghahramani 2016)
4. **TruthfulQA** has human-annotated truthfulness labels (817 questions) as ground truth (Lin et al. 2021)

**Scope Reduction:** 4 BUILD_ON claims / 7 total claims = 57% reduction

---

## Sub-Hypotheses Inventory

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
          HYPOTHESIS INVENTORY (3 hypotheses)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

| ID            | Type      | Statement (Brief)                                    | Prerequisites    | Gate        | Source              |
|---------------|-----------|------------------------------------------------------|------------------|-------------|---------------------|
| H-E1          | Existence | At least one UQ method achieves AUROC ≥ 0.70        | None             | MUST_WORK   | Phase 2A SH1, P0    |
| H-M-integrated| Mechanism | UQ pipeline produces valid uncertainty rankings      | H-E1             | MUST_WORK   | Causal Steps 1-3    |
| H-M-pareto    | Mechanism | ≥2 methods Pareto-optimal (trade-off exists)        | H-M-integrated   | SHOULD_WORK | Causal Steps 4-6, H3|

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## H-E1: AUROC Threshold Validation

**Type:** Existence  
**Gate:** MUST_WORK (blocking)  
**Prerequisites:** None (foundation hypothesis)

**Statement:**  
Under selective prediction on TruthfulQA (817 human-annotated questions) using Llama-3.1-8B-Instruct, if we apply any single-pass UQ method (temperature scaling, conformal prediction, or MC dropout k≤10), then at least one method achieves AUROC ≥ 0.70, because effective uncertainty quantification enables abstention from incorrect predictions.

**Rationale:**  
Validates that cost-efficient UQ methods can achieve meaningful selective prediction performance (AUROC ≥ 0.70 threshold). This is the foundational existence claim: if no method reaches 0.70, the entire hypothesis collapses (8B scale insufficient). Phase 0 baseline check (accuracy ≥ 45%) ensures sufficient signal for UQ methods to demonstrate value.

**Variables:**
- Independent: UQ_method (6 levels)
- Dependent: AUROC_selective_prediction (range [0.0, 1.0], success ≥0.70)
- Controlled: model_architecture (Llama-3.1-8B-Instruct), test_dataset (TruthfulQA 817), random_seed (42, 123, 456)

**Verification Protocol:**
1. Load Llama-3.1-8B-Instruct and TruthfulQA dataset, apply all 6 UQ methods to generate uncertainty scores.
2. For each method, rank questions by uncertainty (high = reject) and compute AUROC using human-annotated labels as ground truth.
3. Aggregate mean AUROC ± std over 3 random seeds per method.
4. Check success criterion: max(AUROC across 6 methods) ≥ 0.70.

**Success Criteria (PoC):**
- Primary: max(AUROC across 6 methods) ≥ 0.70 (at least one method effective)
- Secondary: All non-degenerate methods achieve AUROC > 0.55 (above random + margin)

**Failure Response:**
- IF max(AUROC) < 0.70: STOP experiment, document 8B scale limitation, recommend ≥70B model follow-up
- IF all AUROC < 0.60: CRITICAL FAIL - TruthfulQA too challenging for single-pass UQ at this scale

**Source:** Phase 2A Section 1.6 (Prediction P0 + H1), Phase 2B Section 5 (SH1)

---

## H-M-integrated: UQ Mechanism Pipeline

**Type:** Mechanism  
**Gate:** MUST_WORK (blocking)  
**Prerequisites:** H-E1 must PASS

**Statement:**  
Under the same conditions as H-E1, if we apply the UQ mechanism chain (method selection → uncertainty score generation → AUROC computation), then all non-degenerate methods produce uncertainty scores that correlate positively with prediction incorrectness (Spearman ρ > 0.2, AUROC > 0.55), because uncertainty estimates capture model confidence inversely related to correctness.

**Rationale:**  
Validates the core mechanism pipeline works end-to-end. Ensures uncertainty scores are not random but systematically correlate with prediction errors. Tests cross-dataset generalization: HaluEval calibration → TruthfulQA test for conformal prediction (DQ4 from Phase 2A).

**Variables:**
- Independent: UQ_method (6 levels as in H-E1)
- Dependent: uncertainty_scores (per-question values), Spearman_rho (correlation with incorrectness), AUROC (discrimination ability)
- Controlled: calibration_dataset (HaluEval ~10k for temp scaling + conformal prediction), random_seed (42, 123, 456)

**Verification Protocol:**
1. Apply each UQ method to TruthfulQA, extract uncertainty score per question.
2. Compute Spearman correlation between uncertainty and incorrectness (1 if wrong, 0 if correct).
3. Compute AUROC for selective prediction (uncertainty as discriminator).
4. Success: All methods (except MC k=1 baseline) achieve ρ > 0.2 AND AUROC > 0.55.

**Success Criteria (PoC):**
- Primary: All methods (except MC k=1) achieve AUROC > 0.55 AND Spearman ρ > 0.2
- Secondary: Conformal prediction AUROC within Δ=0.10 of temp scaling (calibration transfer)

**Failure Response:**
- IF conformal prediction fails (AUROC << temp scaling): Document cross-dataset limitation, continue with temp scaling + MC dropout only
- IF all methods fail (ρ < 0.2 or AUROC ≤ 0.55): STOP - mechanism does not work at 8B scale

**Source:** Phase 2A Section 1.3 (Causal Mechanism Steps 1-3), Section 1.4 (Assumption A2: HaluEval transfer)

---

## H-M-pareto: Pareto Frontier Construction

**Type:** Mechanism  
**Gate:** SHOULD_WORK (non-blocking - negative result is scientifically valuable)  
**Prerequisites:** H-M-integrated must PASS

**Statement:**  
Under the same conditions, if we construct the empirical Pareto frontier from (cost, AUROC) pairs for all 6 UQ methods, then at least 2 methods are Pareto-optimal (no method strictly dominates another with statistical significance p < 0.05), because different UQ mechanisms trade off calibration quality vs computational cost at different efficiency zones, enabling budget-aware method selection.

**Rationale:**  
Core novelty claim - tests whether cost-performance trade-offs exist (H3 from Phase 2A). If only 1 method is Pareto-optimal (e.g., MC dropout k=5 dominates all), the Pareto frontier collapses and budget-aware UQ selection is unnecessary. Also tests H1 (MC k=5 highest AUROC) and H2 (temp scaling competitive within Δ=0.05).

**Variables:**
- Independent: cost_AUROC_pairs (6 methods with (cost_i, AUROC_i), cost = FLOPs normalized to 1.0× baseline)
- Dependent: Pareto_set (methods where no other method dominates), Pareto_set_size (success: |Pareto_set| ≥ 2)
- Controlled: statistical_test (paired t-test, α=0.05, n=3 seeds for AUROC comparisons)

**Verification Protocol:**
1. Collect (cost, AUROC) pairs from H-M-integrated results for all 6 methods.
2. For each method i, check dominance: Does any method j have cost_j ≤ cost_i AND AUROC_j > AUROC_i (paired t-test p < 0.05)?
3. Construct Pareto_set = {i | no method dominates i}.
4. Test H1 (MC k=5 highest), H2 (|AUROC_temp - AUROC_mc5| ≤ 0.05), H3 (|Pareto_set| ≥ 2).

**Success Criteria (PoC):**
- Primary: |Pareto_set| ≥ 2 (H3 PASS - cost-performance trade-off exists)
- Secondary: H1 PASS (MC k=5 highest AUROC), H2 PASS (temp scaling competitive)

**Failure Response:**
- IF H3 FAIL (|Pareto_set| = 1): Document negative result - "MC dropout k=5 universally optimal, no trade-off at 8B scale"
- IF H2 FAIL (temp scaling not competitive): Practitioners should default to MC dropout for high-stakes selective prediction
- IF H1 FAIL (MC k=5 not highest): Surprising efficiency - zero-cost methods superior

**Source:** Phase 2A Section 1.3 (Causal Mechanism Steps 4-6), Section 1.6 (Predictions H1/H2/H3), Section 2 (Novelty claim)

---

## Key Assumptions & Risks

### A1: 8B Model Baseline Accuracy ≥ 45%
- **Validity:** HIGH
- **Validation:** Phase 0 pre-check empirically measures Llama-3.1-8B-Instruct accuracy on TruthfulQA
- **Consequence if Violated:** CRITICAL - insufficient signal for UQ methods. Would invalidate entire experiment at 8B scale. Mitigation: document limitation and recommend ≥70B model follow-up.

### A2: HaluEval Calibration Transfers to TruthfulQA
- **Validity:** MEDIUM
- **Validation:** Cross-dataset generalization explicitly tested in H-M-integrated
- **Consequence if Violated:** MEDIUM - conformal prediction may fail to transfer. This is a scientifically valuable negative result if observed.

### A3: Human-Annotated TruthfulQA Labels Reliable
- **Validity:** HIGH
- **Validation:** Official TruthfulQA dataset uses human consensus annotations (Lin et al. 2021, 911 GitHub stars)
- **Consequence if Violated:** LOW - dataset is foundational in LLM evaluation community.

### A4: FLOPs Count Accurately Reflects Inference Cost
- **Validity:** HIGH
- **Validation:** FLOPs is hardware-agnostic and deterministic (normalized to 1.0× baseline)
- **Consequence if Violated:** LOW - practitioner costs include latency (wall-clock), not just FLOPs. Mitigation: report both FLOPs and wall-clock time in supplementary materials.

### A5: Statistical Significance (n=3 seeds) Sufficient
- **Validity:** MEDIUM
- **Validation:** Standard in ML research (3 random seeds is common practice)
- **Consequence if Violated:** MEDIUM - small n=3 may miss rare failure modes. Mitigation: if results show high variance (std > 0.03 AUROC), increase to n=5 seeds for critical comparisons.

---

## Dependency Graph

```
H-E1 (Existence)
  ↓
H-M-integrated (Mechanism Pipeline)
  ↓
H-M-pareto (Pareto Frontier)
  ↓
Phase 5 Baseline Comparison (DETERMINES_SUCCESS gate)
```

**Critical Path:** H-E1 → H-M-integrated → H-M-pareto  
**Gates:** 2 MUST_WORK (H-E1, H-M-integrated), 1 SHOULD_WORK (H-M-pareto)

**Execution Order:**
1. H-E1 (smoke test, all methods)
2. H-M-integrated (pipeline validation, correlation test)
3. H-M-pareto (Pareto construction, H1/H2/H3 tests)
4. Phase 5 (baseline comparison vs prior work)

---

## Scope & Boundaries

### What is Included:
- Single-forward-pass UQ methods (temp scaling, conformal prediction, MC dropout k≤10)
- TruthfulQA selective prediction task (817 human-annotated questions)
- Llama-3.1-8B-Instruct model (fixed architecture, no scaling study)
- AUROC metric for selective prediction quality
- FLOPs-based inference cost (normalized to 1.0× baseline)
- Cross-dataset generalization test (HaluEval calibration → TruthfulQA test)

### What is Excluded:
- Ensemble methods (>10× cost, outside 2-5× budget constraint from primary research question)
- Spectral normalization (Phase 1 Gap 1 - unstudied for LLMs, no implementation evidence)
- Model scale dependency study (Phase 1 Gap 2 - deferred to future work, would require ≥70B models)
- Multiple-choice TruthfulQA (MC1, MC2 tasks - focus on generative QA only)
- Token-level UQ methods (Phase 1 ROUTE_TO_0 failure - don't predict correctness at small scale)
- HaluEval as test set (used only for calibration, TruthfulQA is primary evaluation)

### Known Limitations:
- 8B model scale only - if Phase 0 baseline accuracy <45%, hypothesis NOT testable at this scale
- Single benchmark (TruthfulQA) - generalization to other truthfulness/factuality benchmarks unknown
- HaluEval calibration may not transfer to TruthfulQA (cross-dataset generalization is explicitly tested)
- n=3 random seeds - small sample size, high-variance results may require n=5 for confidence
- Low-star implementation repos (LofreeCP: 9 stars, dropwise: 8 stars) - must validate against paper specs

---

## Timeline & Resource Estimation

**Phase 2C (Experiment Design):** 3 hypothesis designs × 2-3 hours = 6-9 hours  
**Phase 3 (Implementation Planning):** 3 PRDs + architectures × 3-4 hours = 9-12 hours  
**Phase 4 (PoC Coding):** 3 smoke tests × 4-6 hours = 12-18 hours  
**Phase 5 (Baseline Comparison):** Full-scale experiment × 8-12 hours = 8-12 hours

**Total Estimated Effort:** 35-51 hours (PoC → Full validation)

**Critical Resource:** Llama-3.1-8B-Instruct inference (TruthfulQA 817 questions × 6 methods × 3 seeds = ~14,706 forward passes). Estimated GPU time: 2-4 hours on single A100.

---

## Archon Task Mapping

**Pipeline Project ID:** 6143a9ad-3963-4057-ae0b-bd81f48ecc87  
**Pipeline Project Title:** Anonymous Pipeline: Scalable UQ Methods for Foundation Models

**Hypothesis Task Mapping:**
- h-e1: `9ed7db3d-6175-42fb-83af-3e1f221c4c4d` (AUROC Threshold Validation)
- h-m-integrated: `d9b8e023-940f-4396-aefd-d21ad310a57e` (UQ Mechanism Pipeline)
- h-m-pareto: `8d86f5c2-de64-45a6-9c98-7839e33a5531` (Pareto Frontier Construction)

**Pipeline Phase Tasks:**
- Phase 2B: `02a77dfb-a6e5-4c97-9d11-34f22d88bba1` (status: done)
- Phase 2C: `0219770c-9911-4266-b427-2bc50245858c` (status: todo)
- Phase 3: `0079069e-b344-4363-b99a-85d379d8c155` (status: todo)
- Phase 4: `bfd5398f-1994-41b9-b61f-a8f22d90f906` (status: todo)

---

## Next Steps

1. **Phase 2C (Experiment Design):** Generate detailed experiment specifications for each hypothesis (H-E1, H-M-integrated, H-M-pareto)
2. **Phase 3 (Implementation Planning):** Create PRD, architecture, and task breakdown for each hypothesis
3. **Phase 4 (PoC Coding):** Implement smoke tests, validate MUST_WORK gates
4. **Phase 5 (Baseline Comparison):** Full-scale experiment vs Yang et al. 2023 baseline (DETERMINES_SUCCESS gate)

---

**Phase 2B Status:** COMPLETE  
**Generated Sub-Hypotheses:** 3  
**Archon Tasks Created:** 3  
**Ready for Phase 2C:** Yes
