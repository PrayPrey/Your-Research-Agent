# Verification Plan: Calibration-Mediated Correlation Between Factuality and Robustness

**Date:** 2026-08-18
**Hypothesis ID:** H-CalibRobust-v1
**Confidence:** 0.75
**Total Hypotheses:** 4

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement

Under the scope of open-weight LLMs evaluated on word-level adversarial perturbations, if a model exhibits higher factuality error detection accuracy (TruthfulQA MC1), then it will demonstrate higher adversarial robustness (1 - ASR on TextFooler), because calibration quality (lower ECE) provides a shared internal signal that enables both error detection and robustness.

### 1.2 Alternative Hypothesis (H0)

There is no significant correlation (r < 0.3) between factuality error detection accuracy (TruthfulQA MC1) and adversarial robustness (1 - ASR) after controlling for model scale. Calibration does not mediate any observed relationship.

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | TruthfulQA + SST-2 (standard) | TruthfulQA measures factuality; SST-2 provides classification task for adversarial attack |
| **Model** | Multiple open-weight models (LLM family comparison) | Diverse architectures allow testing generalizability of correlation |

**Dataset Details:**
- Source: HuggingFace Datasets
- Path: truthful_qa, sst2

**Model Details:**
- Type: LLM family comparison
- Source: HuggingFace Model Hub
- Models: Llama-2 (7B/13B/70B), Llama-3 (8B/70B), Mistral-7B (v0.1/Instruct), FLAN-T5 (base/large/xl), Phi-2, Phi-3-mini

### 1.4 Baseline Methods (for Phase 5 comparison)

| Method | Performance | Dataset |
|--------|-------------|---------|
| ARES error detection | 72.1% Macro-F1 | Reasoning chains |
| FactSelfCheck | 35.5% factual improvement | Fact-level verification |
| SPOC self-correction | +8.8-20% accuracy | Reasoning tasks |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | ECE reliably measures calibration quality across models and datasets | Standard metric in calibration literature (Guo et al., 2017) | Mediation analysis invalid; need alternative calibration metric |
| A2 | TruthfulQA MC1 captures factuality-related error detection capability | TruthfulQA designed specifically to test truthfulness | Need different benchmark for error detection construct |
| A3 | TextFooler ASR represents meaningful adversarial robustness | Standard benchmark in adversarial NLP literature | Findings may not generalize to other perturbation types |
| A4 | Correlation represents meaningful relationship, not spurious confound | Within-family analysis controls for training data; scale regression controls for capacity | Hidden confound explains correlation without calibration mechanism |
| A5 | Open-weight models are representative of LLMs generally | Diverse architectures (encoder-decoder, decoder-only) | Findings may not generalize to proprietary models |

### 1.6 Research Gap & Novelty

**Preserved Novelty:** First empirical framework connecting factuality benchmarks to robustness metrics via calibration.

**Key Innovation:** Calibration-mediation hypothesis unifying three separate research literatures (factuality, calibration, adversarial robustness).

**Differentiation:**
- Error detection literature (ARES, FactSelfCheck): We correlate detection accuracy with robustness, not just measure detection
- Adversarial robustness literature (TextFooler): We connect robustness to internal calibration, not just attack success
- Calibration literature (Minderer et al.): We show calibration predicts both factuality AND robustness jointly

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

---
**H-E1: Factuality-Robustness Correlation Exists**

**Type:** EXISTENCE
**Statement:** Under evaluation of 12+ open-weight LLMs, if we measure both TruthfulQA MC1 accuracy and adversarial robustness (1-ASR), then a statistically significant positive correlation (r > 0.5, p < 0.05) exists, because both metrics reflect underlying model reliability.

**Rationale:** This establishes the foundational claim that the behavioral correlation exists before investigating mechanism. Without demonstrating correlation, mechanism investigation is premature.

**Variables:**
- Independent: Model identity (12+ models across 4 families)
- Dependent: TruthfulQA MC1 accuracy, 1-ASR on TextFooler
- Controlled: Benchmark versions, evaluation framework (lm-eval-harness)

**Verification Protocol:**
1. Run TruthfulQA MC1 on all 12+ models using lm-evaluation-harness (full test set: 817 questions)
2. Apply TextFooler attack to SST-2 classification (1000+ samples per model)
3. Compute Pearson correlation with bootstrap 95% CI
4. Verify correlation holds within model families (Llama, Mistral, etc.)
5. Control for log(params) via partial correlation

**Success Criteria (PoC: Direction-based):**
- Primary: r > 0.5 with p < 0.05
- Secondary: Bootstrap 95% CI excludes r = 0.3

**Failure Response:**
- IF r < 0.3: ABANDON - hypothesis fundamentally wrong
- IF 0.3 < r < 0.5: PIVOT - weaker correlation, investigate confounds

**Dependencies:** None (foundation)

**Source:** Phase 2A SH1, Prediction P1

---
**H-M1: Calibration Produces Reliable Uncertainty**

**Type:** MECHANISM
**Statement:** Under measurement of ECE across models, if a model has lower ECE (better calibration), then its confidence scores are more aligned with actual accuracy, because calibration by definition measures confidence-accuracy alignment.

**Rationale:** First step of causal chain. Establishes that ECE captures meaningful calibration differences across models, prerequisite for mediation claims.

**Variables:**
- Independent: Model identity
- Dependent: ECE (10 equal-frequency bins)
- Controlled: Temperature (T=1.0 default), bin count (10)

**Verification Protocol:**
1. Extract logprobs from TruthfulQA predictions for all models
2. Compute ECE with 10 equal-frequency bins
3. Validate ECE spread across models (expect 0.02-0.15 range)
4. Correlate ECE with model accuracy to verify calibration concept

**Success Criteria (PoC: Direction-based):**
- Primary: ECE variance > 0.001 across models (meaningful spread)
- Secondary: ECE negatively correlates with accuracy (expected relationship)

**Failure Response:**
- IF ECE variance near zero: PIVOT to alternative calibration metric (Brier score)

**Dependencies:** H-E1

**Source:** Phase 2A Causal Step 1

---
**H-M2: Calibration Enables Error Detection**

**Type:** MECHANISM
**Statement:** Under the scope of models with varying calibration, if a model has lower ECE, then it achieves higher TruthfulQA MC1 accuracy, because well-calibrated confidence allows the model to "know when it's wrong."

**Rationale:** Second step of causal chain. Tests whether calibration predicts factuality performance specifically.

**Variables:**
- Independent: ECE (model-level)
- Dependent: TruthfulQA MC1 accuracy
- Controlled: Model scale (log params)

**Verification Protocol:**
1. Compute ECE and MC1 for all models (data from H-E1, H-M1)
2. Run regression: MC1 ~ ECE + log(params)
3. Test whether ECE coefficient is significant (p < 0.05)
4. Compute partial correlation controlling for scale

**Success Criteria (PoC: Direction-based):**
- Primary: Negative ECE coefficient (lower ECE = higher MC1)
- Secondary: ECE explains additional variance beyond scale (delta R² > 0.05)

**Failure Response:**
- IF ECE coefficient positive or non-significant: Document limitation, proceed to H-M3

**Dependencies:** H-M1

**Source:** Phase 2A Causal Step 2

---
**H-M3: Calibration Mediates Detection-Robustness Relationship**

**Type:** MECHANISM
**Statement:** Under Baron-Kenny mediation analysis, if ECE is included as mediator between model identity and both metrics, then indirect effect accounts for >30% of total correlation, because calibration is the shared internal signal enabling both capabilities.

**Rationale:** Core mechanism test. Demonstrates calibration is not merely correlated but actually mediates the relationship.

**Variables:**
- Independent: Model identity (proxy: factuality score)
- Mediator: ECE
- Dependent: Adversarial robustness (1-ASR)
- Controlled: Model scale

**Verification Protocol:**
1. Run Baron-Kenny mediation: MC1 → ECE → (1-ASR)
2. Compute direct effect (c') and indirect effect (a*b)
3. Calculate mediation percentage: (a*b) / (a*b + c')
4. Run Sobel test for indirect effect significance

**Success Criteria (PoC: Direction-based):**
- Primary: Mediation percentage > 30%
- Secondary: Sobel test p < 0.05

**Failure Response:**
- IF mediation < 10%: ABANDON mechanism claim
- IF 10% < mediation < 30%: Document partial mediation

**Dependencies:** H-M2

**Source:** Phase 2A Causal Step 3, Prediction P2

---

## 3. Execution

### 3.1 Dependency Chain
```
H-E1 → H-M1 → H-M2 → H-M3
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | r > 0.5, p < 0.05 | STOP - reassess hypothesis |
| H-M1 | MUST_WORK | ECE variance > 0.001 | PIVOT to alternative metric |
| H-M2 | SHOULD_WORK | ECE coefficient negative | Document limitation |
| H-M3 | SHOULD_WORK | Mediation > 30% | Document partial support |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 1: Foundation | H-E1 | 2 weeks |
| Phase 2: Mechanisms | H-M1, H-M2, H-M3 | 3 weeks |

**Total Duration:** 5 weeks

---

## 4. Risk Analysis

### 4.1 Risk-Assumption Mapping

| Risk | Source | Affected Hypotheses | Severity |
|------|--------|---------------------|----------|
| R1: ECE unreliable across architectures | A1 | H-M1, H-M2, H-M3 | High |
| R2: TruthfulQA doesn't capture error detection | A2 | H-E1, H-M2 | High |
| R3: TextFooler not representative of robustness | A3 | H-E1, H-M3 | Medium |
| R4: Spurious correlation from confounds | A4 | H-E1, H-M3 | High |
| R5: Open-weight models not generalizable | A5 | All | Medium |

### 4.2 Mitigation Strategies

**R1: ECE Measurement Reliability**
- Prevention: Use equal-frequency bins (more stable than equal-width)
- Detection: Compare ECE with Brier score as sanity check
- Response: PIVOT to Brier score if ECE shows inconsistent behavior

**R2: Benchmark Validity**
- Prevention: Use established TruthfulQA benchmark with published baselines
- Detection: Compare with HaluEval as secondary validation
- Response: SCOPE reduction to specific question types if MC1 problematic

**R3: Attack Generalization**
- Prevention: Document scope limitation explicitly
- Detection: Spot-check with BERT-Attack on subset
- Response: Acknowledge limitation in conclusions

**R4: Confound Control**
- Prevention: Within-family analysis, scale regression
- Detection: Check if correlation disappears with controls
- Response: Report partial correlation results alongside raw

**R5: Generalization Scope**
- Prevention: Include diverse architectures (encoder-decoder, decoder-only)
- Detection: Check consistency across families
- Response: Explicitly scope claims to open-weight models

### 4.3 Risk Summary

| ID | Risk | Severity | Likelihood | Mitigation |
|----|------|----------|------------|------------|
| R1 | ECE unreliable | High | Medium | Alternative metric ready |
| R2 | Benchmark validity | High | Low | Secondary benchmark |
| R3 | Attack generalization | Medium | Medium | Explicit scope |
| R4 | Spurious correlation | High | Medium | Multiple controls |
| R5 | Model generalization | Medium | Low | Diverse families |

**Critical Risks:** 2 (R1, R4)
**High Risks:** 1 (R2)
**Medium Risks:** 2 (R3, R5)

---

## 5. Dependency Graph (DAG) & Timeline

### 5.1 Dependency Visualization

```
═══════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) - 4 Hypotheses
═══════════════════════════════════════════════════════════

[Level 0 - Root]
    H-E1 (Existence - no dependencies)
         │
         ▼
[Level 1 - Mechanism Step 1]
    H-M1 ← H-E1
         │
         ▼
[Level 2 - Mechanism Step 2]
    H-M2 ← H-M1
         │
         ▼
[Level 3 - Mechanism Step 3]
    H-M3 ← H-M2

═══════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M2 → H-M3
═══════════════════════════════════════════════════════════
```

### 5.2 Gantt Timeline

```
═══════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE - 4 Hypotheses
═══════════════════════════════════════════════════════════════════
Phase/Hypothesis    │ W1-2     │ W3       │ W4       │ W5       │
────────────────────┼──────────┼──────────┼──────────┼──────────┤
PHASE 1: Foundation │          │          │          │          │
  H-E1              │ ████████ │          │          │          │
  [Gate 1]          │        ◆ │          │          │          │
────────────────────┼──────────┼──────────┼──────────┼──────────┤
PHASE 2: Mechanisms │          │          │          │          │
  H-M1              │          │ ████     │          │          │
  H-M2              │          │          │ ████     │          │
  H-M3              │          │          │          │ ████     │
  [Gate 2]          │          │          │          │        ◆ │
═══════════════════════════════════════════════════════════════════
Legend: ████ = Active work | ◆ = Gate decision point
Total Duration: 5 weeks
═══════════════════════════════════════════════════════════════════
```

### 5.3 Critical Path Analysis

**Critical Path:** H-E1 → H-M1 → H-M2 → H-M3
**Total Duration:** 5 weeks (2 + 1 + 1 + 1)
**Slack Available:** 0 weeks (all sequential)

### 5.4 Resource Summary

- Total Hypotheses: 4
  - Existence: 1 (H-E1)
  - Mechanism: 3 (H-M1, H-M2, H-M3)
- Verification Phases: 2 (Foundation, Mechanisms)
- Execution Mode: Sequential chain
- Compute Requirements: 12+ model evaluations, ~1000 adversarial samples each

---

## 6. Dialectical Analysis

### 6.1 Thesis

**Core Claim:** Factuality error detection accuracy positively correlates with adversarial robustness in open-weight LLMs, mediated by calibration quality.

**Supporting Evidence:**
1. Calibration determines model reliability (Minderer et al., 2021)
2. Error detection relies on confidence signals (SPOC, ARES)
3. Adversarial inputs should trigger uncertainty in calibrated models

**Strengths:**
- Unifies three separate research literatures
- Clear causal mechanism with testable steps
- Multiple quantified success criteria

**Expected Outcomes:**
- Primary: r > 0.5 correlation between MC1 and 1-ASR
- Secondary: >30% mediation through ECE
- Tertiary: Temperature scaling improves both metrics

### 6.2 Antithesis

**Null Hypothesis (H0):** No significant correlation (r < 0.3) exists between factuality and robustness after controlling for scale. Calibration does not mediate the relationship.

**Counter-Arguments:**
1. Scale dominates: Larger models are simply better at everything
2. Training data quality confounds: Both metrics reflect data, not calibration
3. Architecture effects: Transformer variants differ independently of calibration

**Potential Failure Points:**
- H-E1: Correlation disappears with scale control
- H-M1: ECE shows no meaningful variation
- H-M3: Mediation effect is negligible (<10%)

**Conditions Under Which H0 Would Be Supported:**
- r < 0.3 after controlling for log(params)
- ECE coefficient non-significant in regression
- Mediation percentage < 10%

### 6.3 Synthesis

**Balanced Assessment:**
The hypothesis H-CalibRobust-v1 presents a testable claim that calibration serves as a shared internal signal enabling both factuality and robustness. However, the null hypothesis raises valid concerns about confounds (scale, training data, architecture).

**Resolution Path:**
1. **Foundation verification (H-E1):** Establishes existence with confound controls
2. **Sequential mechanism testing (H-M1-3):** Tests causal chain step-by-step
3. **Gate conditions:** Allow early detection of H0 support

**Conditions for Thesis Support:**
- H-E1 passes (r > 0.5 with controls)
- H-M1 passes (ECE varies meaningfully)
- H-M3 passes (>30% mediation)

**Conditions for Antithesis Support:**
- H-E1 fails (r < 0.3 with controls)
- H-M1 fails (ECE invariant)
- H-M3 fails (mediation < 10%)

**Nuanced Outcome Possibilities:**
1. **Full Support:** All hypotheses pass → Thesis validated
2. **Partial Support:** H-E1 passes, H-M3 weak → Correlation exists, mechanism uncertain
3. **No Support:** H-E1 fails → Antithesis supported

### 6.4 Robustness Assessment

| Aspect | Thesis Position | Antithesis Challenge | Resolution |
|--------|-----------------|----------------------|------------|
| Existence | Correlation r > 0.5 | May be artifact of scale | H-E1 with scale control |
| Mechanism | ECE mediates | Alternative explanations | H-M1-3 sequential tests |
| Scope | Generalizes to open-weight | Limited to specific models | Multiple families |
| Performance | Actionable for practitioners | Marginal improvement | Phase 5 comparison |

**Overall Robustness Score:** Medium-High
**Confidence in Verification Plan:** 0.75

---

## 7. Executive Summary & Conclusions

### 7.1 Executive Summary

**Main Hypothesis:** Calibration-mediated correlation between factuality and robustness in LLMs
- ID: H-CalibRobust-v1, Confidence: 0.75

**Verification Structure:**
- Mode: Incremental (Phase 2A available)
- Sub-Hypotheses: 4 total (H-E: 1, H-M: 3)
- Phases: 2 phases over 5 weeks
- Critical Gates: 2 decision points (Gate 1: foundation, Gate 2: mechanism)

**Risk Assessment:** Medium
- Primary concerns: ECE reliability (R1), spurious correlation (R4)

**Immediate Action:** Begin Phase 1 with H-E1 correlation analysis

### 7.2 Key Achievements

- 4 hypotheses across 2 phases designed
- H0 explicitly addressed via dialectical analysis
- Gate conditions defined for each hypothesis

### 7.3 Verification Execution Order

**Phase 1: Foundation** (2 weeks)
- H-E1: Establish r > 0.5 correlation
- Gate 1: MUST PASS

**Phase 2: Core Mechanisms** (3 weeks)
- H-M1: Verify ECE variance
- H-M2: Test ECE → MC1 relationship
- H-M3: Mediation analysis
- Gate 2: H-M1 must pass

### 7.4 Critical Decision Points

1. **Gate 1 (Foundation):** H-E1 must pass
   - FAIL → STOP, reassess hypothesis
   - PASS → Proceed to Phase 2

2. **Gate 2 (Mechanisms):** H-M1 must pass
   - CRITICAL FAIL → Execute failure response (PIVOT)
   - OPTIONAL FAIL → Document limitation

### 7.5 Open Questions

- Does correlation extend to distributional robustness?
- Do findings generalize to proprietary models (GPT-4, Claude)?
- Can training-time interventions improve both metrics?

### 7.6 Recommendations

1. **Immediate Actions:**
   - Start Phase 1 with H-E1
   - Set up lm-evaluation-harness and TextAttack

2. **Resource Allocation:**
   - Allocate 5 weeks for critical path
   - Reserve 1 week buffer for failures

3. **Failure Management:**
   - Document all failures
   - Execute PIVOT strategies (Brier score for ECE)

---

## Appendices

### A. Phase 2A Reference
- **Source:** 03_refinement.yaml (ID: H-CalibRobust-v1)
- **Scope Reduction:** 60% (BUILD_ON claims not re-verified)

### B. MCP Tool Usage Summary
- **Total MCP calls:** 2
- **Tools:** scientificmethod (hypothesis validation)

### C. Established Facts (BUILD_ON - Not Re-Verified)
1. Architecture determines calibration properties (Minderer et al., 2021)
2. Error detection methods achieve high accuracy (ARES 72.1% F1)
3. Self-correction mechanisms improve accuracy 8-20% (SPOC)

---

*Generated by Phase 2B Planning Workflow*
*Status: Complete*
*Steps Completed: step-00 through step-10*
