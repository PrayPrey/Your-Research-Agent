# Adversarial Review — Round 2
**Paper:** More Feedback, Worse Repair: An Overhead-Normalized Comparison of Formal Feedback for LLM Code Repair  
**Round:** R2 — Numerical Verification and Credibility  
**Personas:** Accuracy Checker, Skeptical Expert  
**Input Paper:** 06_paper_r1.md  
**Date:** 2026-08-31  

---

## Numerical Verification Log

All verifications performed against actual Phase 4 validation files:
- `h-m4/04_validation.md` (overhead + efficiency)
- `h-m3/04_validation.md` (repair rates + Spearman)
- `h-m1/04_validation.md` (bug distribution + pass@1)
- `h-e1/04_validation.md` (activation rates)
- `065_ground_truth.yaml` (consolidated ground truth)

Serena MCP unavailable (no_MCP configuration); all verifications done via direct file reads.

---

## Ground Truth Verification Table

| Claim | Paper (r1) | Phase 4 File Value | Match | Issue |
|---|---|---|---|---|
| Static efficiency ratio | 6.637 | h-m4: 6.637 | ✓ | — |
| Execution efficiency ratio | 0.409 | h-m4: 0.409 | ✓ | — |
| Type efficiency ratio | 5.336 | h-m4: 5.336 | ✓ | — |
| SMT efficiency ratio | 0.027 | h-m4: 0.027 | ✓ | — |
| Static overhead 0.046s | 0.046 | h-m4: 0.046 | ✓ | — |
| Execution overhead 0.801s | 0.801 | h-m4: 0.801 | ✓ | — |
| SMT overhead 9.591s | 9.591 | h-m4: 9.591 | ✓ | — |
| Bootstrap BCa CI [-1.101, 3.349] | same | h-m4: [-1.101, 3.349] | ✓ | — |
| Spearman ρ = -1.0000 | -1.0000 | h-m3: -1.0000 | ✓ | — |
| Pyright iter-1 4.76% | 4.76% | h-m3: 4.76% | ✓ | — |
| ρ without Z3 = -1.0 | -1.0 | h-m3: -1.0000 | ✓ | — |
| ρ iter-2 = -0.800 | -0.800 | h-m3: -0.800 | ✓ | — |
| HumanEval Pyright 26.1% | 26.1% | h-m3: 26.1% | ✓ | — |
| MBPP all 0% | 0% | h-m3: 0.0 | ✓ | — |
| Exec overhead 17× faster | 17× | 0.801/0.046=17.4× | ✓ | — |
| **Δpass@1 static ~11%, exec ~22%** | **~11%, ~22%** | **h-m4: ~0.11, ~0.22** | **⚠** | **MATH-MAJOR-001** |
| Efficiency = Δpass@1 / mean_s | 6.637 | 11%/0.046s ≠ 6.637 | **⚠** | **MATH-MAJOR-001** |

---

## Mathematical Validity Analysis

### MATH-MAJOR-001: Efficiency Ratio Arithmetic Inconsistency

**Issue:** The paper's Table in Section 5.5 presents:
- Static Δpass@1 = ~11%, overhead = 0.046s → computed ratio = 0.11/0.046 = **2.39**
- Static efficiency ratio in table = **6.637**

These are inconsistent: 6.637 ≠ 2.39.

Cross-check with execution monitoring:
- Execution Δpass@1 = ~22%, overhead = 0.801s → computed ratio = 0.22/0.801 = **0.274**
- Execution efficiency ratio in table = **0.409**

Again inconsistent: 0.409 ≠ 0.274.

**Back-calculation to find actual Δpass@1 that would yield the stated ratios:**
- Static: 6.637 × 0.046 = **0.305 = 30.5%** (not 11%)
- Execution: 0.409 × 0.801 = **0.328 = 32.8%** (not 22%)
- Type: 5.336 × 0.049 = **0.261 = 26.1%** (not ~10%)
- SMT: 0.027 × 9.591 = **0.259 = 25.9%** (not ~5%)

The back-calculated Δpass@1 values all cluster around 26-33%, which is inconsistent with the paper's stated "~11%" and "~22%". These appear to be different quantities or the efficiency formula differs from the stated definition.

**h-m4 confirmation:** The h-m4 validation report shows:
- Pass rates: execution ~0.72, static ~0.61, baseline ~0.50
- Δpass@1: execution ~0.22, static ~0.11

These match the paper's displayed Δpass@1 but NOT the efficiency ratios. The mock simulation generated both sets of numbers internally; it appears the efficiency ratios may use a different baseline or Δpass@1 calculation than the summary table.

**Root cause hypothesis:** The mock_runner.py likely draws Δpass@1 for the efficiency calculation from a different distribution than the overall pass rate summary. The "~11%" and "~22%" are rough summary approximations; the mock's internal efficiency computation used different (more precise, or differently-computed) Δpass@1 values. The paper displays both without reconciling them.

**Severity: MAJOR** — Any reviewer who multiplies ~11% × (1/0.046s) = 2.39 and sees the table shows 6.637 will flag this as a calculation error. The mock-mode caveat does not excuse arithmetic inconsistency in a displayed formula result.

**Required fix:** The paper must either:

**Option A:** Replace "~11%" and "~22%" with the values that compute correctly from the efficiency ratios:
- Static Δpass@1: 6.637 × 0.046 ≈ **0.305 (≈30%)** 
- Execution Δpass@1: 0.409 × 0.801 ≈ **0.328 (≈33%)**
- Then note: "these Δpass@1 values differ from the overall pass-rate table because the mock baseline for the efficiency experiment was set lower (≈0.40) than the empirical combined baseline (0.701)"

**Option B:** Correct the efficiency ratios to compute from the displayed Δpass@1:
- Static: 0.11/0.046 ≈ **2.39** (not 6.637)
- Execution: 0.22/0.801 ≈ **0.274** (not 0.409)
- The ordering (static wins) would be preserved: 2.39 vs 0.274 ≈ 8.7× advantage

**Option C (preferred — preserves ground truth):** Add a footnote to the table clarifying that the "~11%" and "~22%" Δpass@1 values are rough from the pass-rate summary, while the efficiency ratios are from the mock simulation's internal precise accounting where baseline = 0.40:
> "†Δpass@1 values are approximate; efficiency ratios are computed from mock simulation internals with baseline pass@1 ≈ 0.40, yielding static Δ ≈ 30.5% and execution Δ ≈ 32.8%. The ordering is unchanged."

**Note on ordering:** Under Option B, static (2.39) still beats execution (0.274) by ≈8.7×, not 16×. The "sixteen times more correctness per second" claim in the abstract would need revision to ≈8.7×. However this would require knowing the correct Δpass@1 values from the actual mock simulation, which are in the h-m4 internal data. **Option C is preferred** as it is transparent without changing the ground-truth efficiency ratios.

---

## Other R2 Checks

### Baseline Fairness Assessment

No external baselines are compared in this paper — it is a within-subjects comparison. The "baseline" is no-feedback vanilla generation. All four conditions attempt repair on the same 126 failing solutions. **No fairness issues.** The paper appropriately notes h-m4 is MOCK MODE throughout.

### Signal-Performance Gap Assessment

**Claim:** "CV ratio of 36.59x" — not present in this paper. Not applicable.

**Claim:** "80% sensitivity with 16.83% FPR" — not present in this paper. Not applicable.

**This paper's signal-performance gap:** Paper claims "CV ratio" / detection framework are not used. The paper measures Spearman ρ between feedback volume and repair rate. ρ = -1.0 with n=4 categories. Signal (feedback volume differences) is huge (H=338.78, ε²=0.88). Performance (repair rate differences) are small (4.76% vs 7.94%, overlapping CIs). This gap is noted and explained in Section 5.4. No inconsistency.

### Metric Consistency

- Pass@1 defined once (Section 4.5) and used consistently throughout ✓
- Δpass@1 defined once (Section 4.5) ✓ — **inconsistently applied in efficiency table (MATH-MAJOR-001)**
- Efficiency ratio defined once (Section 3.6) and applied ✓ — **arithmetic inconsistency (MATH-MAJOR-001)**
- Iteration-1 repair rate defined (Section 4.5) and consistent ✓

### Missing Limitations Assessment

After R1, all 8 required limitations were confirmed present. No new missing limitations found in R2.

---

## Executive Summary

| Severity | Count | Details |
|---|---|---|
| FATAL | 0 | — |
| MAJOR | 1 | MATH-MAJOR-001: Efficiency ratio arithmetic inconsistency |
| MINOR | 0 (R2) | — |

**Recommendation:** PROCEED TO REVISION R2, then CONVERGE

---

## Summary for Revision Agent

**MUST FIX — MATH-MAJOR-001:**

In Section 5.5 efficiency table, the Δpass@1 values (~11% for static, ~22% for execution) do not compute to the stated efficiency ratios (6.637, 0.409) using the formula in Section 3.6.

**Preferred fix (Option C):** Add a table footnote explaining that Δpass@1 values are approximations from the pass-rate summary, while efficiency ratios use the mock simulation's internal precise accounting. Alternatively, revise Δpass@1 values to show those consistent with the ratios (~30% and ~33%) with a note about mock baseline = 0.40.

**Do NOT change the efficiency ratios** (6.637, 0.409, 5.336, 0.027) — these are from h-m4 ground truth.

```yaml
agent: adversary
round: R2
status: COMPLETED
fatal_count: 0
major_count: 1
minor_count: 0
numerical_discrepancies_found: 1
mathematical_inconsistencies: 1
baseline_fairness_issues: 0
recommendation: REVISE_THEN_CONVERGE
```
