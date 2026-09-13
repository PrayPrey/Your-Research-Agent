# Human Review Notes — Phase 6.5 Adversarial Review

> **Purpose:** Minor issues collected during adversarial review for human polish.
> These issues are NOT auto-fixed by the Revision Agent.

**Date:** 2026-08-05T10:15:00Z
**Rounds Completed:** R1 (as of this writing)

---

## Summary by Category

| Category | Count (R1) |
|----------|-----------|
| Typo | 1 |
| Grammar | 0 |
| Style | 1 |
| Clarity | 3 |
| Formatting | 1 |
| **Total** | **6** |

---

## Round 1 Issues

### Typos

1. **Section 6.3 L5:** "undertermined" → "undetermined" *(auto-fixed in R1 revision; moved from MINOR to fixed)*

### Style

1. **Abstract:** The phrase "the first NB-2 quantification" — defensible given Phase 1 literature search, but consider whether "among the first" or "to our knowledge, the first" would be more academically hedged. This is a style preference; the current phrasing is justified by the pipeline's literature review.

### Clarity

1. **Section 3.3 Table:** "P1 — Binary Threshold" and "Mechanism" listed as separate prediction rows. The Mechanism row is not an independent prediction but a sub-test of P1 (with vs. without FE). A footnote like "ᵃMechanism test = P1 specification comparison, not a separate IV prediction" would prevent confusion.

2. **Section 4.3:** The composite score negative control is labeled as an "internal comparison" in the section header, which could be read as implying a contemporary within-study comparison. Adding "(prior episode, same corpus)" to the section header or table caption would clarify this is a historical negative control, not an ablation within the current study.

3. **Section 5.3:** "53.3% more task registrations" — computed as (IRR-1)×100 = (1.5332-1)×100 = 53.32%. Correct, but the paper also says "Within tagged datasets, tag count amplifies adoption log-linearly (IRR=1.5332 per log-unit, p<0.001)" in the Introduction. The Introduction phrasing omits the "53.3%" expression present in Section 5.3 — no inconsistency, but the introduction could reinforce with the percentage for readers who may not interpret IRR directly.

### Formatting

1. **References section:** `Trišović, A., et al. (2025). FAIR Compliance via Automated Metadata. [UNVERIFIED — verify DOI before submission]` — this placeholder must be resolved with the correct journal/proceedings citation before final submission. Do not submit with "[UNVERIFIED]" tag.

---

## Recommended Priority

1. **Fix First (Required):** Resolve the Trišović reference [UNVERIFIED] — must be a complete citation before submission.
2. **Fix Second:** Section 3.3 table footnote for Mechanism row — prevents reviewer confusion.
3. **Consider:** Section 4.3 clarifier "(prior episode, same corpus)" — prevents misreading.
4. **Optional:** Style hedge on "first NB-2 quantification" — defensible as-is.

---

*Note: These issues do not block paper acceptance but improve overall quality and reduce reviewer confusion.*
