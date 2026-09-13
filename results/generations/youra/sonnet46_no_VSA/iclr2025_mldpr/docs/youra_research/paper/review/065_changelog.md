# Adversarial Review Changelog

**Paper**: Community Breadth Diversity Does Not Predict Benchmark Displacement  
**Review Process**: Phase 6.5 Adversarial Review  
**Started**: 2026-08-03  
**Completed**: 2026-08-03  
**Rounds**: 2

---

## Round 1 Changes (06_paper.md → 06_paper_r1.md)

### R1-CHANGE-001: Section 1 Introduction — Prior predictor framing [MAJOR-001]

**Location**: Paragraph 3 (prior signal sentence) + contribution bullet 2 + bullet 3  
**Issue**: Implied current null supersedes prior score-velocity signal  
**Change**:

*Before*: "A prior directional signal (HR = 0.871 for score velocity) appeared only with 22 displacement events..."

*After*: Added explicit parenthetical "(HR = 0.871 for *score velocity*, a different construct)" and added sentence: "The current paper tests *submission-count diversity* at adequate power; the two results are complementary, not contradictory (see Section 5.4)."

Contribution bullet 2 changed from "First well-powered test (EPV≈86) of community breadth as displacement predictor" to "... of community breadth *as operationalized by paper submission count*"

Contribution bullet 3 added: "Score velocity and institutional diversity remain untested at full power."

---

### R1-CHANGE-002: Section 4.2 — PH assumption language [MAJOR-002]

**Location**: Last paragraph of Section 4.2  
**Issue**: "no gross violation detected" implied automated check completed  
**Change**:

*Before*: "Schoenfeld residuals generated visually — no gross violation detected. Impact: LOW, given HR = 1.006."

*After*: "Visual inspection of Schoenfeld residuals (`figures/schoenfeld_residuals.png`) showed no obvious violation of the PH assumption; quantitative confirmation via automated test was not completed. Given HR = 1.006, moderate PH misspecification would not change the null conclusion."

Added fix instructions: "(fix: integer-encode `task_path` before calling `check_assumptions()`)"

---

### R1-CHANGE-003: Section 5.4 — Section heading and Table 3 [MAJOR-001]

**Location**: Section 5.4 heading, Table 3 title, surrounding text  
**Issue**: "Contrast with Prior Directional Signal" implied direct comparison of same predictor  
**Change**:

*Before heading*: "5.4 Contrast with Prior Directional Signal"  
*After heading*: "5.4 Relationship to Prior Directional Signal"

*Before Table 3 title*: "Prior Attempt vs Current Result"  
*After Table 3 title*: "Comparison of Two Distinct Predictor Tests"

Added column clarification: "(score velocity)" and "(submission count)" to predictor names.

Added critical clarification paragraph: "These two runs test *different constructs*. The prior result (HR = 0.871) is for *score velocity* (how fast SOTA scores improved); the current result is for *submission-count diversity*... The current null does not supersede or invalidate the prior directional signal for score velocity — that predictor has not been tested at adequate power."

---

### R1-CHANGE-004: Section 6.4 — Limitation L3 language [MAJOR-002]

**Location**: Section 6.4, L3 entry  
**Issue**: "Visual Schoenfeld residuals show no gross violation" implied detection  
**Change**:

*Before*: "Visual Schoenfeld residuals show no gross violation; HR = 1.006 is robust to moderate PH misspecification."

*After*: "Visual inspection of Schoenfeld residuals showed no obvious violation; quantitative testing was not completed due to a string-encoding error in `task_path` (requires integer-encoding before `check_assumptions()`). Given HR = 1.006, the conclusion is robust to moderate PH misspecification."

---

### R1-CHANGE-005: Section 6.4 — New limitation L5 added [MAJOR-003]

**Location**: Section 6.4, after L4  
**Issue**: Penalizer sensitivity not acknowledged  
**Change**: Added new limitation entry:

"**L5 (Penalizer sensitivity):** The L2 penalty (penalizer = 0.1) was selected for convergence, not optimized for effect estimation. In small samples (258 rows), L2 regularization can shrink coefficients toward zero. The null result HR = 1.006 should be interpreted as 'not distinguishable from null under L2 regularization with penalizer = 0.1.' Sensitivity analysis with penalizer = 0.0 (unpenalized) and penalizer = 0.5 would confirm that the null is not a regularization artifact; these runs were not performed in the current pipeline."

---

### R1-CHANGE-006: Appendix A1 — PH assumption note [MAJOR-002]

**Location**: Appendix A, Figure A1 description  
**Issue**: "No gross violation detected via visual inspection" used passive detection language  
**Change**:

*Before*: "No gross violation detected via visual inspection. Automated quantitative test incomplete..."

*After*: "Visual inspection showed no obvious violation. Automated quantitative test was not completed due to a string-type covariate encoding error (`task_path`); fixing requires integer-encoding `task_path` before calling `check_assumptions()`."

---

## Round 2 Changes (06_paper_r1.md → 06_paper_r2.md)

### R2-CHANGE-001: Section 5.2 Table 2 — |HR−1| precision [MAJOR-004]

**Location**: Section 5.2, Table 2, row "|HR−1|"  
**Issue**: Paper displayed `|HR−1| = 0.006` (rounded) but claimed "17× below threshold." With 0.006: 0.10/0.006 = 16.7× (not 17). Precise value from `experiment_results.json: abs_effect = 0.005613` gives 0.10/0.0056 = 17.9× (~18×).

**Change**:

*Before*: `| \|HR−1\| | 0.006 | ≥ 0.10 | ❌ FAIL (17× below) |`  
*After*: `| \|HR−1\| | 0.0056 | ≥ 0.10 | ❌ FAIL (~18× below) |`

**Evidence**: `experiment_results.json: "abs_effect": 0.005612985078401689`

---

## Final Summary

**Total Revisions Made**: 7 (6 in R1, 1 in R2)  
**Sections Modified**: Introduction, Section 4.2, Section 5.4, Section 6.4 (L3 + L5), Appendix A1, Table 2  
**Word Count Change**: +~180 words (primarily new L5 limitation and Section 5.4 clarification)  
**Numbers Changed**: 1 (|HR−1| precision: 0.006 → 0.0056)

**Review Process**:
- Started: 2026-08-03
- Completed: 2026-08-03
- Rounds: 2 (R1: structural + engagement; R2: numerical verification)
- Personas Used: Accuracy Checker, Bored Reviewer, Skeptical Expert

**Convergence**:
- After R1: FATAL=0, MAJOR=3 found, 3 resolved. Proceed to R2 (min_rounds=2).
- After R2: FATAL=0, MAJOR=1 found, 1 resolved. CONVERGED.

**Files Generated**:
- `06_paper_r1.md` (R1 revision)
- `06_paper_r2.md` (R2 revision)
- `06_paper_final.md` (final — copy of R2)
- `paper/review/065_review_r1.md` (three-persona review)
- `paper/review/065_review_r2.md` (numerical verification review)
- `paper/review/065_review_summary.md` (consolidated summary)
- `paper/review/065_human_review_notes.md` (MINOR issues for human review)
- `paper/review/065_changelog.md` (this file)

**Next Phase**: Phase 6.5.1 (Overleaf LaTeX/PDF generation)
