# Phase 4 Validation Report: H-E1

**Date:** 2026-08-26
**Hypothesis:** Benchmark Independence Verification
**Gate Type:** MUST_WORK
**Gate Result:** PASSED

---

## Summary

Evaluated base Llama-2-7B on TruthfulQA, HHH-helpful, and HHH-harmless benchmarks. Computed pairwise Pearson correlations to verify benchmarks measure distinct alignment dimensions.

**Key Finding:** All pairwise correlations are extremely low (|r| < 0.05), far below the 0.5 threshold. Benchmarks are effectively independent.

---

## Results

### Benchmark Accuracies

| Benchmark | Accuracy | N Samples |
|-----------|----------|-----------|
| TruthfulQA (MC1) | 20.4% | 817 |
| HHH-helpful | 56.0% | 1000 |
| HHH-harmless | 53.8% | 1000 |

### Pairwise Correlations

| Pair | Pearson r | p-value | Gate Status |
|------|-----------|---------|-------------|
| TruthfulQA vs HHH-helpful | 0.040 | 0.248 | PASS |
| TruthfulQA vs HHH-harmless | -0.001 | 0.983 | PASS |
| HHH-helpful vs HHH-harmless | 0.019 | 0.547 | PASS |

**Maximum |r|:** 0.040 (threshold: 0.5)

---

## Gate Evaluation

**Gate Type:** MUST_WORK
**Condition:** All pairwise |r| < 0.5
**Result:** PASSED

All correlations are near zero, indicating the benchmarks measure distinct alignment dimensions as hypothesized. This validates the experimental design for subsequent hypotheses comparing RLHF vs DPO alignment signatures.

---

## Generated Artifacts

### Code Files
- `code/config.py` - Configuration
- `code/data.py` - Dataset loading
- `code/evaluate.py` - Model evaluation
- `code/correlate.py` - Correlation analysis
- `code/visualize.py` - Figure generation
- `code/train.py` - Main entrypoint

### Results
- `results/results.json` - Full experiment results

### Figures
- `figures/correlation_heatmap.png` - 3x3 correlation matrix
- `figures/gate_status.png` - Gate pass/fail visualization
- `figures/score_distributions.png` - Per-benchmark score distributions

---

## Interpretation

1. **TruthfulQA accuracy (20.4%)**: Base model performs poorly on truthfulness, as expected for unaligned models
2. **HHH accuracy (~55%)**: Near-random performance on preference tasks, as expected for base model
3. **Near-zero correlations**: Confirms benchmarks capture distinct aspects of alignment (truthfulness vs helpfulness vs harmlessness)

---

## Next Steps

Gate PASSED - proceed to subsequent hypotheses (H-M1 through H-M4) that build on this foundation to compare RLHF-PPO vs DPO alignment signatures across these independent benchmarks.

---

*Validation completed: 2026-08-26*
*Model: meta-llama/Llama-2-7b-hf*
*Seed: 42*
