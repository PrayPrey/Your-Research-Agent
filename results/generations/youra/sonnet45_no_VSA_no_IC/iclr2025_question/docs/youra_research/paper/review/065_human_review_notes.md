# Human Review Notes - Round 1 Minor Issues

**Paper:** Cost-Performance Trade-offs in UQ for LLM Selective Prediction  
**Generated:** 2026-08-20  
**Status:** NOT FIXED by Revision Agent - requires human review

---

## Instructions

These are MINOR issues identified during adversarial review that were NOT automatically fixed by the Revision Agent. They require human judgment and manual editing during final polish.

---

## Minor Issues List

### 1. Abstract Citation Vagueness
**Location:** Abstract line 3 (original paper)  
**Issue:** "Current UQ research reports winner-take-all rankings without cost analysis" — vague claim without citation  
**Suggestion:** Add specific citation or hedge with "Prior work often reports..." to avoid overclaiming  
**Type:** Clarity

---

### 2. Informal Tone - "The gap is concrete"
**Location:** Introduction line 8 (original paper)  
**Issue:** "The gap is concrete:" — too informal for academic paper  
**Suggestion:** Replace with "Specifically:" or "More precisely:"  
**Type:** Style

---

### 3. Casual Section Header - "What it does:"
**Location:** Methodology line 69 (original paper)  
**Issue:** "What it does:" — section header too casual for academic writing  
**Suggestion:** Replace with "Definition:" or "Description:"  
**Type:** Style

---

### 4. Inconsistent Section Header - "Key Observations:"
**Location:** Results line 271 (original paper)  
**Issue:** "Key Observations:" — inconsistent with Discussion section headers  
**Suggestion:** Consider "Findings:" for consistency  
**Type:** Style

---

### 5. Uniform Standard Deviation Verification
**Location:** Table 1 (all methods)  
**Issue:** Std dev ±0.0082 identical for all methods — suspiciously uniform  
**Action Required:** Verify this is from PoC extrapolation methodology, not copy-paste error  
**Type:** Verification

---

### 6. Figure 1 Color Accessibility
**Location:** Figure 1 caption  
**Issue:** "Green points are Pareto-optimal" — references color before defining color legend (color-blind accessibility concern)  
**Suggestion:** Specify what green/red mean before referencing, or use pattern/shape in addition to color  
**Type:** Accessibility

---

### 7. Bold Formatting Inconsistency
**Location:** Discussion line 350 (original paper)  
**Issue:** "**Why acceptable:**" uses bold formatting inconsistent with rest of paper  
**Suggestion:** Remove bold or apply to all limitation subsection headers for consistency  
**Type:** Formatting

---

### 8. Circular Callback to Flawed Framing
**Location:** Conclusion line 388 (original paper)  
**Issue:** "We began with practitioners facing a budget-accuracy dilemma" — circular callback to "dilemma" framing that was corrected in R1 revision  
**Note:** This was FIXED in R1 revision (changed to "trade-off"), but flagged here as example of consistency check needed  
**Type:** Consistency

---

## Summary

**Total Minor Issues:** 8  
**Issues Requiring Action:** 7 (issue #8 already fixed in R1)  
**Priority Areas:**  
- Style consistency (4 issues)
- Verification (1 issue)  
- Accessibility (1 issue)  
- Clarity (1 issue)

---

## Next Steps for Human Review

1. **High Priority:** Verify Table 1 standard deviations (issue #5) — check if uniform ±0.0082 is methodologically sound
2. **Medium Priority:** Fix accessibility issue in Figure 1 caption (issue #6)
3. **Low Priority:** Polish informal language (issues #2, #3, #4) and formatting consistency (issue #7)
4. **Optional:** Add citation for Abstract claim (issue #1) if specific prior work can be identified

---

**Note:** These issues did not prevent R1 revision acceptance. They are polish items for final publication-ready version.
