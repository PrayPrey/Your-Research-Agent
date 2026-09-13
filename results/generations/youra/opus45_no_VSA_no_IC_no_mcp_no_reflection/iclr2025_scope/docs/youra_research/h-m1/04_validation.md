# Validation Report: h-m1

**Hypothesis:** h-m1 (MECHANISM)
**Statement:** Duality-preserving initialization provides lower initial reconstruction error than random initialization, demonstrating that Mamba-2 duality equations capture meaningful structure from attention weights
**Gate Type:** MUST_WORK
**Validation Date:** 2026-08-31

---

## Executive Summary

**GATE RESULT: FAIL**

The experiment conclusively demonstrated that duality-initialized SSM parameters produce **higher** reconstruction error than random initialization, contrary to hypothesis. This is statistically significant with a large effect size (Cohen's d = -4.56).

---

## Experiment Configuration

| Parameter | Value |
|-----------|-------|
| Dataset | WikiText-103 validation |
| Samples | 500 |
| Model | BERT-base-uncased (12 layers) |
| Sequence length | 64-512 tokens |
| d_state | 64 |
| Device | CUDA |

---

## Results

### Global Statistics

| Metric | Value |
|--------|-------|
| Mean Duality Error | 91.45 |
| Mean Random Error | 89.54 |
| Error Reduction | **-2.13%** (worse) |
| P-value | < 0.0001 |
| Cohen's d | -4.56 (large negative) |

### Per-Layer Results

| Layer | Duality Error | Random Error | Reduction % | Cohen's d |
|-------|---------------|--------------|-------------|-----------|
| 0 | 79.75 | 77.74 | -2.58% | -5.02 |
| 1 | 93.98 | 92.16 | -1.98% | -5.50 |
| 2 | 108.35 | 106.70 | -1.55% | -5.19 |
| 3 | 104.67 | 103.04 | -1.57% | -5.97 |
| 4 | 98.18 | 96.35 | -1.89% | -4.15 |
| 5 | 96.58 | 94.85 | -1.82% | -5.92 |
| 6 | 96.29 | 94.53 | -1.86% | -5.12 |
| 7 | 91.16 | 89.18 | -2.22% | -4.71 |
| 8 | 84.44 | 82.31 | -2.58% | -5.85 |
| 9 | 87.10 | 85.06 | -2.40% | -5.38 |
| 10 | 79.79 | 77.64 | -2.77% | -5.31 |
| 11 | 77.11 | 74.91 | -2.94% | -4.84 |

**Observation:** Duality initialization is consistently worse across ALL 12 layers.

---

## Gate Evaluation

### Success Criteria (from PRD)

| Criterion | Required | Observed | Status |
|-----------|----------|----------|--------|
| Error Direction | duality_error < random_error | duality_error > random_error | **FAIL** |
| Error Reduction | > 0% | -2.13% | **FAIL** |
| Sample Coverage | 100% complete | 100% complete | PASS |

### Gate Verdict

**MUST_WORK: FAIL**

The duality conversion produces valid parameters (per h-e1), but these parameters do NOT capture meaningful attention structure in terms of reconstruction error. The SSM output diverges more from attention output when initialized from duality equations than from random initialization.

---

## Analysis

### Root Cause Hypotheses

1. **Metric mismatch**: Frobenius norm on raw outputs may not be the right metric. MOHAWK uses matrix alignment on the mixing matrices (CB^T vs QK^T), not output alignment.

2. **Architecture mismatch**: BERT's multi-head attention with residual connections differs substantially from the SSD duality assumptions (single-head, scalar A).

3. **Scale mismatch**: The duality-derived parameters may have correct *structure* but wrong *scale* for matching attention outputs without fine-tuning.

4. **Duality conversion flaw**: The SVD-based decomposition (h-e1) may not correctly implement the Mamba-2 duality equations.

### Implication for Main Hypothesis

This does NOT invalidate the main hypothesis (DG-CAD). The main hypothesis proposes initialization + optimization. This mechanism test evaluated initialization alone. The duality equations may still provide better starting point for *optimization*, even if the zero-shot reconstruction is worse.

---

## Artifacts

- Results: `h-m1/code/results/comparison_results.json`
- Figures:
  - `h-m1/code/figures/bar_comparison.png`
  - `h-m1/code/figures/per_layer_comparison.png`
  - `h-m1/code/figures/effect_size_per_layer.png`

---

## Routing Decision

Per workflow rules for MUST_WORK gate failure:
- **First failure attempt**: Route to Phase 2A-Dialogue for hypothesis reformulation
- This was attempt 0, so routing to Phase 2A

**Recommendation**: Reformulate h-m1 to either:
1. Change metric to matrix alignment (CB^T vs QK^T) instead of output Frobenius norm
2. Test reconstruction after minimal optimization (not zero-shot)
3. Investigate the duality conversion implementation for correctness

---

*Report generated: 2026-08-31*
*Prerequisite: h-e1 VALIDATED*
*Gate: MUST_WORK FAIL*
