# Adversarial Review — Round 2 (R2)
# Numerical Verification + Credibility Check
# Paper: "When Confounding Hides the Signal..." (06_paper_r1.md)
# Generated: 2026-05-04T09:45:00Z
# Note: Serena MCP unavailable (no-mcp mode) — verification performed against loaded ground truth files

---

## Ground Truth Verification Table

| Claim | Paper Value | Ground Truth | File Source | Match |
|-------|-------------|-------------|-------------|-------|
| Unadjusted KM p | 0.583 | 0.583 | h-m1/04_validation.md | ✅ YES |
| Matched KM p | 0.0053 | 0.0053 | h-m1/04_validation.md | ✅ YES |
| Cox HR (text) | 3.16 | 3.159 | h-m1/04_validation.md | ✅ (rounding) |
| Cox HR (table) | 3.159 | 3.159 | h-m1/04_validation.md | ✅ YES |
| Cox CI | [1.032, 9.672] | [1.032, 9.672] | h-m1/04_validation.md | ✅ YES |
| Cox p | 0.044 | 0.044 | h-m1/04_validation.md | ✅ YES |
| Median TTFR high-FAIR | 158 days | 158.0 days | h-m1/04_validation.md | ✅ YES |
| Median TTFR low-FAIR | 202 days | 202.0 days | h-m1/04_validation.md | ✅ YES |
| TTFR reduction | 44 days (22%) | 44 days, 21.8%≈22% | calculated | ✅ YES |
| CV | 0.1597 | 0.1597 | h-e1/04_validation.md | ✅ YES |
| Bimodality dip p | 9.96e-6 | 9.96e-6 | h-e1/04_validation.md | ✅ YES |
| n_high | 720 (14.4%) | 720/5000=14.4% | h-e1/04_validation.md | ✅ YES |
| n_low | 4,280 (85.6%) | 4280/5000=85.6% | h-e1/04_validation.md | ✅ YES |
| n matched pairs | 35 | 35 | h-m1/04_validation.md | ✅ YES |
| SMD max | 0.098 | 0.098 | h-m1/04_validation.md | ✅ YES |
| Ablation A p/HR | 0.697 / 1.06 | 0.697 / 1.06 | h-m1/04_validation.md | ✅ YES |
| Ablation B p/HR | 0.064 / 1.79 | 0.064 / 1.79 | h-m1/04_validation.md | ✅ YES |
| Ablation C p/HR | 0.000 / 3.66 | 0.000 / 3.66 | h-m1/04_validation.md | ✅ YES |
| SA-2 p/HR | 0.006 / 3.00 | 0.006 / 3.00 | h-m1/04_validation.md | ✅ YES |
| SA-3 p/HR | 0.005 / 2.93 | 0.005 / 2.93 | h-m1/04_validation.md | ✅ YES |
| n cohort | 200 | 200 | h-m1/04_validation.md | ✅ YES |
| Proxy weights F1/F2/F3 | 0.25/0.50/0.25 | 0.25/0.50/0.25 | 065_ground_truth.yaml | ✅ YES |
| Unit tests h-e1 | 29/29 | 29/29 | 065_ground_truth.yaml | ✅ YES |
| Unit tests h-m1 | 30/30 | 30/30 | 065_ground_truth.yaml | ✅ YES |
| Caliper smoke-test | 0.8 SD | 0.8 | h-m1/04_validation.md | ✅ YES |

---

## Mathematical Validity Analysis

| Check | Calculation | Result |
|-------|-------------|--------|
| 22% TTFR reduction | 44/202=0.2178≈22% | ✅ CORRECT (R1 fix verified) |
| HR vs median ratio | HR=3.159 (hazard rate); 202/158=1.278 (median ratio) | ✅ DISTINCT — paper correctly separates both |
| Group size sum | 720+4280=5000; 14.4+85.6=100% | ✅ CORRECT |
| SMD < threshold | 0.098 < 0.100 | ✅ CORRECT |
| CV > threshold | 0.1597 > 0.150 | ✅ CORRECT (marginal pass) |
| Cox CI excludes 1.0 | lower bound=1.032 > 1.0 | ✅ CORRECT |
| Bimodality dip p < 0.05 | 9.96e-6 < 0.05 | ✅ CORRECT |

**Mathematical impossibilities found: 0**

---

## Executive Summary

| Severity | Count |
|----------|-------|
| FATAL | 0 |
| MAJOR | 1 |
| MINOR | 1 (for human review) |

**Recommendation: FIX MAJOR-R2-001, then CONVERGE** — all numerical claims verified. One disclosure issue found (h-m2 failure not mentioned). After fix, paper qualifies for convergence.

---

## FATAL Issues

*None.*

---

## MAJOR Issues

### R2-MAJOR-001: h-m2 Accessible Mechanism Failure Not Disclosed

**Persona:** Skeptical Expert  
**Location:** Discussion 6.2 (Limitations), Discussion 6.3

**Issue:** The paper's Discussion L3 states "H-M3 and H-M4 not executed" as the scope limitation. However, h-m2 (Accessible sub-criteria → 12-month run count) WAS executed and encountered a SHOULD_WORK gate failure due to a data infrastructure limitation (upload_date missing from OpenML bulk API → only 4 matched pairs achieved vs 500 required; MWU p=1.000). The dry-run confirmed the mechanism is valid (p=6.99e-9, β=0.743), but production execution was blocked by missing metadata.

A reviewer who investigates the Accessible dimension (as the paper's Ablation B implies was tested: "p=0.064, HR=1.79 — marginal") may ask: "was the Accessible mechanism tested independently? If so, what happened?" The current text implies only h-m3 and h-m4 are untested, creating a gap.

**Why it matters:** Selective reporting concerns arise when a negative/inconclusive result from an attempted analysis is not disclosed. Even a data-infrastructure failure should be noted to give reviewers the full picture.

**Required fix:** Extend Discussion L3 to acknowledge h-m2:

> "**L3: Incomplete mechanism coverage.** The Accessible sub-criteria analysis (H-M2) was implemented and verified correct in dry-run (MWU p=6.99e-9, β=0.743), but production execution was blocked by a data infrastructure limitation: the OpenML bulk API does not return upload_date, yielding insufficient matched pairs (n=4 vs. 500 required) and a null production result (MWU p=1.000). This is a data availability issue, not a null mechanism result. H-M3 (Reusable dimension) and H-M4 (HuggingFace cross-repository) were not executed."

---

## MINOR Issues (for Human Review)

| ID | Location | Issue |
|----|----------|-------|
| R2-MIN-001 | Introduction paragraph 1 | "p=0.58" (rounded) vs Abstract/Results "p=0.583" — standardize to 0.583 throughout |

---

## Baseline Fairness Assessment

| Baseline | Reported | Fair Comparison? | Assessment |
|----------|----------|-----------------|------------|
| Unadjusted KM (no matching) | p=0.583 | YES | Correct use: demonstrates confounding problem |
| Aggregate FAIR threshold (Ablation A) | p=0.697, HR=1.06 | YES | Same matched pairs, same DV — valid ablation |
| Accessible IV (Ablation B) | p=0.064, HR=1.79 | YES | Same framework, different IV — valid |

**No unfair baseline comparisons found.**

---

## Serena MCP Verification Log

**Status:** Serena MCP unavailable (no-mcp mode)  
**Fallback:** Direct verification against loaded Phase 4/5 validation files:
- h-e1/04_validation.md — all h-e1 metrics verified
- h-m1/04_validation.md — all h-m1 metrics verified  
- h-m2/04_validation.md — h-m2 context verified (SHOULD_WORK FAIL, data limitation)
- 065_ground_truth.yaml — cross-reference source
- verification_state.yaml — pipeline state confirmed

**All 27 numerical claims verified. 0 discrepancies found.**

---

## Summary for Revision Agent

**Fix required:**
1. **R2-MAJOR-001 (URGENT):** Expand Discussion L3 to disclose h-m2 Accessible mechanism attempt and data-infrastructure failure

**Collect for human review:**
- R2-MIN-001: "p=0.58" → "p=0.583" in Introduction paragraph 1
