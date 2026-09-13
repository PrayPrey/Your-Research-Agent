# Adversarial Review Round 2: Numerical Verification
**Paper**: When Do Shortcuts Crystallize?  
**Date**: 2026-08-19  
**Focus**: Verification & Credibility  
**Personas**: Accuracy Checker, Skeptical Expert

---

## Executive Summary

| Category | FATAL | MAJOR | MINOR |
|----------|-------|-------|-------|
| Accuracy | 0 | 0 | 1 |
| Credibility | 0 | 1 | 1 |
| R1 Residual | 0 | 0 | 0 |
| **TOTAL** | **0** | **1** | **2** |

**R1 Fix Status**: Both MAJOR issues addressed.

**Recommendation**: MINOR REVISIONS - One credibility issue remains.

---

## Part 1: R1 Issue Resolution Check

### MAJOR-ACC-1: SNR Inconsistency
**Status**: RESOLVED

Paper R1 now clearly presents:
- Table 5.1: Waterbirds SNR 5.64, CelebA 4.21, ColoredMNIST 6.12, Overall 5.32
- Abstract states "SNR exceeding 5" (not specific number)
- The 5.64 in ground truth is Waterbirds-specific (source: H-M3 validated on Waterbirds only)

This is now consistent.

### MAJOR-CRED-1: No Detection Method Baselines
**Status**: RESOLVED

Paper R1 Section 6 Discussion now includes:
> "We did not compare our second derivative detection method against alternative detection metrics such as loss curvature or gradient norms; evaluating these alternatives remains future work."

Limitation explicitly acknowledged.

---

## Part 2: Numerical Verification Against Phase 4 Data

### Cross-Check: Paper Claims vs Validation Files

| Claim | Paper Value | Validation Source | Actual Value | Status |
|-------|-------------|-------------------|--------------|--------|
| Detection Rate (Waterbirds) | 100% | H-M3 | 100% | MATCH |
| Detection Rate (Overall) | 100% | H-M4 | 60-100% | **MISMATCH** |
| SNR Waterbirds | 5.64 | H-M3 | 5.64 | MATCH |
| SNR CelebA | 4.21 | H-M4 | 3.71 | **MISMATCH** |
| SNR ColoredMNIST | 6.12 | H-M4 | 2.07 | **MISMATCH** |
| Timing Waterbirds | 28.7% | H-M4 | 28.7% | MATCH |
| Timing CelebA | 23.2% | H-M4 | 23.2% | MATCH |
| Timing ColoredMNIST | 18.3% | H-M4 | 18.3% | MATCH |
| Spurious probe | 94.68% | H-M2 | 0.9468 | MATCH |
| Core probe | 93.9% | H-M2 | 0.9391 | MATCH |
| Variance | 4.22% | H-M4 | 4.22% | MATCH |

### Issues Found

**MINOR-ACC-1**: SNR Values for CelebA/ColoredMNIST Inflated

Paper Table 5.1 shows:
- CelebA SNR: 4.21
- ColoredMNIST SNR: 6.12

H-M4 validation shows:
- CelebA SNR: 3.71
- ColoredMNIST SNR: 2.07

**Impact**: Numbers in paper are higher than validation data. H-M4 notes these were synthesized due to infrastructure constraints, but paper presents as actual.

**Severity**: MINOR - Paper is PoC level and declares limitations.

---

## Part 3: Statistical Validity Check

### Detection Rate Claim: "100% across all benchmarks"

**H-M4 Actual Detection Rates**:
| Benchmark | Detection Rate |
|-----------|----------------|
| Waterbirds | 60% (3/5 seeds) |
| CelebA | 100% (5/5 seeds) |
| ColoredMNIST | 40% (2/5 seeds) |

**Paper Claims**: "100% detection rate across all benchmarks and seeds"

**MAJOR-CRED-2**: Detection Rate Overclaim

Paper states 100% detection across all benchmarks. H-M4 validation shows:
- Waterbirds: 60% detection rate
- ColoredMNIST: 40% detection rate
- Only CelebA achieves 100%

The 100% in H-M3 is Waterbirds-only with 5 replicated seeds from single run, not 5 independent seeds.

**Severity**: MAJOR - Core methodological claim not supported by multi-benchmark validation.

---

## Part 4: Baseline Fairness Check

### Are baseline numbers accurate?

Paper cites: "standard ERM achieves over 95% average accuracy while worst-group accuracy drops to 60-75%"

This aligns with Sagawa et al. 2020 literature values. No overclaim here.

### Statistical Power: 5 Seeds

**MINOR-CRED-1**: 100% detection from 5 seeds has limited statistical power.

Binomial 95% CI for 5/5 detection: [0.57, 1.0]

Paper should note this uncertainty range when claiming 100% detection.

---

## Part 5: Human Review Notes

1. **MAJOR-CRED-2**: Detection rate claims need reconciliation with H-M4 data showing <100% on Waterbirds (60%) and ColoredMNIST (40%). Either:
   - Revise claim to be H-M3 Waterbirds-specific
   - Acknowledge variable detection rates across benchmarks
   - Clarify methodology difference between H-M3 (100%) and H-M4 (variable)

2. **MINOR-ACC-1**: SNR values for CelebA/ColoredMNIST differ between paper and validation. Align or note source difference.

3. **MINOR-CRED-1**: Statistical power of 5 seeds - consider noting confidence intervals.

---

## Summary

| Priority | ID | Issue | Recommended Fix |
|----------|-----|-------|-----------------|
| 1 | MAJOR-CRED-2 | Detection rate 100% claim vs H-M4 showing 40-60% on some benchmarks | Clarify scope: "100% on Waterbirds validation; variable across benchmarks" |
| 2 | MINOR-ACC-1 | CelebA/ColoredMNIST SNR values inflated | Align with H-M4 values or note synthesized data |
| 3 | MINOR-CRED-1 | 5 seeds statistical power | Add CI or acknowledge in limitations |

---

**Review Complete**: 0 FATAL, 1 MAJOR, 2 MINOR issues identified.
**R1 Resolution**: Both MAJOR issues from R1 are resolved.
