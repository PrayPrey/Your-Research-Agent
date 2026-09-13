# Verification Plan: Calibration-Mediated Correlation Between Truthfulness and Adversarial Robustness

**Date:** 2026-08-28
**Hypothesis ID:** H-CalibCorr-v1
**Confidence:** 0.75
**Total Hypotheses:** 4

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement

Under controlled evaluation conditions (lm-eval-harness, consistent settings), if we measure TruthfulQA MC1 accuracy and AdvGLUE average accuracy across 15+ LLMs from multiple families (Llama, Mistral, Pythia, Falcon), then we will observe a significant positive partial correlation (r > 0.3, p < 0.05) after controlling for model size, because both capabilities rely on accurate uncertainty estimation that calibration enables.

### 1.2 Alternative Hypothesis (H0)

There is no significant partial correlation between TruthfulQA MC1 accuracy and AdvGLUE average accuracy after controlling for model parameter count (|r| < 0.2, p > 0.1).

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | TruthfulQA, AdvGLUE, MMLU (standard) | TruthfulQA measures truthfulness, AdvGLUE measures robustness, MMLU provides neutral ECE calculation |
| **Model** | Multi-family LLM sample | Diverse families and sizes enable correlation analysis |

**Dataset Details:**
- Source: Public benchmarks
- Path: Via lm-evaluation-harness

**Model Details:**
- Type: decoder-only autoregressive
- Source: HuggingFace Hub

### 1.4 Baseline Methods (for Phase 5 comparison)

| Method | Performance | Dataset |
|--------|-------------|---------|
| Uncorrected correlation | Pearson r without controlling for model size | Cross-benchmark |
| Random baseline | Correlation with shuffled labels | Cross-benchmark |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | TruthfulQA and AdvGLUE measure distinct but related trust dimensions | Both require model to handle challenging inputs correctly | If measuring same construct, correlation is trivial |
| A2 | ECE calculated on neutral benchmark (MMLU) reflects general calibration | Standard practice in calibration literature | Task-specific calibration may not generalize |
| A3 | Model size is the primary confounder to control | Larger models generally perform better on both metrics | Other confounders may explain correlation |
| A4 | lm-eval-harness provides comparable evaluations across models | Standard evaluation framework, consistent prompt templates | Evaluation inconsistencies may introduce noise |

### 1.6 Research Gap & Novelty

**Gap:** No prior systematic study examines the correlation between truthfulness (TruthfulQA) and adversarial robustness (AdvGLUE) across LLMs, nor whether calibration mediates this relationship.

**Novelty:** First cross-benchmark correlation analysis linking two trust dimensions through the calibration mechanism, with quantitative verification via partial correlation controlling for model size.

**Differentiation:**
- TruthfulQA (Lin et al. 2022): Evaluated truthfulness only
- AdvGLUE (Wang et al. 2022): Evaluated robustness only
- Calibrate Before Use (Zhao et al. 2021): Showed calibration helps performance, not trust dimension interaction

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| h-e1 | EXISTENCE | MUST_WORK | None | READY |
| h-m1 | MECHANISM | SHOULD_WORK | h-e1 | NOT_STARTED |
| h-m2 | MECHANISM | SHOULD_WORK | h-e1 | NOT_STARTED |
| h-c1 | CONDITION | SHOULD_WORK | h-m1, h-m2 | NOT_STARTED |

---

### 2.2 Hypothesis Specifications

#### h-e1: Correlation Existence

**Type:** EXISTENCE
**Statement:** Under lm-eval-harness evaluation of 15+ decoder-only LLMs, if we compute partial correlation between TruthfulQA MC1 and AdvGLUE average accuracy controlling for log(params), then r > 0.3 with p < 0.05, because model capabilities covary beyond size effects.

**Variables:**
- IV: Model identity (categorical across families)
- DV: Partial correlation coefficient r
- CV: Log-transformed parameter count

**Success Criteria:**
- Partial r > 0.3
- p-value < 0.05
- Bootstrap 95% CI excludes 0

**Gate:**
- Type: MUST_WORK
- If Fail: Main hypothesis rejected; pivot to alternative explanations

**Prerequisites:** None

**Verification Protocol:**
1. Collect TruthfulQA MC1, AdvGLUE avg, and param count for 15-20 models
2. Log-transform parameter counts
3. Compute partial Pearson correlation
4. Bootstrap 1000 iterations for CI
5. Report r, p, and CI bounds

---

#### h-m1: Calibration Correlates with Both Metrics

**Type:** MECHANISM
**Statement:** Under MMLU-based ECE measurement, if models have lower ECE (better calibration), then they achieve higher TruthfulQA MC1 AND higher AdvGLUE accuracy, because calibration enables both truthful responses and robust detection.

**Variables:**
- IV: ECE (15-bin, on MMLU)
- DV: TruthfulQA MC1, AdvGLUE avg
- CV: Model parameter count

**Success Criteria:**
- Negative correlation: ECE vs TruthfulQA (r < -0.2)
- Negative correlation: ECE vs AdvGLUE (r < -0.2)
- Both p < 0.10

**Gate:**
- Type: SHOULD_WORK
- If Fail: Calibration not explanatory; seek alternative mechanisms

**Prerequisites:** h-e1 (existence confirmed)

**Verification Protocol:**
1. Compute 15-bin ECE on MMLU for each model
2. Correlate ECE with TruthfulQA MC1
3. Correlate ECE with AdvGLUE avg
4. Control for model size in partial correlations
5. Report both correlation coefficients

---

#### h-m2: Calibration Moderates Correlation Strength

**Type:** MECHANISM
**Statement:** Under ECE tertile stratification, if we compare TruthfulQA-AdvGLUE correlation within low-ECE vs high-ECE groups, then low-ECE group shows stronger correlation, because calibration mediates the relationship.

**Variables:**
- IV: ECE tertile (low/mid/high)
- DV: Within-group correlation coefficient
- CV: Model parameter count

**Success Criteria:**
- Low-ECE tertile r > High-ECE tertile r
- Fisher's z-test p < 0.10

**Gate:**
- Type: SHOULD_WORK
- If Fail: Calibration does not moderate; correlation may be spurious

**Prerequisites:** h-e1 (existence confirmed)

**Verification Protocol:**
1. Split models into ECE tertiles
2. Compute TruthfulQA-AdvGLUE correlation within each tertile
3. Apply Fisher's z-test between low and high tertiles
4. Report z-statistic and p-value

---

#### h-c1: Base vs Instruction-Tuned Consistency

**Type:** CONDITION
**Statement:** Under model type stratification, if we separate base models from instruction-tuned variants, then both subgroups show positive TruthfulQA-AdvGLUE correlation (r > 0.2), because the relationship is fundamental rather than training-artifact.

**Variables:**
- IV: Model type (base/instruction-tuned)
- DV: Within-group correlation
- CV: Model parameter count

**Success Criteria:**
- Base models: r > 0.2
- Instruction-tuned: r > 0.2
- Pattern consistent across both (same sign)

**Gate:**
- Type: SHOULD_WORK
- If Fail: Relationship may be instruction-tuning artifact

**Prerequisites:** h-m1, h-m2 (mechanism hypotheses)

**Verification Protocol:**
1. Label each model as base or instruction-tuned
2. Compute within-group partial correlations
3. Compare correlation coefficients
4. Report whether pattern is consistent

---

## 3. Execution

### 3.1 Dependency Chain
```
h-e1 → [h-m1, h-m2] → h-c1
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| h-e1 | MUST_WORK | r > 0.3, p < 0.05 | REJECT main hypothesis |
| h-m1 | SHOULD_WORK | Both correlations r < -0.2 | Seek alternative mechanism |
| h-m2 | SHOULD_WORK | Fisher z p < 0.10 | Calibration not mediator |
| h-c1 | SHOULD_WORK | Both groups r > 0.2 | Pattern may be artifact |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 1 | h-e1 | 2-3 days |
| Phase 2 | h-m1, h-m2 (parallel) | 2-3 days |
| Phase 3 | h-c1 | 1-2 days |

**Total Duration:** 5-8 days

---

## 4. Risk Analysis

### 4.1 Key Risks

| Risk ID | Description | Probability | Impact | Mitigation |
|---------|-------------|-------------|--------|------------|
| R1 | Sample size (N~20) insufficient for reliable correlation | Medium | High | Maximize model diversity; use bootstrap CI |
| R2 | AdvGLUE subtask heterogeneity masks signal | Medium | Medium | Analyze subtasks separately as sensitivity |
| R3 | ECE measurement noisy due to MMLU subset selection | Low | Medium | Use full MMLU validation set |
| R4 | Model family confounds (Llama variants similar) | Medium | Medium | Weight families equally in analysis |

### 4.2 Risk-Hypothesis Mapping

| Hypothesis | Primary Risks | Mitigation Applied |
|------------|---------------|-------------------|
| h-e1 | R1, R4 | Bootstrap CI, family diversity |
| h-m1 | R1, R3 | Multiple ECE calculations |
| h-m2 | R1, R2 | Tertile analysis robust to outliers |
| h-c1 | R1, R4 | Report confidence intervals |

---

## 5. Dependency Graph (DAG)

```
                    ┌─────────┐
                    │  h-e1   │ ← MUST_WORK (Entry Gate)
                    │EXISTENCE│
                    └────┬────┘
                         │
            ┌────────────┼────────────┐
            │            │            │
            ▼            │            ▼
       ┌─────────┐       │       ┌─────────┐
       │  h-m1   │       │       │  h-m2   │
       │MECHANISM│       │       │MECHANISM│
       │ (ECE↔   │       │       │(Moderat-│
       │ metrics)│       │       │  ion)   │
       └────┬────┘       │       └────┬────┘
            │            │            │
            └────────────┼────────────┘
                         │
                         ▼
                    ┌─────────┐
                    │  h-c1   │
                    │CONDITION│
                    │(Base vs │
                    │  Inst)  │
                    └─────────┘
```

### Execution Order

1. **Phase 1:** h-e1 (MUST pass before proceeding)
2. **Phase 2:** h-m1 || h-m2 (parallel execution)
3. **Phase 3:** h-c1 (requires mechanism results)

---

## 6. Dialectical Analysis

### 6.1 Thesis

Calibration serves as a common cause enabling both truthfulness and adversarial robustness in LLMs. Models with better uncertainty estimation (lower ECE) can:
- Refuse to assert false claims (truthfulness)
- Detect anomalous adversarial inputs (robustness)

This predicts a positive correlation between TruthfulQA and AdvGLUE scores that strengthens with better calibration.

### 6.2 Antithesis (H0 Defense)

The observed correlation may be:
1. **Spurious via model quality:** Better models excel at everything; no specific calibration mechanism
2. **Confounded by training data:** Models trained on more diverse data perform better on both benchmarks
3. **Measurement artifact:** Both benchmarks may inadvertently measure similar surface features

### 6.3 Synthesis

The verification plan addresses these objections:
- **h-e1** controls for model size (primary quality proxy)
- **h-m1/h-m2** directly test calibration's role rather than assuming it
- **h-c1** checks whether pattern holds across training paradigms

If calibration is merely correlated with model quality without causal role, h-m2 (moderation test) should fail.

### 6.4 Robustness Assessment

| Objection | Sub-hypothesis Addressing | Expected Resolution |
|-----------|--------------------------|---------------------|
| Model quality confounder | h-e1 (partial correlation) | Control removes effect |
| Calibration not causal | h-m2 (moderation test) | Stratified analysis reveals mechanism |
| Training artifact | h-c1 (base vs instruction) | Consistency across types |

---

## 7. Executive Summary

### Key Points

1. **4 sub-hypotheses** decompose the main claim into testable components
2. **h-e1 is critical gate:** Must demonstrate r > 0.3 correlation to proceed
3. **Mechanism hypotheses (h-m1, h-m2)** test calibration's explanatory role
4. **Condition hypothesis (h-c1)** validates generality across model types

### Execution Order

```
h-e1 (MUST_WORK) → [h-m1 || h-m2] (SHOULD_WORK) → h-c1 (SHOULD_WORK)
```

### Success Criteria Summary

- **Full Success:** h-e1 + h-m1 + h-m2 + h-c1 all pass
- **Partial Success:** h-e1 passes, some mechanism tests inconclusive
- **Failure:** h-e1 fails (main hypothesis rejected)

### Estimated Timeline

5-8 days for complete verification cycle

---

*Generated by Phase 2B Planning Workflow*
*Next: Phase 2C Experiment Design for h-e1*
