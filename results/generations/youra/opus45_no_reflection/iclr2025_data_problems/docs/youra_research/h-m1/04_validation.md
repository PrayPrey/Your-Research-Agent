# H-M1 Validation Report

**Hypothesis:** Attention pattern structure differs between encoder (bidirectional) and decoder (causal)

**Type:** MECHANISM | **Gate:** MUST_WORK | **Result:** PASS

**Date:** 2026-08-18T14:42:21

---

## Summary

| Metric | BERT | GPT-2 | Threshold |
|--------|------|-------|-----------|
| Upper Triangle Sparsity | 0.0118 | 1.0000 | BERT < 0.10, GPT-2 > 0.99 |
| Is Causal | False | True | - |
| Gate Pass | Yes | Yes | Both must pass |

## Gate Verification

| Check | Expected | Actual | Status |
|-------|----------|--------|--------|
| BERT upper_sparsity < 0.10 | < 0.10 | 0.0118 | PASS |
| GPT-2 upper_sparsity > 0.99 | > 0.99 | 1.0000 | PASS |
| **Overall Gate** | Both pass | Both pass | **PASS** |

**Sparsity Difference:** 0.9882 (GPT-2 - BERT)

## Interpretation

The hypothesis is **confirmed**:

1. **BERT (Bidirectional Encoder)**: Upper triangle sparsity is 0.0118 (1.18%), meaning attention weights are distributed across both past and future tokens. This confirms bidirectional attention.

2. **GPT-2 (Causal Decoder)**: Upper triangle sparsity is 1.0 (100%), meaning all attention weights above the diagonal are exactly zero. This confirms the causal attention mask.

The 98.82% difference in upper triangle sparsity between GPT-2 and BERT provides clear quantitative evidence that attention structure fundamentally differs between encoder and decoder architectures.

## Experiment Configuration

| Parameter | Value |
|-----------|-------|
| Dataset | glue/sst2 (validation) |
| Samples | 872 |
| Device | cuda |
| Seed | 42 |
| BERT Model | bert-base-uncased |
| GPT-2 Model | gpt2 |

## Per-Layer Analysis

### BERT Upper Triangle Sparsity by Layer

| Layer | Sparsity |
|-------|----------|
| 0 | 0.0006 |
| 1 | 0.0118 |
| 2 | 0.1176 |
| 3 | 0.0037 |
| 4 | 0.0006 |
| 5 | 0.0020 |
| 6 | 0.0017 |
| 7 | 0.0013 |
| 8 | 0.0003 |
| 9 | 0.0001 |
| 10 | 0.0014 |
| 11 | 0.0000 |

### GPT-2 Upper Triangle Sparsity by Layer

All layers: 1.0000 (perfect causal masking)

## Figures

| Figure | Description |
|--------|-------------|
| `figures/gate_comparison.png` | Bar chart comparing BERT vs GPT-2 upper triangle sparsity |
| `figures/attention_heatmaps.png` | Sample attention patterns for both models |
| `figures/layerwise_sparsity.png` | Per-layer sparsity breakdown |
| `figures/entropy_histogram.png` | Attention entropy distribution |

## Files Generated

- `code/results.json` - Full metrics in JSON format
- `code/report.md` - Summary report
- `code/run_experiment.py` - Main experiment script
- `figures/` - All visualizations

## Next Steps

Gate PASSED. Hypothesis H-M1 validated. The mechanism (attention pattern structure difference) has been quantitatively confirmed. This supports proceeding to H-M2 (Hessian curvature analysis).
