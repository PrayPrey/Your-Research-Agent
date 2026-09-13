# Phase 6.5 Adversarial Review — Changelog

**Paper:** Quality Filters as Demographic Reweighting
**Review date:** 2026-03-15
**Rounds:** R1, R2

---

## Summary of Changes

| File | Change Type | Description |
|------|-------------|-------------|
| paper/sections/05_results.md | MAJOR fix | Corrected Table 2 entropy values |
| paper/sections/05_results.md | Text revision | Updated descriptive text for C0 and C6 values |
| paper/sections/05_results.md | Text revision | Added nonlinearity observation (C4→C5 step) |
| paper/sections/05_results.md | Text revision | Updated DoReMi log-odds interpretation |
| paper/06_paper.md | MAJOR fix | Corrected Table 2 entropy values |
| paper/06_paper.md | Text revision | Added nonlinearity note to C5 observation |
| paper/06_paper_final.md | NEW FILE | Final combined paper with all revisions |
| paper/065_review_summary.md | NEW FILE | Adversarial review process summary |
| paper/065_changelog.md | NEW FILE | This file |
| paper/065_human_review_notes.md | NEW FILE | Minor issues for human reviewer |
| paper/065_checkpoint.yaml | NEW FILE | Phase 6.5 checkpoint |

---

## Detailed Changes

### Change 1: Table 2 Entropy Values Corrected (MAJOR fix)

**Files:** paper/sections/05_results.md, paper/06_paper.md

**Original values (from 065_ground_truth.yaml, inconsistent with validation report):**

| Config | Old Value (bits) | Old Relative |
|--------|-----------------|--------------|
| C0 | 3.3159 | +0.69% |
| C2 | 3.1847 | −2.62% |
| C3 | 3.0621 | −6.36% |
| C4 | 2.8934 | −11.52% |
| C6 | 3.0541 | −6.61% |

**Corrected values (from h-e1/04_validation.md actual experimental output):**

| Config | New Value (bits) | New Relative |
|--------|-----------------|--------------|
| C0 | 3.2662 | −0.12% |
| C2 | 3.2528 | −0.53% |
| C3 | 3.2275 | −1.31% |
| C4 | 3.1106 | −4.88% |
| C6 | 3.2209 | −1.51% |

**Unchanged (verified correct in both sources):**
- C1: 3.2702 bits (reference)
- C5: 2.5374 bits, −22.41%

**Impact on claims:**
- The headline claim (-22.41% C1→C5) is UNCHANGED — both C1 and C5 values were correct in original
- The monotonic ordering (C1 > C2 > C3 > C4 > C5) is CONFIRMED in corrected values
- The DoReMi comparison changes: C6 (3.2209) is now close to C1, not between C1 and C3
- The nonlinear pattern becomes visible: most compression occurs at C4→C5 step

### Change 2: Descriptive Text Updated to Reflect Corrected Data

**File:** paper/sections/05_results.md

**Original text (excerpt):**
> "with C6 (DoReMi reweighting: 3.0541 bits) falling between C1 and C2. The unfiltered C0 corpus has entropy 3.3159 bits — higher than all filtered configurations."

**Revised text:**
> "with C6 (DoReMi reweighting: 3.2209 bits) slightly below C1. The unfiltered C0 corpus has entropy 3.2662 bits — nominally below C1, consistent with very low filtering having minimal impact. The large entropy drop concentrates at the C4→C5 transition (3.1106 → 2.5374 bits, −18.4% in that step alone), indicating that the 90th percentile threshold is where the demographic-occupation association compression becomes dramatic."

### Change 3: Nonlinearity Observation Added

**File:** paper/sections/05_results.md, paper/06_paper.md

Added observation that the effect is highly nonlinear: intermediate configurations (C2-C4) show modest reductions of 0.5-4.9%, while the jump from C4 to C5 accounts for the bulk of total compression. This is a genuine finding from the corrected data that strengthens the paper's argument about the production threshold being the critical operating point.

### Change 4: DoReMi Log-Odds Interpretation Updated

**File:** paper/sections/05_results.md

Updated DoReMi interpretation to note consistency between DoReMi's entropy (3.2209 bits, close to unfiltered) and log-odds (0.643, slightly below C1) — both indicate domain reweighting preserves more demographic diversity than fastText quality filtering.

### Change 5: Abstract p-value notation (intro/conclusion unchanged)

**File:** paper/06_paper_final.md (final paper only)

Changed "p≈0" to "p=1.4×10⁻²⁴" in the abstract and C1 contribution statement for statistical precision. The original section files retain "p≈0" notation (listed as minor issue for human review).

### Change 6: Discussion updated for nonlinearity finding

**File:** paper/06_paper_final.md (final paper only)

Added to Finding 1 in Discussion: "The nonlinear entropy pattern (modest reductions C1-C4; dramatic drop at C5) indicates that the production threshold (≥90th percentile) is the critical operating point where demographic consequences become substantial."

---

## Rationale for Value Discrepancy

The entropy values in 065_ground_truth.yaml (used by the original paper) appear to have been taken from verification_state.yaml or an alternate source that did not match the h-e1/04_validation.md output from the actual experiment. The validation report is the primary source for experimental results per pipeline design. The discrepancy does not affect any gate decisions (all gates depend on C1 and C5, which matched across sources) but does affect the per-configuration values reported in Table 2.

---

## Verification Status Post-Revision

All numerical claims in the final paper (06_paper_final.md) are verified against:
- h-e1/04_validation.md (entropy values, Spearman rho, bootstrap CI)
- h-m1/04_validation.md (log-odds values, Spearman rho)
- h-m2/04_validation.md (logit margins, Spearman rho, R², negative control)
- verification_state.yaml (gate results, task counts, unit tests)
