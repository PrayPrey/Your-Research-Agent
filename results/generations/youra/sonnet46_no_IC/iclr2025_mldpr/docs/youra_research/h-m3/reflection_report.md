# Reflection Report: H-M3

**Hypothesis ID:** H-M3  
**Gate Type:** SHOULD_WORK  
**Gate Result:** INFORMATIVE_NEGATIVE  
**Reflection Outcome:** LIMITATION_RECORDED  
**Date:** 2026-08-05

---

## 1. Reflection Summary

H-M3 tested the categorical dose-response structure of tag counts across four bins (0, 1-2, 3-5, 6+) using NB-2 regression on the full OpenML corpus (N=5,217). The gate required: (1) monotonic IRR ordering AND (2) ≥2/3 adjacent contrasts significant at Bonferroni α=0.0167.

**Outcome:** LIMITATION_RECORDED — the informative negative is structurally driven by bin sparsity (N=73 in bin "1-2"), not a fixable implementation issue.

---

## 2. What Succeeded

- Monotonic IRR ordering confirmed: IRR(1-2)=1.127 < IRR(3-5)=1.128 < IRR(6+)=1.286 ✓
- NB-2 model converged cleanly with BFGS (LLF=-12859.71, AIC=25739.41)
- CT LR=7509.42 confirms NB-2 strongly appropriate over Poisson
- The 3-5 vs 6+ contrast is highly significant (bonf_p=5.54e-10)
- All 5 figures generated, all code runs without errors

## 3. What Failed (Gate Conditions Not Met)

- Adjacent contrasts: only 1/3 passing (needed ≥2/3)
- 0→1-2 contrast: bonf_p=0.272 (FAIL) — N=73 in bin "1-2" insufficient for statistical power
- 1-2→3-5 contrast: bonf_p=1.0 (FAIL) — IRR gap of 0.001 between bins 1-2 and 3-5 is negligible

## 4. Root Cause Analysis

**Structural data issue:** Bin "1-2" contains only N=73 datasets (1.4% of corpus), compared to N=2,592 (49.7%) in bin "0" and N=1,842 (35.3%) in bin "6+". The tag distribution in OpenML is highly bimodal: datasets either have 0 tags or 3+ tags. Few datasets have exactly 1-2 tags.

This bin sparsity is an intrinsic property of the OpenML dataset corpus, not an implementation bug. No self-modification of the H-M3 hypothesis design would resolve this without fundamentally changing the binning strategy — which would create a different hypothesis (not H-M3).

**IRR gap at 1-2 vs 3-5:** The nearly identical IRRs (1.1267 vs 1.1277) suggest that having 1-2 tags provides essentially the same discovery boost as having 3-5 tags. The real categorical step is at 6+ tags.

## 5. Limitation Recorded

> **Scientific Constraint:** The categorical dose-response for tag count (bins 0, 1-2, 3-5, 6+) is not uniformly graded. The FAIR F1 discovery mechanism operates as a **binary threshold effect** (0 vs ≥1 tag, confirmed by H-E1 IRR=1.23) plus a **high-count amplification** (6+ tags driving the only significant adjacent contrast). The intermediate bins (1-2, 3-5) are statistically indistinguishable from each other given the observed corpus distribution.

## 6. Self-Recovery Assessment

**Self-recovery not warranted** because:
1. The bin sparsity (N=73 in "1-2") is structural — not fixable by code modification
2. The IRR gap between bins "1-2" and "3-5" is 0.001 — no amount of modeling adjustment changes the near-zero gap
3. This is scientifically informative (confirms binary threshold dominance) — recording limitation is the correct action per SHOULD_WORK gate protocol

## 7. Pipeline Impact

- **No cascade effects** — H-M3 is the final hypothesis in the chain (H-E1→H-M1→H-M2→H-M3)
- **No routing to Phase 0 or Phase 2A** — SHOULD_WORK gates do not trigger routing on informative negatives
- **Continue to Phase 4.5** (Hypothesis Synthesis) with all 4 sub-hypothesis outcomes documented

## 8. Lessons Learned

- Categorical binning requires pre-verification of bin sample sizes; bins <100 will lack Bonferroni-corrected contrast power
- Future categorical dose-response designs should use quantile-based bins to ensure equal sample sizes
- The H-E1→H-M2 continuous evidence chain is sufficient without requiring categorical step confirmation
