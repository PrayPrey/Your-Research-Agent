# Adversarial Review R2: Numerical Verification

**Round**: R2
**Focus**: Mathematical validity, baseline fairness, signal-performance gaps, metric consistency, missing limitations
**Paper**: 06_paper_r1.md
**Date**: 2026-08-31

---

## Numerical Verification Table

| Claim | Paper | Ground Truth | Verified | Notes |
|-------|-------|--------------|----------|-------|
| Token growth: 832/180 = 4.6× | 4.6× | 832/180 = 4.622 | VERIFIED | "approximately" qualifier present |
| Gate arithmetic: 1/3 < 2/3 → FAILED | 1 < 2 → FAIL | 1 < 2 | VERIFIED | Correct |
| Bootstrap CI [0.415, 0.972] does not overlap τ=0 | CI does not include 0 | 0.415 > 0 | VERIFIED | Correct |
| ACF lag-1 = 0.634 > 0.1 → Hamed-Rao | Hamed-Rao applied | 0.634 > 0.1 | VERIFIED | Correct |
| Proxy 3 ACF lag-1 = 0.168 > 0.1 → Hamed-Rao | Table 1: Hamed-Rao | 0.168 > 0.1 | VERIFIED | Consistent with ACF threshold |
| Cohort size: 27,902 | 27,902 | 27,902 (h-e1-v2) | VERIFIED | Match |
| h-e1 cohort: 6,769 unique users | Not stated | 6,769 (h-e1) | FLAG | Paper calls it "replication" — cohort sizes differ ~4× |
| 13 months Apr 2023–Apr 2024 | 13 bins | Apr,May,Jun,Jul,Aug,Sep,Oct,Nov,Dec,Jan,Feb,Mar,Apr = 13 | VERIFIED | Correct count |
| p = 0.0005 reported as p < 0.001 | Both used | 0.0005 < 0.001 | MINOR | Technically consistent; precision inconsistency (see Metric Consistency) |
| Correction base rate ~0.05% | ~0.05% | ~0.05% | VERIFIED | Match |
| h-e1 τ = +0.564, p = 0.007 | +0.564, p = 0.007 | +0.564, p = 0.007 | VERIFIED | Exact match |
| h-e1-v2 τ = +0.744, p = 0.0005 | +0.744, p = 0.0005 | +0.744, p = 0.0005 | VERIFIED | Exact match |

**No mathematical impossibilities found. All core numerical claims verified against ground truth.**

---

## Mathematical Validity Analysis

### A. Token Growth Calculation

832 / 180 = 4.622. Paper states "4.6×" with "approximately" qualifier. **VERIFIED.** The qualifier is appropriate; no issue.

### B. Gate Arithmetic

1 significant proxy out of 3; threshold is ≥2. 1 < 2 → gate failed. **VERIFIED.** The paper's gate evaluation is arithmetically correct.

### C. Bootstrap CI Interpretation

CI = [0.415, 0.972]. Lower bound 0.415 > 0. CI does not overlap τ = 0. **VERIFIED.** The paper's claim is correct.

### D. ACF Threshold Logic

Proxy 1 ACF lag-1 = 0.634 > 0.1 → Hamed-Rao applied. **VERIFIED.**

Proxy 3 ACF lag-1 = 0.168 > 0.1 → Hamed-Rao should be applied. Table 1 shows "Hamed-Rao" for Proxy 3. **VERIFIED.** Consistent.

Proxy 2: ACF not computed (no data). Table 1 shows "—" for method. **VERIFIED.** Consistent.

### E. Cohort Size Discrepancy

The paper reports 27,902 returning users (h-e1-v2). The h-e1 validation shows 6,769 unique returning users on the same dataset and criterion (≥3 monthly bins, same WildChat-1M). This is a ~4.1× difference in cohort size between the two experiment rounds using the same stated methodology.

The paper calls h-e1 an "internal replication" of h-e1-v2 (Section 5.6, Appendix A.1). The replication framing is **misleading**: the cohort sizes differ by ~4×, the τ values differ (0.564 vs. 0.744), and the token range endpoints differ substantially (h-e1: 119–598 tokens; h-e1-v2: 180–832 tokens). These are not measurement noise; they indicate different cohort construction or data loading between the two versions.

The paper does not explain the cohort size discrepancy anywhere. Section 5.6 states only "h-e1-v2 replicates and strengthens h-e1. Direction and significance are consistent." This is accurate directionally but suppresses the methodological difference that could explain why the two rounds produced different cohort sizes.

**This is a MAJOR issue.** A reviewer will notice that 6,769 ≠ 27,902 and ask why. The paper currently has no answer.

### F. h-e1 vs h-e1-v2 Replication Consistency

Direction consistent: both τ > 0, both p < 0.05. **VERIFIED.**

However:
- Cohort size: 6,769 vs. 27,902 (~4× difference)
- τ: 0.564 vs. 0.744
- Approximate token range start: ~119 (h-e1) vs. ~180 (h-e1-v2)
- Approximate token range end: ~598 (h-e1) vs. ~832 (h-e1-v2)

The token approximation method also differs: h-e1 used "words × 1.3" approximation, while h-e1-v2 used tiktoken cl100k_base. This methodological difference is not disclosed in the paper's description of h-e1 in the Appendix. The paper presents the Appendix figures as supporting replication without noting the tokenization method difference.

---

## Baseline Fairness Assessment

The paper has no baseline model comparison in the conventional ML sense. The "baseline" is the BAA theoretical directional prediction: τ < 0 (declining engagement). The actual result is τ = +0.744.

This framing is **fair but incompletely characterized**. The paper correctly cites Shen et al. (2024) as the source of the BAA framework and directional prediction. However, Shen et al. (2024) is marked [UNVERIFIED], meaning the accuracy of the attributed BAA prediction (specifically: that prompt token count should decline) cannot be confirmed. If Shen et al. did not explicitly predict declining prompt token count — if that is the paper's own operationalization of BAA — then the "contrary to BAA prediction" framing is the authors' own construction rather than a verified theoretical claim.

The paper does not quote the specific BAA prediction from Shen et al. verbatim. It characterizes the prediction as "declining human behavioral engagement as a consequence of AI quality improvement." Whether this framework specifically predicts shorter prompts (rather than, for example, fewer corrections or lower preference discrimination) is not verified against the source.

**Recommendation**: This is a MAJOR issue. The paper should either (a) quote the specific BAA prediction from Shen et al. verbatim, or (b) clearly mark the operationalization as the authors' own and acknowledge that the directional prediction for prompt token count specifically may not be directly stated in Shen et al.

---

## Signal-Performance Gap Analysis

### τ = +0.744 in Context

For Mann-Kendall with n = 13 bins, τ = 1.0 would mean perfectly monotonic increase across all 13 monthly values. τ = +0.744 indicates very strong monotonic trend — approximately consistent with 11–12 of 13 pairs being concordant. This is not implausibly high; with a genuine underlying trend over a 13-month window, τ in this range is achievable.

### Minimum Detectable Effect

For standard Mann-Kendall with n = 13, the minimum detectable τ at α = 0.05 (two-tailed) is approximately |τ| ≥ 0.46 (critical Z ≈ 1.96, variance from the Mann-Kendall statistic). The Hamed-Rao correction with ACF lag-1 = 0.634 increases the effective variance — it inflates the variance of the S statistic, which reduces the Z score for a given τ. This means the Hamed-Rao-corrected minimum detectable τ is **higher** than the standard MK minimum. The paper's τ = 0.744 clears this higher bar, so the significance claim (p = 0.0005) is plausible and in the right direction.

### Hamed-Rao: τ vs. p-value Adjustment

The paper states: "Hamed-Rao correction is necessary" (Section 5.3) and "the Hamed-Rao modification … adjusts the variance for autocorrelated series" (Section 3.4). This is correct. Hamed-Rao adjusts the **variance** of the S statistic (and therefore the p-value), not τ itself. τ is fixed at 0.744 regardless of autocorrelation correction. The p-value changes based on the corrected variance.

The paper does not conflate τ adjustment with p-value adjustment. **No error here.** However, the paper does not explicitly state what the uncorrected p-value would be, making it impossible for a reader to assess how much the autocorrelation correction moved the p-value. Given ACF lag-1 = 0.634 (high autocorrelation), the uncorrected p-value would be lower (more significant) than the Hamed-Rao-corrected p = 0.0005. The correction is conservative. This should be noted.

**Missing**: The paper does not report the uncorrected p-value as a reference point. A reviewer may ask "how different is the corrected vs. uncorrected p-value?" This is a MINOR gap.

---

## Metric Consistency Check

### "p < 0.001" vs. "p = 0.0005"

The abstract states "p < 0.001." Sections 5.3, Table 1, and Section 5.6 state "p = 0.0005." The value 0.0005 < 0.001, so "p < 0.001" is technically correct but less precise than "p = 0.0005." These two representations are inconsistent in precision. In Section 1, "p < 0.001" appears; in Table 1, "0.0005" appears. A reader doing a ctrl-F check may notice this and raise it as an inconsistency even though it is mathematically non-contradictory. The conclusion (Section 7) uses "p < 0.001" again.

**Recommendation**: Standardize to "p = 0.0005" throughout (or "p < 0.001" throughout with a footnote that the exact value is 0.0005). Using both forms in the same paper is a minor but avoidable consistency issue.

### Correction Frequency Base Rate

Paper Section 3.3 and 5.5: "~0.05% of turns." Ground truth (h-e1-v2/04_validation.md): "~0.05% of turns match." **VERIFIED.** Consistent.

### 13 Monthly Bins

April 2023 through April 2024 inclusive: Apr, May, Jun, Jul, Aug, Sep, Oct, Nov, Dec (2023) = 9 months + Jan, Feb, Mar, Apr (2024) = 4 months. Total = 13. **VERIFIED.**

### Gate Criterion Notation

Section 3.4: "≥2/3 proxies must show |τ| ≥ 0.2 with p < 0.05." Section 5.2: "n_significant = 1/3 → Gate FAILED (threshold: ≥2/3)." Ground truth: criterion is ≥2/3. **Consistent.**

---

## Missing Limitations Check

### Required Limitations (from R1 revision)

| ID | Limitation | Present in R1 paper | Notes |
|----|-----------|---------------------|-------|
| L1 | Returning-user selection bias | YES (Section 6.3 L1) | Adequate |
| L2 | LMSYS access | YES (Section 6.3 L2) | Adequate |
| L3 | Correction frequency proxy inadequacy | YES (Section 6.3 L3) | Adequate |
| L4 | No causal chain verification | YES (Section 6.3 L4, elevated) | Adequate |
| L5 | IP-hash noise | YES (Section 6.3 L5, added in R1) | Present |
| L6 | ChatGPT-only scope | YES (Section 6.3 L6, added in R1) | Present |

All required R1 limitations are present.

### Additional Missing Limitations

**Missing L7: No AI model version information per interaction.**

WildChat-1M covers April 2023–April 2024. During this period, major model transitions occurred: GPT-3.5 Turbo was dominant in early 2023, GPT-4 became widely available via API in March 2023, and the relative usage mix shifted substantially over the observation window. The observed prompt length increase could be partially driven by users switching to GPT-4 (which handles longer prompts better) rather than any behavioral adaptation. The paper's L4 partially covers this ("no per-interaction measure of AI model quality or version") but does not name the specific model transition confound (GPT-3.5 → GPT-4) that coincides with the observation window. This is a MAJOR gap because the GPT-4 release timing is the most plausible confound for a prompt-length increase starting in mid-2023.

**Severity: MAJOR.** The specific model transition confound should be named, not just the general "no AI quality covariate" limitation.

**Missing L8: tiktoken cl100k_base tokenization assumption.**

The paper uses tiktoken cl100k_base to tokenize WildChat conversations (Section 3.3). cl100k_base is the tokenizer for GPT-3.5-turbo and GPT-4 (as of the WildChat data collection period). WildChat logs are OpenAI API calls, so this is the correct tokenizer for the actual model family. However, the paper does not state this justification. A reviewer from a non-OpenAI background may question whether the tokenization is appropriate. This is a MINOR gap — the assumption is likely correct but undocumented.

**Missing L9: Calendar-month binning edge effects.**

The pipeline bins by calendar month. Conversations near month boundaries (e.g., March 31 vs. April 1) are split into different bins. For a monthly time series over 13 bins, this is standard and unlikely to produce a directional bias. However, if WildChat data collection had systematic breaks or batch uploads near month boundaries, this could create artificial jumps. The paper does not acknowledge this. **MINOR** — standard practice, low risk.

---

## FATAL Issues

None found. All core numerical claims are mathematically valid and consistent with ground truth.

---

## MAJOR Issues

1. **[R2-M1] Cohort size discrepancy between h-e1 (6,769) and h-e1-v2 (27,902) is unexplained.**
   The paper calls h-e1 a "replication" of h-e1-v2 but the cohort sizes differ by ~4.1×. The tokenization method also differs (words×1.3 approximation in h-e1 vs. tiktoken in h-e1-v2). The paper does not disclose these differences in the Appendix replication description. A reviewer will notice 6,769 ≠ 27,902 immediately. The paper must either explain the methodological difference that caused the cohort size divergence or retract the "replication" framing in favor of "preliminary experiment with different methodology."

2. **[R2-M2] BAA directional prediction not quoted verbatim from Shen et al. (2024).**
   The paper attributes to BAA the prediction that "human behavioral engagement should decline" (and specifically that prompt token count should decline). Shen et al. (2024) is marked [UNVERIFIED]. If Shen et al. did not make this specific directional prediction for prompt tokens, the paper's framing of its result as "contrary to BAA" is the authors' own operationalization rather than a verified claim. The paper should quote the specific BAA prediction verbatim, or clearly mark the prompt-token operationalization as the authors' own extension of the BAA framework.

3. **[R2-M3] GPT-3.5 → GPT-4 transition confound not named in limitations.**
   Limitation L4 acknowledges no AI quality covariate per interaction, but does not name the specific confounder: the GPT-4 API became widely available in March 2023, directly before the start of the observation window (April 2023). Users switching from GPT-3.5 to GPT-4 may have begun composing longer prompts (taking advantage of GPT-4's larger context window and better instruction following), creating the observed positive prompt length trend entirely as a model-switch artifact. This specific, named confound is more compelling to reviewers than the generic "no AI quality covariate" framing currently in L4.

4. **[R2-M4] p-value precision inconsistency across paper.**
   Abstract and Conclusion use "p < 0.001"; Table 1 and Section 5.3 use "p = 0.0005." Both are mathematically correct but present different precision in the same paper. For a submission claiming exact numerical reproducibility, this is an avoidable inconsistency. Standardize to one form throughout.

---

## MINOR Issues (for human review — do NOT fix)

1. The paper does not report the uncorrected Mann-Kendall p-value alongside the Hamed-Rao-corrected p = 0.0005. Reporting both would help readers understand the magnitude of the autocorrelation correction and demonstrate that the result holds even before correction.

2. tiktoken cl100k_base tokenization choice is not justified in the paper (Section 3.3). A one-sentence justification ("cl100k_base matches the tokenizer used by the GPT-3.5-turbo and GPT-4 models in WildChat") would preempt reviewer questions.

3. Calendar-month binning edge effects are unacknowledged. Standard practice but worth a one-line note in the methodology.

4. Appendix A.3 presents "approximate values" for cohort size and token mean, with tilde qualifiers. These are internally consistent but could be improved by citing the exact values from `results/wildchat_monthly.csv` where available.

5. Section 5.6 states h-e1-v2 "replicates and strengthens" h-e1 without noting that the two used different tokenization methods. This understates the methodological differences between the rounds.

---

## Summary for Revision Agent

```
fatal_count: 0
major_count: 4
minor_count: 5
key_numerical_issues:
  - "h-e1 cohort (6,769) vs. h-e1-v2 cohort (27,902) ~4× discrepancy unexplained"
  - "BAA directional prediction for prompt tokens not verified against Shen et al. source (all citations [UNVERIFIED])"
  - "GPT-3.5 → GPT-4 transition (March 2023) not named as specific confound in L4"
  - "p < 0.001 (abstract/conclusion) vs. p = 0.0005 (table/section) precision inconsistency"
mathematical_impossibilities: 0
baseline_fairness_issues: 1
recommendation: MINOR_REVISION
```

*Note: R1 addressed the most critical structural issues (causal chain framing, selection bias, "FAIL direction" clarity). R2 finds no FATAL issues and the mathematical foundation is sound. The four MAJOR issues are addressable without restructuring the paper. Recommendation upgraded from MAJOR_REVISION (R1) to MINOR_REVISION (R2).*
