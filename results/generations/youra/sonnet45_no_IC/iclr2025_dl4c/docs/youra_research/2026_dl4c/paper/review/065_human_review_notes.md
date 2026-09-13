# Human Review Notes - Round 1

**Paper:** Tri-Modal Reinforcement Learning with Dynamic Feedback Scheduling for Code Generation  
**Review Date:** 2026-07-12  
**Status:** MINOR issues for optional polishing (not blocking publication)

---

## Overview

This document collects minor issues (typos, grammar, style preferences) found during Round 1 adversarial review that were NOT fixed in R1 revision. These are subjective or low-priority issues that human reviewers may choose to address during final polishing.

**Total Minor Issues:** 11

---

## 1. Grammar and Usage

### Issue 1.1: Singular vs Plural "Curriculum"

**Location:** Line 30 (Introduction)

**Current Text:**
```
No existing method explores curriculum over feedback modality
```

**Suggested Change:**
```
No existing method explores curricula over feedback modality
```

**Rationale:** 
- "Explores curriculum" (singular) suggests examining one curriculum as an object
- "Explores curricula" (plural) suggests investigating curriculum approaches as a category
- Both are grammatically correct; depends on intent
- Current phrasing is acceptable

**Priority:** LOW (stylistic preference)

---

### Issue 1.2: Parenthetical Interruption

**Location:** Line 144 (Methods)

**Current Text:**
```
Weight trajectories are logged at every checkpoint (every 100 steps) for later analysis.
```

**Suggested Change:**
```
Weight trajectories are logged every 100 steps for later analysis.
```

**Rationale:**
- Parenthetical "(every 100 steps)" interrupts sentence flow
- Alternative phrasing is more direct
- Current phrasing is acceptable in academic writing (provides precision)

**Priority:** LOW (flow optimization)

---

## 2. Style and Clarity

### Issue 2.1: Metaphor Mixing

**Location:** Line 474 (Conclusion)

**Current Text:**
```
The next chapter—whether this mechanistic soundness yields performance advantages at scale—awaits empirical investigation. We have shown the path is walkable; future work must determine whether it leads to the destination.
```

**Issue:**
- "Next chapter" (book metaphor)
- "Path is walkable" (journey metaphor)
- Mixed metaphors in same paragraph

**Suggested Change:**
```
The next step—whether this mechanistic soundness yields performance advantages at scale—awaits empirical investigation. We have shown the path is walkable; future work must determine whether it leads to the destination.
```

**Rationale:** "Next step" aligns with journey metaphor used throughout conclusion

**Priority:** LOW (stylistic consistency)

---

### Issue 2.2: Abstract Length

**Location:** Lines 17-19 (Abstract)

**Current State:** Single paragraph, 223 words

**Suggested Change:** Split into 2 paragraphs:
- Paragraph 1: Problem + Key Result + Approach (120 words)
- Paragraph 2: Limitations + Implications (103 words)

**Rationale:**
- Dense single-paragraph abstracts are harder to skim
- Two-paragraph format improves readability
- Some venues prefer split format

**Priority:** MEDIUM (readability, venue-dependent)

---

## 3. Terminology Consistency

### Issue 3.1: "Mechanism Validation" vs "PoC Validation"

**Location:** Throughout paper

**Current State:** Both terms used interchangeably:
- "Mechanism validation" (Abstract, Discussion, Conclusion)
- "Proof-of-concept validation" (Methods, Discussion)
- "PoC validation" (Discussion)

**Suggested Change:** Standardize to "mechanism validation" as primary term, use "proof-of-concept" only when contextually appropriate

**Rationale:**
- "Mechanism validation" is more precise (tests mechanism, not full system)
- "PoC" connotes prototype/demo, while "mechanism" connotes rigorous testing
- Current mixed usage is acceptable but could be tightened

**Priority:** LOW (consistency)

---

### Issue 3.2: "Feedback Modality" vs "Feedback Type" vs "Feedback Signal"

**Location:** Throughout paper

**Current State:** All three terms used:
- "Feedback modality" (preferred term, aligns with novelty claim)
- "Feedback type" (used interchangeably)
- "Feedback signal" (used for individual signals)

**Suggested Change:** Use "feedback modality" for curriculum concept, "feedback signal" for individual signals, avoid "feedback type"

**Rationale:**
- "Modality" is the technical term (aligns with "feedback modality curriculum" contribution)
- "Signal" refers to individual instances (execution signal, AI signal)
- "Type" is colloquial, less precise
- Current usage is acceptable but could be standardized

**Priority:** LOW (precision)

---

## 4. Formatting and Presentation

### Issue 4.1: Figure References Without Figures

**Location:** Lines 238, 275, 323 (Results)

**Current Text:**
```
Figure 1 shows weight trajectories across Phase 1 checkpoints.
Figure 2 shows weight trajectories across Phase 2.
Figure 3 shows weight trajectories across Phase 3.
```

**Issue:** Figures mentioned but not included in markdown document

**Resolution Options:**
1. Add figures inline (if available)
2. Remove figure references (tables provide same info)
3. Note "Figure X (see separate figure file)" if figures exist externally

**Rationale:** Current format creates expectation for visual that isn't present

**Priority:** MEDIUM (completeness)

---

### Issue 4.2: Table Footnotes

**Location:** Line 217 (Table 1)

**Current State:** Table 1 shows identical metrics (0.00, 0.36, 0.00) for all models without footnote

**Suggested Addition:**
```
**Table 1:** Baseline comparison results using pretrained CodeGen-350M without RL training. All models achieve 0% pass@1 as expected for pretrained checkpoints on competitive programming. Human preference scores (0.36) reflect code quality heuristics applied uniformly. [FOOTNOTE: Identical values expected—all models use pretrained checkpoint without RL training (see Section 3.7 limitation disclosure)]
```

**Rationale:** Clarifies why all models have identical metrics (prevents reader confusion)

**Priority:** LOW (clarification)

---

### Issue 4.3: Equation Formatting Inconsistency

**Location:** Throughout paper

**Current State:**
- Some equations use display mode `$$` mid-paragraph (lines 118-120)
- Others use inline mode `$` (line 137)

**Suggested Change:** 
- Inline equations: use `$...$` (mid-paragraph)
- Standalone equations: use `$$...$$` (separate line)

**Rationale:** Standard LaTeX convention for readability

**Priority:** LOW (formatting consistency)

---

## 5. Citation Issues

### Issue 5.1: Unverified Citation (Li et al. 2025)

**Location:** References, line 563

**Current State:**
```
@article{LiEtAl2025CurriculumRLAIF,
  ...
  note = {Citation mentioned in paper - exact reference not found in Semantic Scholar search. Related work includes curriculum learning approaches for code generation.}
}
```

**Issue:** Paper cited in text but reference not verified

**Resolution Options:**
1. Find correct citation and verify
2. Mark as "personal communication" or "unpublished work"
3. Remove citation if unavailable

**Rationale:** Unverified citations weaken credibility

**Priority:** HIGH (citation accuracy)

---

### Issue 5.2: Partially Verified Citation (Xu et al. 2026)

**Location:** References, line 570

**Current State:**
```
@article{XuEtAl2026BeSpec,
  ...
  note = {arXiv:2607.02949 - PARTIALLY VERIFIED (rate limit during detailed retrieval)},
  url = {https://arxiv.org/abs/2607.02949}
}
```

**Issue:** Citation verification incomplete due to rate limiting

**Resolution:** Complete verification before publication (check arXiv directly)

**Rationale:** Partial verification suggests reference exists but details unconfirmed

**Priority:** HIGH (citation accuracy)

---

## 6. Content Suggestions (Optional Enhancements)

### Issue 6.1: Section Numbering Inconsistency

**Location:** Throughout paper

**Current State:**
- "# 1. Introduction" (numbered section)
- "## Execution Feedback Reinforcement Learning" (unnumbered subsection)

**Suggested Change:** Standardize to:
- "# 1. Introduction" → "## 1.1 Subsection"
- OR keep unnumbered subsections (common in ML papers)

**Rationale:** Mixed numbering (numbered sections, unnumbered subsections) is inconsistent

**Priority:** LOW (formatting preference, venue-dependent)

---

## 7. Limitation Disclosure (Strengths to Preserve)

**NOTE:** The following are NOT issues but strengths identified during review that should be PRESERVED:

### Strength 7.1: Discussion Section 6.2 Limitation Disclosure

**Location:** Lines 399-414 (Discussion)

**Exemplary Text:**
```
"Limitation 1: Performance Untested. All experiments used pretrained CodeGen-350M without reinforcement learning training..."
"Limitation 2: Heuristic Human Feedback..."
"Limitation 3: No Static Comparison..."
```

**Why Preserve:** 
- Transparent acknowledgment of PoC scope
- Clear distinction between "mechanism validated" vs "performance validated"
- Honest framing prevents overclaiming
- Sets appropriate reader expectations

**Impact:** This section is the TONE MODEL for the entire paper—maintain this calibration throughout

---

### Strength 7.2: Mechanism-First Validation Philosophy

**Location:** Lines 149-153 (Methods), Lines 421-422 (Discussion)

**Exemplary Text:**
```
"Our methodology reflects a 'mechanism-first' design philosophy. Rather than optimizing for maximum performance on benchmarks, we prioritize demonstrating that the proposed mechanism—curriculum over feedback modality—can be implemented and produces predicted behavioral patterns."
```

**Why Preserve:**
- Clear methodological stance
- Justifies PoC limitations as intentional design choice
- Distinguishes mechanism validation from performance benchmarking
- Provides conceptual framework for contribution

---

## Summary for Human Reviewers

### High Priority (Address Before Publication)
1. **Citation verification** (Issues 5.1, 5.2): Verify Li et al. 2025 and Xu et al. 2026 references
2. **Figure inclusion** (Issue 4.1): Add figures or remove references

### Medium Priority (Consider for Polishing)
1. **Abstract formatting** (Issue 2.2): Split into 2 paragraphs for readability
2. **Table footnotes** (Issue 4.2): Add footnote to Table 1 explaining identical values

### Low Priority (Optional Refinements)
1. Grammar choices (Issues 1.1, 1.2): Acceptable as-is, minor flow improvements possible
2. Terminology consistency (Issues 3.1, 3.2): Current usage acceptable, standardization would tighten
3. Style preferences (Issues 2.1, 4.3, 6.1): Subjective, venue-dependent

### Preserve (Do Not Change)
1. Discussion Section 6.2 limitation disclosure (Strength 7.1)
2. Mechanism-first validation philosophy (Strength 7.2)
3. Honest PoC framing throughout paper

---

## Reviewer Notes

**Overall Assessment:** The paper's honest limitation disclosure and mechanism-first framing are STRENGTHS that should be preserved. Minor issues (grammar, citations, formatting) are standard polishing tasks. The R1 revision successfully addressed all MAJOR issues while maintaining transparency about PoC scope.

**Recommendation:** Address high-priority citation issues, consider medium-priority formatting improvements, and preserve the exemplary limitation disclosure tone. Low-priority items are optional refinements based on venue requirements and author preference.
