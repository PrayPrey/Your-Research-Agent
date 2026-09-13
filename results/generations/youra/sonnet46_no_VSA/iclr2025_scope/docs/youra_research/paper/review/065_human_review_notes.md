# Human Review Notes
# Phase 6.5 Adversarial Review — Minor Issues (NOT auto-fixed)

> **Purpose:** Minor issues collected during adversarial review for human review before final submission.
> These do NOT block acceptance but improve overall quality.

**Date:** 2026-08-03  
**Rounds Completed:** 1 (R2 notes will be appended below)

---

## Summary by Category

| Category | R1 Count | R2 Count | Total |
|----------|----------|----------|-------|
| Typo | 0 | TBD | 0+ |
| Grammar | 0 | TBD | 0+ |
| Style | 1 | TBD | 1+ |
| Clarity | 1 | TBD | 1+ |
| Formatting | 1 | TBD | 1+ |

---

## Round 1 Issues

### Formatting

1. **Paper Frontmatter Internal Note**  
   Location: `06_paper.md` YAML frontmatter, `note:` field  
   Issue: "Word count exceeds ICML 8-page target (~2800 words for main text). Sections 2-4 should be condensed for final submission; supplementary material can absorb Tables 2, 5.5, and H-M2 discussion."  
   Fix: Remove this internal pipeline note before submission. It is not appropriate for a conference submission frontmatter.

### Clarity

2. **Raw vs Normalized Frobenius Distinction**  
   Location: Section 5.1, Results  
   Issue: The paper explains normalization (error/N) in Section 3.2, but does not note that raw Frobenius values grow with N (super-linear, slope ≈0.63). A reader who expects "error decreasing" could be confused when they see raw values growing. A one-sentence clarification would preempt this.  
   Suggested addition (footnote or parenthetical in Section 5.1): "The raw Frobenius norm grows with N as expected (reflecting the larger matrix size); normalization by N reveals the per-position error trend used for gate evaluation."

### Style

3. **UNVERIFIED Citation Tag in References**  
   Location: References section, MOHAWK entry  
   Issue: "[UNVERIFIED title — see bib note]" is an internal pipeline tag. Before final submission, either verify the exact MOHAWK title/venue or replace with a standard "[to be confirmed]" note and resolve via direct paper lookup.  
   Note: Semantic Scholar search returned no match for Bick et al. 2024 NeurIPS MOHAWK — attempt alternate search (try "Bick" + "SSM" + "NeurIPS 2024", or "mechanistic" + "distillation" + "Mamba").

---

## Round 2 Issues

### Internal File (not submission blocker)

4. **"1,760" Residual in h-m1/04_validation.md**  
   Location: `h-m1/04_validation.md`, Phase 2C Handoff section, "Proven Components" table  
   Issue: "Successfully fit 1,760 attention matrices" — this is the source of the FATAL-001 error now fixed in the paper. The internal validation file still has the wrong number.  
   Fix: Update `h-m1/04_validation.md` Phase 2C Handoff table: "1,760" → "1,920". Not a submission blocker (internal file), but recommended for consistency.

---

## Recommended Priority for Human Review

1. **Fix First:** Remove internal pipeline note from paper frontmatter (formatting)
2. **Fix Before Submission:** Resolve MOHAWK citation verification (style)
3. **Consider Adding:** Raw vs normalized footnote in Section 5.1 (clarity, optional)
