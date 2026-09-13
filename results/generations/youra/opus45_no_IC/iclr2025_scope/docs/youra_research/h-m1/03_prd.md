# Product Requirements Document: H-M1

**Date:** 2026-08-10
**Hypothesis:** Early attention entropy reflects task structure - entropy variance across tasks exceeds within-category variance
**Type:** MECHANISM
**Gate:** MUST_WORK (F-test p < 0.05)

---

## Executive Summary

Validate whether early attention entropy (first 100 tokens) discriminates between LongBench task types. This tests the causal mechanism underlying H-E1's task clusters by measuring if attention patterns encode task-relevant information.

---

## Problem Statement

H-E1 established k*=3 task clusters exist in compression response profiles. This hypothesis tests whether attention entropy provides a computable signal that correlates with these clusters, enabling a potential routing mechanism.

---

## Functional Requirements

### FR-1: Data Loading
- Load LongBench dataset (21 tasks, 6 categories)
- Sample 10 examples per task (210 total)
- Tokenize with Llama-2 tokenizer, truncate to 100 tokens

### FR-2: Model Setup
- Load Llama-2-7B-hf with `output_attentions=True`
- FP16 precision, device_map="auto"
- Extract attention from all 32 layers × 32 heads

### FR-3: Entropy Computation
- Compute Shannon entropy per attention head
- Formula: H = -Σ p(x) log p(x) over attention distribution
- Output: (n_samples, 32 layers, 32 heads) tensor

### FR-4: Statistical Analysis
- Compute task-level mean entropy (aggregate per task)
- Group tasks by LongBench category (6 groups)
- Run one-way ANOVA (F-test) comparing between-task vs within-category variance

### FR-5: Visualization
- Entropy heatmap: 21 tasks × 32 layers
- Category boxplot: entropy distribution per category
- F-statistic visualization with p < 0.05 threshold line

### FR-6: Gate Evaluation
- PASS if F-test p-value < 0.05
- FAIL otherwise → trigger PIVOT action

---

## Non-Functional Requirements

- **NFR-1:** GPU memory < 16GB (A100 compatible)
- **NFR-2:** Runtime < 1 hour
- **NFR-3:** Reproducible (seed=42 for sampling)

---

## Success Criteria

| Metric | Threshold | Type |
|--------|-----------|------|
| F-test p-value | < 0.05 | GATE (MUST_WORK) |
| Effect size (η²) | > 0.10 | Secondary |
| Runtime | < 60 min | NFR |

---

## Data Specifications

### Input Dataset
- **Name:** LongBench
- **Source:** THUDM/LongBench (HuggingFace)
- **Tasks:** 21 tasks across 6 categories
- **Samples:** 10 per task (210 total for statistical power)

### Task Categories (from LongBench)
1. Single-Doc QA: narrativeqa, qasper, multifieldqa_en, multifieldqa_zh
2. Multi-Doc QA: hotpotqa, 2wikimqa, musique, dureader
3. Summarization: gov_report, qmsum, multi_news, vcsum
4. Few-shot: trec, triviaqa, samsum, lsht
5. Synthetic: passage_count, passage_retrieval_en, passage_retrieval_zh
6. Code: lcc, repobench-p

---

## Dependencies

- **Prerequisites:** H-E1 PASSED (k*=3 clusters)
- **Artifacts:** h-e1/cluster_labels.json (for correlation analysis)
- **Libraries:** transformers, datasets, scipy, torch, numpy, matplotlib

---

## Risks and Mitigations

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Entropy uniform across tasks | Medium | PIVOT to alternative features (head sparsity) |
| Memory overflow | Low | Batch processing, gradient checkpointing disabled |
| Numerical instability | Low | Add eps=1e-10 to entropy computation |

---

*Generated for Phase 3 Implementation Planning*
