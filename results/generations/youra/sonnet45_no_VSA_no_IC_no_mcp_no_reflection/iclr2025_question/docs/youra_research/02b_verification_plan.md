# Verification Plan: Single-Pass Distribution Entropy for Selective Prediction

**Date:** 2026-08-28
**Hypothesis ID:** H-EntropySelectivePrediction-v1
**Confidence:** 0.80
**Total Hypotheses:** 4

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement
Under factual question-answering tasks with single-answer targets, if we apply entropy-based rejection thresholds to frozen LLM predictions, then selective prediction accuracy will exceed max-probability-based rejection, because entropy captures multi-modal distribution uncertainty that max-probability (mode-only) misses.

### 1.2 Alternative Hypothesis (H0)
There is no significant difference in selective prediction performance (coverage-accuracy AUC) between entropy-based and max-probability-based rejection methods.

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | TriviaQA (primary), SQuAD, Natural Questions (standard) | Factual QA with single answers - fits selective prediction use case and scope limitation |
| **Model** | Llama-7B, Llama-13B, Llama-70B | Open models with accessible logprobs, no retraining required, scales tested for generalization |

**Dataset Details:**
- Source: Public benchmarks (HuggingFace Datasets)
- Path: trivia_qa/unfiltered, squad, natural_questions

**Model Details:**
- Type: Autoregressive decoder-only transformer
- Source: Meta AI / HuggingFace

### 1.4 Baseline Methods (for Phase 5 comparison)

| Method | Performance | Dataset |
|--------|-------------|---------|
| Max-probability thresholding | Strong baseline per Hendrycks et al. OOD detection | CIFAR, ImageNet (vision); need to establish for LLM QA |
| Deep ensemble uncertainty | State-of-art but expensive (5-10 models) | Various vision/NLP tasks |
| MC Dropout | Moderate; requires dropout at inference | Various |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | Entropy and max-prob are not perfectly correlated (r < 0.95) | If r ≥ 0.95, signals are redundant - hypothesis fails by design | Entropy adds no information; max-prob is sufficient |
| A2 | Disagreement quadrant Q3 (high max-prob, high entropy) is non-trivial (>5% of predictions) | If Q3 is empty or tiny, phenomenon doesn't generalize | Quadrant analysis is not meaningful; edge case only |
| A3 | Multi-modal uncertainty manifests in top-5 token distributions | Most probability mass concentrates in top-k tokens for LLMs | Top-5 entropy check (P3) may fail even if mechanism is correct |
| A4 | Entropy thresholds can be set to achieve target coverage levels | Entropy is continuous; threshold sweep should span 0-100% coverage | Cannot construct coverage-accuracy curves |
| A5 | Single-answer factual QA is representative of selective prediction use cases | Common deployment scenario (medical QA, fact-checking) | Results do not generalize to other task types (acknowledged scope limitation) |

### 1.6 Research Gap & Novelty

**Key Innovation:** Quadrant analysis framework for entropy-maxprob disagreement; first systematic study of distribution entropy for LLM selective prediction.

**Differentiation:**
- **vs Max-probability baselines:** Shows max-prob misses multi-modal uncertainty; entropy captures it via full distribution shape
- **vs Ensemble methods:** Single forward pass vs multiple models; zero-shot vs training required
- **vs Temperature scaling and calibration:** No calibration set required; entropy from raw distribution vs post-hoc rescaling
- **vs Conformal prediction:** No held-out calibration data; applicable to frozen API models

**Preserved Novelty:** Quadrant analysis framework for identifying where max-prob is high but entropy is also high (Q3) - showing entropy captures missed uncertainty

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| H-E1 | Existence | MUST_WORK | None | READY |
| H-M1 | Mechanism | MUST_WORK | H-E1 | NOT_STARTED |
| H-M2 | Mechanism | MUST_WORK | H-M1 | NOT_STARTED |
| H-M3 | Mechanism | MUST_WORK | H-M2 | NOT_STARTED |

---

### 2.2 Hypothesis Specifications

---
**H-E1: Entropy Signal Accessibility**

**Statement**: Under factual QA with frozen LLMs, if we extract token probability distributions from single forward passes, then entropy signals are measurable and correlate with prediction correctness, because output distributions encode uncertainty through their shape.

**Rationale**: Foundation hypothesis validating that entropy signal exists and is accessible. Without this, subsequent mechanism hypotheses cannot be tested. Tests P1-P3 infrastructure.

**Variables** (from Phase 2A):
- Independent: None (infrastructure)
- Dependent: Entropy extractability, correlation with accuracy
- Controlled: Model family (Llama 7B/13B/70B), Datasets (TriviaQA/SQuAD/NQ)

**Verification Protocol**:
1. Run inference on TriviaQA dev set (~1000 examples), extract logits and compute softmax distributions
2. Calculate Shannon entropy per prediction, verify continuous range (0-log|V|)
3. Compute Spearman correlation between entropy and prediction correctness (binary: correct/incorrect)
4. Verify correlation is significant (p < 0.05) and negative (higher entropy → lower accuracy expected)
5. Confirm quadrant Q3 population >5% (assumption A2 check)

**Success Criteria** (PoC: Direction-based):
- Primary: Entropy signal extractable for >95% of predictions, significant negative correlation with accuracy (p < 0.05)
- Secondary: Q3 population >5%, entropy range spans >50% of theoretical maximum

**Failure Response**:
- IF fails: ABANDON (infrastructure broken, cannot proceed)

**Dependencies**: None (foundation)

**Source**: Phase 2A SH1, Predictions P1-P3

---
**H-M1: Entropy-Error Correlation**

**Statement**: Under factual QA tasks, if we compute distribution entropy, then higher entropy predictions have lower accuracy than lower entropy predictions, because entropy quantifies distribution spread which indicates model uncertainty.

**Rationale**: Validates causal step 2 (distribution shape encodes uncertainty). Establishes that entropy is a meaningful uncertainty signal, not just a computed statistic.

**Variables**:
- Independent: Entropy level (continuous)
- Dependent: Prediction accuracy (binary: correct/incorrect)
- Controlled: Model, dataset, metric (exact match)

**Verification Protocol**:
1. Bin predictions by entropy quartiles (Q1: low entropy, Q4: high entropy)
2. Compute accuracy within each quartile on TriviaQA test set
3. Verify monotonic decrease: Acc(Q1) > Acc(Q2) > Acc(Q3) > Acc(Q4)
4. Statistical test: Paired t-test between Q1 and Q4 accuracy (p < 0.05)

**Success Criteria**:
- Primary: Monotonic accuracy decrease across entropy quartiles
- Secondary: Q1-Q4 accuracy gap >10 percentage points

**Failure Response**:
- IF fails: PIVOT to alternative uncertainty signal

**Dependencies**: H-E1

**Source**: Phase 2A Causal Step 2

---
**H-M2: Multi-Modal Uncertainty Detection**

**Statement**: Under high max-prob scenarios, if entropy is also high (quadrant Q3), then top-5 token distributions are flatter than low-entropy cases (Q1), because multi-modal uncertainty manifests as multiple competitive tokens beyond the mode.

**Rationale**: Validates causal step 3 (max-prob captures mode only, entropy captures full geometry). Tests mechanism explanation for why entropy adds signal beyond max-prob.

**Variables**:
- Independent: Quadrant (Q1: high max-prob low entropy, Q3: high max-prob high entropy)
- Dependent: Top-5 entropy (Shannon entropy over top-5 tokens only)
- Controlled: Model, dataset

**Verification Protocol**:
1. Median-split predictions on max-prob and entropy to create quadrants Q1-Q4
2. Extract top-5 token distributions for each prediction
3. Compute top-5 entropy for Q1 and Q3 separately
4. Paired t-test: Top-5 entropy(Q3) > Top-5 entropy(Q1), p < 0.017 (Bonferroni-corrected)

**Success Criteria**:
- Primary: Top-5 entropy(Q3) significantly higher than Q1 (p < 0.017)
- Secondary: Effect size (Cohen's d) > 0.5

**Failure Response**:
- IF fails: EXPLORE alternative mechanism (tail entropy, normalized entropy)

**Dependencies**: H-M1

**Source**: Phase 2A Causal Step 3, Prediction P3

---
**H-M3: Entropy Rejection Advantage**

**Statement**: Under selective prediction, if we reject high-entropy predictions, then accuracy on retained predictions exceeds max-prob-based rejection, because entropy identifies multi-modal uncertainty that max-prob misses (especially in quadrant Q3).

**Rationale**: Validates causal step 4 (entropy-based rejection outperforms max-prob). Core hypothesis claim - proves entropy adds value for selective prediction beyond existing max-prob baseline.

**Variables**:
- Independent: Rejection method (entropy threshold vs max-prob threshold)
- Dependent: Accuracy at fixed coverage (60%, 70%, 80%, 90%), Coverage-accuracy AUC
- Controlled: Model, dataset, coverage level

**Verification Protocol**:
1. Sweep entropy thresholds to achieve target coverage levels (60/70/80/90%) on TriviaQA
2. Sweep max-prob thresholds to achieve same coverage levels
3. Measure accuracy at each coverage level for both methods
4. Compute coverage-accuracy AUC (0-1 coverage range) for both methods
5. Paired comparison: AUC(entropy) > AUC(max-prob) on all three datasets (TriviaQA/SQuAD/NQ)
6. Quadrant analysis: Verify Q3 accuracy < Q1 accuracy by >5% (p < 0.017)

**Success Criteria**:
- Primary: Q1-Q3 accuracy gap >5% with p < 0.017 (Prediction P1)
- Secondary: AUC(entropy) > AUC(max-prob) on all three datasets (Prediction P2)

**Failure Response**:
- IF fails: EXPLORE conditional application (may work on subset of tasks/models)

**Dependencies**: H-M2

**Source**: Phase 2A Causal Step 4, Predictions P1-P2

---

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
<!-- Format: H-E1 → H-M1 → H-M2 → H-CP1 -->

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | Entropy signal extractable (>95%), significant negative correlation with accuracy (p < 0.05) | ABANDON (infrastructure broken) |
| H-M1 | MUST_WORK | Monotonic accuracy decrease across entropy quartiles, Q1-Q4 gap >10% | PIVOT to alternative uncertainty signal |
| H-M2 | MUST_WORK | Top-5 entropy(Q3) > Top-5 entropy(Q1) with p < 0.017, Cohen's d > 0.5 | EXPLORE alternative mechanism (tail entropy) |
| H-M3 | MUST_WORK | Q1-Q3 accuracy gap >5% (p < 0.017), AUC(entropy) > AUC(max-prob) on all datasets | EXPLORE conditional application |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 3: Experiment Design | H-E1, H-M1, H-M2, H-M3 | 1 week |
| Phase 4: Implementation | H-E1, H-M1, H-M2, H-M3 | 2 weeks |
| Phase 5: Baseline Comparison | All hypotheses | 1 week |
| Phase 6: Analysis & Writing | All hypotheses | 1 week |

**Total Duration:** 5 weeks

---
