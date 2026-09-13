# Product Requirements Document: H-M1

**Hypothesis:** CCR is higher for perplexity-filtered training than random-sampled training (CCR difference > 0.1, p<0.05 bootstrap)
**Type:** MECHANISM
**Date:** 2026-08-08
**Gate:** MUST_WORK
**Prerequisites:** H-E1 (VALIDATED)

---

## Executive Summary

Demonstrate causal relationship between data filtering strategy and benchmark contamination by comparing CCR across perplexity-filtered, random-sampled, and inverse-perplexity corpus variants trained on Pythia-1B.

---

## Problem Statement

Need to establish:
1. Perplexity-based filtering affects contamination propagation differently than random sampling
2. Low-perplexity (high quality) corpora have higher CCR than random baselines
3. Effect size is statistically significant under bootstrap resampling

---

## Functional Requirements

### FR-1: Data Preparation

- **FR-1.1:** Load RedPajama-Data-V2 (English, head_middle partition, snapshot 2023-14)
- **FR-1.2:** Extract `ccnet_perplexity` quality signal from dataset
- **FR-1.3:** Implement perplexity-filtered subset (bottom 30% perplexity = high quality)
- **FR-1.4:** Implement random-sampled subset (uniform random, same size)
- **FR-1.5:** Implement inverse-perplexity subset (top 30% perplexity = low quality, control)
- **FR-1.6:** Match corpus size: ~1B tokens per strategy
- **FR-1.7:** Load MMLU test set (14,042 questions) for injection
- **FR-1.8:** Inject MMLU at rates [0.1%, 0.5%, 1.0%] per H-E1 calibration

### FR-2: Model Training (3 strategies × 5 seeds = 15 runs)

- **FR-2.1:** Initialize Pythia-1B from EleutherAI/pythia-1b
- **FR-2.2:** Train with AdamW (lr=2.5e-4, betas=(0.9, 0.95), eps=1e-8, weight_decay=0.1)
- **FR-2.3:** Use cosine LR schedule with 1% warmup, min_lr=2.5e-5
- **FR-2.4:** Batch size 512 (global), sequence length 2048
- **FR-2.5:** Train on 1B tokens per corpus variant
- **FR-2.6:** Train 5 seeds per strategy for bootstrap CI
- **FR-2.7:** Save final checkpoints for evaluation

### FR-3: Contamination Detection (reuse H-E1 stack)

- **FR-3.1:** Implement 8-gram overlap detection (per ConTAM recommendation)
- **FR-3.2:** Compute CCR per trained model
- **FR-3.3:** Measure CCR across all 15 model variants

### FR-4: Evaluation

- **FR-4.1:** Compute CCR for each (strategy, seed) pair
- **FR-4.2:** Measure MMLU 5-shot accuracy per model
- **FR-4.3:** Implement bootstrap test (1000 resamples)
- **FR-4.4:** Compute CCR(perplexity) - CCR(random) with 95% CI
- **FR-4.5:** Report p-value for CCR difference > 0

### FR-5: Visualization

- **FR-5.1:** CCR by filtering strategy (bar chart with error bars)
- **FR-5.2:** CCR distribution (box plots across 5 seeds per strategy)
- **FR-5.3:** Bootstrap distribution histogram with p-value annotation
- **FR-5.4:** Gate metrics comparison (target vs actual)

---

## Non-Functional Requirements

- **NFR-1:** Multi-GPU training support (8× A100 recommended for 15 runs)
- **NFR-2:** Reproducible with seeds [42, 43, 44, 45, 46]
- **NFR-3:** Total runtime < 72 hours (parallelizable)
- **NFR-4:** Checkpoint storage ~30GB (15 models × 2GB)

---

## Success Criteria

| Metric | Target | Priority |
|--------|--------|----------|
| CCR(ppl) - CCR(rand) | > 0.1 | P0 |
| Bootstrap p-value | < 0.05 | P0 |
| All 15 models trained | Yes | P0 |
| MMLU accuracy measured | All 15 | P1 |

---

## Dependencies

### Libraries
- PyTorch ≥ 2.0, Transformers, Datasets (HuggingFace)
- lm-eval (EleutherAI) for MMLU evaluation
- NumPy, SciPy for bootstrap statistics
- Matplotlib for visualization

### Prerequisite Artifacts
- H-E1 CCR measurement code (validated)
- H-E1 n-gram detection code (validated)

---

## Data Assets

| Asset | Source | Size |
|-------|--------|------|
| Pythia-1B | EleutherAI/pythia-1b | 2GB |
| RedPajama-V2 | togethercomputer/RedPajama-Data-V2 | ~100GB (streaming) |
| MMLU | cais/mmlu | ~50MB |

---

## Experimental Design Summary

| Condition | Corpus | Samples | Seeds |
|-----------|--------|---------|-------|
| Perplexity-filtered | Bottom 30% ccnet_perplexity | 1B tokens | 5 |
| Random-sampled | Uniform random | 1B tokens | 5 |
| Inverse-perplexity | Top 30% ccnet_perplexity | 1B tokens | 5 |

**Total:** 3 conditions × 5 seeds = 15 trained models

---

*Source: Phase 2C Experiment Brief (02c_experiment_brief.md)*
*Prerequisite: H-E1 validated CCR metric stack*
