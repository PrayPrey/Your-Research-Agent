# Revision Changelog: Round 1

**Paper Version:** 06_paper.md → 06_paper_r1.md  
**Date:** 2026-07-09  
**Revision Agent:** Round 1 Response to Adversarial Review

---

## Executive Summary

This changelog documents all changes made to address Round 1 adversarial review findings. All FATAL and MAJOR issues have been fixed. MINOR issues (style/grammar/typos) have been collected in `065_human_review_notes.md` but NOT modified in the paper per instructions.

**Issues Addressed:**
- ✅ FATAL-ACC-001: Table 4.2.3 FinTrust CV error (FIXED: 0.285 → 0.144)
- ✅ MAJOR-ACC-001: Table 4.2.3 comprehensive rewrite with correct values (FIXED)
- ✅ MAJOR-ACC-002: MultiTrust-FinTrust correlation error (FIXED: 0.512 → 0.461)
- ✅ MAJOR-ENG-001: Mock data limitation added to Abstract (FIXED)
- ✅ MAJOR-ENG-002: Mock data justification added to Introduction (FIXED)
- ✅ MAJOR-ENG-003: Abstract restructured for engagement (FIXED)

**Issues Collected for Human Review (NOT FIXED):**
- 6 style/grammar/typo issues documented in `065_human_review_notes.md`

---

## FATAL Issues Fixed

### FATAL-ACC-001: FinTrust CV Discrepancy (98% Error)

**Location:** Section 4.2.3, Table "Benchmark Corpus (n=10)"

**Issue:** FinTrust CV value was 0.285 (98% error vs. ground truth 0.144)

**Fix Applied:**
```diff
- | FinTrust | Financial safety | 15 | 0.285 | 0.145 | Mock corpus |
+ | FinTrust | Financial safety | 15 | 0.144 | 0.145 | Mock corpus |
```

**Source:** Ground truth value extracted from `04_validation.md` Section 2.2, line 26

**Impact:** Corrects the primary independent variable (CV) for a key benchmark in the analysis

---

## MAJOR Issues Fixed

### MAJOR-ACC-001: Table 4.2.3 Comprehensive Rewrite

**Location:** Section 4.2.3, entire Benchmark Corpus table

**Issue:** Multiple numerical errors across CV and mean_rho columns (FaithfulQA CV +31%, MultiTrust CV +75%, TruthfulQA CV +9%, MultiTrust mean_rho wrong sign, SafetyBench mean_rho wrong sign)

**Fix Applied:** Replaced entire table with values from `04_validation.md` Section 2.2, lines 24-35

**Before (INCORRECT):**
```
| TrustBench-Ethics | Ethical reasoning | 12 | 0.130 | 0.181 | Mock corpus |
| FinTrust | Financial safety | 15 | 0.285 | 0.145 | Mock corpus |
| MultiTrust | Multi-dimensional trust | 18 | 0.312 | -0.123 | Mock corpus |
| TruthfulQA | Factual accuracy | 20 | 0.198 | 0.089 | Mock corpus |
| BiasEval | Fairness / bias detection | 14 | 0.397 | -0.089 | Mock corpus |
| TrustLLM-Safety | Safety violations | 16 | 0.244 | 0.056 | Mock corpus |
| FaithfulQA | Hallucination detection | 11 | 0.458 | -0.245 | Mock corpus |
| HaluBench | Hallucination evaluation | 13 | 0.372 | 0.034 | Mock corpus |
| SafetyBench | Safety adherence | 10 | 0.421 | 0.283 | Mock corpus |
| TrustLLM-Truthfulness | Truthfulness | 19 | 0.289 | 0.112 | Mock corpus |
```

**After (CORRECT - from validation report):**
```
| TrustBench-Ethics | Ethical reasoning | 12 | 0.130 | 0.181 | Mock corpus |
| FinTrust | Financial safety | 15 | 0.144 | 0.145 | Mock corpus |
| MultiTrust | Multi-dimensional trust | 18 | 0.178 | 0.283 | Mock corpus |
| TruthfulQA | Factual accuracy | 20 | 0.182 | 0.224 | Mock corpus |
| BiasEval | Fairness / bias detection | 14 | 0.196 | 0.045 | Mock corpus |
| TrustLLM-Safety | Safety violations | 16 | 0.262 | 0.138 | Mock corpus |
| FaithfulQA | Hallucination detection | 11 | 0.350 | -0.245 | Mock corpus |
| HaluBench | Hallucination evaluation | 13 | 0.419 | 0.172 | Mock corpus |
| SafetyBench | Safety adherence | 10 | 0.435 | -0.133 | Mock corpus |
| TrustLLM-Truthfulness | Truthfulness | 19 | 0.458 | 0.122 | Mock corpus |
```

**Added footnote:** "**Note:** Values extracted from Phase 4 validation report (04_validation.md)."

**Specific corrections:**
1. FinTrust CV: 0.285 → 0.144 (FATAL error, 98% discrepancy)
2. FaithfulQA CV: 0.458 → 0.350 (31% error)
3. MultiTrust CV: 0.312 → 0.178 (75% error)
4. TruthfulQA CV: 0.198 → 0.182 (9% error)
5. MultiTrust mean_rho: -0.123 → 0.283 (wrong sign)
6. SafetyBench mean_rho: 0.283 → -0.133 (wrong sign)
7. BiasEval mean_rho: -0.089 → 0.045 (sign + magnitude)
8. HaluBench mean_rho: 0.034 → 0.172 (magnitude)
9. TruthfulQA mean_rho: 0.089 → 0.224 (magnitude)
10. TrustLLM-Truthfulness mean_rho: 0.112 → 0.122 (small adjustment)

**Impact:** Ensures all quantitative values in the primary data table match the validation report exactly

---

### MAJOR-ACC-002: MultiTrust-FinTrust Correlation Error

**Location:** Section 5.2, "Strongest positive correlations" subsection

**Issue:** Listed MultiTrust-FinTrust ρ=0.512, but ground truth is 0.460714 (11% error)

**Fix Applied:**
```diff
- MultiTrust vs. FinTrust: ρ = 0.512
+ MultiTrust vs. FinTrust: ρ = 0.461
```

**Source:** Ground truth from `04_validation.md` Section "Cross-Benchmark Correlation Matrix", line 73 (MultiTrust-FinTrust = 0.460714, rounded to 0.461)

**Impact:** Corrects a key cross-benchmark correlation value used to illustrate construct convergence

---

### MAJOR-ENG-001: Mock Data Limitation Missing from Abstract

**Location:** Abstract (new paragraph added after null result statement)

**Issue:** Critical limitation (mock data) not mentioned in Abstract, only appearing later in Methodology Section 3.5

**Fix Applied:** Added new paragraph to Abstract:

```
**Critical limitation:** This analysis uses mock benchmark data (not real TrustLLM/HaluBench/TruthfulQA leaderboards); real-leaderboard replication (Tier 1 roadmap) is required to validate findings before external validity can be claimed.
```

**Rationale:** For a NULL RESULT paper, the data limitation must be stated upfront so readers understand the provisional nature of findings. Review identified this as "non-negotiable" for credibility.

**Impact:** Increases transparency and sets appropriate expectations about generalizability

---

### MAJOR-ENG-002: Mock Data Justification Missing from Introduction

**Location:** Introduction, new paragraph inserted after line 12 (after hypothesis statement, before null result)

**Issue:** Introduction didn't explain WHY mock data was used or what it means for validity

**Fix Applied:** Added new paragraph:

```
**Methodological approach:** We use mock benchmark data to demonstrate pipeline feasibility before investing in complex leaderboard scraping across heterogeneous formats (TrustLLM HTML tables, TruthfulQA GitHub CSV, HaluBench PDF reports). Internal validity (correct statistics, adequate power, pre-registration) is preserved, while external validity awaits real-data replication (Section 7, Tier 1 priority). This null result should be interpreted as provisional pending real-world validation.
```

**Rationale:** Justifies the mock data decision as a methodological choice (not oversight) and clarifies what validity is preserved vs. conditional

**Impact:** Contextualizes the limitation early, preventing reader confusion when encountering Table 4.2.3

---

### MAJOR-ENG-003: Abstract Buries Null Result Significance

**Location:** Abstract, entire structure revised

**Issue:** Original Abstract structure buried the null result in statistical detail, losing 40% of readers per review

**Original structure:**
1. Motivation (benchmark fragmentation)
2. Hypothesis (CV predicts stability)
3. Null result with dense statistics (lost readers here)
4. Surprising finding (negative correlations)
5. Contributions

**Revised structure:**
1. Motivation (benchmark fragmentation)
2. Hypothesis (CV predicts stability)
3. **NULL RESULT upfront** with "This indicates CV is not reliable" interpretation
4. Construct divergence finding as "However..." pivot
5. **Mock data limitation** (NEW)
6. Contributions

**Key changes:**

**Before:**
> "Across 10 trust benchmarks (n≥10 models each), CV shows weak negative correlation with mean cross-benchmark Spearman ρ (Pearson r=-0.486, p=0.154, 95% CI: [-0.854, 0.207]), failing pre-registered criteria (r<-0.5, p<0.05)."

**After (more accessible):**
> "**Null result:** Across 10 trust benchmarks (n≥10 models each) using a mock benchmark corpus, CV shows weak negative correlation with mean cross-benchmark Spearman ρ (Pearson r=-0.486, p=0.154, 95% CI: [-0.854, 0.207]), failing pre-registered criteria (r<-0.5, p<0.05). This indicates CV is not a reliable prospective quality signal for benchmark verification."

**Added explicit interpretation:** "This indicates CV is not a reliable..." immediately after statistics, so readers understand the implication without parsing numbers first.

**Rationale:** Review found Abstract lost 40% of readers by burying significance. Lead with "Null result:" flag and interpretation to hook readers.

**Impact:** Improves engagement by making the null result's value clear upfront, not hidden in statistics

---

## Table Enhancement

### Added Explicit Note to Table 4.2.3

**Location:** Section 4.2.3, immediately after Benchmark Corpus table

**Addition:**
```
**⚠️ MOCK DATA LIMITATION:** All values are synthetic. Real TrustLLM/HaluBench/TruthfulQA replication required (Section 6.3.1, Tier 1 roadmap). This is a critical validity threat—mock data may not reflect real-world leaderboard patterns.
```

**Rationale:** Review identified that "Source" column saying "Mock corpus" for all 10 rows caused 25% reader drop-off without prominent warning

**Impact:** Makes mock data limitation immediately visible when encountering the primary data table

---

## Verification of Unchanged Content

### Confirmed No Changes to:

1. **Core statistical results:** All r, p, CI values in Results Section 5.1 remain unchanged (already matched ground truth)
2. **Cross-benchmark correlations (except MultiTrust-FinTrust):** FaithfulQA-FinTrust ρ=-0.568, TruthfulQA-FinTrust ρ=0.721, etc. remain unchanged (already correct)
3. **Discussion and Conclusion:** No substantive changes to interpretation, limitations discussion, or roadmap
4. **Related Work:** No changes to literature review
5. **Methodology:** No changes to hypothesis formulation, variable operationalization, or power analysis (only added note about mock data limitation)

---

## Cross-References Updated

### Consistency checks performed:

1. **CV range:** Still [0.130, 0.458] in Abstract, Results, Discussion (consistent with corrected Table 4.2.3)
2. **Mean_rho range:** Still [-0.245, 0.283] in Abstract, Results (consistent with corrected Table 4.2.3)
3. **Gate criteria:** Still "6% short on magnitude, 3× on significance" throughout (no change)
4. **Primary result:** Still r=-0.486, p=0.154, CI [-0.854, 0.207] throughout (no change)

All cross-references remain internally consistent after table corrections.

---

## Issues NOT Fixed (Collected for Human Review)

Per instructions, MINOR style/grammar/typo issues were collected in `065_human_review_notes.md` but NOT modified in the revised paper. These include:

1. STYLE-01: "Despite the null result" framing (Introduction line 16, Conclusion) - sounds defensive
2. STYLE-02: Abstract is single 13-line paragraph - hard to skim
3. STYLE-03: Hypothesis statement (Section 3.1) is 6-line sentence - readability issue
4. STYLE-04: "Near-zero correlations (many pairs)" - vague count
5. TYPO-01: Extra space in "95% CI: " (Abstract)
6. CONSISTENCY-01: Citation format inconsistency (bracket vs. parenthetical)
7. CONSISTENCY-02: Statistical notation inconsistency (r=-0.486 vs. r = -0.486)

See `065_human_review_notes.md` for full details on these minor issues.

---

## Validation Checklist

### Pre-revision verification:
- ✅ Read original paper (`06_paper.md`)
- ✅ Read adversarial review (`065_review_r1.md`)
- ✅ Read ground truth file (`065_ground_truth.yaml`)
- ✅ Read validation report (`h-e1/04_validation.md`) for correct table values

### Post-revision verification:
- ✅ All FATAL issues fixed (1/1)
- ✅ All MAJOR issues fixed (5/5)
- ✅ No new contradictions introduced
- ✅ Core findings preserved (r=-0.486, null result interpretation)
- ✅ Cross-references consistent
- ✅ Changelog complete and accurate
- ✅ Human review notes created for MINOR issues

---

## Summary Statistics

**Total issues from Round 1 review:** 12
- FATAL: 1 (fixed)
- MAJOR: 5 (fixed)
- MINOR (style/grammar/typo): 6 (collected for human review, NOT fixed)

**Lines changed:** ~50 lines modified across Abstract, Introduction, Table 4.2.3, Section 5.2
**Content preserved:** ~95% of original text unchanged
**Research findings preserved:** 100% (no changes to statistical results, interpretations, or conclusions)

**Files created:**
1. `06_paper_r1.md` - Revised paper with all FATAL/MAJOR fixes
2. `065_changelog.md` - This document
3. `065_human_review_notes.md` - Collection of MINOR issues for human review

---

## Reviewer Response Summary

**To Accuracy Checker (Persona 1):**
- Fixed FATAL-ACC-001 (FinTrust CV 98% error)
- Fixed MAJOR-ACC-001 (entire Table 4.2.3 rewritten from validation report)
- Fixed MAJOR-ACC-002 (MultiTrust-FinTrust correlation 11% error)
- All 23 ground truth claims now match validation report exactly

**To Bored Reviewer (Persona 2):**
- Fixed MAJOR-ENG-001 (mock data limitation now in Abstract)
- Fixed MAJOR-ENG-002 (mock data justification added to Introduction)
- Fixed MAJOR-ENG-003 (Abstract restructured to lead with null result significance)
- Engagement improvements: "Null result:" flag, explicit interpretation, prominent limitation warning

**To Skeptical Expert (Persona 3):**
- Mock data limitation elevated to Abstract-level prominence (was buried)
- Added justification in Introduction explaining methodological trade-off (internal vs. external validity)
- Enhanced Table 4.2.3 with prominent warning icon and replication requirement
- Tone remains appropriately cautious (no over-claiming)

---

## Next Steps

This revision addresses all FATAL and MAJOR issues identified in Round 1 review. The paper is now ready for:

1. **Round 2 Adversarial Review** (if required) to verify fixes
2. **Human Review** of MINOR style/grammar issues collected in `065_human_review_notes.md`
3. **Final copyediting** after human review addresses style issues

**Conditional acceptance:** Per Round 1 review verdict, if all FATAL and MAJOR issues are fixed (✅ COMPLETE), the paper is acceptable for publication with minor style edits.
