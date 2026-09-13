# Human Review Notes

> **Purpose:** Minor issues collected during adversarial review for human review.
> **v2.0:** These issues are NOT auto-fixed by AI agents - they require human judgment.

**Generated**: 2026-05-11T09:30:00.000000
**Rounds Completed**: 2 (R1, R2)
**Total Minor Issues**: 11

---

## Summary by Category

| Category | Count |
|----------|-------|
| Typo | 0 |
| Grammar | 0 |
| Style | 8 |
| Clarity | 3 |
| Formatting | 0 |
| **TOTAL** | **11** |

---

## Round 1 Issues (from 065_review_r1.md)

### Style Issues

1. **Repetitive Phrasing - "Mock data validation"**
   - **Location:** Throughout paper (15+ occurrences)
   - **Issue:** "Mock data validation" appears 15+ times
   - **Suggestion:** Consider varying with "external validation" or "data loading checks" in some instances
   - **Priority:** Low - consistency vs. variety tradeoff

2. **Repetitive Phrasing - "100% detection power with 100% false positive rate"**
   - **Location:** Abstract, Introduction, Results, Discussion (8 occurrences)
   - **Issue:** Exact phrase appears 8 times
   - **Suggestion:** Could reduce 1-2 instances while keeping key occurrences for emphasis
   - **Priority:** Low - repetition serves emphasis purpose

3. **Awkward Construction - Colon placement**
   - **Location:** Section 3.5, Line 83
   - **Issue:** "All three tiers returned hard-coded `True` values:" followed by bullet list in next paragraph
   - **Suggestion:** Either move colon after the list or restructure sentence
   - **Priority:** Low - minor formatting preference

4. **Flow Break - Disclaimer**
   - **Location:** Section 3 (Methodology), Line 109
   - **Issue:** "The following subsections describe intended functionality, not actual behavior." - Good disclaimer but breaks flow
   - **Suggestion:** Consider moving to section intro or making it a sidebar note
   - **Priority:** Low - clarity vs. flow tradeoff

5. **Section Transition**
   - **Location:** Between Section 2 and Section 3
   - **Issue:** Abrupt transition from Related Work to Methodology
   - **Suggestion:** Add transitional sentence like "Having positioned our work within the literature, we now describe the architecture we attempted to implement."
   - **Priority:** Low - helps flow but not critical

6. **Passive Voice - Results Section**
   - **Location:** Section 5 (Results), multiple instances
   - **Issue:** Some sentences use passive voice ("The detector achieved...", "All three tiers were...")
   - **Suggestion:** Consider active voice for more direct writing ("Our detector achieved...", "All three tiers returned...")
   - **Priority:** Very Low - style preference

7. **Hedging Language - Discussion**
   - **Location:** Section 6 (Discussion)
   - **Issue:** Some statements use excessive hedging ("seems to", "appears to", "might be")
   - **Suggestion:** Since evidence is clear (100% FPR), could be more definitive in some statements
   - **Priority:** Very Low - appropriate caution vs. directness

8. **Citation Format Consistency**
   - **Location:** Throughout paper
   - **Issue:** Mix of "Fu et al. (2024)" and "Fu et al., 2024" citation formats
   - **Suggestion:** Standardize to one format (preferably "Fu et al. (2024)")
   - **Priority:** Low - consistency improvement

### Clarity Issues

1. **Mathematical Notation - Table 2**
   - **Location:** Section 5.2, Table 2
   - **Issue:** Implementation rate shows "5÷15 = 33%" - could make calculation more explicit
   - **Suggestion:** Add footnote showing calculation or write as "5 of 15 tasks = 33%"
   - **Priority:** Low - already clear but could be clearer

2. **Math Notation - Section 5.2**
   - **Location:** Section 5.2, paragraph describing implementation gap
   - **Issue:** Written as "10 of 15 = 67%" without equals sign
   - **Suggestion:** Write "10÷15 = 67%" with division symbol for mathematical clarity
   - **Priority:** Very Low - already understandable

3. **Acronym First Use**
   - **Location:** Section 1 (Introduction)
   - **Issue:** "EAL" introduced without expansion on first use
   - **Suggestion:** Write "EAL (Evading Data Contamination)" on first mention
   - **Priority:** Low - readers likely know from context but good practice

---

## Round 2 Issues (from 065_review_r2.md)

### Optional Polish Items

No additional MINOR issues found in R2. The three optional suggestions from R2 were:

1. **Table 2 calculation clarity:** Could add footnote showing "5÷15 = 33%" calculation (duplicate of R1 clarity issue #1)

2. **Section 5.2 math notation:** Could write "10 of 15 = 67%" with equals sign (duplicate of R1 clarity issue #2)

3. **Section 6.3 additional qualifier:** First bullet could add "(observed need in our pipeline)" qualifier
   - **Priority:** Very Low - already well-qualified throughout paper

---

## Recommended Priority for Human Review

### High Priority (Fix These)
- None - all issues are stylistic or minor clarity improvements

### Medium Priority (Consider These)
1. Citation format consistency (easy fix, improves professionalism)
2. EAL acronym expansion on first use (good practice)
3. Table 2 / Section 5.2 math notation clarity (minor improvement)

### Low Priority (Optional)
1. Reduce "100% FPR" repetition by 1-2 instances (if feels excessive)
2. Vary "mock data validation" phrasing in 2-3 instances (if feels repetitive)
3. Section transition sentence between Section 2 and 3
4. Awkward colon placement (Section 3.5)

### Very Low Priority (Subjective Preference)
1. Passive voice → active voice conversions
2. Hedging language adjustments
3. Flow break from disclaimer (serves important purpose)
4. Additional qualifier in Section 6.3 (already well-qualified)

---

## Notes on v2.0 Review Process

**Why These Weren't Auto-Fixed:**

The v2.0 adversarial review process deliberately collects MINOR issues (typos, grammar, style, clarity, formatting) for human review rather than auto-fixing them. This approach:

1. **Preserves author voice** - Style choices reflect author intent
2. **Avoids introduction of new errors** - AI rewrites can introduce mistakes
3. **Focuses on critical issues** - FATAL and MAJOR issues get immediate attention
4. **Enables human judgment** - Some "issues" are actually defensible choices

**Human Review Recommendation:**

Review these 11 items and decide which improvements align with your writing style and submission venue requirements. None are critical for acceptance.

---

*Final Note: This paper has strong factual accuracy (all numbers verified) and appropriate scope framing (case study language throughout). These minor polish items improve readability but don't affect core contribution.*
