# Human Review Notes — Round 1 Minor Issues

**Paper**: When Does a Benchmark Saturate? Detecting Regime Shifts in ML Leaderboard Performance Variance
**Date**: 2026-08-21
**Source**: 065_review_r1.md MINOR issues — NOT auto-fixed in R1

These issues were collected but not applied in the R1 automated revision. A human reviewer should assess each and decide whether to fix before submission.

---

## MINOR-1: post_variance rounding inconsistency

- **Location**: Table 3 (§5.3)
- **Issue**: Post-segment variance is reported as 0.688; ground truth is 0.6885. Other values in the same table use 4 decimal places (ratio=0.1981). The inconsistency is minor (Δ=0.0005) but could be flagged by a meticulous reviewer.
- **Suggested fix**: Change 0.688 → 0.6885 (or 0.689 for 3 d.p.) to match precision of surrounding values.

## MINOR-2: "collapses by 80%" antecedent ambiguous

- **Location**: Abstract
- **Issue**: "variance collapses by 80%" — relative to pre-segment or global? The correct answer is relative to pre-segment (H-M2: ratio=0.1981). A skeptical reader could interpret "collapses" relative to the global baseline instead.
- **Suggested fix**: Change to "post-breakpoint variance collapses to 20% of pre-breakpoint levels (80% reduction)" or similar phrasing that makes the reference clear.

## MINOR-3: Forward figure references in §3.1 (methodology)

- **Location**: §3.1
- **Issue**: §3.1 references "Figure 8" (scatter_regime.png) and "Figure 9" (penalty_sensitivity.png) within the methodology section, before results are presented. Forward-referencing figures from §3 before they appear in §5 is nonstandard and may confuse readers.
- **Suggested fix**: Either move figure references to §5 where they are discussed in results context, or add "(see §5 for details)" to the §3.1 mentions to explicitly signal the forward reference.

## MINOR-4: Permutation test directionality not explained

- **Location**: §3.5
- **Issue**: The permutation test p-value is defined as "fraction of permutations with detected breakpoint index ≤ observed index" — this is a one-tailed left test (testing whether the observed breakpoint is unusually early). The paper does not explain why left-tailed is appropriate rather than two-tailed. If the intent is to test structural significance rather than position, the statistic choice deserves one sentence of justification.
- **Suggested fix**: Add one sentence: "We use a left-tailed test because our hypothesis is specifically that the structural break occurs early in the paper_count distribution — consistent with saturation onset — rather than merely that a break exists at any location."

## MINOR-5: "[UNVERIFIED in SS]" pipeline artifacts in references

- **Location**: References section
- **Issue**: References [Killick2012], [Liao2022], [Truong2020], [PwC2019] contain "[UNVERIFIED in SS]" annotations. These are pipeline artifacts (Semantic Scholar verification flags) that must be removed before submission.
- **Suggested fix**: Remove the "[UNVERIFIED in SS]" tag from each affected reference. Optionally, verify the citations manually before removing the tag.

## MINOR-6: YAML header "format: ICML2025" is outdated

- **Location**: Paper YAML front matter (lines 1–14)
- **Issue**: The header specifies `format: "ICML2025"` but the paper date is 2026-08-21 and includes 2026 references. This is a template artifact that will look odd to reviewers.
- **Suggested fix**: Update `format` to reflect the actual target venue and year, or remove the field if it is not used by the submission system.

---

## Round 2 Minor Issues (from 065_review_r2.md)

**Source**: 065_review_r2.md MINOR issues — NOT auto-fixed in R2

## MINOR-7: PELT L2 Gaussian assumption not acknowledged

- **Location**: §6.2 Limitations
- **Issue**: The L2 cost function assumes Gaussian residuals. Whether benchmark residual CoV follows a Gaussian distribution is not tested or discussed. Reviewers may ask why not RBF or a non-parametric cost.
- **Suggested fix**: Add one sentence to §6.2: "The L2 cost assumes Gaussian residuals; non-Gaussian distributions (e.g., heavy-tailed CoV) could affect PELT's sensitivity, though the robustness sweep across penalties (Figure 9) confirms the single breakpoint is stable."

## MINOR-8: "[UNVERIFIED in SS]" pipeline artifacts still present

- **Location**: References section
- **Issue**: References [Killick2012], [Liao2022], [Truong2020], [PwC2019] still contain "[UNVERIFIED in SS]" annotations after R1. These must be removed before submission to avoid desk rejection.
- **Suggested fix**: Remove the "[UNVERIFIED in SS]" tag from each affected reference. (Same as MINOR-5 from R1 — not yet applied.)

## MINOR-9: "Three independently designed experiments" overstates statistical independence

- **Location**: §5.4, §6.1, Table 5 caption area
- **Issue**: H-E1, H-M1, and H-M2 use the same dataset and the same breakpoint index (8). They are not independent in the statistical sense. Phrasing "three independently designed experiments converge" may mislead readers into thinking they provide independent data replications.
- **Suggested fix**: Change "three independently designed experiments" → "three experiments with distinct test designs and null hypotheses" to be accurate about what "independent" means here.

## MINOR-10: "format: ICML2025" YAML header artifact still present

- **Location**: Paper YAML front matter
- **Issue**: The header specifies `format: "ICML2025"` while the paper date is 2026-08-21 and includes 2026 references. Same as MINOR-6 from R1 — not yet applied.
- **Suggested fix**: Update `format` to the actual target venue and year, or remove the field.
