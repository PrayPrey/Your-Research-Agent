# Product Requirements Document: H-M3

**Hypothesis:** Amplification Index (AI) is positive for perplexity filtering vs random (AI > 0, 95% CI excludes zero)
**Type:** MECHANISM
**Date:** 2026-08-08
**Phase 2C Source:** 02c_experiment_brief.md

---

## Executive Summary

H-M3 measures whether perplexity-based data curation disproportionately amplifies performance on contaminated benchmark examples compared to random sampling. This is quantified via the Amplification Index (AI), comparing accuracy differentials between contaminated and clean MMLU subsets across filtering strategies.

**Key Deliverable:** Compute AI with bootstrap 95% CI; gate passes if AI > 0 and CI excludes zero.

---

## Problem Statement

Training data curation may inadvertently increase benchmark contamination effects. If perplexity filtering preferentially retains benchmark-similar examples, models trained on filtered data may show inflated benchmark scores that don't generalize. H-M3 quantifies this amplification effect.

---

## Functional Requirements

### FR-1: Model Loading
Load 15 pre-trained Pythia-1B checkpoints from H-M1:
- `random_seed{1-5}`: Random sampling baseline
- `perplexity_seed{1-5}`: Perplexity-filtered training
- `dedup_seed{1-5}`: Deduplication-filtered training

### FR-2: Benchmark Dataset Preparation
- **MMLU (contaminated)**: Load `cais/mmlu` test split (14,042 questions)
- **MMLU-Redux (clean)**: Load `edinburgh-dawg/mmlu-redux-2.0`, filter to `error_type == "ok"`
- Create contaminated/clean partition masks

### FR-3: MMLU Evaluation
- 5-shot evaluation following standard protocol
- Log-likelihood MCQ scoring
- Batch size: 32, FP16 precision
- Output: per-question correctness array per model

### FR-4: Amplification Index Computation
```python
AI = mean(delta_perplexity) - mean(delta_random)
# where delta = Acc_contaminated - Acc_clean
```

### FR-5: Bootstrap Confidence Interval
- 10,000 bootstrap resamples
- Paired cluster bootstrap (same seed indices)
- Output: 95% CI (2.5th, 97.5th percentiles)

### FR-6: Gate Evaluation
- Pass: AI > 0 AND CI_lower > 0
- Fail: AI ≤ 0 OR CI includes zero

### FR-7: Visualization
- **Required**: AI bar chart with 95% CI error bars
- **Optional**: Accuracy heatmap, delta distributions

---

## Non-Functional Requirements

### NFR-1: Performance
- Inference throughput: Process all 15 models × ~20K questions in < 4 hours on single GPU

### NFR-2: Reproducibility
- Fixed random seeds for bootstrap
- Deterministic evaluation (no dropout)

### NFR-3: Memory
- Peak GPU memory < 16GB (FP16 Pythia-1B)

---

## Success Criteria

| Metric | Threshold | Gate Type |
|--------|-----------|-----------|
| Amplification Index | > 0 | SHOULD_WORK |
| 95% CI Lower Bound | > 0 | SHOULD_WORK |

---

## Dependencies

### Prerequisites
- **H-M1**: Provides 15 trained model checkpoints
- H-M1 validation status: COMPLETED (PARTIAL_PASS)

### External Dependencies
- HuggingFace datasets: `cais/mmlu`, `edinburgh-dawg/mmlu-redux-2.0`
- HuggingFace transformers: model loading

---

## Data Specifications

| Dataset | Source | Split | Size |
|---------|--------|-------|------|
| MMLU | cais/mmlu | test | 14,042 |
| MMLU-Redux 2.0 | edinburgh-dawg/mmlu-redux-2.0 | test | ~5,700 (clean) |

---

## Out of Scope

- New model training (reuses H-M1 models)
- Alternative contamination detection methods (KDS, n-gram overlap)
- MMLU-CF or other clean benchmarks (future work)
