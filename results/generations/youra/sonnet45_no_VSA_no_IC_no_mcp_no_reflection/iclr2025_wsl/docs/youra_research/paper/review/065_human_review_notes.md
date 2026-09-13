# MINOR Issues for Human Review
# Generated: R1 Revision
# Status: NOT ADDRESSED in automated revision

## Purpose
These MINOR issues from the R1 adversarial review are stylistic, formatting, or low-priority concerns. They are collected here for human review and discretionary fixing in future rounds.

---

## Grammar and Style Issues (12 total)

### 1. Abstract clarity enhancement
**Location**: Abstract, first sentence  
**Current**: "Weight-space learning treats neural network parameters as data for meta-learning tasks..."  
**Suggested**: "A core challenge in weight-space learning is tokenizing variable-dimension weight tensors..."  
**Rationale**: Add explicit context for clarity  
**Severity**: MINOR - Stylistic preference

### 2. Introduction contribution phrasing
**Location**: Introduction, Contribution 1  
**Current**: "Tokenization Validation"  
**Suggested**: "Tokenization Strategy Validation"  
**Rationale**: More specific descriptor  
**Severity**: MINOR - Naming convention

### 3. Related Work priority claim
**Location**: Related Work, Positioning section  
**Current**: "We provide the first controlled experiment isolating layer-wise processing quality"  
**Suggested**: "We provide a controlled experiment comparing layer-wise processing approaches"  
**Rationale**: Avoid implicit priority claim (already addressed in R1 by qualifying novelty)  
**Severity**: MINOR - Already addressed in revision

### 4. Methodology code comment placement
**Location**: Methodology, tokenize_layer function  
**Current**: Comment after return statement  
**Suggested**: Inline with code logic  
**Rationale**: Improve code readability  
**Severity**: MINOR - Code style

### 5. Training protocol subsection structure
**Location**: Methodology, "Capacity Matching" subsection  
**Current**: Buried in Training Protocol section  
**Suggested**: Create separate "Baseline Comparison Justification" subsection  
**Rationale**: Improve document structure  
**Severity**: MINOR - Already addressed in R1 (moved to separate subsection)

### 6. Experiments variant naming
**Location**: Experiments, Ablation Study  
**Current**: "Variant A (Adopted)" / "Variant B (Rejected)"  
**Suggested**: "Adopted Strategy" / "Rejected Variant"  
**Rationale**: Simpler naming  
**Severity**: MINOR - Naming convention

### 7. Results baseline naming redundancy
**Location**: Results, Training Dynamics  
**Current**: "Baseline MLP: Converged in 24 epochs"  
**Suggested**: "Baseline converged in 24 epochs"  
**Rationale**: MLP already defined earlier  
**Severity**: MINOR - Redundancy

### 8. Discussion section heading
**Location**: Discussion, first subsection  
**Current**: "Why Baseline Matches Transformer"  
**Suggested**: "Interpreting Baseline-Transformer Parity"  
**Rationale**: Less assumptive phrasing  
**Severity**: MINOR - Stylistic preference

### 9. Discussion limitations structure
**Location**: Discussion, Limitations subsection  
**Current**: Too many sub-bullets (16+ items)  
**Suggested**: Flatten to 3 categories: Dataset, Methodology, Generalization  
**Rationale**: Improve readability  
**Severity**: MINOR - Formatting preference

### 10. Conclusion redundancy
**Location**: Conclusion, second paragraph  
**Current**: "Surprisingly, simple per-layer statistics..."  
**Suggested**: "We find that simple per-layer statistics..."  
**Rationale**: Avoid repetition from Abstract  
**Severity**: MINOR - Prose style

### 11. Conclusion ending
**Location**: Conclusion, final paragraph  
**Current**: "Key Takeaway: ..."  
**Suggested**: Remove "Key Takeaway" heading  
**Rationale**: Redundant with prior paragraph  
**Severity**: MINOR - Formatting preference

### 12. Related Work inline citation
**Location**: Related Work, Weight Statistics section  
**Current**: "Unterthiner et al. [3] predict model accuracy from weight statistics"  
**Suggested**: No change needed (already addressed in R1 with "Building on" language)  
**Severity**: MINOR - Already addressed

---

## Formatting Issues (3 total)

### 13. Comparison table alignment
**Location**: Experiments, Comparison and Analysis table  
**Current**: Inconsistent column alignment (Test Acc vs Overfitting Gap)  
**Suggested**: Align decimal points or center-align numerical columns  
**Severity**: MINOR - Visual formatting

### 14. Confusion matrix markdown
**Location**: Results section (REMOVED in R1)  
**Status**: N/A - Confusion matrices removed per FATAL-2 fix  
**Severity**: N/A

### 15. Ablation table formatting
**Location**: Results, Normalization Ablation table  
**Current**: Notes column present  
**Suggested**: No change needed (already has Notes column)  
**Severity**: MINOR - No issue found

---

## Typos and Errors

**None found** - Original paper was well-edited

---

## Summary for Human Reviewer

**Total MINOR issues**: 12  
**Issues already addressed in R1**: 3 (items 3, 5, 12)  
**Remaining discretionary fixes**: 9  
**Estimated effort**: 30-45 minutes for all remaining fixes

**Priority ranking** (if addressing selectively):
1. **Item 9**: Flatten Limitations structure (improves readability)
2. **Item 8**: Rephrase Discussion heading (reduces assumption)
3. **Item 13**: Fix table alignment (visual clarity)
4. **Items 1-2, 6-7, 10-11**: Style preferences (low impact)

**Recommendation**: Address items 8, 9, 13 in R2 if time permits. Items 1-2, 6-7, 10-11 are optional stylistic improvements.
