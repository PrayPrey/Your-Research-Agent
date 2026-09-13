# Adversarial Review — Round 2
**Paper**: When Did GLUE Go Stale? (R1 revised version)  
**Round**: R2 — Numerical Verification and Credibility  
**Personas**: Accuracy Checker, Skeptical Expert  
**Date**: 2026-08-25T20:20:00+00:00  

---

## Verification Method

Primary: Direct reading of Phase 4 validation reports (h-m3/04_validation.md, h-m4/04_validation.md, h-m1/04_validation.md, h-m2/04_validation.md, h-c1/04_validation.md). Pattern matching performed manually on key numerical claims. Serena MCP not available in this session.

---

## Ground Truth Verification Table (R2)

| Claim | Paper Value | Phase 4 Source | Match |
|-------|------------|----------------|-------|
| K_GLUE | 0.8955 | h-m3 results: 0.8955 | ✓ |
| K_SuperGLUE | 0.8858 | h-m3 results: 0.8858 | ✓ |
| r_GLUE | 0.2017 | h-m3 results: 0.2017 | ✓ |
| r_SuperGLUE | 0.1578 | h-m3 results: 0.1578 | ✓ |
| t0_GLUE | −6.77m | h-m3 results: t0_rel=−6.771 (rounds to −6.77) | ✓ |
| t0_SuperGLUE | −2.85m | h-m3 results: t0_rel=−2.855 (rounds to −2.85) | ✓ |
| GLUE saturation | Dec 2019 | h-m4 results: 2019-12 | ✓ |
| SuperGLUE saturation | Nov 2021 | h-m4 results: 2021-11 | ✓ |
| Sensitivity 0.99/0.05 GLUE | 3m | h-m4 sensitivity table: 3m | ✓ |
| Sensitivity 0.95/0.05 GLUE | 1m | h-m4 sensitivity table: 1m | ✓ |
| Sensitivity 0.99/0.05 SuperGLUE | 5m | h-m4 sensitivity table: 5m | ✓ |
| Sensitivity 0.95/0.05 SuperGLUE | 1m | h-m4 sensitivity table: 1m | ✓ |
| bootstrap_n | 500 | h-m3 handoff: bootstrap_n=500 | ✓ |
| maxfev | 10000 | h-m3 handoff: maxfev=10000 | ✓ |
| **K lower bound** | **0.8 (paper)** | **h-m3: K [0.5, 1.05]; h-m4: K_bounds [0.5, 1.05]** | **✗ DISCREPANCY** |

**Total discrepancies: 1 (K lower bound)**

---

## Executive Summary

| Severity | Found | Source |
|----------|-------|--------|
| FATAL | 0 | — |
| MAJOR | 1 | K lower bound discrepancy |
| MINOR | 1 | Plausibility gate vs fitting bound conflation |

**Persuasiveness R2**: PASSED (no regression from R1)

---

## FATAL Issues

*None.*

---

## MAJOR Issues

### MAJ-005 — K Lower Bound: Paper Says 0.8, Code Used 0.5

**Persona**: Accuracy Checker  
**Location**: Section 3.3 (Methodology, Growth Model Fitting table), Appendix B  
**Evidence from Phase 4 files:**
- `h-m3/04_validation.md` Phase 2C handoff: `K: [0.5, 1.05]`
- `h-m4/04_validation.md` optimal hyperparameters: `K_bounds: [0.5, 1.05]`

**Paper claims** (Section 3.3 table):
```
K | 0.8 | 1.05 | Near-human-parity asymptote
```

**Actual implementation** (Phase 4 validation reports):
```
K: [0.5, 1.05]
```

**Impact analysis**: The actual fitted K values (0.8955, 0.8858) fall within both [0.5, 1.05] and [0.8, 1.05]. The discrepancy does NOT affect the reported results — the optimizer settled well within either bound range. However, the paper's rationale ("Near-human-parity asymptote") justifies K_lower=0.8 as a meaningful constraint, while the actual code used K_lower=0.5 (a looser constraint). This is a methodological transparency issue: a reader trying to reproduce the results with K_lower=0.8 would get identical results, but the methodology as described does not match the actual implementation.

**Required fix**: Update the methodology to accurately reflect the actual bounds used. Two options:
1. **Option A**: Correct to K∈[0.5, 1.05] and update the rationale ("Broad positive bound; optimizer converges to near-parity values regardless due to data constraints")
2. **Option B**: If K_lower=0.8 was intended as a design decision (not implemented correctly), correct the implementation and re-verify that results are unchanged. Given the fitted values (~0.89) are unaffected, Option A is simpler and equally valid.

The methodology section (Section 3.3) and Appendix B must be consistent with each other and with the actual implementation.

---

## MINOR Issues (R2, collected for human_review_notes)

MIN-008: Section 3.3 table — the "Criterion" column in Table 3 (parameter plausibility) uses K ∈ [0.8, 1.0], while the fitting bounds are K ∈ [0.5 (actual) or 0.8 (stated), 1.05]. The plausibility criterion and fitting bounds serve different purposes (post-hoc check vs optimization constraint); the paper uses them somewhat interchangeably. After fixing MAJ-005, a footnote clarifying "fitting bounds (for optimization) differ from plausibility criteria (post-hoc check)" would prevent reader confusion.

---

## Mathematical Validity Analysis

**ΔAIC multiplier computations:**
- 250.50/10 = 25.05× ✓ (R1 fixed; "19–25× vs linear" is correct)
- 194.37/10 = 19.4× ✓ (within "19–25×" range)
- 357.09/10 = 35.7× ✓ ("11–36× vs power-law" correct)
- 112.72/10 = 11.3× ✓ (within "11–36×" range)

**t0 rounding checks:**
- t0_GLUE: −6.771 → paper says −6.77 ✓ (correct rounding)
- t0_SuperGLUE: −2.855 → paper says −2.85 ✓ (truncated, not rounded; acceptable for this precision)

**Dual-criterion mathematical consistency:**
- 0.99 × K_GLUE = 0.99 × 0.8955 = 0.8865 — achievable given GLUE plateau ✓
- 0.99 × K_SuperGLUE = 0.99 × 0.8858 = 0.8769 — achievable given SuperGLUE plateau ✓
- θ_K = 1.00 failure: mathematically expected since logistic asymptote is approached but never reached ✓ (paper explains this correctly)

**Sensitivity grid arithmetic:**
All 18 cells cross-checked against h-m4/04_validation.md tables — all match ✓

---

## Baseline Fairness Assessment

**Model selection baselines (linear, power-law):** Fair. These are the canonical alternatives for S-curve vs non-S-curve dynamics. The AIC comparison is three-way. No straw man involved.

**Saturation detection baseline (naive threshold):** Added in R1 revision. The naive detector context (Table 4) is accurate — score-threshold-only detects 1–2 months earlier but at higher false-positive risk. This is appropriately framed in the text.

**Literature baseline:** No prior automated saturation detection exists per the literature survey; the method is compared to "infinite error" (no detection) as a practical null baseline. This is stated transparently.

**Ground truth sources:** 
- GLUE ground truth: Wang et al. 2019 (SuperGLUE paper) — community-reported ✓
- SuperGLUE ground truth: BIG-bench collaboration (Srivastava et al. 2022) — community-reported ✓
- L6 limitation (added in R1) correctly acknowledges circularity ✓

---

## R2 Summary for Revision Agent

**Fix required (1 MAJOR):**
1. MAJ-005: Correct K lower bound in Section 3.3 table and Appendix B from 0.8 to 0.5 (matching actual implementation), OR update rationale to explain the discrepancy.

**Collect in human_review_notes (1 MINOR):**
- MIN-008: Fitting bounds vs plausibility criteria distinction clarification

**Agent return summary:**
- fatal_count: 0
- major_count: 1
- minor_count: 1
- numerical_discrepancies: 1 (K lower bound)
- mathematical_impossibilities: 0
- baseline_fairness_issues: 0
- serena_searches_performed: 0 (Serena MCP unavailable; equivalent direct file reads performed)
