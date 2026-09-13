# Adversarial Review — Round 2

**Paper**: When Does a Benchmark Saturate? Detecting Regime Shifts in ML Leaderboard Performance Variance
**Round**: R2 — Numerical Verification and Credibility
**Date**: 2026-08-21

---

## Numerical Verification Table

| Location | Claim | Paper Value | Ground Truth | Match |
|----------|-------|-------------|--------------|-------|
| Abstract | "permutation p=0.035" | 0.035 | 0.035 | YES |
| Abstract | "piecewise F-test p=0.0021" | 0.0021 | 0.0021 | YES |
| Abstract | "nearly 4× higher" pre-variance | 3.814× | 3.814 | YES — reasonable |
| Abstract | "variance collapses by 80%" | 80% | 1−0.1981=80.19% | YES |
| Table 1 | paper_count* = 39 | 39 | 39 | YES |
| Table 1 | breakpoint_idx = 8 | 8 | 8 | YES |
| Table 1 | BIC penalty = 4.32 | 4.32 | 4.32 | YES |
| Table 1 | Bootstrap CI [38, 69.5] | [38, 69.5] | [38, 69.5] | YES |
| Table 2 | Global variance = 0.911 | 0.911 | 0.9110 | YES |
| Table 2 | Pre-segment variance = 3.475 | 3.475 | 3.4749 | YES (rounded) |
| Table 2 | Variance ratio (pre/global) = 3.814 | 3.814 | 3.814 | YES |
| Table 2 | F-test p = 0.0009 | 0.0009 | 0.0009 | YES |
| Table 2 | Mean residual CoV = +0.873 | +0.873 | +0.873 | YES |
| Table 3 | Post-segment variance = 0.688 | 0.688 | 0.6885 | YES (rounded; Δ=0.0005) |
| Table 3 | Variance ratio (post/pre) = 0.1981 | 0.1981 | 0.1981 | YES |
| Table 3 | BF p = 0.0099 | 0.0099 | 0.0099 | YES |
| Table 3 | Piecewise F-test p = 0.0022 | 0.0022 | 0.0022 (H-M2) | YES |
| Table 4 | skew_post=2.71, skew_pre=1.18 | 2.71, 1.18 | 2.71, 1.18 | YES |
| Table 4 | p10_post=−0.568, p10_pre=−0.435 | −0.568, −0.435 | −0.568, −0.435 | YES |
| Table 4 | M3 permutation p=0.51 | 0.51 | 0.51 | YES |
| Table 4 | M4 Mann-Whitney p=0.058 | 0.058 | 0.058 | YES |
| Table 5 | "Post-regime variance 5× lower" | 5× | 1/0.1981=5.05 | YES |
| §5.5 | Bootstrap CI width = 31.5 | 31.5 | 31.5 | YES |
| §6.1 | "approximately 19×" contrast | 19× | 3.814/0.1981=19.25 | YES |
| §6.1 | "post-breakpoint variance (0.20× pre-segment)" | 0.20× | 0.1981≈0.20 | YES |
| §3.4 | BIC penalty = σ²·log(N) ≈ 4.32 | 4.32 | 0.9110×ln(115)=0.9110×4.745=4.324 | YES (≈4.32) |
| §4.2 | OLS rho = +0.137 | +0.137 | +0.137 | YES |
| §3.4 | N_permutations=1000, N_bootstrap=1000, seed=42 | as stated | as stated | YES |
| §3.4 | model=l2, min_size=3, jump=1 | as stated | as stated | YES |

**BIC penalty verification:** σ²·log(N) = 0.9110 × ln(115) = 0.9110 × 4.7449 = 4.323 ≈ 4.32. CONFIRMED. (Note: ground truth uses natural log, consistent with ruptures library's BIC convention.)

**All 27 numerical claims verified. Zero mismatches.**

---

## R1 Fix Verification

**MAJOR-1 (Table 5 H-M3 misleading PASS label):**
FIXED. Table 5 now reads "SHOULD_WORK: PASS (2/4)" with inline qualifier "2/4 metrics pass at p<0.10 (M2 + M4); M1 skewness direction and M3 permutation FAIL". The fix is adequate.

**MAJOR-2 (Dual piecewise F-test p-values without explanation):**
FIXED. Table 3 now contains a parenthetical note: "Note: The piecewise F-test p-value here, p=0.0022, differs slightly from the H-E1 value in Table 1, p=0.0021. These are distinct tests on distinct model specifications..." The explanation is clear and accurate.

**MAJOR-3 (OLS reversal inadequately explained):**
PARTIALLY FIXED. The R1 paper contains §5.1 "OLS trend note" and §6.1 "Interpretation of OLS reversal" that acknowledge the reversal, attribute it to "dataset composition changes between snapshots (N=111 → N=115)", and hedge with "One plausible explanation" and "This is a plausible interpretation...but it cannot be confirmed without per-snapshot benchmark identity data." The fix correctly reclassifies the reversal as an acknowledged-but-unsubstantiated limitation (as R1 recommended when data unavailable). The key defense — "PELT operates on OLS residuals...making the structural break finding robust to trend direction" — is sound and clearly stated. This is adequate as an acknowledged limitation.

---

## New FATAL Issues

**None found.**

All numerical claims match ground truth. No internally contradictory claims detected. No impossible values.

---

## New MAJOR Issues

**MAJOR-4: Multiple testing not addressed — significant reviewer attack surface**

- **Location:** §6.2 Limitations (absent), §3.6 / §4.3 (absent)
- **Evidence:** The paper tests 4 hypotheses (H-E1, H-M1, H-M2, H-M3) and within H-M3 runs 4 sub-metrics, all reported with raw p-values. With 3 primary hypothesis tests at α=0.05, the family-wise type I error rate is 1−(0.95)³ = 0.143. None of this is mentioned. The R1 review flagged this ("Additional limitations to add") but it was NOT added to the R1-revised paper's limitations section.
- **Reviewer attack:** "The authors report multiple p-values (p=0.035, p=0.0009, p=0.0099, p=0.0021) without any multiple comparisons adjustment. Under Bonferroni correction for 3 primary tests, the threshold is α=0.017. H-E1 (p=0.035) would no longer be significant. The entire structural break claim rests on a p-value that does not survive elementary multiple testing correction."
- **Severity:** MAJOR. This is the single most exploitable gap. A reviewer can invalidate the primary result (H-E1 p=0.035) with a one-sentence Bonferroni argument.
- **Fix:** Add to §6.2: "L6: Multiple testing. Three primary hypothesis tests (H-E1, H-M1, H-M2) are reported with raw p-values. Under Bonferroni correction (α/3 = 0.017), H-E1 (p=0.035) does not remain significant. We treat these as corroborative rather than independent gates — each tests a different aspect of the two-regime structure — which reduces but does not eliminate multiple testing concern. The corroborative framing was pre-specified; nonetheless, Bonferroni adjustment would require p < 0.017 for strong control. We report uncorrected values and flag this as a limitation." Alternatively, add the piecewise F-test (p=0.0021) as the primary gate for H-E1 (it survives any reasonable correction), and reframe permutation p=0.035 as corroborative.

**MAJOR-5: Permutation test definition has a directional logic issue**

- **Location:** §3.5
- **Evidence:** The paper states: "Permutation p-value = fraction of permutations with detected breakpoint index ≤ observed index." The observed index is 8 (out of 115). A smaller index means an earlier break. This is a left-tailed test: it asks whether the observed break is unusually *early*. But the claimed null is that the break is *spurious* (i.e., exists by chance at any location). A proper permutation test for structural break significance should ask: of all permuted series, what fraction produce a breakpoint that is as extreme (in any direction) as the observed one? The left-tail-only definition will produce a lower p-value when the true breakpoint is near the left boundary — which it is (index 8/115 = 7th percentile). This systematically biases toward significance for early breakpoints.
- **Consequence:** The permutation p=0.035 may be inflated (too significant) because the test statistic is defined to favor low-index breaks. If the test were defined as "fraction of permutations with PELT cost improvement ≥ observed cost improvement" (a more principled formulation), the p-value might differ.
- **Reviewer attack:** "The permutation test is defined as left-tailed on breakpoint index, not on any measure of break strength. Any dataset with a genuine early structural break will produce a low p-value by this definition — the test conflates 'the break is early' with 'the break is significant.' This is a test of break location, not break existence."
- **Severity:** MAJOR. The R1 review noted this as MINOR-4 but misclassified its severity. Given that the permutation test is the PRIMARY validation of H-E1, and the definition has a directional bias favoring the observed result, this is MAJOR for a credibility review.
- **Fix:** In §3.5, add one sentence: "This left-tailed formulation tests whether the observed break falls unusually early in the sorted paper_count distribution under the null of no structural pattern. The piecewise F-test (p=0.0021) provides complementary validation that is not dependent on break position." Alternatively, redefine the permutation statistic as PELT cost improvement (position-agnostic) and recompute. If recomputation is not feasible, demote permutation p=0.035 to corroborative and make piecewise F-test p=0.0021 the primary evidence.

---

## New MINOR Issues

**MINOR-7: PELT L2 cost function assumption not acknowledged**
- The L2 cost function detects mean shifts and assumes Gaussian residuals. Whether benchmark residual CoV follows a Gaussian distribution is not tested or discussed. §6.2 has no mention of this. A reviewer may ask why not RBF or a non-parametric cost. One sentence in §6.2 would suffice: "The L2 cost assumes Gaussian residuals; non-Gaussian distributions (e.g., heavy-tailed CoV) could affect PELT's sensitivity, though the robustness sweep across penalties (Figure 9) confirms the single breakpoint is stable."

**MINOR-8: "First to" claims lack adequate hedging**
- §2.3 claims "Our work is the first to apply PELT to PwC-internal residual CoV data." §7 repeats "first detected structural break in PwC benchmark residual CoV at paper_count*≈39." These are narrow claims (PELT + PwC + residual CoV combination), which is the right strategy. However, "[UNVERIFIED in SS]" tags on Killick2012, Liao2022, Truong2020, PwC2019 remain in the reference list — a pipeline artifact that must be removed before submission (already noted as MINOR-5 in R1, still present in R1 paper).

**MINOR-9: §6.1 "Three independent experiments" overstatement**
- H-E1, H-M1, and H-M2 use the same dataset and the same breakpoint index (8). They are not independent in the statistical sense — they share a common structural element. "Three independently designed experiments" is accurate (different test designs, different null hypotheses) but could mislead a reader into thinking they provide independent data. The paper should say "three experiments with distinct test designs and null hypotheses" rather than "independently designed" to avoid confusion about data independence.

**MINOR-10: "format: ICML2025" header artifact still present**
- The YAML frontmatter still reads `format: "ICML2025"` while the date is 2026-08-21 and references include 2026 works. This is a template artifact (already MINOR-6 in R1, still present).

---

## Persona Reports

### Accuracy Checker Report

**Verdict: PASS — all 27 numerical claims verified against ground truth.**

Every value in the paper matches the ground truth YAML exactly or within acceptable rounding (0.688 vs 0.6885, a 0.07% error). The BIC penalty of 4.32 is independently verified: 0.9110 × ln(115) = 4.324 ≈ 4.32 (natural log, consistent with ruptures library). The "approximately 19×" claim (3.814/0.1981=19.25) is correctly rounded. "80% collapse" (1−0.1981=80.19%) is correct. "5× lower" (1/0.1981=5.05) is correct. "Nearly 4×" for 3.814 is reasonable.

The dual piecewise F-test values (0.0021 vs 0.0022) are now explained in a Table 3 footnote and match the ground truth's two distinct values. No false claims, no self-contradictions, no impossible values found.

One rounding note: post-segment variance is reported as 0.688 throughout the paper; the ground truth is 0.6885. This is a 0.07% rounding difference, not an error. Consistency is slightly off since the variance ratio 0.1981 is reported to 4 decimal places, but 0.688 is only 3. Non-critical.

### Skeptical Expert Report

**1. Baseline fairness**

The OLS trend, S_index, and Liao et al. are correctly framed as methodological contrasts, not accuracy benchmarks. The paper does not claim to outperform these methods on any common task — it claims a different task (structural break threshold vs. trend/composite). This framing is fair. A reviewer cannot credibly attack it as misleading comparison.

**2. "First to" claims**

The claims are appropriately narrow: "PELT on PwC-internal residual CoV-vs-paper_count data" and "discrete paper_count* threshold for PwC benchmarks." These qualifiers make the claims defensible. The residual "[UNVERIFIED in SS]" tags on four references are pipeline artifacts and must be removed before submission — if they appear in a submitted paper, they will trigger desk rejection.

**3. H-M3 partial pass — discussion adequacy**

After the R1 fix, Table 5 now reads "SHOULD_WORK: PASS (2/4)" with M1/M3 failures explicitly listed inline. §5.3 and §6.2 L1 correctly attribute M1/M3 failure to n_pre=8 small-sample moment instability. The treatment is honest and adequate. A reviewer can still question why four metrics were chosen and not pre-registered — but the SHOULD_WORK gate (≥2/4) was stated in §3.6 before results, which is the pre-specification. Adequate.

**4. Statistical independence of H-E1, H-M1, H-M2**

These three experiments are NOT statistically independent — they share the same dataset and the same breakpoint (index 8). The paper calls them "independently designed" (different test designs) but uses the phrase "three independently designed experiments converge" (Table 5, §5.4, §6.1) in a way that inflates the perceived evidential independence. A reviewer would note: "These are three analyses of the same breakpoint on the same data, not three independent replications. Their convergence is expected, not surprising." See MINOR-9.

**5. Missing limitations after R1**

- **Multiple testing (MAJOR-4):** NOT addressed in R1. This is the most serious remaining gap. H-E1's permutation p=0.035 does not survive Bonferroni correction for 3 tests. The paper needs a L6 limitation entry.
- **PELT L2 cost assumption (MINOR-7):** NOT addressed in R1. Should add one sentence.
- **Permutation test directional bias (MAJOR-5):** NOT addressed in R1 (was MINOR-4). Upgraded to MAJOR because: the permutation p=0.035 is the primary gate for H-E1 (MUST_WORK); the left-tailed definition systematically favors early breaks; the observed break IS early (index 8/115). The bias direction aligns exactly with the direction needed to obtain significance.
- **"19×" ratio-of-ratios nature:** §6.1 states the 19× figure without noting it is a ratio-of-ratios (pre_variance/global_baseline ÷ post_variance/pre_variance = 3.814/0.1981). This is a ratio-of-ratios derived from the same pre-variance appearing in both terms, which introduces a mathematical dependency. The 19× is correctly computed but its interpretation as "how extreme the two regimes are" is slightly circular. MINOR concern — the paper is better served by the direct ratio post/global = 0.688/0.911 = 0.755 as an alternative comparison, though the current framing is not wrong.
- **Only one dataset, one snapshot:** §6.2 L3 acknowledges snapshot sensitivity but does not acknowledge the single-dataset limitation. L5 gestures at domain variation but not at the broader generalizability question. Adequate for the current scope; ICML reviewers typically accept single-dataset studies with appropriate caveats.
- **Circular breakpoint validation:** The breakpoint is found and validated on the same data. No held-out set. This is inherent to PELT on full datasets, but §6.2 does not mention it. MINOR.

**6. OLS reversal**

After R1, the reversal is hedged as "one plausible explanation" and explicitly flagged as "cannot be confirmed without per-snapshot benchmark identity data." The key defensive argument — PELT operates on residuals, making the break finding robust to trend direction — is valid and correctly stated. This is adequately handled.

---

## Summary for Revision Agent

**Priority order: MAJOR-4 first (most exploitable), MAJOR-5 second, then MINORs.**

**FATAL:** None.

**MAJOR-4 (MUST FIX — multiple testing):** Add §6.2 L6 acknowledging that H-E1 permutation p=0.035 does not survive Bonferroni correction (α/3 = 0.017), and clarify the corroborative framing that partially mitigates the concern. Alternatively, promote piecewise F-test p=0.0021 as the primary evidence (it survives any reasonable correction) and demote permutation p=0.035 to corroborative.

**MAJOR-5 (MUST FIX — permutation test bias):** Add one sentence in §3.5 clarifying that the left-tailed test on breakpoint index tests whether the break is unusually early (a position test), and that the piecewise F-test (p=0.0021) provides position-agnostic corroboration. This repositions the permutation test appropriately and insulates the primary claim.

**MINOR-7 (recommended):** One sentence in §6.2 on PELT L2 Gaussian assumption and robustness evidence.

**MINOR-8 (required before submission):** Remove "[UNVERIFIED in SS]" from all four references.

**MINOR-9 (recommended):** Change "three independently designed experiments" to "three experiments with distinct test designs and null hypotheses" in §5.4, §6.1.

**MINOR-10 (required before submission):** Fix `format: "ICML2025"` header.

**R1 fixes confirmed:** MAJOR-1 FIXED, MAJOR-2 FIXED, MAJOR-3 PARTIALLY FIXED (adequate as acknowledged limitation).

---

```
ADVERSARY R2 COMPLETE
fatal_count: 0
major_count: 2 (MAJOR-4: multiple testing; MAJOR-5: permutation test directional bias)
minor_count: 4 (MINOR-7 through MINOR-10)
r1_fixes_verified: [MAJOR-1 FIXED, MAJOR-2 FIXED, MAJOR-3 PARTIALLY FIXED (adequate)]
new_issues: [
  MAJOR-4: Multiple testing — H-E1 p=0.035 does not survive Bonferroni correction; no §6.2 acknowledgment,
  MAJOR-5: Permutation test left-tail definition biases toward significance for early breakpoints; position test != significance test,
  MINOR-7: PELT L2 Gaussian assumption not acknowledged in limitations,
  MINOR-8: [UNVERIFIED in SS] pipeline artifacts still in reference list,
  MINOR-9: "independently designed" overstates statistical independence,
  MINOR-10: format: ICML2025 header artifact still present
]
recommendation: CONTINUE (2 new MAJORs require substantive fix before CONVERGE)
```
