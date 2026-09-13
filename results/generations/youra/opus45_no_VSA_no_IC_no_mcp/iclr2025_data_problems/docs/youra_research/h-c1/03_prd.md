# Product Requirements Document: H-C1

**Date:** 2026-08-28
**Hypothesis:** H-C1 (COMPARISON)
**Statement:** CPDR-optimized curation parameters outperform RedPajama literature defaults by >1% on benchmark ensemble at 125M scale

---

## Executive Summary

This experiment compares CPDR-optimized curation parameters (p50 perplexity threshold, fuzzy_0.85 deduplication) against RedPajama literature defaults (p30 perplexity, exact deduplication) at GPT-2 125M scale. The goal is to demonstrate >1% improvement on a benchmark ensemble (HellaSwag, ARC-Easy, PIQA, WinoGrande).

---

## Problem Statement

RedPajama-v2 provides default curation parameters based on heuristics. Prior hypotheses (H-E1 through H-M3) identified optimal parameters that differ from defaults. This experiment validates whether the CPDR-optimized configuration delivers measurable benchmark improvement.

---

## Functional Requirements

### FR-1: Dataset Preparation
- Load RedPajama-v2 English subset via HuggingFace streaming
- Apply CPDR-optimized curation: p50 perplexity filter + fuzzy_0.85 MinHash dedup
- Apply RedPajama defaults: p30 perplexity filter + exact dedup
- Target: 10B tokens per configuration

### FR-2: Model Training
- Architecture: GPT-2 125M (768 embed, 12 layers, 12 heads)
- Train from scratch with AdamW, lr=6e-4, cosine decay
- Warmup: 2000 steps, batch size: 512, precision: BF16
- Three seeds: 42, 43, 44

### FR-3: Benchmark Evaluation
- Evaluate using lm-evaluation-harness
- Tasks: HellaSwag, ARC-Easy, PIQA, WinoGrande
- Compute ensemble score as mean accuracy
- Zero-shot evaluation

### FR-4: Comparison Analysis
- Compute improvement: CPDR_mean - RP_mean
- Gate condition: improvement > 1%
- Statistical significance with 3 seeds

### FR-5: Visualization
- Bar chart: CPDR vs RedPajama ensemble scores with error bars
- Per-benchmark breakdown grouped bar chart
- Training loss curves for both configurations

---

## Non-Functional Requirements

### NFR-1: Reproducibility
- Fixed random seeds (42, 43, 44)
- Deterministic data loading order
- Version-pinned dependencies

### NFR-2: Efficiency
- BF16 mixed precision training
- Streaming dataset loading
- Checkpoint every 1000 steps

---

## Success Criteria

| Metric | Threshold | Type |
|--------|-----------|------|
| Ensemble Score Improvement | >1% | MUST |
| Statistical Significance | p < 0.05 (if 3 seeds sufficient) | SHOULD |
| Per-benchmark Direction | All 4 tasks improve | SHOULD |

---

## Dependencies

- Prior: H-M3 (optimal parameters identified)
- Data: RedPajama-v2 (HuggingFace Hub)
- Eval: lm-evaluation-harness (EleutherAI)
- Reuse: H-E1/H-M3 training pipeline components

---

## Out of Scope

- Scaling experiments beyond 125M
- Alternative benchmark suites
- Hyperparameter tuning (use established settings)
