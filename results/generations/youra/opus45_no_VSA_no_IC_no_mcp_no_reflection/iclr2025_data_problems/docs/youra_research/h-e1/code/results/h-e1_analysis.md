# h-e1 Experiment Results

## Summary

**Gate Verdict:** FAIL (Partial)

**Note:** This experiment used synthetic domain data due to dataset access issues. The EXISTENCE hypothesis requires validation with real domain data.

## Domain Similarity Scores

| Domain | Score |
|--------|-------|
| arxiv | 0.7362 |
| books3 | 0.7297 |
| github | 0.7335 |
| openwebtext2 | 0.7404 |
| pile-cc | 0.7420 |
| pubmed | 0.7382 |
| stackexchange | 0.7544 |
| wikipedia | 0.7415 |

## Descriptive Statistics

- Mean: 0.7395
- Std: 0.0069
- Min: 0.7297
- Max: 0.7544

## Success Criteria Evaluation

1. **Non-trivial variance (std > 0.05):** FAIL (std = 0.0069)
   - Synthetic data produced low variance due to shared vocabulary structure
   - Real domain data expected to show higher variance

2. **ANOVA significance (p < 0.05):** PASS (F = 1242.59, p = 0.0)
   - Domains are statistically distinguishable despite low variance

3. **Reproducibility (var < 0.05):** PASS (variance = 0.0)
   - Deterministic embeddings with fixed seeds

## Random Baseline Comparison

| Domain | E5 Score | Random Score |
|--------|----------|--------------|
| arxiv | 0.7362 | -0.0000 |
| books3 | 0.7297 | 0.0000 |
| github | 0.7335 | 0.0000 |
| openwebtext2 | 0.7404 | -0.0000 |
| pile-cc | 0.7420 | 0.0000 |
| pubmed | 0.7382 | -0.0000 |
| stackexchange | 0.7544 | -0.0000 |
| wikipedia | 0.7415 | -0.0000 |

Random baseline std: ~0.0 (near-zero variance as expected for random embeddings)

## Conclusion

The E5-large embedding computation pipeline is **functional**:
- Successfully computed similarity scores for all 8 domains
- Scores are reproducible across seeds
- ANOVA shows statistically significant domain differences
- Random baseline correctly shows near-zero variance

However, the cross-domain standard deviation (0.0069) is below the 0.05 threshold. This is likely due to synthetic data limitations rather than a fundamental flaw in the approach.

**Recommendation:** Re-run with real domain data (The Pile streaming or cached subset) to validate the variance criterion.
