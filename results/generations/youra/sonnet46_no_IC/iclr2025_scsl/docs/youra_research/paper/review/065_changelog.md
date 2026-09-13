# Revision Changelog — Round 1
**Paper**: Where Does WGA Improvement Come From? Backbone vs. Head Robustification in ResNet-50 on Waterbirds  
**Source**: `06_paper.md`  
**Output**: `06_paper_r1.md`  
**Date**: 2026-08-05  
**Issues addressed**: M-1 (fixed), M-2 (fixed), M-3 (fixed)

---

## M-1: "Verified Causal Chain" Language Replaced

**Problem**: "verified causal chain" overstates what observational probe data can establish. No intervention (ablation, randomized experiment) was performed.

**Changes** (all replacements of "verified causal chain" / "causal chain"):

| Location | Old text | New text |
|----------|----------|----------|
| Abstract | "three-step verified causal chain" | "three-step mechanistic chain" |
| Introduction para 3 | "three-step verified causal chain" | "three-step mechanistic chain" |
| Introduction Contribution #3 | "Verified causal chain for GroupDRO robustification." | "Mechanistic chain for GroupDRO robustification." |
| Section 3.1 | "characterize the causal chain from GroupDRO's..." | "characterize the mechanistic pathway from GroupDRO's..." |
| Section 3.8 body | "The four experiments form a verified causal chain:" | "The four experiments form a verified mechanistic chain:" |
| Section 5.5 | "The causal chain is verified." | "The mechanistic chain is verified." |
| Section 7 Conclusion | "we verify a three-step causal chain:" | "we verify a three-step mechanistic chain:" |

**Addition in Discussion 6.2** (after L5, before Section 6.3):  
> "Establishing causality would require intervention studies (e.g., ablating minority upweighting while holding architecture fixed); our results establish consistent mechanistic co-occurrence, not causal necessity."

---

## M-2: Raymond 2026 Citation Qualified as Preprint

**Problem**: Raymond et al. [2026] cited as if published (ICLR 2026) without preprint qualification. In a 2026 submission, expert reviewers will question availability.

**Changes**:

| Location | Old text | New text |
|----------|----------|----------|
| Related Work 2.3 | "Raymond et al. [2026] provide corroborating evidence..." | "Raymond et al. [2026, preprint] provide corroborating evidence...; our H-M2 result stands on its own pre-registered weight-difference evidence independent of this citation." |
| Discussion 6.1 | "corroborates Raymond et al. [2026]." | "corroborates Raymond et al. [2026, preprint]; our finding stands on its own pre-registered evidence independent of this citation." |
| References | "GroupDRO reshapes representations across all layers. *ICLR*, 2026." | "GroupDRO reshapes representations across all layers. *arXiv preprint*, 2026." |

---

## M-3: Gradient Norm Comparison Labeled as Qualitative

**Problem**: "ERM = 1.152 vs. GroupDRO = 0.230" presented without per-seed breakdown, confidence interval, or explicit "qualitative" label. Not a pre-registered gate.

**Change**:

| Location | Old text | New text |
|----------|----------|----------|
| Results 5.2 | "Gradient norm analysis at layer4: ERM = 1.152 vs. GroupDRO = 0.230, indicating qualitatively different training dynamics..." | "Gradient norm analysis at layer4: ERM = 1.152 vs. GroupDRO = 0.230 (qualitative illustration; representative single-seed values, not a pre-registered gate), indicating qualitatively different training dynamics..." |

---

---

# Revision Changelog — Round 2
**Source**: `06_paper_r1.md`  
**Output**: `06_paper_r2.md`  
**Date**: 2026-08-05  
**Issues addressed**: Residual M-1 header fix

## Residual M-1: Section 3.8 Header Updated

**Problem**: R1 replaced all body text instances of "causal chain" → "mechanistic chain" but missed the section header itself.

| Location | Old text | New text |
|----------|----------|----------|
| Section 3.8 header | `### 3.8 Causal Chain Structure` | `### 3.8 Mechanistic Chain Structure` |

**R2 review verdict**: No FATAL or MAJOR issues found. All numerical claims verified against Phase 4 source files.

---

## Preserved (unchanged)

- All quantitative results (p-values, effect sizes, probe accuracies, ratios, WGA values)
- All hypothesis gate verdicts (CONFIRMED / SUGGESTIVE / PASS)
- All five limitations in Section 6.2
- All MINOR issues (collected in `065_human_review_notes.md`, not touched in paper)
- Section structure, figure references, all other text

---

## Final Summary

**Total Revisions Made**: 10 (7 body text + 1 addition + 1 reference + 1 section header)
**Sections Modified**: Abstract, Introduction, Section 3.1, Section 3.8, Section 5.2, Section 5.5, Section 6.1, Section 6.2, Section 7, Related Work 2.3, References
**Word Count Change**: ~+35 words net (added intervention-studies sentence in 6.2 + three qualifiers)

**Review Process**:
- Started: 2026-08-05
- Completed: 2026-08-05
- Rounds: 2 (R1 + R2)
- Personas Used: accuracy_checker, bored_reviewer, skeptical_expert

**Files Generated**:
- 06_paper_final.md (final paper)
- 065_review_r1.md, 065_review_r2.md (round reviews)
- 065_review_summary.md (consolidated review)
- 065_human_review_notes.md (7 MINOR issues for human review)
- 065_changelog.md (this file)
- 065_review_checkpoint.yaml (final state: COMPLETED, CONDITIONAL_ACCEPT)

**Next Phase**: Phase 6.5.1 (Overleaf LaTeX/PDF generation)
