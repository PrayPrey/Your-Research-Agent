# Verification Plan: RLHF-Induced Discriminative Degradation of Confidence Signals

**Date:** 2026-03-24
**Hypothesis ID:** H-CalibrationGeometry-v1
**Confidence:** 0.75
**Total Hypotheses:** 4

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement
Under multiple-choice QA evaluation on instruction-tuned LLMs, if RLHF instruction tuning is applied, then the discriminative quality of confidence signals degrades (AUROC for margin-based correctness prediction drops and margin-accuracy monotonicity weakens under percentile normalization), because preference optimization rewards decisive responses regardless of correctness, inflating logit margins even for incorrect predictions.

### 1.2 Alternative Hypothesis (H0)
RLHF instruction tuning does not degrade discriminative confidence quality; AUROC(margin → correctness) is unchanged between base and instruct models, and any ECE differences are attributable to scalar rescaling (equivalent to temperature shift) rather than geometric distortion of the confidence-accuracy relationship.

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | MMLU + TruthfulQA (standard) | MCQ format enables clean confidence extraction; domain labels enable stratified analysis; TruthfulQA tests factual accuracy |
| **Model** | Qwen2.5-7B, Llama-2-7B, Mistral-7B (base + instruct) | Multiple families enable cross-family generalization test; base+instruct pairs enable within-family alignment effect measurement |

**Dataset Details:**
- Source: Hugging Face datasets
- Path: cais/mmlu, truthful_qa

**Model Details:**
- Type: Causal LLM
- Source: Hugging Face model hub

### 1.4 Baseline Methods (for H-CP* comparison)

| Method | Performance | Dataset |
|--------|-------------|---------|
| Uncalibrated (T=1) | Raw softmax probabilities | MMLU, TruthfulQA |
| Global Temperature Scaling (Guo et al. 2017) | ~40% ECE reduction | CIFAR, ImageNet → LLM adaptation |
| Domain-Conditioned Temperature Scaling | Per-domain T_opt | MMLU domains |
| DACA (Luo et al. 2025) | 15% ECE improvement | MMLU, TruthfulQA |
| CCPS (Khanmohammadi et al. 2025) | 55% ECE reduction | MMLU |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | Logit margin is valid operationalization of model confidence for MCQ tasks | Standard practice in calibration literature; probability = softmax(margin) | Need alternative confidence definition (e.g., verbalized confidence) |
| A2 | Base models represent meaningful epistemic baseline for comparison | Base models trained on next-token likelihood without preference shaping | Cannot attribute calibration differences to RLHF specifically |
| A3 | Cross-family comparison is valid despite different training details | All families use similar RLHF paradigm (SFT + preference optimization) | Findings may be vendor-specific rather than RLHF-general |
| A4 | MMLU domain labels correspond to semantically distinct representational subspaces | MMLU subjects cover distinct knowledge domains | Domain structure findings would be meaningless |
| A5 | Discriminative degradation is not fully explained by accuracy differences | AUROC measures rank-ordering independent of accuracy level | Effect would be trivial consequence of accuracy drop |

### 1.6 Research Gap & Novelty

**Preserved Novelty:** First systematic study of discriminative degradation (AUROC-based) rather than calibration metrics (ECE-based) under RLHF.

**Key Innovation:** Testing geometry distortion via percentile-normalized monotonicity, distinguishing fundamental signal corruption from scalar rescaling.

**Differentiation:**
- Guo et al. 2017: Applied to LLMs with RLHF; tests whether scaling suffices to repair distortion
- Tian et al. 2023: Measures discriminative degradation (AUROC) not just calibration shift (ECE)
- DACA/CCPS 2025: Tests cross-family generalizability and mechanistic claims, not just method performance

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| H-E1 | Existence | MUST_WORK | None | READY |
| H-M1 | Mechanism | MUST_WORK | H-E1 | BLOCKED |
| H-M2 | Mechanism | MUST_WORK | H-M1 | BLOCKED |
| H-M3 | Mechanism | SHOULD_WORK | H-M2 | BLOCKED |

---

### 2.2 Hypothesis Specifications

---

#### H-E1: AUROC Discriminative Degradation Existence

**Statement**: Under MCQ evaluation on instruction-tuned LLMs, if RLHF instruction tuning is applied, then AUROC(margin → correctness) is significantly lower for instruct models than base models across Qwen, Llama, and Mistral families, because preference optimization rewards decisive responses regardless of correctness.

**Rationale**: This existence hypothesis establishes whether discriminative degradation occurs at all. If AUROC doesn't drop, the entire "geometry distortion" narrative collapses. Cross-family consistency validates RLHF as the causal factor rather than vendor-specific training details.

**Variables**:
- Independent: Model Type (base vs. instruct), Model Family (Qwen/Llama/Mistral)
- Dependent: AUROC(margin → correctness)
- Controlled: Decoding Temperature (T=0), Evaluation Dataset (MMLU ~14,000 samples)

**Verification Protocol**:
1. Load base and instruct model pairs for each of 3 families from HuggingFace.
2. Run greedy inference (T=0) on full MMLU test set, extract top-1 and top-2 logits.
3. Compute margin = logit_top1 - logit_top2, calculate AUROC using margin as predictor.
4. Bootstrap 95% CIs for AUROC difference (instruct - base) per family.
5. Run random-effects meta-analysis for cross-family heterogeneity (I², τ²).

**Success Criteria** (PoC):
- Primary: AUROC_instruct < AUROC_base with non-overlapping 95% CIs for all 3 families
- Secondary: I² < 50% indicating low heterogeneity (cross-family consistency)

**Failure Response**: IF fails → ABANDON (core claim invalidated; geometric distortion narrative unsupported)

**Dependencies**: None (foundation hypothesis)

**Source**: Phase 2A SH1, Prediction P1

---

#### H-M1: Conditional Margin Inflation

**Statement**: Under MCQ evaluation, if RLHF instruction tuning inflates logit margins uniformly including for incorrect predictions, then E[margin | incorrect]_instruct > E[margin | incorrect]_base, because Bradley-Terry preference optimization penalizes hedging and rewards decisive responses.

**Rationale**: This mechanism hypothesis tests the first causal step - whether RLHF actually inflates margins for incorrect predictions. This is the mechanistic foundation explaining WHY AUROC degrades: margins become less informative about correctness.

**Variables**:
- Independent: Model Type (base vs. instruct)
- Dependent: E[margin | incorrect], E[margin | correct]
- Controlled: Difficulty bins (base model accuracy), Same MMLU test samples

**Verification Protocol**:
1. Partition MMLU samples into correct/incorrect by model prediction.
2. Compute conditional margin distributions for base and instruct models.
3. Calculate mean margins: E[margin | incorrect] and E[margin | correct] per model.
4. Run permutation test (n=10000) for E[margin | incorrect] difference.
5. Visualize conditional margin distributions with kernel density estimates.

**Success Criteria** (PoC):
- Primary: E[margin | incorrect]_instruct > E[margin | incorrect]_base (permutation p < 0.05)
- Secondary: Effect consistent across model families

**Failure Response**: IF fails → PIVOT to alternative mechanism (verbalized confidence, attention patterns)

**Dependencies**: H-E1 (existence must be established first)

**Source**: Phase 2A Causal Step 2, Prediction P3

---

#### H-M2: Percentile-Normalized Monotonicity Attenuation

**Statement**: Under percentile-normalized margin analysis, if margin inflation decouples confidence-correctness relationship, then β_percentile_instruct < β_percentile_base in logistic regression Pr(correct) = σ(α + β·z-score(margin)), because the geometric shape of the probability landscape is distorted beyond scalar rescaling.

**Rationale**: Percentile normalization distinguishes geometric distortion from scalar rescaling (temperature-like). If β_percentile drops, the effect is fundamental signal corruption, not just confidence scale shift. This is the key methodological innovation.

**Variables**:
- Independent: Model Type (base vs. instruct), Prompt Format (zero-shot/few-shot)
- Dependent: β_percentile (logistic regression slope)
- Controlled: 2×2 factorial design for prompt robustness, Difficulty stratification

**Verification Protocol**:
1. Z-score normalize margins within each model (percentile normalization).
2. Fit logistic regression Pr(correct) = σ(α + β·z-score(margin)) per model.
3. Extract β_percentile coefficients with bootstrap 95% CIs.
4. Compare across 2×2 conditions (base/instruct × zero-shot/few-shot).
5. Verify effect persists across prompt formats (robustness check).

**Success Criteria** (PoC):
- Primary: β_percentile_instruct < β_percentile_base with p < 0.05
- Secondary: Effect survives 2×2 prompt design controls

**Failure Response**: IF fails → EXPLORE alternative normalization schemes; consider scalar rescaling as full explanation

**Dependencies**: H-M1 (margin inflation must be established)

**Source**: Phase 2A Causal Step 3, Prediction P2

---

#### H-M3: Geometry vs. Scale Distinction (Brier Decomposition)

**Statement**: Under Murphy Brier decomposition, if the distortion is geometric rather than scalar, then Refinement component decreases in instruct models while Reliability may improve, because geometric distortion affects discriminative information content while temperature scaling only affects calibration.

**Rationale**: Brier decomposition separates calibration (Reliability) from discrimination (Refinement). If RLHF distortion is purely geometric, Refinement should degrade. If it's scalar (temperature-like), only Reliability is affected. This distinguishes the two explanations.

**Variables**:
- Independent: Model Type (base vs. instruct)
- Dependent: Brier Score, Reliability, Refinement, Uncertainty components
- Controlled: 15-bin calibration curves, Same evaluation samples

**Verification Protocol**:
1. Compute softmax probabilities from logit margins for each model.
2. Calculate Brier Score = mean((probability - correctness)²).
3. Apply Murphy decomposition: Brier = Reliability - Refinement + Uncertainty.
4. Compare component changes between base and instruct models.
5. Analyze whether Refinement decreases (geometric) or only Reliability changes (scalar).

**Success Criteria** (PoC):
- Primary: Refinement_instruct < Refinement_base (discrimination degrades)
- Secondary: Reliability may improve (temperature-like calibration effect coexists)

**Failure Response**: IF fails → Accept scalar rescaling as sufficient explanation; revise theoretical claims

**Dependencies**: H-M2 (monotonicity attenuation must be established)

**Source**: Phase 2A Causal Step 4, Evidence Summary

---

## 3. Risk Analysis

### 3.1 Assumption-Based Risks

**Risk R1: Invalid Confidence Operationalization**
- **Source Assumption:** A1 - Logit margin is valid operationalization of model confidence
- **Description:** If logit margin doesn't capture true model confidence, all AUROC-based analyses become meaningless
- **Severity:** High
- **Likelihood:** Low (well-established practice)
- **Affected Hypotheses:** H-E1, H-M1, H-M2

**Risk R2: Baseline Confounding**
- **Source Assumption:** A2 - Base models represent meaningful epistemic baseline
- **Description:** If base models have pre-existing calibration issues unrelated to RLHF, cannot attribute differences specifically to preference optimization
- **Severity:** High
- **Likelihood:** Medium (base models may have training artifacts)
- **Affected Hypotheses:** H-E1, H-M1

**Risk R3: Vendor-Specific Effects**
- **Source Assumption:** A3 - Cross-family comparison is valid
- **Description:** Different RLHF implementations (DPO vs PPO, different reward models) may confound cross-family generalization
- **Severity:** Medium
- **Likelihood:** Medium (training details differ across vendors)
- **Affected Hypotheses:** H-M1, H-M2, H-M3

**Risk R4: Spurious Domain Structure**
- **Source Assumption:** A4 - MMLU domains correspond to distinct representational subspaces
- **Description:** Domain labels may correlate with difficulty/lexical features rather than representational structure
- **Severity:** Low (exploratory finding only)
- **Likelihood:** High (known confound concern)
- **Affected Hypotheses:** (Exploratory - not blocking)

**Risk R5: Accuracy-AUROC Confounding**
- **Source Assumption:** A5 - Discriminative degradation not explained by accuracy differences
- **Description:** If instruct models have lower accuracy, AUROC drop could be trivial consequence rather than novel finding
- **Severity:** High
- **Likelihood:** Low (AUROC is rank-based)
- **Affected Hypotheses:** H-E1 (primary), all H-M*

### 3.2 Risk-Hypothesis Mapping

| Risk | Source | Affected Hypotheses | Severity | Impact |
|------|--------|---------------------|----------|--------|
| R1 | A1 | H-E1, H-M1, H-M2 | High | Invalidates margin-based methodology |
| R2 | A2 | H-E1, H-M1 | High | Cannot attribute to RLHF |
| R3 | A3 | H-M1, H-M2, H-M3 | Medium | Limits generalizability claims |
| R4 | A4 | (Exploratory) | Low | Domain findings conditional |
| R5 | A5 | H-E1, all H-M* | High | Effect becomes trivial |

**Risk Propagation:**
- R1, R2, R5 threaten foundational H-E1 → cascade to all mechanism hypotheses
- R3 limits scope of conclusions but doesn't invalidate core findings
- R4 affects only exploratory domain analysis (already scoped as conditional)

### 3.3 Mitigation Strategies

**R1 Mitigation: Invalid Confidence Operationalization**
- **Prevention:** Use established margin definition (logit_top1 - logit_top2) from calibration literature
- **Detection:** Compare AUROC with alternative confidence measures (verbalized, entropy-based)
- **Response:**
  - PIVOT: Switch to verbalized confidence (Tian et al. 2023 approach)
  - SCOPE: Report margin-based findings with caveats
  - ABORT: If no confidence measure shows discriminative degradation

**R2 Mitigation: Baseline Confounding**
- **Prevention:** Select models with documented training procedures from major vendors
- **Detection:** Check base model ECE/AUROC against known benchmarks; flag outliers
- **Response:**
  - PIVOT: Use different base model checkpoints or model families
  - SCOPE: Limit claims to "instruct vs base" without RLHF attribution
  - ABORT: If base models have severe pre-existing calibration issues

**R3 Mitigation: Vendor-Specific Effects**
- **Prevention:** Use meta-analysis with heterogeneity statistics (I², τ²)
- **Detection:** Monitor heterogeneity; I² > 75% indicates vendor-specific effects
- **Response:**
  - PIVOT: Focus on families with similar RLHF approach (e.g., all DPO-based)
  - SCOPE: Report per-family results separately; acknowledge heterogeneity
  - ABORT: Not applicable (heterogeneity is valid finding)

**R4 Mitigation: Spurious Domain Structure**
- **Prevention:** Include lexical controls (token length, answer entropy) as covariates
- **Detection:** F-test for domain coefficients after adding lexical covariates
- **Response:**
  - PIVOT: Not applicable (already scoped as conditional finding)
  - SCOPE: Report domain findings only if survive lexical controls
  - ABORT: Accept domain structure is proxy for lexical features

**R5 Mitigation: Accuracy-AUROC Confounding**
- **Prevention:** Use difficulty stratification (base model accuracy bins)
- **Detection:** Check AUROC within difficulty strata; verify effect persists
- **Response:**
  - PIVOT: Report stratified results; focus on bins with matched accuracy
  - SCOPE: Control for accuracy in regression analysis
  - ABORT: If effect vanishes after accuracy stratification

### 3.4 Risk Summary

| ID | Risk | Source | Severity | Affected | Primary Mitigation |
|----|------|--------|----------|----------|-------------------|
| R1 | Invalid confidence operationalization | A1 | High | H-E1, H-M1-2 | Use established margin definition |
| R2 | Baseline confounding | A2 | High | H-E1, H-M1 | Select documented model pairs |
| R3 | Vendor-specific effects | A3 | Medium | H-M1-3 | Meta-analysis with heterogeneity stats |
| R4 | Spurious domain structure | A4 | Low | Exploratory | Lexical covariate controls |
| R5 | Accuracy-AUROC confounding | A5 | High | All H-* | Difficulty stratification |

**Risk Profile:**
- Critical Risks: 0
- High Risks: 3 (R1, R2, R5)
- Medium Risks: 1 (R3)
- Low Risks: 1 (R4)

**Key Observation:** High-severity risks (R1, R2, R5) all threaten the foundational H-E1 hypothesis. If H-E1 fails due to any of these risks, the entire mechanism chain (H-M1-3) is invalidated. This reinforces the MUST_WORK gate on H-E1.

---

## 4. Dependency Structure

### 4.1 Dependency Graph (DAG)

```
═══════════════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) - 4 Hypotheses
═══════════════════════════════════════════════════════════════════

[Level 0 - Foundation]
         ┌───────────────────────────────────────┐
         │  H-E1: AUROC Discriminative           │
         │        Degradation Existence          │
         │  Gate: MUST_WORK                      │
         │  Status: READY                        │
         └───────────────────┬───────────────────┘
                             │
                             ▼
[Level 1 - Mechanism Step 1]
         ┌───────────────────────────────────────┐
         │  H-M1: Conditional Margin Inflation   │
         │  Gate: MUST_WORK                      │
         │  Prereq: H-E1                         │
         └───────────────────┬───────────────────┘
                             │
                             ▼
[Level 2 - Mechanism Step 2]
         ┌───────────────────────────────────────┐
         │  H-M2: Percentile-Normalized          │
         │        Monotonicity Attenuation       │
         │  Gate: MUST_WORK                      │
         │  Prereq: H-M1                         │
         └───────────────────┬───────────────────┘
                             │
                             ▼
[Level 3 - Mechanism Step 3]
         ┌───────────────────────────────────────┐
         │  H-M3: Geometry vs. Scale             │
         │        (Brier Decomposition)          │
         │  Gate: SHOULD_WORK                    │
         │  Prereq: H-M2                         │
         └───────────────────┬───────────────────┘
                             │
                             ▼
                    ┌────────────────┐
                    │   PHASE 5      │
                    │   Baseline     │
                    │   Comparison   │
                    └────────────────┘

═══════════════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M2 → H-M3 → Phase 5
All hypotheses are SEQUENTIAL (no parallelization)
═══════════════════════════════════════════════════════════════════
```

### 4.2 Dependency Hierarchy

| Level | Hypothesis | Prerequisites | Gate Type | Fail Action |
|-------|-----------|---------------|-----------|-------------|
| 0 | H-E1 | None | MUST_WORK | STOP - Reassess hypothesis |
| 1 | H-M1 | H-E1 | MUST_WORK | PIVOT - Alternative mechanism |
| 2 | H-M2 | H-M1 | MUST_WORK | EXPLORE - Alternative normalization |
| 3 | H-M3 | H-M2 | SHOULD_WORK | ACCEPT - Scalar rescaling explanation |

**Verification Phases:**

**Phase 1 - Foundation (H-E1)**
- Test: AUROC_instruct < AUROC_base across 3 families
- Gate: MUST PASS → If fail, core claim is invalidated
- Consequence: Failure terminates pipeline

**Phase 2 - Core Mechanisms (H-M1, H-M2, H-M3)**
- H-M1 Gate: MUST PASS → Establishes margin inflation mechanism
- H-M2 Gate: MUST PASS → Distinguishes geometry from scale
- H-M3 Gate: SHOULD PASS → Provides Brier decomposition evidence
- Consequence: H-M1/H-M2 failure requires mechanism revision; H-M3 failure documents limitation

**Phase 3 - Baseline Comparison (Phase 5)**
- Deferred to Phase 5 after all mechanism hypotheses complete
- Uses verification_state.yaml for hypothesis handoff

---

## 5. Execution

### 5.1 Dependency Chain
```
H-E1 → H-M1 → H-M2 → H-M3 → Phase 5 (Baseline Comparison)
```

### 5.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | AUROC_instruct < AUROC_base (all 3 families, non-overlapping 95% CIs) | STOP - Core claim invalidated |
| H-M1 | MUST_WORK | E[margin\|incorrect]_instruct > E[margin\|incorrect]_base (p < 0.05) | PIVOT - Alternative mechanism |
| H-M2 | MUST_WORK | β_percentile_instruct < β_percentile_base (p < 0.05) | EXPLORE - Alternative normalization |
| H-M3 | SHOULD_WORK | Refinement_instruct < Refinement_base | ACCEPT - Document as scalar rescaling |

### 5.3 Timeline (Gantt)

```
═══════════════════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE - 4 Hypotheses (5 Weeks Total)
═══════════════════════════════════════════════════════════════════════════════
Phase/Hypothesis       │ W1-2      │ W3-4      │ W5        │ Notes
───────────────────────┼───────────┼───────────┼───────────┼──────────────────
PHASE 1: Foundation    │           │           │           │
  H-E1 AUROC           │ ██████████│           │           │ 3 families × MMLU
  [Gate 1]             │           ◆           │           │ MUST_WORK
───────────────────────┼───────────┼───────────┼───────────┼──────────────────
PHASE 2: Mechanisms    │           │           │           │
  H-M1 Margin Inflate  │           │ ██████████│           │ Conditional dist.
  H-M2 β_percentile    │           │     ██████│█████      │ 2×2 prompt design
  H-M3 Brier Decomp    │           │           │     █████ │ Refinement analysis
  [Gate 2]             │           │           │         ◆ │ Core mechanisms
───────────────────────┼───────────┼───────────┼───────────┼──────────────────
PHASE 5: Baseline      │           │           │           │ (Deferred)
  Comparison           │           │           │   ────────│→ After Phase 4
═══════════════════════════════════════════════════════════════════════════════
Legend: ████ = Active work | ◆ = Gate decision point | ──→ = Deferred
Total Duration: 5 weeks (excluding Phase 5 baseline comparison)
═══════════════════════════════════════════════════════════════════════════════
```

### 5.4 Critical Path Analysis

**Critical Path:** H-E1 → H-M1 → H-M2 → H-M3

**Duration Breakdown:**
| Phase | Hypotheses | Duration | Cumulative |
|-------|-----------|----------|------------|
| Foundation | H-E1 | 2 weeks | Week 1-2 |
| Mechanisms | H-M1 | 2 weeks | Week 3-4 |
| Mechanisms | H-M2 | 1 week | Week 5 |
| Mechanisms | H-M3 | 1 week | Week 5 (parallel) |

**Total Duration:** 5 weeks (H-M2 and H-M3 can overlap in Week 5)

**Slack Analysis:**
- H-E1: 0 slack (critical)
- H-M1: 0 slack (critical, depends on H-E1 gate)
- H-M2: 0 slack (critical)
- H-M3: 1 week slack (can start after H-M2 data available)

**Risk to Timeline:**
- Gate 1 (H-E1) failure: Terminates at Week 2
- Gate 2 (H-M1) failure: Requires mechanism pivot at Week 4

### 5.5 Resource Summary

**Compute Requirements:**
| Resource | H-E1 | H-M1 | H-M2 | H-M3 | Total |
|----------|------|------|------|------|-------|
| GPU Hours | 36 | 0 | 2 | 1 | 39 |
| Models | 6 | - | - | - | 6 |
| MMLU Samples | ~14K | - | - | - | ~14K |

**Breakdown:**
- H-E1: 6 models × 3 families × 2 hrs/model = 36 GPU hours (single A100)
- H-M1: Reuses H-E1 logits, no additional inference
- H-M2: 2×2 prompt design doubles inference for subset (4K samples) = 2 GPU hours
- H-M3: Brier decomposition uses H-E1 outputs, minimal compute

**Personnel:** Single researcher + GPU cluster access

**Data Dependencies:**
- MMLU: Hugging Face `cais/mmlu` (available)
- TruthfulQA: Hugging Face `truthful_qa` (available)
- Models: All available on HuggingFace Hub

### 5.6 Execution Order

**Step 1** (Week 1-2): Execute H-E1 - AUROC Discriminative Degradation Existence
- Load 6 models (3 base + 3 instruct)
- Run inference on full MMLU test set
- Compute margins and AUROC per family
- Bootstrap 95% CIs for AUROC difference
- Run meta-analysis for heterogeneity (I², τ²)

**Step 2** (Week 2): Evaluate Gate 1
- Check: AUROC_instruct < AUROC_base for all 3 families?
- Check: Non-overlapping 95% CIs?
- Check: I² < 50% (low heterogeneity)?
- **IF FAIL → STOP** (core claim invalidated)
- **IF PASS → Proceed to H-M1**

**Step 3** (Week 3-4): Execute H-M1 - Conditional Margin Inflation
- Partition samples into correct/incorrect
- Compute conditional margin distributions
- Run permutation test for E[margin|incorrect] difference
- Visualize distributions with kernel density

**Step 4** (Week 5): Execute H-M2 - Percentile-Normalized Monotonicity
- Z-score normalize margins per model
- Fit logistic regression Pr(correct) = σ(α + β·z-score(margin))
- Compare β_percentile across 2×2 conditions
- Verify effect survives prompt format controls

**Step 5** (Week 5): Execute H-M3 - Brier Decomposition (parallel with H-M2)
- Compute Brier Score from softmax probabilities
- Apply Murphy decomposition (Reliability, Refinement, Uncertainty)
- Compare Refinement component between base/instruct

**Step 6** (Week 5): Evaluate Gate 2
- Check: E[margin|incorrect]_instruct > E[margin|incorrect]_base?
- Check: β_percentile_instruct < β_percentile_base?
- Document H-M3 findings (SHOULD_WORK gate)
- **IF H-M1/H-M2 FAIL → PIVOT** (alternative mechanism)
- **IF PASS → Verification complete, proceed to Phase 5**

**Total Duration:** 5 weeks

---

## 6. Dialectical Analysis

### 6.1 Thesis Statement

**Core Claim:** RLHF instruction tuning systematically degrades the discriminative quality of LLM confidence signals, measurable as reduced AUROC for logit-margin-based correctness prediction and weakened margin-accuracy monotonicity under percentile normalization.

**Supporting Evidence:**
1. Bradley-Terry preference model underlying RLHF rewards decisive, confident-sounding responses regardless of correctness
2. This creates selection pressure that inflates logit margins uniformly, including for incorrect predictions
3. Margin inflation decouples the confidence-correctness relationship that exists in base models
4. Percentile normalization reveals geometric distortion (probability landscape shape) rather than scalar rescaling
5. Prior work (Tian et al. 2023) documents RLHF-induced overconfidence; this extends to discriminative degradation

**Strengths:**
- Builds on established RLHF overconfidence literature (Tian 2023, 598 citations)
- Uses AUROC which is rank-based and independent of accuracy level
- Cross-family design (Qwen, Llama, Mistral) enables generalizability test
- Percentile normalization is novel methodological contribution distinguishing geometry from scale
- Clear falsification criteria via bootstrap confidence intervals and heterogeneity statistics

**Expected Outcomes:**
- Primary: AUROC_instruct < AUROC_base across 3 families; I² < 50%
- Secondary: β_percentile_instruct < β_percentile_base survives 2×2 prompt controls
- Tertiary: Brier Refinement decreases in instruct models

### 6.2 Antithesis Development

**Null Hypothesis (H0):** RLHF instruction tuning does not degrade discriminative confidence quality; any observed AUROC differences are attributable to scalar rescaling (equivalent to temperature shift) rather than geometric distortion of the confidence-accuracy relationship.

**Counter-Arguments:**
1. Temperature scaling is known to repair calibration without affecting discrimination - if RLHF effect is scalar, simple rescaling should eliminate apparent degradation
2. Base and instruct models have different output distributions due to prompting format differences, not fundamental representational changes
3. AUROC drop could be trivially explained by accuracy differences rather than confidence signal corruption
4. Cross-family heterogeneity may be high (I² > 75%) indicating vendor-specific effects unrelated to RLHF mechanism
5. Logit margin may not be the appropriate confidence measure for instruction-tuned models

**Potential Failure Points:**
- R1: Invalid confidence operationalization (logit margin inappropriate)
- R2: Baseline confounding (base models have pre-existing issues)
- R5: Accuracy-AUROC confounding (trivial explanation)

**Conditions Under Which H0 Would Be Supported:**
- Percentile normalization eliminates AUROC difference between base and instruct
- Brier Refinement component unchanged (only Reliability affected)
- High heterogeneity (I² > 75%) across model families
- Conditional margin distributions identical (E[margin|incorrect] unchanged)

### 6.3 Synthesis

**Balanced Assessment:**

The hypothesis H-CalibrationGeometry-v1 presents a testable claim that RLHF fundamentally corrupts discriminative confidence signals through geometric distortion of the probability landscape. However, the null hypothesis raises valid concerns that observed differences could be explained by simpler scalar rescaling mechanisms.

**Resolution Path:**

The verification plan addresses this dialectic through hierarchical hypothesis testing:
1. **H-E1 (Foundation):** Establishes existence of AUROC degradation with cross-family consistency
2. **H-M1 (Conditional Margins):** Tests whether margin inflation affects incorrect predictions specifically
3. **H-M2 (Percentile Normalization):** The key test distinguishing geometry from scale
4. **H-M3 (Brier Decomposition):** Separates calibration effects (Reliability) from discrimination effects (Refinement)

**Conditions for Thesis Support:**
- H-E1: AUROC_instruct < AUROC_base with non-overlapping 95% CIs; I² < 50%
- H-M1: E[margin|incorrect]_instruct > E[margin|incorrect]_base (p < 0.05)
- H-M2: β_percentile_instruct < β_percentile_base survives prompt controls
- H-M3: Refinement_instruct < Refinement_base

**Conditions for Antithesis Support:**
- H-E1 fails (AUROC unchanged or CIs overlap)
- H-M2 shows β_percentile difference vanishes under normalization
- H-M3 shows only Reliability affected, Refinement unchanged
- High heterogeneity (I² > 75%) across model families

**Nuanced Outcome Possibilities:**
1. **Full Support:** All MUST_WORK gates pass, Refinement degrades → Thesis validated
2. **Partial Support:** H-E1, H-M1, H-M2 pass but H-M3 inconclusive → Geometric distortion confirmed, Brier evidence limited
3. **Mixed Evidence:** Low heterogeneity but moderate β_percentile effect → Both geometric and scalar components present
4. **No Support:** H-E1 fails → Antithesis supported, core claim invalidated

### 6.4 Robustness Assessment

| Aspect | Thesis Position | Antithesis Challenge | Resolution Test |
|--------|-----------------|----------------------|-----------------|
| Existence | AUROC degrades across families | May be artifact or vendor-specific | H-E1 with heterogeneity stats |
| Mechanism | Margin inflation for errors | Simple scale shift | H-M1 conditional analysis |
| Geometry vs Scale | β_percentile attenuation | Temperature-like rescaling | H-M2 percentile normalization |
| Decomposition | Refinement degrades | Only Reliability affected | H-M3 Brier decomposition |
| Generalizability | Cross-family consistency | Vendor-specific effects | I² < 50% criterion |

**Overall Robustness Score:** High

The verification plan is robust because:
- Multiple independent tests (AUROC, conditional margins, percentile slopes, Brier) converge on same question
- Clear gate conditions prevent wasted effort on invalidated claims
- Cross-family design with heterogeneity statistics addresses generalizability concerns
- 2×2 prompt design controls for format confounds
- Difficulty stratification controls for accuracy-AUROC confounding

**Confidence in Verification Plan:** 0.75

**Key Uncertainties:**
- Binning choices for Brier decomposition may affect conclusions
- Moderate heterogeneity (50% < I² < 75%) would require nuanced interpretation
- MMLU-specific results may not generalize to other task types

---

## 7. Summary & Conclusions

### 7.1 Executive Summary

**Main Hypothesis:** RLHF instruction tuning degrades discriminative confidence quality (AUROC drops, monotonicity weakens)
- ID: H-CalibrationGeometry-v1, Confidence: 0.75

**Verification Structure:**
- Mode: Incremental (Phase 2A available)
- Sub-Hypotheses: 4 total (H-E1, H-M1, H-M2, H-M3)
- Phases: 2 phases over 5 weeks
- Critical Gates: 4 decision points (2 MUST_WORK, 2 SHOULD_WORK)

**Risk Assessment:** Medium
- Primary concerns: Baseline confounding (R2), Accuracy-AUROC confounding (R5)

**Key Innovation:** Percentile-normalized monotonicity analysis distinguishes geometric distortion from scalar rescaling

**Immediate Action:** Begin Phase 2C experiment design for H-E1

### 7.2 Final Summary

**Key Achievements:**
- 4 hypotheses defined with complete verification protocols
- H0 addressed: "AUROC unchanged, differences are scalar rescaling"
- Established Facts preserved: Temperature scaling, RLHF overconfidence, post-hoc calibration methods

**Verification Execution Order:**

**Phase 1: Foundation** (2 weeks)
- H-E1: AUROC_instruct < AUROC_base across Qwen, Llama, Mistral families
- Gate 1: MUST PASS (non-overlapping 95% CIs, I² < 50%)

**Phase 2: Core Mechanisms** (3 weeks)
- H-M1: E[margin|incorrect] inflation test
- H-M2: Percentile-normalized β_percentile attenuation
- H-M3: Brier decomposition (Refinement degradation)
- Gate 2: H-M1, H-M2 must pass

**Critical Decision Points:**
1. **Gate 1 (H-E1):** FAIL → STOP, core claim invalidated
2. **Gate 2 (H-M1):** FAIL → PIVOT to alternative mechanism
3. **Gate 3 (H-M2):** FAIL → EXPLORE alternative normalization
4. **Gate 4 (H-M3):** FAIL → ACCEPT scalar rescaling component

### 7.3 Conclusions

**Open Questions (from Phase 2A):**
- Whether domain structure survives lexical controls (exploratory, not blocking)
- Whether domain-conditioned scaling achieves Pareto improvement (Phase 5)
- Effect size magnitude for deployment recommendations

**Recommendations:**

1. **Immediate Actions:**
   - Proceed to Phase 2C: Experiment Design for H-E1
   - Set up inference pipeline for 6 models on MMLU
   - Prepare bootstrap and meta-analysis infrastructure

2. **Resource Allocation:**
   - Allocate 39 GPU hours for H-E1 (36 inference + 3 analysis)
   - Reserve 1 week buffer for unexpected issues
   - Plan for 2×2 prompt design in H-M2

3. **Failure Management:**
   - Document all intermediate results regardless of outcome
   - Execute PIVOT strategies if H-M1 fails (alternative mechanism)
   - Accept partial support as valid publishable outcome

### 7.4 Appendices

**A. Phase 2A Reference**
- Source: `docs/youra_research/20260323_buildingtrust/03_refinement.yaml`
- Hypothesis ID: H-CalibrationGeometry-v1
- Schema Version: 10.0.0 (Free-Parse)

**B. MCP Tool Usage Summary**
- Total MCP calls: 7
  - mcp__clearThought__scientificmethod: 4 (hypothesis + experiment stages)
  - mcp__clearThought__structuredargumentation: 3 (thesis, antithesis, synthesis)

**C. Scope Reduction**
- Total Claims: 5
- BUILD_ON: 3 (temperature scaling, RLHF overconfidence, post-hoc calibration)
- PROVE_NEW: 2 (discriminative degradation, domain structure)
- Reduction: 50% (focus on novel claims only)

---

## 8. State & Task Integration

### 8.1 Verification State Status

**File Created:** `verification_state.yaml` (schema v3.5)

**Sub-Hypotheses Registered:** 4
| ID | Type | Status | Gate |
|----|------|--------|------|
| h-e1 | EXISTENCE | READY | MUST_WORK |
| h-m1 | MECHANISM | NOT_STARTED | MUST_WORK |
| h-m2 | MECHANISM | NOT_STARTED | MUST_WORK |
| h-m3 | MECHANISM | NOT_STARTED | SHOULD_WORK |

**Workflow Status:** ACTIVE
**Current Phase:** Phase 2B (COMPLETED)
**Next Action:** Begin Phase 2C with H-E1 (first READY hypothesis)

### 8.2 Pipeline Tasks Updated

**Pipeline Project:** Anonymous Pipeline: Building Trust - Confidence Frequency Calibration
**Project ID:** `a9ac2505-d1b6-4ddd-9129-01cacc8836d2`

| Task | Status | Task ID |
|------|--------|---------|
| Phase 2B - Planning | done | `beed3432-3a2a-423a-a1e4-2524eccecd8b` |
| Phase 2C - Experiment Design | doing | `cb39c5ad-6d19-4865-aa10-0b84d98606fc` |

### 8.3 Hypothesis Tasks Created

**Created:** 4 hypothesis tasks in Pipeline Project

| Hypothesis | Type | Task ID | Feature |
|------------|------|---------|---------|
| H-E1 | EXISTENCE | `a6880300-3c98-4425-a15c-caadc7446ca7` | Hypothesis Verification |
| H-M1 | MECHANISM | `840d70b0-ddbc-45ca-826a-06e4c15f548e` | Hypothesis Verification |
| H-M2 | MECHANISM | `cf8692f8-102c-42ac-8cdf-8b8cfa3a4e27` | Hypothesis Verification |
| H-M3 | MECHANISM | `2d9a0116-688d-42c1-931a-eaa6bd9f631b` | Hypothesis Verification |

**Mapping stored in:** `verification_state.yaml` → `metadata.hypothesis_task_mapping`

---

*Generated by YouRA Phase 2B (v6.0) | 2026-03-24*
