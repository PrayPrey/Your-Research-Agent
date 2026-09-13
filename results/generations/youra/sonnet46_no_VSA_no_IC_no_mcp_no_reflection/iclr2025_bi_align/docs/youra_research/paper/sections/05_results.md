# Results

Our experiments reveal one strong and unexpected finding, one infrastructure failure, and one measurement failure. The combination constitutes the empirical record for the BAA existence test and motivates a reframing of what "detecting BAA" requires.

## Cohort Construction

Figure 3 shows the WildChat-1M retention funnel. Of the full WildChat-1M population, 27,902 users satisfy the ≥3 monthly bin criterion with ≥50 users per bin over the analysis window. The effective analysis period is April 2023 – April 2024 (13 monthly bins), constrained by the ≥50 cohort-size floor. Pre-April 2023 data is absent or below threshold density; post-April 2024 data was not available in our WildChat-1M snapshot.

The 13-bin window is shorter than the planned 24 bins (January 2023 – December 2024), which reduces Mann-Kendall power. The analysis cohort represents high-engagement users — users who interact with the WildChat platform in ≥3 distinct months over a 13-month window are, by construction, non-casual users. This selection property is the paper's central interpretive challenge.

## Gate Evaluation Summary

Table 1 presents the gate evaluation results across all three proxies. The gate criterion (≥2/3 proxies significant at p < 0.05 with |τ| ≥ 0.2) is not met.

**Table 1.** Mann-Kendall gate evaluation for all three behavioral proxies (h-e1-v2).

| Proxy | Measure | τ | 95% CI | p | ACF lag-1 | Method | Gate |
|-------|---------|---|--------|---|-----------|--------|------|
| P1: Prompt tokens | Monthly mean token count | **+0.744** | [0.415, 0.972] | **0.0005** | 0.634 | Hamed-Rao | FAIL (direction) |
| P2: Vote entropy | Shannon H over win/lose/tie | N/A | N/A | N/A | N/A | — | FAIL (no data) |
| P3: Correction freq | Fraction of turns with explicit correction | 0.051 | [−0.441, 0.536] | 0.855 | 0.168 | Hamed-Rao | FAIL |

**n_significant = 1/3 → Gate FAILED (threshold: ≥2/3).**

Figure 1 visualizes the gate results as a τ ± 95% CI bar chart with PASS/FAIL color coding. The figure makes clear that Proxy 1 is strongly significant while Proxies 2 and 3 are not, and that Proxy 1's direction (positive τ) is opposite to the BAA disengagement prediction.

## Proxy 1: Prompt Token Count — Strong Positive Trend

**Returning WildChat users' prompt length increases significantly over 2023–2024 (τ = +0.744, p = 0.0005).** This is the paper's central empirical finding.

Figure 2 shows the monthly time series of mean prompt token count for the returning-user cohort. The trend is monotonically increasing from approximately 180 tokens in April 2023 to approximately 832 tokens in April 2024 — a 4.6× growth over 13 months. The series exhibits strong autocorrelation (ACF lag-1 = 0.634), confirming that the Hamed-Rao correction is necessary: the standard Mann-Kendall test would produce an inflated false positive rate under this autocorrelation structure.

The 95% bootstrap CI [0.415, 0.972] does not overlap with τ = 0, and the lower bound substantially exceeds the effect threshold (|τ| ≥ 0.2). This result is not borderline: the effect is large, robust to autocorrelation correction, and consistent across two independent experiment rounds (h-e1: τ = +0.564, p = 0.007; h-e1-v2: τ = +0.744, p = 0.0005).

**This result is opposite to the BAA directional prediction (τ < 0).** The BAA framework predicts that as AI quality improves, prompt complexity declines — users offload elaboration to AI and need to specify less. The observed positive trend falsifies this directional prediction for the most reliable proxy. Whether this constitutes a refutation of BAA or merely a measurement artifact of the cohort design is the interpretive question we address in the Discussion.

## Proxy 2: Vote Shannon Entropy — Not Computed

The LMSYS primary dataset (`lmsys/chatbot_arena_conversations`) is access-gated on HuggingFace. We successfully loaded the fallback dataset (`lmsys/lmsys-arena-human-preference-55k`) but found it contains no timestamp field (`tstamp`), making monthly temporal binning impossible. No vote entropy time series can be computed from publicly available LMSYS data.

This is not a failure of the entropy methodology — the `scipy.stats.entropy` implementation is correct and verified against synthetic data in the smoke test. It is an infrastructure access failure that blocks Proxy 2 entirely. The central LMSYS-based BAA test (declining vote entropy as ELO improves) is untestable under current public data access conditions.

## Proxy 3: Correction/Negation Frequency — No Detectable Signal

Explicit correction/negation frequency shows no temporal trend in the returning-user cohort (τ = 0.051, p = 0.855). The 95% bootstrap CI [−0.441, 0.536] spans zero symmetrically. The ACF lag-1 = 0.168 triggers the Hamed-Rao correction, which does not substantially alter the conclusion.

The monthly base rate of the correction regex pattern is approximately 0.05% of turns. This near-zero signal level means the Mann-Kendall test has effectively no power: a time series that oscillates near zero with small random noise will produce τ ≈ 0 regardless of any underlying behavioral change. The proxy fails not because corrections don't happen, but because explicit verbal corrections (`"no,"`, `"actually,"`, `"that's wrong"`) are extremely rare in naturalistic AI interaction — users more commonly correct implicitly by rephrasing or resubmitting.

Figure 2 includes the Proxy 3 monthly time series alongside Proxy 1 for direct comparison. The contrast illustrates the measurement challenge: Proxy 1 yields a strong, trending signal while Proxy 3 yields near-zero noise.

## Internal Replication: h-e1 vs. h-e1-v2

The h-e1-v2 Proxy 1 result (τ = +0.744) replicates and strengthens the h-e1 result (τ = +0.564). Both are positive and statistically significant; h-e1-v2 shows a larger effect and lower p-value, consistent with the tighter cohort construction (stricter min_bins and explicit bin-size floor). The direction and significance are consistent across methodological variants, indicating the positive trend is not an artifact of any single analysis choice.

Appendix Figures A1–A2 reproduce the h-e1 gate summary and time series for reference.
