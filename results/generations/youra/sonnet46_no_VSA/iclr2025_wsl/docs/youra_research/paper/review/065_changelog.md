# Phase 6.5 Changelog

**Date:** 2026-08-03
**Review:** Adversarial (2 rounds)

---

## Changes Applied to 06_paper.md → 06_paper_final.md

### Change 1 — MAJOR fix: CISE framing (Introduction)
**Location:** Introduction, paragraph 2
**Before:** "For CISE, a sinusoidal positional encoder widely used in weight-space learning, you get R² = −1.63."
**After:** "For CISE, a sinusoidal positional encoder designed as a representative non-invariant baseline, you get R² = −1.63."
**Reason:** "Widely used" implies external adoption — no external CISE citation exists. Accurate framing is "representative non-invariant baseline."

### Change 2 — MAJOR fix: CISE framing (Section 3.2)
**Location:** Section 3.2, C1 description opening sentence
**Before:** "The channel-index sinusoidal encoder applies per-channel learned projections..."
**After:** "We design the channel-index sinusoidal encoder as a representative non-invariant baseline: it applies per-channel learned projections..."
**Reason:** Same as Change 1 — clarifies CISE is this paper's construction, not an established external method.

### Change 3 — MAJOR fix: CISE baseline table entry
**Location:** Section 4.3, baseline table, C1 row
**Before:** `| C1 | CISE (sinusoidal PE) | Non-invariant | Established baseline (OrbitVar=0.010333) |`
**After:** `| C1 | CISE (sinusoidal PE) | Non-invariant | Representative non-invariant baseline (this work) |`
**Reason:** "Established baseline" implies prior literature — CISE is this paper's construction.

### Change 4 — MAJOR fix: C0 OrbitVar in Table 1
**Location:** Section 5.1, Table 1
**Before:** C0 row shows "~1e-33" OrbitVar and "~31 OOM" gap
**After:** C0 row shows "N/M (≈0)" and "not measured" with explanatory footnote
**Reason:** ~1e-33 was never measured in any validation file and is inconsistent with text describing C0 as "approximately invariant." Footnote explains measurement was not performed for C0.

### Change 5 — Minor wording: Contributions bullet 1
**Location:** Introduction, Contributions section, bullet 1
**Before:** "...a gap of 5 to 12 orders of magnitude confirmed..."
**After:** "...a gap of 5 to 12 orders of magnitude between invariant and non-invariant encoders, confirmed..."
**Reason:** Minor clarity improvement — specifies the direction of the gap.

---

## Issues NOT Fixed (deferred to human review)
See 065_human_review_notes.md for MINOR issues.
