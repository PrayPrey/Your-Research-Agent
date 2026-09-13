# Hypothesis Context: H-M1

**Date:** 2026-07-12
**Hypothesis ID:** h-m1
**Type:** MECHANISM (Step 1 of 4)
**Status:** IN_PROGRESS

---

## Hypothesis Statement

Under stratified training (oversampling low-educational, high-BEIR examples), the retrieval-quality classifier learns to identify documents with high factual density and entity coverage, as evidenced by classifier-selected documents showing ≥15% higher named entity density than perplexity-matched controls.

---

## Rationale

Validates that stratified training explicitly targets retrieval-pretraining divergence by forcing the classifier to learn quality signals independent of educational fluency.

---

## Variables

- **Independent:** Stratified training strategy (oversample low-educational, high-BEIR)
- **Dependent:** Named entity density (entities per 100 tokens), Type-token ratio
- **Controlled:** Corpus sample size, FastText architecture, training epochs

---

## Verification Protocol

1. Train classifier on stratified BEIR examples (explicit low-educational, high retrieval stratification)
2. Apply classifier to Common Crawl sample and select top-50K documents
3. Compute named entity density (spaCy NER) for classifier-selected vs perplexity-matched control set
4. Measure type-token ratio and other informativeness metrics
5. Statistical test: paired t-test comparing density distributions

---

## Success Criteria

- **Primary:** Entity density_retrieval ≥ entity density_perplexity × 1.15 (15% improvement)
- **Secondary:** Type-token ratio shows similar improvement pattern

---

## Gate Condition

- **Type:** SHOULD_WORK
- **Condition:** Entity density ≥ 1.15× baseline
- **If Fail:** Classifier did not learn retrieval-specific signals → PIVOT to different training strategy or feature engineering

---

## Dependencies

- **Prerequisites:** H-E1 (if retrieval filtering shows no Recall improvement, this mechanism is moot)
- **H-E1 Status:** COMPLETED (PASSED)
- **H-E1 Results:** Recall@10 improvement: +0.05 (baseline: 0.47, proposed: 0.52, delta: +10.6%)

---

## Experimental Setup (from Phase 2B)

### Dataset
- **Name:** BEIR Natural Questions (test set)
- **Type:** Standard benchmark
- **Source:** beir/nq
- **Size:** ~3.5K queries
- **Task:** Factoid QA with extractive answers

### Model
- **Type:** Dense retrieval (bi-encoder)
- **Architecture:** DPR (Dense Passage Retriever)
- **Source:** facebook/dpr-question_encoder-single-nq-base, facebook/dpr-ctx_encoder-single-nq-base
- **Justification:** Pre-trained on Natural Questions, ensuring reader model is well-calibrated for the task

---

## Source

Phase 2A Section 1.3, Causal Step 1
Phase 2B Verification Plan, Section 2.2, H-M1 specification
