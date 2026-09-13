# Human Review Notes - Round 1 (MINOR Issues)

**Date:** 2026-04-15  
**Source:** 065_review_r1.md  
**Status:** Collected for human copy-editing (NOT auto-fixed per v2.0 protocol)

---

## INSTRUCTIONS FOR HUMAN REVIEWER

These are MINOR issues identified by the adversarial review that were **intentionally NOT auto-fixed** by the revision agent. Per v2.0 protocol, grammar/style/formatting issues should be reviewed and fixed by human copy-editor to avoid over-automation.

**Total MINOR Issues:** 9  
**Categories:** Grammar (2), Style (3), Citations (3), Formatting (1)

---

## CATEGORY 1: GRAMMAR & ARTICLES

### MINOR-001: Article Usage - "a natural" vs "the natural"

**Location:** Abstract Line 5 (now fixed in R1, but flagged for verification)  
**Current Text (R1):** "This raises the natural but largely-unexplored question"  
**Review Note:** Article changed from "a" to "the" during revision. Verify this reads naturally.  
**Recommendation:** Keep "the natural" (implies THE obvious question, stronger framing)  
**Priority:** LOW

---

### MINOR-002: Hyphenation - Compound Adjectives

**Location:** Abstract, Introduction (multiple instances)  
**Current Text:** "largely-unexplored question" (R1 has hyphen)  
**Original Text:** "largely unexplored question" (R0 no hyphen)  
**Review Note:** R1 added hyphen for compound adjective consistency. Verify style guide preference.  
**Recommendation:** Check ICML style guide - compound adjectives before nouns typically hyphenated  
**Priority:** LOW

---

## CATEGORY 2: STYLE & READABILITY

### MINOR-003: Opening Sentence Length - Introduction

**Location:** Introduction Para 1, Line 24  
**Current Text (R1):** "Foundation model pretraining uses static domain mixing ratios—typically fixed proportions like 60% web text, 20% code, and 20% books throughout training—determined through expensive hyperparameter sweeps across thousands of GPU hours."  
**Issue:** Run-on sentence (42 words). Dense with embedded clauses.  
**Recommendation:** Consider splitting into two sentences:
```
Foundation model pretraining uses static domain mixing ratios—typically fixed proportions like 60% web text, 20% code, and 20% books throughout training. These ratios are determined through expensive hyperparameter sweeps across thousands of GPU hours.
```
**Priority:** MEDIUM (readability improvement)

---

### MINOR-004: Passive Voice - Abstract Line 12

**Location:** Abstract Para 1, Line 12  
**Current Text (R1):** "Path-dependent SGD optimization in non-convex deep learning means that early training phases may disproportionately shape representational geometry"  
**Issue:** Could be more active/direct  
**Recommendation:** Consider: "In non-convex deep learning, path-dependent SGD optimization means early training phases disproportionately shape representational geometry"  
**Priority:** LOW (stylistic preference)

---

### MINOR-005: Phrasing - "All 22 unit tests pass"

**Location:** Abstract Para 2, Line 14  
**Current Text (R1):** "all 22 unit tests pass"  
**Alternative:** "all unit tests (22/22) pass" or "22 out of 22 unit tests pass"  
**Recommendation:** Current phrasing acceptable, but alternative may be clearer  
**Priority:** LOW

---

## CATEGORY 3: CITATIONS & REFERENCES

### MINOR-006: Missing Citation for "Thousands of GPU Hours" Claim

**Location:** Introduction Para 1, Line 24  
**Current Text (R1):** "expensive hyperparameter sweeps across thousands of GPU hours"  
**Issue:** Dramatic quantitative claim without citation  
**Recommendation:** Either:
- Add citation (e.g., GPT-3 training cost papers, Chinchilla scaling laws)
- Soften language: "expensive hyperparameter sweeps requiring substantial GPU resources"
- Remove "thousands" if no citation available
**Priority:** MEDIUM (unsupported quantitative claim)

---

### MINOR-007: Incomplete References Section

**Location:** References section (Line 41)  
**Current Text (R1):** "[See 06_references.bib]"  
**Issue:** Placeholder text instead of actual reference list  
**Recommendation:** Generate full BibTeX-formatted reference list for all in-text citations:
- Bengio et al., 2009 (curriculum learning)
- Xie et al., 2023 (DoReMi)
- Chen et al., 2021 (Codex)
- Brown et al., 2020 (GPT-3)
- Chowdhery et al., 2022 (PaLM)
- Touvron et al., 2023 (Llama)
- Gao et al., 2020 (The Pile)
- Hendrycks et al., 2021 (MMLU)
- BIG-bench Collaboration, 2022
- [... and all other citations in Sections 2-7]
**Priority:** HIGH (required for submission)

---

### MINOR-008: Repository URL Placeholder

**Location:** Appendix A, Line 49  
**Current Text (R1):** "will be released upon publication at [repository URL]"  
**Issue:** Placeholder instead of actual URL or anonymization statement  
**Recommendation:** For blind review submission:
- "will be released upon publication at [URL withheld for blind review]"
- Or: "will be released upon publication at https://anonymous.4open.science/..."
**Priority:** MEDIUM (standard for blind review)

---

## CATEGORY 4: FORMATTING & CONSISTENCY

### MINOR-009: Affiliation Anonymization

**Location:** Paper header, Lines 3-7  
**Current Text (R1):**
```
**Authors:** [Anonymous for Review]
**Affiliation:** [Anonymous for Review]
**Correspondence:** [Anonymous for Review]
```
**Issue:** Placeholder formatting acceptable for blind review, but verify journal submission requirements  
**Recommendation:** Check ICML formatting guide for proper anonymization format  
**Priority:** LOW (likely acceptable as-is)

---

## ADDITIONAL RECOMMENDATIONS (NOT FROM REVIEW)

### Figure 1 Missing (MAJOR Issue Deferred)

**Location:** Introduction (should appear after Para 4)  
**Issue:** ENGAGE-MAJOR-002 identified missing Figure 1 (curriculum visualization)  
**Status:** Deferred to asset creation (requires visualization)  
**Recommendation:** Create figure showing:
- X-axis: Training progress (0-100%)
- Y-axis: Domain sampling weights
- Curves: Gaussian-weighted transitions for 6 domains (Pile-CC → PubMed)
- Caption: "Figure 1: Diversity-ranked curriculum schedule showing smooth Gaussian-weighted domain transitions. High-diversity domains (Pile-CC, StackExchange) peak early, while low-diversity domains (Github, PubMed) peak late."
**Priority:** HIGH (significantly improves skimmability)

---

## PRIORITY SUMMARY

| Priority | Count | Issues |
|----------|-------|--------|
| HIGH | 2 | MINOR-007 (References), Figure 1 (deferred) |
| MEDIUM | 3 | MINOR-003 (sentence length), MINOR-006 (GPU hours citation), MINOR-008 (repo URL) |
| LOW | 6 | MINOR-001, 002, 004, 005, 009 (style/grammar) |

---

## REVIEW CHECKLIST FOR HUMAN COPY-EDITOR

- [ ] **References:** Generate complete BibTeX list from all in-text citations (HIGH)
- [ ] **Figure 1:** Create curriculum visualization diagram (HIGH)
- [ ] **Introduction Para 1:** Consider splitting 42-word opening sentence (MEDIUM)
- [ ] **GPU Hours Claim:** Add citation or soften language (MEDIUM)
- [ ] **Repository URL:** Update placeholder for blind review (MEDIUM)
- [ ] **Style Pass:** Review hyphenation, passive voice, phrasing preferences (LOW)
- [ ] **Formatting:** Verify ICML style guide compliance (anonymization, figures, tables) (LOW)

---

## NOTES FOR REVISION AGENT

**Why These Were NOT Auto-Fixed:**

1. **Grammar/Style (MINOR-001 to 005):** Subjective preferences that may vary by author voice and style guide. Human judgment required.

2. **Citations (MINOR-006 to 008):** Require external research (finding correct papers, BibTeX formatting). Outside scope of adversarial review response.

3. **Formatting (MINOR-009):** Journal-specific requirements vary. Human verification needed.

4. **Figure 1:** Requires asset creation (visualization tool, graphic design). Cannot be auto-generated from text alone.

**Auto-Fix Boundary:** Revision agent fixed all issues that were:
- Objectively incorrect (FATAL: calculation errors, missing sections)
- Content gaps (MAJOR: missing value proposition, vague claims)
- Structural problems (MAJOR: timeline inconsistencies, scope ambiguities)

Revision agent did NOT fix issues that require:
- Subjective style judgment
- External research/assets
- Journal-specific formatting decisions

This boundary preserves author voice while ensuring scientific accuracy and structural completeness.

---

**Human review notes completed:** 2026-04-15  
**Next step:** Human copy-editor addresses HIGH and MEDIUM priority items before R2 submission

---

## Round 2 Issues (Numerical Verification Review)

**Date:** 2026-04-15  
**Source:** 065_review_r2.md  
**Status:** Collected for human copy-editing (NOT auto-fixed per v2.0 protocol)

**R2 Review Verdict:** CONDITIONAL ACCEPT (0 FATAL, 2 MAJOR [FIXED], 8 MINOR [BELOW])

---

## CATEGORY 1: GRAMMAR & CONSISTENCY

### R2-MINOR-001: Hyphenation Inconsistency - "path-dependent" vs "path dependent"

**Locations:** Multiple sections  
**Current Usage:**
- Abstract L13: "Path-dependent SGD optimization" (hyphenated)
- Introduction L25: "optimization is fundamentally path-dependent" (hyphenated)
- Introduction L29: "through path-dependent optimization" (hyphenated)
- Section 2.4: Usage varies

**Issue:** Inconsistent hyphenation of compound adjectives. "Path-dependent" should be hyphenated when used as compound adjective before noun, but current usage appears consistent. Verify throughout paper.

**Recommendation:** Maintain "path-dependent" (hyphenated) consistently as compound adjective. Check all instances.

**Priority:** LOW (appears mostly consistent in sample)

---

### R2-MINOR-002: Introduction Opening Sentence Length (42 Words)

**Location:** Introduction Line 25  
**Current Text:** "Foundation model pretraining uses static domain mixing ratios—typically fixed proportions like 60% web text, 20% code, and 20% books throughout training—determined through expensive hyperparameter sweeps across thousands of GPU hours."

**Issue:** Long sentence (42 words) with embedded clause creating density. Could impact readability for skimmers.

**Recommendation:** Consider splitting:
```
Foundation model pretraining uses static domain mixing ratios—typically fixed proportions like 60% web text, 20% code, and 20% books throughout training. These ratios are determined through expensive hyperparameter sweeps across thousands of GPU hours.
```

**Priority:** MEDIUM (readability improvement)

---

### R2-MINOR-003: Citation Spacing Inconsistency

**Locations:** Throughout paper  
**Issue:** Inconsistent spacing around parenthetical citations

**Examples:**
- "(Bengio et al., 2009)" - standard
- "(Xie et al., 2023)" - standard
- Some may have extra spaces before punctuation

**Recommendation:** Verify consistent spacing: "text (Author, Year)" with no space before opening parenthesis, single space after comma.

**Priority:** LOW (likely already consistent, requires verification)

---

## CATEGORY 2: STYLE & CLARITY

### R2-MINOR-004: Temporal Construction - "While X, then Y"

**Location:** Section 2 (exact line not specified in R2 review)  
**Issue:** Awkward temporal construction mixing "While" (simultaneous) with "then" (sequential)

**Example Pattern:** "While X does Y, then Z happens"  
**Problem:** "While" implies simultaneity, "then" implies sequence—contradictory temporal markers

**Recommendation:** Rephrase to use consistent temporal markers:
- "While X does Y, Z also happens" (both simultaneous)
- "After X does Y, then Z happens" (both sequential)

**Priority:** MEDIUM (clarity improvement)

**Note:** Requires locating specific instance in Section 2 via text search.

---

### R2-MINOR-005: Abstract Line 12 - Passive Voice

**Location:** Abstract Line 12  
**Current Text:** "Path-dependent SGD optimization in non-convex deep learning means that early training phases may disproportionately shape representational geometry"

**Issue:** Could use more active construction (though current version is acceptable)

**Alternative:** "In non-convex deep learning, path-dependent SGD optimization means early training phases disproportionately shape representational geometry"

**Recommendation:** Consider rephrasing for directness, but current version is grammatically correct.

**Priority:** LOW (stylistic preference)

---

### R2-MINOR-006: Article Usage Preference

**Location:** Introduction Line 25  
**Current Text:** "This raises the natural but largely-unexplored question"  
**Alternative:** "This raises a natural but largely-unexplored question"

**Issue:** "the natural" (definite article) implies THE obvious question (stronger). "a natural" (indefinite) implies one among possible questions (softer).

**Recommendation:** Keep "the natural" for stronger framing (current R1 choice). Verify this matches author intent.

**Priority:** LOW (stylistic preference, current choice is valid)

---

## CATEGORY 3: CROSS-REFERENCE CLARITY

### R2-MINOR-007: Abstract Training Steps Ambiguity

**Location:** Abstract Line 17  
**Current Text:** "Planned Phase 5 experiments (40 runs: 4 conditions × 2 scales × 5 seeds, 100K-150K steps)"

**Issue:** "100K-150K steps" could be misread as "both scales train between 100K-150K steps" when actually 1B trains for 100K, 7B trains for 150K.

**Clarification Needed:** Section 4.5 specifies "100K steps at 1B, 150K steps at 7B" but Abstract is ambiguous.

**Recommendation:** Change to: "100K steps (1B) / 150K steps (7B)" or "100K-150K steps depending on scale"

**Priority:** MEDIUM (cross-reference clarity)

---

## CATEGORY 4: FORMATTING & FLOW

### R2-MINOR-008: Appendix C Note Positioning

**Location:** Appendix C, Line 715 (after smoke test table)  
**Current Text:** "*Note: Static condition maintains uniform weights throughout. Diversity-ranked Gaussian-weighted transitions validated via unit tests (6/6 scheduler tests pass), not executed in smoke test.*"

**Issue:** Note appears AFTER the table showing static weights. Could improve flow by moving ABOVE table so reader understands context before seeing data.

**Recommendation:** Move note to appear before Table (currently after).

**Priority:** LOW (formatting preference)

---

## PRIORITY SUMMARY (ROUND 2)

| Priority | Count | Issues |
|----------|-------|--------|
| MEDIUM | 3 | R2-MINOR-002 (sentence length), R2-MINOR-004 (temporal construction), R2-MINOR-007 (cross-ref) |
| LOW | 5 | R2-MINOR-001, 003, 005, 006, 008 (style/grammar) |
| **TOTAL** | **8** | All deferred to human copy-editor |

---

## REVIEW CHECKLIST FOR HUMAN COPY-EDITOR (ROUND 2)

- [ ] **Introduction Sentence:** Consider splitting 42-word opening sentence (MEDIUM)
- [ ] **Temporal Construction:** Locate and fix "While X, then Y" in Section 2 (MEDIUM)
- [ ] **Cross-Reference:** Clarify "100K-150K steps" in Abstract to specify per-scale (MEDIUM)
- [ ] **Hyphenation:** Verify "path-dependent" consistent throughout (LOW)
- [ ] **Citation Spacing:** Verify consistent spacing around citations (LOW)
- [ ] **Passive Voice:** Consider more active construction in Abstract L12 (LOW)
- [ ] **Article Usage:** Verify "the natural" vs "a natural" matches intent (LOW)
- [ ] **Table Note:** Consider moving Appendix C note above table (LOW)

---

## NOTES FOR REVISION AGENT (ROUND 2)

**Why R2 MINOR Issues Were NOT Auto-Fixed:**

Per v2.0 protocol boundary:

1. **Grammar/Style (R2-MINOR-001, 003, 005, 006, 008):** Subjective preferences requiring human judgment. Current versions are grammatically correct; alternatives are style choices.

2. **Readability (R2-MINOR-002, 004):** Sentence restructuring changes author voice. While 42-word sentence is dense, it's not incorrect. Human should decide based on target audience.

3. **Cross-Reference (R2-MINOR-007):** Ambiguity is minor (Section 4.5 clarifies), but Abstract should be self-contained. Human judgment needed on whether to add characters to Abstract for clarity vs maintaining brevity.

**Auto-Fix Boundary (R2):**
- ✓ FIXED: Missing numerical data (all 6 diversity scores now in Abstract)
- ✓ FIXED: Inconsistent qualifier strength (Introduction now matches Abstract tone)
- ✗ NOT FIXED: Style preferences, optional readability improvements, formatting choices

This preserves author voice while ensuring scientific accuracy and numerical transparency.

---

## COMPARISON: R1 vs R2 MINOR ISSUES

| Metric | Round 1 | Round 2 | Notes |
|--------|---------|---------|-------|
| Total MINOR | 9 | 8 | -1 (improvement) |
| Grammar | 2 | 2 | Similar |
| Style | 3 | 3 | Similar |
| Citations | 3 | 1 | Improved (R1 added citations) |
| Formatting | 1 | 2 | Similar |

**Key Difference:** R2 MINOR issues are truly minor (style preferences, optional readability). R1 MINOR issues included missing references (now resolved). R2 represents polishing stage, not structural fixes.

---

**Round 2 human review notes completed:** 2026-04-15  
**Next step:** Human copy-editor addresses MEDIUM priority items (3 issues), optionally LOW priority (5 issues)  
**Expected effort:** 15-30 minutes for MEDIUM issues, 15-30 minutes additional for LOW issues  
**Paper status after human review:** Publication-ready for technical report or workshop venue
