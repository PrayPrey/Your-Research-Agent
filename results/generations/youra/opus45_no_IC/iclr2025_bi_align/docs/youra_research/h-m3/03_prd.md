# Product Requirements Document: H-M3

**Hypothesis:** Lower Delta Signals Accommodation
**Date:** 2026-08-10
**Type:** MECHANISM
**Budget Tier:** FULL (30 tasks max)

---

## Executive Summary

H-M3 tests whether small formality deltas between human and AI messages correlate with higher conversation continuation rates. This validates the accommodation-as-attentiveness mechanism in the main hypothesis chain.

**Core Question:** Does low |human_formality - AI_formality| predict user continuation?

---

## Problem Statement

H-M2 established AI formality correlates with human formality (r=0.152). H-M3 must now test whether this accommodation (small delta) signals attentiveness and motivates continuation.

**Success Metric:** Lowest delta tercile has highest continuation rate with monotonic trend.

---

## Functional Requirements

### FR-1: Data Loading and Preparation
- **FR-1.1:** Load Anthropic/hh-rlhf dataset from HuggingFace
- **FR-1.2:** Filter conversations with ≥2 turns per side
- **FR-1.3:** Parse Human/Assistant turn structure
- **FR-1.4:** Extract (human_i, AI_i) turn pairs

### FR-2: Formality Scoring
- **FR-2.1:** Load DeBERTa formality ranker (s-nlp/deberta-large-formality-ranker)
- **FR-2.2:** Score all human turns with formality values [-1, 1]
- **FR-2.3:** Score all AI turns with formality values [-1, 1]
- **FR-2.4:** Cache scores for reuse (leverage H-M2 cache if available)

### FR-3: Delta Computation
- **FR-3.1:** Compute absolute formality delta per turn pair: |human_formality - ai_formality|
- **FR-3.2:** Store delta with conversation_id for clustering

### FR-4: Continuation Labeling
- **FR-4.1:** Define continuation: 1 if human sends next turn, 0 if conversation ends
- **FR-4.2:** Label each (human, AI) pair with continuation flag

### FR-5: Tercile Analysis
- **FR-5.1:** Compute tercile boundaries at 33.33% and 66.67% percentiles
- **FR-5.2:** Assign each sample to tercile (T1=low delta, T2=mid, T3=high delta)
- **FR-5.3:** Calculate continuation rate per tercile
- **FR-5.4:** Verify monotonic trend: rate(T1) > rate(T2) > rate(T3)

### FR-6: Statistical Validation
- **FR-6.1:** Compute Spearman correlation (delta vs continuation)
- **FR-6.2:** Implement cluster bootstrap for robust p-value (n_boot=2000)
- **FR-6.3:** Report both naive and cluster-corrected p-values

### FR-7: Visualization
- **FR-7.1:** Generate tercile continuation rates bar chart (MANDATORY)
- **FR-7.2:** Generate delta distribution histogram with tercile boundaries
- **FR-7.3:** Generate scatter plot: delta vs continuation with trend line
- **FR-7.4:** Save all figures to h-m3/figures/

---

## Non-Functional Requirements

### NFR-1: Performance
- Process ~111K conversation pairs efficiently
- Bootstrap with 2000 iterations must complete within 10 minutes

### NFR-2: Reproducibility
- Random seed: 42
- All results must be deterministic with fixed seed

### NFR-3: Memory
- Handle full dataset in memory or use batched processing
- Cache formality scores to avoid recomputation

---

## Success Criteria (Gate Conditions)

| Criterion | Target | Measurement |
|-----------|--------|-------------|
| Monotonic Trend | T1 > T2 > T3 | Continuation rates comparison |
| Direction | T1 rate > T3 rate | Low delta → high continuation |
| Statistical Significance | p_robust < 0.05 | Cluster-corrected p-value |
| Sample Size | n ≥ 10,000 | Full dataset analysis |

---

## Dependencies

### From H-M2
- Dataset: Anthropic/hh-rlhf (same)
- Model: s-nlp/deberta-large-formality-ranker (same)
- Formality scores: Can reuse cached scores

### External
- scipy.stats for Spearman correlation
- numpy for array operations
- matplotlib for visualization

---

## Out of Scope

- Model training (statistical analysis only)
- Alternative engagement proxies (response time, thumbs up)
- Cross-model analysis
- Multiple dataset validation

---

## Appendix: Expected Output

```
Tercile Analysis Results:
- T1 (low delta): continuation_rate = X.XX%
- T2 (mid delta): continuation_rate = X.XX%
- T3 (high delta): continuation_rate = X.XX%
- Monotonic: True/False
- Spearman rho: -X.XXX (negative = low delta → high continuation)
- p_robust: X.XXXX
- Gate: PASS/FAIL
```
