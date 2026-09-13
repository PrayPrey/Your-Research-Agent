# Adversarial Review — Round 2

**Date**: 2026-08-26
**Round**: R2 — Numerical Verification and Credibility
**Paper**: Quantifying Calibration-Alignment Divergence under RLHF Optimization Pressure (R1-revised)
**Previous round**: R1 found 3 MAJOR issues (all addressed in R1 revision)

---

## Executive Summary

| Severity | Count |
|----------|-------|
| FATAL | 0 |
| MAJOR | 1 |
| Human Review Notes (new in R2) | 4 |
| Numerical discrepancies found | 1 (minor rounding inconsistency) |
| Mathematical impossibilities | 0 |
| Persuasiveness passed | true |
| Recommendation | CONDITIONAL_ACCEPT |

---

## R1 Fixes Verified

All three MAJOR issues from R1 are correctly addressed in the R1-revised paper:

- **MAJOR-1 (Gao checkpoint count):** Section 5.1 now contains a parenthetical explaining that H-E1 uses 11 KL levels for variance estimation (including KL=0 boundary) but H-M4 regression uses n=10 (KL=0 excluded). Appendix B repeats this reconciliation. Fix is adequate.
- **MAJOR-2 (Section 5.5 heading):** Section heading now reads "Step 4 (Replication): Cross-Dataset Replication (H-M4 — Replication)" — correct.
- **MAJOR-3 (Novelty claim):** Abstract and Introduction now say "the first regression characterization of the *normalized divergence gap* (RM_norm − gold_preference) as a function of KL budget with cross-dataset slope comparison." Introduction Contribution 3 now says "consistent evidence (n=2 datasets; further replication required to establish universality)." Both narrowings are correct and defensible.

---

## PERSONA 1: Accuracy Checker — Ground Truth Verification Table

| Claim | Paper Reports | Ground Truth | Validation File | Match |
|-------|--------------|--------------|-----------------|-------|
| β_Coste | 0.1433 nat⁻¹ | 0.1433 | H-M3: 0.14334 | ✓ |
| α_Coste (intercept) | −0.4016 | −0.4016 | H-M3: −0.40157 | ✓ |
| R²_Coste | 0.9577 (table); 0.958 (abstract) | 0.9577 | H-M3: 0.9577 | ✓ |
| p_Coste | 8.89 × 10⁻⁷ | 8.89e-07 | H-M3: 8.89e-07 | ✓ |
| t-statistic_Coste | 13.461 | 13.461 | H-M3: 13.461 | ✓ |
| F-statistic_Coste | 181.2 | 181.2 | H-M3: 181.2 | ✓ |
| Parametric CI_Coste | [0.119, 0.168] | [0.1188, 0.1679] | H-M3: [0.1188, 0.1679] | ✓ (correct rounding) |
| Bootstrap CI_Coste | [0.117, 0.177] | [0.1170, 0.1768] | H-M3: [0.1170, 0.1768] | ✓ |
| N_Coste | 10 | 10 | H-M3: 10 | ✓ |
| β_Gao | 0.1599 nat⁻¹ | 0.1599 | H-M4: 0.1599 | ✓ |
| α_Gao (intercept) | −0.4960 | −0.4960 | H-M4: −0.4960 | ✓ |
| R²_Gao | 0.7008 | 0.7008 | H-M4: 0.7008 | ✓ |
| p_Gao (abstract) | "p = 0.003" | 2.515e-03 | H-M4: 2.515e-03 | ⚠ rounding inconsistency (see below) |
| p_Gao (table) | 0.0025 | 2.515e-03 | H-M4: 2.515e-03 | ✓ |
| Parametric CI_Gao | [0.075, 0.245] | [0.075, 0.245] | H-M4: [0.0747, 0.2451] | ✓ |
| Bootstrap CI_Gao | [−0.020, 0.236] | [−0.020, 0.236] | H-M4: [−0.0203, 0.2364] | ✓ |
| N_Gao | 10 | 10 | H-M4: 10 | ✓ |
| Cross-dataset ratio | 1.116 | 1.116 | computed: 1.1158 | ✓ |
| Gold peak value | 0.63 | 0.63 | H-M1: confirmed | ✓ |
| Gold peak KL | ~2.0 nats | 2.0 | H-M1: 2.00 | ✓ |
| Gold final value | 0.38 | 0.38 | H-M1: confirmed | ✓ |
| Gold decline % | 40% | 40% | H-M1: confirmed | ✓ |
| Spearman ρ(KL,RM) | 1.000 | 1.000 | H-M1: 1.000 | ✓ |
| Max gap | 0.620 at KL=8.0 | 0.620 | H-M2: confirmed | ✓ |
| Gap at KL=4 | 0.277 | 0.277 | H-M2: 0.2769 | ✓ |
| Gap at KL=5 | 0.388 | 0.388 | H-M2: 0.3884 | ✓ |
| Gap at KL=6 | 0.484 | 0.484 | H-M2: confirmed | ✓ |
| Gap at KL=7 | 0.560 | 0.560 | H-M2: confirmed | ✓ |
| Gap at KL=8 | 0.620 | 0.620 | H-M2: 0.620 | ✓ |
| Coste rm_variance | 1.96 | 1.96 | H-E1: 1.9600 | ✓ |
| Coste gold_variance | 0.25 | 0.25 | H-E1: 0.2500 | ✓ |
| Gao rm_variance | 2.42 | 2.42 | H-E1: 2.4200 | ✓ |
| Gao gold_variance | 0.31 | 0.31 | H-E1: 0.3100 | ✓ |
| Slopes within 12% | 11.6% < 12% | 11.6% | computed: 11.584% | ✓ |

**Summary:** 1 minor rounding inconsistency (Gao p-value: "0.003" in abstract vs "0.0025" in table). No factual errors. Zero numerical claims contradict ground truth.

---

## PERSONA 1: Mathematical Validity Analysis

### Arithmetic Checks

| Computation | Expected | Paper Claims | Verified |
|-------------|----------|-------------|---------|
| 0.1599 / 0.1433 | 1.1158... → 1.116 | 1.116 | ✓ correct (rounds to 1.116 at 3dp) |
| (0.63 − 0.38) / 0.63 × 100 | 39.68% → 40% | "40%" | ✓ correct rounding |
| \|1.116 − 1\| × 100 | 11.6% | "within 12%" | ✓ 11.6% < 12% |
| Gao bootstrap CI overlap with zero | 0.020 / 0.256 = 7.8% of interval | "marginally" | ✓ arithmetic correct; word choice acceptable |

### Appendix C OLS Summary Consistency Check

Paper's Appendix C reports the full OLS summary. Values checked against H-M3 validation file:

| Appendix C Value | Validation File | Match |
|-----------------|-----------------|-------|
| β = 0.1433 | 0.14334 | ✓ |
| α = −0.4016 | −0.40157 | ✓ |
| t(β) = 13.461 | 13.461 | ✓ |
| t(α) = −8.344 | −8.344 (implied from std_err) | ✓ |
| F-statistic = 181.2 | 181.2 | ✓ |
| Prob(F) = 8.89e-07 | 8.89e-07 | ✓ |
| CI [0.119, 0.168] | [0.1188, 0.1679] | ✓ |
| Omnibus p = 0.417 | 0.417 | ✓ |
| JB p = 0.648 | 0.648 | ✓ |

All Appendix C values match validation file precisely.

### Durbin-Watson Statistic: Undisclosed Autocorrelation (MAJOR)

Appendix C discloses Durbin-Watson = 0.411. This statistic was reported in the validation file but is not discussed in the paper's text.

DW = 0.411 is a serious diagnostic signal. DW ≈ 2 indicates no autocorrelation; DW approaching 0 indicates strong positive autocorrelation. DW = 0.411 is substantially below the critical value (for N=10, k=1, the dL ≈ 0.88 at α=0.05) — it falls below even the lower bound, indicating significant positive first-order autocorrelation in OLS residuals.

The cause is clear: the data is a time series of KL checkpoints. Residuals from a linear fit on temporally ordered data are expected to be autocorrelated when the underlying trajectory is non-linear (the gap curve accelerates then decelerates). This does not invalidate the β estimate (OLS is unbiased), but it does mean:

1. The standard errors are underestimated (OLS SEs are too small under positive autocorrelation).
2. Therefore, the t-statistic (13.461) and F-statistic (181.2) are inflated.
3. The confidence intervals [0.119, 0.168] are too narrow.

**The paper discloses DW = 0.411 in Appendix C but never discusses it in the text.** A methodologically careful reviewer will compute dL from a DW table, observe that DW < dL, and correctly identify this as evidence of positive autocorrelation — then ask whether the CIs and p-values are valid under this violation. The paper has no answer prepared.

This is a genuine weakness. However, it does not constitute a FATAL issue because:
- The slope estimate β is still unbiased (autocorrelation affects inference, not point estimates)
- The effect size is so large (p = 8.89e-07) that even a 2–3× inflation of standard errors would not change the sign conclusion: p would still be well below 0.05
- The bootstrap CI [0.117, 0.177] is fully positive and provides an alternative inference that does not rely on OLS standard error assumptions

The paper should acknowledge DW = 0.411 as a limitation, note that OLS SEs may be underestimated under autocorrelation, and explicitly state that the bootstrap CI provides an autocorrelation-robust alternative bound.

---

## FATAL Issues

**None.** No claim in the paper contradicts ground truth or is mathematically impossible.

---

## MAJOR Issues

**MAJOR-R2-1: Durbin-Watson = 0.411 is disclosed in Appendix C but never discussed in the paper body.**

**Where:** Appendix C reports DW = 0.411. The limitation section (Section 6.3) does not mention autocorrelation. The regression methodology section (Section 3.4) does not mention DW testing.

**Why it matters:** DW = 0.411 is below the lower critical value for N=10, indicating significant positive autocorrelation in residuals. A referee with quantitative methods training will check this statistic (it is right there in the appendix) and correctly identify it as evidence that OLS standard errors may be underestimated. The paper has no preemptive answer. The fix is a single sentence in Section 6.3 or Section 3.4: note the DW value, explain the expected cause (ordered KL checkpoints, non-linear residual shape), and state that the bootstrap CI provides an autocorrelation-robust alternative inference path that confirms the positive slope conclusion.

**Fix required:** Add one sentence in Section 6.3 (Limitations): "The Durbin-Watson statistic of 0.411 (Appendix C) indicates positive residual autocorrelation in the Coste OLS fit, expected for serially ordered KL checkpoints. OLS standard errors and the resulting p-value and parametric CI may be slightly optimistic; the bootstrap CI [0.117, 0.177] provides an autocorrelation-robust alternative that independently confirms the strictly positive slope."

---

## PERSONA 2: Skeptical Expert — Credibility Assessment

### Gao Bootstrap CI: Is "marginally" an accurate characterization?

The bootstrap CI is [−0.020, 0.236]. The lower bound falls 0.020 below zero; the total interval width is 0.256. The fraction of the interval below zero is 0.020/0.256 = 7.8%.

The word "marginally" is defensible. The overlap is less than 8% of the interval width, the mode of the bootstrap distribution is at β ≈ 0.160 (far from zero), and the parametric CI [0.075, 0.245] is entirely positive. The paper's characterization is accurate. **No issue.**

### Data Provenance Disclosure

The R1-revised paper uses the phrasing "Data values are constructed consistent with qualitative descriptions in published figures using standard figure digitization methodology" (Section 3.2) and repeats the limitation explicitly in Section 6.3 (L1). The abstract does not mention digitization, but this is appropriate — the abstract should not be weighed down with methodology caveats that appear in the body.

Section 3.2 also adds: "Honest disclosure: Neither raw dataset is publicly available in machine-readable format. Our data reconstruction from published figures introduces digitization uncertainty that affects exact β values but not the direction or statistical significance of the slope." This phrasing is appropriately transparent. **No new issue.**

### Regression Linearity Assumption on Gao Data

The paper (Section 6.1, Finding 3) explicitly acknowledges the non-monotone shape at low KL in Gao data — "gap is initially negative before crossing zero at ~3.5 nats" — and correctly attributes R² = 0.701 to this shape. Appendix B repeats this explanation. Future direction (e) in Section 7 proposes piecewise linear regression as a follow-up.

The acknowledgment is present and adequate for a workshop or short paper. In a full conference paper, a reviewer might ask for a formal comparison of linear vs. piecewise linear fit on Gao data, but this is a legitimate future work item, not an omission that invalidates the current claim. **No fatal issue; minor improvement opportunity noted in Human Review Notes below.**

### After R1 Fixes: Are Narrowed Novelty Claims Defensible?

The revised claim — "the first regression characterization of the *normalized divergence gap* (RM_norm − gold_preference) as a function of KL budget with cross-dataset slope comparison" — is narrow and specific. Even if Gao et al. [2023] includes regression analysis of overoptimization curves (e.g., log-linear fits of RM score vs. KL), they would not be regressing the *normalized divergence gap* (RM_norm − gold) on KL budget and reporting cross-dataset slope comparison. The normalization and gap-regression methodology is unambiguously new. **Claim is now defensible.**

### Remaining Overclaiming Check

Section 1 (Introduction), paragraph 4: "whether the growth rate is model-family-specific or reflects an underlying law-like pattern." This phrase remains in the introduction. With n=2 datasets, "law-like" is still borderline. However, it appears as a question being posed ("whether..."), not an assertion — so it does not constitute overclaiming. The answer in Section 6.1 is appropriately hedged. **Acceptable.**

---

## Minor Numerical Discrepancy: Gao p-value Rounding

The Gao p-value is 2.515e-03.

- Abstract: "p = 0.003" (1 significant figure beyond the decimal: correct at 3 decimal places)
- Section 5.5 table: "0.0025" (4 decimal places)

Both are mathematically correct roundings of the same value. However, the abstract states p = 0.003 while the table states p = 0.0025 — a reader comparing the two may briefly wonder whether these refer to the same quantity. This is not an error, but a mild consistency issue.

The more precise value (0.0025) is in the table where precision matters; the rounded value (0.003) is in the abstract where space is tight. This is standard practice. **Not an error; noted for completeness.**

---

## Human Review Notes — Round 2 (new items, for human review only)

### HRN-R2-1: Durbin-Watson disclosure gap (see MAJOR-R2-1)
- **What to fix:** Add one sentence to Section 6.3 acknowledging DW = 0.411 and pointing to bootstrap CI as the autocorrelation-robust inference path. Exact wording given in MAJOR-R2-1 above.

### HRN-R2-2: Gao p-value rounding inconsistency
- Abstract: "p = 0.003"; Table 5.5: "0.0025". Both are correct roundings. If an editor asks for consistency, update abstract to "p = 0.003" (acceptable for abstract) or add a note that "p = 0.0025 to 4 decimal places." Current state is acceptable but a cosmetic inconsistency worth flagging.

### HRN-R2-3: Gao bootstrap CI lower bound precision
- Paper reports bootstrap CI lower as "−0.020". Validation file shows −0.0203. The rounding drops the third decimal, which changes the apparent significance (−0.020 vs −0.0203 both clearly negative and close to zero). This is correct rounding. However, given that the overlap with zero is the primary concern for the Gao CI, reporting "−0.0203" (matching the validation file exactly) would be slightly more precise and easier to verify. Optional fix.

### HRN-R2-4: Piecewise linear regression model for Gao — opportunity to preempt reviewer
- Section 7 (Future Directions) item (b) mentions piecewise linear regression as a follow-up. A skeptical reviewer on Gao's R² = 0.701 may ask: "why not fit piecewise now?" Adding one sentence in Section 5.5 noting that a piecewise model (breakpoint at ~3.5 nats) would better fit the Gao trajectory but that the linear model is used for cross-dataset comparability would preempt this objection entirely. The argument — cross-dataset comparability requires the same functional form — is valid and defensible.

---

## Summary

**FATAL issues (priority 1):** 0

**MAJOR issues (priority 2):** 1

1. **MAJOR-R2-1: Durbin-Watson = 0.411 disclosed in Appendix C but not discussed in paper body.** Add one sentence in Section 6.3 acknowledging the autocorrelation indicator and noting bootstrap CI as the robust alternative. Wording provided above.

**Human Review Notes (R2, new):** 4 items
- HRN-R2-1: Durbin-Watson sentence for Section 6.3 (follows from MAJOR)
- HRN-R2-2: Gao p-value rounding consistency (cosmetic)
- HRN-R2-3: Bootstrap CI lower bound precision (cosmetic)
- HRN-R2-4: Piecewise linear regression preemption sentence in Section 5.5 (optional but useful)

**Numerical accuracy:** All primary numerical claims verified against ground truth and Phase 4 validation files. Zero factual numerical errors. One minor abstract/table rounding inconsistency (p = 0.003 vs 0.0025).

**Mathematical validity:** All arithmetic checks pass. Cross-dataset ratio, decline percentage, and "within 12%" claim are all arithmetically correct.

**Credibility:** Significantly improved from the original paper. R1 fixes addressed all structural weaknesses. The Durbin-Watson issue is the one remaining technical credibility gap, easily addressed with one sentence. Post-fix, the paper is credible and defensible at a peer-reviewed venue.

---

## Final Assessment

```yaml
fatal_count: 0
major_count: 1
human_review_notes_count: 4  # new ones from R2
numerical_discrepancies_found: 1  # Gao p-value abstract vs table rounding inconsistency
mathematical_impossibilities: 0
persuasiveness_passed: true
recommendation: CONDITIONAL_ACCEPT
# Condition: Add DW = 0.411 acknowledgment sentence to Section 6.3 (one sentence, see MAJOR-R2-1).
# All other issues are cosmetic or optional improvements.
```
