# Product Requirements Document: H-M1 Semantic Similarity Analysis

## Overview

**Hypothesis:** Mode 3 response pairs have lower semantic similarity than Mode 1 response pairs (Cohen's d > 0.3)

**Objective:** Validate mechanism that RM-human disagreement (Mode 3) correlates with semantic divergence in response pairs.

## Scope

### In Scope
- Load h-e1 mode classifications and response pairs
- Compute sentence embeddings using MiniLM-L6-v2
- Calculate pairwise cosine similarity per battle
- Compare Mode 1 vs Mode 3 similarity distributions
- Statistical analysis: Welch's t-test + Cohen's d

### Out of Scope
- New RM scoring (reuse h-e1)
- Alternative embedding models (post-hoc sensitivity only)
- Mode 2/4 analysis

## Functional Requirements

### FR-1: Data Loading
- Load h-e1 outputs: `rm_scores.parquet`, `mode_distribution.json`
- Filter to Mode 1 and Mode 3 samples
- Validate n >= 500 per mode

### FR-2: Embedding Computation
- Use sentence-transformers/all-MiniLM-L6-v2
- Encode response_a and response_b texts
- Batch processing (64-128 samples)
- Cache to `embeddings.npz`

### FR-3: Similarity Calculation
- Cosine similarity per (response_a, response_b) pair
- Store in `similarity_scores.parquet`

### FR-4: Statistical Analysis
- Split similarities by mode
- Welch's t-test (unequal variance)
- Cohen's d with 95% CI (bootstrap)
- Save to `statistical_results.json`

## Non-Functional Requirements

### Performance
- Total runtime < 60 min (GPU) or < 15 min (CPU)
- Memory < 8GB RAM

### Reproducibility
- Fixed random seed for bootstrap
- Deterministic embedding (same input = same output)

## Success Criteria

| Metric | Threshold |
|--------|-----------|
| Cohen's d | > 0.3 (Mode 1 > Mode 3 similarity) |
| p-value | < 0.05 |

## Dependencies

- h-e1 validation outputs (Mode 3 = 23.7% confirmed)
- sentence-transformers library
- scipy for statistics

## Output Deliverables

1. `embeddings.npz` - Cached embeddings
2. `similarity_scores.parquet` - Per-battle similarity with mode labels
3. `statistical_results.json` - Cohen's d, CI, p-value
4. `04_validation.md` - Analysis report
