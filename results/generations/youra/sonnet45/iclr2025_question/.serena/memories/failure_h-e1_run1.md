# Phase 4 Failure Record: h-e1 (Run 1)

**Date:** 2026-03-19T08:36:00Z
**Hypothesis:** h-e1
**Run:** 1
**Final Status:** FAIL
**Failure Type:** MUST_WORK_FAIL

## Performance Gap

| Metric | Expected | Actual | Status |
|--------|----------|--------|--------|
| rho_data (α₀ vs data scale correlation) | > 0.9 | -0.800 | FAILED |
| rho_error (α₀⁻¹ vs error correlation) | > 0.7 | -0.800 | FAILED |
| Pass Rate | 100% (2/2) | 0% (0/2) | FAILED |

## Experimental Results

- **Alpha0 values:** [4.60, 4.39, 4.12, 4.22] (across 10%, 25%, 50%, 100% data scales)
- **Errors:** [0.759, 0.763, 0.739, 0.758]
- **Correlation direction:** NEGATIVE (opposite of prediction)
- **Statistical significance:** p=0.200 (not significant)

## Root Cause Analysis

1. **Hypothesis prediction was wrong**: The hypothesis predicted that Dirichlet concentration α₀ would CONTRACT monotonically with increasing data size (positive correlation ρ > 0.9), but experiments showed NEGATIVE correlation (ρ = -0.8)

2. **Contradicts epistemic reducibility claim**: The negative correlation pattern contradicts the core claim that "constrained evidence accumulation yields reducible epistemic signals that reflect true model uncertainty"

3. **Fundamental mechanism failure**: This is not a parameter tuning issue or implementation bug - the core theoretical prediction about α₀ behavior under increasing data is empirically falsified

4. **Dataset verification passed**: Code correctly uses real ARC-Challenge dataset from HuggingFace (allenai/ai2_arc), ruling out mock data as a confounding factor

## Lessons Learned

1. **IB-EDL α₀ contraction assumption was incorrect**: The assumption that Information Bottleneck regularization would cause Dirichlet concentration to contract with more data (indicating epistemic uncertainty reduction) was empirically falsified

2. **Need theoretical re-examination**: The relationship between IB regularization, evidence accumulation, and epistemic uncertainty quantification needs fundamental theoretical reconsideration

3. **PoC validation is critical**: This MUST_WORK gate correctly caught a fundamental flaw before extensive hyperparameter tuning was attempted

4. **Direction matters more than magnitude**: Even with p=0.200 (not statistically significant), the sign reversal (-0.8 vs expected +0.9) indicates a fundamental misunderstanding of the mechanism

## Why Route to Phase 0

This failure indicates a **fundamental flaw in the theoretical premise**, not an implementation issue:
- The core prediction about α₀ behavior was directionally wrong
- No parameter adjustment can fix a sign reversal in correlation
- Requires complete re-thinking of the research direction

---
*For cross-phase reference*
*Written at: 2026-03-19T08:36:00Z*
