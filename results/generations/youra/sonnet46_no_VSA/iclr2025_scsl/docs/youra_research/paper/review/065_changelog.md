# Adversarial Review Changelog

## Round 1 Revisions

**Date**: 2026-08-04
**Input**: 06_paper.md
**Output**: 06_paper_r1.md

### CRED-MAJOR-001 (Abstract overclaim "across five seeds") — PARTIAL FIX
- **Location**: Introduction paragraph 1 (hook sentence)
- **Change**: "AUROC 0.88 across five random seeds" → "AUROC 0.85–0.90 in 4/5 random seeds (mean AUROC 0.885 across passing seeds)"
- **Note**: Abstract already correctly states "4/5 random seeds achieve AUROC≥0.85" — abstract was correct; Introduction hook was the problem.

### CRED-MAJOR-002 (Gate threshold discrepancy) — FIXED
- **Location**: Section 3.6, final paragraph
- **Change**: "The H-E3 gate requires ≥4/5 seeds to pass all three criteria simultaneously" → "The H-E3 gate requires ≥3/5 seeds to pass all three criteria simultaneously (pre-registered threshold); our implementation achieved 4/5 seeds passing."
- **Rationale**: Phase 4 implementation config shows min_seeds_passing: 3. The pre-registered gate was 3/5; 4/5 passed.

### CRED-MAJOR-003 (Abstract confidence threshold) — FIXED
- **Location**: Abstract
- **Change**: "minority training confidence saturates to ≥0.97 at t*" → "minority training confidence saturates to ≥0.967 at t* (range: 0.9678–0.9999 across seeds)"
- **Rationale**: Seed 5 achieves p_minority=0.9678, which is below 0.97. Correct lower bound is 0.9678 ≈ 0.967.

### CRED-MAJOR-004 (No comparative baseline AUROC) — ADDRESSED
- **Location**: Section 5.1, after "Epoch-0 control" paragraph
- **Change**: Added "Comparison context" paragraph explicitly scoping the existence result and deferring direct baseline AUROC comparison to future work, with justification.
- **Rationale**: A comparative run of JTT/SELF as minority detectors requires a full separate experimental pipeline. The paper is an existence result; future work should compare directly.

---

## Sections Modified (R1)

| Section | Change |
|---------|--------|
| Introduction (paragraph 1) | Fixed "across five random seeds" → "in 4/5 random seeds" |
| Abstract | Fixed confidence lower bound ≥0.97 → ≥0.967 |
| Section 3.6 | Fixed gate threshold ≥4/5 → ≥3/5 (pre-registered) with achieved result |
| Section 5.1 | Added comparison context paragraph for baseline AUROC |

**Word count delta**: +82 words (added comparison context paragraph)

---

## Round 2 Revisions

**Date**: 2026-08-04
**Input**: 06_paper_r1.md
**Output**: 06_paper_r2.md

### CRED-MAJOR-002 — CONFIRMED FALSE POSITIVE, REVERTED

The R1 fix that changed "≥4/5" to "≥3/5" in Section 3.6 was incorrect. Code verification of `evaluate_trajectory.py:110` confirmed `n_passing >= 4` — the paper's ≥4/5 statement is correct. The 04_validation.md documentation listing `min_seeds_passing: 3` was a doc artifact.
- Section 3.6 reverted to original "≥4/5 seeds" wording.

### R1-Introduced Error: Mean AUROC 0.885 → 0.89 — FIXED

R1 changed Introduction hook to include "mean AUROC 0.885 across passing seeds."
Actual mean: (0.8855+0.8973+0.9026+0.8896)/4 = 0.8938 ≈ 0.89.
- Introduction hook corrected to "mean AUROC 0.89 across the 4 passing seeds."

## Sections Modified (R2)

| Section | Change |
|---------|--------|
| Introduction (paragraph 1) | Corrected mean AUROC from 0.885 to 0.89 |
| Section 3.6 | Reverted ≥3/5 back to ≥4/5 (paper was correct, R1 fix was wrong) |

**Word count delta R2**: 0 (corrections only, no net additions)

---

## Final Summary

**Total Revisions Made**: 5 (4 from R1, 1 correction in R2)
**Sections Modified**: Abstract, Introduction, Section 3.6, Section 5.1
**Word Count Change**: Original → Final (+82 words, net addition of comparison context)

**Review Process**:
- Started: 2026-08-04T07:00:00+00:00
- Completed: 2026-08-04T07:30:00+00:00
- Rounds: 2
- Personas Used: accuracy_checker, bored_reviewer, skeptical_expert

**Files Generated**:
- 06_paper_r1.md (R1 revised paper)
- 06_paper_r2.md (R2 revised paper = final)
- 06_paper_final.md (copy of R2)
- 065_review_r1.md
- 065_review_r2.md
- 065_review_summary.md
- 065_human_review_notes.md
- 065_changelog.md (this file)

**Next Phase**: Phase 6.5.1 (Overleaf LaTeX/PDF generation)
