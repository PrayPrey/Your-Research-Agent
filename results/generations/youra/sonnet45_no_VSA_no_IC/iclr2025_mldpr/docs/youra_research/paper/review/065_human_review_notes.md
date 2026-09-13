# Phase 6.5 Human Review Notes

**Generated:** 2026-08-19T20:30:00Z  
**Total Notes:** 12 (8 from Adversary R1 + 4 MAJOR deferred)

---

## High Priority (4 MAJOR Issues Deferred)

### MAJOR-ACC-002: Required field range ambiguity
- **Location:** Abstract, Introduction, Results
- **Issue:** "75-95% presence" could mislead readers - combines two fields (license, version) across platforms
- **Suggested Fix:** First mention: "required fields (license, version) show 74-95% presence"
- **Priority:** High (clarity vs brevity trade-off)

### MAJOR-ENG-002: Abstract buries the lede
- **Location:** Abstract
- **Issue:** Methodology details before findings - reader may lose attention
- **Suggested Fix:** Reorder: (1) Problem, (2) Finding (45-61pp gap), (3) Method (friction score), (4) Significance
- **Priority:** High (engagement)

### MAJOR-CRED-004: "Practical impact" positioning
- **Location:** Abstract final sentence (partially fixed)
- **Issue:** "Suggesting design hypotheses" may undersell contribution vs "practical impact" oversells
- **Suggested Fix:** Find middle ground: "offering design implications for repository administrators"
- **Priority:** High (positioning vs overclaim balance)

### MAJOR-ENG-001: Generic opening (partially fixed)
- **Location:** Introduction, first sentence
- **Current:** "Why do HuggingFace datasets show 61%... " (improved but could be stronger)
- **Suggested Fix:** Full rewrite leading with specific failure scenario before statistics
- **Priority:** High (engagement)

---

## Medium Priority (Style & Formatting)

### Hyphenation consistency
- **Location:** Throughout paper
- **Issue:** "friction-reduction" vs "friction reduction" inconsistent
- **Suggested Fix:** Normalize: "friction-reduction" for compound adjective, "friction reduction" for noun phrase
- **Priority:** Medium

### Citation formatting
- **Location:** Throughout paper
- **Issue:** "Yang et al. (2024)" vs "Yang (2024)" inconsistent
- **Suggested Fix:** APA style: "Yang et al." for 3+ authors
- **Priority:** Medium (journal requirement)

### Figure 1 reference
- **Location:** Introduction
- **Issue:** No Figure 1 mentioned (Bored Reviewer test requires self-explanatory Figure 1)
- **Suggested Fix:** Verify Figure 1 exists and is referenced in text
- **Priority:** Medium

### Abstract detail level
- **Location:** Abstract, paragraph 1
- **Issue:** "friction score (0-4: automated extraction + templates + validation + API)" too detailed for abstract
- **Suggested Fix:** Shorten to "friction score (0-4 UX features)" or move detail to Introduction
- **Priority:** Medium

---

## Low Priority (Clarity & Style)

### Transition phrases
- **Location:** Introduction, "Building on this insight, we make the following contributions:"
- **Issue:** Slightly verbose
- **Suggested Fix:** "We contribute:"
- **Priority:** Low

### UX-driven vs UX-correlated
- **Location:** Related Work
- **Issue:** "UX-driven effects" assumes causality for correlational study
- **Suggested Fix:** "UX-correlated patterns"
- **Priority:** Low

### Gate Decision terminology
- **Location:** Results, "Gate Decision: PASS"
- **Issue:** May be unfamiliar to reviewers
- **Suggested Fix:** Add footnote or brief definition on first use
- **Priority:** Low

### Paragraph length
- **Location:** Throughout paper
- **Issue:** Some paragraphs 8-10 sentences (readability)
- **Suggested Fix:** Break long paragraphs at logical breaks
- **Priority:** Low

---

## Summary by Type

| Type | Count | High Priority | Medium | Low |
|------|-------|---------------|--------|-----|
| Positioning/Overclaim | 2 | 2 | 0 | 0 |
| Engagement | 2 | 2 | 0 | 0 |
| Accuracy/Clarity | 1 | 1 | 2 | 2 |
| Style/Formatting | 7 | 0 | 4 | 3 |
| **TOTAL** | **12** | **5** | **6** | **5** |

---

## Recommended Review Order

1. **MAJOR-ACC-002, MAJOR-ENG-002, MAJOR-CRED-004** (High): Positioning and engagement
2. **Hyphenation, Citation formatting, Figure 1** (Medium): Consistency for submission
3. **Abstract detail, transitions, paragraph breaks** (Low): Final polish

---

## Notes

- 5 MAJOR issues already fixed by Revision Agent (see changelog)
- These 12 notes require human judgment (positioning trade-offs, engagement style, clarity preferences)
- All numerical accuracy issues resolved - remaining are presentation/framing
