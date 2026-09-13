# Human Review Notes

> **Purpose:** Minor issues collected during adversarial review for human review during final polish.
> These issues are NOT auto-fixed by the revision pipeline.

**Date:** 2026-08-25
**Rounds Completed:** R1, R2

---

## Summary by Category

| Category | Count |
|----------|-------|
| Style | 2 |
| Formatting | 3 |
| Clarity | 2 |
| Typo | 0 |
| Grammar | 0 |
| **Total** | **7** |

---

## Round 1 Issues

### Style

1. **Abstract, sentence 2:** "confidence reliability" is an unusual compound — consider "confidence-accuracy reliability" for clarity.
2. **Section 3.3:** "ΔΔECE (delta-delta ECE)" — capitalization inconsistent (lowercase delta in some narrative uses vs. uppercase ΔΔECE in formal notation). Pick one convention and apply uniformly.

### Formatting

1. **Section 5.4, Table 3:** Checkmark ✓ and ✗ symbols may not render correctly in all LaTeX/PDF workflows; ensure LaTeX-compatible equivalents (e.g., `\checkmark`, `$\times$`) are used in final submission.
2. **Introduction §"The Gap" (bold sentence):** Bold formatting for the gap statement is inconsistent with rest of paper's formatting style. Check whether ICML2025 style permits bold mid-paragraph.
3. **Frontmatter:** `citations_note` field contains "[UNVERIFIED-NO-MCP]" comment — must be removed or replaced with verification status before submission.

### Clarity

1. **Discussion, L1:** Forward-references "P1 (≥60% of model × task cells show ΔECE > 0.05)" without earlier introduction of P1 notation in the main text body. Either introduce P1 in the Experimental Setup or rephrase to avoid notation.
2. **Section 5.4:** "Llama-2-7b-chat" used without the "-hf" suffix in some locations (e.g., Table 3 header abbreviation "7b pair"). For consistency, refer to the full checkpoint name on first use per section.

---

## Round 2 Issues

### Clarity

3. **Section 3.2:** After the SST-2 exclusion fix (MAJOR-ACC-002 resolution), verify the parenthetical reads naturally in context and doesn't interrupt the flow of the cell count sentence.

### Formatting

4. **Abstract (revised):** New opening sentence is longer than original; verify revised abstract stays within ICML2025 word/character limits for abstracts.

---

## Recommended Priority

1. **Fix First:** Frontmatter citation note (high visibility; reader-facing)
2. **Fix Second:** LaTeX symbol compatibility in Table 3 (formatting correctness)
3. **Consider:** Style and clarity notes (improve polish; lower urgency)

---

*Note: These issues do not block paper acceptance but improve overall quality and ICML submission readiness.*
