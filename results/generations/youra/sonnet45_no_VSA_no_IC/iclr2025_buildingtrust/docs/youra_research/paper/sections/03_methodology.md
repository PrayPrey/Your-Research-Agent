# Methodology

Our sparse coupling hypothesis requires measuring all 10 dimension pairs (from 5 dimensions: truthfulness, robustness, fairness, safety, privacy) to distinguish broad coupling (many pairs significant) from narrow coupling (few pairs). Difficulty-independence requires explicit control via partial correlation. This section explains why each design choice addresses the coupling characterization problem.

## Phi Coefficient for Coupling Strength

We measure coupling via the phi coefficient (φ), an effect size for 2×2 contingency tables. For each dimension pair (A, B) and model, we construct a contingency table from instance-level binary labels (pass/fail):

```
           B_pass  B_fail
A_pass       n11     n12
A_fail       n21     n22
```

Phi coefficient quantifies association strength:

φ = (n11·n22 - n12·n21) / √[(n11+n12)(n21+n22)(n11+n21)(n12+n22)]

Phi ranges from 0 (independence) to 1 (perfect coupling), providing an interpretable scale: φ ≥ 0.3 indicates medium effect size in social science conventions. We pair this with chi-square significance tests (p < 0.01 threshold) to separate real coupling from sampling noise.

**Why phi over alternatives?** Odds ratios are less interpretable (exponential scale), chi-square alone provides no effect size, and Pearson correlation assumes continuous data. Phi directly measures co-occurrence probability in binary outcomes—exactly our coupling definition.

## Partial Correlation for Difficulty Control

Instance difficulty confounds coupling estimates. Hard instances may fail on all dimensions simultaneously, creating spurious correlation independent of shared vulnerabilities. We control this via partial correlation, computing phi after partialing out difficulty:

φ_partial(A, B | difficulty) = correlation residual after regressing A, B on difficulty

We operationalize difficulty as a composite score derived from model confidence (simulated in Phase 4; API logprobs in production). Figure 1 validates the control strategy: difficulty shows |r| < 0.2 with all dimensions, confirming statistical independence required for partial correlation.

**Why partial correlation over stratification?** We use both as dual validation. Partial correlation provides continuous control across the difficulty spectrum, while quartile stratification (Figure 3) offers robustness checking—coupling must persist in ≥3 quartiles. The dual approach guards against distributional assumptions in either method.

## Mantel Test for Model-Specific Fingerprints

Model-specific coupling profiles require comparing coupling matrices across model pairs. Each model produces a 5×5 symmetric coupling matrix (10 unique pairs). The Mantel test measures matrix similarity via permutation-based correlation:

1. Compute Pearson r between vectorized matrices (GPT-4 vs Claude-3)
2. Permute rows/columns of one matrix 10,000 times
3. Calculate r for each permutation
4. p-value = proportion of permutations with |r| ≥ observed |r|

**Why Mantel over element-wise correlation?** Mantel preserves matrix structure—dimensions have inherent ordering (truthfulness, robustness, fairness, safety, privacy). Element-wise correlation treats pairs as independent, ignoring positional information. Our threshold r < 0.7 defines "distinct profiles"—Bonferroni-corrected p < 0.0167 confirms significance.

## Bonferroni Correction for Multi-Pair Analysis

Testing ≥3 significant pairs per model (h-m2) requires multiple comparison correction. We use Bonferroni correction for family-wise error rate control:

α_adjusted = 0.01 / 30 ≈ 0.00033 (10 pairs × 3 models)

Each pair must meet both φ ≥ 0.3 AND p < α_adjusted to count toward the ≥3 threshold. This conservative approach controls false positives but may exclude borderline pairs.

**Why Bonferroni over FDR?** Bonferroni guarantees family-wise error rate < 0.01—no false positives across all 30 tests. FDR (Benjamini-Hochberg) controls expected false discovery proportion, accepting some false positives for higher power. We chose Bonferroni for confirmatory analysis (h-m2 tests a specific prediction: ≥3 pairs), reserving FDR for exploratory sensitivity analysis.

## Intuition Building via Figures

Our methodology produces three key visualizations:

**Figure 1 (difficulty_independence.png):** Correlation heatmap showing difficulty vs. each dimension. All |r| < 0.2 validates that difficulty is orthogonal to dimension-specific failures—required assumption for partial correlation.

**Figure 2 (partial_vs_raw_phi.png):** Scatter plot comparing raw phi (x-axis) vs partial phi (y-axis) for 6 significant pairs across 3 models. Points above the diagonal (5/6 cases) show retention >100%—difficulty acts as suppressor, not confounder. This surprising result indicates difficulty masks true coupling strength rather than inflating it.

**Figure 3 (quartile_stratified_phi.png):** Heatmap showing coupling strength across difficulty quartiles (Q0=easy to Q3=hard) for truthfulness-robustness and fairness-safety pairs. Persistence in 3-4 quartiles per model validates coupling independence from difficulty gradients—complementary to partial correlation.

## Technical Depth Balance

Main paper presents phi formula, partial correlation intuition, and Mantel test overview with visual aids. Appendix provides full contingency tables (30 tables: 10 pairs × 3 models), power analysis explaining why n=100/dimension underpowers h-c1 Mantel test (requires n ≥ 500 for r=0.5 detection at 80% power), and sensitivity analysis comparing Bonferroni vs FDR correction.

This methodology addresses three design requirements: (1) measure all 10 pairs to distinguish broad from sparse coupling, (2) control difficulty to isolate genuine coupling, (3) compare models to test fingerprint hypothesis. The next section reports results validating sparse, difficulty-independent coupling with model-specific profiles.
