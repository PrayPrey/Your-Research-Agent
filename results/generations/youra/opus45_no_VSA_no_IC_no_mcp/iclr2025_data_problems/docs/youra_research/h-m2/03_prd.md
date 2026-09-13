# Product Requirements Document: H-M2

**Hypothesis:** Deduplication stringency affects the memorization-generalization balance: an optimal deduplication level exists between none and strict (exact+fuzzy), measurable via benchmark ensemble score.

**Date:** 2026-08-28
**Type:** MECHANISM
**Gate:** SHOULD_WORK

---

## Executive Summary

This experiment tests whether deduplication stringency exhibits a non-monotonic relationship with downstream benchmark performance. The hypothesis posits that moderate deduplication outperforms both no deduplication and strict deduplication, suggesting an optimal quality-diversity tradeoff exists.

---

## Problem Statement

Over-deduplication may remove beneficial training signal diversity, while under-deduplication allows memorization to inflate apparent performance. Finding the optimal stringency level is critical for LLM data curation pipelines.

---

## Functional Requirements

### FR-1: Data Pipeline with Configurable Deduplication

| Requirement | Specification |
|-------------|---------------|
| Dataset | RedPajama-v2 (10B tokens per configuration) |
| Deduplication levels | 5 levels: none, fuzzy_0.7, fuzzy_0.85, exact, exact_plus_fuzzy |
| Implementation | text-dedup library (MinHash LSH) |
| Output | Deduplicated JSONL per level |

### FR-2: Model Training Pipeline

| Requirement | Specification |
|-------------|---------------|
| Architecture | GPT-2 125M (12 layers, 768 hidden, 12 heads) |
| Training | From scratch on each deduplicated dataset |
| Optimizer | AdamW (β1=0.9, β2=0.95, wd=0.1) |
| LR Schedule | Cosine decay, warmup 2000 steps, peak 6e-4 |
| Batch size | 512 sequences (512K tokens) |
| Total tokens | 10B per configuration |
| Seeds | 3 per configuration |

### FR-3: Evaluation Pipeline

| Requirement | Specification |
|-------------|---------------|
| Benchmarks | HellaSwag, ARC-Easy, PIQA, WinoGrande |
| Framework | lm-evaluation-harness |
| Primary metric | PC1 ensemble score |
| Secondary | Individual benchmark accuracies |

### FR-4: Mechanism Verification

| Requirement | Specification |
|-------------|---------------|
| Verification | Log deduplication stats (removed count, percentage) |
| Validation | Confirm non-trivial removal for non-"none" levels |
| Data stats | Token count, unique docs per level |

### FR-5: Ablation Variants

| Variant | Description |
|---------|-------------|
| none | No deduplication (baseline) |
| fuzzy_0.7 | MinHash Jaccard ≥ 0.7 |
| fuzzy_0.85 | MinHash Jaccard ≥ 0.85 |
| exact | Exact string match only |
| exact_plus_fuzzy | Exact + MinHash 0.85 (strictest) |

---

## Non-Functional Requirements

### NFR-1: Reproducibility
- Fixed random seeds (3 seeds per configuration)
- Deterministic data loading order
- Logged hyperparameters

### NFR-2: Computational Efficiency
- Checkpoint every 1B tokens
- Support resume from checkpoint

### NFR-3: Statistical Rigor
- Report mean ± std across seeds
- Compute effect sizes for key comparisons

---

## Success Criteria

| Criterion | Threshold |
|-----------|-----------|
| Non-monotonic curve | At least one intermediate level outperforms strictest |
| Effect size | >0.5% accuracy difference between optimal and strictest |
| Reproducibility | Consistent pattern across 3 seeds |

---

## Technical Dependencies

| Dependency | Version | Purpose |
|------------|---------|---------|
| text-dedup | latest | Deduplication |
| transformers | 4.x | Model training |
| lm-eval | latest | Benchmark evaluation |
| datasets | 2.x | Data loading |
| torch | 2.x | Training framework |

---

## Data Specifications

### Input
- RedPajama-v2 raw documents (JSONL)
- HuggingFace: `togethercomputer/RedPajama-Data-v2`

### Output
- 5 deduplicated datasets (one per level)
- 15 trained checkpoints (5 levels × 3 seeds)
- Benchmark results JSON
- Figures: dose-response curve, per-benchmark breakdown

---

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Monotonic result | Document as negative finding, explore per-benchmark effects |
| Compute cost | Use 125M model, 10B tokens (manageable scale) |
| Deduplication variance | Use established text-dedup library with tested parameters |
