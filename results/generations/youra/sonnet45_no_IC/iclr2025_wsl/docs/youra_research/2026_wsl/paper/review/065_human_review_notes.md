# Human Review Notes - Minor Issues

**Generated**: 2026-07-13 Round 1
**Purpose**: Non-critical improvements for human final polish
**Source**: 065_review_r1.md Part 4 (Minor issues flagged by Adversary Agent)

---

## Overview

This document collects MINOR issues from R1 adversarial review that do NOT require immediate automated fixing but should be addressed during final human polish before publication. These are style, clarity, formatting, and consistency improvements that would benefit from human judgment rather than automated revision.

**Status**: DEFERRED to human review
**Priority**: LOW (post-R2, pre-submission)

---

## Style and Clarity

| Location | Issue | Type | Suggested Fix |
|----------|-------|------|---------------|
| Abstract | "Architecture GNN residual" awkward phrasing | Style | Consider "GNN-based architectural topology encoding" or "Graph Neural Network topology residual" |
| Introduction line 15 | "Within-architecture methods work well:" informal | Clarity | Change to "Within-architecture methods achieve strong results:" for more formal tone |
| Discussion line 467 | "Plausibility: HIGH" informal tone for analysis section | Tone | Consider "Highly plausible:" or restructure as prose: "This explanation is highly plausible because..." |
| Conclusion line 530 | "At ρ = 0.67, they become tractable" connects poorly to prior sentence | Flow | Review sentence transition; may need bridge sentence or restructure |

---

## Formatting and Mathematical Notation

| Location | Issue | Type | Suggested Fix |
|----------|-------|------|---------------|
| Methodology line 134 | "Reshape to R^(C_out × C_r)" missing boldface R | Formatting | Should be "Reshape to ℝ^(C_out × C_r)" (real numbers, not R variable) |
| Throughout | Inconsistent math notation: some use ℝ, some use R | Consistency | Audit all math notation for consistent use of ℝ (real numbers) |

---

## Tables and Figures

| Location | Issue | Type | Suggested Fix |
|----------|-------|------|---------------|
| Results Table 1 (Section 5.3) | Consider adding "Significance" column | Enhancement | Add p-values for each ablation step to show statistical rigor at component level |
| All sections | Blueprint mentions 8 figures generated but only 3 referenced in text (fig_5, fig_7, fig_1) | Completeness | Audit figure references: Are fig_2, fig_3, fig_4, fig_6, fig_8 needed? Remove or add references as appropriate |

---

## Citations and References

| Location | Issue | Type | Suggested Fix |
|----------|-------|------|---------------|
| Throughout | Inconsistent citation format: some "Schürholt et al., 2024", some "Schürholt 2024" | Consistency | Standardize to venue guidelines (likely "Schürholt et al., 2024" with comma) |
| Related Work Section 2 | Check all citations follow consistent parenthetical vs narrative style | Consistency | Audit: "(Author, Year)" for parenthetical, "Author (Year)" for narrative |

---

## Figure Production Checklist (Phase 6)

**From Revision Agent Analysis:**

The paper references figures that do not yet exist or have numbering inconsistencies:

1. **Figure 1**: Text references "Figure 1 illustrates the full CAPE architecture" (Methodology 3.1 line 118)
   - **Status**: Not included in paper
   - **Blueprint**: Lists `fig_1_main_result` as gate comparison bar chart (contradiction?)
   - **Action Needed**: Clarify if Figure 1 should be architecture diagram or gate comparison; generate both and number consistently

2. **Figure 2**: Likely the gate comparison bar chart (Results 5.1 mentions "Figure 5")
   - **Status**: Reference exists but number unclear
   - **Action Needed**: Determine correct figure number (2 or 5?) and generate

3. **Figure 3-8**: Blueprint lists 8 figures total
   - **Status**: Only 3 figures referenced in text
   - **Action Needed**: Audit blueprint figure list, determine which are needed, generate missing figures, add references to text

**Recommendation**: During Phase 6 figure production, create comprehensive figure checklist matching blueprint to text references and resolve numbering conflicts.

---

## Prose Flow and Transitions

| Location | Issue | Type | Notes |
|----------|-------|------|-------|
| Introduction | Four-subsection structure condensed to two | Flow | Human should verify narrative still flows logically after condensing from "Surface Problem / Deeper Problem / Gap / Our Approach" to "The Problem / The Gap / Our Approach" |
| Results 5.6 H-E1 | Connection to main CAPE validation could be strengthened | Clarity | Currently states "H-E1 establishes signal existence, H-M-Integrated demonstrates utility" — consider expanding with concrete example |
| Discussion 6.2 | Three competing explanations format is clear but verbose | Style | Consider tabular format for competing explanations (Explanation / Plausibility / Evidence) to improve scannability |

---

## Terminology Consistency Audit

**Completed in R1 Revision:**
- "property prediction" → "mechanism validation" (where appropriate)
- "breaks the ceiling" → reduced to 3 strategic instances
- "paradigm shift" → "methodological shift"

**Remaining for Human Check:**
- Verify "mechanism validation" vs "property prediction" distinction is clear to readers throughout
- Ensure "PoC validation" consistently refers to synthetic labels + 100 models + 10 epochs
- Confirm "full-scale validation" consistently refers to Phase 5 (400 models + real labels + 100 epochs)

---

## Enhancement Opportunities (Low Priority)

These are NOT issues but opportunities to strengthen the paper if space/time permits:

1. **Add concrete example in Contributions section**: MAJOR-ENG-003 flagged contributions as too abstract. While technical terminology is appropriate, consider one concrete analogy in introduction (e.g., "like using specialized translators for different languages rather than one universal translator") to aid skimming readers.

2. **Expand Related Work comparison table**: Table 1 (Section 2) is excellent but could add row for "Statistical Validation" column showing CAPE has p < 0.05 while others lack significance tests.

3. **Discussion 6.2 competing explanations**: Consider adding "Test in Phase 5" row showing how full-scale validation will disambiguate (e.g., "If α remains > 0.35 with 4 architectures, Explanation 1 confirmed").

4. **Conclusion future work**: Currently lists 3 directions (Phase 5, P2, P3). Consider adding 4th direction: "Extend operation encoders to NLP (BERT/GPT) and speech domains" to highlight generalizability.

---

## Post-R2 Action Items

After R2 review completes and if paper receives ACCEPT or MINOR_REVISION:

1. ✅ Address all style/clarity issues from this document
2. ✅ Standardize citation format throughout
3. ✅ Fix mathematical notation (ℝ vs R)
4. ✅ Generate all figures per blueprint and audit references
5. ✅ Add Table 1 enhancement (significance column) if space permits
6. ✅ Review prose flow after Introduction condensing
7. ✅ Verify terminology consistency (mechanism validation vs property prediction)
8. ✅ Spell-check and grammar pass (automated tools)
9. ✅ Final read-through for flow and engagement

---

## Notes for Phase 6.5 (Adversarial Review Continuation)

If R2 review triggers additional rounds:

- **Watch for**: Reviewer pushback on "mechanism validation" framing (some may argue synthetic labels undermine contribution)
- **Defend by**: Pointing to diagnostic falsifiers (all pass), ablation study (components validated), statistical significance (p = 0.032)
- **Concede if**: Reviewer provides evidence that synthetic labels create misleading patterns not present in real labels

---

## Summary

**Total Minor Issues**: 8
- Style/Clarity: 4
- Formatting: 2
- Enhancement: 2

**Estimated Time to Address**: 2-3 hours (human polish)
**Recommended Timing**: After R2 ACCEPT, before final submission
**Risk Level**: LOW (none affect paper validity, only presentation quality)
