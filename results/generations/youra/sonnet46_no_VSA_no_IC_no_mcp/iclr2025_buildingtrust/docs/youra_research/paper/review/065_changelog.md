# Revision Log

---

## Final Summary

**Total Revisions Made:** 6 (5 in R1, 1 in R2)
**Sections Modified:** Abstract, Introduction §Contributions, Results §5.4, Discussion §Limitations, Methodology §3.2
**Net Word Count Change:** +122 words (R1: +110, R2: +12)

**Review Process:**
- Started: 2026-08-25
- Completed: 2026-08-25
- Rounds: 2
- Personas Used: Accuracy Checker, Bored Reviewer, Skeptical Expert

**Files Generated:**
- `paper/06_paper_final.md` (final paper)
- `paper/review/065_review_summary.md` (review summary)
- `paper/review/065_human_review_notes.md` (MINOR issues for human review)
- `paper/review/065_changelog.md` (this file)
- `paper/review/065_review_r1.md` (R1 adversary report)
- `paper/review/065_review_r2.md` (R2 adversary report)
- `paper/06_paper_r1.md` (R1 revised paper)
- `paper/06_paper_r2.md` (R2 revised paper)

**Next Phase:** Phase 6.5.1 (Overleaf LaTeX/PDF generation)

---

## Round 2 Revision

**Date:** 2026-08-25
**Input Paper:** paper/06_paper_r1.md
**Review File:** paper/review/065_review_r2.md
**Output Paper:** paper/06_paper_r2.md

---

### Issues Addressed

#### MAJOR Issues

| ID | Title | Decision | Action Taken |
|----|-------|----------|--------------|
| MAJOR-ACC-002 | SST-2 exclusion rationale factually wrong | ACCEPT | Changed "insufficient for ECE measurement" to accurate description: excluded for scope (redundancy with QQP), noting n=148 was computed and available |

### Sections Modified

- **Section 3.2 Cell Structure:** SST-2 exclusion parenthetical corrected

### Word Count Change: +12 words (parenthetical expanded to accurate description)

---

---

## Round 1 Revision

**Date:** 2026-08-25
**Input Paper:** paper/06_paper.md
**Review File:** paper/review/065_review_r1.md
**Output Paper:** paper/06_paper_r1.md

---

### Issues Addressed

#### MAJOR Issues

| ID | Title | Decision | Action Taken |
|----|-------|----------|--------------|
| MAJOR-ENG-001 | Abstract buries counterintuitive hook | ACCEPT | Restructured abstract to open with the ANLI paradox finding (ΔECE = −0.041 vs +0.071) as the first sentence; finding stated concretely in opening 2 sentences |
| MAJOR-CRED-001 | Contribution 4 (JSONL caching) oversells engineering practice | ACCEPT | Removed JSONL caching as standalone Contribution 4; folded into Contribution 1 as implementation detail; reduced contributions from 4 to 3 |
| MAJOR-CRED-002 | Abstract/Intro overclaim scope ("establish", "predicting") | ACCEPT | Changed "establish" → "motivate" in abstract conclusion; "provides a conditional framework for predicting" → "motivates a conditional framework for understanding"; added "(in a single-model pilot study)" scope qualifier in abstract |
| MAJOR-CRED-003 | H-M2/H-M3 gate failures not disclosed | ACCEPT | Added new Limitation L5 explicitly disclosing: (a) conf_wrong = 0.616 < 0.70 pre-specified threshold; (b) only 1/5 cells exceeded ΔECE > 0.05 threshold; framed as "overspecified from vision-domain priors" |
| MAJOR-ACC-001 | ANLI R2 ΔΔECE framing misleading | ACCEPT | Clarified Finding 1 in Section 5.4: explicitly noted ΔECE(base)=+0.002 ≈ 0; stated that large ΔΔECE = +0.147 is primarily driven by chat model's improvement (ΔECE(chat) = −0.146), not base degradation |

### Issues NOT Addressed

*None — all 5 MAJOR issues addressed.*

---

### Sections Modified

- **Abstract:** Full restructure of opening sentences; added concrete numbers upfront; softened conclusion language; added pilot-study scope qualifier
- **Introduction §Contributions:** Reduced from 4 to 3 contributions; JSONL caching merged into Contribution 1; conclusion sentence softened
- **Results §5.4 Finding 1:** Clarified ANLI R2 ΔΔECE interpretation
- **Discussion §Limitations:** Added new limitation L5 disclosing pre-specified threshold failures

### Word Count Changes

| Section | Change |
|---------|--------|
| Abstract | +15 words (added concrete finding hook, scope qualifier) |
| Introduction Contributions | −35 words (removed Contribution 4, softened closing) |
| Results §5.4 | +40 words (clarification of ANLI R2) |
| Discussion Limitations | +90 words (new L5) |
| **Net** | **+110 words** |
