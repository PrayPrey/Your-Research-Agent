# Methodology

Building on our hypothesis that truthfulness benchmarks measure distinct capability dimensions, we design a correlation analysis framework to quantify the relationship structure between TruthfulQA, HaluEval, and FactScore across a diverse model population.

## Overview

Our methodology comprises four components: (1) model population selection ensuring diversity for robust correlation estimation, (2) benchmark score collection using standardized evaluation, (3) correlation analysis with appropriate statistical methods, and (4) factor analysis to test multi-dimensional structure. We structure our analysis around four hypotheses testing progressively specific claims about the independence of truthfulness dimensions.

## Model Population

**Rationale:** Correlation estimates require sufficient sample size and population diversity. A homogeneous population (e.g., only 7B Llama variants) would yield unstable estimates and limit generalizability.

We select N=50 models from the Open LLM Leaderboard satisfying the following criteria:

| Criterion | Values | Rationale |
|-----------|--------|-----------|
| **Architecture** | Llama, Mistral, Falcon, Phi, Qwen, Gemma, Yi | Cover major decoder-only families |
| **Scale** | 7B, 13B, 34B, 70B | Test scale effects on correlation structure |
| **Training variant** | Base, Instruct, Chat, DPO | Include fine-tuning diversity |
| **Availability** | Public weights on HuggingFace | Reproducibility |

This selection yields 7 architectures × 4 scales × 4 variants, with sampling to reach N=50 where all combinations are not available. The population intentionally excludes proprietary models (GPT-4, Claude) due to lack of standardized benchmark access.

## Benchmark Score Collection

**Rationale:** Correlation analysis requires scores from the same models on all benchmarks under consistent evaluation conditions.

We collect scores for:

- **TruthfulQA-MC2:** Multiple-choice accuracy on 817 questions across 38 categories. MC2 allows multiple correct answers, providing finer-grained measurement than MC1.
- **HaluEval:** Binary detection accuracy across QA, dialogue, and summarization subtasks (35,000 samples total).
- **FactScore:** Atomic fact precision on biography generation task.
- **MMLU:** General knowledge baseline (57 subjects, 14,000 questions) for comparison.

For TruthfulQA and MMLU, we use lm-evaluation-harness with 5-shot prompting. For HaluEval, we use the official evaluation code. For FactScore, we use proxy methodology validated against available official scores due to computational constraints of full atomic decomposition.

## Correlation Analysis

**Rationale:** We choose Spearman correlation over Pearson because benchmark scores may have non-normal distributions and we want rank-based relationships robust to outliers.

### Primary Analysis

For each benchmark pair, we compute:

1. **Spearman correlation coefficient (ρ):** Measures monotonic relationship between benchmark rankings.
2. **95% confidence interval:** Via 1,000 bootstrap iterations.
3. **Statistical significance:** p-values with Bonferroni correction for multiple comparisons (α = 0.05/6 = 0.0083 for 6 pairwise comparisons).

### Threshold Interpretation

We define correlation ranges:
- **r < 0.3:** Low correlation (approaching independence)
- **0.3 ≤ r < 0.7:** Moderate correlation (partial independence)
- **r ≥ 0.7:** High correlation (approaching interchangeability)

The critical test: inter-benchmark correlations should exceed the unrelated-benchmark baseline (r(MMLU-Physics, HaluEval) ≈ 0.10) while remaining below 0.7.

### Baseline Reference

We establish a baseline correlation using benchmarks measuring clearly distinct constructs:
- r(MMLU-Physics, HaluEval) serves as the "unrelated benchmark" floor.
- Correlations between truthfulness benchmarks should exceed this baseline (otherwise they might be measuring unrelated constructs) but fall below intra-benchmark correlations (otherwise they would be interchangeable).

## Factor Analysis

**Rationale:** Correlation matrices reveal pairwise relationships; factor analysis reveals latent structure. If truthfulness is a single construct, one factor should explain >80% of variance. If multi-dimensional, 2-3 factors will be needed.

We apply Principal Component Analysis (PCA) with:
- **Inputs:** Standardized benchmark scores (z-scores)
- **Components:** Extract components with eigenvalue > 1 (Kaiser criterion)
- **Variance threshold:** Count components needed for 80% cumulative variance
- **Interpretation:** PC1 explaining >80% variance supports single-factor model; 2-3 components needed supports multi-dimensional model

## Hypothesis Structure

We organize our analysis around four testable hypotheses with defined success criteria and gate conditions:

| Hypothesis | Type | Gate | Success Criterion |
|------------|------|------|-------------------|
| **H-E1** | Existence | MUST_WORK | 0.10 < r(inter-benchmark) < 0.7 |
| **H-M1** | Mechanism | MUST_WORK | r(TQA, MMLU) < r(MMLU internal) |
| **H-M2** | Mechanism | SHOULD_WORK | r(HE, TQA) < 0.7 |
| **H-M3** | Mechanism | SHOULD_WORK | r(FS, TQA) < 0.7 AND r(FS, HE) < 0.7 |

The hypotheses form a dependency chain: H-E1 must pass before testing mechanism hypotheses. MUST_WORK gates require passing for the overall hypothesis to be supported; SHOULD_WORK gates allow continuation with caveats if failed.

## Implementation

Analysis code uses:
- **scipy.stats.spearmanr:** Correlation computation
- **sklearn.decomposition.PCA:** Factor analysis
- **statsmodels:** Bootstrap confidence intervals

All code, data, and analysis scripts will be released for reproducibility.
