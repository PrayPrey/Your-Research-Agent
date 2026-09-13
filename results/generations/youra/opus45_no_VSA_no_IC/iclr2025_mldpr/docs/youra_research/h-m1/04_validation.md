# H-M1 Validation Report: BFS-Gap Correlation Analysis

**Hypothesis ID**: h-m1
**Type**: MECHANISM
**Gate Type**: SHOULD_WORK
**Statement**: Benchmark Fingerprint Score (classifier confidence for true benchmark) correlates positively with cross-dataset performance gap (r>0.3, p<0.05)

## Experiment Summary

**Date**: 2026-08-24
**Code**: `docs/youra_research/h-m1/code/run_correlation.py`
**Environment**: youra-h-e1-final conda env, CUDA GPU

## Methodology

1. **BFS Computation**: Used H-E1's pre-trained fingerprint classifier to compute mean prediction confidence for the true benchmark class across each model's probe features.

2. **Gap Computation**: For each finetuned model, trained a linear transfer head on the cross-benchmark dataset (cifar100 models evaluated on flowers, flowers models evaluated on cifar100) with frozen backbone. Gap = in-domain accuracy - transfer accuracy.

3. **Correlation Analysis**: Computed Pearson correlation between BFS scores and performance gaps across all 6 models (2 benchmarks x 3 seeds).

## Results

| Benchmark | Seed | BFS | In-Domain Acc | Transfer Acc | Gap |
|-----------|------|-----|---------------|--------------|-----|
| cifar100 | 0 | 0.9998 | 0.8300 | 0.3872 | 0.4428 |
| cifar100 | 1 | 0.9999 | 0.7320 | 0.3662 | 0.3658 |
| cifar100 | 2 | 1.0000 | 0.8360 | 0.4088 | 0.4272 |
| flowers | 0 | 0.9998 | 0.8943 | 0.5596 | 0.3347 |
| flowers | 1 | 0.9999 | 0.8954 | 0.5304 | 0.3650 |
| flowers | 2 | 0.9998 | 0.9024 | 0.5456 | 0.3568 |

### Correlation Statistics

- **Pearson r**: 0.0219
- **p-value**: 0.9672
- **n**: 6 models

### Gate Evaluation

**Threshold**: r > 0.3 AND p < 0.05
**Result**: **FAIL**

- r = 0.022 << 0.3 (no meaningful correlation)
- p = 0.967 >> 0.05 (not statistically significant)

## Interpretation

The experiment found no evidence that BFS correlates with cross-dataset performance gap:

1. **Near-ceiling BFS**: All models achieved BFS > 0.999, indicating the fingerprint classifier is extremely confident about benchmark identity regardless of model variations. This ceiling effect leaves no variance to correlate with gap.

2. **Gap variance exists but uncorrelated**: Performance gaps ranged from 0.33 to 0.44, but this variance appears unrelated to fingerprint detectability.

3. **Possible explanations**:
   - BFS saturates when fingerprinting is highly successful (H-E1 achieved 99.5% accuracy)
   - Cross-dataset gap may be driven by domain shift (flowers vs cifar100 are very different domains) rather than benchmark-specific overfitting
   - Need more benchmarks with varying fingerprint detectability to test correlation

## Artifacts

- Results JSON: `h-m1/code/results/experiment_results.json`
- Scatter plot: `h-m1/code/figures/bfs_gap_scatter.png`
- Code: `h-m1/code/run_correlation.py`

## Conclusion

H-M1 mechanism hypothesis is **NOT SUPPORTED** by this experiment. The proposed BFS-Gap correlation (r>0.3, p<0.05) was not observed. The fingerprint classifier's near-perfect confidence across all models prevents detection of any correlation.

**Gate Result**: FAIL
**Route**: Continue to next hypothesis (h-m2) per SHOULD_WORK gate semantics
