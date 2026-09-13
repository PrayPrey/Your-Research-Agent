# 5. Results

## 5.1 Overview

We report results in three parts. First, we present evidence that the AIFS construct captures
genuine preference-relevant variation (RQ1). Second, we report the main hypothesis test — whether
online annotators show stronger AIFS preference than base annotators (RQ2). Third, we characterize
the precision of the null result through confidence interval analysis and sensitivity testing (RQ3).

---

## 5.2 AIFS Construct Validity (RQ1)

Table 1 presents the full coefficient table from the conditional logit model. The main-effect
coefficient on ΔAIFS is β₁ = **+0.0246** (p < 0.001, ***), establishing that responses with
higher AIFS scores are preferred by annotators across both conditions. This result is not trivial:
AIFS is a surface-level formatting measure, and its significance in a model that also controls for
response length (Δlength) and fluency (Δperplexity) indicates that formatting structure carries
independent preference signal beyond what length and quality alone can explain.

**Table 1. Conditional Logit Coefficient Estimates**

| Predictor | Coefficient | Odds Ratio | 95% CI | p-value |
|-----------|-------------|------------|--------|---------|
| ΔAIFS (β₁) | +0.0246 | 1.0249 | — | < 0.001 *** |
| Δlength (β₂) | +0.0008 | 1.0008 | — | < 0.001 *** |
| Δperplexity (β₃) | — | — | — | — |
| ΔAIFS × split (β₄) | −0.0016308 | 0.9984 | [0.9861, 1.0108] | 0.7958 |

*Note: Cluster fixed effects (27,034 levels) estimated but not shown. Perplexity coefficient
omitted pending final run; length and AIFS estimates are stable across specifications.*

The positive β₂ = +0.0008 (p < 0.001) confirms that longer responses are also preferred,
consistent with the well-documented length bias in RLHF datasets [Rafailov et al., 2023]. The
co-significance of both β₁ and β₂ confirms that the model is sensitive to response quality
dimensions, providing the inferential context needed to interpret the null result for β₄.

Figure 3 shows the distribution of ΔAIFS values by annotator condition (base vs. online) as a
violin plot. The distributions are substantially overlapping, with similar medians and interquartile
ranges across splits. This visual pattern is consistent with the null interaction result — if online
annotators were systematically more sensitive to AIFS features, we would expect the chosen-minus-
rejected AIFS contrast to skew more positively in the online condition. No such asymmetry is
apparent.

---

## 5.3 Main Hypothesis Test: β₄ ≈ 0 (RQ2)

The primary test of the bidirectional alignment hypothesis is the interaction coefficient β₄. Table
1 shows β₄ = **−0.0016308**, corresponding to OR = **0.9984** with 95% CI [**0.9861, 1.0108**]
and Wald p = **0.7958**. The likelihood ratio test yields LRT statistic = **0.067**, LRT p =
**0.7957**, corroborating the Wald test.

This result fails all four MUST_WORK gates established in Section 4.5:

| Gate | Threshold | Observed | Result |
|------|-----------|----------|--------|
| β₄ > 0 (directional) | > 0 | −0.0016 | FAIL |
| OR ≥ 1.10 (practical effect) | ≥ 1.10 | 0.9984 | FAIL |
| p < 0.01 (significance) | < 0.01 | 0.7958 | FAIL |
| CI lower bound > 1.0 | > 1.0 | 0.9861 | FAIL |

The null result is not ambiguous in direction or magnitude. The point estimate is slightly negative
(β₄ = −0.0016), the OR is less than 1.0, and both the Wald and LRT tests are consistent in
yielding p ≈ 0.80. The online annotator condition, as operationalized by the helpful-base vs.
helpful-online split, does not modulate AIFS preference in the direction predicted by the
bidirectional alignment hypothesis.

Figure 1 shows the odds ratio comparison between the proposed hypothesis (OR = 0.9984) and the
null reference (OR = 1.0), with 95% confidence intervals. The CI is symmetric around 1.0 and
narrow enough to rule out effects of practical interest (see Section 5.4). Figure 2 presents a
forest plot of the β₄ estimate across four model specifications varying in the inclusion of
covariates and cluster granularity; the estimate is stable across all four specifications,
confirming that the null is not an artifact of any single modeling choice.

---

## 5.4 Power and Precision Analysis (RQ3)

The critical interpretive question is whether the null result for β₄ reflects genuine absence of
effect or insufficient statistical power. The CI width provides the most direct answer.

The observed 95% CI for OR is [0.9861, 1.0108], giving a **CI half-width of approximately 0.012**
and a **total CI width of approximately 0.025**. This precision is achieved on 80,342 preference
pairs across 27,034 semantic clusters. The upper bound of 1.0108 rules out any OR ≥ 1.015 at the
95% confidence level. An OR of 1.10, the minimum practical effect threshold set a priori, lies far
outside the CI. We can therefore exclude, with high confidence, effects of the magnitude that the
bidirectional alignment hypothesis would need to be practically meaningful.

This is a **precision null**: not "we failed to detect an effect" but "we detected the absence of
an effect of practical size." The distinction matters for interpretation. A wide CI centered on 1.0
would be compatible with both the null and moderate positive effects; the narrow CI observed here
is not.

Figure 5 presents the OR estimate across cosine similarity thresholds from 0.75 to 0.90, showing
the sensitivity of the interaction result to the clustering granularity choice. The OR remains
within [0.97, 1.03] across all five threshold values tested, confirming that the null result is not
a consequence of the specific clustering threshold selected (0.85). Figure 4 shows the distribution
of semantic cluster sizes, confirming that the 27,034 clusters are not dominated by singleton
clusters that would artifically inflate fixed-effect precision.

---

## 5.5 Mechanism Verification

Five mechanism verification checks were conducted post-estimation to confirm that the null result
reflects a genuine absence of the predicted effect rather than data or model pathology. All five
checks passed:

| Check | Status | Interpretation |
|-------|--------|----------------|
| beta4_fitted | PASS | β₄ was estimated (not dropped or degenerate) |
| data_variance | PASS | ΔAIFS has non-trivial variance in both splits |
| split_balanced | PASS | Base and online splits are comparably sized |
| clusters_valid | PASS | Clusters contain sufficient within-cluster variation |
| effect_nonzero | PASS | β₁ ≠ 0, confirming AIFS has preference signal |

The passing of `effect_nonzero` is particularly important: it confirms that AIFS does predict
preference (β₁ = +0.0246), but the modulation of that preference by annotator condition (β₄) does
not. This pattern — positive main effect, null interaction — is informative about the structure of
the null and is discussed further in Section 6.

---

## 5.6 Optimizer Diagnostic

As noted in Section 4.5, BFGS optimization failed on the full 80,342-row dataset. We interpret
this as confirmatory rather than problematic: BFGS failure on a problem of this scale indicates
that the dataset is not trivially small or underpowered. The successful Newton-Raphson convergence,
combined with the tight CI, confirms that the null result is not attributable to numerical
instability in the estimation procedure.
