# Phase 6.5 Human Review Notes

**Generated:** 2026-07-13T19:56:00Z
**Purpose:** Minor issues for human review during final polish (NOT auto-fixed by agents)

---

## Instructions for Human Reviewer

These are stylistic, formatting, and minor clarity issues that survived adversarial review. They do NOT affect paper correctness or credibility — just polish.

**Priority:** Low (final pass before submission)
**Estimated Time:** 15-20 minutes

---

## Round 1 Notes

### Clarity Issues

#### NOTE-001: Dataset Size Threshold Explanation

**Location:** Methodology, Dataset subsection (around "minimum 32 stars")
**Issue:** "minimum 32 stars (indicating community interest)" — rationale could be explained. Why 32 not 50 or 100?
**Suggested Fix:** Add brief note: "minimum 32 stars (chosen as minimum viable community interest threshold — avoids hobby/abandoned repos while keeping dataset size reasonable)"
**Type:** clarity

#### NOTE-002: Papers with Code Domain Precision

**Location:** Abstract, line 3
**Issue:** "Papers with Code benchmark repositories" → could specify "Papers with Code ML benchmark repositories" for maximum precision
**Suggested Fix:** Add "ML" qualifier for complete accuracy
**Type:** clarity

#### NOTE-003: Methodology Dataset Threshold

**Location:** Methodology Section 3, dataset rationale
**Issue:** Staleness threshold "180 days" is referenced as "standard in repository maintenance literature" but optimality is untested. Consider adding one sentence acknowledging this is convention not optimization.
**Already Acknowledged:** Actually, paper does note "threshold sensitivity analysis needed" later. Consider cross-referencing earlier for flow.
**Type:** clarity

---

### Style Issues

#### NOTE-004: Introduction Transition Smoothness

**Location:** Introduction, paragraph 2 ("Repository maintenance prediction matters...")
**Issue:** Transition from opening hook to problem importance feels slightly abrupt
**Suggested Fix:** Consider bridging sentence: "This matters because..." or "Understanding why repository maintenance prediction is valuable clarifies what's at stake."
**Type:** style

#### NOTE-005: Limitations Ordering

**Location:** Discussion Section 6, Limitations subsection
**Issue:** L1-L4 ordering seems appropriate (domain specificity first), but consider if severity-based ordering would improve flow
**Current Order:** Domain specificity → Sample size → Temporal stability → Linear separability
**Alternative:** Could reorder by "how much this limits contribution" but current order works
**Type:** style

---

### Formatting Issues

#### NOTE-006: Table 1 Status Column Notation

**Location:** Results Section 5, Table 1 (Metrics comparison)
**Issue:** "+ 25%" notation in Status column is non-standard for academic papers
**Current:** "✓ PASS (+25%)"
**Suggested:** "✓ PASS (exceeds by 25%)" or "✓ PASS (1.0 vs 0.75)"
**Type:** formatting

#### NOTE-007: Repository URL Placeholder

**Location:** Abstract, final sentence
**Issue:** "Code and data available at [repository URL]" — placeholder not filled
**Suggested Fix:** Either fill with actual URL or change to "Code and data available in supplementary materials" if anonymous submission
**Type:** formatting

---

## Summary

**Total Notes:** 7
**By Type:**
- Clarity: 3
- Style: 2
- Formatting: 2

**Priority Breakdown:**
- High: 1 (NOTE-007 repository URL — should be resolved before submission)
- Medium: 2 (NOTE-001, NOTE-006 — improves professional appearance)
- Low: 4 (NOTE-002, NOTE-003, NOTE-004, NOTE-005 — nice-to-have polish)

---

## Notes for Final Pass

**What NOT to change:**
- Numerical claims (all verified against ground truth)
- Contribution statements (already calibrated in R1 revision)
- Limitation acknowledgments (already honest and complete)

**What to verify:**
- All citations formatted consistently
- Figure/table references point to correct numbers
- Placeholder text filled in (repository URL)
- Section numbering consecutive

**Ready for submission after:** Human final pass addressing these 7 notes + standard proofreading (typos, grammar)
