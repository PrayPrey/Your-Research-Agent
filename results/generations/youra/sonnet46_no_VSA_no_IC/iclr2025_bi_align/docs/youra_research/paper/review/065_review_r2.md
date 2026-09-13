# Adversarial Review — Round 2

**Paper:** Directed Citation Asymmetry in the huashen218 Bidirectional Alignment Corpus: Pipeline Validation and Preliminary Measurement
**Reviewed:** 2026-08-21
**Reviewer:** Adversary Agent (Accuracy Checker + Skeptical Expert)
**Round:** R2 — Numerical Verification and Credibility
**Input:** 06_paper_r1.md (post-R1 revision)

---

## Executive Summary

| Category | FATAL | MAJOR | Status |
|----------|-------|-------|--------|
| Accuracy (numerical) | 0 | 0 | OK |
| Mathematical validity | 0 | 1 | NEEDS_WORK |
| Baseline fairness | 0 | 0 | OK |
| Signal-performance | 0 | 0 | OK |
| Metric consistency | 0 | 0 | OK |
| Missing limitations | 0 | 0 | OK |
| **TOTAL** | **0** | **1** | **MINOR_REVISION** |

**Recommendation:** CONDITIONAL_ACCEPT (one major issue identified; fixable with a sentence)

---

## Serena MCP Verification Log

*Note: Serena MCP was used to verify actual metric values via the pipeline validation data and ground truth file. Direct file content inspection performed for all numerical claims.*

| Search Type | Pattern | Path | Result |
|-------------|---------|------|--------|
| Test count | "23/23" | h-e1/04_validation.md | ✓ CONFIRMED |
| Resolution rate | "67.3%" | h-e1/04_validation.md | ✓ CONFIRMED (67.3% = 33/49) |
| Scheme 3 counts | "28 \| 5" | h-e1/04_validation.md | ✓ CONFIRMED (R1 fix applied) |
| Cross-group edges | "9" scheme3 | h-e1/04_validation.md | ✓ CONFIRMED |
| ML_NLP outgoing | "47" | 045_validated_hypothesis.md | ✓ CONFIRMED (42+5=47) |
| HCI outgoing | "4" | 045_validated_hypothesis.md | ✓ CONFIRMED (4+0=4) |
| Ratio calculation | "0.10638" | 065_ground_truth.yaml | ✓ CONFIRMED (5/47 / 4/4 = 0.10638) |
| Gate thresholds | "0.70 \| 30" | 065_ground_truth.yaml | ✓ CONFIRMED |

---

## Ground Truth Verification Table

| Claim | Paper (R1) | Ground Truth | Serena Verified | Match? |
|-------|------------|--------------|-----------------|--------|
| 23/23 tests pass | ✓ | 23/23 (0.85s) | ✓ | ✓ |
| S2AG resolution 67.3% | ✓ | 67.35% (33/49) | ✓ | ✓ |
| Scheme 1/2 coverage 12.1% | ✓ | 12.12% (4/33) | ✓ | ✓ |
| Scheme 3 ML_NLP=28 | ✓ (fixed in R1) | 28 | ✓ | ✓ |
| Scheme 3 HCI=5 | ✓ (fixed in R1) | 5 | ✓ | ✓ |
| ML_NLP→HCI=5 | ✓ | 5 | ✓ | ✓ |
| HCI→ML_NLP=4 | ✓ | 4 | ✓ | ✓ |
| ML_NLP outgoing total=47 | ✓ | 47 | ✓ | ✓ |
| HCI outgoing total=4 | ✓ | 4 | ✓ | ✓ |
| Ratio=0.107 | ✓ | 0.10638 | ✓ | ✓ |
| Cross-group edges max=9 | ✓ | 9 (Scheme 3) | ✓ | ✓ |
| 49 extracted IDs | ✓ | 49 | ✓ | ✓ |
| 16 unresolved (ACM DL) | ✓ | 16 | ✓ | ✓ |

**All numbers verified. No new numerical discrepancies found after R1 correction.**

---

## Mathematical Validity Analysis

### Check 1: Ratio Calculation Correctness

```
Paper claims: r = (5/47) / (4/4) = 0.107
Verify: 5/47 = 0.10638, 4/4 = 1.0, r = 0.10638/1.0 = 0.10638 ≈ 0.107
CORRECT. Rounding to 3 decimal places is appropriate.
```

### Check 2: ML_NLP Outgoing Total Consistency

```
Paper table: ML_NLP → ML_NLP=42, ML_NLP → HCI=5, outgoing total=47
Verify: 42+5=47 ✓
Consistent.
```

### Check 3: HCI Outgoing Total Consistency

```
Paper table: HCI → ML_NLP=4, HCI → HCI=0, outgoing total=4
Verify: 4+0=4 ✓
Consistent.
```

### Check 4: Coverage Calculation

```
Paper: 33/49 = 67.3%
Verify: 33/49 = 0.6735 → 67.35% → rounded to 67.3% ✓
CORRECT.
```

### Check 5: Scheme 1/2 Coverage

```
Paper: 4/33 = 12.1%
Verify: 4/33 = 0.12121 → 12.12% → rounded to 12.1% ✓
CORRECT.
```

### Check 6: ML_NLP→HCI Proportion

```
Paper: 5/47 = 10.6%
Verify: 5/47 = 0.10638 → 10.638% → reported as 10.6% ✓
CORRECT.
```

### Check 7: Cross-group Edge Gate Shortfall

```
Paper: "gate FAIL by 21 edges" (9 found vs 30 threshold)
Verify: 30-9=21 ✓
CORRECT.
```

### Check 8: Coverage Gate Shortfall

```
Paper: "gate FAIL by 2.7 pp" (67.3% vs 70%)
Verify: 70-67.3=2.7 ✓
CORRECT.
```

---

## Mathematical Validity Issues

### MAJOR Issues — Mathematical Validity

#### MAJOR-MATH-001: "89.4% within-group" calculation not shown — easy to verify but not explicit

**Location:** Section 5.3, Interpretation paragraph
**Issue:** Paper states "ML/NLP alignment papers allocate 89.4% of within-corpus outgoing citations to other ML/NLP papers." This is derived from 42/47 = 89.36% ≈ 89.4%. The calculation is correct, but the paper does not make the arithmetic explicit or cite the 42 (ML_NLP→ML_NLP) value from the directed edge matrix in this prose sentence. A reviewer seeing "89.4%" without the supporting arithmetic may wonder where it comes from; the directed edge matrix is one paragraph above but this specific number is not easy to trace without doing the division.
**Evidence:** 42/47 = 0.8936 ≈ 89.4% — CORRECT mathematically. But not explicitly stated in prose.
**Suggested Fix:** Change "ML/NLP alignment papers allocate 89.4% of within-corpus outgoing citations to other ML/NLP papers" to "ML/NLP alignment papers allocate 42 of 47 within-corpus outgoing citations (89.4%) to other ML/NLP papers" — making the arithmetic self-evident.

---

## Baseline Fairness Assessment

This is a pipeline/measurement paper with no comparative ML baselines. The "baselines" are the venue-string classification schemes (Scheme 1, Scheme 2) compared to FoS-primary (Scheme 3). These are:
- Fairly described — Scheme 1/2 limitations are accurately stated
- Not cherry-picked — all three pre-registered schemes are reported
- No numbers from prior literature that could be misrepresented

**Baseline fairness: PASS. No issues.**

---

## Signal-Performance Gap Analysis

The "signal" in this paper is the CV ratio or detection performance analogy — but this is a bibliometric paper, not an ML detection paper. The relevant signal is the ratio 0.107 vs null of 1.0.

- Is the ratio 0.107 "strong" enough to be meaningful? The paper correctly says: directionally consistent, not statistically confirmable at N=9. No overclaim.
- Is the gate failure honestly reported? Yes — both gates explicitly failed with exact shortfalls.
- Is INCONCLUSIVE properly distinguished from REFUTED? Yes — paper is explicit throughout.

**Signal-performance: PASS. No issues.**

---

## Missing Limitations Check

Reviewing the 5 limitations in Section 6.2 against ground truth:

| Limitation | Present? | Honest? |
|-----------|----------|---------|
| Statistical predictions INCONCLUSIVE | ✓ (Limitation 1) | ✓ |
| 33-paper proxy corpus | ✓ (Limitation 2) | ✓ |
| Scheme 1/2 sensitivity not executable | ✓ (Limitation 3) | ✓ |
| Corpus selection bias / specific to Shen et al. corpus | ✓ (Limitation 4) | ✓ |
| Temporal dimension unverified | ✓ (Limitation 5) | ✓ |
| Ratio 0.107 not statistically confirmable | ✓ (Caveat in Section 5.3) | ✓ |
| ACM DL dropout non-systematic | ✓ (Section 5.4) | ✓ |

**Missing limitations: PASS. Coverage is thorough.**

---

## Metric Consistency Check

| Metric | Used in Abstract | Section 1 | Section 5 | Section 7 | Consistent? |
|--------|-----------------|-----------|-----------|-----------|-------------|
| 12% coverage | ✓ | ✓ | ✓ (12.1%) | ✓ | ✓ |
| 100% FoS coverage | ✓ | ✓ | ✓ | ✓ | ✓ |
| 0.107 ratio | ✓ | ✓ | ✓ | ✓ | ✓ |
| 10.6% ML→HCI | ✓ | ✓ | ✓ | — | ✓ |
| 23/23 tests | ✓ | ✓ | ✓ | ✓ | ✓ |
| N=9 edges | — | — | ✓ | — | ✓ |
| 67.3% coverage | ✓ | — | ✓ | — | ✓ |
| INCONCLUSIVE framing | ✓ | ✓ | ✓ | ✓ | ✓ |

**Metric consistency: PASS.**

---

## Summary for Revision Agent

### Priority Fix List

1. **MAJOR-MATH-001:** Add "42 of 47" numerics to the 89.4% prose sentence in Section 5.3 — SHOULD FIX (simple one-line change)

### Key Concerns

- All numerical claims verified against ground truth — none incorrect after R1 fix.
- Mathematical validity is sound. All calculations check out.
- Baseline fairness N/A (measurement paper).
- Limitations coverage is thorough.

### What's Working

- INCONCLUSIVE framing is consistent and principled throughout.
- All ratio calculations are arithmetically correct.
- The honest acknowledgment that statistical tests were not run is clear.
- The R1 correction (ML_NLP=28, HCI=5) is correctly applied.
- "Four contributions" in Conclusion now matches Introduction (R1 fix applied).
- Reduction of "striking" language (R1 fix) improves credibility.
