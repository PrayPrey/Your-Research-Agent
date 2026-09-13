# Phase 6.5: Human Review Notes (MINOR Issues)

**Generated**: 2026-08-25T01:11:45Z  
**Status**: DEFERRED TO HUMAN  
**Action Required**: Optional polish (does not block publication)

---

## MINOR Issues — Style & Completeness

These issues were flagged during adversarial review but are non-blocking. Fix at your discretion during final copyedit.

### m1: Inconsistent Gradient Asymmetry Rounding
**Location**: Abstract, Introduction, Results (9 occurrences)  
**Issue**: Gradient asymmetry reported as "26%" in some sections, "26.23%" in others  
**Technically**: Both correct (26.23% rounds to 26%)  
**Recommendation**: Standardize to one format throughout:
- Option A: "26%" everywhere (cleaner, abstract-friendly)
- Option B: "26.23%" everywhere (precise, data-driven)

**Current occurrences**:
- "26%": Abstract (revised), Introduction line 12
- "26.23%": Introduction line 18, Results lines 29, 35, 41

---

### m2: Jargon Before Definition
**Location**: Abstract sentence 1 (original, now revised)  
**Issue**: "spurious correlations" used without inline definition  
**Impact**: Non-fairness reviewers may pause to Google  
**Recommendation**: Original abstract defined it indirectly ("shortcuts... systematically failing on minority groups"). Current revised abstract is more technical — consider adding parenthetical:  
> "Batch Normalization amplifies worst-group accuracy gaps... on spurious correlation tasks (statistical shortcuts that fail under distribution shift)"

---

### m3: Introduction First Sentence Slightly Overwrought
**Location**: Introduction line 1  
**Issue**: "not due to insufficient data, but because of an architectural choice made decades ago" reads dramatic  
**Impact**: Minor tone issue (doesn't affect substance)  
**Recommendation**: Simplify to:  
> "A model achieving 97% average accuracy can fail on 28% of minority groups due to an architectural design choice."

---

### m4: Organization Paragraph Adds Zero Information
**Location**: Introduction end (after contributions list)  
**Issue**: "Organization. Section 2 discusses related work..." (60 words of boilerplate)  
**Impact**: Wastes space, readers can see section headings  
**Recommendation**: Cut entirely (standard practice in ML conferences)

**Current text**:
> **Organization.** Section 2 discusses related work on spurious correlation detection, temporal learning dynamics, and Batch Normalization's role in optimization. Section 3 presents our methodology, including the accuracy-matched comparison design and gradient instrumentation approach. Section 4 describes our experimental setup and success criteria. Section 5 presents results validating the existence and mechanistic hypotheses. Section 6 discusses interpretation, limitations, and broader impact. Section 7 concludes with future directions.

---

### m5: Related Work Citation Gap
**Location**: Related Work Section 2  
**Issue**: Cites Shen2021 (BN harms fairness) but doesn't cite broader BatchNorm alternatives surveys  
**Impact**: Completeness (not critical, but strengthens positioning)  
**Recommendation**: Add 1-2 citations:
- Brock et al. 2021 "High-Performance Large-Scale Image Recognition Without Normalization" (NormFree Nets)
- Ioffe 2017 "Batch Renormalization" (BN variant)
- OR Wu & He 2018 "Group Normalization" (intermediate between BN and LN)

**Insertion point**: Related Work Section 2, after Santurkar2019 paragraph or in new "Normalization Variants" subsection

---

## Summary

- **Total MINOR issues**: 5
- **Estimated fix time**: 15-30 minutes
- **Impact on publication**: None (all non-blocking)
- **Recommendation**: Address during final copyedit before submission, not critical for Phase 6.5 completion

---

**Human reviewer**: Review these notes before final submission. All MAJOR issues (M1-M6) have been fixed in-place in 06_paper.md sections.
