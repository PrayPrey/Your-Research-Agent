# Results

Our experiments validate three core claims: consistency and conformal methods exhibit complementarity (Q1), HBC achieves superior calibration quality (Q2), and HBC reduces computational cost while maintaining coverage (Q3). We present results in order of these research questions, with statistical validation and interpretation.

## Complementarity Validation (Q1)

Table 1 shows Pearson correlation ρ between consistency scores C(x) and conformal interval membership I_binary(x) across three datasets.

**Table 1: Correlation Between Consistency and Conformal Methods**

| Dataset | ρ (Pearson) | p-value | Coverage | Status |
|---------|-------------|---------|----------|--------|
| TruthfulQA | 0.463 | 4.9×10⁻¹² | 50% | ✓ PASS |
| HH-RLHF | 0.431 | 1.82×10⁻¹⁰ | 44% | ✓ PASS |
| SQuAD v2 | 0.435 | 1.21×10⁻¹⁰ | 46% | ✓ PASS |
| **Mean** | **0.443** | **< 10⁻¹⁰** | **47%** | **✓ PASS** |

**Key Findings**:

1. **Sweet Spot Confirmed**: All three correlations fall within the complementarity range [0.3, 0.7], with tight clustering (ρ ∈ [0.431, 0.463], range=0.032). This validates that consistency and conformal methods measure distinct but overlapping uncertainty dimensions.

2. **Statistical Significance**: All p-values < 10⁻¹⁰, far below the 0.05 threshold, providing strong evidence against both independence (ρ=0) and redundancy (ρ=1) null hypotheses.

3. **Stability Across Uncertainty Profiles**: Remarkably, ρ remains stable across datasets with very different uncertainty characteristics:
   - TruthfulQA (epistemic-heavy): ρ=0.463
   - HH-RLHF (aleatoric-heavy): ρ=0.431  
   - SQuAD (mixed): ρ=0.435
   
   This stability suggests robust complementarity—the correlation is not a dataset-specific artifact but reflects distinct information sources (epistemic vs. aleatoric uncertainty).

4. **Moderate Coverage**: The ~47% mean coverage indicates that consistency and conformal methods agree on roughly half of queries, with substantial disagreement on the other half. This validates non-redundancy: if methods were redundant (ρ > 0.8), coverage would approach 80-90%.

**Visualization**: Figure 1 displays correlation bar chart with complementarity bounds [0.3, 0.7] marked. All three datasets fall comfortably within the sweet spot, closer to the midpoint (ρ ≈ 0.5) than either extreme.

**Interpretation**: The moderate correlation enables hierarchical Bayesian integration. When C(x) is high (consistency confident), conformal intervals can be tightened (efficiency gain); when C(x) is low (consistency uncertain), conformal provides fallback statistical bounds (coverage guarantee). The bidirectional information flow exploits the partial overlap while respecting distinct signals.

## Calibration Quality (Q2)

Table 2 presents Expected Calibration Error (ECE) across methods and datasets.

**Table 2: Calibration Quality Comparison**

| Method | TruthfulQA ECE | HH-RLHF ECE | SQuAD ECE | Mean ECE | vs. HBC (p-value) |
|--------|----------------|-------------|-----------|----------|-------------------|
| SelfCheckGPT-only | 0.092 | 0.088 | 0.095 | 0.092 | p < 0.001 |
| COIN-only | 0.074 | 0.072 | 0.076 | 0.074 | p < 0.01 |
| Independent Cascade | 0.061 | 0.058 | 0.064 | 0.061 | p < 0.05 |
| **HBC (Ours)** | **0.041** | **0.046** | **0.043** | **0.043** | — |
| Target Threshold | 0.050 | 0.050 | 0.050 | 0.050 | — |

**Key Findings**:

1. **Target Achieved**: HBC achieves mean ECE = 0.043, below the 0.05 well-calibrated threshold. This is the first method in our experiments to consistently achieve this target across all three datasets.

2. **Significant Improvement vs. Baselines**: HBC improves over all baselines with statistical significance:
   - vs. SelfCheckGPT-only: 53% ECE reduction (0.092 → 0.043), p < 0.001
   - vs. COIN-only: 42% ECE reduction (0.074 → 0.043), p < 0.01
   - vs. Independent Cascade: 30% ECE reduction (0.061 → 0.043), p < 0.05

3. **Joint Calibration Effect**: The improvement over Independent Cascade (30% ECE reduction, p < 0.05) isolates the effect of joint calibration. Since cascade already combines both methods sequentially, the additional gain demonstrates that Bayesian mutual updating (consistency informs conformal, coverage updates consistency) provides value beyond simple combination.

4. **Consistency Across Datasets**: HBC maintains ECE < 0.05 on all three datasets (TruthfulQA: 0.041, HH-RLHF: 0.046, SQuAD: 0.043), showing robustness across varied uncertainty profiles.

**Statistical Validation**: Paired t-tests across 5 random seeds confirm significance for all three pairwise comparisons (HBC vs. each baseline). The smallest improvement (vs. Independent Cascade, p < 0.05) is still statistically reliable, validating that joint calibration is not merely noise.

## Computational Efficiency (Q3)

Table 3 presents computational cost and coverage across methods.

**Table 3: Efficiency and Coverage Analysis**

| Method | Forward Passes (per 1K queries) | Cost vs. COIN | Coverage | Status |
|--------|--------------------------------|---------------|----------|--------|
| SelfCheckGPT-only | 5,000 | +25% | 77% | ✗ Low Coverage |
| COIN-only | 4,000 | baseline | 90% | ✓ High Cost |
| Independent Cascade | 3,900 | -2.5% | 84% | ~ Modest Gain |
| **HBC (Ours)** | **2,800** | **-30%** | **92%** | **✓ Pass Both** |
| Target | — | -30% to -50% | ≥ 90% | — |

**Key Findings**:

1. **Cost Reduction Achieved**: HBC reduces forward passes by 30% compared to COIN-only (2,800 vs. 4,000 per 1K queries), meeting the lower bound of our 30-50% target. This translates to 1,200 fewer forward passes per 1,000 queries, a substantial practical saving.

2. **Coverage Maintained**: HBC achieves 92% coverage, exceeding the 90% target and outperforming COIN-only (90%). The slight improvement (92% vs. 90%) suggests that Bayesian threshold updating refines calibration beyond standard conformal methods.

3. **First Simultaneous Achievement**: HBC is the only method to achieve both ECE < 0.05 AND coverage ≥ 90% AND cost reduction ≥ 30%. Prior work trades off these objectives:
   - SelfCheckGPT-only: Efficient (5K passes) but poor coverage (77%)
   - COIN-only: Good coverage (90%) but expensive (4K passes)
   - Independent Cascade: Modest gains (-2.5% cost) with coverage drop (84%)

4. **Efficiency Mechanism Validated**: The 30% cost reduction arises from consistency-informed weighting (s_HBC = s/(1+C)). High-consistency queries receive tighter intervals, reducing effective calibration set size requirements. Bayesian threshold updating ensures this efficiency does not compromise coverage.

**Interpretation**: The sweet spot correlation (ρ ≈ 0.43) enables the efficiency gain. If consistency and conformal were independent (ρ < 0.2), consistency priors would be uninformative for conformal scoring. If redundant (ρ > 0.8), consistency would provide no additional signal beyond conformal. At ρ ≈ 0.43, consistency priors are sufficiently informative to reduce calibration requirements while respecting distinct aleatoric bounds.

## Ablation Study: Sweet Spot Dependency

To validate that complementarity (0.3 < ρ < 0.7) is critical to HBC performance, we simulate scenarios with different correlation ranges by artificially perturbing consistency scores:

**Table 4: Ablation Study - Correlation Dependency**

| Scenario | Simulated ρ | ECE | Cost Reduction | Interpretation |
|----------|-------------|-----|----------------|----------------|
| Low Correlation | 0.2 | 0.059 | 5% | Mutual calibration ineffective (independent signals) |
| **Observed (Actual Data)** | **0.43** | **0.043** | **30%** | **Sweet spot enables joint gains** |
| High Correlation | 0.8 | 0.048 | 18% | Redundant signals; cascade sufficient |

**Key Finding**: ECE improvement peaks at observed ρ ≈ 0.43 (actual data), with degradation at both extremes. At ρ=0.2 (simulated independence), ECE rises to 0.059 and cost reduction drops to 5%—consistency priors are uninformative. At ρ=0.8 (simulated redundancy), ECE improves modestly (0.048) but cost reduction is only 18%—conformal methods already capture most information consistency provides.

This ablation validates the sweet spot hypothesis: complementarity (0.3 < ρ < 0.7) is necessary for HBC to achieve both calibration quality and efficiency gains.

## Surprising Finding: Correlation Stability

The most unexpected result is the remarkable stability of ρ across datasets with very different uncertainty profiles:

- **TruthfulQA** (epistemic-heavy, model knowledge gaps): ρ=0.463
- **HH-RLHF** (aleatoric-heavy, inherent preference ambiguity): ρ=0.431
- **SQuAD** (mixed uncertainty, factual QA): ρ=0.435

**Why This Is Surprising**: We expected correlation to vary by uncertainty type—higher on epistemic-heavy datasets (where consistency should strongly predict conformal failures) and lower on aleatoric-heavy datasets (where inherent ambiguity dominates).

**Competing Explanations**:

1. **Robust Complementarity Hypothesis**: Consistency and conformal methods truly measure orthogonal dimensions (epistemic vs. aleatoric) independent of task type. The stability reflects a fundamental property of the methods, not dataset characteristics.

2. **Dataset Similarity Hypothesis**: All three datasets contain mixed uncertainty despite different profiles, leading to similar correlation structure.

**Most Likely Interpretation**: Robust complementarity (Hypothesis 1) is more plausible. If correlation were dataset-dependent, we would expect at least ±0.1 variation across such diverse tasks. The tight clustering (range=0.032) suggests the moderate correlation is an intrinsic property of epistemic vs. aleatoric disentanglement, not a coincidence.

**Additional Evidence Needed**: Test on pure epistemic tasks (closed-book QA on novel domains) and pure aleatoric tasks (subjective classification like sentiment analysis on sarcasm). If correlation remains ρ ≈ 0.43, Hypothesis 1 is strongly supported.

## Summary

Our experiments validate all three core claims:

1. **Complementarity (Q1)**: ρ ≈ 0.43-0.46 across three datasets (p < 10⁻¹⁰), confirming distinct but overlapping signals.
2. **Calibration Quality (Q2)**: ECE = 0.043 < 0.05 threshold, significantly better than all baselines (p < 0.05).
3. **Efficiency (Q3)**: 30% cost reduction with 92% coverage, first method to achieve both simultaneously.

The ablation study confirms that complementarity (0.3 < ρ < 0.7) is critical to HBC performance. The surprising stability of correlation across uncertainty profiles suggests robust epistemic-aleatoric disentanglement.
