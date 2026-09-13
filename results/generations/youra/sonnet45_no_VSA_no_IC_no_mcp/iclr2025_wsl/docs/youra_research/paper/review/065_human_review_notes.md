# Human Review Notes - Round 1

**Date**: 2026-08-25T00:00:00Z  
**Source**: Adversarial Review Round 1 (065_review_r1.md)  
**Status**: NOT_FIXED_BY_REVISION_AGENT  
**Action Required**: Final polish during human review phase  

---

## Overview

These are MINOR issues identified by the Adversary Agent that were **intentionally not fixed** by the Revision Agent. Per the workflow specification, minor issues are collected for human review during final polish rather than automated revision.

**Total Issues**: 9

---

## Minor Issues List

### MINOR-STYLE-001: Nested Parenthetical Disrupts Flow

**Location:** Abstract, paragraph 1 (ORIGINAL VERSION - may have been modified in R1 revision)

**Issue:** "Deep learning researchers in constraint-driven contexts (existing datasets and benchmarks only, no human evaluation)" — nested parenthetical disrupts reading flow

**Type:** Clarity / Style

**Suggested Fix:** Consider rephrasing to avoid nested clarification, e.g., "Deep learning researchers constrained to existing datasets and benchmarks (no human evaluation) waste months..."

**Priority:** Low

---

### MINOR-STYLE-002: Brand Capitalization

**Location:** Abstract and throughout paper

**Issue:** "HuggingFace" should be "Hugging Face" (brand capitalization per official style guide)

**Type:** Style

**Suggested Fix:** Global find-replace "HuggingFace" → "Hugging Face"

**Priority:** Low

**Note:** Verify official brand capitalization before final submission. Some venues may accept "HuggingFace" as common usage.

---

### MINOR-STYLE-003: Word Variation

**Location:** Introduction, paragraph 2

**Issue:** "This problem is particularly acute in constraint-driven research contexts such as academic labs" — consider "especially" instead of "particularly" for variation (style preference)

**Type:** Style

**Suggested Fix:** "This problem is especially acute..." (if "particularly" appears frequently in surrounding text)

**Priority:** Very Low

**Note:** This is a stylistic preference. Only change if variety improves readability.

---

### MINOR-FORMAT-001: Citation Format Verification

**Location:** Related Work section

**Issue:** "Bouthillier et al., 2021" — verify this citation format matches target venue (ICML typically uses author-year inline, but format may vary)

**Type:** Formatting

**Suggested Fix:** Cross-check all citations against target venue's style guide (e.g., ICML 2026 LaTeX template)

**Priority:** Medium (venue-specific)

**Note:** Apply consistently to all 5+ citations throughout paper.

---

### MINOR-CLARITY-001: API Implementation Detail

**Location:** Methodology, Knowledge Base Construction section

**Issue:** "We query the API for all datasets with benchmark metadata" — specify timeout/retry logic for reproducibility

**Type:** Clarity / Reproducibility

**Suggested Fix:** Add implementation detail: "We query the API for all datasets with benchmark metadata (30-second timeout, 3 retries on failure)"

**Priority:** Low

**Note:** Already partially addressed in "Implementation Details" section ("HuggingFace API accessed via REST requests with 30-second timeout"). Consider whether duplication improves clarity.

---

### MINOR-CLARITY-002: Experimental Setup Blinding

**Location:** Experimental Setup, Formal Verification False Positive Rate (h-m2)

**Issue:** "Three independent DL researchers label each hypothesis via majority vote" — were reviewers blinded to system classifications? Potential bias if not.

**Type:** Clarity / Methodology

**Suggested Fix:** Add blinding protocol: "Three independent DL researchers, blinded to system classifications, label each hypothesis via majority vote"

**Priority:** Medium (methodology transparency)

**Note:** If reviewers were NOT blinded, acknowledge as limitation in Discussion.

---

### MINOR-FORMAT-002: Scientific Notation Inconsistency

**Location:** Results, Experimental Success Rate (h-m4)

**Issue:** "P-value distribution: range 8.36e-07 to 0.757, median 0.0010" — scientific notation inconsistency (8.36e-07 vs 0.757)

**Type:** Formatting

**Suggested Fix:** Normalize notation: either "range 8.36×10⁻⁷ to 7.57×10⁻¹" OR "range 0.000000836 to 0.757" (if venue prefers decimal)

**Priority:** Low

**Note:** Check venue style guide for preferred scientific notation format.

---

### MINOR-STYLE-004: Abbreviation for Readability

**Location:** Discussion, Limitations section

**Issue:** "Multi-source KB aggregation (HuggingFace + Papers With Code + TensorFlow Datasets + Google Dataset Search)" — abbreviate after first mention for readability

**Type:** Style / Readability

**Suggested Fix:** First mention: "Multi-source KB aggregation (HuggingFace + Papers With Code + TensorFlow Datasets + Google Dataset Search, hereafter 'multi-source aggregation')" → Later: "Multi-source aggregation is projected to achieve 95%+ coverage"

**Priority:** Very Low

**Note:** Only apply if this phrase appears multiple times. Single occurrence does not require abbreviation.

---

### MINOR-STRUCTURE-001: Conclusion Repetition

**Location:** Conclusion, paragraph 4

**Issue:** "The broader contribution extends beyond testability classification: we establish that meta-research evaluation need not be circular" — this statement is already covered in Discussion paragraph 1. Conclusion paragraph 4 repeats Discussion content.

**Type:** Structure / Redundancy

**Suggested Fix:** Consider moving broader impact discussion entirely to Discussion section, keeping Conclusion focused on concrete contributions (problem solved, 90% accuracy, future work directions). OR condense Conclusion paragraph 4 to 1-2 sentences referencing Discussion without repeating full argument.

**Priority:** Low

**Note:** Some venues prefer Conclusions with broader impact restatement; others prefer concise summary. Check target venue norms.

---

## Summary by Type

| Type | Count | Priority Distribution |
|------|-------|---------------------|
| Style | 4 | Low: 3, Very Low: 1 |
| Formatting | 2 | Low: 1, Medium: 1 |
| Clarity | 2 | Low: 1, Medium: 1 |
| Structure | 1 | Low: 1 |
| **Total** | **9** | **Medium: 2, Low: 5, Very Low: 2** |

---

## Recommended Action Plan

**For Final Human Review:**

1. **Medium Priority (2 issues):**
   - MINOR-FORMAT-001: Verify citation format against target venue style guide (ICML/NeurIPS/ICLR)
   - MINOR-CLARITY-002: Clarify whether expert labelers were blinded to system classifications (add to methodology OR acknowledge as limitation)

2. **Low Priority (5 issues):**
   - MINOR-STYLE-002: Global find-replace "HuggingFace" → "Hugging Face" (verify brand style first)
   - MINOR-CLARITY-001: Consider adding API timeout/retry details to Methodology (may be redundant with Implementation Details section)
   - MINOR-FORMAT-002: Normalize scientific notation for p-value ranges
   - MINOR-STRUCTURE-001: Check if Conclusion paragraph 4 repeats Discussion content unnecessarily
   - MINOR-STYLE-001: Review Abstract flow (may already be fixed in R1 revision)

3. **Very Low Priority (2 issues):**
   - MINOR-STYLE-003: Word variation ("particularly" → "especially") — only if stylistic variety improves readability
   - MINOR-STYLE-004: Abbreviate multi-source aggregation phrase — only if it appears multiple times

---

## Notes

- All issues in this file are **cosmetic, stylistic, or formatting** concerns
- **No accuracy, credibility, or engagement issues** remain (those were addressed in R1 revision)
- Human reviewer should prioritize Medium issues, apply Low issues as time permits, skip Very Low issues unless quick wins
- Final polish should be conducted with target venue style guide (ICML/NeurIPS/ICLR LaTeX template) for consistent formatting
