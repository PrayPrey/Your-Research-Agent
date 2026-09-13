# Human Review Notes — Phase 6.5 Adversarial Review

> **Purpose:** Minor issues collected during adversarial review for human review.
> These issues are NOT auto-fixed by the Revision Agent.
> Fix before submission for maximum quality.

**Date:** 2026-08-21
**Rounds Completed:** 2 (R1, R2)
**Total Notes:** 5 (HRN-006 assessed as not a typo — see note)

---

## Summary by Category

| Category | Count |
|----------|-------|
| Typo | 0 |
| Grammar | 0 |
| Style | 2 |
| Clarity | 2 |
| Formatting | 2 |

---

## Round 1 Issues

### Style

1. **HRN-001** — Abstract, sentence 2
   - Location: "yet the aggregation step that converts a per-token sequence into a single confidence score"
   - Note: "per-token sequence" is slightly ambiguous. Consider: "per-token log-probability sequence" for precision.
   - Priority: Low (technical readers will infer; abstract real estate is scarce)

2. **HRN-002** — Introduction, Contribution 4
   - Location: "**Unexpected positive finding.**"
   - Note: Label "Unexpected positive finding" is weaker than "Unexpected finding" — the positiveness is already implied by the description. In R1, this was revised to "Unexpected finding." No further action needed.
   - Status: RESOLVED in R1 revision

### Clarity

3. **HRN-003** — Section 3.4 (Inference Protocol)
   - Location: "Custom implementation (22/22 unit tests passing) used in place of lm-polygraph due to hardware/dependency compatibility constraints."
   - Note: "due to hardware/dependency compatibility constraints" reads slightly awkward. Consider: "due to hardware and dependency compatibility constraints" or simply "to match our hardware configuration."
   - Priority: Low

4. **HRN-004** — Section 4 (Datasets Table)
   - Location: Column header "N" in the dataset table
   - Note: "N" is not defined in the table caption. Consider: "N (samples)" or add a footnote "(samples per model, LLaMA/Mistral)".
   - Priority: Medium (reviewers may notice)

### Formatting

5. **HRN-005** — Section 5.3
   - Location: "Figure 7 (`figures/fig4_summary_table.png`) summarizes P1/P2/P3 gate results."
   - Note: Figure 7 is described as a table image (PNG). In the final ICML submission, this should be a proper LaTeX table rather than a rendered PNG, to enable text search and accessibility. If time/scope allows, convert to LaTeX `tabular` in the camera-ready.
   - Priority: Medium (for camera-ready; PNG acceptable for review)

6. **HRN-006** — References
   - Location: Farquhar citation year: "[Farquhar et al., 2023]" in-text vs. "Nature, 2024" in reference list
   - Assessment: This is NOT a typo. The paper was posted to arXiv in 2023 and published in Nature in 2024. The dual-year practice (in-text arXiv year, reference list publication year) is standard and correct. No action needed.
   - Status: NO FIX REQUIRED

---

## Round 2 Issues

No new human review notes in Round 2.

---

## Recommended Priority

1. **Fix First:** HRN-004 — undefined "N" in dataset table (high visibility to reviewers)
2. **Fix Second:** HRN-001 — "per-token sequence" → "per-token log-probability sequence" (minor clarity)
3. **Consider:** HRN-003 — minor wording improvement in §3.4
4. **Camera-Ready:** HRN-005 — convert Figure 7 PNG to LaTeX table (if scope allows)
5. **No Action:** HRN-002 (resolved in R1), HRN-006 (not a typo)

---

*Note: These issues do not block paper acceptance. All FATAL and MAJOR issues have been resolved.*
