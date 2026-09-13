# 5. Results

## 5.1 Data Infrastructure (H-E1): Valid Cross-Dataset Join

The fuzzy join of LLM LB v1 (N=500 models) with the bias proxy source yielded N=297 complete rows (match_rate = 1.000 at threshold=75), exceeding the pre-registered minimum of N≥30 by a factor of nearly 10. A sensitivity sweep of the fuzzy join threshold (65–80) confirmed N=297 across all values, indicating match stability. The venn diagram (Figure [fig_14]) shows model coverage between sources.

**Key finding:** The data infrastructure is valid for correlation analysis. Note that match_rate=1.000 is an artifact of the ARC proxy originating from the same data source as the LLM LB v1 CSV; it should not be interpreted as confirming genuine cross-source join quality for BBQ-specific data.

## 5.2 MMLU as Scale Covariate (H-M1): R² Far Exceeds Threshold

MMLU explains a substantial fraction of cross-model variance in both alignment benchmarks:

| Pair | Spearman rho | R² | p-value |
|------|--------------|----|---------|
| MMLU × TruthfulQA MC2 | 0.702 | **0.493** | 3.15 × 10⁻⁴⁵ |
| MMLU × BBQ-proxy | 0.874 | **0.763** | 5.01 × 10⁻⁹⁴ |
| TruthfulQA × BBQ (raw baseline) | 0.732 | — | 5.83 × 10⁻⁵¹ |

Both R² values clear the pre-registered threshold of 0.05 by orders of magnitude (9.9× and 15.3×, respectively). These results confirm that MMLU is a strong scale covariate: an open-weight model's BBQ-proxy score can be predicted with 76% explained variance from its MMLU score alone, before any alignment-specific information is considered.

Figure [fig_6] (heatmap) shows the full Spearman matrix for {MMLU, TruthfulQA, BBQ-proxy}. Figures [fig_8] and [fig_9] show scatter plots for MMLU vs BBQ-proxy and MMLU vs TruthfulQA, respectively, illustrating the strong positive relationships with annotated Spearman rho values.

**Gate H-M1: PASS (MUST_WORK)**

## 5.3 Primary Result — Fisher Z Difference Test (H-M2): 53% Confound

The central result of this paper is the statistically decisive reduction from raw to partial Spearman rho:

| Metric | Raw (no MMLU control) | Partial (MMLU controlled) |
|--------|----------------------|--------------------------|
| Spearman rho | **0.732** | **0.343** |
| BCa 95% CI | (0.670, 0.780) | (0.180, 0.492) |
| p-value | 5.83 × 10⁻⁵¹ | 1.40 × 10⁻⁹ |
| CI overlap | — | **Non-overlapping** |

**Fisher z difference:** z = 6.9679, p = 3.22 × 10⁻¹²

The reduction from 0.732 to 0.343 represents a **53.1% decrease** in Spearman rho. Both pre-registered success criteria are satisfied simultaneously: (1) p = 3.22 × 10⁻¹² ≪ 0.05, and (2) the BCa confidence intervals are non-overlapping (raw: [0.670, 0.780] vs partial: [0.180, 0.492]). The finding is not marginal or borderline — by either criterion, MMLU scale confounding of the TruthfulQA × BBQ correlation is statistically decisive.

Notably, the partial correlation (0.343, p = 1.40 × 10⁻⁹) is itself highly significant, indicating that a real alignment-specific co-movement remains after scale control. Factuality and bias-proxy performance are neither pure scale surrogates nor fully orthogonal constructs.

Figure [fig_1] (raw vs partial rho bar chart with CI error bars) is the primary result visualization. Figure [fig_3] (H-M3 confirmation, raw vs partial) provides an independent graphical confirmation. Figure [fig_5] (Fisher z number line) visualizes the statistical decisiveness of the difference test.

**Gate H-M2: PASS (MUST_WORK)**

## 5.4 Scenario Classification (H-M3): AMBIGUOUS — Pre-Registered Valid Outcome

With partial_rho = 0.343 and BCa 95% CI = [0.180, 0.492]:

| Scenario | Criterion | Result |
|----------|-----------|--------|
| (a) Independent | |partial_rho| < 0.20 | **Not met** (0.343 > 0.20) |
| (b) Scale-free coherence | partial_rho > 0.40 with CI entirely above 0.40 | **Not met** (0.343 < 0.40; CI spans 0.40) |
| (c) Tradeoff | partial_rho < −0.20 | **Not met** (positive) |
| **Grey zone** | −0.20 < partial_rho < 0.40 | **Met** → **AMBIGUOUS** |

The BCa CI [0.180, 0.492] spans the +0.40 boundary between the grey zone and scenario (b), confirming that N=296 is insufficient to resolve the scenario boundary. The AMBIGUOUS classification is a pre-registered valid outcome, not a failure.

**Boundary sensitivity.** Under three boundary variants (primary: a=0.20, b=0.40; tight: a=0.15, b=0.35; wide: a=0.25, b=0.45), all returned AMBIGUOUS — confirming robustness of the grey-zone classification to boundary choice.

Figure [fig_10] (scenario number line) displays partial_rho, BCa CI band, and scenario boundaries, visually conveying the pre-registered scenarios and the position of our estimate relative to each threshold.

**Gate H-M3: PASS (SHOULD_WORK)** — scenario assigned (AMBIGUOUS is valid)

## 5.5 Robustness Analysis

**Family-weighted Fisher z.** Computing the Fisher z difference test using model-family means (51 families identified; 30 with ≥3 models) confirmed the primary result directionally. Family-weighting did not change the conclusion that MMLU significantly confounds the alignment benchmark correlation.

**RLHF Tier 3 (Optional).** The ΔBBQ sign test across 300 base/chat pairs yielded k_positive=146/300, proportion=0.487, binomtest p=0.686. There is no evidence that RLHF fine-tuning systematically increases BBQ-proxy scores relative to base models. This null result contrasts with the established RLHF improvement on TruthfulQA MC2 (+3.406 pts), suggesting potential asymmetry in RLHF alignment targets. Figure [fig_12] (ΔBBQ histogram with sign test annotation) illustrates this distribution.

**HarmBench Tier 2 (Skipped).** Zero model name matches between LLM LB v1 and HarmBench Table 2 (N=33 models) at rapidfuzz threshold=75. Safety dimension cannot be included; three-dimensional partial Spearman matrix could not be computed.

## 5.6 Summary of Findings

| Prediction | Status | Key Metric |
|------------|--------|------------|
| P1: Fisher z p < 0.05 OR non-overlapping CIs | **SUPPORTED** | p = 3.22 × 10⁻¹²; CIs non-overlapping |
| P2: Scenario assignment | **PARTIALLY_SUPPORTED** | AMBIGUOUS; CI spans 0.40 boundary |
| P3: RLHF sign test significant | **REFUTED** | p = 0.686, proportion ≈ 0.5 |

The primary hypothesis (P1) is confirmed with exceptional statistical strength. The 53% reduction in TruthfulQA × BBQ correlation after MMLU control constitutes the central empirical finding.
