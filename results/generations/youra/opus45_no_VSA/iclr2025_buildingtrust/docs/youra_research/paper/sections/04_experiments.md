# Experimental Setup

We design experiments to test four hypotheses corresponding to the existence, mechanism, intervention effect, and generalizability of the proposed GRC factor.

## Research Questions

**RQ1 (Existence):** Does a dominant latent factor persist after controlling for model scale and release date?

**RQ2 (Mechanism):** Does the latent factor correlate with behavioral stability, supporting representation stability as the underlying mechanism?

**RQ3 (Intervention):** Does instruction-tuning—a stability-enhancing training procedure—increase both behavioral stability and factor scores?

**RQ4 (Generalizability):** Do frozen factor weights generalize to holdout trustworthiness benchmarks not used in factor extraction?

## Data Sources

### Primary Dataset: Open LLM Leaderboard

We collect benchmark scores for N = 4,561 models from the Open LLM Leaderboard (Beeching et al., 2023).

| Benchmark | Task Type | Metric |
|-----------|-----------|--------|
| IFEval | Instruction following | Accuracy |
| BBH | Multi-step reasoning | Accuracy |
| MATH Lvl 5 | Mathematical reasoning | Accuracy |
| GPQA | Graduate-level QA | Accuracy |
| MUSR | Multi-step understanding | Accuracy |
| MMLU-PRO | Professional knowledge | Accuracy |

**Rationale:** These six benchmarks span diverse trustworthiness-relevant capabilities while sharing the common requirement of consistent, reliable model behavior. The large sample (N > 4,500) provides statistical power for factor analysis.

### Model Characteristics

| Property | Range | Coverage |
|----------|-------|----------|
| Parameters | 7B – 70B+ | 16 model families |
| Release Date | 2022-01 – 2026-06 | Continuous |
| Architecture | Decoder-only | Llama, Mistral, Qwen, Gemma, Phi |
| Training Type | Base + Instruct | Matched pairs available |

### Behavioral Stability Measurement

For mechanism validation (RQ2), we construct a Behavioral Stability Index (BSI) measuring output consistency on paraphrase datasets:

- **PAWS** (Zhang et al., 2019): 8,000 paraphrase pairs
- **QQP** (Wang et al., 2018): 40,000 question pairs

BSI operationalizes the degree to which a model produces consistent outputs when inputs are semantically equivalent but lexically varied.

### Holdout Benchmarks

For prospective validity (RQ4), we use six dimensions not included in factor extraction:

| Holdout Benchmark | Construct |
|-------------------|-----------|
| Truthfulness | Factual accuracy |
| Safety | Harmful output avoidance |
| Fairness | Demographic parity |
| Robustness | Perturbation resistance |
| Privacy | Information leakage |
| Ethics | Normative reasoning |

## Baselines and Comparisons

**Permutation Null:** Shuffled model-benchmark pairings establish chance-level factor strength. We generate 1,000 permutations and compute λ₁ for each.

**Scale-Only Model:** Regression of benchmarks on log(parameters) alone tests whether residualization adds value beyond scale control.

**Raw PCA:** Factor analysis without confound control shows pre-residualization factor structure for comparison.

## Statistical Methods

### Factor Extraction (RQ1)

1. Z-score normalize benchmark scores
2. Regress each benchmark on log₂(params) + release_date
3. Extract residuals for each benchmark
4. Apply PCA to N × 6 residual matrix
5. Compare observed λ₁ to permutation null 95th percentile

**Significance criterion:** p < 0.05 (observed λ₁ > 95% of permuted λ₁ values)

### Mechanism Validation (RQ2)

Pearson correlation between PC1 scores and BSI with bootstrap 95% confidence intervals (1,000 iterations).

**Success criterion:** ρ > 0, p < 0.05, CI excluding zero

### Intervention Analysis (RQ3)

Paired t-test on 16 matched base/instruct model pairs with Cohen's d effect size. Wilcoxon signed-rank test for robustness.

**Success criterion:** Δ_BSI > 0 and Δ_PC1 > 0, both with p < 0.05

### Prospective Validity (RQ4)

Correlation of holdout benchmark scores with frozen PC1 projection.

**Success criterion:** Loading ≥ 0.3 for at least 2 of 6 holdout benchmarks

## Implementation Details

All analyses implemented in Python 3.10 with:
- NumPy/SciPy for statistical computations
- Scikit-learn for PCA
- Statsmodels for regression diagnostics

**Diagnostic checks:** VIF < 5 (multicollinearity), KMO ≥ 0.6 (sampling adequacy), Shapiro-Wilk for normality assessment.

**Reproducibility:** Random seed fixed at 42 for permutation tests. Analysis code available in supplementary materials.
