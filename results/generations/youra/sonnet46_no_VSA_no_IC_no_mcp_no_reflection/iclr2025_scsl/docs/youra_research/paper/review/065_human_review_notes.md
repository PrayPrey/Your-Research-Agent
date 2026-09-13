# Human Review Notes

> **Purpose:** Minor issues collected during adversarial review for human review.
> These issues do NOT block paper acceptance. NONE were auto-fixed.

**Date:** 2026-08-31  
**Rounds Completed:** 2

---

## Summary by Category

| Category | Count |
|----------|-------|
| Style | 2 |
| Clarity | 3 |
| Formatting | 1 |
| Grammar | 0 |
| Typo | 0 |
| **Total** | **6** |

*(2 MINOR issues from R2 already addressed as formatting fix; remaining 6 below)*

---

## Round 1 Issues

### Style

**BR-MINOR-001**  
- **Location:** Section 6, heading "Root Cause: Batch Contamination"  
- **Issue:** Heading says "Root Cause" but paper subtitle says "Mechanistic Diagnosis." Consider changing to "Mechanistic Diagnosis: Batch Contamination" for consistency with paper framing.  
- **Suggestion:** `## Mechanistic Diagnosis: Batch Contamination`  
- **Priority:** Low — aesthetic only, does not affect meaning

### Clarity

**BR-MINOR-002**  
- **Location:** Section 5, Results — Alignment Inversion subsection  
- **Issue:** "The inversion partially recovers by epoch 50 (0.349)" — the word "partially" is ambiguous. 0.349 is about 70% of the way from 0.150 to 0.5, but is still well below chance. "Partially" may understate how far it remains from meaningful discriminability.  
- **Suggestion:** Consider "The signal moves toward chance by epoch 50 (0.349) but alignment never approaches discriminative territory."  
- **Priority:** Low — existing text is not wrong, only imprecise

**SE-MINOR-006**  
- **Location:** Section 6, Discussion — contamination formal analysis  
- **Issue:** The text says "With $k$ potentially large at epoch 1 (due to high minority loss)" without quantifying k. Readers may want a ballpark. Ground truth shows WB loss_roc_auc = 0.93 at epoch 1, suggesting minority samples have very high loss early in training (consistent with large k), but k is not directly measured.  
- **Suggestion:** Consider adding: "Empirically, loss ROC-AUC = 0.93 at epoch 1 indicates minority samples incur substantially higher loss than majority, consistent with large $k$, though $k$ is not directly measured here."  
- **Priority:** Medium — adds context without claiming unmeasured values

**ACC-MINOR-004**  
- *Already addressed in R1: CelebA subsample note updated to "~10% of full 162K dataset"* — Resolved.

### Formatting

**BR-MINOR-003**  
- *Already addressed in R1: Table 1 column headers updated to "WB Align", "WB Loss", etc.* — Resolved.

---

## Round 2 Issues

### Clarity

**R2-MINOR-001**  
- **Location:** Section 6, Discussion  
- **Issue:** "k potentially large at epoch 1 (due to high minority loss)" — could benefit from cross-reference to Table 1 loss values to give reader a concrete sense of magnitude  
- **Suggestion:** Add parenthetical: "(Table 1: WB loss ROC-AUC = 0.930 at epoch 1, consistent with high minority loss)"  
- **Priority:** Low — already somewhat addressed by presence of Table 1 in adjacent section

---

## Recommended Priority for Human Review

1. **Fix First (Medium priority):** SE-MINOR-006 — add informal k context with loss ROC-AUC cross-reference
2. **Consider (Low priority):** BR-MINOR-002 — "partially recovers" phrasing
3. **Optional (Aesthetic):** BR-MINOR-001 — heading alignment with subtitle

---

*Note: These issues do not block paper acceptance but improve overall quality and reviewer experience.*
