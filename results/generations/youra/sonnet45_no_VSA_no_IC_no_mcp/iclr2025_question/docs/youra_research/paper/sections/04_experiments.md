# 4. Experimental Setup

We design experiments to answer three research questions corresponding to the framework's core mechanisms: (RQ1) Does micro-pilot overhead correlate with full-scale overhead? (RQ2) Do Bayesian updates reduce prediction error? (RQ3) Does Gate 1 achieve >80% viability classification accuracy? Each question tests a specific mechanism (M1-M3) with quantified success criteria and statistical validation.

## 4.1 Research Questions

**RQ1 (Mechanism M1):** Does micro-pilot overhead O₁₀ exhibit strong correlation (r > 0.7) with full-scale overhead O_full across diverse hypothesis types?

**Rationale**: Linear extrapolation O_full = k × O₁₀ requires predictive scaling. If r < 0.7, the correlation is too weak for reliable extrapolation and the framework collapses.

**RQ2 (Mechanism M2):** Do Bayesian updates combining Gate 1 prior with Gate 2 likelihood reduce prediction error by >40% compared to Gate 1 alone?

**Rationale**: Bayesian refinement adds complexity (100-sample investment at Gate 2). If error reduction is marginal (<20%), the framework should default to Gate 1-only prediction.

**RQ3 (Mechanism M3—Core Claim):** Does Gate 1 viability classification achieve >80% accuracy for predicting whether hypotheses exceed an overhead threshold, compared to 50% random baseline?

**Rationale**: This validates the primary prediction (P1). Accuracy ≤60% would indicate the framework performs no better than random guessing plus a small margin.

## 4.2 Corpus: Retrospective ML Projects

**Data Source**: We construct a synthetic corpus of 32 ML hypotheses with both micro-pilot (10-sample) and full-scale overhead measurements. Each hypothesis represents a variation in model architecture (attention mechanisms, gradient penalties, regularization techniques, normalization schemes) evaluated on standard benchmarks.

**Rationale for Synthetic Data**: Retrospective validation requires published papers reporting micro-pilot timing data—a constraint rarely satisfied in ML literature. Papers with Code and conference proceedings (NeurIPS, ICML, ICLR) typically report full-scale results but omit 10-sample ablations. Rather than abandon validation, we generate synthetic data that preserves the statistical properties we aim to test (scaling correlation, Bayesian error reduction, classification accuracy) while controlling for confounds. This establishes proof-of-concept for framework mechanics. External validity testing on real published papers remains critical future work (FD1).

**Corpus Structure**: 32 hypotheses stratified across overhead levels:
- 11 low-overhead (<20% full-scale overhead)
- 11 mid-overhead (20-80%)
- 10 high-overhead (>80%)

Stratification ensures balanced representation across the overhead spectrum. We verify coefficient of variation CV = 0.044 < 0.5 threshold, confirming adequate distribution balance.

**Overhead Threshold**: We use T = 10% as the viability threshold, reflecting real-time deployment constraints where overhead must remain minimal. This strict threshold results in 26 of 32 hypotheses (81.25%) classified as non-viable—a realistic distribution for deployment-constrained scenarios.

**Data Generation Process**: For each hypothesis, we:
1. Sample base overhead from stratified distribution
2. Generate micro-pilot overhead O₁₀ with scaling factor k=1.000 (perfect linearity for proof-of-concept)
3. Generate mid-scale overhead O₁₀₀ = O_full / (dataset_size / 100)
4. Compute full-scale overhead O_full deterministically from base overhead

This construction enforces perfect linear scaling (r=1.000) by design, representing an idealized scenario. Real-world validation will test whether the r ≥ 0.7 threshold holds under measurement noise and hardware variance.

## 4.3 Baseline Comparison Methods

| Method | Description | Expected Performance |
|--------|-------------|----------------------|
| **Random Guessing** | Coin flip for viable/non-viable classification | 50% accuracy (null hypothesis) |
| **Informal Micro-Pilot** | Researcher runs 10 samples, eyeballs overhead, decides without formalized threshold or statistical framework | ~60-70% accuracy (estimated, combines measurement with informal judgment) |
| **Expert Intuition** | Assessment based on hypothesis description alone, no empirical micro-pilot | ~60-70% accuracy (anecdotal, h-e1 example suggests 60-70% informal accuracy) |
| **Full Implementation** | Measure ground truth overhead on complete dataset | 100% accuracy, but requires full resource investment (days) |
| **Gate 1 (Ours)** | Micro-pilot prediction O_pred = k × O₁₀ with formalized threshold comparison and Bayesian refinement option | Target: >80% accuracy, <1 hour investment |

Our framework's value proposition: accuracy approaching full implementation (93.3% vs 100%) at a fraction of the cost (10 samples, <1 hour vs full dataset, days), with formalized decision criteria (threshold comparison, statistical confidence intervals) that informal micro-pilot approaches lack.

## 4.4 Evaluation Metrics

**RQ1 Metrics (Correlation)**:
- **Pearson r**: Linear correlation between O₁₀ and O_full. Success: r > 0.7, p < 0.05.
- **R² (coefficient of determination)**: Variance in O_full explained by linear model. Success: R² > 0.5.
- **Scaling factor k**: Slope of regression line O_full = k × O₁₀. Report mean k and coefficient of variation CV across hypothesis types.

**RQ2 Metrics (Bayesian Error Reduction)**:
- **Prediction error**: |O_pred - O_full| / O_full (relative error percentage).
- **Error reduction**: (Error_G1 - Error_G2) / Error_G1 × 100%. Success: >40%, paired t-test p < 0.05.
- Sample size: ≥10 hypotheses with Gate 2 data for adequate statistical power.

**RQ3 Metrics (Classification Accuracy)**:
- **Accuracy**: (TP + TN) / Total. Success: >80% (24/30 correct), binomial test vs 50% null, p < 0.05.
- **Confusion matrix**: True Positives (non-viable correctly identified), True Negatives (viable correctly identified), False Positives (viable incorrectly stopped), False Negatives (non-viable missed).
- **Recall on non-viable**: TP / (TP + FN). Prioritize minimizing false negatives (missed non-viable hypotheses).
- **Precision on viable**: TN / (TN + FP). Monitor false positives (viable hypotheses incorrectly stopped).

Statistical significance testing ensures results are not due to chance. For RQ1, we use Pearson correlation p-value. For RQ2, paired t-test comparing Gate 1 vs Gate 2 errors. For RQ3, binomial test against 50% null hypothesis.

## 4.5 Implementation Details

**Hardware**: Standard CPU-based execution (no GPU required for synthetic validation). Real-world validation will require profiling on target deployment hardware.

**Software**: Python 3.8+, scipy.stats for Bayesian updates and statistical tests, numpy for linear regression, matplotlib for visualization.

**Reproducibility**: All experiments use fixed random seed (42). Synthetic corpus generation is deterministic. Code and data available in supplementary materials.

**Measurement Protocol**: For each hypothesis:
1. Gate 1: Measure O₁₀ on 10 samples (wall-clock time normalized by baseline)
2. Gate 2: Measure O₁₀₀ on 100 samples (subset of hypotheses for RQ2)
3. Gate 3: Measure O_full on complete synthetic dataset (ground truth)
4. Repeat each measurement 3 times, report mean (measurement stability check)

**Threat Mitigation**: Synthetic data introduces internal validity risk (perfect linearity artifact). We address this by:
- Explicitly documenting synthetic nature in results (Section 5)
- Prioritizing external validation on real corpus (Future Work FD1)
- Testing framework mechanics (gate logic, Bayesian updates, statistical tests) rather than claiming generalizability

This experimental design balances proof-of-concept validation (synthetic corpus establishes that framework mechanics work as designed) with transparent limitation disclosure (external validity unknown until real-world validation).
