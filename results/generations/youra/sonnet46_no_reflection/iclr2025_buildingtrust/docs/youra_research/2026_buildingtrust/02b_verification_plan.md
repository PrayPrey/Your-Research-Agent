---
stepsCompleted: ["step-00-init-environment", "step-01-init-parsing", "step-02-input-hypothesis", "step-03-hypothesis-generation", "step-04-hypothesis-inventory", "step-05-risk-analysis", "step-06-dependency-graph", "step-07-timeline-planning", "step-08-dialectical-analysis", "step-09-summary", "step-10-finalize"]
status: complete
completedAt: "2026-05-12T11:39:00"
hypothesis_id: H-ResidualInstability-v1
pipeline_project_id: a5a7bf00-63e5-4d9c-80b9-397f15d40dee
phase2b_task_id: 0c82ada5-1b42-4030-a387-0f2fa244fe1a
phase2c_task_id: 7ceb97d0-8598-4a3c-b565-3246f669cdf9
research_mode: incremental
causal_chain_count: 4
total_hypothesis_count: 5
generated_at: "2026-05-12"
---

# Verification Plan: Residual Instability as an Orthogonal Trust-Failure Predictor in LLMs

**Date:** 2026-05-12
**Hypothesis ID:** H-ResidualInstability-v1
**Confidence:** 0.72
**Total Hypotheses:** 5

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement
Under a diverse set of ≥30 LLMs spanning ≥3 families, ≥2 scales, and ≥2 training regimes, if adversarial robustness fragility (AdvGLUE accuracy drop) is residualized against a composite capability index (PC1 of MMLU/GSM8K/BBH/HellaSwag/WinoGrande) and mean model confidence to produce a Residual Instability score (RI), then RI will significantly predict calibration error (ECE), hallucination rate (HaluEval), and out-of-sample safety failure (HarmBench) — because adversarial fragility reflects a domain-general structural property of the model's decision surface that is orthogonal to capability and causes coupled failure across trust dimensions.

### 1.2 Alternative Hypothesis (H0)
There is no significant partial correlation between RI and trust failure metrics (ECE, HaluEval rate, HarmBench failure rate) after controlling for capability-PC1 and mean confidence; any observed correlation is fully explained by general capability.

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | TrustLLM + lm-evaluation-harness multi-benchmark matrix (standard) | Provides cross-dimension benchmark scores for a diverse model set covering robustness (AdvGLUE), calibration (ECE), hallucination (HaluEval), safety (HarmBench), truthfulness (TruthfulQA), and fairness (WinoBias/BBQ) — exactly the dimensions needed for RI computation and prediction testing |
| **Model** | ≥30 LLMs spanning LLaMA-series, Mistral-series, GPT-series (or equivalent) | Provides diversity across families, scales (7B–175B+), and training regimes (pretrained, RLHF, instruction-tuned) required for LOFO-CV and within-cell analyses |

**Dataset Details:**
- Source: TrustLLM (HowieHwong/TrustLLM, 622 stars); EleutherAI/lm-evaluation-harness (12505 stars); RUCAIBox/HaluEval (569 stars); centerforaisafety/HarmBench
- Path: Scores available via TrustLLM toolkit for 16 models; additional open-source models via lm-evaluation-harness

**Model Details:**
- Type: Autoregressive transformer LLMs
- Source: TrustLLM 16 models + additional open-source from lm-evaluation-harness public results; GPT-series via OpenAI API

### 1.4 Baseline Methods (for comparison)

| Method | Performance | Dataset |
|--------|-------------|---------|
| DecodingTrust (8-dimension trustworthiness) | GPT-4 more vulnerable to jailbreaking despite higher standard benchmark scores | GPT-3.5, GPT-4 on proprietary tasks |
| TrustLLM toolkit (ICML 2024) | 16 LLMs benchmarked across 8 dimensions with independent scores | 16 frontier LLMs |
| Cross-benchmark capability correlation (ctlllll) | 0.94 Spearman correlation with human Elo using 2 LASSO-selected benchmarks | Standard capability benchmarks |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | The TrustLLM/lm-evaluation-harness model set (≥30 models spanning ≥3 families) is sufficiently diverse to detect cross-family correlations | TrustLLM benchmarks 16 LLMs; lm-evaluation-harness supports 40+ additional open-source models; combined provides adequate family and scale coverage | Correlations may reflect family-specific lineage artifacts rather than structural instability; LOFO-CV would detect this (negative ΔR² in cross-family folds) |
| A2 | Benchmark contamination does not systematically bias AdvGLUE scores in a way that inflates or reverses correlations with ECE/HaluEval | AdvGLUE uses algorithmically generated adversarial examples (14 attack methods), reducing verbatim memorization risk vs. static QA benchmarks; contamination sensitivity analysis stratified by benchmark release date | Inflated correlations for highly contaminated models (e.g., GPT-4); detected by comparing correlation strength across contamination-risk strata |
| A3 | Capability-PC1 (MMLU/GSM8K/BBH/HellaSwag/WinoGrande) adequately captures general model capability as a confounder | Prior work shows 5-6 standard benchmarks explain 97.4% of capability variance via PCA; PC1 used in literature as capability proxy | Residual confounding from pretraining data volume or architecture type; addressed by supplementary log(param_count) control and interaction testing |
| A4 | The residual instability (RI) operationalization (OLS residual of AdvGLUE_drop on PC1 + mean_confidence) linearly separates instability from capability | OLS is standard; split-sample Fisher z-test for interactions (high vs. low PC1 halves) checks linearity assumption | RI may wash out nonlinear instability effects; addressed by testing interaction terms and reporting nonlinear model fits |
| A5 | LOFO-CV with 3 family folds provides sufficient statistical power to detect ΔR² ≥ 0.1 in forward prediction | With ≥30 models and ≥10 per training-regime cell, each fold has ≥10 test models; power analysis at ρ=0.4 with n=10 gives ~0.61 power — reported as exploratory | Forward prediction results may be underpowered; framed as exploratory with bootstrap CIs; would not support strong construct claim but descriptive correlation paper remains publishable |

### 1.6 Research Gap & Novelty

**Scope Reduction (75%):** 6 of 8 claims are established BUILD_ON facts; only 2 PROVE_NEW claims require experimental validation:
1. No systematic cross-dimension predictive correlation study exists for robustness → failure modes
2. Adversarial robustness fragility (RI) is an orthogonal axis beyond capability

**Key Innovation:** Residual Instability (RI) — a capability-controlled operationalization of adversarial fragility that predicts hallucination, calibration error, and safety failure out-of-sample via LOFO-CV; validated cross-domain via GSM8K OVI mechanistic probe.

**Differentiation from Prior Work:**
- DecodingTrust evaluates 8 trust dimensions **independently** (no inter-dimension predictive correlations, no capability residualization)
- TrustLLM reports dimension scores **independently** (no RI construct, no forward prediction)
- ctlllll targets **general capability** benchmarks, not robustness-to-failure-mode prediction

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| H-E1 | EXISTENCE | MUST_WORK | None | READY |
| H-M1 | MECHANISM | MUST_WORK | H-E1 | NOT_STARTED |
| H-M2 | MECHANISM | SHOULD_WORK | H-M1 | NOT_STARTED |
| H-M3 | MECHANISM | SHOULD_WORK | H-M2 | NOT_STARTED |
| H-M4 | MECHANISM | SHOULD_WORK | H-M3 | NOT_STARTED |

---

### 2.2 Hypothesis Specifications

---
**H-E1: Adversarial Robustness Fragility is Measurable and Variance-Sufficient**

**Statement**: Under a diverse set of ≥30 LLMs spanning ≥3 families, ≥2 scales, and ≥2 training regimes, if AdvGLUE accuracy drop is computed across the model set, then the distribution of AdvGLUE drops will show sufficient variance (SD > 5%) and the Residual Instability (RI) score (OLS residual of AdvGLUE_drop on PC1 + mean_confidence) will be computable with non-trivial residual variance (R²_residualization < 0.8), because adversarial fragility is a distinct property not reducible to capability.

**Rationale**: This is the foundational existence test — before claiming RI predicts anything, we must verify RI can be measured with sufficient spread across our model set. If all models show similar adversarial fragility after capability control, the RI construct collapses. Phase 2B readiness (SH1) explicitly flags this as the first gate.

**Variables** (from Phase 2A):
- Independent: AdvGLUE accuracy drop (raw); Capability-PC1; Mean model confidence
- Dependent: Residual Instability (RI) = OLS residual of AdvGLUE_drop ~ PC1 + mean_confidence
- Controlled: Model family (as covariate), Log parameter count (supplementary)

**Verification Protocol** (3-5 steps):
1. Collect AdvGLUE accuracy drop, MMLU/GSM8K/BBH/HellaSwag/WinoGrande scores, and mean_confidence for ≥30 diverse LLMs via TrustLLM toolkit + lm-evaluation-harness.
2. Compute capability-PC1 via PCA on [MMLU, GSM8K, BBH, HellaSwag, WinoGrande]; verify PC1 explains ≥70% of variance.
3. Fit OLS: AdvGLUE_drop ~ PC1 + mean_confidence; compute R²_residualization and extract RI residuals.
4. Check SD(AdvGLUE_drop) > 5% across model set and R²_residualization < 0.8; report distribution statistics.
5. Visualize RI distribution by family and training regime; confirm non-trivial spread.

**Success Criteria** (PoC: Direction-based):
- Primary: SD(AdvGLUE_drop) > 5% AND R²_residualization < 0.8 (RI is measurable and non-degenerate)
- Secondary: RI distribution shows spread across both pretrained and RLHF model subsets

**Failure Response**:
- IF fails: PIVOT — investigate whether AdvGLUE scores are available for sufficient model count; consider alternative adversarial benchmarks (ANLI)

**Dependencies**: None (foundation)

**Source**: Phase 2A Section 5 (SH1 — Phase 2B readiness)

---

---
**H-M1: Residual Instability Predicts Calibration Error (ECE)**

**Statement**: Under the ≥30 LLM model set with computed RI scores, if Spearman partial correlation ρ(RI, ECE | PC1, mean_confidence) is computed, then ρ ≥ 0.4 with Holm-corrected p < 0.05 and consistent positive sign across ≥2 of 3 family subgroups, because sharp decision boundaries cause overconfident predictions in brittle regions, producing calibration error.

**Rationale**: This is the primary mechanism test and the most critical MUST_WORK gate. The causal story hinges on RI → ECE being the first downstream coupling: models fragile under adversarial perturbation overcommit confidence to brittle predictions. Failure here invalidates the entire RI construct.

**Variables**:
- Independent: Residual Instability (RI)
- Dependent: Expected Calibration Error (ECE) via p-lambda/verified_calibration
- Controlled: Capability-PC1, Mean model confidence, Model family (LOFO-CV and within-family partials)

**Verification Protocol**:
1. Compute ECE for all models via p-lambda/verified_calibration library on QA benchmarks; collect bootstrap CIs (10,000 resamples).
2. Compute Spearman partial correlation ρ(RI, ECE | PC1, mean_confidence) with Holm-Bonferroni correction across full model set.
3. Run split-sample Fisher z-test: divide by median PC1; compute ρ_high and ρ_low; test for significant interaction.
4. Compute within-family partial correlations for LLaMA, Mistral, and GPT subsets separately.
5. Report VIF < 5 for multicollinearity check; Cook's distance for outlier sensitivity.

**Success Criteria**:
- Primary: Partial ρ(RI, ECE) ≥ 0.4, Holm-corrected p < 0.05
- Secondary: Consistent positive sign in ≥2 of 3 family subgroups; no significant PC1 interaction that eliminates main effect

**Failure Response**:
- IF fails (ρ < 0.2 or sign reversal in >1 family): ABANDON construct claim; pivot to descriptive correlation paper without RI as predictive construct

**Dependencies**: H-E1

**Source**: Phase 2A Section 1.3 Causal Step 2; Section 1.6 Prediction P1

---

---
**H-M2: Residual Instability Predicts Hallucination Rate (HaluEval)**

**Statement**: Under the ≥30 LLM model set, if Spearman partial correlation ρ(RI, HaluEval_rate | PC1, mean_confidence) is computed, then ρ ≥ 0.4 with Holm-corrected p < 0.05 and within-family ρ ≥ 0.2 in ≥2 of 3 families, because the same sharp-boundary instability causes hallucination under distribution shift — the model overcommits to plausible-sounding but incorrect responses when inputs move away from training distribution.

**Rationale**: This extends the RI→ECE coupling to hallucination, confirming that calibration failure and hallucination share the same structural root (instability), not separate mechanisms. If RI predicts ECE but not HaluEval, the two failure modes are independent and the RI construct loses generality.

**Variables**:
- Independent: Residual Instability (RI)
- Dependent: Hallucination rate (fraction of hallucinated responses on HaluEval QA/dialogue/summarization)
- Controlled: Capability-PC1, Mean model confidence, Model family

**Verification Protocol**:
1. Collect hallucination rates via RUCAIBox/HaluEval evaluation scripts for the full model set.
2. Compute Spearman partial correlation ρ(RI, HaluEval_rate | PC1, mean_confidence) with Holm correction.
3. Compute within-family partial correlations (LLaMA, Mistral, GPT subsets).
4. Check whether RI predicts HaluEval independently of ECE (partial correlation controlling for ECE as additional covariate, reported as supplementary).
5. Report bootstrap CIs and Cook's distance outlier sensitivity.

**Success Criteria**:
- Primary: Partial ρ(RI, HaluEval_rate) ≥ 0.4, Holm p < 0.05
- Secondary: Within-family ρ ≥ 0.2 in ≥2 of 3 families

**Failure Response**:
- IF fails (ρ < 0.2 universally): EXPLORE — document that calibration and hallucination are independent failure modes not linked by shared instability; report as descriptive finding

**Dependencies**: H-M1

**Source**: Phase 2A Section 1.3 Causal Step 3; Section 1.6 Prediction P2

---

---
**H-M3: Residual Instability Adds Out-of-Sample Predictive Power for Safety Failure (HarmBench)**

**Statement**: Under LOFO-CV with 3 family folds, if regression [RI + PC1] vs. [PC1 only] is used to predict HarmBench safety failure rate, then ΔR² ≥ 0.1 in ≥2 of 3 LOFO folds with consistent positive direction and permutation test p < 0.05, because domain-general instability extends to safety failure: high-RI models misclassify safety-relevant inputs under style perturbations, just as they fail under adversarial text perturbations.

**Rationale**: The forward prediction requirement (held-out family fold) tests transportability of RI — whether instability measured on one family predicts safety failure in a different family. This distinguishes the RI construct from a spurious correlation within the training sample. It is the strongest predictive claim and the most policy-relevant result.

**Variables**:
- Independent: Residual Instability (RI) + Capability-PC1 (augmented model)
- Dependent: HarmBench safety failure rate (attack success rate / refusal failure rate)
- Controlled: Model family (via LOFO-CV folds)

**Verification Protocol**:
1. Collect HarmBench safety failure rates for all models via centerforaisafety/HarmBench.
2. Implement LOFO-CV: train [RI+PC1]→HarmBench on 2 families, test on 3rd; rotate 3 folds.
3. Compute ΔR² per fold ([RI+PC1] model vs. [PC1 only] baseline); test for consistent positive direction.
4. Run permutation test (n=1000 permutations of RI labels) to establish p < 0.05.
5. Report ΔR² per fold with bootstrap CIs; explicitly flag any fold with negative ΔR².

**Success Criteria**:
- Primary: ΔR² ≥ 0.1 in ≥2 of 3 LOFO folds; consistent positive direction across all folds
- Secondary: Permutation p < 0.05

**Failure Response**:
- IF fails (ΔR² < 0.1 in ≥2 folds or negative ΔR²): EXPLORE — document limited cross-family transportability; construct claim narrowed to within-family associations

**Dependencies**: H-M2

**Source**: Phase 2A Section 1.3 Causal Step 3 (safety mechanism); Section 1.6 Prediction P3

---

---
**H-M4: Residual Instability Predicts Domain-General Output Variance (OVI on GSM8K)**

**Statement**: Under the open-source model subset (temperature sampling accessible), if Spearman correlation ρ(RI, OVI_GSM8K) is computed where OVI = normalized entropy over 20 sampled final answers at T=0.7, then ρ ≥ 0.4 with Holm-corrected p < 0.05, because domain-general instability extends beyond NLP tasks — high-RI models exhibit elevated output variance on GSM8K arithmetic reasoning, confirming the structural (not task-specific) nature of instability.

**Rationale**: This is the most novel and paradigm-shifting prediction. If RI (measured on adversarial NLP tasks) predicts output variance on arithmetic reasoning, instability is a structural property of the model's decision surface — not a task-specific linguistic artifact. This rules out the alternative explanation that RI merely captures sensitivity to lexical perturbations. Note: limited to open-source models (closed-API excludes temperature sampling).

**Variables**:
- Independent: Residual Instability (RI)
- Dependent: Output Variance Index (OVI) = normalized entropy over 20 GSM8K sampled final answers at T=0.7, top-p=1.0
- Controlled: Capability-PC1 (partial correlation), Model family

**Verification Protocol**:
1. For each open-source model, run GSM8K with 20 samples at T=0.7, top-p=1.0 via lm-evaluation-harness; extract final numeric answers.
2. Compute OVI = normalized entropy over the 20 sampled final answer distribution per model.
3. Compute Spearman correlation ρ(RI, OVI) with Holm correction; report for open-source subset only.
4. Run partial correlation ρ(RI, OVI | PC1) to confirm OVI is not just a capability proxy.
5. Report limitation: GPT-series excluded from OVI test; document as open-source-only finding.

**Success Criteria**:
- Primary: ρ(RI, OVI_GSM8K) ≥ 0.4, Holm p < 0.05 (open-source subset)
- Secondary: Partial ρ(RI, OVI | PC1) ≥ 0.3 — OVI is not fully explained by capability

**Failure Response**:
- IF fails (ρ < 0.2): EXPLORE — document instability signal as NLP-specific (not domain-general); adjust paper framing from "structural instability" to "adversarial NLP fragility"

**Dependencies**: H-M3

**Source**: Phase 2A Section 1.3 Causal Step 4; Section 1.6 Prediction P4; Discussion Exchange 16

---

---

## 3. Execution

### 3.1 Dependency Chain
```
H-E1 → H-M1 → H-M2 → H-M3 → H-M4
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | SD(AdvGLUE_drop) > 5% AND R²_resid < 0.8 | STOP — reassess dataset availability |
| H-M1 | MUST_WORK | Partial ρ(RI, ECE) ≥ 0.4, Holm p < 0.05 | ABANDON RI construct; pivot to descriptive |
| H-M2 | SHOULD_WORK | Partial ρ(RI, HaluEval) ≥ 0.4, Holm p < 0.05 | EXPLORE — document as independent failure modes |
| H-M3 | SHOULD_WORK | LOFO-CV ΔR² ≥ 0.1 in ≥2/3 folds, perm p < 0.05 | EXPLORE — narrow construct claim |
| H-M4 | SHOULD_WORK | ρ(RI, OVI) ≥ 0.4, Holm p < 0.05 (open-source) | EXPLORE — narrow to NLP-specific instability |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 1: Foundation | H-E1 | 2 weeks |
| Phase 2: Core Mechanisms | H-M1, H-M2, H-M3, H-M4 | 5 weeks (2+1+1+1) |

**Total Duration:** 7 weeks

---

## 4. Risk Analysis

### 4.1 Assumption-to-Risk Mapping

**Risk R1: Insufficient Model Diversity (from A1)**

**Source Assumption:** A1 — Model set lacks family/scale diversity

**Description:** If TrustLLM + lm-evaluation-harness cannot provide ≥30 models spanning ≥3 families with AdvGLUE scores available, LOFO-CV becomes underpowered and within-family correlations unreliable. Family-lineage artifacts may dominate signal.

**Affected Hypotheses:** H-E1, H-M1, H-M2, H-M3, H-M4 (all)

**Severity:** High

**Mitigation Strategy:**
1. **Prevention:** Pre-check model availability before data collection; identify all models with publicly available AdvGLUE scores via TrustLLM toolkit and lm-evaluation-harness leaderboard data.
2. **Detection:** If <30 models available, check whether diversity criteria (≥3 families, ≥2 scales) are still met with reduced N.
3. **Response:**
   - PIVOT: Include ANLI as additional adversarial robustness benchmark if AdvGLUE scores are unavailable for sufficient models.
   - SCOPE: If N < 30 but ≥20, report as pilot study with exploratory framing; pre-register power limitation.
   - ABORT: If < 3 families available, core LOFO-CV design collapses — fallback to within-family analysis only.

**Early Warning Indicators:**
- TrustLLM toolkit reports AdvGLUE for <20 models
- lm-evaluation-harness public results missing AdvGLUE for key model families

---

**Risk R2: Benchmark Contamination Confound (from A2)**

**Source Assumption:** A2 — Contamination inflates or reverses correlations

**Description:** Models trained on data that includes AdvGLUE test examples may show artificially low accuracy drops, biasing RI computation for those models. This could inflate or invert the RI→ECE/HaluEval correlation.

**Affected Hypotheses:** H-M1, H-M2, H-M3

**Severity:** Medium

**Mitigation Strategy:**
1. **Prevention:** Stratify models by benchmark release year (AdvGLUE 2021, TruthfulQA 2021 = high risk; HaluEval 2023, HarmBench 2024 = lower risk).
2. **Detection:** Compare correlation magnitude between low-contamination-risk and high-contamination-risk model strata; significant divergence signals contamination confound.
3. **Response:**
   - PIVOT: Report contamination stratification as sensitivity analysis in supplementary; if contamination strata show consistent results, claim holds.
   - SCOPE: Exclude GPT-series from primary analysis if contamination risk is high; report as open-source-only finding.

**Early Warning Indicators:**
- Correlation markedly stronger for post-2022 models vs. pre-2022 models
- GPT-4 is an outlier with unusually low RI despite known adversarial vulnerabilities

---

**Risk R3: Capability-PC1 Inadequate Confounder Control (from A3)**

**Source Assumption:** A3 — PC1 does not fully capture capability

**Description:** If capability-PC1 leaves residual confounding (e.g., from pretraining data volume or architecture-specific factors), RI may be capturing residual capability variance rather than a distinct instability dimension.

**Affected Hypotheses:** H-M1, H-M2, H-M3, H-M4

**Severity:** Medium

**Mitigation Strategy:**
1. **Prevention:** Report supplementary partial correlations controlling for log(param_count) instead of PC1; check sensitivity of RI to capability proxy choice.
2. **Detection:** If ρ(RI, ECE | PC1) >> ρ(RI, ECE | log_params), the PC1 choice is driving results — report as specification sensitivity.
3. **Response:**
   - PIVOT: Use both PC1 and log(param_count) as joint controls in sensitivity analysis.
   - SCOPE: Limit claim to "RI predicts ECE beyond PC1" rather than "RI is orthogonal to all capability dimensions."

**Early Warning Indicators:**
- VIF > 5 between RI and PC1 after residualization (suggests residualization was insufficient)
- RI correlation reverses when log(param_count) added as additional control

---

**Risk R4: OLS Linearity Assumption Violated for RI Computation (from A4)**

**Source Assumption:** A4 — Linear OLS residualization does not separate instability from capability

**Description:** The RI operationalization assumes a linear relationship between AdvGLUE_drop and (PC1 + mean_confidence). If the true relationship is nonlinear (e.g., instability spikes at a capability threshold), OLS residuals will systematically underestimate instability for high-capability models.

**Affected Hypotheses:** H-M1, H-M2, H-M3, H-M4

**Severity:** Medium

**Mitigation Strategy:**
1. **Prevention:** Run split-sample Fisher z-test dividing models at median PC1; test for significant ρ_high vs. ρ_low difference.
2. **Detection:** If ρ_high << ρ_low in split-sample, nonlinearity is present — test quadratic PC1 term.
3. **Response:**
   - PIVOT: Include PC1² as quadratic term in RI regression; report nonlinear-adjusted RI as sensitivity analysis.
   - SCOPE: Report both linear and nonlinear RI; if results are qualitatively similar, linear is reported as primary.

**Early Warning Indicators:**
- Split-sample Fisher z-test shows significant interaction (p < 0.05 for ρ_high vs. ρ_low difference)
- Residual plots show curvature in AdvGLUE_drop ~ PC1 regression

---

**Risk R5: LOFO-CV Statistical Power Insufficient (from A5)**

**Source Assumption:** A5 — Power ~0.61 per fold (n≈10) is exploratory

**Description:** With ≥30 models and 3 family folds, each test fold has ≈10 models. At ρ=0.4, power is ~0.61 — subgroup results are underpowered and may fail to reach ΔR² ≥ 0.1 threshold due to small-sample variability rather than true null effect.

**Affected Hypotheses:** H-M3 (primary), H-M1, H-M2 (within-family sub-analyses)

**Severity:** Medium

**Mitigation Strategy:**
1. **Prevention:** Pre-register H-M3 LOFO-CV as exploratory; report bootstrap CIs for ΔR² per fold.
2. **Detection:** If confidence intervals for ΔR² per fold are very wide (spanning zero), power limitation is the likely explanation.
3. **Response:**
   - SCOPE: Report LOFO-CV ΔR² as exploratory evidence, not confirmatory; emphasize consistent direction over magnitude threshold.
   - ABORT: If ΔR² is negative in ≥2 folds, interpret as evidence against cross-family transportability (not just underpowered).

**Early Warning Indicators:**
- Bootstrap CI for ΔR² in any fold spans zero
- ΔR² < 0.05 in all folds (too small to be practically meaningful even if positive)

---

### 4.2 Risk-Hypothesis Mapping

| Risk | Source | Affected Hypotheses | Severity |
|------|--------|---------------------|----------|
| R1: Insufficient model diversity | A1 | H-E1, H-M1, H-M2, H-M3, H-M4 | High |
| R2: Benchmark contamination | A2 | H-M1, H-M2, H-M3 | Medium |
| R3: PC1 inadequate confounder | A3 | H-M1, H-M2, H-M3, H-M4 | Medium |
| R4: OLS linearity violated | A4 | H-M1, H-M2, H-M3, H-M4 | Medium |
| R5: LOFO-CV underpowered | A5 | H-M3 (primary) | Medium |

**Critical Risks:** 0  
**High Risks:** 1 (R1)  
**Medium Risks:** 4 (R2, R3, R4, R5)  
**Low Risks:** 0

### 4.3 Baseline Failure Patterns → Risks

| Baseline Limitation | Potential Risk | Mitigation |
|---------------------|----------------|------------|
| DecodingTrust evaluates dimensions independently | Cannot validate that RI bridges dimensions | RI partial correlation design directly addresses this gap |
| TrustLLM model set limited to 16 frontier models | Insufficient N for LOFO-CV | Augment with lm-evaluation-harness open-source models to reach ≥30 |
| ctlllll focuses on capability, not trust | PC1 may not adequately separate capability from instability | Supplementary log(param_count) control + split-sample interaction test |

---

## 5. Dependency Graph & Timeline

### 5.1 Dependency Graph (DAG)

```
═══════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) - 5 Hypotheses
═══════════════════════════════════════════════════════════

[Level 0 - Root / Foundation]
    H-E1: Adversarial Robustness Fragility Measurable
         │  Gate 1: MUST_WORK (SD>5%, R²<0.8)
         ▼
[Level 1 - Primary Mechanism]
    H-M1: RI → ECE (Calibration Error)
         │  Gate 2: MUST_WORK (ρ≥0.4, Holm p<0.05)
         ▼
[Level 2 - Secondary Mechanism]
    H-M2: RI → HaluEval (Hallucination Rate)
         │  Gate: SHOULD_WORK (ρ≥0.4)
         ▼
[Level 3 - Forward Prediction]
    H-M3: RI → HarmBench OOS (LOFO-CV)
         │  Gate: SHOULD_WORK (ΔR²≥0.1 in ≥2/3 folds)
         ▼
[Level 4 - Domain Generality]
    H-M4: RI → OVI/GSM8K (Cross-Domain Instability)
         │  Gate: SHOULD_WORK (ρ≥0.4, open-source only)
         ▼
    [COMPLETE]

═══════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M2 → H-M3 → H-M4
MUST_WORK gates: H-E1, H-M1 (failure stops pipeline)
SHOULD_WORK gates: H-M2, H-M3, H-M4 (failure narrows scope)
═══════════════════════════════════════════════════════════
```

### 5.2 Dependency Hierarchy

| Level | Hypothesis | Prerequisites | Gate Type |
|-------|-----------|---------------|-----------|
| 0 | H-E1 | None | MUST_WORK |
| 1 | H-M1 | H-E1 | MUST_WORK |
| 2 | H-M2 | H-M1 | SHOULD_WORK |
| 3 | H-M3 | H-M2 | SHOULD_WORK |
| 4 | H-M4 | H-M3 | SHOULD_WORK |

### 5.3 Gantt Timeline

```
═══════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE - 5 Hypotheses
═══════════════════════════════════════════════════════════════════
Phase/Hypothesis  │ W1-2    │ W3-4    │ W5      │ W6      │ W7
──────────────────┼─────────┼─────────┼─────────┼─────────┼─────
PHASE 1: Foundation
  H-E1            │ ████████│         │         │         │
  [Gate 1]        │       ◆ │         │         │         │
──────────────────┼─────────┼─────────┼─────────┼─────────┼─────
PHASE 2: Mechanisms
  H-M1            │         │ ████████│         │         │
  [Gate 2]        │         │       ◆ │         │         │
  H-M2            │         │         │ ████    │         │
  H-M3            │         │         │         │ ████    │
  H-M4            │         │         │         │         │ ████
──────────────────┼─────────┼─────────┼─────────┼─────────┼─────
═══════════════════════════════════════════════════════════════════
Legend: ████ = Active work | ◆ = Gate decision point
Total Duration: 7 weeks
═══════════════════════════════════════════════════════════════════
```

### 5.4 Critical Path Analysis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  CRITICAL PATH ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Critical Path: H-E1 → H-M1 → H-M2 → H-M3 → H-M4

Total Duration: 7 weeks
  Formula: 2 (H-E1) + 2 (H-M1) + 1 (H-M2) + 1 (H-M3) + 1 (H-M4)

Slack Available: 0 weeks (all sequential)

MUST_WORK bottlenecks:
  - H-E1 failure → entire pipeline halts
  - H-M1 failure → RI construct abandoned, pipeline halts
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 5.5 Resource Summary

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  RESOURCE SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Total Hypotheses: 5
- Existence: 1 (H-E1)
- Mechanism: 4 (H-M1 to H-M4)
- Condition: 0 (none required)

Verification Phases: 2
1. Foundation (H-E1): 2 weeks
2. Mechanisms (H-M1 to H-M4): 5 weeks

Total Duration: 7 weeks
Critical Path Length: 7 weeks
Execution Mode: Sequential chain
Datasets: TrustLLM, lm-evaluation-harness, HaluEval, HarmBench, GSM8K (temp sampling)
Statistical tools: scipy/pingouin (Spearman partial correlation), sklearn (OLS, PCA),
                   verified_calibration (ECE), custom LOFO-CV
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 6. Dialectical Analysis

### 6.1 Thesis

**Core Claim:** Adversarial robustness fragility (AdvGLUE accuracy drop), after residualizing against capability-PC1 and mean confidence, constitutes a distinct Residual Instability (RI) dimension that significantly predicts calibration error (ECE), hallucination rate (HaluEval), and out-of-sample safety failure (HarmBench) across ≥30 diverse LLMs.

**Supporting Evidence:**
1. **Causal mechanism grounded in prior work:** Sharp/anisotropic decision boundaries → overconfident brittle predictions (ECE) → hallucination under distribution shift (HaluEval) → safety failure under style perturbations (HarmBench). Each link is supported by Wang et al. 2021, Li et al. 2023, and Eiras et al. 2025.
2. **Methodological rigor:** Capability-PC1 residualization directly addresses the inverse scaling confound identified by Lin et al. 2021 (TruthfulQA). LOFO-CV tests cross-family transportability.
3. **Cross-domain validation via OVI:** If RI predicts GSM8K arithmetic output variance (OVI), instability is structural — not a task-specific NLP artifact — providing the strongest evidence for the orthogonal-axis claim.

**Strengths:**
- Uses only existing benchmarks (fully constraint-compliant)
- Pre-registered falsification criteria with explicit withdrawal thresholds
- Two-stage design separates descriptive correlations from structural proof
- LOFO-CV tests cross-family generalization beyond training sample

**Expected Outcomes:**
- Primary (P1): Partial ρ(RI, ECE | PC1, mean_conf) ≥ 0.4, Holm p < 0.05
- Secondary (P2): Partial ρ(RI, HaluEval) ≥ 0.4, within-family ρ ≥ 0.2 in ≥2 families
- Tertiary (P4): ρ(RI, OVI_GSM8K) ≥ 0.4 for open-source subset

### 6.2 Antithesis

**Null Hypothesis (H0):** There is no significant partial correlation between RI and trust failure metrics (ECE, HaluEval rate, HarmBench failure rate) after controlling for capability-PC1 and mean confidence; any observed raw correlation between AdvGLUE drop and trust failures is fully explained by general capability.

**Counter-Arguments:**
1. **Capability mediation:** All trust failures (calibration error, hallucination, safety failure) may be driven by general capability differences that PC1 incompletely captures. Residual in RI may be measurement noise, not a structural instability dimension. DecodingTrust found GPT-4 (higher capability) more vulnerable to jailbreaking — suggesting the capability–trust relationship is non-monotone and complex.
2. **Contamination artifacts:** AdvGLUE (2021) and TruthfulQA (2021) are old benchmarks with high contamination risk for models trained after 2022. If contamination inflates adversarial accuracy for some models, RI would be biased by training data composition, not model structure.
3. **LOFO-CV underpowering:** With n≈10 per family fold, ΔR² threshold of 0.1 may not be achievable due to sampling variance — failure to reach threshold does not distinguish true null from insufficient power.

**Potential Failure Points:**
- R1 (model diversity): If <3 families with full benchmark coverage available, LOFO-CV design is invalid
- R2 (contamination): If GPT-series RI is contamination-biased, primary P1/P2 results may be driven by a few outlier models
- R4 (linearity): If instability is nonlinear in capability (threshold effects at scale), OLS residualization produces systematically wrong RI scores

**Conditions Under Which H0 Would Be Supported:**
- Partial ρ(RI, ECE) < 0.2 across multiple PC1 control specifications
- Sign reversal in >1 family subgroup for RI→ECE
- LOFO-CV ΔR² negative in ≥2 folds
- Within-family ρ < 0.2 universally (lineage explains all variance)

### 6.3 Synthesis

**Balanced Assessment:**

H-ResidualInstability-v1 presents a testable claim that adversarial fragility residualized against capability constitutes a distinct predictive dimension for trust failures. However, H0 raises valid concerns that general capability (incompletely captured by PC1) and benchmark contamination could explain observed correlations.

**Resolution Path:**

The verification plan addresses this dialectic through:
1. **Foundation verification (H-E1):** Establishes RI measurability before any predictive claim — if RI degenerates (R² ≥ 0.8), the construct itself fails before prediction testing.
2. **Sequential mechanism testing (H-M1→H-M4):** Tests the causal chain step-by-step; each step can fail independently, enabling partial-support outcomes that distinguish the thesis from pure H0.
3. **Gate conditions:** MUST_WORK on H-E1 and H-M1 allows early detection of H0 support; SHOULD_WORK on H-M2–H-M4 allows nuanced partial-support outcomes.
4. **Sensitivity analyses:** Contamination stratification, supplementary log(param_count) control, and split-sample Fisher z-test directly test the three primary antithesis arguments.

**Conditions for Thesis Support:**
- H-E1 and H-M1 both pass MUST_WORK gates (necessary minimum)
- At least one of P2/P3 supports (RI has general cross-dimension predictive value, not just ECE)
- OVI cross-domain result positive (strongest evidence for structural orthogonality)

**Conditions for Antithesis Support:**
- H-E1 fails (RI is degenerate — not a distinct measurable dimension)
- H-M1 fails (RI does not predict ECE after capability control — null is supported)
- LOFO-CV negative ΔR² in ≥2 folds (cross-family transportability absent)

**Nuanced Outcome Possibilities:**
1. **Full Support:** H-E1 + H-M1 + H-M2 + H-M3 all pass → Strong thesis validated; paper submitted with RI as structural instability construct
2. **Partial Support:** H-E1 + H-M1 pass; H-M2 or H-M3 fails → Refined thesis: RI predicts calibration but not broader trust failure spectrum; narrowed contribution
3. **Minimal Support:** H-E1 + H-M1 pass; H-M2–H-M4 all fail → RI is a calibration-specific construct, not domain-general; descriptive cross-benchmark paper
4. **No Support:** H-E1 or H-M1 fail → H0 supported; RI cannot be distinguished from residual capability; pipeline terminates

### 6.4 Robustness Assessment

| Aspect | Thesis Position | Antithesis Challenge | Resolution |
|--------|-----------------|----------------------|------------|
| Existence | RI measurable with SD > 5% variance | Could be noise/measurement error | H-E1 R²_residualization < 0.8 test |
| Primary mechanism | RI → ECE via boundary overconfidence | Capability residual confound | H-M1 partial ρ + split-sample interaction test |
| Secondary mechanism | RI → HaluEval (same structural root) | ECE and hallucination are independent | H-M2 checks cross-DV consistency |
| Forward prediction | RI transports across model families | Only within-family correlations | H-M3 LOFO-CV tests cross-family generalization |
| Domain generality | RI → OVI on GSM8K (structural) | NLP-specific lexical artifact | H-M4 cross-domain OVI probe |
| Contamination robustness | Stratification handles bias | Contamination irresolvable | Sensitivity analysis in supplementary |

**Overall Robustness Score:** Medium-High (strong design with acknowledged power limitations in subgroup analyses)

**Confidence in Verification Plan:** 0.72

---

## 7. Executive Summary & Conclusions

### 7.1 Executive Summary

**Main Hypothesis:** Residual Instability (RI = capability-controlled adversarial fragility) predicts multi-dimensional trust failures in LLMs
- ID: H-ResidualInstability-v1, Confidence: 0.72

**Verification Structure:**
- Mode: Incremental (75% scope reduction from Phase 2A established facts)
- Sub-Hypotheses: 5 total — H-E1 (existence) + H-M1–H-M4 (mechanism chain)
- Phases: 2 phases over 7 weeks
- Critical Gates: 2 MUST_WORK gates (H-E1, H-M1) + 3 SHOULD_WORK gates

**Risk Assessment:** Medium
- Primary concerns: Model diversity (R1, High) and benchmark contamination (R2, Medium)

**Immediate Action:** Begin Phase 1 with H-E1 — collect benchmark matrix for ≥30 diverse LLMs

### 7.2 Conclusions

**Key Achievements:**
- 5 sub-hypotheses defined across 2 phases with clear success/failure criteria
- H0 addressed: RI is null against capability-PC1 + mean_confidence control
- Established Facts (75% of claims) properly scoped out — only 2 PROVE_NEW claims validated

**Verification Execution Order:**

**Phase 1: Foundation** (2 weeks)
- H-E1: SD(AdvGLUE_drop) > 5%; R²_residualization < 0.8; RI computable for ≥30 models
- Gate 1: MUST PASS — if fails, entire pipeline halts

**Phase 2: Core Mechanisms** (5 weeks)
- H-M1 (W3-4): Partial ρ(RI, ECE | PC1, conf) ≥ 0.4 — primary MUST_WORK gate
- H-M2 (W5): Partial ρ(RI, HaluEval | PC1, conf) ≥ 0.4 — SHOULD_WORK
- H-M3 (W6): LOFO-CV ΔR²(RI+PC1 vs PC1) ≥ 0.1 in ≥2/3 folds — SHOULD_WORK
- H-M4 (W7): ρ(RI, OVI_GSM8K) ≥ 0.4 (open-source only) — SHOULD_WORK

**Critical Decision Points:**

1. **Gate 1 (Foundation — H-E1):** RI must be measurable
   - FAIL → STOP pipeline; investigate data availability; consider ANLI as alternative adversarial benchmark
   - PASS → Proceed to Phase 2

2. **Gate 2 (Primary Mechanism — H-M1):** RI must predict ECE
   - FAIL (ρ < 0.2) → ABANDON RI construct claim; pivot to descriptive cross-benchmark correlation paper
   - PARTIAL (0.2 ≤ ρ < 0.4) → Continue cautiously; narrow claim to "weak association"
   - PASS → Proceed to H-M2–H-M4 for construct breadth

**Open Questions (from Phase 2A):**
- Does RI survive within-family partial correlation (ρ ≥ 0.2 in ≥2 families), or is it fully explained by lineage?
- Does the AdvGLUE × PC1 interaction term eliminate the RI main effect under high-capability conditions?
- Is OVI (GSM8K variance) accessible for the closed-API model subset, or only open-source?
- How should contamination strata (low/medium/high risk) be operationalized for sensitivity analysis?

**Recommendations:**

1. **Immediate Actions:**
   - Begin benchmark data collection: TrustLLM + lm-evaluation-harness + HaluEval + HarmBench
   - Pre-register protocol on OSF before data collection (falsification criteria pre-committed)

2. **Resource Allocation:**
   - Allocate 7 weeks for critical path (no slack — all sequential)
   - Reserve 1-2 weeks buffer for data collection challenges (model availability, API limits)

3. **Failure Management:**
   - Document all gate results (pass/partial/fail) in verification_state.yaml
   - Execute PIVOT strategies per risk mitigation plan
   - Frame H-M3 and H-M4 results as exploratory (pre-register power limitation)

### 7.3 Appendices

**Appendix A: Phase 2A Reference**
- Source: docs/youra_research/20260512_buildingtrust/03_refinement.yaml
- Hypothesis ID: H-ResidualInstability-v1
- Phase 2A convergence: Exchange 16 (all 6 criteria met)
- Discussion agents: Dr. Nova (novelty), Prof. Vera (falsifiability), Dr. Sage (significance), Prof. Pax (plausibility), Dr. Ally (advocate), Prof. Rex (critic)

**Appendix B: MCP Tool Usage Summary**
- Total MCP calls: 4 (ClearThought scientificmethod × 2, structuredargumentation × 1, collaborativereasoning × 1 implicit via synthesis)
- Tools used: mcp__clearThought__scientificmethod (H-E1 + H-M chain), mcp__clearThought__structuredargumentation (dialectical analysis)
- Archon: Pipeline project verified; Phase 2B task updated to doing

---

*Generated by YouRA Phase 2B (v6.0) | 2026-05-12*
