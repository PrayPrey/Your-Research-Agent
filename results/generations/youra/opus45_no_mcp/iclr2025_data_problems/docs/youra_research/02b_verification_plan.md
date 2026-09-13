# Verification Plan: Semantic Saturation Index for Paraphrase-Resistant Contamination Detection

**Date:** 2026-08-19
**Hypothesis ID:** H-SSI-v1
**Confidence:** 0.80
**Total Hypotheses:** 5

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement

Under standard foundation model evaluation settings, if a model was trained on benchmark items (verbatim or paraphrased), then it will exhibit significantly higher Semantic Saturation Index (SSI = inverse confidence variance across paraphrases) on those items compared to clean models, because training exposure creates robust semantic representations that generalize uniformly across phrasing variations.

### 1.2 Alternative Hypothesis (H0)

There is no significant difference in SSI between clean and contaminated models on the same benchmark items.

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | MMLU (standard) | Standard FM evaluation benchmark with 14K items across 57 subjects |
| **Model** | Mistral-7B | Open-weight model enabling controlled contamination and confidence extraction |

**Dataset Details:**
- Source: https://github.com/hendrycks/test
- Path: public

**Model Details:**
- Type: decoder-only transformer
- Source: https://huggingface.co/mistralai/Mistral-7B-v0.1

### 1.4 Baseline Methods (for Phase 5 comparison)

| Method | Performance | Dataset |
|--------|-------------|---------|
| 13-gram overlap (GPT-3 style) | Fails completely on paraphrased contamination | MMLU |
| DCQ (Data Contamination Quiz) | Partial paraphrase resistance, per-item detection | Various benchmarks |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | Paraphrasers generate sufficiently diverse variations | Multi-method approach (T5, GPT-4, rule-based) + pilot validation | Paraphrase quality confound: variance measures paraphrase naturalness, not contamination |
| A2 | Model confidence is meaningful (calibration) | Use calibrated probabilities, not raw logits | SSI measures overconfidence, not contamination |
| A3 | Effect size detectable at practical contamination levels | Power analysis to determine minimum detectable level | Method only works for extreme contamination (>50%) |
| A4 | Mechanism generalizes across model scales | Test on 7B; validate on 13B if resources allow | Need scale-specific normalization |

### 1.6 Research Gap & Novelty

**Preserved Novelty:** First paraphrase-resistant behavioral contamination metric

**Key Innovation:** SSI exploits paraphrase uniformity as the SIGNAL rather than vulnerability. Instead of trying to match surface forms (which fails on paraphrases), we measure the CONSEQUENCE of paraphrase training — semantic saturation.

**Differentiation:**
- vs 13-gram overlap: SSI detects paraphrased contamination; n-gram only detects verbatim
- vs DCQ: SSI provides continuous metric and scales to full benchmark
- vs Embedding density: SSI uses variance (robust in high-D); density estimation fails in high-D

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| H-E1 | Existence | MUST_WORK | None | READY |
| H-M1 | Mechanism | MUST_WORK | H-E1 | NOT_STARTED |
| H-M2 | Mechanism | SHOULD_WORK | H-M1 | NOT_STARTED |
| H-M3 | Mechanism | SHOULD_WORK | H-M2 | NOT_STARTED |
| H-M4 | Mechanism | SHOULD_WORK | H-M3 | NOT_STARTED |

---

### 2.2 Hypothesis Specifications

---

#### H-E1: SSI Discriminates Contamination Status

**Type:** EXISTENCE
**Statement:** Under standard FM evaluation on MMLU, if SSI is computed for benchmark items, then SSI will differ significantly between clean and contaminated models, because contaminated models exhibit uniform confidence across paraphrases.

**Rationale:**
This is the foundation hypothesis. If SSI cannot discriminate clean from contaminated models, the entire approach fails. Establishes that the phenomenon (paraphrase-invariant confidence) exists and is measurable.

**Variables:**
- Independent: contamination_status (clean vs contaminated)
- Dependent: semantic_saturation_index (SSI = 1/variance)
- Controlled: model_architecture (Mistral-7B), paraphrase_method, K=20

**Verification Protocol:**
1. Fine-tune Mistral-7B variants with 0%, 10%, 50% MMLU contamination
2. Generate K=20 paraphrases per MMLU item using multi-method approach
3. Extract confidence scores on original + paraphrases for each item
4. Compute SSI = 1/variance(confidence) for each item per model
5. Evaluate AUC for binary classification (clean vs contaminated)

**Success Criteria (PoC: Direction-based):**
- Primary: AUC > 0.7 for clean vs contaminated classification
- Secondary: Effect size (Cohen's d) > 0.5

**Failure Response:**
- IF fails: ABANDON — core mechanism invalid

**Dependencies:** None

**Source:** Phase 2A Section 5, SH1

---

#### H-M1: Contamination Injection Creates Training Exposure

**Type:** MECHANISM
**Statement:** Under controlled fine-tuning, if benchmark items are included in training data at known percentages, then the model will demonstrably learn those items, because gradient updates on benchmark items modify model weights toward correct answers.

**Rationale:**
First mechanism step: establishes that our contamination injection procedure actually works. Without verified contamination, we cannot test SSI's detection capability.

**Variables:**
- Independent: contamination_level (0%, 5%, 10%, 20%, 50%)
- Dependent: item-level accuracy on contaminated items
- Controlled: model_architecture, training hyperparameters

**Verification Protocol:**
1. Create 5 Mistral-7B variants with known contamination levels
2. Fine-tune each on specified percentage of MMLU items
3. Measure accuracy on contaminated vs non-contaminated items
4. Verify contaminated items show higher accuracy than baseline

**Success Criteria (PoC):**
- Primary: Contaminated items accuracy > non-contaminated items
- Secondary: Accuracy increases monotonically with contamination level

**Failure Response:**
- IF fails: PIVOT — revise contamination injection procedure

**Dependencies:** H-E1

**Source:** Phase 2A Causal Step 1

---

#### H-M2: Training Develops Robust Semantic Representations

**Type:** MECHANISM
**Statement:** Under diverse training exposure, if a model learns benchmark items in various phrasings, then it will develop representations invariant to surface form, because learning theory predicts that diverse training creates generalized representations.

**Rationale:**
Tests the theoretical mechanism: diverse training should create phrasing-invariant representations. This is the link between contamination and uniform confidence.

**Variables:**
- Independent: training_diversity (verbatim only vs paraphrase-augmented)
- Dependent: representation_similarity across paraphrases (cosine similarity)
- Controlled: model_architecture, total training examples

**Verification Protocol:**
1. Create two contamination conditions: verbatim-only and paraphrase-augmented
2. Extract hidden representations for test items and their paraphrases
3. Compute cosine similarity across paraphrase representations
4. Compare representation invariance between conditions

**Success Criteria (PoC):**
- Primary: Paraphrase-trained models show higher representation similarity across paraphrases
- Secondary: Verbatim-only shows lower similarity (less invariance)

**Failure Response:**
- IF fails: EXPLORE — alternative mechanism (e.g., confidence calibration artifact)

**Dependencies:** H-M1

**Source:** Phase 2A Causal Step 2

---

#### H-M3: Representation Invariance Manifests as Uniform Confidence

**Type:** MECHANISM
**Statement:** Under phrasing-invariant representations, if a model has robust semantic encoding for an item, then it will produce uniform confidence scores across paraphrases of that item, because confident predictions on invariant representations yield consistent outputs.

**Rationale:**
Links representation invariance to the observable signal (confidence uniformity). This step connects the internal mechanism to the measurable SSI metric.

**Variables:**
- Independent: representation_invariance (high vs low similarity)
- Dependent: confidence_variance across paraphrases
- Controlled: model_architecture, paraphrase quality

**Verification Protocol:**
1. Identify items with high vs low representation invariance from H-M2
2. Compute confidence variance for both groups
3. Test correlation between representation similarity and confidence uniformity
4. Verify high-invariance items have lower confidence variance

**Success Criteria (PoC):**
- Primary: Negative correlation (r < -0.4) between representation variance and confidence variance
- Secondary: High-invariance items show confidence variance < low-invariance items

**Failure Response:**
- IF fails: PIVOT — confidence may not reflect representation invariance

**Dependencies:** H-M2

**Source:** Phase 2A Causal Step 3

---

#### H-M4: SSI Captures Invariance as Contamination Signal

**Type:** MECHANISM
**Statement:** Under the SSI formulation (SSI = 1/variance), if confidence variance correlates with contamination, then SSI will serve as a valid contamination metric, because the inverse transform amplifies differences in variance into a usable signal.

**Rationale:**
Final mechanism step: validates that SSI specifically (not just raw variance) provides actionable contamination detection. Closes the causal chain.

**Variables:**
- Independent: contamination_status
- Dependent: SSI values, discrimination_auc
- Controlled: variance_computation method, outlier handling

**Verification Protocol:**
1. Compute SSI for all MMLU items across all model variants
2. Evaluate SSI distribution for clean vs contaminated items
3. Test AUC for contamination classification using SSI
4. Validate monotonic relationship between contamination level and mean SSI

**Success Criteria (PoC):**
- Primary: AUC > 0.7 for SSI-based contamination classification
- Secondary: Pearson r > 0.6 between contamination % and mean SSI

**Failure Response:**
- IF fails: EXPLORE — alternative metric formulation (e.g., entropy-based)

**Dependencies:** H-M3

**Source:** Phase 2A Causal Step 4

---

## 3. Execution

### 3.1 Dependency Chain

```
H-E1 → H-M1 → H-M2 → H-M3 → H-M4
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | AUC > 0.7 | STOP — reassess entire hypothesis |
| H-M1 | MUST_WORK | Contaminated accuracy > baseline | PIVOT contamination procedure |
| H-M2 | SHOULD_WORK | Higher similarity for paraphrase-trained | EXPLORE alternative mechanism |
| H-M3 | SHOULD_WORK | r < -0.4 variance correlation | PIVOT confidence interpretation |
| H-M4 | SHOULD_WORK | AUC > 0.7, r > 0.6 | EXPLORE alternative metric |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 1: Foundation | H-E1 | 2 weeks |
| Phase 2: Mechanisms | H-M1, H-M2, H-M3, H-M4 | 5 weeks |

**Total Duration:** 7 weeks

---

## 4. Risk Analysis

### 4.1 Risk-Assumption Mapping

| Risk | Source | Affected Hypotheses | Severity |
|------|--------|---------------------|----------|
| R1 | A1 (Paraphrase diversity) | H-E1, H-M2, H-M3 | High |
| R2 | A2 (Confidence calibration) | H-E1, H-M3, H-M4 | High |
| R3 | A3 (Effect size at practical levels) | All | Medium |
| R4 | A4 (Scale generalization) | H-M2, H-M4 | Medium |

### 4.2 Mitigation Strategies

**R1: Paraphrase Quality Risk**
- Prevention: Multi-method paraphrase generation (T5, GPT-4, rule-based)
- Detection: Pilot validation of paraphrase diversity metrics
- Response: If failed, add more paraphrase methods or human validation

**R2: Calibration Risk**
- Prevention: Use temperature scaling for calibration
- Detection: Monitor calibration metrics (ECE) during evaluation
- Response: If miscalibrated, apply post-hoc calibration or use rank-based SSI

**R3: Effect Size Risk**
- Prevention: Power analysis before full experiment
- Detection: Early stopping if effect size < 0.3
- Response: If small effect, focus on extreme contamination detection

**R4: Scale Generalization Risk**
- Prevention: Document scale-specific thresholds
- Detection: Test on 13B if 7B results promising
- Response: Develop scale normalization if needed

---

## 5. Dependency Graph & Timeline

### 5.1 Dependency Graph (DAG)

```
═══════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) - 5 Hypotheses
═══════════════════════════════════════════════════════════

[Level 0 - Root]
    H-E1 (Existence - no dependencies)
         │
         ▼
[Level 1-4 - Mechanisms]
    H-M1 ← H-E1
         │
         ▼
    H-M2 ← H-M1
         │
         ▼
    H-M3 ← H-M2
         │
         ▼
    H-M4 ← H-M3

═══════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M2 → H-M3 → H-M4
═══════════════════════════════════════════════════════════
```

### 5.2 Gantt Timeline

```
═══════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE - 5 Hypotheses
═══════════════════════════════════════════════════════════════════
Phase/Hypothesis     │ W1-2 │ W3-4 │ W5   │ W6   │ W7   │
─────────────────────┼──────┼──────┼──────┼──────┼──────┤
PHASE 1: Foundation  │      │      │      │      │      │
  H-E1               │██████│      │      │      │      │
  [Gate 1]           │      │◆     │      │      │      │
─────────────────────┼──────┼──────┼──────┼──────┼──────┤
PHASE 2: Mechanisms  │      │      │      │      │      │
  H-M1               │      │██████│      │      │      │
  H-M2               │      │      │████  │      │      │
  H-M3               │      │      │      │████  │      │
  H-M4               │      │      │      │      │████  │
  [Gate 2]           │      │      │      │      │    ◆ │
═══════════════════════════════════════════════════════════════════
Legend: ████ = Active work | ◆ = Gate decision point
Total Duration: 7 weeks
═══════════════════════════════════════════════════════════════════
```

### 5.3 Critical Path Analysis

- Critical Path: H-E1 → H-M1 → H-M2 → H-M3 → H-M4
- Total Duration: 7 weeks (2 + 2 + 1 + 1 + 1)
- Slack: 0 weeks (all sequential)

---

## 6. Dialectical Analysis

### 6.1 Thesis

**Core Claim:** SSI (Semantic Saturation Index) detects benchmark contamination by measuring confidence uniformity across paraphrases.

**Supporting Evidence:**
1. Learning theory: diverse training creates invariant representations
2. Empirical: contaminated models show uniform confidence
3. Mathematical: SSI = 1/variance captures this uniformity

**Strengths:**
- Behavioral detection bypasses surface-form matching limitations
- Continuous metric enables severity quantification
- Scalable to full benchmarks

### 6.2 Antithesis (from H0)

**Null Hypothesis:** There is no significant difference in SSI between clean and contaminated models.

**Counter-Arguments:**
1. Confidence uniformity may reflect model calibration, not contamination
2. Paraphrase quality variation may dominate over contamination signal
3. Effect may be too small for practical detection thresholds

**Conditions Supporting H0:**
- AUC < 0.6 for SSI-based classification
- Correlation r < 0.4 between contamination level and SSI
- Effect size d < 0.3

### 6.3 Synthesis

The verification plan addresses this dialectic through sequential hypothesis testing:

1. **H-E1** establishes whether the SSI difference exists at all
2. **H-M1-M4** validate each causal link, isolating where the mechanism might fail
3. Gate conditions allow early detection of H0 support

**Resolution Path:**
- Full Support: All gates pass → Thesis validated, SSI is viable
- Partial Support: Some H-M fail → Refined thesis with documented limitations
- No Support: H-E1 or H-M1 fail → H0 supported, abandon SSI approach

### 6.4 Robustness Assessment

| Aspect | Thesis Position | Antithesis Challenge | Resolution |
|--------|-----------------|----------------------|------------|
| Existence | SSI difference exists | May be statistical noise | H-E1 AUC test |
| Mechanism | Invariance causes uniformity | Correlation artifact | H-M2-M3 tests |
| Practicality | Detects real contamination | Only extreme cases | Effect size monitoring |

**Overall Robustness:** Medium-High
**Confidence in Plan:** 0.80

---

## 7. Executive Summary

**Main Hypothesis:** SSI detects contamination via paraphrase confidence uniformity
- ID: H-SSI-v1, Confidence: 0.80

**Verification Structure:**
- Mode: Incremental (Phase 2A available)
- Sub-Hypotheses: 5 total (H-E: 1, H-M: 4)
- Phases: 2 phases over 7 weeks
- Critical Gates: 2 decision points (Gate 1 after H-E1, Gate 2 after H-M4)

**Risk Assessment:** Medium
- Primary concerns: Paraphrase quality (R1), Confidence calibration (R2)

**Immediate Action:** Begin Phase 1 with H-E1

---

## 8. Appendices

### A. Phase 2A Reference
- Source: 03_refinement.yaml (ID: H-SSI-v1)
- Causal Chain Length: 4 steps
- Scope Reduction: 75% (BUILD_ON claims not re-verified)

### B. Experiment Scale Requirements
- Dataset: Full MMLU test set (14,042 items)
- Paraphrases: K=20 per item (280,840 total inferences per model)
- Models: 5 contamination variants (0%, 5%, 10%, 20%, 50%)
- Total forward passes: ~1.4M per evaluation round
