# Revision Log - Round 1

**Date**: 2026-05-12T07:30:00Z
**Input Paper**: 06_paper.md
**Review File**: 065_review_r1.md
**Output Paper**: 06_paper_r1.md

---

## Issues Addressed

### MAJOR Issues

| ID | Title | Decision | Action Taken |
|----|-------|----------|--------------|
| BORE-MAJOR-001 | PoC Scale Not Foregrounded Until Too Late | ACCEPT | Added "proof-of-concept study on 8 test instances (3-SAT easy, 10-40 variables)" to Abstract first sentence. Updated Introduction contribution to "diagnostic evidence from a proof-of-concept evaluation". Updated Conclusion to frame as "proof-of-concept evaluation (8 instances, 3-SAT easy)" |
| SKEP-MAJOR-001 | Statistical Power Not Addressed | ACCEPT | Added explicit acknowledgment in Discussion limitations: "With n=8 instances, quartile estimates (Q3-Q1) used in our gate criteria have limited statistical power; robust distribution statistics require n≥100 for reliable quartile-based thresholds." |
| SKEP-MAJOR-002 | Generalization Claims Too Strong | ACCEPT | Softened generalization claims in Discussion and Conclusion. Changed "generalizes beyond SAT to any constraint satisfaction domain" to "may extend beyond SAT" with explicit caveat: "we note that these hypothesized generalizations remain untested. Our empirical evidence is specific to 3-SAT easy instances with baseline NeuroSAT; cross-domain validation (theorem proving, code synthesis, planning) is required to confirm transferability." |

### MINOR Issues (Collected for Human Review)

All MINOR issues from Round 1 review have been collected in `065_human_review_notes.md` for human review and are NOT auto-fixed per v2.0 protocol.

---

## Issues NOT Addressed (with justification)

None - all MAJOR issues were accepted and addressed.

---

## Sections Modified

- **Abstract**: Added PoC scale context (BORE-MAJOR-001)
- **Introduction (Contributions)**: Updated contribution #1 to frame as "diagnostic evidence" from PoC (BORE-MAJOR-001)
- **Discussion (Limitations)**: Added statistical power discussion for n=8 quartile estimates (SKEP-MAJOR-001)
- **Discussion (Broader Impact)**: Softened generalization claims, added cross-domain validation caveat (SKEP-MAJOR-002)
- **Conclusion**: Updated multiple locations to frame as PoC evaluation and soften generalization claims (BORE-MAJOR-001, SKEP-MAJOR-002)

---

## Word Count Changes

| Section | Before | After | Delta |
|---------|--------|-------|-------|
| Abstract | 171 | 187 | +16 |
| Introduction | 650 | 660 | +10 |
| Discussion | 1100 | 1180 | +80 |
| Conclusion | 620 | 640 | +20 |
| **Total** | ~6500 | ~6626 | +126 |

---

## Key Changes Summary

1. **Front-loaded PoC Scale**: Abstract now immediately discloses "proof-of-concept study on 8 test instances" to set appropriate expectations from the start.

2. **Statistical Power Acknowledgment**: Explicitly stated that quartile-based gate criteria with n=8 have limited statistical power and require n≥100 for robust validation.

3. **Generalization Claims Softened**: Changed definitive cross-domain claims to "may extend" with explicit caveat that cross-domain validation is untested future work.

---

## Revision Principles Applied

- **Honesty First**: Front-loaded limitations rather than hiding them in Discussion
- **Precision in Claims**: Changed "first quantitative evidence" to "diagnostic evidence from proof-of-concept"
- **Appropriate Hedging**: Used "may extend" and "suggests potential" for untested generalizations
- **Preservation**: Kept all core findings and technical content intact
- **Clarity**: Added explicit statistical power discussion to help readers interpret results appropriately
