# H-M1 Validation Report

**Hypothesis:** Attention pattern structure differs between encoder (bidirectional) and decoder (causal)

**Date:** 2026-08-18 14:42:21

---

## Summary

| Metric | BERT | GPT-2 |
|--------|------|-------|
| Upper Triangle Sparsity | 0.011759 | 1.000000 |
| Is Causal | False | True |

## Gate Verification

- **BERT Pass** (<0.10): True
- **GPT-2 Pass** (>0.99): True
- **Gate Result:** PASS
- **Sparsity Difference:** 0.988241

## Interpretation

BERT shows bidirectional attention (low upper-triangle sparsity) while GPT-2 shows causal attention (high upper-triangle sparsity near 1.0). The hypothesis is confirmed.

## Figures

- `gate_comparison.png`: Bar chart comparing sparsity
- `attention_heatmaps.png`: Sample attention patterns
- `layerwise_sparsity.png`: Per-layer breakdown
- `entropy_histogram.png`: Attention entropy distribution

## Config

- Dataset: glue/sst2 (872 samples)
- Device: cuda
- Seed: 42
