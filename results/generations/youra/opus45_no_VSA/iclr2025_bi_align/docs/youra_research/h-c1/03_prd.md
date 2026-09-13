# Product Requirements Document: H-C1 Semantic Coherence Analysis

**Date:** 2026-08-08
**Hypothesis:** H-C1 (CONDITION)
**Author:** Anonymous
**Base Hypothesis:** H-M2 (PARTIAL - 11.77% disagreement rate)

---

## Executive Summary

Validate that disagreement cases (high-BAI/low-reward slice) are semantically coherent, with majority exhibiting interpretable agency-preserving patterns (clarifying, deferring, hedging) rather than noise or verbosity artifacts. This CONDITION hypothesis determines whether H-M2's disagreement findings represent meaningful agency behaviors or statistical artifacts.

---

## Problem Statement

H-M2 found 11.77% disagreement rate between BAI and reward scores (4932 samples). The dominant quadrant was high-BAI/low-reward (3063 samples). But are these responses actually exhibiting agency-preserving behaviors, or are they long/verbose responses that happen to score high on surface-level agency proxies? This hypothesis clusters the disagreement slice semantically to verify interpretable agency patterns dominate.

---

## Functional Requirements

### FR-1: Disagreement Slice Loading
- Load H-M2 disagreement samples (~4932 total)
- Primary source: `h-m2/disagreement_samples.json` (if saved)
- Fallback: Recompute from HH-RLHF/RewardBench with BAI/reward quartile filtering
- Extract response text for clustering

### FR-2: Embedding Generation
- Load sentence-transformers model: `all-MiniLM-L6-v2`
- Compute embeddings for all disagreement responses
- Expected shape: (N, 384) where N ≈ 4932

### FR-3: BERTopic Clustering
- Initialize BERTopic with:
  - UMAP: n_neighbors=15, n_components=5, metric="cosine"
  - HDBSCAN: min_cluster_size=50, cluster_selection_method="eom"
  - top_n_words=10 for interpretable topic keywords
- Fit on disagreement slice embeddings
- Extract topic assignments and probabilities

### FR-4: Agency Pattern Classification
- Define agency pattern keywords:
  - **Clarifying**: clarify, understand, mean, asking, question, sure
  - **Deferring**: prefer, choice, decide, up to you, your call, depends
  - **Hedging**: might, perhaps, possibly, could be, uncertain, not sure
  - **Option enumeration**: option, alternatively, or, either, choices, ways
- For each cluster, check if top-10 keywords match ≥2 agency patterns
- Compute agency_pattern_rate = (agency_clusters / total_clusters)

### FR-5: Coverage and Coherence Metrics
- Compute coverage: % samples assigned to non-noise clusters (topic ≠ -1)
- Compute silhouette score on valid clusters
- Target: coverage > 70%, silhouette > 0.0

### FR-6: Mechanism Verification
- Verify ≥3 non-noise topics discovered
- Verify coverage > 50% (majority not noise)
- Verify topic embeddings are semantically distinct (mean pairwise r < 0.9)

### FR-7: Representative Document Extraction
- For each agency-classified cluster, extract 5 representative documents
- Save for human verification in validation report

### FR-8: Visualization
- **Required**: Bar chart comparing agency_pattern_rate vs 50% threshold
- UMAP 2D projection colored by cluster
- Topic word clouds for top-5 clusters
- Cluster size distribution histogram
- Save all figures to h-c1/figures/

---

## Non-Functional Requirements

### NFR-1: Performance
- Full clustering completes in <30 minutes on CPU
- Embedding generation is main bottleneck (~5 min for 5000 samples)

### NFR-2: Reproducibility
- UMAP random_state=42
- HDBSCAN deterministic with fixed seed
- sentence-transformers deterministic inference

### NFR-3: Dependencies
- Python 3.8+
- bertopic, sentence-transformers, umap-learn, hdbscan
- sklearn, matplotlib, numpy
- datasets (for fallback recompute)

### NFR-4: Memory
- Embedding matrix ~15MB for 5000 × 384 floats
- BERTopic internal structures ~100MB
- Total: <500MB RAM

---

## Success Criteria

| Criterion | Target | Gate |
|-----------|--------|------|
| Agency pattern rate > 50% | Hypothesis PASS | SHOULD_WORK |
| Coverage > 70% | Clustering quality | Required |
| Agency pattern rate ∈ [30%, 50%] | PARTIAL result | Mixed interpretability |
| Agency pattern rate < 30% | Hypothesis FAIL | Artifacts dominate |
| Mechanism verification passed | Code correctness | Required |

---

## Dependencies

### From H-M2 (Prerequisite)
- Disagreement samples with BAI/reward scores
- Quadrant labels (HL = high-BAI/low-reward, LH = low-BAI/high-reward)
- Response text strings

### External
- HuggingFace sentence-transformers
- BERTopic library
- UMAP and HDBSCAN libraries

---

## Data Flow

```
H-M2 Disagreement Slice (4932 samples)
                │
                ▼
    [sentence-transformers]
    all-MiniLM-L6-v2
                │
                ▼
        embeddings (N, 384)
                │
                ▼
    ┌───────────┴───────────┐
    │     BERTopic          │
    │  UMAP → HDBSCAN →     │
    │  c-TF-IDF keywords    │
    └───────────┬───────────┘
                │
                ▼
        topics[] + keywords[]
                │
                ▼
    [Agency Pattern Classifier]
    keyword matching against patterns
                │
                ▼
        agency_pattern_rate
```

---

## Out of Scope

- Manual annotation of clusters
- Training custom embedding models
- Cluster labeling via LLM (too expensive)
- Cross-dataset generalization testing
- Causal analysis of why patterns exist
