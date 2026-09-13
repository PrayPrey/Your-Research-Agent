# Product Requirements Document: H-E1

**Hypothesis:** Benchmarks cluster meaningfully (silhouette > 0.5) based on uncertainty distribution similarity
**Type:** EXISTENCE (PoC)
**Date:** 2026-08-10
**Author:** Anonymous

---

## Executive Summary

Implement benchmark clustering analysis to validate whether LLM uncertainty distributions (semantic entropy) create meaningful clusters across different QA benchmarks. This is the foundation hypothesis for the conditional transfer research program.

**Gate Condition:** Silhouette score > 0.5
**Fail Action:** ABANDON entire verification plan

---

## Problem Statement

Current hallucination detection thresholds are calibrated per-benchmark. If benchmarks cluster by uncertainty distribution similarity, thresholds could transfer within clusters—reducing calibration overhead. This experiment tests whether such clusters exist.

---

## Functional Requirements

### FR-1: Multi-Benchmark Data Loading
- Load 6 QA benchmarks from HuggingFace:
  - TriviaQA (trivia_qa, unfiltered.nocontext) - 1,000 samples
  - NaturalQuestions (natural_questions) - 1,000 samples
  - SQuAD (squad) - 1,000 samples
  - PopQA (akariasai/PopQA) - 1,000 samples
  - HaluEval-QA (pminervini/HaluEval, qa) - 1,000 samples
  - FEVER (fever, v1.0) - 1,000 samples
- Total: 6,000 queries
- Seed: 42 for reproducibility

### FR-2: Response Generation
- Model: Llama-2-7B-hf (meta-llama/Llama-2-7b-hf)
- Per query: Generate 10 responses at temperature=0.7
- Total generations: 60,000
- Cache generations for reproducibility

### FR-3: Semantic Entropy Computation
- Cluster responses via bidirectional entailment (DeBERTa-v3-large NLI)
- Compute semantic entropy per query
- Output: 6 × 1,000 = 6,000 entropy values

### FR-4: Distribution Similarity Analysis
- Fit KDE to each benchmark's entropy distribution
- Compute 6×6 JS-divergence distance matrix
- Verify matrix symmetry and zero diagonal

### FR-5: Hierarchical Clustering
- Apply Ward linkage clustering
- Test cluster counts: 2, 3, 4
- Select best by silhouette score

### FR-6: Gate Metric Evaluation
- Compute silhouette score on best clustering
- **GATE:** silhouette > 0.5 → PASS, else FAIL

### FR-7: Visualization Generation
- JS-divergence heatmap (6×6)
- Clustering dendrogram
- Per-benchmark entropy violin plots
- Silhouette coefficient plot
- Gate metric bar chart (silhouette vs 0.5 threshold)

---

## Non-Functional Requirements

### NFR-1: Reproducibility
- Fixed seed (42) for all random operations
- Generation cache for re-runs
- Version-pinned dependencies

### NFR-2: Compute Efficiency
- GPU: 1× A100 (80GB) or 2× A6000
- Time budget: ~8 hours total
- Storage: ~10GB for generation cache

### NFR-3: Verification Logging
- Log mechanism activation messages
- Save intermediate artifacts (KDEs, distance matrix)

---

## Success Criteria

| Metric | Threshold | Priority |
|--------|-----------|----------|
| Silhouette Score | > 0.5 | **GATE** |
| Cluster Count | 2-4 | Secondary |
| Code Execution | No errors | Required |

---

## Dependencies

### External
- HuggingFace Datasets (datasets)
- HuggingFace Transformers (transformers)
- Llama-2-7B model access (requires agreement)
- DeBERTa-v3-large for NLI

### Internal
- scipy (JS-divergence, hierarchical clustering)
- sklearn (silhouette_score)
- numpy, matplotlib, seaborn

---

## Data Flow

```
[6 Benchmarks] → [LLM Generation] → [NLI Clustering] → [Entropy Computation]
                      ↓
              [KDE per Benchmark] → [JS-Divergence Matrix] → [Hierarchical Clustering]
                                           ↓
                                   [Silhouette Score] → [GATE DECISION]
```

---

## Out of Scope

- Model training or fine-tuning
- Threshold transfer experiments (H-M3/H-M4)
- Mechanism analysis (H-M1/H-M2)
- API-based LLMs (need logits)

---

## Acceptance Criteria

1. All 6 benchmarks loaded with 1,000 samples each
2. 60,000 generations completed and cached
3. 6,000 entropy values computed
4. 6×6 JS-divergence matrix computed and validated
5. Silhouette score computed and compared to 0.5 threshold
6. All visualizations generated to h-e1/figures/
7. Gate decision documented in 04_validation.md
