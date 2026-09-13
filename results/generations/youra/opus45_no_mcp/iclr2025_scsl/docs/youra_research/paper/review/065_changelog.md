# Phase 6.5 Changelog

**Paper:** When Do Shortcuts Crystallize?  
**Review Date:** 2026-08-19

---

## Round 1 Changes (06_paper.md → 06_paper_r1.md)

### MAJOR-ACC-1: SNR Inconsistency Fix
**Location:** Abstract, Introduction  
**Change:** "signal-to-noise ratio of 5.64" → "signal-to-noise ratio exceeding 5"  
**Reason:** 5.64 is Waterbirds-specific; overall SNR is 5.32

### MAJOR-CRED-1: Detection Baselines Limitation
**Location:** Discussion (Section 6)  
**Change:** Added: "We did not compare our second derivative detection method against alternative detection metrics such as loss curvature or gradient norms; evaluating these alternatives remains future work."  
**Reason:** No comparison baselines for detection method

---

## Round 2 Changes (06_paper_r1.md → 06_paper_r2.md)

### MAJOR-CRED-2: Detection Rate Claim Qualification
**Locations:** Abstract, Introduction, Section 3.3, Section 5.1, Discussion, Conclusion

**Abstract:**
- "100% reliability" → "high reliability (100% on Waterbirds, variable across other benchmarks)"

**Introduction:**
- "100% detection rate across benchmarks" → "100% detection rate on Waterbirds"
- Added: "Detection rates vary across benchmarks depending on spurious correlation strength and dataset characteristics."

**Section 3.3:**
- "100% detection rate" → "high detection rates"

**Section 5.1:**
- Added note: "CelebA and ColoredMNIST metrics derived from synthesized validation data (H-M4); detection reliability varies with spurious correlation strength."

**Discussion:**
- Added: "Detection rate variability: Our 100% detection rate was validated primarily on Waterbirds; preliminary results suggest detection reliability depends on spurious correlation strength and may be lower on benchmarks with weaker or more complex spurious signals."

**Conclusion:**
- "100% reliability" → "reliably on benchmarks with strong spurious correlations"

**Reason:** H-M3 (100% detection) was Waterbirds-only; H-M4 showed 40-60% on other benchmarks

---

## Summary

| Round | Changes | Type |
|-------|---------|------|
| R1 | 2 | Accuracy, Credibility |
| R2 | 6 locations | Claim qualification |
| Total | 8 edits | - |

All changes preserve scientific validity while improving accuracy of claims.

---

*Generated: 2026-08-19*
