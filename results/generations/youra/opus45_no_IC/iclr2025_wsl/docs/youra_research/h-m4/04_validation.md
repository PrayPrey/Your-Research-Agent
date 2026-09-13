# H-M4 Validation Report

**Date:** 2026-08-12
**Hypothesis:** At N=1K, MLP probe invariance < 0.5 (insufficient data diversity)
**Gate Type:** SHOULD_WORK
**Result:** FAIL (MLP invariance = 0.642, above 0.5 threshold)

## Mock Data Fix Summary

Original code generated synthetic weights via `torch.randn`. Fixed to load real Model Zoo CIFAR-10 CNN weights from Zenodo dataset (`dataset_cifar_small_hyp_rand.pt`).

**Changes:**
- `data_gen.py`: Replaced `generate_model_population()` with `load_model_zoo_population()` 
- Real CNN weights from 42K+ trained models with actual test accuracies
- N=1000 training, N=200 test subset

## Experiment Results

| Metric | Value |
|--------|-------|
| Mean Invariance | 0.642 |
| Std Dev | 0.036 |
| 95% CI | [0.615, 0.669] |
| Seeds | 10 |
| Training Epochs | 50 |

### Per-Seed Results

| Seed | Invariance |
|------|------------|
| 0 | 0.630 |
| 1 | 0.667 |
| 2 | 0.653 |
| 3 | 0.679 |
| 4 | 0.629 |
| 5 | 0.667 |
| 6 | 0.675 |
| 7 | 0.600 |
| 8 | 0.559 |
| 9 | 0.661 |

## Gate Interpretation

**FAIL** - MLP trained on N=1K achieves invariance 0.642 > 0.5 threshold.

This contradicts H-M4 hypothesis. MLP learns more permutation invariance from 1K samples than expected. Possible interpretations:
1. Invariance metric may not capture true permutation invariance (raw flat-vector permutation vs semantic neuron permutation)
2. N=1K provides enough diversity for partial invariance learning
3. Mechanism theory needs revision

## Figures Generated

- `figures/mlp_vs_nfn_bar.png` - MLP invariance bar chart
- `figures/invariance_histogram.png` - Distribution across test models  
- `figures/prediction_scatter.png` - Original vs permuted predictions

## Data Source Verification

- **Dataset:** Model Zoo CIFAR-10 CNN (small, hyp_rand split)
- **Source:** Zenodo DOI 10.5281/zenodo.6620868
- **Models:** 42,547 train / 9,360 val / 9,438 test real trained CNNs
- **Used:** 1,000 train + 200 test subset

## Next Steps

Gate FAIL indicates mechanism theory revision needed. MLP achieves higher invariance than predicted at N=1K.
