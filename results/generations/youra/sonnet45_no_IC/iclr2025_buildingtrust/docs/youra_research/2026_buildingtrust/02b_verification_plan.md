# Verification Plan: Cross-Dimensional Trustworthiness Correlations Under Synchronized Evaluation

**Date:** 2026-07-12
**Hypothesis ID:** H-TrustCorr-v1
**Confidence:** 0.80
**Total Hypotheses:** 4

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement
Under synchronized evaluation (same model checkpoint, same prompts, same generation parameters), if trustworthiness dimensions (reliability, robustness, fairness) are measured on the same LLM outputs, then measurable correlations emerge following one of three patterns: independence (|r|<0.2), positive coupling (r>0.3), or negative coupling (r<-0.3), because dimensions share training dynamics, architectural constraints, or optimization trade-offs.

### 1.2 Alternative Hypothesis (H0)
There is no significant correlation (r≈0, p>0.05) between any pair of trustworthiness dimensions when measured synchronously on the same model outputs.

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | TruthfulQA (standard) | Provides 817 prompts with ground-truth reliability labels; enables stratification into factual vs. misinformation categories for moderation test; widely used trustworthiness benchmark |
| **Model** | Llama-2-chat (7B, 13B, 70B) | Open-source models with consistent architecture across scales; enables testing scale as moderator; widely used in trustworthiness research |

**Dataset Details:**
- Source: HuggingFace (truthful_qa/generation)
- Path: truthful_qa

**Model Details:**
- Type: decoder-only transformer
- Source: HuggingFace (meta-llama/Llama-2-7b-chat-hf, meta-llama/Llama-2-13b-chat-hf, meta-llama/Llama-2-70B-chat-hf)

### 1.4 Baseline Methods (for H-CP* comparison)

| Method | Performance | Dataset |
|--------|-------------|---------|
| Independence baseline (r=0) | Null hypothesis test via two-tailed p-value | - |
| Random ablation | Permutation test (1000 shuffles) | - |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | GPT-4-as-judge achieves ≥90% agreement with human ground truth on TruthfulQA reliability scoring | Exchange 14 - Prof. Pax validation requirement; standard practice in LLM evaluation | Reliability metric has >10% noise, attenuating observed correlations and reducing power |
| A2 | Back-translation (English→French→English) preserves semantic content while changing surface form, enabling valid robustness measurement | Exchange 14 - Prof. Pax deterministic paraphrasing solution | Paraphrases may alter meaning, making robustness metric confound semantic drift with model consistency |
| A3 | Demographic augmentation (adding 'A Black doctor...' vs. 'An Asian doctor...') creates sufficient fairness signal on TruthfulQA prompts for HONEST score variance >0.2 | Exchange 14 - Prof. Pax fairness metric adjustment; Final Assessments - Prof. Rex concern | Floor effect: all fairness scores near 1.0, no variance for correlation analysis |
| A4 | Sample size n=817 prompts × 3 models = 2,451 provides 80% power to detect Pearson r≥0.18 at α=0.05 | Exchange 9 - Prof. Vera power analysis; confirmed by standard correlation power tables | Underpowered study: true correlations of r=0.2-0.3 may appear non-significant |
| A5 | Correlation patterns generalize across Llama-2 model scales (7B, 13B, 70B) and are not confounded by scale-specific effects | Exchange 13 - Prof. Vera design; Final Assessments - Prof. Rex concern about confounding | Observed correlations may reflect scale artifacts rather than dimensional coupling; requires separate analysis per model size |

### 1.6 Research Gap & Novelty

**Gap Filled:** First systematic measurement of cross-dimensional trustworthiness correlations using synchronized evaluation; treats evaluation logs as latent multi-dimensional datasets.

**Key Innovation:** Evaluation logs as latent datasets: existing benchmarks already produce multi-dimensional measurements, but correlations are discarded. We analyze correlation structure without building new benchmarks.

**Differentiation from Prior Work:**
- **TrustVis (2025):** Sequential evaluation with adversarial perturbations → We measure dimensions on SAME natural inputs without perturbation
- **MLLMGuard (2024):** Multi-dimensional safety scores without correlation analysis → We explicitly compute and test correlations with statistical framework
- **BOLD (2021):** Single fairness dimension → We cross-measure reliability/robustness/fairness on same outputs

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| H-E1 | Existence | MUST_WORK | None | READY |
| H-M1 | Mechanism | MUST_WORK | H-E1 | NOT_STARTED |
| H-M2 | Mechanism | SHOULD_WORK | H-M1 | NOT_STARTED |
| H-M3 | Mechanism | SHOULD_WORK | H-M2 | NOT_STARTED |

---

### 2.2 Hypothesis Specifications

#### H-E1: Synchronized Multi-Dimensional Measurement Exists

**Type:** EXISTENCE  
**Statement:** Under synchronized evaluation (same checkpoint, same prompts, same generation parameters), if trustworthiness dimensions (reliability, robustness, fairness) are measured on the same LLM outputs, then synchronized multi-dimensional measurements exist with sufficient variance (σ>0.2) for correlation analysis, because dimensions can be operationalized as independent metrics on the same evaluation logs.

**Rationale:**  
This foundational hypothesis validates that multi-dimensional trustworthiness evaluation is technically feasible on existing benchmarks. Without sufficient measurement variance, correlation analysis would be meaningless due to floor/ceiling effects.

**Variables:**
- IV: Evaluation Setup (synchronization: same model checkpoint, same prompts, fixed generation parameters)
- DV: Reliability Score (GPT-4-as-judge accuracy 0-1), Robustness Score (paraphrase consistency 0-1), Fairness Score (HONEST bias 0-1)
- CV: Generation Parameters (temp=0.7, top-p=0.9, seed fixed), Model Architecture (Llama-2 family)

**Verification Protocol:**
1. Generate outputs for all 817 TruthfulQA prompts on Llama-2 (7B, 13B, 70B) with fixed generation parameters
2. Score reliability via GPT-4-as-judge, robustness via paraphrase consistency, fairness via demographic-augmented HONEST
3. Compute variance (σ) for each dimension across all outputs
4. Validate GPT-4-as-judge on n≥100 sample (target ≥90% agreement with human labels)
5. Confirm HONEST score variance >0.2 on n≥50 demographic-augmented pilot

**Success Criteria:**
- Primary: All three dimensions show σ>0.2 (sufficient variance for correlation)
- Secondary: GPT-4-as-judge achieves ≥90% agreement, HONEST variance ≥0.2

**Gate:**
- Type: MUST_WORK
- If Fail: Abort all subsequent hypotheses (no correlation analysis possible without variance)

**Prerequisites:** None (foundation hypothesis)

**Source:** Phase 2A Section 5 (SH1 - Existence)

---

#### H-M1: Reliability-Robustness Positive Coupling via Memorization

**Type:** MECHANISM  
**Statement:** Under factual prompts where memorization is expected, if reliability and robustness are measured on the same model outputs, then positive correlation r>0.3 (p<0.05) emerges, because shared training dynamics create correlations between factual correctness (reliability) and consistent retrieval (robustness) for memorized content.

**Rationale:**  
Tests the mechanism that memorized facts enable both reliability (correct retrieval) and robustness (consistent across paraphrases). Validates correlation arises from training dynamics, not measurement artifacts.

**Variables:**
- IV: Prompt Type (factual subset from TruthfulQA, ~400 prompts)
- DV: Pearson r (reliability-robustness correlation)
- CV: Same as H-E1

**Verification Protocol:**
1. Stratify TruthfulQA into factual vs. misinformation prompts based on question category
2. Compute Pearson correlation between reliability and robustness scores for factual stratum
3. Test significance via two-tailed p-value (α=0.05)
4. Check 95% CI lower bound >0.2 (correlation meaningfully positive)
5. Permutation test (1000 shuffles) to confirm observed r exceeds 95th percentile of null distribution

**Success Criteria:**
- Primary: Pearson r>0.3, p<0.05, 95% CI lower bound >0.2 on factual prompts
- Secondary: At least one model shows r>0.4 (strong coupling)

**Gate:**
- Type: MUST_WORK
- If Fail: Explore alternative mechanisms (retrieval quality, model calibration)

**Prerequisites:** H-E1 (measurements must exist)

**Source:** Phase 2A Causal Step 1 (Shared training dynamics)

---

#### H-M2: Fairness-Reliability Negative Coupling via Alignment Tax

**Type:** MECHANISM  
**Statement:** Under social-content questions, if fairness and reliability are measured on the same model outputs, then negative correlation r<-0.2 (p<0.05) emerges overall, because RLHF fine-tuning prioritizes fairness/safety over factual accuracy, creating an alignment tax trade-off.

**Rationale:**  
Tests the alignment tax hypothesis that RLHF creates trade-offs between safety (fairness) and accuracy (reliability). This mechanism explains negative coupling and has implications for model training strategies.

**Variables:**
- IV: Full TruthfulQA dataset (817 prompts)
- DV: Pearson r (fairness-reliability correlation)
- CV: Fine-tuning method (all models use RLHF - Llama-2-chat)

**Verification Protocol:**
1. Compute Pearson correlation between fairness and reliability scores across all 817 prompts
2. Test significance via two-tailed p-value (α=0.05)
3. Check 95% CI upper bound <-0.1 (correlation meaningfully negative)
4. Stratify by social content presence (demographic vs. non-demographic questions) to test moderation
5. Report effect size (Cohen's d) for practical significance

**Success Criteria:**
- Primary: Pearson r<-0.2, p<0.05, 95% CI upper bound <-0.1 overall
- Secondary: Negative correlation stronger on social-content subset (moderation effect)

**Gate:**
- Type: SHOULD_WORK
- If Fail: Pivot to independence hypothesis (dimensions orthogonal, no trade-off)

**Prerequisites:** H-M1 (reliability-robustness coupling established)

**Source:** Phase 2A Causal Step 2 (Alignment tax)

---

#### H-M3: Prompt-Type Moderation of Correlation Strength

**Type:** MECHANISM  
**Statement:** Under stratified prompt types (factual vs. misinformation), if reliability-robustness correlations are computed separately per stratum, then correlation magnitudes differ significantly (Fisher z-test p<0.05), because factual prompts show stronger coupling (r>0.4) than reasoning/misinformation prompts (r<0.3) due to different retrieval vs. computation mechanisms.

**Rationale:**  
Tests moderation hypothesis that correlation structure depends on cognitive task type. Factual tasks use memorization (strong coupling), reasoning tasks use computation with multiple paths (weak coupling). This validates mechanistic interpretation.

**Variables:**
- IV: Prompt Stratum (Factual vs. Misinformation from TruthfulQA)
- DV: Correlation Difference (Fisher z-test statistic)
- CV: Correlation computation method (Pearson, same for both strata)

**Verification Protocol:**
1. Compute reliability-robustness correlation separately for factual stratum (~400 prompts) and misinformation stratum (~400 prompts)
2. Apply Fisher z-transformation to both correlations
3. Test difference via Fisher z-test (α=0.05)
4. Confirm factual stratum r > misinformation stratum r by at least 0.1
5. Visualize with forest plot showing correlations per stratum with 95% CIs

**Success Criteria:**
- Primary: Fisher z-test p<0.05 (significant moderation effect)
- Secondary: Factual stratum r>0.4, Misinformation stratum r<0.3

**Gate:**
- Type: SHOULD_WORK
- If Fail: Report homogeneous correlations (mechanism not moderated by prompt type)

**Prerequisites:** H-M2 (mechanism hypotheses established)

**Source:** Phase 2A Causal Step 3 (Moderation by prompt type)

<!--
Each hypothesis follows this format:

#### {H-ID}: {Title}

**Type:** {EXISTENCE|MECHANISM|CONDITION|COMPARISON}
**Statement:** {Full Under-If-Then-Because statement}

**Variables:**
- IV: {independent variable}
- DV: {dependent variable}
- CV: {controlled variables}

**Success Criteria:**
- {quantitative threshold 1}
- {quantitative threshold 2}

**Gate:**
- Type: {MUST_WORK|SHOULD_WORK|DETERMINES_SUCCESS}
- If Fail: {consequence}

**Prerequisites:** {list or "None"}

**Verification Protocol:** (100-150 words)
{step-by-step protocol}

---
-->

---

## 3. Execution

### 3.1 Dependency Chain
```
H-E1 → H-M1 → H-M2 → H-M3
```
<!-- Sequential dependency: Each hypothesis builds on previous validation -->

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | All dimensions σ>0.2, GPT-4 ≥90% agreement | Abort pipeline (no variance) |
| H-M1 | MUST_WORK | r>0.3, p<0.05, 95% CI>0.2 on factual | Explore alternative mechanisms |
| H-M2 | SHOULD_WORK | r<-0.2, p<0.05, 95% CI<-0.1 overall | Pivot to independence |
| H-M3 | SHOULD_WORK | Fisher z p<0.05, factual r > misinf r | Report homogeneous correlations |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 2C | All (H-E1, H-M1, H-M2, H-M3) | Experiment design + implementation search |
| Phase 3 | All | PRD/Architecture generation |
| Phase 4 | Sequential (H-E1 → H-M1 → H-M2 → H-M3) | Code + validation per hypothesis |

**Total Duration:** 4 hypotheses × Phase 2C-4 pipeline = Full verification cycle

---

## 4. Risk Analysis

### 4.1 Assumption-Based Risks

| Risk | Source | Description | Severity | Affected Hypotheses |
|------|--------|-------------|----------|---------------------|
| R1 | A1 | GPT-4-as-judge noise >10% attenuates correlations | HIGH | H-E1, H-M1, H-M2, H-M3 |
| R2 | A2 | Back-translation semantic drift confounds robustness | MEDIUM | H-E1, H-M1, H-M3 |
| R3 | A3 | Fairness floor effect (all scores ~1.0) | HIGH | H-E1, H-M2 |
| R4 | A4 | Underpowered: true r=0.2-0.3 appears non-significant | MEDIUM | H-M1, H-M2, H-M3 |
| R5 | A5 | Model scale confounding (70B ≠ 7B patterns) | MEDIUM | All hypotheses |

### 4.2 Mitigation Strategies

**Risk R1: GPT-4-as-judge Noise**
- **Prevention:** Validate on n≥100 human-annotated sample before main eval (target ≥90% agreement)
- **Detection:** Monitor inter-rater reliability during validation phase
- **Response:** If agreement <90%, switch to human annotation or alternative automated scorer (e.g., fine-tuned classifier)

**Risk R2: Back-Translation Semantic Drift**
- **Prevention:** Pilot study (n=20) with expert review to confirm semantic preservation
- **Detection:** Manual inspection of paraphrase quality on random sample (n=50)
- **Response:** If drift detected, switch to deterministic paraphrasing (synonym substitution, word order permutation)

**Risk R3: Fairness Floor Effect**
- **Prevention:** Pilot HONEST scores on n≥50 demographic-augmented prompts, confirm variance ≥0.2
- **Detection:** Check variance during H-E1 validation
- **Response:** If variance <0.2, augment with adversarial fairness prompts or use alternative fairness metric (e.g., toxicity classifier)

**Risk R4: Statistical Power**
- **Prevention:** Preregistered power analysis confirms n=2,451 adequate for r≥0.18
- **Detection:** Post-hoc power analysis after data collection
- **Response:** If underpowered, report as exploratory finding; collect additional data for confirmatory study

**Risk R5: Model Scale Confounding**
- **Prevention:** Report correlations separately per model size (7B, 13B, 70B)
- **Detection:** Test for scale × correlation interaction via meta-regression
- **Response:** If confounded, stratify analysis by scale; test generalization via cross-scale meta-analysis

### 4.3 Risk-Hypothesis Mapping

```
Critical Path Risks:
- R1 (GPT-4 noise) → Affects ALL hypotheses → Validate FIRST
- R3 (Fairness floor) → Blocks H-E1, H-M2 → Pilot test FIRST

Moderate Risks:
- R2 (Semantic drift) → Affects H-M1, H-M3 → Pilot during H-E1
- R4 (Power) → Affects all mechanism tests → Monitor during analysis
- R5 (Scale confounding) → Affects generalization → Stratified reporting
```

---

## 5. Dependency Graph & Timeline

### 5.1 Hypothesis Dependency DAG

```
       ┌──────┐
       │ H-E1 │ ← Foundation (MUST_WORK gate)
       └───┬──┘
           │
       ┌───▼──┐
       │ H-M1 │ ← Reliability-Robustness Coupling (MUST_WORK)
       └───┬──┘
           │
       ┌───▼──┐
       │ H-M2 │ ← Fairness-Reliability Trade-off (SHOULD_WORK)
       └───┬──┘
           │
       ┌───▼──┐
       │ H-M3 │ ← Prompt-Type Moderation (SHOULD_WORK)
       └──────┘
```

**Dependency Rules:**
- H-E1: No prerequisites (foundation)
- H-M1: Requires H-E1 PASS (measurements must exist)
- H-M2: Requires H-M1 PASS (reliability coupling established)
- H-M3: Requires H-M2 COMPLETE (tests moderation after mechanisms)

**Critical Path:** H-E1 → H-M1 (both MUST_WORK gates)

### 5.2 Execution Timeline (Gantt Structure)

```
┌─────────────────────────────────────────────────────────────┐
│ Phase 2C: Experiment Design (Per-Hypothesis)               │
├─────────────────────────────────────────────────────────────┤
│ H-E1 Design │█████████│ (MCP search, dataset/model selection) │
│ H-M1 Design │         │█████████│                            │
│ H-M2 Design │         │         │█████████│                  │
│ H-M3 Design │         │         │         │█████████│        │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ Phase 3: Implementation Planning (Parallel PRD/Arch)       │
├─────────────────────────────────────────────────────────────┤
│ All H-* PRD │██████│                                         │
│ All H-* Arch│      │██████│                                  │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ Phase 4: Coding & Validation (Sequential)                  │
├─────────────────────────────────────────────────────────────┤
│ H-E1 Code+Val│███████████│ (GATE: MUST_WORK)                │
│ H-M1 Code+Val│           │███████████│ (GATE: MUST_WORK)    │
│ H-M2 Code+Val│                       │███████████│          │
│ H-M3 Code+Val│                                   │███████████│
└─────────────────────────────────────────────────────────────┘
```

**Timeline Notes:**
- **Phase 2C:** Sequential (each design builds on previous)
- **Phase 3:** Parallel (all PRD/Arch can run together)
- **Phase 4:** Sequential (gates enforce dependency order)

**Critical Milestones:**
1. H-E1 validation PASS → Unlock H-M1
2. H-M1 validation PASS → Unlock H-M2
3. All hypotheses complete → Proceed to Phase 5 (Baseline Comparison)

---

## 6. Dialectical Analysis

### 6.1 Thesis: Dimensional Coupling via Shared Training Dynamics

**Claim:** Trustworthiness dimensions (reliability, robustness, fairness) exhibit measurable correlations because they share training dynamics, architectural constraints, and optimization trade-offs.

**Supporting Evidence:**
- Memorization enables both reliability (correct retrieval) and robustness (consistency)
- RLHF alignment tax creates fairness vs. accuracy trade-offs
- Prompt type moderates correlation strength (factual vs. reasoning tasks)

**Predictions:**
- Positive coupling: Reliability-robustness r>0.3 on factual prompts
- Negative coupling: Fairness-reliability r<-0.2 overall
- Moderation: Factual correlations > Misinformation correlations

### 6.2 Antithesis: Dimensional Independence by Construction

**Counter-Claim:** Trustworthiness dimensions are orthogonal by design. Evaluation metrics measure distinct aspects of model behavior with no mechanistic coupling.

**Supporting Evidence:**
- Dimensions target different failure modes (correctness vs. consistency vs. bias)
- Metrics use different measurement approaches (accuracy vs. similarity vs. lexical analysis)
- No prior empirical evidence of cross-dimensional correlations

**Counter-Predictions:**
- Independence: All dimension pairs show |r|<0.2
- No moderation: Correlations homogeneous across prompt types
- Random ablation: Observed r within permutation null distribution

### 6.3 Synthesis: Outcome-Independent Publishability

**Resolution:** Both thesis and antithesis produce publishable, actionable results.

**Scenario 1 (Coupling Confirmed):**
- **Finding:** Dimensions correlate as predicted (r>0.3 or r<-0.2)
- **Implication:** Multi-dimensional evaluation should account for correlations; trade-offs guide training strategies
- **Contribution:** First empirical evidence of dimensional coupling in LLM trustworthiness

**Scenario 2 (Independence Confirmed):**
- **Finding:** All dimensions show |r|<0.2 (orthogonal)
- **Implication:** Dimensions can be optimized independently; no inherent trade-offs
- **Contribution:** Validates independence assumption; enables modular evaluation design

**Scenario 3 (Mixed Patterns):**
- **Finding:** Some dimensions couple (e.g., reliability-robustness r>0.3), others independent
- **Implication:** Partial coupling guides selective optimization; some trade-offs exist
- **Contribution:** Nuanced understanding of dimensional relationships

**Key Insight:** All three outcomes fill the knowledge gap (researchers currently ASSUME relationships without evidence). Any result provides empirical foundation for multi-dimensional evaluation design.

### 6.4 Robustness Assessment

**Threats to Validity:**
1. **Construct Validity:** Do metrics measure intended dimensions?
   - Mitigation: Validate GPT-4-as-judge, pilot HONEST scores, confirm semantic preservation
2. **Internal Validity:** Are correlations causal or confounded?
   - Mitigation: Control for model scale, generation parameters; test via permutation
3. **External Validity:** Do results generalize beyond Llama-2?
   - Limitation: Llama-2-only scope; future work needed for GPT/Claude/Gemini

**Sensitivity Analysis:**
- Test correlation stability across models (7B vs. 13B vs. 70B)
- Ablate metrics (e.g., swap GPT-4 for human annotations, test alternative robustness)
- Vary sample size (n=500, 1000, 2451) to assess power curve

**Falsifiability Check:**
- Each hypothesis has explicit threshold (r>0.3, r<-0.2, Fisher z p<0.05)
- 95% CIs provide falsification boundaries
- Permutation test provides null distribution baseline

---

## 7. Executive Summary

### 7.1 Research Objective

Systematically measure cross-dimensional correlations in LLM trustworthiness evaluation to determine whether dimensions (reliability, robustness, fairness) are independent, positively coupled, or negatively coupled when measured synchronously on the same model outputs.

### 7.2 Hypothesis Structure (4 Sub-Hypotheses)

1. **H-E1 (Existence - MUST_WORK):** Synchronized multi-dimensional measurements exist with sufficient variance (σ>0.2)
2. **H-M1 (Mechanism - MUST_WORK):** Reliability-robustness positive coupling (r>0.3) via memorization on factual prompts
3. **H-M2 (Mechanism - SHOULD_WORK):** Fairness-reliability negative coupling (r<-0.2) via alignment tax
4. **H-M3 (Mechanism - SHOULD_WORK):** Prompt-type moderation (Fisher z p<0.05): factual r > misinformation r

### 7.3 Experimental Scope

- **Models:** Llama-2-chat (7B, 13B, 70B)
- **Dataset:** TruthfulQA (817 prompts, stratified factual vs. misinformation)
- **Metrics:** Reliability (GPT-4-as-judge), Robustness (paraphrase consistency), Fairness (HONEST bias)
- **Sample Size:** n=2,451 (817 prompts × 3 models), 80% power for r≥0.18

### 7.4 Key Risks & Mitigations

- **R1 (GPT-4 noise):** Validate on n≥100 human sample (≥90% agreement)
- **R3 (Fairness floor):** Pilot n≥50 demographic prompts (variance ≥0.2)
- **R5 (Scale confounding):** Report correlations separately per model size

### 7.5 Success Criteria

**MUST_WORK Gates:**
- H-E1: All dimensions σ>0.2, GPT-4 ≥90% agreement → Unlock correlation analysis
- H-M1: Pearson r>0.3, p<0.05 on factual prompts → Validate memorization mechanism

**SHOULD_WORK Gates:**
- H-M2: Pearson r<-0.2, p<0.05 overall → Validate alignment tax
- H-M3: Fisher z p<0.05 → Validate moderation effect

**Outcome-Independent Publishability:** Coupling, independence, or mixed patterns all fill knowledge gap.

### 7.6 Novelty & Impact

**Key Innovation:** First systematic measurement of cross-dimensional trustworthiness correlations using synchronized evaluation; treats evaluation logs as latent correlation datasets.

**Differentiation:**
- vs. TrustVis: Measures natural inputs (not adversarial perturbations), explicitly tests correlations
- vs. MLLMGuard: Provides statistical framework for coupling vs. independence
- vs. BOLD: Cross-measures reliability/robustness/fairness on same outputs

**Impact:** Empirical foundation for multi-dimensional evaluation design; identifies trade-offs (if negative coupling) or independence (if orthogonal) to guide LLM training strategies.

---

## 8. Next Steps

### 8.1 Immediate Actions (Phase 2C)

1. **For Each Hypothesis (H-E1, H-M1, H-M2, H-M3):**
   - Run Phase 2C Experiment Design workflow
   - Generate detailed experiment brief (Level 1.5)
   - Search implementations via Exa MCP
   - Analyze code via Serena MCP
   - Produce per-hypothesis 02c_context_H-*.md file

2. **Validation Pilots:**
   - GPT-4-as-judge: Annotate n=100 TruthfulQA samples, compute agreement
   - HONEST fairness: Generate n=50 demographic-augmented prompts, check variance
   - Back-translation: Review n=20 paraphrases for semantic preservation

### 8.2 Phase 3-4 Pipeline

**Phase 3 (Implementation Planning):**
- Generate PRD/Architecture for all 4 hypotheses
- Assess complexity (all likely LIGHT tier - correlation analysis)
- Create Archon tasks for tracking

**Phase 4 (Coding & Validation):**
- Sequential execution: H-E1 → H-M1 → H-M2 → H-M3
- Coder-Validator loop per hypothesis
- Gate enforcement: MUST_WORK failures block pipeline

### 8.3 Phase 5 (Baseline Comparison)

**Deferred to Phase 5:**
- H-CP: Compare against independence baseline (r=0) and random ablation
- Full-scale experiment: TruthfulQA × 3 models × 3 dimensions
- Statistical testing: DeLong test, Fisher z-test, permutation test
- Result synthesis: Classify into independence, coupling, or mixed patterns

---

## Appendices

### A. Scope Reduction from Phase 2A

**Established Facts (BUILD_ON - No Re-Verification Needed):**
1. Current trustworthiness benchmarks (TruthfulQA, BOLD, AdvGLUE) evaluate dimensions independently
2. Frameworks like TrustVis/MLLMGuard perform multi-dimensional evaluation but don't analyze correlations

**Claims to Prove (PROVE_NEW):**
1. Synchronized measurement enables correlation discovery

**Scope Reduction:** 33% (2 of 3 claims already validated)

### B. Phase 2A Traceability

| Phase 2B Element | Phase 2A Source |
|------------------|-----------------|
| H-E1 | Section 5: SH1 (Existence) |
| H-M1 | Causal Step 1 (Memorization) |
| H-M2 | Causal Step 2 (Alignment tax) |
| H-M3 | Causal Step 3 (Moderation) |
| Variables | Section 1.2 (Variables table) |
| Assumptions | Section 1.4 (A1-A5) |
| Dataset/Model | Section 2 (Experimental setup) |
| Baselines | Section 4 (Related work) |

### C. Hypothesis Task Mapping (Archon)

Created in Step 10 (Finalize):
- H-E1 → Archon task (Hypothesis Verification feature)
- H-M1 → Archon task
- H-M2 → Archon task  
- H-M3 → Archon task

Pipeline Project ID: 1d475e5b-244a-4821-9800-9b38bea55cf4

---

**Document Status:** COMPLETE  
**Phase 2B Output:** 02b_verification_plan.md  
**Next Workflow:** Phase 2C Experiment Design (per-hypothesis)  
**Pipeline Status:** Phase 2B → Phase 2C transition ready

---
