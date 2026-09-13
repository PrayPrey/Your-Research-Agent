# Limitation Record: h-m4 (Run 1)

**Date:** 2026-04-24T19:11:59.523909
**Hypothesis:** h-m4
**Run:** 1
**Gate Type:** SHOULD_WORK
**Result:** LIMITATION_RECORDED
**Pipeline Status:** Continued (not blocked)

## Limitation Details

While extended training and full alignment metric improvements identified, near-zero positive correlation (ρ=0.0447) suggests functional coupling between geometry and robustness may be weaker or absent. Success probability ~40-45% below 50% threshold.

## Failed Checks

- No significant negative correlation: ρ=0.0447, p=0.8517 (expected ρ<-0.6, p<0.01)
- Near-zero correlation indicates no functional coupling
- Insufficient training (5 epochs) likely caused poor endpoint differentiation

## Partial Results

| Metric | Value |
|--------|-------|
| fge_correlation | 0.0447 |
| fge_p_value | 0.8517 |
| linear_correlation | 0.0447 |
| linear_p_value | 0.8517 |
| expected_correlation | < -0.6 |
| expected_p_value | < 0.01 |

## Experiment Summary

Tested functional coupling between curvature alignment A(w) and worst-group accuracy (WGA) along mode-connected paths between ERM and DRO endpoints. Expected strong negative correlation (ρ<-0.6) but observed near-zero positive correlation (ρ=0.0447, p=0.8517). Root causes: insufficient training (5 epochs), simplified alignment metric, poor WGA performance (most checkpoints WGA≈0).

## LLM Assessment Details

### Improvement Potential: Yes
**Identified Improvements:**
1. Extended training (50-100 epochs instead of 5)
2. Full Hessian-based A(w) metric (replace simplified gradient variance proxy)
3. Endpoint validation (ensure ERM WGA ~70%, DRO WGA ~80% before path sampling)
4. Use pre-trained baselines from h-e1 if available

### Worth Retry: No (Probability ~40-45%)
**Reasoning:**
- While training improvements would help endpoint differentiation
- Near-zero positive correlation (not just weak negative) suggests mechanism weaker than hypothesized
- Non-monotonic WGA behavior (drops to zero mid-path) indicates methodological issues
- Success probability 40-45% is below the 50% threshold for retry

## Context

This limitation was recorded but **did not block the pipeline**.
The hypothesis proceeded to Phase 5 with this limitation noted.

Future research attempts should consider:
1. The specific checks that failed
2. Whether the limitation is fundamental or circumstantial
3. Alternative approaches that might avoid this limitation

### Mechanism Chain Context

This is the final mechanism hypothesis (H-M4) in the chain:
- **H-E1 (PASS):** Geometric signature exists - ERM alignment (0.7234) > DRO alignment (0.3156)
- **H-M1 (PASS):** Sharp curvature concentrates in outlier subspace
- **H-M2 (PASS):** Sharp directions align with minority gradients
- **H-M3 (PASS):** SGD flows along flat directions
- **H-M4 (FAIL):** Functional coupling between geometry and robustness NOT validated

The prior steps validated geometric phenomena exist, but the final coupling to robustness phenotype was not demonstrated.

---

## When This Memory Is Read

- **Phase 0:** If pipeline routes back to Phase 0 (from Phase 5 PARTIAL),
  this limitation informs brainstorming to avoid similar issues
- **Phase 2A:** Consider whether geometry-robustness coupling needs reconceptualization
- **Phase 6 Discussion:** Limitation is included in paper's Limitations section

---
*Limitation recorded at: 2026-04-24T19:11:59.523928*
*For cross-phase reference*
