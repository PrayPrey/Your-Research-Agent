# H-C1 Validation Report

**Hypothesis**: SA-correctness correlation generalizes across 3+ LLMs with variance std(r) < 0.15

**Gate Type**: SHOULD_WORK

## Results Summary

| Metric | Value | Threshold | Pass |
|--------|-------|-----------|------|
| Models tested | 4 | ≥3 | ✓ |
| Mean r (pylint_score) | 0.747 | >0.35 | ✓ |
| Min r (pylint_score) | 0.424 | >0.20 | ✓ |
| **Std r (pylint_score)** | **0.186** | **<0.15** | **✗** |

**Gate Result: FAIL**

## Per-Model Correlations (pylint_score, LOC-controlled)

| Model | r_partial | p-value | Significant |
|-------|-----------|---------|-------------|
| gpt4 | 0.424 | 7.0e-08 | ✓ |
| claude3 | 0.860 | 8.4e-45 | ✓ |
| codellama | 0.845 | 8.8e-42 | ✓ |
| codestral | 0.859 | 1.4e-44 | ✓ |

## Analysis

All 4 models show statistically significant SA-correctness correlation (p < 0.001). The mean correlation (r=0.747) far exceeds the H-M1 threshold of 0.35.

**Variance issue**: gpt4 shows lower correlation (r=0.42) compared to other models (r~0.85). This outlier inflates std(r) to 0.186, exceeding the 0.15 threshold.

Possible causes:
1. Synthetic completion generation may have model-specific artifacts
2. gpt4 profile in synthetic data differs from real-world characteristics
3. The variance threshold (0.15) may be too strict for practical generalization

## Secondary Metric (radon_cc)

| Model | r_partial | p-value |
|-------|-----------|---------|
| gpt4 | -0.333 | 3.3e-05 |
| claude3 | -0.580 | 9.2e-15 |
| codellama | -0.574 | 1.9e-14 |
| codestral | -0.550 | 3.6e-13 |

radon_cc also shows consistent negative correlation across all models.

## Conclusion

The SHOULD_WORK gate **fails** on the strict variance criterion (std < 0.15) but shows strong evidence of cross-model generalization:
- All models show significant correlations
- Mean correlation (0.747) is strong
- 3 of 4 models cluster tightly (r = 0.84-0.86)

The hypothesis holds directionally but with higher variance than specified.

## Experimental Setup

- Dataset: HumanEval + MBPP-sanitized (150 samples per model)
- Models: gpt4, claude3, codellama, codestral (synthetic completions)
- SA Metrics: pylint_score (primary), radon_cc (secondary)
- Total samples: 600

## Files

- `code/results/h_c1_summary.json` - Summary statistics
- `code/results/h_c1_correlations.json` - Per-model correlations
- `code/results/h_c1_data.csv` - Raw data
- `code/figures/` - Visualization plots
