# Product Requirements Document: H-E1

**Hypothesis:** Task-dependent compression response clusters exist in KV cache compression across LongBench tasks, identifiable via gap statistic showing k* > 1

**Type:** EXISTENCE (PoC)
**Date:** 2026-08-10
**Budget Tier:** LIGHT (max 15 tasks)

---

## Executive Summary

Validate existence of task-dependent compression response structure in LLM KV cache. Run Llama-2-7B on 21 LongBench tasks across 6 compression configurations, compute accuracy retention matrix (21×6), apply gap statistic to determine optimal cluster count k*.

**Success Criterion:** k* > 1 with gap > standard error.

---

## Problem Statement

KV cache compression methods (eviction, quantization) are applied uniformly across tasks. Hypothesis: different task types respond differently to compression strategies, forming identifiable clusters. Proving this enables task-adaptive compression routing.

---

## Functional Requirements

### FR-1: Dataset Loading
- Load all 21 LongBench tasks from THUDM/LongBench
- Use FULL test sets (~200-500 samples per task, ~4750 total)
- Truncate to 4096 tokens (Llama-2-7B context limit)

### FR-2: Baseline Model
- **Model:** meta-llama/Llama-2-7b-hf
- Load with float16, device_map="auto"
- Full KV cache evaluation as accuracy baseline per task

### FR-3: Compression Configurations (6 total)
| Config | Method | Retention | Quantization |
|--------|--------|-----------|--------------|
| C1 | full | 100% | None |
| C2 | H2O | 80% | None |
| C3 | H2O | 40% | None |
| C4 | full | 100% | int8 |
| C5 | full | 100% | int4 |
| C6 | H2O | 60% | int8 |

### FR-4: Response Matrix Computation
- Run inference: 21 tasks × 6 configs = 126 evaluation runs
- Compute per-task accuracy using LongBench metrics
- Normalize to accuracy retention ratio (task_acc / full_kv_acc)
- Output: 21×6 response matrix

### FR-5: Gap Statistic Clustering
- Apply gap statistic with B=500 bootstrap samples
- Test k ∈ {1, 2, 3, 4, 5, 6}
- Return k* (optimal clusters), gap values, standard errors

### FR-6: Secondary Metrics
- Compute silhouette score for k* clusters
- Generate cluster-task mapping

### FR-7: Visualization
- Gap statistic curve (gap vs k with SE error bars)
- Response matrix heatmap (21×6)
- Cluster visualization (2D PCA/t-SNE)
- Save all figures to `h-e1/figures/`

---

## Non-Functional Requirements

### NFR-1: Compute
- 1× A100 GPU (40GB+ VRAM)
- ~21 GPU-hours inference (parallelizable)
- ~5 min CPU for gap statistic

### NFR-2: Memory
- Llama-2-7B: ~14GB VRAM (float16)
- KV cache: ~400MB at full context
- Peak: ~20GB with batch processing

### NFR-3: Dependencies
- transformers, torch, datasets
- gap-stat (milesgranger/gap_statistic)
- bitsandbytes (for int4/int8 quantization)
- H2O implementation (FMInference/H2O or HuggingFace PR)

---

## Success Criteria

| Metric | Target | Gate |
|--------|--------|------|
| k* (optimal clusters) | > 1 | MUST_WORK |
| Gap significance | gap(k*) - E[gap_null] > SE | MUST_WORK |
| Silhouette score | > 0.5 | NICE_TO_HAVE |

**If FAIL:** ABANDON hypothesis chain (no task structure → no routing basis).

---

## Data Specifications

### Input
- LongBench dataset: THUDM/LongBench (HuggingFace)
- 21 tasks across 6 categories
- Full test splits (~4750 samples total)

### Output
- `response_matrix.npy`: 21×6 float array
- `gap_results.json`: k*, gap_df, significance
- `cluster_labels.json`: task → cluster mapping
- `figures/`: visualization PNGs

---

## Dependencies

### External Libraries
| Library | Version | Purpose |
|---------|---------|---------|
| transformers | ≥4.36 | Model loading |
| torch | ≥2.0 | Inference |
| datasets | ≥2.14 | LongBench loading |
| gap-stat | ≥2.0 | Gap statistic |
| bitsandbytes | ≥0.41 | Quantization |
| scikit-learn | ≥1.3 | KMeans, silhouette |

### Reference Implementations
- Gap statistic: milesgranger/gap_statistic
- H2O cache: FMInference/H2O (h2o_hf/)
- LongBench eval: THUDM/LongBench/eval.py

---

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| k*=1 (no clusters) | Gate → ABANDON chain |
| H2O integration issues | Fallback to HuggingFace H2OCache PR |
| Memory overflow | Batch processing, gradient checkpointing |
| Slow inference | Parallelize across configs |

---

*Generated from Phase 2C experiment brief*
*Next: Architecture design (Step 3)*
