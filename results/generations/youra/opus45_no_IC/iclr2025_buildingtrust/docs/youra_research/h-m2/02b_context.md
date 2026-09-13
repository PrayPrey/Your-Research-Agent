# Phase 2B Context: H-M2

**Hypothesis ID:** h-m2
**Type:** MECHANISM
**Statement:** Different confidence distributions require different temperature parameters for optimal calibration

## Prerequisites
- h-m1: PASS - 17/21 cluster pairs significantly different (KS p<0.05)

## Gate Condition
- **Type:** SHOULD_WORK
- **Condition:** Coefficient of variation of optimal T > 0.1
- **Fail Action:** EXPLORE (check regularization strength)

## Verification Protocol
1. Split data 80/20 per cluster (5-fold CV)
2. Optimize T per cluster on training fold
3. Compare optimal T values across clusters
4. Test if T variance exceeds regularization noise
5. Report T distribution with confidence intervals

## Success Criteria (PoC)
- Primary: Coefficient of variation of optimal T > 0.1
- Secondary: Range of T values spans >0.3

## Experimental Setup
- **Dataset:** TruthfulQA (817 questions, 7 clusters)
- **Model:** Llama-2-7B (open-weight, logit access)
- **Method:** Per-cluster temperature scaling optimization

## Previous Hypothesis Results
- **H-E1:** PASS - ANOVA p=0.00012 < 0.05, ECE range=0.099 > 0.05
- **H-M1:** PASS - KS test 17/21 pairs significant (p<0.05)

## Continuation Context
H-M1 confirmed that LLMs produce category-specific confidence distributions. Now testing whether these different distributions require different temperature parameters for optimal calibration. This is the mathematical consequence of M1 - if distributions differ, optimal scaling should differ.
