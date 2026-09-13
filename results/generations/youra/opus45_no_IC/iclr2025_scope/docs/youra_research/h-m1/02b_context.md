# Phase 2B Context: H-M1

**Generated:** 2026-08-10
**Source:** 02b_verification_plan.md (JIT extraction)

---

## Hypothesis Information

- **ID:** H-M1
- **Type:** MECHANISM
- **Statement:** Early attention entropy reflects task structure - entropy variance across tasks exceeds within-category variance
- **Gate:** MUST_WORK
- **Prerequisites:** H-E1 (COMPLETED, PASSED)

---

## Experimental Setup (from Phase 2B Section 1.3)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | LongBench (standard) | 21 tasks across 6 categories; enables task-dependent analysis |
| **Model** | Llama-2-7B | Standard benchmark model; KV cache significant at 7B scale |

**Dataset Details:**
- Source: https://github.com/THUDM/LongBench
- Path: huggingface: THUDM/LongBench

**Model Details:**
- Type: decoder-only transformer
- Source: meta-llama/Llama-2-7b-hf

---

## Verification Protocol (from Phase 2B)

1. Forward pass on each task sample, capture attention weights
2. Compute Shannon entropy per head per layer over first 100 tokens
3. Aggregate: mean entropy per task, variance across tasks, variance within categories
4. Apply F-test comparing between-category vs within-category variance

---

## Success Criteria

- **Primary:** Between-task entropy variance > within-category variance (F-test p<0.05)
- **Secondary:** Interpretable pattern (e.g., QA higher entropy than summarization)

---

## Failure Response

IF fails → PIVOT (try alternative features: head sparsity, top-k concentration)

---

## Dependencies

- **H-E1:** Task-dependent compression clusters exist ✓ PASSED (k*=3)

---

## Gate Condition

**Type:** MUST_WORK
**Condition:** F-test p<0.05 for entropy variance between vs within categories
**Fail Action:** PIVOT to alternative features

---

## Previous Hypothesis Results

### H-E1 Results (Prerequisite)
- **Status:** COMPLETED, PASSED
- **k*:** 3 clusters detected
- **Silhouette:** 0.411
- **Clusters:**
  - Cluster 0: Multi-doc QA + Code (high eviction sensitivity)
  - Cluster 1: Single-doc QA + Few-shot (moderate sensitivity)
  - Cluster 2: Summarization + Synthetic (different compression profile)

### Artifacts Available
- `h-e1/response_matrix.npy` - 21×6 accuracy retention matrix
- `h-e1/cluster_labels.json` - Task cluster assignments
- `h-e1/gap_results.json` - Gap statistic results

---

## Continuation Context

H-M1 builds directly on H-E1's finding that k*=3 task clusters exist. The hypothesis now tests whether early attention entropy can explain/predict these cluster differences. If entropy separates task categories, it provides a mechanism for the observed clustering and a signal for routing.

**Key insight from H-E1:** Different task types (multi-doc QA, single-doc QA, summarization) show systematically different compression tolerances.

**H-M1 tests:** Do attention entropy patterns differ systematically across these task types?
