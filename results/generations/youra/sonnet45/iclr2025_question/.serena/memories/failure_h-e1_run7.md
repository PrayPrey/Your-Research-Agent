# Phase 4 Failure Record: h-e1 (Run 7)

**Date:** 2026-03-20T20:59:30Z
**Hypothesis:** h-e1
**Run:** 7
**Final Status:** FAIL
**Failure Type:** GATE_CRITERIA_NOT_MET

## Performance Gap

| Metric | NTK Regime | Feature Regime | Target |
|--------|------------|----------------|--------|
| Power-law β | -0.3905 | -0.2416 | -0.50 (CLT prediction) |
| β 95% CI | [-0.448, -0.333] | [-0.322, -0.162] | Contains -0.50 (NTK) |
| R² | 0.9977 | 0.9883 | ≥ 0.90 |
| Test Accuracy | 0.6417 ± 0.0295 | 0.9678 ± 0.0011 | N/A |

**Critical Failure:** NTK regime β confidence interval [-0.448, -0.333] does not contain the theoretical CLT prediction of -0.50.

## Root Cause Analysis

- **Statistical Deviation:** NTK power-law exponent β=-0.391 significantly deviates from CLT prediction of -0.50 (gap of 0.109)
- **Confidence Interval Exclusion:** The 95% CI [-0.448, -0.333] completely excludes the target value of -0.50
- **Regime-Specific Behavior:** Feature regime (β=-0.242) also deviates, suggesting systematic regime-dependent convergence rates
- **Sample Size Limitation:** 20 runs may provide insufficient statistical power for tight CI bounds, but deviation appears systematic rather than noise-driven
- **Theoretical Mismatch:** CLT assumptions may not hold uniformly across NTK and Feature training regimes due to different optimization dynamics

## Lessons Learned

1. **CLT Universality Questioned:** Standard CLT predictions (β=-0.50) do not universally apply to deep learning variance scaling across all training regimes
2. **Regime-Dependent Convergence:** NTK and Feature regimes exhibit fundamentally different convergence behaviors (β=-0.39 vs β=-0.24), suggesting regime-specific mechanisms
3. **High R² Not Sufficient:** Excellent power-law fits (R² > 0.99) do not guarantee agreement with theoretical predictions - the exponent itself matters
4. **Statistical Power vs Systematic Error:** While larger sample sizes would tighten CIs, the observed deviation appears systematic (both regimes deviate in same direction)
5. **Hypothesis Assumption Gaps:** Original hypothesis assumed uniform CLT behavior without accounting for optimization regime effects on variance propagation

## Gate Evaluation

**Gate Type:** MUST_WORK  
**Result:** FAIL (4/5 criteria passed)

**Failed Criteria:**
- Test 1: NTK β 95% CI contains -0.50 → **FAIL** (CI excludes target)

**Passed Criteria:**
- Test 2a: Feature β 95% CI excludes -0.50 → PASS
- Test 2b: Feature β > -0.40 → PASS
- Test 3a: NTK R² ≥ 0.90 → PASS
- Test 3b: Feature R² ≥ 0.90 → PASS

## Experiment Summary

**Total Runs:** 40 (20 NTK + 20 Feature)  
**Dataset:** Fashion-MNIST  
**Architecture:** 1-hidden-layer MLP (width 128 for NTK, 32 for Feature)  
**Training:** Deterministic (fixed seeds 0-19)

**NTK Regime (Full-Batch GD, width=128):**
- Mean accuracy: 64.17% ± 2.95%
- Convergence rate: β=-0.391 (slower than CLT prediction)
- Excellent fit quality: R²=0.998

**Feature Regime (Adam, width=32):**
- Mean accuracy: 96.78% ± 0.11%
- Convergence rate: β=-0.242 (much slower than CLT prediction)
- Strong fit quality: R²=0.988

## Routing Decision

**Target:** Phase 0 (Hypothesis Reassessment)  
**Reason:** MUST_WORK gate failure requires fundamental reassessment of hypothesis assumptions

**Recommendations for Phase 0:**
1. **Separate Regime Hypotheses:** Create distinct hypotheses for NTK vs Feature regime convergence rates instead of unified CLT prediction
2. **Relax β Thresholds:** Consider regime-specific thresholds based on observed data (e.g., NTK: β ∈ [-0.45, -0.35], Feature: β ∈ [-0.30, -0.20])
3. **Theoretical Investigation:** Research theoretical foundations for regime-dependent CLT behavior in neural network training
4. **Increase Sample Size:** If maintaining unified hypothesis, increase to 50-100 runs per regime for tighter statistical bounds
5. **Alternative Framework:** Consider non-CLT variance scaling frameworks that account for optimization regime effects

## Historical Context

This is the **7th failure** for h-e1 across multiple iterations:
- Runs 1-6: Previous failures with various experimental configurations
- Run 7 (current): Fashion-MNIST with dual-regime testing (NTK + Feature)

**Pattern:** Consistent difficulty achieving CLT-predicted convergence rates across all attempts, suggesting fundamental theoretical mismatch rather than experimental error.

---
*For cross-phase reference*  
*Written at: 2026-03-20T20:59:30Z*
