# Human Review Notes - Round 1

**Date**: 2026-04-22T12:00:00Z
**Source**: Adversarial Review R1 - Part 4: Human Review Notes
**Status**: FOR HUMAN REVIEW (Not auto-fixed by Revision Agent)

---

## Instructions

These are MINOR issues identified by the Adversary that should be reviewed by a human during final polish. The Revision Agent does NOT auto-fix these to preserve author voice and avoid over-editing.

**Review these during final preparation before submission.**

---

## Style and Consistency Issues

### 1. Abstract - "orthogonal versus" vs "vs" consistency
**Location**: Abstract, line 12
**Issue Type**: Style consistency
**Note**: "orthogonal versus" could be "orthogonal vs." for consistency with later "vs" usage throughout paper
**Priority**: Low
**Suggested Action**: Choose one style ("versus" or "vs.") and apply consistently

---

### 2. Introduction - Repetitive sentence structure
**Location**: Introduction, paragraph 4 (lines starting "Prior work has not...")
**Issue Type**: Style / readability
**Note**: Three consecutive "No X" sentences - consider varying structure:
- "No study has isolated..."
- "No work has measured..."
- "No research has characterized..."
**Priority**: Low
**Suggested Action**: Consider rephrasing for variety, e.g., "Studies have not yet isolated..." or combine sentences

---

### 3. Introduction - Temperature notation inconsistency
**Location**: Introduction, paragraph 7; later sections use different format
**Issue Type**: Consistency
**Note**: "temperature T=0.7" in one place, but later sections use "temperature 0.7" without T=
**Priority**: Low
**Suggested Action**: Standardize to either "temperature 0.7" or "temperature T=0.7" throughout

---

### 4. Results Table 1 - Bold formatting on correlations
**Location**: Results, Section 5.2, Table 1
**Issue Type**: Formatting choice
**Note**: Bold formatting on 1.000 correlations (self-correlation and bug) draws eye but may be distracting
**Priority**: Low
**Suggested Action**: Consider whether bold is necessary or if plain text is cleaner

---

### 5. Results Section 5.2 - Absolute value clarification
**Location**: Results, Section 5.2, paragraph discussing correlation
**Issue Type**: Clarity
**Note**: "0.208 between semantic entropy and verbalized confidence" - consider adding "(absolute value)" since correlation can be negative
**Current Text**: "Maximum observed correlation is 0.208..."
**Priority**: Low
**Suggested Action**: Could clarify as "Maximum observed correlation (in absolute value) is 0.208..." or "Maximum observed |correlation| is 0.208..."

---

### 6. Results Section 5.3 - Spacing around equals signs
**Location**: Results, Section 5.3, statistical test reporting
**Issue Type**: Style consistency
**Note**: "t = -1.418, p = 0.158" - consider consistent spacing around equals signs throughout paper
**Priority**: Very Low
**Suggested Action**: Verify spacing is consistent in all statistical reporting (t-tests, p-values, etc.)

---

### 7. Discussion Section - Positive note on framing
**Location**: Discussion, L1 (Limitations)
**Issue Type**: Positive feedback (not an issue)
**Note**: "proof-of-concept" vs "production-ready" - excellent framing, no change needed
**Priority**: N/A
**Suggested Action**: None - this is good as-is

---

### 8. Conclusion - Long sentence readability
**Location**: Conclusion, paragraph 2
**Issue Type**: Readability
**Note**: Long sentence starting "Through controlled ablation..." could be split for easier reading
**Current**: "Through controlled ablation with matched computational budgets, we demonstrated that semantic clustering contributes measurably beyond multiple sampling (9-point AUROC improvement)."
**Priority**: Low
**Suggested Action**: Consider splitting into two sentences or breaking with semicolon

---

### 9. Overall - Figure reference completeness
**Location**: Throughout paper
**Issue Type**: Completeness check
**Note**: Check that all figure references (Figure 1-5) are actually included in paper package
**Referenced Figures**:
- Figure 1: AUROC comparison (Section 5.1)
- Figure 2: ROC curves (Section 5.1)
- Figure 3: Correlation heatmap (Section 5.2)
- Figure 4: Diversity distributions box plots (Section 5.3)
- Figure 5: Error signatures 2D plot (Section 5.3)
**Priority**: Medium
**Suggested Action**: Verify all 5 figures are included in submission package

---

## Summary Statistics

**Total Notes**: 9
**Style/Consistency**: 6
**Clarity**: 1
**Completeness**: 1
**Positive Feedback**: 1

**Priority Breakdown**:
- High: 0
- Medium: 1 (figure completeness check)
- Low: 6
- Very Low: 1
- N/A (positive): 1

---

## Recommendation

These are all minor polish items. The most important action item is:

1. **Verify all 5 figures are included** (medium priority)

The rest are low-priority style choices that can be addressed during final copy-editing. None of these issues affect the scientific validity or core contribution of the paper.

---

## Notes on v2.0 Protocol Compliance

Per Adversarial Review v2.0 protocol:
- MINOR issues are collected here, NOT auto-fixed
- This preserves author voice and prevents over-editing
- Human reviewer makes final judgment on style/consistency choices
- All FATAL and MAJOR issues were addressed in the revised paper (06_paper_r1.md)
