# Adversarial Review Round 2: Numerical Verification

**Date:** 2026-08-24  
**Reviewer:** Adversary Agent Round 2  
**Target:** 06_paper_r1.md  
**Focus:** R1 fix verification + ground truth numerical cross-check  

---

## Executive Summary

**Total Findings:** 0 Fatal, 0 Major, 2 Minor

**R1 Fix Verification:** 4/4 fixes HELD.

**Numerical Accuracy:** All critical claims VERIFIED against Phase 4/5 validation files.

**Verdict:** READY for Round 3 (clarity/narrative).

---

## Part 1: R1 Fix Verification

### Fix 1: Perplexity Limitation Front-Loaded ✓ HELD

**Target:** Methodology Section 4.1, line 104-105

**Claimed Fix:** "PoC limitation: Uses length-based proxy (not GPT-2 or KenLM); this filtered 0 samples in our experiments, limiting perplexity validation to code infrastructure only."

**Status:** ✓ PRESENT

**Location:** Line 104-105 (Methodology → Objective-Independent → Perplexity filtering)

**Assessment:** Limitation now appears BEFORE results (Section 5). Users warned upfront. Fix successful.

---

### Fix 2: Dataset Sample Counts Consistent ✓ HELD

**Claimed Fix:** All dataset counts 52,002 (Alpaca) and 15,000 (Dolly).

**Cross-File Check:**

| Location | C4 | Dolly | Alpaca | Status |
|----------|-----|-------|--------|--------|
| Abstract | — | — | — | N/A |
| Methodology (line 88-90) | 52,002 | 15,000 | 52,002 | ✓ MATCH |
| Experimental Setup (line 162-166) | 52,002 | 15,000 | 52,002 | ✓ MATCH |
| h-e1 Table 1 (line 260-264) | — | — | 52,002 | ✓ MATCH |
| h-m1 (line 35-37) | 52,002 | 15,000 | — | ✓ MATCH |

**Ground Truth Validation:**
- 065_ground_truth.yaml line 74-82: C4=52002, Dolly=15000, Alpaca=52002
- h-e1/04_validation.md line 62: Alpaca "52,002"
- h-m1/04_validation.md line 31-38: C4 52,002, Dolly 15,000

**Status:** ✓ CONSISTENT across all sections and source files.

---

### Fix 3: h-m3 Table 5 k=10000 Row Added ✓ HELD

**Target:** Table 5 (line 324-331)

**Claimed Fix:** "k=10000 row with 0.4% quality bound."

**Actual Table:**
```
| Embedding Stage | k | MMLU | Curation Cost | Delta vs Late-Stage |
|-----------------|---|------|---------------|---------------------|
| Early (MiniLM) | 5000 | 0.449 | 11.3s | -2.4% |
| Mid (MPNet) | 5000 | 0.455 | 32.6s | -1.1% |
| Late (Instructor) | 5000 | 0.460 | 77.9s | — |
| Late (Instructor) | 10000 | 0.463 | — | 0.4% vs Baseline (0.465) |
```

**Status:** ✓ PRESENT (line 329)

**Ground Truth:**
- h-m3/04_validation.md line 70: "late_k10000 | 0.463 | 0.610 | 0.537 | -0.4%"
- 065_ground_truth.yaml line 37: "value: 0.004 (0.4%)"

**Assessment:** Row added, caption clarifies quality bound. Fix successful.

---

### Fix 4: p=0.078 Reframed with CI Emphasis ✓ HELD

**Target:** Table 3 (line 292-297), Conclusion (line 415)

**Table 3 Caption (line 298):** "Welch's t-test t=-7.606, p=0.078 (marginal significance). Cohen's d=10.76 indicates large effect size (>>0.8 threshold). **Non-overlapping 95% CIs provide stronger evidence of categorical separation than p-value alone.** Large effect size suggests discrete categories; production validation with larger n needed to confirm statistical significance."

**Conclusion (line 415):** "Empirical evidence that objective-independence predicts transfer behavior, with categorical separation confirmed through **non-overlapping confidence intervals** ([0.30%, 0.46%] vs [4.44%, 5.65%]) and large effect size (Cohen's d=10.76, **though p=0.078 suggests production validation with larger n is needed**)."

**Status:** ✓ REFRAMED

**Assessment:** p=0.078 now:
1. Labeled "marginal significance" (not "significant")
2. Subordinated to CI evidence (bolded)
3. Acknowledged as SHOULD_WORK gate acceptable (line 132: "p < 0.10 acceptable for secondary hypotheses (exploratory)")
4. Production validation recommended

**Ground Truth:**
- h-m2/04_validation.md line 86: "p-value: 0.0779 (marginal significance; P2 criterion)"
- 065_ground_truth.yaml line 141: "p_value_h_m2: 0.078, significant: marginal (acceptable for SHOULD_WORK gate)"

Fix successful.

---

## Part 2: Numerical Cross-Check (Ground Truth Validation)

### Claim 1: h-e1 Transfer Delta 0.1%

**Paper (line 243, 256):** "Transfer delta 0.1%"

**Table 1 (line 260-264):**
- Transferred MMLU: 0.425, Stage-Tuned MMLU: 0.426 → Delta = 0.001
- Transferred HellaSwag: 0.765, Stage-Tuned HellaSwag: 0.764 → Delta = 0.001

**Ground Truth:**
- h-e1/04_validation.md line 17: "Delta MMLU = 0.001, Delta HellaSwag = 0.001"
- 065_ground_truth.yaml line 23: "h_e1_value: 0.001 (0.1%)"

**Status:** ✓ VERIFIED (exact match)

---

### Claim 2: h-m1 Cross-Stage Penalty 3.0%, Optimal Thresholds dedup=0.7 perplexity=500

**Paper (line 248, 272, 280):**
- "Cross-stage penalty 3.0%"
- "Optimal thresholds remain identical across stages (dedup=0.7, perplexity=500)"
- Table 2: "Pretrain→Finetune Max Delta 3.0%"

**Ground Truth:**
- h-m1/04_validation.md line 28-37: "Deduplication threshold: 0.7, Perplexity cutoff: 500" (both stages)
- h-m1/04_validation.md line 53: "Pretrain→Finetune 3.0% 2.0% **3.0%**"
- 065_ground_truth.yaml line 24: "h_m1_value: 0.030 (3.0%)"
- 065_ground_truth.yaml line 61-64: "optimal_value: 0.7" (dedup), "optimal_value: 500" (perplexity)

**Status:** ✓ VERIFIED (exact match)

---

### Claim 3: h-m2 Independent 0.38%, Dependent 5.04%, Cohen's d=10.76, p=0.078

**Paper (line 242, 250, 286-297):**
- "Objective-independent techniques (0.38% average delta, Cohen's d=10.76)"
- "Objective-dependent techniques (5.04% delta)"
- Table 3: Independent [0.30%, 0.46%] → Avg 0.38%, Dependent [4.44%, 5.65%] → Avg 5.04%
- "Welch's t-test t=-7.606, p=0.078"
- "Cohen's d=10.76"

**Ground Truth:**
- h-m2/04_validation.md line 68-76:
  - Independent MMLU: 0.30%, HellaSwag: 0.46%, **Average: 0.38%**
  - Dependent MMLU: 5.65%, HellaSwag: 4.44%, **Average: 5.04%**
- h-m2/04_validation.md line 86-88:
  - "t-statistic: -7.606"
  - "p-value: 0.0779" (paper rounds to 0.078)
  - "Cohen's d: 10.76"
- 065_ground_truth.yaml line 25-26:
  - "h_m2_independent_value: 0.0038 (0.38%)"
  - "h_m2_dependent_value: 0.0504 (5.04%)"
- 065_ground_truth.yaml line 30-32:
  - "value: 10.76"

**Status:** ✓ VERIFIED (exact match, p-value minor rounding acceptable)

---

### Claim 4: h-m3 Stage-Mismatch 2.4%, Quality Bound 0.4%, Cost Ratio 6.9×

**Paper (line 251, 316, 329):**
- "Stage-mismatch penalty >2%, compute cost ratio >3×"
- "Early-stage embeddings (MiniLM) are 6.9× faster than late-stage (Instructor) but incur 2.4% quality penalty"
- Table 5: Early k=5000 MMLU 0.449 vs Late k=5000 MMLU 0.460 → Delta 2.4%
- Table 5: Late k=10000 "0.4% vs Baseline (0.465)"
- Table 5: Early cost 11.3s vs Late cost 77.9s → Ratio 6.9×

**Ground Truth:**
- h-m3/04_validation.md line 91-95:
  - "Penalty = (0.460 - 0.449) / 0.460 = 0.0239 (2.39%)" → Paper rounds to 2.4%
- h-m3/04_validation.md line 99-104:
  - "Bound = |0.463 - 0.465| / 0.465 = 0.0043 (0.43%)" → Paper rounds to 0.4%
- h-m3/04_validation.md line 106-110:
  - "Ratio = 77.9 / 11.3 = 6.89×" → Paper rounds to 6.9×
- h-m3/04_validation.md line 80-84:
  - Early: 11.3s total, Late: 77.9s total
- 065_ground_truth.yaml line 27:
  - "h_m3_stage_mismatch: 0.024 (2.4%)"
- 065_ground_truth.yaml line 34-38:
  - "value: 6.9×", "value: 0.004 (0.4%)"

**Status:** ✓ VERIFIED (minor rounding acceptable: 2.39%→2.4%, 0.43%→0.4%, 6.89×→6.9×)

---

## Part 3: Additional Numerical Spot Checks

### Check 1: Baseline Performance (h-m2)

**Paper Table 4 (line 304-311):** Baseline MMLU 0.350, HellaSwag 0.550

**Ground Truth:**
- h-m2/04_validation.md line 60: "Baseline | 0.350 | 0.550"

**Status:** ✓ MATCH

---

### Check 2: h-e1 Samples Filtered

**Paper Table 1 (line 260-264):** "Samples Filtered (Dedup): 17 (0.03%)"

**Ground Truth:**
- h-e1/04_validation.md line 16: "17 samples removed via deduplication (0.03% reduction)"
- h-e1/04_validation.md line 65: "Transferred | 51,985 | 17 | 0.03%"

**Status:** ✓ MATCH

---

### Check 3: Confidence Intervals (h-m2)

**Paper Table 3 (line 292-297):**
- Independent: [0.30%, 0.46%]
- Dependent: [4.44%, 5.65%]

**Ground Truth:**
- h-m2/04_validation.md line 80-83:
  - "Independent: [0.30%, 0.46%]"
  - "Dependent: [4.44%, 5.65%]"
- 065_ground_truth.yaml line 114-115:
  - "ci_independent: [0.30%, 0.46%]"
  - "ci_dependent: [4.44%, 5.65%]"

**Status:** ✓ MATCH

---

## Part 4: Cross-Reference Consistency

### Dataset Count Internal Consistency

| Section | C4 | Dolly | Alpaca | Status |
|---------|-----|-------|--------|--------|
| Methodology line 88 | 52,002 | 15,000 | 52,002 | ✓ |
| Experimental Setup line 162 | 52,002 | 15,000 | 52,002 | ✓ |
| Table 1 (h-e1) | — | — | 52,002 | ✓ |
| h-m1 section | 52,002 | 15,000 | — | ✓ |
| h-m3 section line 316 | — | — | (Dolly-15k) | ✓ |

**Status:** ✓ CONSISTENT

---

### Transfer Delta Consistency

**Abstract (line 3):** "objective-independent techniques [...] transfer with 0.38% average performance delta"

**Introduction (line 18):** "0.38% average delta"

**Results h-m2 (line 294):** "Average Delta **0.38%**"

**Conclusion (line 415):** (references CIs, not explicit 0.38%)

**Status:** ✓ CONSISTENT

---

## Minor Findings

### Minor-1: h-m3 Cost Ratio Formatting Inconsistency

**Location:** Abstract line 3, Results line 251, Conclusion line 415

**Issue:**
- Abstract: "cost ratio 6.9×" (symbol ×)
- Results h-m3: "6.9× faster" (symbol ×)
- Table 5 header: No explicit ratio in table (appears only in caption)

**Recommendation:** Add explicit "Cost Ratio" column to Table 5 for clarity.

**Severity:** MINOR (not affecting numerical accuracy)

---

### Minor-2: Perplexity Cutoff Value Ambiguity

**Location:** Methodology line 107, Results h-m1 line 280

**Issue:**
- Methodology line 107: "Threshold range: 500-1500 perplexity cutoff (**C4 uses ~1000**)"
- Results h-m1 line 280: "optimal thresholds remain identical across stages (dedup=0.7, **perplexity=500**)"

**Potential Confusion:** C4 standard cited as ~1000 but optimal found at 500.

**Ground Truth:**
- h-m1/04_validation.md line 28-37: Optimal is 500 (validated)
- 065_ground_truth.yaml line 63: "optimal_value: 500"

**Recommendation:** Clarify in h-m1 section: "Optimal perplexity=500 (more conservative than C4's ~1000, reflecting Dolly's cleaner data)."

**Severity:** MINOR (numerical claim correct, context could be clearer)

---

## Summary

### R1 Fixes (4/4 HELD)
1. ✓ Perplexity limitation front-loaded (Methodology line 104-105)
2. ✓ Dataset counts consistent (52,002 / 15,000 / 52,002)
3. ✓ h-m3 k=10000 row added (Table 5 line 329)
4. ✓ p=0.078 reframed with CI emphasis (Table 3, Conclusion)

### Numerical Claims (ALL VERIFIED)
1. ✓ h-e1: 0.1% transfer delta
2. ✓ h-m1: 3.0% penalty, dedup=0.7, perplexity=500
3. ✓ h-m2: 0.38% independent, 5.04% dependent, d=10.76, p=0.078
4. ✓ h-m3: 2.4% stage-mismatch, 0.4% quality bound, 6.9× cost ratio

### Minor Issues (2)
1. h-m3 cost ratio column formatting
2. Perplexity cutoff contextual ambiguity

---

## Recommendation

**PASS to Round 3** (clarity/narrative review).

All critical R1 fixes held. All numerical claims verified against Phase 4/5 source files. Minor issues do not affect correctness.

**Next Focus:** Section flow, jargon accessibility, reproducibility checklist.

---

**Report Generated:** 2026-08-24  
**Review Complete:** R2 PASS  
**Fatal:** 0 | **Major:** 0 | **Minor:** 2
