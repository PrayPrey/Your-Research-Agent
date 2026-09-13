# Methodology

Building on our observation that curation parameters can be treated as continuous variables with measurable dose-response relationships, we design a controlled experimental framework that isolates individual parameters while holding all other factors constant.

## Experimental Design Overview

Our core methodology follows the fixed-token experimental design: for each curation parameter under study, we train models on identical token budgets, architectures, and hyperparameters, varying only the parameter of interest. This controls for confounds that plague pipeline comparisons where multiple factors change simultaneously.

**Rationale:** Without fixed-token design, observed performance differences could stem from training duration, model capacity, or optimization dynamics rather than data quality. By equalizing these factors, we isolate the curation signal.

### Independent Variables

We study two primary curation parameters:

1. **Perplexity Threshold:** KenLM 5-gram perplexity percentile cutoff (trained on Wikipedia reference corpus). Levels: none (p0), p10, p20, p30, p40, p50, p60, p70, p80, p90.

2. **Deduplication Stringency:** MinHash/exact deduplication configuration. Levels: none, fuzzy_0.7, fuzzy_0.85, exact, exact_plus_fuzzy.

### Dependent Variables

**Primary:** Benchmark ensemble score computed as the first principal component (PC1) of accuracy scores across HellaSwag, ARC-Easy, PIQA, and WinoGrande. This ensemble reduces noise from individual benchmark variance.

**Secondary:** Individual benchmark scores, training loss curves, convergence metrics.

### Controlled Variables

- Training token budget: 10B tokens per configuration (reduced to 5M-10M for PoC validation)
- Model architecture: GPT-2 (125M, 350M, 1B variants)
- Training hyperparameters: learning rate 6e-4, batch size 512, warmup 2000 steps
- Evaluation protocol: lm-eval-harness with contamination verification
- Random seeds: 3 seeds per configuration for variance estimation

## Dose-Response Analysis

### Polynomial Regression

To characterize dose-response relationships, we fit polynomial models of increasing order and select using information criteria:

```
y = β₀ + β₁x + β₂x² + ... + βₖxᵏ + ε
```

Model selection uses AIC/BIC comparison:
- If quadratic (k=2) significantly outperforms linear (k=1): evidence for non-monotonic relationship
- If quadratic shows interior peak: optimal threshold exists within parameter range

**Rationale:** Linear models capture monotonic relationships ("stricter is always better" or "stricter is always worse"). Selection of higher-order models with interior extrema indicates the quality-diversity tradeoff we hypothesize.

### Peak Identification

For quadratic models y = β₀ + β₁x + β₂x², the optimal threshold is:

```
x* = -β₁ / (2β₂)
```

We compute 95% confidence intervals via bootstrap resampling (1000 iterations), reporting both point estimate and interval bounds.

## Mechanism Verification

Beyond existence of dose-response relationships, we test the underlying mechanism: noise dilution at low thresholds versus diversity loss at high thresholds.

### Convergence Dynamics Analysis

We track training loss curves L(t) across filtering levels and compute:

1. **Convergence AUC:** Area under the loss curve, capturing total training cost. Higher AUC indicates slower/worse convergence.

2. **Steps to Threshold:** Number of steps to reach target loss value, measuring convergence speed.

**Prediction:** If noise dilutes learning signal, unfiltered training (p0) should show higher AUC than moderate filtering (p50). If over-filtering removes useful diversity, strict filtering (p90) should converge quickly but plateau at higher final loss.

### Quality-Diversity Tradeoff Visualization

We measure:
- **Quality:** Mean perplexity reduction from filtering
- **Diversity:** Vocabulary coverage, topic distribution entropy

Plotting quality versus diversity across thresholds visualizes the tradeoff and identifies the Pareto frontier.

## Scale Transfer Analysis

To test whether optimal parameters transfer across model scales, we:

1. Identify optimal threshold at 125M scale from full sweep
2. Run targeted validation at 1B scale with optimal threshold ± neighboring levels
3. Compare relative improvement over RedPajama defaults at both scales
4. Compute transfer ratio: (improvement at 1B) / (improvement at 125M)

**Success criterion:** Transfer ratio > 0.80 indicates optima are scale-stable within 20%.

## Implementation

All experiments use the following pipeline:

1. **Data preparation:** RedPajama-v2 filtered at each threshold level using KenLM scoring
2. **Training:** HuggingFace Transformers with standard GPT-2 configuration
3. **Evaluation:** lm-eval-harness benchmark suite with Min-K%++ contamination verification
4. **Analysis:** Custom polynomial regression and convergence analysis toolkit

Figure 3 shows representative loss curves across filtering levels, illustrating the convergence dynamics that enable mechanism verification. Figure 10 demonstrates the polynomial model comparison approach used for dose-response characterization.
