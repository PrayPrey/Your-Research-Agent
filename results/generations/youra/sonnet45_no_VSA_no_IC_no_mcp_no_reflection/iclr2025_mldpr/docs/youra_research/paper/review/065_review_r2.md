# Round 2 Adversarial Review: Numerical Verification

**Review Date**: 2026-08-28  
**Reviewer**: Adversary Agent (Round 2)  
**Paper Version**: `06_paper_r1.md`  
**Ground Truth**: `065_ground_truth.yaml`  
**Previous Review**: `065_review_r1.md`

---

## Executive Summary

| Category | Fatal | Major | Minor |
|----------|-------|-------|-------|
| **R1 Fix Verification** | 0 | 1 | 0 |
| **Numerical Accuracy** | 0 | 1 | 0 |
| **Mathematical Validity** | 0 | 0 | 1 |
| **TOTAL** | **0** | **2** | **1** |

**Recommendation**: **MINOR_REVISION**

**Status**: R1 successfully addressed FATAL-A1 (ImageNet date contradiction). Two MAJOR issues remain: (1) figures still missing from paper body, (2) confidence interval mismatch between ground truth and validation file.

---

## Part 1: Verification of R1 Fixes

### 1.1 FATAL-A1 Fix: ImageNet Temporal Contradiction ✅ RESOLVED

**R1 Review Issue**: Paper stated ImageNet saturation as "August 2015" (h-m1 convergence) vs "June 2019" (h-c1 expert consensus) without explanation—46-month gap unexplained.

**R1 Paper Response** (lines 222-223):
> **Note on dual saturation dates**: Score convergence detected ImageNet saturation as August 2015 (h-m1 algorithmic signal), while expert modal consensus placed saturation at June 2019 (h-c1 community recognition). This 46-month lag suggests community recognition trails algorithmic signal by approximately 4 years—validating the early warning potential of automated detection.

**Verification**: 
- ✅ Explanation added in Results §5.3
- ✅ Reinforced in Discussion §6.1 (line 271)
- ✅ Framing reinterprets contradiction as validation of early warning hypothesis

**Verdict**: RESOLVED. Explanation is clear and scientifically sound.

---

### 1.2 MAJOR-E1 Fix: Missing Figures ❌ PARTIALLY FIXED

**R1 Review Issue**: Paper contained ZERO figure references despite 6 figures documented in ground truth.

**Current Status**:
- Figures directory verified: `/home/PrayPrey/.../paper/figures/` contains all 6 PNG files (42-98KB each)
- `grep -n "Figure\|figure" 06_paper_r1.md` → **ZERO matches**
- Paper still has NO figure references in body text

**Search Results**:
```bash
$ ls figures/
agreement_bars.png               # 42KB (exists)
confidence_stratification.png    # 60KB (exists)
convergence_timeline_imagenet.png # 91KB (exists)
gate_metrics.png                  # 74KB (exists)
lead_time_histogram.png           # 87KB (exists)
timeline.png                      # 98KB (exists)

$ grep -n "Figure" 06_paper_r1.md
(no output)
```

**Verdict**: ❌ NOT RESOLVED. Figures exist but remain unreferenced. Paper is still text-only.

**MAJOR-R2-E1**: Figures Still Missing from Paper Body

**Location**: Results sections (§5.1-5.5), Discussion §6.1

**Issue**: R1 revision did NOT add figure references despite R1 review MAJOR-E1 flag. Ground truth documents 6 figures, all exist as PNG files, but paper body contains zero `Figure N` references or image markdown links.

**Required Figures** (from ground truth):
- Figure 1: `agreement_bars.png` → Results §5.1 (h-c1 consensus)
- Figure 2: `convergence_timeline_imagenet.png` → Results §5.3 (h-m1 detection)
- Figure 3: `timeline.png` → Results §5.4 (h-m2 precedence)
- Figure 4: `lead_time_histogram.png` → Discussion §6.1
- Figure 5: `gate_metrics.png` → Results §5.6 (h-m3 precision)
- Figure 6: `confidence_stratification.png` → Results §5.2 (h-c2 dispersion)

**Fix Required**: Add figure markdown references at appropriate locations:
```markdown
Results §5.1 after Table 1:
![Figure 1: Expert consensus agreement rates by benchmark](figures/agreement_bars.png)

Results §5.3 after Table 2:
![Figure 2: ImageNet score convergence timeline with saturation detection](figures/convergence_timeline_imagenet.png)
```

**Why MAJOR**: Engagement issue flagged in R1 remains unresolved. Figures are load-bearing for ML paper skimmability. Text-only presentation hurts readability.

---

### 1.3 Other R1 MAJOR Issues: Status Check

**MAJOR-C4 (Infrastructure overclaims)**: ✅ RESOLVED
- Abstract line 3 now states "validated on synthetic data (real-world deployment pending)"
- Introduction uses "proof-of-concept" framing
- Conclusion §7 softened to "could enable" rather than "operationalizes"

**MAJOR-C1 (Linzen citation)**: N/A (not numerically verifiable in R2)

**MAJOR-C2 (FAIR-B underspecified)**: N/A (not numerically verifiable in R2)

**MAJOR-C3 (No algorithmic baselines)**: N/A (not numerically verifiable in R2)

**MAJOR-A2 (Threshold calibration)**: N/A (methodology issue, not numerical)

**MAJOR-A3 (Cohen's h)**: See §2.3 below for verification

---

## Part 2: Ground Truth Numerical Verification

### 2.1 Verification Methodology

**Search Strategy**: Used `grep` and `Read` tool to search actual validation files (h-*/04_validation.md) for exact numerical values claimed in paper and ground truth.

**Files Searched**:
```
/docs/youra_research/h-c1/04_validation.md  (expert consensus)
/docs/youra_research/h-c2/04_validation.md  (low-confidence dispersion)
/docs/youra_research/h-m1/04_validation.md  (score convergence)
/docs/youra_research/h-m2/04_validation.md  (temporal precedence)
/docs/youra_research/h-e2/04_validation.md  (velocity decay)
/docs/youra_research/h-m3/04_validation.md  (citation correlation)
```

---

### 2.2 Claim-by-Claim Verification Table

| Claim ID | Paper Statement | Ground Truth | Validation File | Match? | Issue? |
|----------|-----------------|--------------|-----------------|--------|--------|
| **claim_1** | "92.9%, 76.3%, 89.5% agreement" | ImageNet 92.9%, GLUE 76.3%, SQuAD 89.5% | h-c1 line 58-60: 92.9%, 76.3%, 89.5% | ✅ YES | None |
| **claim_1 (CI)** | "83.3-100.0%, 62.5-90.0%, 78.3-100.0%" | Same as paper | h-c1 line 59: **63.2-89.5%** (GLUE) | ❌ NO | **MAJOR-R2-A1** |
| **claim_2** | "Levene's p<0.05 (1.5×10⁻⁸, 2.6×10⁻⁴, 0.014)" | ImageNet 1.5×10⁻⁸, GLUE 2.6×10⁻⁴, SQuAD 0.014 | h-m1 line 29-31: 1.5e-08, 2.6e-04, 0.014 | ✅ YES | None |
| **claim_2 (thresholds)** | "0.8-1.2% thresholds" | ImageNet 1.2%, GLUE 0.8%, SQuAD 1.0% | h-m1 line 29-31: 1.2%, 0.8%, 1.0% | ✅ YES | None |
| **claim_3** | "32-78 months (mean 48mo)" | ImageNet 78mo, GLUE 34mo, SQuAD 32mo | h-m2 line 50-52: 78.1mo, 34.1mo, 32.1mo | ⚠️ CLOSE | See §2.3 |
| **claim_3 (dates)** | "2015-08, 2018-03, 2018-05" | Same as paper | h-m2 line 50-52: 2015-08, 2018-03, 2018-05 | ✅ YES | None |
| **claim_4** | "3-4× wider dispersion, 30% std dev" | GLUE 30.0%, 1.40yr std, 4.67yr range | h-c2 line 49: 30.0%, 1.40yr, 4.67yr | ✅ YES | None |
| **claim_5** | "100% detection, CV=0.242" | Detection 100%, CV 0.242 | h-e2 line 38-39: 100% (3/3), CV 0.242 | ✅ YES | None |
| **claim_6** | "Precision 0.50 vs 0.80 target" | Precision 0.50, target 0.80 | h-m3 line 16: 0.50, target 0.80 | ✅ YES | None |

---

### 2.3 Numerical Discrepancies Found

#### **MAJOR-R2-A1**: Confidence Interval Mismatch (GLUE)

**Location**: Results §5.1 Table 1, Ground Truth line 24

**Issue**: 
- **Ground Truth** claims GLUE CI: `62.5%-90.0%`
- **Validation File** (h-c1/04_validation.md line 59): `63.2%-89.5%`
- **Paper R1** (line 193 Table 1): `62.5-90.0%` (matches ground truth, NOT validation)

**Search Evidence**:
```bash
$ grep "GLUE.*76.3" h-c1/04_validation.md
| GLUE | 76.3% | 63.2%-89.5% | 2020-03 | 38 | 1.000 |
```

**Arithmetic Verification**:
- Ground truth CI: 62.5% to 90.0% → width = 27.5 percentage points
- Validation CI: 63.2% to 89.5% → width = 26.3 percentage points
- Difference: 1.2 percentage points (non-trivial)

**Root Cause**: Ground truth file (`065_ground_truth.yaml`) was likely written BEFORE h-c1 validation finalized. Paper copied from ground truth instead of validation file.

**Impact**: 
- Low severity (CI widths differ by ~1pp, doesn't change interpretation)
- BUT indicates paper author did NOT verify numbers against actual validation files
- Suggests possible copy-paste from ground truth without verification

**Fix Required**: Update paper Table 1 (line 193) to match h-c1 validation file:
```markdown
| GLUE | 2020-03 | 76.3% | 63.2-89.5% | 0.43 |
```

**Why MAJOR**: Not isolated typo—indicates systematic issue where paper numbers came from ground truth (which has errors) rather than validation files (which are authoritative). If paper copied from ground truth blindly, other undetected errors may exist.

---

#### **MINOR-R2-M1**: Lead Time Rounding (Acceptable)

**Location**: Results §5.4 Table 4, Discussion §6.1

**Issue**: 
- **Paper** states: "32-78 months (mean 48 months)"
- **Validation** shows: "32.1-78.1 months (mean 48.1 months)"

**Analysis**:
- Paper rounds to integers (32, 78, 48)
- Validation uses one decimal place (32.1, 78.1, 48.1)
- Difference: 0.1 months ≈ 3 days (negligible)

**Verdict**: ✅ ACCEPTABLE. Rounding to nearest month is standard practice for multi-year timescales. Does NOT constitute error.

**No action required**.

---

#### **MINOR-R2-M2**: Cohen's h Verification

**Location**: Discussion §6.2 L3

**R1 Review Issue**: MAJOR-A3 claimed Cohen's h=1.57 is incorrect; should be ~1.29.

**Validation File Evidence** (h-m2/04_validation.md):
```
With only n=3 pairs, binomial test lacks statistical power. Even 3/3 successes 
yields p=0.125. Effect size (Cohen's h=1.57) indicates large practical effect, 
but small sample prevents formal significance.
```

**Paper R1 Statement** (line not found via grep—checking Discussion):
- `grep "Cohen" 06_paper_r1.md` → **NO MATCHES**

**Verification**: Paper R1 does NOT mention Cohen's h anywhere. R1 review flagged this as incorrect calculation, and R1 revision **removed the claim entirely** rather than recalculating.

**Verdict**: ✅ ACCEPTABLE RESOLUTION. Removing unverified statistical claim is conservative approach. Paper no longer makes Cohen's h claim, so no error exists.

**No action required**.

---

## Part 3: Mathematical Validity Check (Skeptical Expert)

### 3.1 Temporal Arithmetic Verification

**Claim**: "ImageNet saturated August 2015, 78 months before ViT adoption February 2022"

**Calculation**:
- Aug 2015 to Feb 2022 = (2022-2015)×12 + (2-8) = 7×12 - 6 = 84 - 6 = 78 months ✅

**Claim**: "GLUE saturated March 2018, 34 months before GPT-3 adoption January 2021"

**Calculation**:
- Mar 2018 to Jan 2021 = (2021-2018)×12 + (1-3) = 3×12 - 2 = 36 - 2 = 34 months ✅

**Claim**: "SQuAD saturated May 2018, 32 months before GPT-3 adoption January 2021"

**Calculation**:
- May 2018 to Jan 2021 = (2021-2018)×12 + (1-5) = 3×12 - 4 = 36 - 4 = 32 months ✅

**Mean Lead Time**:
- (78 + 34 + 32) / 3 = 144 / 3 = 48 months ✅

**Verdict**: All temporal arithmetic correct.

---

### 3.2 Statistical Significance Claims

**Claim**: "Levene's test p<0.05 for all benchmarks"

**Values**: ImageNet p=1.5×10⁻⁸, GLUE p=2.6×10⁻⁴, SQuAD p=0.014

**Verification**:
- 1.5×10⁻⁸ = 0.000000015 < 0.05 ✅
- 2.6×10⁻⁴ = 0.00026 < 0.05 ✅
- 0.014 < 0.05 ✅

**Verdict**: All p-values correctly interpreted as statistically significant.

---

### 3.3 Percentage Calculation Verification

**Claim**: "GLUE 30.0% standard deviation (1.40 years std over 4.67-year range)"

**Calculation**:
- (1.40 / 4.67) × 100% = 29.98% ≈ 30.0% ✅

**Claim**: "ImageNet 27.8% standard deviation (1.23 years std over 4.42-year range)"

**Calculation**:
- (1.23 / 4.42) × 100% = 27.82% ≈ 27.8% ✅

**Verdict**: Percentage calculations correct.

---

### 3.4 Baseline Comparison Fairness

**Claim**: "100% detection rate (3/3 benchmarks)"

**Analysis**: Paper tests on 3 benchmarks (ImageNet, GLUE, SQuAD) and detects saturation on all 3. This is NOT selection bias IF:
1. Benchmarks were pre-specified (not cherry-picked post-hoc)
2. All tested benchmarks reported (no suppressed failures)

**Evidence**: 
- Methodology §3.1-3.3 specifies 3 benchmarks upfront ✅
- Results §5.3 reports all 3 results (no selective reporting) ✅
- Limitations §6.2 L2 acknowledges synthetic data limits generalization ✅

**Verdict**: ✅ FAIR. 100% detection is valid for tested sample, with appropriate caveats.

---

### 3.5 Impossible Claims Audit

**Question**: Do any numbers contradict each other or violate mathematical constraints?

**Checks**:
- ✅ Agreement rates sum to ≤100% (not percentages of overlapping sets)
- ✅ Confidence intervals contain point estimates (92.9% ∈ [83.3%, 100%])
- ✅ Lead times are positive (saturation precedes shifts)
- ✅ Standard deviations < range (1.40 years < 4.67 years)
- ✅ P-values ∈ [0, 1]
- ✅ Precision/recall ∈ [0, 1]

**Verdict**: No impossible claims detected.

---

## Part 4: Search Log (Transparency)

### 4.1 Grep Searches Performed

```bash
1. grep -n "92.9\|76.3\|89.5" h-c1/04_validation.md
   → Found: Lines 58-60, 65-67, 107, 129-131, 178, 292
   → Verified: Agreement rates match

2. grep -n "1.5.*10.*8\|2.6.*10.*4\|0.014" h-m1/04_validation.md
   → Found: Lines 31, 114
   → Verified: Levene's p-values match

3. grep -n "78\|34\|32.*month\|48.*month" h-m2/04_validation.md
   → Found: Lines 15, 19-20, 34, 50-58, 115, 191, 226, 230
   → Verified: Lead times match (with 0.1mo rounding)

4. grep -n "0.242\|100%" h-e2/04_validation.md
   → Found: Lines 38-39, 66
   → Verified: Velocity metrics match

5. grep -n "precision\|0.50\|0.80" h-m3/04_validation.md
   → Found: Lines 16, 21, 29, 48, 58, 108-109, 120, 126, 132, 143, etc.
   → Verified: Precision values match

6. grep "63.2\|62.5" h-c1/04_validation.md
   → Found: 63.2%-89.5% (actual CI)
   → MISMATCH: Ground truth claims 62.5%-90.0%

7. grep -n "Figure\|figure" 06_paper_r1.md
   → Found: ZERO matches
   → CONFIRMED: No figure references in R1 paper
```

---

### 4.2 Files Read in Full

```
1. 06_paper_r1.md (full paper, 327 lines)
2. 065_ground_truth.yaml (full ground truth, 275 lines)
3. 065_review_r1.md (previous review, 582 lines)
4. h-m1/04_validation.md (lines 1-100)
5. h-c2/04_validation.md (lines 1-100)
```

---

## Part 5: Summary for Revision Agent

### 5.1 Issue Counts

| Severity | Count | IDs |
|----------|-------|-----|
| FATAL | 0 | None (R1 FATAL-A1 resolved) |
| MAJOR | 2 | MAJOR-R2-E1 (figures missing), MAJOR-R2-A1 (CI mismatch) |
| MINOR | 1 | MINOR-R2-M1 (lead time rounding, acceptable) |

---

### 5.2 Priority Fix List

#### MAJOR (Must Fix)

1. **MAJOR-R2-E1**: Add Figure References to Paper Body
   - **Location**: Results §5.1-5.6, Discussion §6.1
   - **Fix**: Insert 6 figure markdown links at appropriate locations (see §1.2 for details)
   - **Effort**: Low (copy-paste figure references)

2. **MAJOR-R2-A1**: Correct GLUE Confidence Interval
   - **Location**: Results §5.1 Table 1 line 193
   - **Fix**: Change "62.5-90.0%" to "63.2-89.5%" (match h-c1 validation)
   - **Effort**: Trivial (one-number change)

#### MINOR (Optional)

3. **MINOR-R2-M1**: Lead Time Rounding
   - **Status**: ACCEPTABLE (no action required)
   - Paper rounds 48.1→48 months; standard practice for multi-year timescales

---

### 5.3 Verification Verdicts

| Aspect | Status | Evidence |
|--------|--------|----------|
| R1 FATAL-A1 fix (ImageNet dates) | ✅ RESOLVED | Lines 222-223, 271 explain 46mo lag |
| R1 MAJOR-C4 fix (infrastructure overclaims) | ✅ RESOLVED | Abstract/conclusion use "proof-of-concept" framing |
| Agreement rates (92.9%, 76.3%, 89.5%) | ✅ VERIFIED | h-c1 validation lines 58-60 match |
| Levene's p-values (1.5×10⁻⁸, 2.6×10⁻⁴, 0.014) | ✅ VERIFIED | h-m1 validation lines 29-31 match |
| Lead times (78mo, 34mo, 32mo, mean 48mo) | ✅ VERIFIED | h-m2 validation (0.1mo rounding acceptable) |
| Velocity decay (100%, CV=0.242) | ✅ VERIFIED | h-e2 validation lines 38-39 match |
| Citation precision (0.50 vs 0.80) | ✅ VERIFIED | h-m3 validation line 16 matches |
| GLUE confidence interval | ❌ MISMATCH | Paper: 62.5-90.0%, Validation: 63.2-89.5% |
| Figures in paper body | ❌ MISSING | Zero figure references despite 6 PNGs existing |

---

### 5.4 Recommendation

**Status**: MINOR_REVISION

**Rationale**: 
- R1 successfully resolved FATAL issue (ImageNet date contradiction)
- Numerical accuracy is HIGH (6/7 claims verified, 1 minor CI mismatch)
- Mathematical validity checks passed
- Two MAJOR issues remain but both are LOW-EFFORT fixes:
  1. Add figure references (copy-paste task)
  2. Correct one CI value (one-number change)

**Estimated Revision Effort**: 30 minutes

**Convergence Likelihood**: VERY HIGH (no new conceptual issues, only formatting/copy-paste errors)

---

### 5.5 Round 3 Scope

If R2 fixes applied, Round 3 should focus on:
1. **Credibility issues** flagged in R1 but not verifiable in R2:
   - MAJOR-C1 (Linzen citation verification)
   - MAJOR-C2 (FAIR-B framework specification)
   - MAJOR-C3 (Algorithmic baseline comparisons)
2. **Engagement flow** (Bored Reviewer persona):
   - Results §5.7 redundancy
   - Discussion §6.3-6.4 generic content
3. **Final polish** (typography, formatting)

**R2 Review Complete**: 2026-08-28  
**Next Step**: Route to Revision Agent for figure insertion + CI correction
