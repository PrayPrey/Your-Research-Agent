# Human Review Notes
# Phase 6.5 Adversarial Review — Minor Issues for Human Review
# These issues are NOT auto-fixed. Review and apply at your discretion.

**Date**: 2026-08-31  
**Rounds Completed**: R1, R2

---

## Summary by Category

| Category | Count |
|----------|-------|
| Style | 2 |
| Clarity | 2 |
| Formatting | 1 |
| **Total** | **5** |

---

## Round 1 Issues

### Style

1. **Abstract opening hook (MINOR-001)**  
   **Section:** Abstract, sentence 1  
   **Current:** "Understanding which properties of benchmark datasets predict ML reproducibility failure could enable automated pre-review auditing of high-risk papers — but only if the required dataset metadata is accessible at scale."  
   **Issue:** Generic setup; narrative blueprint specified opening with the counterintuitive finding ("We set out to measure X and discovered Y").  
   **Suggestion:** Reorder abstract to open with: "We set out to measure how dataset documentation quality and benchmark concentration predict ML reproducibility failure — and discovered that the metadata infrastructure we assumed existed does not." Then provide motivation.  
   **Priority:** Medium (affects first impression; paper still passes engagement check)

2. **PwC recommendation confidence in abstract (MINOR-005)**  
   **Section:** Abstract, C3 reference  
   **Current:** "identify Papers With Code as the appropriate primary data source"  
   **Issue:** Stated without empirical caveat; body correctly qualifies it in Discussion 6.1.  
   **Suggestion:** Add "based on our characterization of HF+OpenML limitations" or similar qualifier.  
   **Priority:** Low

### Clarity

3. **Section 5.2 domain table "Datasets queried" column (MINOR-002)**  
   **Section:** Section 5.2, domain pattern table  
   **Issue:** Approximate counts (~10, ~15, ~5, ~5, ~15) are not explained. After R1 revision, the table was updated with more specific domain assignments but readers still cannot verify domain assignments without a supplementary list.  
   **Suggestion:** Add footnote: "Domain assignments based on primary evaluation context of each dataset in the literature. Full dataset-domain mapping available at [repo link]."  
   **Priority:** Medium

4. **"double-bind" framing (MINOR-006 — from body)**  
   **Section:** Section 5.3, paragraph 2  
   **Current:** "This reveals a double-bind: not only does HF Hub cover only 30% of the corpus, but the documentation quality signal (IV1) is weak even among covered datasets."  
   **Issue:** "Double-bind" is a somewhat informal term; a skeptical reviewer might object to the rhetorical framing. Consider "compound limitation" or "dual limitation."  
   **Priority:** Low (style preference)

### Formatting

5. **Section 5.5 table alignment (MINOR-007)**  
   **Section:** Section 5.5, Pipeline Validity table  
   **Issue:** The last row "H-E1 gate (HF ≥50% AND OpenML ≥70%)" is bold in source but the "✗ FAIL" in the right column appears inconsistently bolded across renderers.  
   **Suggestion:** Verify table renders correctly in ICML LaTeX format; bold both cells in final row.  
   **Priority:** Low (formatting only)

---

*Note: These issues do not block paper acceptance. MAJOR issues (MAJOR-001, MAJOR-002) were auto-fixed in R1 revision. These MINOR issues improve overall quality but are subject to author judgment.*
