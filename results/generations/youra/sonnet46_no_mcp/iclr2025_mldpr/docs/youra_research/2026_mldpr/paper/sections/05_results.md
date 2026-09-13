# 5. Results

We present results in the order of our three research questions, building from the prerequisite variance check (RQ1) through the primary mechanism test (RQ2) to the practical ablation insight (RQ3).

## 5.1 RQ1: FAIR Score Variance in the OpenML Corpus

**Finding:** The OpenML corpus exhibits sufficient FAIR score polarization for matched-pairs analysis, with a strongly bimodal distribution confirming heterogeneous documentation practices.

Figure 1 shows the distribution of proxy Findable FAIR scores across 5,000 OpenML datasets. The distribution is bimodal (Hartigan's dip test p=9.96e-6), with a pronounced valley near the 0.5 threshold. The coefficient of variation CV=0.1597 marginally exceeds the required 0.15 threshold, and group sizes (n_high=720, n_low=4,280) provide sufficient observations for matched analysis.

| Metric | Value | Gate | Status |
|---|---|---|---|
| CV of proxy FAIR scores | 0.1597 | > 0.15 | **PASS** |
| Bimodality (dip test p) | 9.96e-6 | < 0.05 | **PASS** |
| n_high (score ≥ 0.5) | 720 (14.4%) | ≥ 500 | **PASS** |
| n_low (score < 0.5) | 4,280 (85.6%) | ≥ 500 | **PASS** |

The 85.6% low-FAIR rate is striking: the majority of OpenML datasets score below the 0.5 threshold on our proxy Findable measure. This polarization reflects heterogeneous documentation practices across uploaders and time periods, and confirms that a FAIR compliance intervention would affect the majority of the corpus.

## 5.2 RQ2: Does FAIR Findable Score Predict Shorter Time-to-First-Run?

**Finding:** After propensity matching, high-FAIR datasets reach their first experimental run 28% faster (median 158 vs. 202 days). The unadjusted analysis yields a null result — the confounding reversal is the central empirical finding of this paper.

### 5.2.1 The Confounding Reversal

The most striking result is not the matched analysis itself but the contrast between unadjusted and matched outcomes:

| Analysis | Log-rank p | Interpretation |
|---|---|---|
| **Unadjusted KM** (no matching) | 0.583 | Not significant — naive analysis concludes no FAIR effect |
| **Matched KM** (35 pairs, SMD max=0.098) | **0.0053** | Highly significant — true FAIR effect revealed after confounder removal |

Both analyses use the same datasets, the same proxy-Findable IV, and the same KM log-rank test. The difference is entirely attributable to propensity matching removing the suppressor confounding from dataset age and prominence. This reversal demonstrates that unadjusted FAIR-reuse analyses are unreliable — they can produce qualitatively incorrect conclusions, not merely attenuated estimates.

Figure 2 shows the matched Kaplan-Meier survival curves. The high-FAIR group (solid line) consistently shows higher survival probability (longer TTFR), crossing the 50th percentile at 158 days vs. 202 days for the low-FAIR group — a 44-day reduction in median time-to-first-run.

### 5.2.2 Cox Proportional Hazards Regression

Figure 4 shows the Cox proportional hazards forest plot. The proxy-Findable FAIR score yields:

| Metric | Value | Gate | Status |
|---|---|---|---|
| Cox HR | 3.159 | > 1.2 | **PASS** |
| 95% CI | [1.032, 9.672] | Must exclude 1.0 | **PASS** |
| Cox p-value | 0.044 | — | Significant |

A hazard ratio of 3.159 means that high-FAIR datasets have approximately 3× the instantaneous rate of receiving their first experimental run compared to matched low-FAIR datasets. In practical terms: at any given day after upload, a high-FAIR dataset is three times more likely to attract its first run than a matched low-FAIR dataset.

The wide confidence interval [1.032, 9.672] reflects the small matched sample (35 pairs) and underscores the preliminary nature of these results. The lower bound barely exceeds 1.0, confirming statistical significance but indicating that the true effect could range from modest (HR~1) to very large (HR~10). Production-scale replication is essential for a reliable effect size estimate.

**Note on proportional hazards assumption:** Schoenfeld residual tests flag a potential PH violation in the smoke-test cohort, suggesting the FAIR effect may be time-varying (stronger in early months, weaker later). This should be investigated with stratified Cox models in production-scale analysis.

### 5.2.3 Covariate Balance Validation

Figure 3 (Love plot) shows standardized mean differences before and after matching. All covariates achieve SMD < 0.098 after matching (threshold: < 0.1), confirming that age, task type, and dataset size are balanced between high-FAIR and low-FAIR groups. This balance is the prerequisite for interpreting the matched KM result causally.

## 5.3 RQ3: Sub-criteria Disaggregation vs. Aggregate FAIR Scoring

**Finding:** Aggregate FAIR compliance scoring is effectively uninformative (p=0.697, HR=1.06), while Findable sub-criteria disaggregation reveals a strong significant effect (p=0.005, HR=3.16). This ~100× difference in p-values from the same datasets has direct implications for repository administrators.

| Analysis | Log-rank p | Cox HR | Interpretation |
|---|---|---|---|
| **Findable IV** (primary) | 0.0053 | 3.159 | Strong significant effect |
| **Ablation A: Aggregate threshold** | 0.697 | 1.06 | Near-zero effect |
| **Ablation B: Accessible IV** | 0.064 | 1.79 | Marginal (trend, not significant) |
| **Ablation C: Relaxed caliper** | 0.000 | 3.66 | Robust across caliper settings |

The aggregate FAIR threshold (splitting on overall quality score ≥ 0.5) yields p=0.697 and HR=1.06 — statistically indistinguishable from the null hypothesis. The Findable sub-criteria IV on the same matched pairs yields p=0.0053 and HR=3.159. This demonstrates that different FAIR dimensions have heterogeneous effects on discovery dynamics, and that aggregate scores dilute the Findable signal with dimensions that contribute little to initial discovery speed.

The Accessible ablation (B) shows a marginal trend (p=0.064, HR=1.79), consistent with Accessible properties (open licenses, standard formats) providing secondary discoverability benefits — but this dimension does not achieve statistical significance at the 0.05 threshold.

## 5.4 Sensitivity Analysis: Observation Window Robustness

Figure 5 shows the sensitivity analysis across observation windows. The Findable effect is robust:

| Window | Log-rank p | Cox HR |
|---|---|---|
| 365 days (short-term) | 0.006 | 3.00 |
| **730 days (primary)** | **0.0053** | **3.159** |
| 1095 days (long-term) | 0.005 | 2.93 |

Consistency across 1-3 year windows rules out sensitivity to arbitrary window selection. The effect is present and stable regardless of whether we measure short-term or long-term discovery dynamics, suggesting that the Findable advantage operates throughout the dataset lifetime, not only in the immediate post-upload period.

## 5.5 Summary of Results

| RQ | Finding | Confidence |
|---|---|---|
| RQ1: FAIR variance exists | CV=0.1597, bimodal (p=9.96e-6), n_high=720 | MEDIUM (proxy scores, marginal CV) |
| RQ2: Findable → shorter TTFR | Matched KM p=0.0053; Cox HR=3.159; 28% faster | MEDIUM (smoke-test only, production replication required) |
| RQ3: Sub-criteria > aggregate | Findable p=0.005 vs. aggregate p=0.697 | MEDIUM-HIGH (directionally clear across both metrics) |
| Methodological | Matching is necessary: unadjusted p=0.583 → matched p=0.005 | MEDIUM-HIGH (robust to window; consistent with suppressor theory) |
