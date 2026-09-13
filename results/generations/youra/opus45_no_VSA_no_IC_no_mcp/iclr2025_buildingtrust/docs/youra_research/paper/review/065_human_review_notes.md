# Human Review Notes - Phase 6.5
# Minor issues NOT auto-fixed; collected for human review
# Generated: 2026-08-28

## Summary

| Category | Count |
|----------|-------|
| Typo | 0 |
| Grammar | 0 |
| Style | 2 |
| Clarity | 2 |
| Formatting | 0 |
| **Total** | **4** |

---

## Round 1 Issues

### 1. Figure Captions (Clarity)

**Location:** Results section (Figures 1-4)
**Issue:** Figure references in text but captions could be more self-contained for readers who skim figures first.
**Suggestion:** Consider expanding figure captions to include key takeaway (e.g., "Figure 1: TruthfulQA vs AdvGLUE scatter. Models cluster along positive diagonal, confirming r=0.80 correlation.")

---

### 2. Methodology ECE Section Density (Clarity)

**Location:** Section 3 (Methodology), around line 115
**Issue:** ECE formula presented without intuitive lead-in; may lose readers unfamiliar with calibration metrics.
**Suggestion:** Add one-sentence intuition before formula: "ECE measures the gap between a model's confidence and its actual accuracy across probability bins."

---

### 3. "Falsified" Tone (Style)

**Location:** Multiple sections (Abstract, Results, Discussion, Conclusion)
**Issue:** "Falsified" is philosophically strong language. Fisher z-test p=0.165 is not statistically significant; the evidence is directional but not conclusive.
**Suggestion:** Consider alternatives: "evidence against", "ruled out", "contradicted by our data". Reserve "falsified" for p<0.05 results.

---

### 4. RLHF Citation Relevance (Clarity)

**Location:** Related Work, Truthfulness Evaluation subsection
**Issue:** Ouyang et al. 2022 (RLHF) cited but connection to truthfulness not explained in the sentence.
**Suggestion:** Brief clarification: "...explored interventions such as RLHF to improve truthful behavior by training models to prefer accurate responses [Ouyang et al., 2022]."

---

## Round 2 Issues

(To be added after R2)

---

*These issues do not block publication but warrant human review before final submission.*
