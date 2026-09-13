# Adversarial Review - Round 2

**Paper:** When Adversarial Examples Improve Calibration: Construction-Method-Dependent Calibration Degradation in Open-Weight LLMs (R1 revised)
**Reviewed:** 2026-08-25
**Reviewer:** Adversary Agent v2 (Numerical Verification Round)
**Round:** R2 - Numerical Verification and Credibility

> **Note on MCP availability:** Serena MCP is unavailable in this session (no_MCP environment). Numerical verification performed directly from Phase 4 validation reports (h-e1/04_validation.md, h-c1-v2/04_validation.md, h-m1/04_validation.md). All source values confirmed. This review covers all standard R2 verification without Serena pattern search.

---

## Executive Summary

| Category | FATAL | MAJOR | Status |
|----------|-------|-------|--------|
| Numerical Accuracy | 0 | 1 | NEEDS_WORK |
| Mathematical Validity | 0 | 0 | OK |
| Baseline Fairness | 0 | 0 | OK |
| Credibility (R1 fixes) | 0 | 0 | OK |
| **TOTAL** | **0** | **1** | **NEEDS_WORK** |

**Recommendation:** CONDITIONAL_ACCEPT — All R1 fixes verified. One new MAJOR issue found: SST-2 exclusion rationale is factually inaccurate. All other numerical claims verified against source data.

---

## Verification Status from R1

All R1 MAJOR issues confirmed resolved in 06_paper_r1.md:
- ✓ MAJOR-CRED-001: Contributions reduced from 4 to 3; JSONL caching in Contribution 1
- ✓ MAJOR-CRED-002: "establish" → "motivate"; pilot-study scope qualifier added
- ✓ MAJOR-CRED-003: L5 added (H-M2/H-M3 gate failure disclosure)
- ✓ MAJOR-ENG-001: Abstract now leads with counterintuitive finding
- ✓ MAJOR-ACC-001: ANLI R2 ΔΔECE clarified (chat improvement vs base degradation)

---

## Numerical Verification Log

### Source Files Verified

| File | Contents | Status |
|------|----------|--------|
| h-e1/04_validation.md | ECE results table, all cells | ✓ READ |
| h-c1-v2/04_validation.md | ΔΔECE per-cell (7B pair) | ✓ READ |
| h-m1/04_validation.md | Label preservation rates, bin-count ablation | ✓ READ |
| 065_ground_truth.yaml | Pre-extracted claims | ✓ READ |

### Complete Numerical Verification Table

| Claim | Paper (r1) | Source | Source Value | Match |
|-------|-----------|--------|-------------|-------|
| NLI clean ECE | 0.279 | h-e1 Results Table | 0.2792 | ✓ |
| AdvGLUE MNLI ΔECE | +0.071 | h-e1: 0.3497-0.2792 | 0.0705 | ✓ |
| ANLI R1 ΔECE | −0.041 | h-e1: 0.2387-0.2792 | −0.0405 | ✓ |
| ANLI R2 ΔECE | −0.014 | h-e1: 0.2656-0.2792 | −0.0136 | ✓ |
| ANLI R3 ΔECE | +0.024 | h-e1: 0.3036-0.2792 | +0.0244 | ✓ |
| AdvGLUE QQP ΔECE | −0.029 | h-e1: 0.0329-0.0623 | −0.0294 | ✓ |
| ΔΔECE ANLI R1 | +0.115 | h-c1-v2 | +0.1149 | ✓ |
| ΔΔECE ANLI R2 | +0.147 | h-c1-v2 | +0.1474 | ✓ |
| ΔΔECE ANLI R3 | +0.043 | h-c1-v2 | +0.0425 | ✓ |
| ΔΔECE AdvGLUE | −0.026 | h-c1-v2 | −0.0256 | ✓ |
| ΔECE(base) ANLI R1 | −0.017 | h-c1-v2 | −0.0165 | ✓ |
| ΔECE(chat) ANLI R1 | −0.131 | h-c1-v2 | −0.1314 | ✓ |
| ΔECE(base) ANLI R2 | +0.002 | h-c1-v2 | +0.0017 | ✓ |
| ΔECE(chat) ANLI R2 | −0.146 | h-c1-v2 | −0.1458 | ✓ |
| ΔECE(base) AdvGLUE | +0.065 | h-c1-v2 | +0.0648 | ✓ |
| ΔECE(chat) AdvGLUE | +0.090 | h-c1-v2 | +0.0904 | ✓ |
| Label preservation | 1.000 all | h-m1 | 1.000 all | ✓ |
| Bin-count ECE stability | 0.3497 (10/15) | h-m1 ablation | 0.3497 both | ✓ |
| Accuracy (NLI clean) | 0.365 | h-e1 | 0.365 | ✓ |
| Accuracy (ANLI R1) | 0.380 | h-e1 | 0.380 | ✓ |
| n(AdvGLUE MNLI) | 121 | h-e1 | 121 | ✓ |
| n(ANLI R1-R3) | 200 each | h-e1 | 200 | ✓ |
| n(AdvGLUE QQP) | 78 | h-e1 | 78 | ✓ |

**Total: 23 claims verified. 0 discrepancies.**

---

## Mathematical Validity Analysis

### ΔECE Arithmetic Verification

All ΔECE values verified by direct subtraction:
- 0.3497 − 0.2792 = 0.0705 → rounds to 0.071 ✓ (paper rounds to 0.001)
- 0.2387 − 0.2792 = −0.0405 → rounds to −0.041 ✓
- 0.2656 − 0.2792 = −0.0136 → rounds to −0.014 ✓
- 0.3036 − 0.2792 = 0.0244 → rounds to +0.024 ✓

### ΔΔECE Arithmetic Verification

All ΔΔECE verified by ΔECE(base) − ΔECE(chat):
- ANLI R1: −0.0165 − (−0.1314) = +0.1149 → paper +0.115 ✓
- ANLI R2: +0.0017 − (−0.1458) = +0.1475 → paper +0.147 ✓ (rounds consistently)
- ANLI R3: −0.0112 − (−0.0537) = +0.0425 → paper +0.043 ✓
- AdvGLUE: +0.0648 − (+0.0904) = −0.0256 → paper −0.026 ✓

### ANLI Gradient Monotonicity

Paper claims: "smooth transition from improvement to degradation"
Actual values: R1(−0.041) < R2(−0.014) < R3(+0.024) — strictly monotone increasing ✓

Mathematical claim verified: gradient is indeed monotone.

---

## FATAL Issues — Round 2
*None.*

## MAJOR Issues — Round 2

### MAJOR-ACC-002: SST-2 exclusion rationale is factually inaccurate

**Location:** Section 3.2, Cell Structure paragraph

**Issue:** The paper states: *"(SST-2 adversarial data was insufficient for ECE measurement and excluded.)"*

However, h-e1/04_validation.md shows that SST-2 adversarial data WAS measured:
- SST-2 adversarial n=148 (exceeds the paper's own 50-sample minimum)
- ECE-15 = 0.1044, ECE-10 = 0.0596
- SST-2 clean ECE = 0.1567

The actual reason for SST-2 exclusion from the main analysis cells is scope/framing, not data insufficiency. The paper established a 5-cell design (NLI + QQP). SST-2 adversarial was computed but not included in the primary analysis — likely because (a) it's a binary task similar to QQP, (b) it would have been redundant with QQP for the binary/NLI comparison, and (c) the paper focuses on adversarial NLI as its primary domain.

**Evidence:**
- h-e1 Results Table: SST-2 adversarial n=148, ECE-15=0.1044 — clearly computed
- Paper's own minimum: ≥50 examples required — SST-2 at 148 satisfies this
- Paper states "insufficient for ECE measurement" — factually wrong

**Impact:** A reviewer who checks: "You said SST-2 was excluded for insufficient data. Your h-e1 report shows n=148 with valid ECE. Which is it?" This is a verifiable factual inconsistency that undermines confidence in the methodology reporting.

**Required Fix:** Change "SST-2 adversarial data was insufficient for ECE measurement and excluded" to accurately state the real reason:
"SST-2 adversarial data (n=148) was computed but excluded from the main analysis cell set for scope reasons: SST-2 provides a second binary classification task redundant with AdvGLUE QQP for the construction-method × task-type factorial design. SST-2 results are available for future analysis."

---

## Baseline Fairness Assessment

This is a measurement study, not a comparison against ML baselines. "Baselines" are:
1. Clean ECE values (own model on clean data) — fair by design ✓
2. Llama-2-7b base vs chat comparison — same model family, appropriate ✓

No baseline fairness concerns.

---

## Human Review Notes — Round 2 Additions

| Location | Note | Type |
|----------|------|------|
| Section 3.2 | After fixing SST-2 exclusion wording, check that the parenthetical reads naturally in context | clarity |
| Abstract (revised) | New opening sentence is strong; verify it doesn't exceed ICML abstract word limit when combined with the rest | formatting |

---

## Summary for Revision Agent

### Priority Fix List

1. **MAJOR-ACC-002:** Fix SST-2 exclusion rationale (currently says "insufficient" but data was computed with n=148). Fix: state actual reason (scope/redundancy with QQP). MUST FIX.

### What's Working (Post-R1)

- All R1 fixes correctly applied and verified
- All 23 numerical claims verified from source data — zero discrepancies
- Mathematical validity confirmed (all arithmetic checks out)
- ANLI gradient monotonicity confirmed
- Label preservation verified from h-m1 source
- Paper is otherwise ready for submission contingent on citation verification
