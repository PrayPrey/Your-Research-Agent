# Human Review Notes - Rounds 1 & 2

**Date:** 2026-04-15T04:30:00+00:00
**Paper Version:** 06_paper_r2.md (Round 2 - unchanged from R1)
**Source:** Adversary Agent Round 1 & Round 2 Reviews (065_review_r1.md, 065_review_r2.md)

**R2 Update:** Round 2 review confirmed no new minor issues were introduced. All 10 items below remain from R1.

---

## Instructions for Human Reviewer

These are MINOR issues (typos, grammar, formatting, clarity) identified by the Adversary Agent that were **NOT automatically fixed** by the Revision Agent. These require human judgment and should be addressed during final polish before submission.

**Total Issues:** 10 minor items

---

## Minor Issues for Human Review

### 1. Terminology Consistency

**Location:** Abstract, line 2

**Issue:** "AI-powered" vs "AI-assisted" - consider consistent terminology

**Type:** Style

**Note:** The paper uses both "AI-powered" and "AI-assisted" interchangeably. Choose one term and use consistently throughout the paper.

**Suggested Action:** Search-and-replace to standardize on either "AI-powered" or "AI-assisted"

---

### 2. Number Format Consistency

**Location:** Introduction, line 29

**Issue:** "over 100,000 datasets" - consider "over 100K datasets" for consistency with later usage

**Type:** Style

**Note:** The paper uses both "100,000" (spelled out) and "100K" notation. Standardize.

**Suggested Action:** Decide on one format (recommend "100,000" for formal academic writing) and use consistently

---

### 3. Notation Formatting

**Location:** Methodology, line 156

**Issue:** "Temperature = 0.7" formatting - consider consistent notation (0.7 vs. 70% in results)

**Type:** Formatting

**Note:** Temperature is correctly shown as 0.7 (not 70%), but verify consistency in how parameters are formatted throughout.

**Suggested Action:** Review all parameter notation for consistency (equals signs, spacing, units)

---

### 4. Figure Caption Phrasing

**Location:** Results, Figure 1 caption

**Issue:** "All three domains achieve" - awkward phrasing, consider "Each domain achieves"

**Type:** Clarity

**Note:** Minor grammatical improvement for readability

**Suggested Action:** Change "All three domains achieve" → "Each domain achieves" in Figure 1 caption

---

### 5. Math Clarity

**Location:** Results, line 390

**Issue:** "exceeding our target by 31%" - math seems off (92-70=22, which is 31% relative increase of 70). Clarify absolute vs relative.

**Type:** Clarity

**Note:** The statement is mathematically correct (22/70 = 31.4% relative increase), but readers may be confused expecting absolute difference.

**Suggested Action:** Rephrase to "exceeding our target by 22 percentage points (a 31% relative increase)" for clarity

**STATUS:** This line may have been removed in Round 1 revision. Verify if issue still exists.

---

### 6. Run-on Sentence

**Location:** Discussion, line 437

**Issue:** "few-shot prompting with high-quality exemplars captures cross-cutting documentation needs" - long sentence, consider breaking up

**Type:** Style

**Note:** Sentence exceeds 40 words and could be split for better readability

**Suggested Action:** Review sentence and consider splitting into 2 shorter sentences

**STATUS:** This line may have been modified in Round 1 revision. Verify if issue still exists.

---

### 7. Consistency Check - Aspirational Language

**Location:** Conclusion, line 548

**Issue:** "The path to better-documented ML research is now an engineering challenge" - see MAJOR-CRED-001, but even after revision, verify this sentence survives appropriately revised

**Type:** Clarity

**Note:** This was part of MAJOR-CRED-001 overclaiming issue. Verify the Round 1 revision adequately addressed this.

**Suggested Action:** Confirm the revised version appropriately calibrates this claim to PoC scope

**STATUS:** ADDRESSED in Round 1 revision. This sentence was completely rewritten. REMOVE from human review list.

---

### 8. Bibliography Completeness

**Location:** References

**Issue:** Verify all citations are complete (several marked as [1], [2], etc. without full bibliography)

**Type:** Formatting

**Note:** The paper uses numbered citations but the full bibliography is not included in the reviewed draft

**Suggested Action:** 
1. Create complete References/Bibliography section
2. Verify all citations are accurate and complete
3. Check citation format matches target venue requirements (ICML, etc.)

---

### 9. Metadata Removal

**Location:** Multiple sections (end of each section)

**Issue:** Several sections note word counts in the source - remove these from final version

**Type:** Formatting

**Note:** Comments like "Word count: ~550 words" appear at end of sections

**Suggested Action:** Remove all word count metadata comments before final submission

**Example locations:**
- End of Abstract: "**Word count:** 186 words..."
- End of Introduction: "**Word count:** ~550 words"
- End of each major section

---

### 10. Figure Verification

**Location:** Results section (multiple references)

**Issue:** Verify all referenced figures exist (Figure 1, 2, 3 mentioned but not shown in reviewed draft)

**Type:** Completeness

**Note:** The paper references:
- Figure 1: stratified_acceptance.png
- Figure 2: action_breakdown.png
- Figure 3: acceptance_rate_comparison.png

**Suggested Action:** 
1. Verify these figure files exist in ../figures/ directory
2. Confirm figures match descriptions in captions
3. Ensure figure quality is publication-ready
4. Verify figure formatting matches venue requirements

---

## Summary for Human Reviewer

**Priority 1 (Must Fix):**
- Issue #8: Complete bibliography
- Issue #9: Remove word count metadata
- Issue #10: Verify figures exist

**Priority 2 (Should Fix):**
- Issue #1: Terminology consistency (AI-powered vs AI-assisted)
- Issue #2: Number format consistency (100,000 vs 100K)
- Issue #5: Clarify absolute vs relative percentage (if still present)

**Priority 3 (Nice to Fix):**
- Issue #3: Parameter notation consistency
- Issue #4: Figure caption phrasing
- Issue #6: Long sentence splitting (if still present)

**Already Addressed:**
- Issue #7: Conclusion overclaiming (fixed in Round 1 revision)

---

## Notes for Final Polish

1. **Proofread entire paper** for remaining typos and grammatical errors
2. **Verify figure-caption alignment** - ensure all figure descriptions match actual figures
3. **Check cross-references** - verify all internal references (sections, figures, tables) are correct
4. **Format consistency** - consistent spacing, capitalization, notation throughout
5. **Citation accuracy** - verify all cited works are correct and complete
6. **Venue requirements** - ensure paper meets all formatting requirements for target venue

---

## Revision Agent Notes

These issues were intentionally NOT fixed by the automated Revision Agent because they require human judgment:

- **Typos and grammar:** Human proofreading more reliable than automated fixes
- **Stylistic choices:** Terminology preferences (AI-powered vs AI-assisted) are author decisions
- **Figure verification:** Requires checking actual files, beyond text revision scope
- **Bibliography completion:** Requires accurate citation lookup, not automated text generation
- **Formatting:** Final formatting should match venue requirements, decided by human

The Revision Agent focused on **MAJOR issues** (substantive problems affecting paper acceptance) and left **MINOR issues** (polish and formatting) for human review.
