# Revision Changelog — Round 1

**Paper**: When Does a Benchmark Saturate? Detecting Regime Shifts in ML Leaderboard Performance Variance
**Revision**: R1
**Date**: 2026-08-21
**Source review**: 065_review_r1.md

---

## Major Fixes Applied

### MAJOR-1: Table 5 H-M3 label clarified to show partial result

- **Location**: §5.4, Table 5
- **Change**: H-M3 row label changed from `SHOULD_WORK: PASS` to `SHOULD_WORK: PASS (2/4)`. Key Evidence column updated from "2/4 metrics at p<0.10" to "2/4 metrics pass at p<0.10 (M2 + M4); M1 skewness direction and M3 permutation FAIL".
- **Rationale**: The prior label could mislead skimming reviewers into thinking all sub-metrics passed. The revised label accurately reflects the partial result while preserving the pre-specified SHOULD_WORK gate (≥2/4).

### MAJOR-2: Dual piecewise F-test p-values explained

- **Location**: §5.3, immediately after Table 3 (before the "80% variance reduction" paragraph)
- **Change**: Added a parenthetical note clarifying that p=0.0022 (Table 3, H-M2) and p=0.0021 (Table 1, H-E1) come from distinct tests on distinct model specifications: H-E1 tests one-segment vs. two-segment fit on the full residual CoV series; H-M2 tests pre vs. post segment fits within the variance-comparison model.
- **Rationale**: Without this note, two different p-values for "piecewise F-test" appear in the paper without explanation, which undermines statistical credibility.

### MAJOR-3: OLS reversal reframed as hypothesis, not established fact

- **Location**: §5.1 "OLS trend note" and §6.1 "Interpretation of OLS reversal"
- **Change**:
  - §5.1: Rewrote "This reversal reflects dataset composition changes" → "One plausible explanation is that dataset composition changed... We do not have per-snapshot benchmark identities to verify this directly; the reversal is acknowledged as an unresolved sensitivity."
  - §6.1: Rewrote "it reflects PwC benchmark database composition changes over time" → "We hypothesize it reflects PwC benchmark database composition changes between snapshots... This is a plausible interpretation... but it cannot be confirmed without per-snapshot benchmark identity data."
- **Rationale**: The original text stated the composition-change explanation as established fact. The revised text accurately represents it as an interpretation, consistent with the paper's broader hedged framing.

---

## No Numerical Changes

No numerical findings were altered. All ground-truth values remain as reported.

## No Structural Changes

Section structure, figure references, and conclusions are unchanged.

---

# Revision Changelog — Round 2

**Paper**: When Does a Benchmark Saturate? Detecting Regime Shifts in ML Leaderboard Performance Variance
**Revision**: R2
**Date**: 2026-08-21
**Source review**: 065_review_r2.md

---

## Major Fixes Applied

### MAJOR-4: Multiple testing limitation added (§6.2 L6)

- **Location**: §6.2 Limitations
- **Change**: Added new limitation entry L6: "**L6: Multiple testing.** We test three primary hypotheses (H-E1, H-M1, H-M2) without a family-wise correction. Under Bonferroni (α/3≈0.017), the H-E1 permutation p=0.035 does not survive correction; the corroborating piecewise F-test (p=0.0021) does. We recommend treating the permutation test as one of two convergent lines of evidence (together with p=0.0021) rather than a standalone significance claim."
- **Rationale**: H-E1 permutation p=0.035 does not survive Bonferroni correction for 3 primary tests. Without acknowledging this, a reviewer can invalidate the primary structural break claim with a one-sentence argument. The piecewise F-test (p=0.0021) survives any reasonable correction and the dual-evidence framing is already present in the abstract; the L6 entry makes it explicit as a limitation. The abstract already presents both p-values together; no change needed there.

### MAJOR-5: Permutation test directional interpretation clarified (§3.5)

- **Location**: §3.5 Statistical Validation
- **Change**: Added clarifying sentence after the permutation test definition: "This formulation tests whether the detected break position is statistically earlier than chance — a meaningful test given that early breaks are most likely to reflect genuine exploration-to-saturation transitions rather than boundary artifacts. The complementary piecewise F-test (p=0.0021) provides position-agnostic model comparison evidence."
- **Rationale**: The permutation test is a left-tailed position test (fraction of permutations with breakpoint index ≤ observed index=8). Without clarification, reviewers may (correctly) note that a break at the 7th percentile will almost always yield a low p-value by this definition — conflating "break is early" with "break is significant." The added sentence defends the test design while being transparent about what it measures, and explicitly redirects primary evidential weight to the piecewise F-test.

---

## No Numerical Changes

No numerical findings were altered. All ground-truth values remain as reported.

## No Structural Changes

Section structure, figure references, and conclusions are unchanged.

---
## Final Summary

**Total Revisions Made**: 5 MAJOR fixes
**Sections Modified**: §3.5, §5.1, §5.3, §5.4, §6.1, §6.2
**Review Process**:
- Started: 2026-08-21T13:00:00+00:00
- Completed: 2026-08-21T14:00:00+00:00
- Rounds: 2
- Personas: accuracy_checker, bored_reviewer, skeptical_expert

**Files Generated**:
- 06_paper_final.md (final paper)
- 065_review_summary.md (review summary)
- 065_human_review_notes.md (10 MINOR issues for human review)
- 065_changelog.md (this file)

**Next Phase**: Phase 6.5.1 (Overleaf LaTeX/PDF generation)
