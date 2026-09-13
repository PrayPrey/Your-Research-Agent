# Adversarial Review - Round 2 (Numerical Verification)

**Paper:** Measuring Doctest Executability in Python Corpora: Feasibility of Execution-Filtered SFT Data Curation
**Reviewed:** 2026-08-04T20:10:00Z
**Reviewer:** Adversary Agent v2

---

## Serena MCP Verification Log

Pre-run by Orchestrator. All numerical values cross-checked against:
- `/h-c1/results.json` (primary experiment output)
- `/h-c1/04_validation.md` (validation report)
- `065_ground_truth.yaml` (scholar-verified prior work)

| Source | Field | Value |
|--------|-------|-------|
| results.json | n_sampled | 10000 ✓ |
| results.json | n_pattern_positive | 310 ✓ |
| results.json | n_ast_positive | 204 ✓ |
| results.json | n_executable_positive | 10 ✓ |
| results.json | doctest_pattern_rate | 0.031 ✓ |
| results.json | doctest_ast_rate | 0.0204 ✓ |
| results.json | doctest_executable_rate | 0.001 ✓ |
| results.json | estimated_full_subset_executable_files | 12960 ✓ |
| results.json | estimated_token_pool_M | 0.004376 ✓ |
| results.json | scan_duration_seconds | 129.827 ✓ |
| results.json | seed | 42 ✓ |
| 04_validation.md | n_workers | 4 ✓ |
| 04_validation.md | timeout_sec | 5 ✓ |
| 04_validation.md | "import_error dominates" | stated in text; no specific % ✓ |
| ground_truth | phi-1 50.6% HumanEval at 1.3B | VERIFIED-SCHOLAR ✓ |
| ground_truth | EffiCoder +13pp on Qwen2.5-Coder-7B | VERIFIED-SCHOLAR ✓ |
| ground_truth | StarCoder 40% HumanEval at 15.5B | VERIFIED-SCHOLAR ✓ |

---

## Ground Truth Verification Table

| Claim | Paper Value | Verified Value | Source | Match? |
|-------|-------------|----------------|--------|--------|
| Phase A count/rate | 310 / 3.1% | 310, 0.031 | results.json | PASS |
| Phase B count/rate | 204 / 2.0% | 204, 0.0204 | results.json | PASS |
| Phase C count/rate | 10 / 0.1% | 10, 0.001 | results.json | PASS |
| Gap multiplier | 31× | 3.1/0.1 = 31.0 | math | PASS |
| Token pool | 0.004M | 0.004376M | results.json | PASS (rounded) |
| Token pool gap | 125,000× | 500/0.004 = 125,000 | math | PASS |
| Scan duration | 129.8s | 129.827s | results.json | PASS (rounded) |
| Throughput | ~77 files/sec | 10000/129.8 = 77.0 | math | PASS |
| Workers | 4 | n_workers=4 | 04_validation.md | PASS |
| Unit tests | 28/28 | 28/28 | 04_validation.md | PASS |
| Full-corpus executable files | 12,960 | 12960 | results.json | PASS |
| Phase C fail count | 194 | 204-10=194 | math | PASS |
| import_error fraction | ~95% | NOT in any source file | UNVERIFIED |
| phi-1 HumanEval | 50.6% at 1.3B | VERIFIED-SCHOLAR | ground_truth | PASS |
| EffiCoder improvement | +13pp | VERIFIED-SCHOLAR | ground_truth | PASS |
| StarCoder HumanEval | 40% at 15.5B | VERIFIED-SCHOLAR | ground_truth | PASS |
| Dataset disclosed | codeparrot-clean-valid | fallback confirmed | 04_validation.md | PASS |

---

## R1 Fix Verification

| R1 Issue | Fix Required | Fix Applied? | Evidence |
|----------|-------------|-------------|----------|
| MAJOR-A1: "30×" in Section 5.1 paragraph | Change to "31×" | **YES — FIXED** | Section 5.1 now reads "falls 31× below it" — confirmed in paper text |
| MAJOR-C1: "First empirical characterization" | Scope more precisely | **YES — FIXED** | Section 1.4 now reads "First systematic measurement of the gap between `>>>` pattern prevalence and subprocess executability in a curated Python code corpus used for LLM training" |
| MAJOR-C2: "production-ready" overclaim | Remove/soften | **YES — FIXED** | Section 6.1 reads "feasible at scale and avoids the import isolation problem"; Section 6.3 "production-ready" removed |
| MAJOR-C2: "expected outcome 2-5pp" speculation | Remove or caveat | **YES — FIXED** | Section 5.2 no longer contains speculative HumanEval range; reads as design-only |
| MAJOR-E1: Scope contract with reader | Clarify H-C1 as primary contribution | **YES — FIXED** | Section 5.2 explicitly states "not a current claim of this paper" and notes compile-only benefit is pending H-E1 confirmation |
| Human: "~95%" unsourced | Cite or soften | **PARTIAL** | Paper retains "~95%" in Section 5.1 and Section 7 without a source — softening was applied in tone but figure is still present as an approximation |
| Human: "ruling out file size as confound" | Soften given n=10 | **NOT VERIFIED** | Section 5.3 text was not reviewed by R1 revision agent — needs check |

---

## Mathematical Validity Analysis

### Check 1: Core Gap Calculation
- Paper: "31× gap between 3.1% and 0.1%"
- Math: 3.1 / 0.1 = 31.0 exactly
- Consistency: Abstract (31×), Introduction (31×), Section 1.4 (31×), Section 5.1 (31×), Figure 2 caption (31×), Conclusion (31×)
- **VALID — fully consistent throughout**

### Check 2: Token Pool and Gap
- Paper: "0.004M tokens" / "125,000× below 500M target"
- Actual: 0.004376M → rounds to 0.004M ✓
- Math: 500 / 0.004 = 125,000 ✓
- **VALID**

### Check 3: Throughput Calculation
- Paper: "~77 files/second"
- Math: 10,000 / 129.827 = 77.0 files/second ✓
- **VALID**

### Check 4: Phase B→C Attrition
- Phase B: 204 files
- Phase C pass: 10 files
- Phase C fail: 204 − 10 = 194 files
- Paper Figure 4 description: "194 files that passed Phase B" ✓
- **VALID**

### Check 5: Stacked Breakdown (Figure 2 description)
- Paper: "96.9% of files have no doctest patterns; 2.1% have patterns but fail AST parsing; 1.9% pass Phase B but fail Phase C; 0.1% pass all three phases"
- Verify: 
  - No patterns: (10,000−310)/10,000 = 9,690/10,000 = 96.9% ✓
  - Pattern but fail AST: (310−204)/10,000 = 106/10,000 = 1.06% — **DISCREPANCY: paper claims 2.1%**
  - Pass B but fail C: (204−10)/10,000 = 194/10,000 = 1.94% ≈ 1.9% ✓
  - Pass all: 10/10,000 = 0.1% ✓
  - Sum: 96.9 + 1.06 + 1.94 + 0.1 = 100.0% ✓ (with corrected value)
- **DISCREPANCY FOUND: "2.1% have patterns but fail AST parsing" is incorrect. Actual: (310−204)/10,000 = 1.06%, which should round to 1.1%, not 2.1%**

### Check 6: ~95% Import Error Claim
- Source: 04_validation.md states "import_error dominates" without a specific percentage
- No quantified percentage appears in results.json or 04_validation.md
- Paper presents this as a measured value (~95%) in Section 5.1 table and Section 7
- **UNSOURCED APPROXIMATION — not verifiable from released artifacts**

### Check 7: AST Rate Decimal
- Paper Section 5.1 table: "Phase B (AST) | 204 | 2.0%"
- results.json: doctest_ast_rate = 0.0204 = 2.04%
- Paper rounds 2.04% to 2.0% — technically correct (1 decimal)
- Section 1.4 states "Phase B: 2.0%" — consistent
- **VALID (rounding)**

---

## Executive Summary

| Category | FATAL | MAJOR | MINOR |
|----------|-------|-------|-------|
| Numerical accuracy | 0 | 1 | 1 |
| Mathematical consistency | 0 | 0 | 0 |
| R1 fix verification | 0 | 0 | 1 |
| Prior work accuracy | 0 | 0 | 0 |
| **TOTAL** | **0** | **1** | **2** |

**Recommendation: MINOR_REVISION** — The R1 fixes were successfully applied for the four MAJOR issues. One new MAJOR issue is identified (Figure 2 percentage arithmetic error: 2.1% should be 1.1%). The ~95% import error claim remains an unsourced approximation. All other numbers are internally consistent and verified against source files.

---

## FATAL Issues

None.

---

## MAJOR Issues

**MAJOR-N1: Arithmetic error in Figure 2 stacked breakdown description (Section 5.1)**

The paper states: "2.1% have patterns but fail AST parsing"

Actual arithmetic: (310 − 204) / 10,000 = 106 / 10,000 = 1.06% ≈ **1.1%**, not 2.1%.

The 2.1% figure appears to be a transcription or rounding error. The sum still works out to 100% because the error compensates against the other categories, but the individual figure is wrong and will be caught by any reviewer who performs the arithmetic.

- **Location:** Section 5.1, Figure 2 description paragraph; also Figure 2 caption in Figure Captions section
- **Fix:** Change "2.1% have patterns but fail AST parsing" to "1.1% have patterns but fail AST parsing" in both locations
- **Source:** 310 − 204 = 106 files; 106/10,000 = 1.06% → rounds to 1.1%

---

## Human Review Notes

| Location | Note | Severity |
|----------|------|----------|
| Section 5.1, Section 7 | "~95%" import error fraction is not present in any released source file (results.json, 04_validation.md). Either quantify this from the error_type_distribution figure data or soften to "large majority" | MINOR |
| Section 5.3 | "ruling out file size as a confound" — n=10 executable files is insufficient statistical power for this inference. R1 review flagged this; confirm whether the revision agent softened this language | MINOR |
| Section 7 (Conclusion) | Uses "import isolation rejects ~95% of AST-parseable doctests at the ModuleNotFoundError stage" — this is the same unsourced figure as above, repeated in the Conclusion where it is most visible to readers | MINOR |

---

## Summary for Revision Agent

### Priority Fixes for R2

1. **[MAJOR-N1 — MUST FIX]** Correct "2.1% have patterns but fail AST parsing" to "1.1%" in:
   - Section 5.1 Figure 2 description paragraph
   - Figure 2 caption in the Figure Captions section
   - Arithmetic: (310 − 204) / 10,000 = 106 / 10,000 = 1.06% ≈ 1.1%

2. **[MINOR — SHOULD FIX]** Replace "~95%" in Section 5.1 table and Section 7 (Conclusion) with "a large majority" or source the figure from the error_type_distribution data. The current figure is an approximation not verifiable from released artifacts.

3. **[MINOR — CONFIRM]** Verify Section 5.3 "ruling out file size as a confound" was softened in R1 revision to account for n=10 sample size. If not, add qualifier: "is consistent with file size not being a confound, though the n=10 executable file sample is too small for definitive statistical inference."

### R1 Fix Status: VERIFIED

All four MAJOR issues from R1 are confirmed fixed:
- MAJOR-A1: "31×" (not "30×") — confirmed throughout
- MAJOR-C1: "First systematic measurement" scoping — confirmed in Section 1.4
- MAJOR-C2: "feasible at scale" (not "production-ready") — confirmed in Section 6.1/6.3
- MAJOR-E1: H-E1 correctly positioned as design/future work — confirmed in Section 5.2

### Assessment

The paper's core numbers are clean. Only one arithmetic error was found (Figure 2: 2.1% vs. 1.1%), and it is straightforward to fix. After fixing MAJOR-N1 and the two MINOR notes, the paper is numerically sound and ready for submission.
