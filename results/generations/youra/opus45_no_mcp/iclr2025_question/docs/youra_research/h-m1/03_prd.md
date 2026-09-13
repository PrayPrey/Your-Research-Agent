# Product Requirements Document: H-M1

**Date:** 2026-08-19
**Author:** PrayPrey
**Hypothesis:** H-M1 - Entropy-Correctness Correlation
**Type:** MECHANISM
**Gate:** MUST_WORK

---

## Executive Summary

Validate that token entropy from Llama-2-7B-chat correlates with answer correctness on TriviaQA. Higher entropy should indicate uncertainty and predict incorrect answers.

---

## Problem Statement

H-E1 confirmed entropy is computable (mean: 0.1224, std: 0.0395). Now test whether this signal predicts correctness - the first mechanism validation for the complementary hallucination detection thesis.

---

## Functional Requirements

### FR-1: Response Generation
- Generate 10 responses per question using Llama-2-7B-chat
- Temperature: 0.7, Top-p: 0.9, Max tokens: 128
- Extract logits for entropy computation
- Reuse H-E1 validated generation pipeline

### FR-2: Entropy Computation
- Compute token-level entropy: H = -Σ p(t) log p(t)
- Average across generated tokens
- Store per-question entropy values

### FR-3: Correctness Evaluation
- Compare generated answer to TriviaQA ground truth
- Use normalized exact match (lowercase, strip)
- Match against all answer aliases
- Label each question as correct/incorrect

### FR-4: Statistical Analysis
- t-test: Compare entropy distributions (correct vs incorrect)
- AUROC: Predictive power of inverted entropy
- Effect size: Cohen's d
- Store results in structured format

### FR-5: Visualization
- Gate metrics bar chart (AUROC target vs actual)
- Entropy distribution histograms by correctness
- ROC curve with confidence band

---

## Data Requirements

### Dataset: TriviaQA (rc.nocontext)
- **Source:** HuggingFace (mandarjoshi/trivia_qa)
- **Split:** Validation (~11,313 questions)
- **Fields:** question, answer.aliases
- **Preprocessing:** Skip empty answers, normalize text

---

## Model Requirements

### Baseline Model
- **Model:** meta-llama/Llama-2-7b-chat-hf
- **Loading:** HuggingFace Transformers, float16, device_map="auto"
- **Requirement:** Logit access for entropy computation

---

## Evaluation Metrics

### Primary (Gate Criteria)
| Metric | Target | Failure Action |
|--------|--------|----------------|
| t-test p-value | < 0.05 | STOP |
| Direction | mean_incorrect > mean_correct | STOP |
| AUROC | > 0.55 | STOP |

### Secondary
- Cohen's d effect size
- Pearson correlation
- Accuracy rate

---

## Dependencies

### From H-E1 (Prerequisite)
- `entropy_module.py`: compute_entropy()
- `response_generator.py`: generate_responses()
- Validated entropy range: [0.03, 0.18]

---

## Success Criteria

**PoC PASS requires ALL:**
1. Code executes on full validation set (~11K questions)
2. t-test p-value < 0.05
3. mean_incorrect_entropy > mean_correct_entropy
4. AUROC > 0.55

**If PASS:** Proceed to H-M2 (consistency mechanism)
**If FAIL:** STOP - entropy signal not predictive

---

## Non-Functional Requirements

- **Runtime:** < 8 hours for full evaluation
- **Memory:** < 24GB GPU (single A100)
- **Output:** Structured JSON + figures

---

## Output Files

| File | Description |
|------|-------------|
| 04_validation.md | Results report |
| figures/gate_metrics.png | AUROC bar chart |
| figures/entropy_distribution.png | Histograms |
| figures/roc_curve.png | ROC curve |
