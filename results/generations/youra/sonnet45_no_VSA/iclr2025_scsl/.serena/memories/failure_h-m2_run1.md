# Phase 4 Failure Record: h-m2 (Run 1)

**Date:** 2026-07-11T05:54:19+00:00
**Hypothesis:** h-m2
**Run:** 1
**Final Status:** FAIL
**Failure Type:** MECHANISM_NOT_VALIDATED
**Gate Type:** MUST_WORK

## Performance Gap

| Metric | SWA | SGD | Gap |
|--------|-----|-----|-----|
| Noise Robustness Reduction (Epoch 10→15) | -1.31% | 21.75% | -23.06% |
| Gate Threshold | 5.0% | N/A | N/A |
| Gate Pass | False | N/A | N/A |

## Root Cause Analysis

- SWA mechanism did not demonstrate global basin centering through noise robustness improvement
- SWA noise robustness loss increased (-1.31% reduction) instead of decreasing
- SGD baseline showed 21.75% reduction in noise robustness loss, outperforming SWA
- Hypothesis H-M2 failed MUST_WORK gate criteria (requires ≥5% reduction)

## Lessons Learned

1. **SWA Global Basin Centering Not Validated:** The hypothesis that SWA trajectory averaging centers the model in a wider basin (reducing noise sensitivity) was not validated in this experiment
2. **Quick PoC Parameters:** Experiment used 20 epochs with SWA starting at epoch 10, which may not provide sufficient trajectory averaging time
3. **Noise Robustness Metric:** Gaussian weight perturbation (σ=0.01) showed SGD baseline outperforming SWA
4. **MUST_WORK Gate Enforcement:** Gate policy correctly triggered ABANDON routing due to fundamental mechanism failure

## Gate Decision

**Route:** ABANDON (per MUST_WORK gate policy)

---
*For cross-phase reference*
*Written at: 2026-07-11T05:54:19+00:00*