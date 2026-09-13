# Product Requirements Document: H-M1

**Hypothesis:** Benchmark Fingerprint Score (BFS) correlates positively with cross-dataset performance gap (r>0.3, p<0.05)

**Type:** MECHANISM | **Gate:** SHOULD_WORK

---

## Objective

Validate that BFS (classifier confidence for true benchmark) predicts generalization degradation on out-of-distribution data.

## Requirements

### Functional

1. **BFS Computation**
   - Load fingerprint classifier from H-E1
   - Extract softmax probabilities for each model's features
   - BFS = mean confidence for true benchmark class

2. **Gap Computation**
   - Evaluate each fine-tuned model on in-domain test set
   - Evaluate same model on NABirds (cross-dataset)
   - Gap = in-domain accuracy - NABirds accuracy

3. **Correlation Analysis**
   - Collect (BFS, Gap) pairs for all 6 models
   - Compute Pearson correlation r and p-value
   - Generate scatter plot with regression line

### Non-Functional

- Reuse H-E1 artifacts (6 models, fingerprint classifier)
- Single evaluation pass per model
- Results in JSON + scatter plot

## Success Criteria

- r > 0.3 (moderate positive correlation)
- p < 0.05 (statistically significant)

## Deliverables

1. `run_correlation.py` - main experiment script
2. `experiment_results.json` - BFS, Gap, r, p per model
3. `figures/bfs_gap_scatter.png` - visualization

## Dependencies

- H-E1 validated artifacts
- scipy.stats.pearsonr
- matplotlib for plotting
