# Hypothesis Context: H-E1

**Date:** 2026-07-12
**Type:** EXISTENCE
**Status:** IN_PROGRESS

---

## Hypothesis Statement

Under RAG corpus construction from Common Crawl, if a retrieval-quality classifier (trained on stratified BEIR success examples) filters documents, then the resulting 1M-document corpus achieves ≥3% higher Recall@10 on Natural Questions compared to perplexity-based filtering (matched corpus size), because the classifier learns to identify documents with high factual density and entity coverage.

---

## Rationale

This existence hypothesis validates the core claim that retrieval-specific quality signals can be learned and applied to corpus curation. It establishes whether task-specific filtering (retrieval utility) measurably diverges from pretraining-optimal filtering (perplexity).

---

## Variables

**Independent Variable:**
- Filtering Strategy (Perplexity | Educational | Retrieval-Quality)

**Dependent Variable:**
- Recall@10 on BEIR Natural Questions test set (10K queries, DPR indexing)

**Controlled Variables:**
- Corpus Size: 1M documents
- Common Crawl source: 100K sample
- Retrieval Model: DPR

---

## Experimental Setup (from Phase 2B Section 1.3)

### Dataset
- **Selection:** BEIR Natural Questions (test set) (standard)
- **Justification:** Natural Questions is factoid QA with extractive answers, ideal for controlled validation of retrieval utility. Test set size (~3.5K queries) sufficient for statistical power. Derived from Wikipedia, likely well-covered in Common Crawl (addresses coverage assumption).
- **Source:** BEIR benchmark (Thakur et al., 2021)
- **Path:** beir/nq

### Model
- **Selection:** DPR (Dense Passage Retriever)
- **Justification:** DPR is standard dense retrieval architecture widely used for RAG. Pre-trained on Natural Questions, ensuring reader model is well-calibrated for the task. Bi-encoder design allows indexing filtered corpora without retraining.
- **Type:** Dense retrieval (bi-encoder)
- **Source:** facebook/dpr-question_encoder-single-nq-base, facebook/dpr-ctx_encoder-single-nq-base

---

## Verification Protocol

1. Train retrieval-quality FastText classifier on stratified BEIR examples (oversample low-educational, high-retrieval pairs)
2. Apply three filtering methods to Common Crawl 100K sample: Perplexity (GPT-2 threshold), Educational (FineWeb-style), Retrieval-Quality (FastText)
3. Index each 1M-document corpus with DPR (facebook/dpr-ctx_encoder-single-nq-base)
4. Measure Recall@10 on Natural Questions test queries (~3.5K queries from BEIR benchmark)
5. Statistical test: two-tailed t-test (3-5 replications, α=0.05, power=0.80)

---

## Success Criteria (PoC: Direction-based)

**Primary:**
- Recall@10_retrieval ≥ Recall@10_perplexity + 0.03 (absolute), p<0.05

**Secondary:**
- Retrieval filtering also outperforms educational filtering baseline

---

## Gate Condition

**Type:** MUST_WORK (Phase 4 PoC gate)

**Condition:** Recall@10 ≥ baseline + 0.03, p<0.05

**If Fail:** If |ΔRecall@10| < 0.01 or p>0.05, retrieval-specific filtering provides no measurable advantage → ABORT or PIVOT to different quality signals

---

## Prerequisites

None (foundation hypothesis)

---

## Baseline Methods (for Phase 5 comparison)

| Method | Performance | Dataset | Why Insufficient |
|--------|-------------|---------|------------------|
| Perplexity-based filtering | Not RAG-specific; serves as pretraining baseline | Common Crawl (600B tokens) | Optimizes for pretraining fluency, not retrieval utility |
| FineWeb-Edu educational filtering | +5.0pp MMLU, +4.5pp ARC for knowledge tasks | Common Crawl (15T tokens → 1.3T filtered) | Educational quality ≠ retrieval utility; may reject high-perplexity technical docs valuable for factoid retrieval |
| DataComp-LM model-based filtering | 7B model to 64% MMLU with 40% less compute than prior SOTA | 240T token pool → 3.8T DCLM-BASELINE | Optimizes for pretraining; FastText positive/negative examples selected for language modeling quality, not retrieval utility |

**Best Baseline:** FineWeb-Edu shows +5.0pp gains on knowledge-intensive tasks; if retrieval filtering achieves comparable Recall@10 gains (≥3%), demonstrates retrieval-specific quality dimension analogous to educational quality.

---

## Dependencies

This hypothesis is the foundation (Level 0) with no prerequisites. All mechanism hypotheses (H-M1 through H-M4) depend on H-E1's success.

---

*Source: 02b_verification_plan.md Section 2.2 (H-E1)*
