# Product Requirements Document: H-E1

**Date:** 2026-08-28
**Hypothesis:** H-E1 - Dose-Response Curation
**Type:** EXISTENCE (PoC)

---

## 1. Objective

Validate that at least one curation parameter (perplexity threshold or deduplication stringency) exhibits non-monotonic (concave) dose-response relationship with benchmark ensemble score at 125M scale.

## 2. Success Criteria

| Criterion | Metric | Threshold |
|-----------|--------|-----------|
| Primary | AIC model selection | Quadratic/cubic preferred over linear (ΔAIC < -2) |
| Secondary | Peak location | Within parameter range (not at boundary) |
| Completion | Configurations run | 15/15 without error |

## 3. Scope

### In Scope
- Perplexity threshold sweep (10 levels: none, p10-p90)
- Deduplication stringency sweep (5 levels at fixed p50)
- GPT-2 125M training from scratch (15 runs × 10B tokens)
- Benchmark ensemble evaluation (HellaSwag, ARC-Easy, PIQA, WinoGrande)
- Polynomial regression analysis with AIC/BIC model selection

### Out of Scope
- Multiple seeds (PoC uses single seed=42)
- Scale experiments beyond 125M
- Alternative quality signals
- Hyperparameter tuning

## 4. Technical Requirements

### 4.1 Data Pipeline
- **Dataset:** RedPajama-v2 (English, streaming)
- **Quality Signal:** ccnet_perplexity field
- **Deduplication:** MinHash via text-dedup library
- **Tokenization:** GPT-2 BPE (50257 vocab)
- **Sequence Length:** 1024 tokens
- **Training Volume:** 10B tokens per configuration

### 4.2 Model Training
- **Architecture:** GPT-2 125M (12L, 768H, 12A)
- **Optimizer:** AdamW (β1=0.9, β2=0.95, wd=0.1)
- **LR:** 6e-4 peak, cosine decay, 2000 warmup steps
- **Batch Size:** 512 sequences (524k tokens/batch)
- **Training:** ~19,000 steps per configuration

### 4.3 Evaluation
- **Library:** lm-evaluation-harness
- **Tasks:** hellaswag, arc_easy, piqa, winogrande
- **Metric:** PC1 ensemble score from individual accuracies

### 4.4 Analysis
- Polynomial regression (degree 1-3)
- AIC/BIC model selection
- Peak identification with confidence intervals

## 5. Deliverables

| Artifact | Description |
|----------|-------------|
| 15 checkpoints | Trained models per configuration |
| benchmark_results.json | Evaluation scores per configuration |
| figures/dose_response_perplexity.png | Primary result figure |
| figures/dose_response_dedup.png | Deduplication effect figure |
| 04_validation.md | Analysis and conclusion |

## 6. Resource Estimate

- **GPU Hours:** ~75 hours (15 configs × 5h each @ A100)
- **Storage:** ~50GB (checkpoints + tokenized data)
- **Compute:** Single A100 80GB sufficient

## 7. Constraints

- Single seed only (PoC scope)
- No hyperparameter tuning across configs
- Fixed training duration (10B tokens)

## 8. Dependencies

- RedPajama-v2 dataset access (HuggingFace)
- lm-evaluation-harness
- text-dedup library
- GPU compute (A100 recommended)

---

*Next: Phase 3 architecture/logic/config documents*
