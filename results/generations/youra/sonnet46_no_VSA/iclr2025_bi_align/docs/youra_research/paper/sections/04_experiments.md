# 4. Experimental Setup

## 4.1 Experimental Questions

Our experimental design is structured around four sub-hypotheses, each addressing a distinct verification question in a sequential pipeline:

**EQ1 (H-E1):** Is the data infrastructure valid for cross-dataset correlation analysis? Specifically, does fuzzy joining of LLM Leaderboard v1 names with the bias benchmark yield N ≥ 30 complete rows with valid scores?

**EQ2 (H-M1):** Does MMLU function as a substantive scale covariate for both alignment benchmarks? We require R²(MMLU × TruthfulQA) > 0.05 and R²(MMLU × BBQ-proxy) > 0.05 — both gates must pass for the partial Spearman analysis to be meaningful.

**EQ3 (H-M2):** Is the reduction from raw to partial Spearman rho statistically significant? We test p < 0.05 OR non-overlapping BCa 95% CIs (either criterion sufficient; both are reported). This is the primary hypothesis of the paper.

**EQ4 (H-M3):** Can the residual partial_rho be assigned to a pre-specified structural scenario? We classify into: scenario (a) independent (|rho| < 0.20), scenario (b) coherent (rho > 0.40), scenario (c) tradeoff (rho < −0.20), or AMBIGUOUS (grey zone), with CI analysis as a secondary criterion.

## 4.2 Datasets

**Open LLM Leaderboard v1 (LLM LB v1).** Approximately 500 open-weight LLM evaluation records containing MMLU aggregate accuracy, TruthfulQA MC2 accuracy, and ARC Challenge normalized accuracy per model. Publicly available; accessed via HuggingFace datasets.

**BBQ Proxy: ARC Challenge.** Due to the unavailability of genuine HELM Lite BBQ per-model scores (see Section 3.7), we use ARC Challenge normalized accuracy from the same LLM LB v1 CSV as a proxy for bias avoidance. ARC Challenge measures logical reasoning in a multiple-choice format; it does not directly measure social bias. All claims about "bias avoidance" are qualified as reflecting performance on this proxy.

**Analysis Dataset.** Inner join on `model_name` between the LLM LB v1 CSV (N=500) and a separate BBQ proxy file (N=300), yielding N=297 matched models, reduced to N=296 after removing rows with missing values on any of the three analysis columns (TruthfulQA MC2, BBQ-proxy, MMLU). The final N=296 far exceeds our pre-specified minimum of N≥30.

## 4.3 Baselines

For EQ3 (the primary test), we compare:

- **Raw Spearman rho:** Standard Spearman rank correlation between TruthfulQA and BBQ-proxy, without MMLU control. This is the baseline that prior work would typically report.
- **Partial Spearman rho:** MMLU-controlled rank correlation via `pingouin.partial_corr(method='spearman', covar=['MMLU'])`. This is our proposed corrected estimate.

The Fisher z difference between these two estimates is the primary test statistic.

For EQ4 (scenario classification), the pre-specified scenario boundaries serve as classification thresholds:

| Boundary | Value | Scenario |
|----------|-------|----------|
| Lower independence threshold | |rho| < 0.20 | Scenario (a): independent constructs |
| Upper coherence threshold | rho > 0.40 | Scenario (b): scale-free coherence |
| Tradeoff threshold | rho < −0.20 | Scenario (c): alignment tradeoff |

These boundaries were pre-specified prior to data analysis to avoid post-hoc threshold selection.

## 4.4 Evaluation Metrics and Success Criteria

| Sub-Hypothesis | Gate Type | Success Criterion | Pre-registered |
|----------------|-----------|------------------|----------------|
| H-E1 | MUST_WORK | N_complete ≥ 30 after join | Yes |
| H-M1 | MUST_WORK | R²(MMLU×TruthfulQA) > 0.05 AND R²(MMLU×BBQ) > 0.05 | Yes |
| H-M2 | MUST_WORK | p < 0.05 (Fisher z) OR non-overlapping BCa 95% CIs | Yes |
| H-M3 | SHOULD_WORK | Any scenario assigned (including AMBIGUOUS) | Yes |

For H-M2, BCa confidence intervals are computed via clustered bootstrap (B=5000, seed=42) with model family as the clustering unit, providing robustness to within-family correlation among related models.

## 4.5 Implementation

All analyses were implemented in Python 3.11. Core statistical libraries: scipy ≥ 1.10, pingouin ≥ 0.5, pandas ≥ 1.5, numpy ≥ 1.23. Fuzzy string matching: rapidfuzz 3.x. Visualization: matplotlib ≥ 3.6, seaborn ≥ 0.12. Each sub-hypothesis has a dedicated analysis directory (`h-e1/`, `h-m1/`, `h-m2/`, `h-m3/`) with self-contained code, tests (pytest), and output artifacts. Total: 57/57 test cases pass across all sub-hypotheses (H-E1: 13, H-M1: 11, H-M2: 12, H-M3: 16).
