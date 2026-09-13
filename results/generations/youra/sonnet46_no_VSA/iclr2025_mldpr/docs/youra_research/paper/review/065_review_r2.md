# Adversarial Review — Round 2 (R2)
**Paper**: Community Breadth Diversity Does Not Predict Benchmark Displacement (R1 Revision)  
**Round**: R2 — Numerical Verification and Credibility  
**Personas**: Accuracy Checker · Skeptical Expert  
**MCP Verification**: Serena pattern search + direct experiment_results.json verification  
**Date**: 2026-08-03

---

## Serena MCP Verification Log

All numerical claims verified against raw pipeline outputs:

| Search Target | Source File | Pattern | Result |
|---------------|-------------|---------|--------|
| HR value | `h-m1/experiment_results.json` | `"HR"` | 1.0056129850784017 ✅ |
| p-value | `h-m1/experiment_results.json` | `"p_value"` | 0.9494719219406311 ✅ |
| CI lower | `h-m1/experiment_results.json` | `"CI_lower"` | 0.8457060914824751 ✅ |
| CI upper | `h-m1/experiment_results.json` | `"CI_upper"` | 1.1957552226987227 ✅ |
| LRT stat | `h-m1/experiment_results.json` | `"lrt_stat"` | 0.00401574954867101 ✅ |
| Concordance | `h-m1/experiment_results.json` | `"concordance_M1"` | 0.7362932604735883 ✅ |
| M0 log-lik | `h-m1/experiment_results.json` | `"M0_log_likelihood"` | -750.7334857422607 ✅ |
| M1 log-lik | `h-m1/experiment_results.json` | `"M1_log_likelihood"` | -750.7314778674863 ✅ |
| abs_effect | `h-m1/experiment_results.json` | `"abs_effect"` | 0.005612985078401689 ✅ |
| Panel rows | `h-m1/code/experiment.log` | `"258 rows"` | 258 ✅ |
| NaN dropped | `h-m1/code/experiment.log` | `"Dropped 87"` | 87 ✅ |
| penalizer | `h-m1/04_validation.md` | `"penalizer: 0.1"` | 0.1 ✅ |
| G0 | `h-e1/04_validation.md` | `"G0_coverage"` | 0.862 ✅ |
| G1 partial r² | `h-e1/04_validation.md` | `"G1_partial_r2"` | 0.6053 ✅ |
| G2 partial r² | `h-e1/04_validation.md` | `"G2_partial_r2"` | 0.9751 ✅ |
| G3 std | `h-e1/04_validation.md` | `"G3_std"` | 0.2462 ✅ |
| G4 max VIF | `h-e1/04_validation.md` | `"G4_max_vif"` | 2.14 ✅ |

**Mathematical verification:**
- LRT stat = −2 × (M0 − M1) = −2 × (−750.7335 − −750.7315) = 0.0040 ✅
- ΔlogL = M1 − M0 = −750.7315 − −750.7335 = 0.0020 ✅
- chi2.sf(0.0040, df=1) = 0.9495 ✅ (verified computationally)
- |HR−1| precise = |1.0056 − 1| = 0.0056 ✅

---

## Ground Truth Verification Table

| Claim | Paper (R1) | Ground Truth (raw) | Match |
|-------|------------|--------------------|-------|
| HR | 1.006 | 1.0056 | ✅ (rounded) |
| 95% CI | [0.846, 1.196] | [0.8457, 1.1958] | ✅ (rounded) |
| LRT stat | 0.0040 | 0.00401574... | ✅ |
| LRT p | 0.9495 | 0.9494719... | ✅ |
| ΔlogL | 0.0020 | 0.0020079... | ✅ |
| Concordance | 0.7363 | 0.7362932... | ✅ |
| \|HR−1\| displayed | 0.006 | 0.0056 | ⚠️ MINOR inconsistency |
| "17× below threshold" | 17× | 0.10/0.0056=17.9x OR 0.10/0.006=16.7x | ⚠️ MAJOR-004 |
| Rows used | 258 | 258 | ✅ |
| NaN dropped | 87 | 87 | ✅ |
| EPV ≈ 86 | ≈86 | Not directly in JSON; consistent with 258 rows, ~86 events | ✅ (plausible) |
| G0 | 0.862 | 0.862 | ✅ |
| G1 | 0.605 | 0.6053 | ✅ |
| G2 | 0.975 | 0.9751 | ✅ |
| G3 std | 0.246 | 0.2462 | ✅ |
| G4 max VIF | 2.14 | 2.14 | ✅ |

---

## Executive Summary

| Severity | Count | Description |
|----------|-------|-------------|
| FATAL | 0 | None |
| MAJOR | 1 | MAJOR-004: |HR-1| / "17×" multiplier inconsistency |
| MINOR | 2 | See Human Review Notes |

**All core quantitative claims verified against raw experiment_results.json. One MAJOR numerical precision inconsistency found.**

---

## FATAL Issues

**None.**

---

## MAJOR Issues

### MAJOR-004 (Accuracy Checker): |HR−1| Display vs. "17×" Multiplier Inconsistency

**Location**: Section 5.2 Table 2, and Table 2 row "|HR−1| = 0.006 ≥ 0.10 ❌ FAIL (17× below)"

**Issue**: The paper displays `|HR−1| = 0.006` (rounded from 0.0056 actual) in Table 2, then claims this is "17× below threshold." The two numbers are inconsistent:

- If using displayed 0.006: 0.10 / 0.006 = **16.7×** (rounds to "17×" — marginal)
- If using precise 0.0056: 0.10 / 0.0056 = **17.9×** (rounds to "18×")

The "17×" claim implicitly uses the precise 0.0056 but the table displays 0.006, creating a subtle inconsistency. A reviewer checking arithmetic will notice: "0.10 / 0.006 = 16.7, not 17."

**Evidence**: `experiment_results.json`: `"abs_effect": 0.005612985078401689`; `experiment.log` line 9: `|HR-1|=0.0056`.

**Required fix**: Use the 3-decimal precise value `|HR−1| = 0.0056` in Table 2 (consistent with JSON and log), then claim "18× below threshold" (0.10/0.0056 = 17.9×, rounds to ~18×). **OR** keep `|HR−1| = 0.006` and say "~17× below." The first option (use precise 0.0056) is preferred for scientific precision.

**Severity rationale**: A reviewer performing spot-checks will compute 0.10/0.006 = 16.7 and question whether the "17×" is sloppy rounding throughout. One consistent precision choice eliminates this attack surface entirely.

---

## Mathematical Validity Analysis

### Check 1: LRT Calculation
ΔlogL = M1 − M0 = −750.7315 − (−750.7335) = 0.0020 ✅  
LRT stat = 2 × ΔlogL = 0.0040 ✅  
chi²(0.0040, df=1) = 0.9495 ✅ — verified independently with scipy.

### Check 2: CI Plausibility
HR = 1.006, CI = [0.846, 1.196]. Width = 0.350. For a single predictor at n=258, this CI width is plausible. The CI symmetrically straddles 1.0 (0.154 below, 0.190 above — slight asymmetry is expected on log scale). ✅

### Check 3: EPV Calculation
258 complete-case rows; 1 predictor in M1. The paper states EPV ≈ 86, consistent with ~86 events (displacements) in the 258-row panel. This cannot be verified from experiment_results.json alone (EPV requires event count), but is consistent with all reported statistics. ✅ (stated, not independently computed).

### Check 4: Penalizer Effect Plausibility
penalizer=0.1 with n=258 and HR=1.006. L2 regularization at 0.1 strength should have minimal effect on a predictor with |β|≈0.006 (very small effect estimate). The L5 limitation added in R1 is appropriate; the regularization is unlikely to have caused the null (the effect is too small to shrink meaningfully further), but sensitivity analysis would formally confirm this. ✅ (L5 limitation adequate).

### Check 5: "17× below threshold" precision
0.10 / 0.006 (displayed) = 16.7 → paper says "17×" — **INCONSISTENT** (MAJOR-004 above).  
0.10 / 0.0056 (precise) = 17.9 → rounds to "18×" — also inconsistent with "17×."  
Fix: use 0.0056 and "~18×" for full consistency.

---

## Baseline Fairness Assessment

This paper has no ML performance baseline comparison — it is a survival analysis null result study. The relevant "baselines" are:
1. The null model M0 (LRT comparison is the standard Cox test — fair ✅)
2. The prior directional signal (R1 fixed the conflation — now properly described as different construct ✅)
3. Cited population-level Ott et al. result — correctly distinguished as different analysis granularity ✅

**No baseline fairness issues.**

---

## Credibility Assessment (Skeptical Expert)

### Novelty Claims Post-R1 Revision

After R1 fixes, all novelty claims are appropriately scoped:
- "most statistically powered test to date of community breadth *as operationalized by paper submission count*" — qualified correctly ✅
- "5-gate FAIL FAST protocol is a reusable methodological contribution" — modest and defensible ✅
- "score velocity and institutional diversity remain untested at full power" — appropriately deferred ✅

### Unverified References (Ground Truth C3)

Ground truth flags four unverified references. This is a MAJOR submission risk but out of scope for automated fix:
- `ott2022benchmark`: Could not be verified via Semantic Scholar during pipeline
- `paullada2021data`: Could not be verified via Semantic Scholar during pipeline
- `rogers2003diffusion`: Classic book — likely correct but edition/publisher unconfirmed
- `iclr2025benchmarking`: Workshop proceedings — exact name/URL unconfirmed

**Classified as MINOR in this review** (requires human lookup; cannot be auto-fixed). Added to human_review_notes as HIGH priority.

### Remaining Attack Surfaces for Real Reviewers

1. EPV ≈ 86 — stated but not directly computed from event count. Reviewers may ask for exact event count in the 258-row panel. Consider adding exact N_events to Table 2.
2. Complete-case analysis (87 NaN dropped) — NaN pattern not investigated. Addressed in L2 but no analysis of whether missing-at-random assumption holds.
3. Log-rank p-value for KM Q1 vs Q4 (P3) — stated as "visual null" but no numeric p-value. Weakens P3 evidence.

---

## Summary for Revision Agent (R2)

**Fix MAJOR-004**: Table 2 row `|HR−1|` — change displayed value from `0.006` to `0.0056`, and change "17× below" to "~18× below." This creates full numerical consistency with experiment_results.json.

**Collect MINOR issues** (do NOT auto-fix):
- M6 (HIGH priority): Unverified references (ott2022benchmark, paullada2021data, rogers2003diffusion, iclr2025benchmarking) — requires manual lookup before submission
- M7: P3 KM analysis has no numeric log-rank p-value — consider adding from experiment log if available
