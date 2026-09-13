# Phase 4 Failure Record: h-e1 (Run 3)

**Date:** 2026-03-20T02:00:00Z
**Hypothesis:** h-e1
**Run:** 3
**Final Status:** FAIL
**Failure Type:** MUST_WORK_FAIL

## Performance Gap

| Metric | Target | Actual | Gap |
|--------|--------|--------|-----|
| ρ(α₀, data%) | ≥0.90 | 0.10 | -0.80 (89% below target) |
| ρ(α₀⁻¹, error) | ≥0.70 | -0.10 | -0.80 (114% below target) |
| Slope comparison | >0.0 | 2.32 | ✓ PASS |

**Pass Rate:** 1/3 criteria (33%)

## Root Cause Analysis

- **Non-monotonic α₀ contraction**: IB-EDL's α₀ (epistemic uncertainty) does not contract monotonically with increasing training data size
- **α₀ spike at 25% data**: α₀ = 4.56 (10%) → 8.39 (25%) → 7.88 (50%) → 7.80 (75%) → 7.87 (100%)
- **No correlation with test error**: ρ(α₀⁻¹, error) = -0.10 indicates IB-EDL's epistemic uncertainty signal is uncorrelated with model error
- **Mechanism correctly implemented but theoretically flawed**: Code validation confirms IB-EDL mechanism is correctly implemented (encoder → latent → Dirichlet decoder), suggesting the theoretical assumption that α₀ reflects epistemic uncertainty is invalid for this architecture

## Lessons Learned

1. **IB-EDL epistemic uncertainty (α₀) does not reliably reflect model uncertainty in data-scaling experiments**: The hypothesis that α₀ would contract monotonically with data size was falsified
2. **Information Bottleneck regularization may interfere with epistemic uncertainty estimation**: The IB loss term (β × KL divergence) may cause α₀ to reflect compression rather than epistemic uncertainty
3. **Validation on simpler models recommended**: Before applying IB-EDL to large LLMs (Llama-3-8B), validate on smaller models (GPT-2) where failure modes are easier to diagnose
4. **Data scaling protocol is sound**: The experimental protocol (5 splits, fresh initialization, 10 epochs) successfully captured α₀ behavior across data sizes
5. **Gate threshold appropriateness confirmed**: With pass_rate=0.33 and major metric gaps (-0.80 on both primary metrics), MUST_WORK FAIL routing is justified

---
*For cross-phase reference*
*Written at: 2026-03-20T02:00:00Z*
