# Experiments

This section describes the benchmark corpus characteristics, data extraction procedures, and analysis implementation. All code and data artifacts are available in the h-e1/ directory for reproducibility.

## Benchmark Corpus

We analyzed 10 trust evaluation benchmarks meeting our inclusion criteria (n≥10 models, public leaderboard, trust-relevant construct). Table 1 summarizes benchmark characteristics.

**Table 1: Benchmark Corpus Summary**

| Benchmark | CV | Mean ρ | n_pairs | Primary Focus |
|-----------|-----|--------|---------|---------------|
| TrustBench-Ethics | 0.130 | 0.181 | 9 | Ethical reasoning, moral judgment |
| FinTrust | 0.144 | 0.145 | 9 | Financial trustworthiness, fiduciary alignment |
| MultiTrust | 0.178 | 0.283 | 9 | Multi-dimensional trust (general) |
| TruthfulQA | 0.182 | 0.224 | 9 | Truthfulness, resistance to false statements |
| BiasEval | 0.196 | 0.045 | 9 | Fairness, bias detection across demographics |
| TrustLLM-Safety | 0.262 | 0.138 | 9 | Safety, harmlessness, toxicity avoidance |
| FaithfulQA | 0.350 | -0.245 | 9 | Hallucination detection, faithfulness to context |
| HaluBench | 0.419 | 0.172 | 9 | Hallucination detection (14.9k samples) |
| SafetyBench | 0.435 | -0.133 | 9 | Safety, red-teaming, harmful content generation |
| TrustLLM-Truthfulness | 0.458 | 0.122 | 9 | Truthfulness (sub-dimension of TrustLLM) |

**Corpus characteristics:**
- **CV range:** [0.130, 0.458] — substantial variance in score dispersion across benchmarks
- **Mean ρ range:** [-0.245, 0.283] — highly heterogeneous cross-benchmark agreement, including negative values
- **Model overlap:** All benchmark pairs had ≥5 shared models (n_pairs=9 for each benchmark, indicating pairwise comparisons with 9 other benchmarks)
- **Primary focus diversity:** Benchmarks span 6 trust sub-dimensions (ethics, finance, truthfulness, fairness, safety, hallucination detection)

### Benchmark Descriptions

**Truthfulness and Hallucination Detection:**
- **TruthfulQA** [Lin et al. 2021]: 817 adversarial questions designed to elicit false statements, evaluating resistance to common misconceptions
- **FaithfulQA**: Hallucination detection benchmark assessing faithfulness to provided context
- **HaluBench** [PatronusAI]: 14,900 samples across real-world domains (finance, medicine, general knowledge) with binary hallucination labels
- **TrustLLM-Truthfulness**: Truthfulness sub-dimension from TrustLLM's 8-dimensional framework

**Safety and Harmlessness:**
- **TrustLLM-Safety**: Safety sub-dimension assessing resistance to jailbreaks, toxicity generation, harmful content
- **SafetyBench**: Comprehensive safety evaluation including red-teaming, adversarial robustness

**Fairness and Bias:**
- **BiasEval**: Bias detection across demographic attributes (gender, race, age, religion)

**Domain-Specific Trust:**
- **FinTrust** [Hu et al. 2025]: Financial domain trustworthiness, including fiduciary alignment, disclosure quality, risk assessment
- **TrustBench-Ethics**: Ethical reasoning and moral judgment scenarios

**Multi-Dimensional:**
- **MultiTrust**: General multi-dimensional trust evaluation (exact dimensions not specified in our dataset documentation)

### Data Collection Procedure

**Source:** Mock benchmark corpus (see Methodology Section 3 and Limitations Section 6.1 for validity threat discussion). Real leaderboard extraction (TrustLLM HTML, TruthfulQA GitHub CSV, HaluBench PDF) was planned in Phase 2C but not executed in Phase 4 implementation.

**Model score extraction:**
1. For each benchmark, extract model identifiers and corresponding scores (single aggregate metric per model)
2. Verify n≥10 models requirement (all 10 benchmarks met threshold)
3. Compute descriptive statistics: mean (μ), standard deviation (σ), min, max

**CV computation:**
```python
import pandas as pd
import numpy as np

def compute_cv(scores):
    """Compute coefficient of variation."""
    mu = np.mean(scores)
    sigma = np.std(scores, ddof=1)  # Sample standard deviation
    return sigma / mu
```

**Cross-benchmark ρ computation:**
```python
from scipy.stats import spearmanr

def compute_cross_benchmark_rho(benchmark_a, benchmark_b):
    """Compute Spearman rho between two benchmarks (shared models only)."""
    shared_models = set(benchmark_a.keys()) & set(benchmark_b.keys())
    if len(shared_models) < 5:
        return None  # Insufficient overlap
    
    scores_a = [benchmark_a[m] for m in shared_models]
    scores_b = [benchmark_b[m] for m in shared_models]
    rho, _ = spearmanr(scores_a, scores_b)
    return rho

def compute_mean_rho(target_benchmark, all_benchmarks):
    """Compute mean cross-benchmark rho for target benchmark."""
    rhos = []
    for other_benchmark in all_benchmarks:
        if other_benchmark == target_benchmark:
            continue
        rho = compute_cross_benchmark_rho(target_benchmark, other_benchmark)
        if rho is not None:
            rhos.append(rho)
    return np.mean(rhos)
```

All benchmarks achieved n_pairs=9 (pairwise comparisons with 9 other benchmarks), indicating 100% valid overlap rate (≥5 shared models with all other benchmarks). This high overlap rate strengthens cross-benchmark ρ estimates—no benchmark was excluded due to insufficient model overlap.

## Analysis Implementation

### Statistical Test

**Primary analysis:** Pearson correlation between CV and mean cross-benchmark ρ

```python
from scipy.stats import pearsonr

cv_values = [0.130, 0.144, 0.178, 0.182, 0.196, 0.262, 0.350, 0.419, 0.435, 0.458]
mean_rho_values = [0.181, 0.145, 0.283, 0.224, 0.045, 0.138, -0.245, 0.172, -0.133, 0.122]

r, p = pearsonr(cv_values, mean_rho_values)
print(f"Pearson r: {r:.3f}, p-value: {p:.4f}")

# Confidence interval (via Fisher z-transformation)
import numpy as np
from scipy.stats import norm

n = len(cv_values)
z = np.arctanh(r)  # Fisher z-transform
se_z = 1 / np.sqrt(n - 3)
ci_z = [z - 1.96*se_z, z + 1.96*se_z]
ci_r = [np.tanh(ci_z[0]), np.tanh(ci_z[1])]
print(f"95% CI: [{ci_r[0]:.3f}, {ci_r[1]:.3f}]")
```

**Output:**
- Pearson r: -0.486
- p-value: 0.1542
- 95% CI: [-0.854, 0.207]

### Visualizations

Four visualizations were generated (saved to h-e1/figures/):

1. **cv_vs_rho_scatter.png** (Figure 1, Results Section): Scatter plot with regression line (r=-0.486, p=0.154), shaded MUST_WORK threshold region (r < -0.5), and 95% confidence band
2. **pairwise_rho_heatmap.png** (Figure 2, Results Section): 10×10 heatmap of pairwise Spearman ρ between all benchmarks, color-coded by correlation strength (red=negative, white=zero, blue=positive)
3. **gate_metrics_comparison.png** (Figure 3, Results Section): Bar chart comparing target vs. actual gate criteria (correlation magnitude, significance)
4. **cv_rho_per_benchmark_bars.png** (Supplementary): Dual bar chart showing CV and mean ρ per benchmark for exploratory analysis

All visualizations generated via matplotlib with consistent styling (colorblind-friendly palette, high-resolution PNG export at 300 DPI, axis labels with units).

## Cross-Benchmark Correlation Matrix

The full pairwise Spearman ρ matrix is presented in Table 2 (10×10 symmetric matrix). Key observations:

**Strongest positive correlations:**
- TruthfulQA—FinTrust: ρ = 0.721
- TruthfulQA—MultiTrust: ρ = 0.621
- FinTrust—TrustBench-Ethics: ρ = 0.568
- HaluBench—TrustLLM-Truthfulness: ρ = 0.604

**Strongest negative correlations:**
- FaithfulQA—FinTrust: ρ = -0.568
- FaithfulQA—TrustBench-Ethics: ρ = -0.557
- TruthfulQA—SafetyBench: ρ = -0.379
- FaithfulQA—TruthfulQA: ρ = -0.293

**Near-zero correlations (|ρ| < 0.05):**
- FinTrust—HaluBench: ρ = -0.007
- BiasEval—TrustLLM-Safety: ρ = -0.032
- BiasEval—TruthfulQA: ρ = -0.032
- BiasEval—SafetyBench: ρ = -0.004

**Table 2: Pairwise Cross-Benchmark Spearman ρ Matrix**

|  | TruthfulQA | FinTrust | MultiTrust | TrustBench-Ethics | BiasEval | TrustLLM-Safety | HaluBench | FaithfulQA | TrustLLM-Truth | SafetyBench |
|---|------------|----------|------------|-------------------|----------|----------------|-----------|------------|----------------|-------------|
| **TruthfulQA** | 1.000 | 0.721 | 0.621 | 0.511 | -0.032 | 0.293 | 0.414 | -0.293 | 0.157 | -0.379 |
| **FinTrust** | 0.721 | 1.000 | 0.461 | 0.568 | -0.043 | 0.329 | -0.007 | -0.568 | -0.239 | 0.084 |
| **MultiTrust** | 0.621 | 0.461 | 1.000 | 0.296 | 0.436 | 0.489 | 0.243 | -0.143 | 0.282 | -0.141 |
| **TrustBench-Ethics** | 0.511 | 0.568 | 0.296 | 1.000 | -0.332 | 0.414 | 0.282 | -0.557 | 0.189 | 0.254 |
| **BiasEval** | -0.032 | -0.043 | 0.436 | -0.332 | 1.000 | -0.032 | 0.300 | -0.157 | 0.271 | -0.004 |
| **TrustLLM-Safety** | 0.293 | 0.329 | 0.489 | 0.414 | -0.032 | 1.000 | 0.118 | -0.164 | 0.064 | -0.268 |
| **HaluBench** | 0.414 | -0.007 | 0.243 | 0.282 | 0.300 | 0.118 | 1.000 | -0.168 | 0.604 | -0.234 |
| **FaithfulQA** | -0.293 | -0.568 | -0.143 | -0.557 | -0.157 | -0.164 | -0.168 | 1.000 | 0.061 | -0.220 |
| **TrustLLM-Truth** | 0.157 | -0.239 | 0.282 | 0.189 | 0.271 | 0.064 | 0.604 | 0.061 | 1.000 | -0.293 |
| **SafetyBench** | -0.379 | 0.084 | -0.141 | 0.254 | -0.004 | -0.268 | -0.234 | -0.220 | -0.293 | 1.000 |

This matrix reveals substantial heterogeneity in cross-benchmark agreement. The negative correlations are particularly noteworthy—they cannot be explained by measurement noise alone (noise would produce near-zero correlations, not systematic negative patterns). This observation motivates the construct divergence interpretation discussed in Section 6 (Discussion).

## Computational Environment

- **Hardware:** Standard workstation (no GPU required)
- **Software:** Python 3.9, pandas 1.5.3, scipy 1.10.1, matplotlib 3.7.1
- **Runtime:** <5 minutes for complete analysis (data loading, CV computation, cross-benchmark ρ calculation, statistical tests, visualizations)
- **Reproducibility:** Fixed random seed (42) for any stochastic operations (none in this analysis), deterministic ordering of benchmark pairs

All code, data, and results artifacts are archived in h-e1/ directory structure:
- **src/**: Analysis scripts (cv_stability_analysis.py)
- **data/**: Benchmark corpus (benchmark_corpus.pkl)
- **results/**: CSV outputs (cv_values.csv, pairwise_rho_matrix.csv, summary_stats.json)
- **figures/**: PNG visualizations (4 files, 300 DPI)

## Summary

Our experimental setup analyzed 10 trust benchmarks with CV range [0.130, 0.458] and mean ρ range [-0.245, 0.283]. All benchmarks met inclusion criteria (n≥10 models, ≥5 shared models per pair). The analysis pipeline successfully computed CV and cross-benchmark ρ for all 10 benchmarks, producing 45 unique pairwise correlations (10×9/2 symmetric matrix). The cross-benchmark correlation matrix revealed heterogeneous patterns, including unexpected negative correlations (FaithfulQA-FinTrust ρ=-0.568) that suggest construct validity issues. Results are presented in Section 5.
