# Hypothesis Context: H-M2

**Generated from:** Phase 2B Verification Plan
**Date:** 2026-07-12
**Main Hypothesis:** RAG-Specific Corpus Curation
**Phase 2B Source:** 02b_verification_plan.md

---

## Hypothesis Information

### Statement
Documents with high factual density and entity coverage improve retrieval performance specifically on semantic queries (BM25-failed) by +4% Recall@10, compared to +1% improvement on lexical queries (BM25-succeeded), because high-density documents contain information in multiple phrasings and higher informativeness per token.

### Type
MECHANISM (Step 2 of 4)

### Rationale
Demonstrates that quality improvement is semantic (meaning-based), not just lexical coverage. Differential gains validate retrieval-specific utility beyond keyword matching.

---

## Verification Protocol

### Conceptual Test
1. Split Natural Questions into Lexical (answer in BM25 top-10) vs Semantic (answer not in BM25 top-10) query subsets
2. Measure Recall@10 improvement (retrieval filter - perplexity baseline) for each subset separately
3. Compare ΔRecall_semantic vs ΔRecall_lexical to validate differential gain
4. Analyze query-document match patterns (multi-phrasing evidence)

### Success Criteria
- **Primary:** ΔRecall_semantic ≥ 0.04 AND ΔRecall_lexical ≤ 0.01 (differential gain ≥3pp)
- **Secondary:** Evidence of multi-phrasing in high-density documents

### Variables
- **Independent Variable:** Document factual density (from H-M1 classifier selection)
- **Dependent Variable:** Recall@10 improvement on semantic vs lexical query subsets
- **Controlled Variables:** Query split methodology (BM25 top-10 baseline), corpus size

---

## Experimental Setup (from Phase 2A via Phase 2B)

### Selected Dataset
- **Name:** BEIR Natural Questions (test set)
- **Type:** standard
- **Source:** BEIR benchmark (Thakur et al., 2021)
- **Path:** beir/nq
- **Hypothesis Fit:** Natural Questions is factoid QA with extractive answers, ideal for controlled validation of retrieval utility. Test set size (~3.5K queries) sufficient for statistical power. Derived from Wikipedia, likely well-covered in Common Crawl.

### Selected Model
- **Name:** DPR (Dense Passage Retriever)
- **Type:** Dense retrieval (bi-encoder)
- **Source:** facebook/dpr-question_encoder-single-nq-base, facebook/dpr-ctx_encoder-single-nq-base
- **Hypothesis Fit:** DPR is standard dense retrieval architecture widely used for RAG. Pre-trained on Natural Questions, ensuring reader model is well-calibrated for the task. Bi-encoder design allows indexing filtered corpora without retraining.

---

## Baseline & Comparison Targets

### Baseline Methods
- Perplexity-based filtering (Common Crawl, 600B tokens)
- FineWeb-Edu educational filtering (+5.0pp MMLU, +4.5pp ARC)
- DataComp-LM model-based filtering (7B model to 64% MMLU)

### Baseline Performance
FineWeb-Edu shows +5.0pp gains on knowledge-intensive tasks; if retrieval filtering achieves comparable Recall@10 gains (≥3%), demonstrates retrieval-specific quality dimension.

### Gap Analysis
This hypothesis tests if high-density documents specifically improve semantic retrieval (BM25-failed queries) more than lexical retrieval, validating that quality is meaning-based, not just keyword coverage.

---

## Dependencies and Gate Conditions

### Prerequisites
- H-M1 (Classifier learns factual density via stratified training)

### Gate Information
**Gate Type:** SHOULD_WORK

**Consequence if Fails:** If gains are uniform (ΔRecall_semantic ≈ ΔRecall_lexical), quality is just lexical coverage → EXPLORE alternative quality metrics

**Phase Assignment:** Phase 2 (Mechanisms)

**Estimated Duration:** 1 week

---

## Dependency Context

### Relationship to Other Hypotheses
H-M2 depends on H-M1 (requires factual density validation). It validates the mechanism by which high-density documents improve retrieval: semantic understanding, not just lexical matching.

---

## Verification State Reference

**State File:** verification_state.yaml
**Current Status:** IN_PROGRESS
**Workflow Status:** ACTIVE

---

## Phase 2C Usage Notes

This context file provides:
1. Complete hypothesis specification for experiment design
2. Gate conditions (SHOULD_WORK)
3. Dependency on H-M1 for factual density validation
4. Success criteria: ΔRecall_semantic ≥ 0.04, ΔRecall_lexical ≤ 0.01
5. Baseline comparison targets (perplexity-based, educational filtering)

Phase 2C will:
1. Search for query splitting implementations (BM25 baseline)
2. Find semantic vs lexical retrieval evaluation patterns
3. Design controlled experiment using H-M1 classifier output
4. Output: docs/youra_research/h-m2/02c_experiment_brief.md
