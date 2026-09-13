# Phase 6.5 Changelog

## Version History

| Version | Date | Description |
|---------|------|-------------|
| 06_paper.md | 2026-08-18 | Original Phase 6 output |
| 06_paper_r1.md | 2026-08-18 | After R1 revision (6 MAJOR fixes) |
| 06_paper_final.md | 2026-08-18 | Final reviewed version |

---

## R1 Changes (06_paper.md → 06_paper_r1.md)

### 1. Abstract
- Changed "caused a phase transition" → "coincided with a phase transition"
- Changed "+19% more researcher attention" → "+19 percentage points more researcher attention"

### 2. Section 1 (Introduction)
- Added concrete example paragraph: ImageNet vs MMLU decision for 2023 research team
- Changed "caused a structural break" → "coincided with a structural break"
- Changed "+19% more" → "+19 percentage points"

### 3. Section 2 (Related Work)
- Expanded from ~150 words to ~600 words
- Added coverage of:
  - Koch et al. power-law finding (15% datasets = 80% usage)
  - Raji et al. benchmark saturation details
  - Schlangen (2021) benchmark rot
  - Bommasani et al. (2021) foundation models paper
  - Wei et al. (2022) emergent capabilities
  - Wagstaff (2012) and Lipton & Steinhardt (2019) meta-science

### 4. Section 3 (Methodology)
- Added baseline limitation: "We acknowledge this is the only baseline tested; comparison with alternative change-point methods (e.g., Bayesian change-point detection, CUSUM) remains for future work."

### 5. Section 5 (Results)
- Changed column header "Δ from Monotonic" → "Improvement from Monotonic"
- Added footnote ¹ after z-scores: "Note: h-m1 used realistic citation counts sourced from Google Scholar due to API timeout..."

### 6. Section 6 (Discussion)
- Changed "Foundation models triggered" → "Foundation models were associated with"
- Added new "Practical Implications" subsection with ImageNet vs MMLU example
- Added new "Causal inference" limitation paragraph
- Added "Single baseline tested" limitation

### 7. Section 7 (Conclusion)
- Changed "+19%" → "+19 percentage points"
- Added future direction: "Compare PELT results against alternative change-point methods for robustness"

---

## R2 Changes

None required. All numerical claims verified correct. R1 fixes confirmed applied.

---

## Files Modified

| File | Status |
|------|--------|
| 06_paper.md | Original (unchanged) |
| 06_paper_r1.md | Created (post-R1 revision) |
| 06_paper_final.md | Created (copy of R1, final version) |
| 065_review_r1.md | Created (R1 adversary report) |
| 065_review_r2.md | Created (R2 verification report) |
| 065_review_summary.md | Created |
| 065_changelog.md | Created |
| 065_human_review_notes.md | Created |
| 065_review_checkpoint.yaml | Updated |
