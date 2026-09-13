# Phase 6.5 Changelog

**Paper:** Static Analysis for LLM Code Repair: A Methodology Study  
**Review Date:** 2026-08-29

---

## Version History

| Version | File | Description |
|---------|------|-------------|
| Original | `06_paper.md` | Initial paper from Phase 6 |
| R1 | `06_paper_r1.md` | After Round 1 revisions |
| Final | `06_paper_final.md` | Final reviewed version |

---

## Changes Made

### Round 1 (R1)

#### MAJOR-001: Added 30% threshold justification

**File:** `06_paper.md` → `06_paper_r1.md`  
**Section:** 3.4 Existence Gate Protocol  
**Location:** Line ~137

**Before:**
```
**Rationale:** If most solutions have zero warnings, static analysis provides no signal—the intervention is null.
```

**After:**
```
**Rationale:** If most solutions have zero warnings, static analysis provides no signal—the intervention is null. We set the 30% threshold based on practical considerations: below this rate, fewer than 1 in 3 problems would receive static feedback, limiting the intervention's statistical power and practical utility. This threshold is conservative; lower rates (e.g., 20%) might still enable meaningful experiments but would require larger sample sizes to detect effects.
```

**Rationale:** Skeptical Expert identified that the 30% gate threshold was arbitrary without justification. Added explanation of practical reasoning behind the choice.

---

## Issues Not Changed (Human Review)

The following MINOR issues were identified but not auto-fixed:

1. **Blyth et al. citation:** Numbers (40%→13%, 80%→11%) from external paper not verified
2. **Methodology redundancy:** Sections 3.3-3.5 overlap with Section 4
3. **Pipeline validation claim:** "Validated" could be strengthened with test evidence

See `065_human_review_notes.md` for details.

---

## Summary Statistics

| Metric | Count |
|--------|-------|
| Total changes | 1 |
| FATAL fixes | 0 |
| MAJOR fixes | 1 |
| MINOR fixes | 0 |
| Lines changed | ~3 |

---

*Changelog generated: 2026-08-29*
