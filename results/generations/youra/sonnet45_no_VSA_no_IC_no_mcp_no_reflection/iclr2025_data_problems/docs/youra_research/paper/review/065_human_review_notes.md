# Human Review Notes

> **Purpose:** Minor issues collected during adversarial review for human final polish.  
> These issues do NOT block paper acceptance but improve overall quality.

**Date**: 2026-08-28T16:38:00Z  
**Rounds Completed**: 1 (R1 only, early convergence)  
**Paper Status**: CONDITIONAL_ACCEPT

---

## Summary by Category

| Category | Count |
|----------|-------|
| Typo | 0 |
| Grammar | 0 |
| Style | 1 |
| Clarity | 0 |
| Formatting | 2 |
| **TOTAL** | **3** |

---

## Round 1 Issues

### Style

1. **Introduction, paragraph 4:**  
   - Location: "data quality is measurable through information density—the 'bits of learning' each token provides"
   - Issue: "bits of learning" is informal phrasing in otherwise formal paper
   - Suggestion: Either formalize ("information content per token") or define informally once and use consistently
   - Priority: OPTIONAL (adds personality vs formalism tradeoff)

### Formatting

2. **Abstract, sentence 2:**  
   - Location: "This ignores that data quality could dramatically reduce compute requirements—yet 'quality' lacks an operational definition"
   - Issue: Em dash spacing consistency (some use spaced ` — `, some unspaced `—`)
   - Suggestion: Standardize to unspaced em dash (`—`) per Chicago Manual style, or spaced per author preference
   - Priority: LOW (minor formatting consistency)

3. **Methodology, Section 3:**  
   - Location: Equation blocks (deduplication ratio, domain diversity, perplexity score formulas)
   - Issue: Verify LaTeX rendering in final PDF (equation numbering, alignment, symbol clarity)
   - Suggestion: Check that all math symbols render correctly ($$\text{dedup\_ratio}$$, $$\sum_{i=1}^{N}$$, $$\log$$)
   - Priority: MEDIUM (equations must be readable)

---

## Round 2 Issues

(Not applicable — workflow converged after R1)

---

## Round 3 Issues

(Not applicable — workflow converged after R1)

---

## Recommended Priority

1. **Fix First**: Equation formatting check (Priority: MEDIUM) — verify LaTeX rendering in Section 3
2. **Fix Second**: Em dash spacing consistency (Priority: LOW) — quick global find-replace
3. **Consider**: "bits of learning" formalization (Priority: OPTIONAL) — stylistic choice, not error

---

## Additional Notes

**Why So Few Issues?**

Paper entered Phase 6.5 already well-polished from Phase 6:
- Phase 6 Step 7 pre-validated all numerical claims against ground truth
- Narrative blueprint (Step 2) enforced clear structure, honest positioning
- Limitations section (Step 5) comprehensively documented scope gaps

Adversarial review (R1) found no structural, accuracy, or credibility issues — only cosmetic formatting notes.

**Next Steps:**

1. Human reviewer performs final pass focusing on these 3 items
2. Phase 6.5.1 generates LaTeX (will catch equation rendering issues automatically)
3. Final PDF proofread for any rendering artifacts

---

*Note: These issues do not block paper acceptance. All FATAL and MAJOR issues were already resolved (none found in R1).*
