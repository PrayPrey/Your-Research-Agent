# Phase 6.5 Changelog

**Paper:** Quantifying Benchmark Contamination: A Transfer Function Approach  
**Review Date:** 2026-08-10

---

## Summary of Changes

| Round | FATAL Fixed | MAJOR Fixed | MINOR Collected |
|-------|-------------|-------------|-----------------|
| R1 | 2 | 3 | 3 |
| R2 | 0 | 1 | 4 |
| **Total** | **2** | **4** | **7** |

---

## Round 1 Changes

### FATAL-001: Mock Data Disclosure
**Issue:** Results presented as empirical findings but came from synthetic data with hardcoded correlation formula.

**Changes:**
- Abstract: Added "In preliminary validation" prefix, "pending full-scale validation" suffix
- Contributions: Changed "first quantitative evidence" → "methodology for measuring...with preliminary validation results"
- Section 5: Added "(Preliminary)" label to main finding
- Discussion: Expanded "Simulated validation" limitation

### FATAL-002: Sample Size Inconsistency
**Issue:** n=80 in Results vs n=72 in Abstract

**Change:**
- Section 5, line 177: Changed "n = 80" → "n = 72"

### MAJOR-001: "First Evidence" Overclaims
**Issue:** Multiple claims of "first quantitative evidence" invalid without real data

**Changes:**
- Abstract: Removed "first quantitative evidence that contamination impact is measurable"
- Contributions item 2: Changed to "Preliminary correlation evidence"
- Related Work: Changed to "providing a methodology for contamination-inflation correlation measurement"
- Conclusion: Changed to "methodology provides a framework"

### MAJOR-002: Limitations Understated
**Issue:** "PoC validation" phrasing implied simplified-but-real; truth was entirely synthetic

**Change:**
- Discussion limitations: Expanded to explicitly state "simulated validation" with computational requirements

### MAJOR-003: Per-Benchmark Statistics Unvalidated
**Issue:** Per-benchmark correlations presented as established but were also from mock data

**Change:**
- Added "Statistical significance caveat" to limitations: "Only 2 of 4 benchmarks (MMLU, ARC-Challenge) show statistically significant correlation at p < 0.05"

---

## Round 2 Changes

### MAJOR-004: Mock Data Caveat Insufficient
**Issue:** Even after R1 fixes, the mock data nature wasn't explicit enough about the hardcoded correlation

**Change:**
- Discussion limitations: Changed "simulated contamination data" → "simulated contamination data where contamination-inflation correlation was structurally embedded in the data generation process"
- Added: "real Pythia checkpoint experiments are required to validate whether the observed relationship holds in practice"

---

## Files Modified

| File | Status |
|------|--------|
| 06_paper.md | Source paper (modified in place) |
| 06_paper_r1.md | After R1 revisions |
| 06_paper_r2.md | After R2 revisions |
| 06_paper_final.md | Final version (copy of r2) |

---

## Diff Summary

```
Abstract:
- "the first quantitative evidence that contamination impact is measurable"
+ "preliminary findings suggest that contamination-inflation correlation is measurable...pending full-scale validation"

Section 1 Contributions:
- "we present the first quantitative evidence"
+ "we present a methodology...with preliminary validation results"

Section 5:
- "Finding: A statistically significant positive correlation exists...n = 80"
+ "Finding (Preliminary): In simulated validation, we observe...n = 72"

Section 6 Limitations:
- "Results derive from PoC validation"
+ "Current results derive from proof-of-concept validation using simulated contamination data where contamination-inflation correlation was structurally embedded...real Pythia checkpoint experiments are required to validate"

Section 7:
- "provides the first quantitative answer"
+ "provides a framework for answering this question. Preliminary validation suggests...pending full experimental validation"
```

---

## Version History

| Version | Date | Description |
|---------|------|-------------|
| 06_paper.md | 2026-08-10 | Original from Phase 6 |
| 06_paper_r1.md | 2026-08-10 | Post-R1: Fixed FATAL issues, reframed claims |
| 06_paper_r2.md | 2026-08-10 | Post-R2: Strengthened mock data disclosure |
| 06_paper_final.md | 2026-08-10 | Final reviewed version |
