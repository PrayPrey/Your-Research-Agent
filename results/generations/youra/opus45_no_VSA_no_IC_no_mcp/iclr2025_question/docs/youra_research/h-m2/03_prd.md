# Product Requirements Document: H-M2 Consistency-Stability Link

**Hypothesis ID:** h-m2
**Type:** MECHANISM
**Gate:** MUST_WORK
**Generated:** 2026-08-28
**Phase:** 3 - Implementation Planning

---

## 1. Executive Summary

Validate the mechanistic hypothesis that N-sample consistency captures generation stability: when the model's sampling process is unstable for a question, different runs yield semantically divergent answers, and this instability correlates with factual incorrectness.

**Success Criteria:**
- Mean consistency (incorrect) < Mean consistency (correct)
- Cohen's d > 0.2 (small but detectable effect)

---

## 2. Problem Statement

H-E1 established that token entropy and N-sample consistency individually predict factual correctness. H-M2 investigates the **mechanism** behind consistency's predictive power: does low consistency reflect generation instability that indicates hallucination?

**Research Question:** Does generation stability (measured by N-sample consistency) mechanistically distinguish correct from incorrect/hallucinated responses?

---

## 3. Functional Requirements

### FR1: Data Reuse from H-E1
- **Input:** h-e1 generated responses (N=5 per TruthfulQA question)
- **Input:** h-e1 computed consistency scores
- **Input:** Ground truth correctness labels
- **Priority:** P0 (Critical)

### FR2: Correctness Labeling
- Label each response as correct (0) or incorrect/hallucinated (1)
- Use TruthfulQA best_answer vs incorrect_answers for labeling
- **Priority:** P0 (Critical)

### FR3: Distribution Analysis
- Partition consistency scores by correctness label
- Compute mean consistency for correct responses
- Compute mean consistency for incorrect responses
- **Priority:** P0 (Critical)

### FR4: Effect Size Calculation
- Compute Cohen's d effect size
- Compute pooled standard deviation
- Report 95% confidence interval
- **Priority:** P0 (Critical)

### FR5: Statistical Testing
- Perform independent samples t-test
- Report p-value and statistical significance
- **Priority:** P1 (High)

### FR6: Visualization
- Generate box plot / violin plot comparing distributions
- Generate histogram overlay by correctness
- Save to h-m2/figures/
- **Priority:** P1 (High)

---

## 4. Non-Functional Requirements

### NFR1: Computational Efficiency
- Analysis should complete in < 5 minutes on standard hardware
- No GPU required (analysis only, no inference)

### NFR2: Reproducibility
- Fixed random seeds where applicable
- All results reproducible from h-e1 artifacts

### NFR3: Statistical Rigor
- Use full TruthfulQA generation split (817 questions)
- No arbitrary subsampling

---

## 5. Data Specifications

| Attribute | Value |
|-----------|-------|
| Dataset | TruthfulQA (generation split) |
| Sample Size | 817 questions |
| Model | LLaMA-2-7B (inference from h-e1) |
| Responses per Question | 5 |
| Total Responses | 4,085 |

**Reused Artifacts from H-E1:**
- `h-e1/outputs/generated_responses.json`
- `h-e1/outputs/consistency_scores.json`
- `h-e1/outputs/correctness_labels.json`

---

## 6. Success Criteria

| Metric | Target | Threshold |
|--------|--------|-----------|
| Direction | mean(incorrect) < mean(correct) | Required |
| Effect Size (Cohen's d) | > 0.2 | Minimum |
| P-value | < 0.05 | Statistical significance |

**PoC Pass Condition:**
1. Code runs without error
2. Direction correct (incorrect < correct)
3. Cohen's d > 0.2

---

## 7. Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| H-E1 Validation | COMPLETED | Prerequisite satisfied |
| H-E1 Artifacts | Available | Generated responses, consistency scores |
| TruthfulQA | Standard | HuggingFace datasets |

---

## 8. Out of Scope

- New model inference (reuse h-e1)
- Alternative consistency metrics (future work)
- Cross-dataset validation (future work)
- Training or fine-tuning

---

## 9. Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Effect size too small | PIVOT to alternative metric (BERTScore) |
| H-E1 artifacts missing | Re-run h-e1 pipeline |
| Statistical power insufficient | Full dataset ensures adequate power |

---

*Generated for Phase 3 Implementation Planning*
*Next: Architecture Design*
