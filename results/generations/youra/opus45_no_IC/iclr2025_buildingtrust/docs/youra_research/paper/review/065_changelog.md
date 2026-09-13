# Phase 6.5 Changelog

**Generated:** 2026-08-10
**Rounds:** R1, R2

## Round 1 Changes (06_paper.md → 06_paper_r1.md)

### Section 5.2 (h-m1 Results)
**Issue:** MAJOR-1 — h-m1 simulated data circularity not adequately disclosed
**Change:** Expanded methodological caveat paragraph:
- Added explicit acknowledgment of circularity
- Stated 17/21 result "demonstrates internal consistency of simulation rather than independent empirical finding"
- Noted h-m2 provides primary mechanistic evidence

### Section 5.3 (h-m2 Results)
**Issue:** MAJOR-2 — T=10 bound saturation interpretive uncertainty underemphasized
**Change:** Added "Interpretive note" paragraph:
- Explained two possibilities (true optimal T=10 vs. optimal beyond bound)
- Noted conclusion limited to tested range
- Suggested future work with extended bounds (T up to 50-100)

### Section 6 (Limitations)
**Change:** Strengthened limitation bullets:
- Added "potentially revealing cluster differentiation at higher temperatures"
- Expanded h-m1 simulation caveat with circularity explanation

## Round 2 Changes (06_paper_r1.md → 06_paper_r2.md)

### Section 3 (Methodology — Cluster Table)
**Issue:** MAJOR-1 — Cluster names/sample sizes mismatched h-e1/04_validation.md
**Change:** Corrected cluster names and sample sizes:

| Before | After |
|--------|-------|
| Science & Nature (142) | Science/Technology/Math (112) |
| Health & Medicine (127) | Health/Nutrition/Psychology (118) |
| Society & Culture (168) | History/Geography/Culture (123) |
| Finance & Economics (70) | Finance/Economics (98) |
| Misconceptions & Myths (134) | Misconceptions/Myths/Superstitions (137) |
| Politics & Law (98) | Law/Politics/Government (127) |
| Other (78) | Religion/Philosophy/Ethics (102) |

### Section 5.1 (Results — ECE Table)
**Issue:** MAJOR-2 — Per-cluster ECE values mismatched source
**Change:** Corrected ECE values to match h-e1/04_validation.md:

| Cluster | Before | After |
|---------|--------|-------|
| Science/Technology/Math | 0.178 | 0.169 |
| Health/Nutrition/Psychology | 0.186 | 0.184 |
| History/Geography/Culture | 0.201 | 0.193 |
| Law/Politics/Government | 0.195 | 0.216 |
| Religion/Philosophy/Ethics | 0.224 | 0.228 |

(Finance/Economics 0.152 and Misconceptions 0.251 unchanged)

## Summary

| Round | FATAL Fixed | MAJOR Fixed | Lines Changed |
|-------|-------------|-------------|---------------|
| R1 | 0 | 2 | ~15 |
| R2 | 0 | 2 | ~20 |
| **Total** | **0** | **4** | **~35** |

All changes preserve core findings. No numerical claims altered except corrections to match source validation files.
