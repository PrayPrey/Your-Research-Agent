# Reflection Report: H-M4

**Date:** 2026-04-24T19:12:00Z
**Hypothesis:** h-m4
**Gate Type:** SHOULD_WORK
**Gate Result:** FAIL
**Reflection Outcome:** LIMITATION_RECORDED

---

## Executive Summary

Hypothesis h-m4 tested functional coupling between loss landscape geometry and distribution shift robustness. The experiment **FAILED** to demonstrate the predicted strong negative correlation between curvature alignment A(w) and worst-group accuracy (WGA).

**Decision:** Record limitation and continue to Phase 5.

---

## Gate Evaluation Results

**SHOULD_WORK Gate Criteria:**
1. **Primary:** FGE path ρ < -0.6, p < 0.01
   - **Result:** ✗ FAIL (ρ=0.0447, p=0.8517)
2. **Secondary:** Linear path ρ < -0.7, p < 0.01
   - **Result:** ✗ FAIL (ρ=0.0447, p=0.8517)

**Overall:** FAIL (0/2 criteria met)

---

## LLM Self-Assessment (SHOULD_WORK)

### Question 1: Improvement Potential
**Can specific, actionable modifications be identified?**

**Answer:** Yes

**Identified Improvements:**
1. **Extended Training:** Increase from 5 epochs to 50-100 epochs
   - Current training insufficient for distinct ERM/DRO geometric signatures
   - Need well-converged endpoints before path sampling
2. **Full Hessian-based A(w) Metric:** Replace simplified gradient variance proxy
   - Current simplified metric may not capture full geometric signature
   - Use validated Marchenko-Pastur outlier alignment from h-m2
3. **Endpoint Validation:** Verify endpoint properties before path sampling
   - Ensure ERM achieves expected WGA ~70%
   - Ensure DRO achieves expected WGA ~80%
4. **Reuse Pre-trained Baselines:** Load validated checkpoints from h-e1 if available

### Question 2: Worth Retry
**Is there ≥50% probability that modifications would pass the gate?**

**Answer:** No (Probability: 40-45%)

**Reasoning:**
- While training improvements would help endpoint differentiation, the **near-zero positive correlation** (not just weak negative) suggests the functional coupling may be fundamentally weaker than hypothesized
- **Non-monotonic WGA behavior:** Most interpolated checkpoints have WGA≈0, indicating methodological issues beyond just training duration
- **Success probability 40-45%** is below the 50% threshold for retry
- Prior hypotheses (h-e1 through h-m3) validated geometric phenomena, but the final coupling to robustness phenotype is not demonstrated

### Decision Matrix

| Improvement Potential | Worth Retry | Decision |
|----------------------|-------------|----------|
| Yes | No | **FAIL** |

**Outcome:** LIMITATION_RECORDED

---

## Root Cause Analysis

### Primary Causes

1. **Insufficient Training (5 epochs)**
   - Too short to produce well-differentiated ERM/DRO models
   - Endpoints lack strong geometric signatures
   - ERM WGA (32.3%) and DRO WGA (9.8%) both below expected ranges

2. **Simplified Alignment Metric**
   - Gradient variance proxy may not capture full Hessian-based A(w)
   - Full eigendecomposition needed for accurate alignment measurement

3. **Poor WGA Performance Along Path**
   - Most checkpoints (α ≈ 0.16 to 0.84) exhibit WGA≈0
   - Indicates severe minority-group failure in interpolated models
   - Non-monotonic behavior suggests path interpolation methodology issues

### Secondary Observations

4. **Near-Zero Correlation**
   - ρ=0.0447 is not just "weak negative" but actually slightly positive
   - Suggests functional coupling may be weaker or absent compared to hypothesis

5. **Mechanism Chain Incompleteness**
   - H-E1 through H-M3 validated geometric phenomena exist
   - H-M4 failed to validate the final link: geometry → robustness
   - Gap between geometric observations and behavioral outcomes

---

## Lessons Learned

### What Worked
1. Mechanism chain approach (H-E1 → H-M1 → H-M2 → H-M3) successfully validated intermediate steps
2. Geometric signatures (alignment, curvature concentration, SGD flow) all demonstrated
3. Mode-connected path methodology is sound conceptually

### What Didn't Work
1. Lightweight training (5 epochs) insufficient for final coupling test
2. Simplified metrics adequate for intermediate steps but not final validation
3. Functional coupling assumption may be too strong

### For Future Attempts
1. **Always validate endpoint performance** before path sampling experiments
2. **Use full metrics** (not proxies) for critical validation steps
3. **Consider alternative coupling mechanisms** if geometry-phenotype link is weak
4. **SHOULD_WORK gates** appropriately used for optional hypotheses - failure doesn't block pipeline

---

## Reflection Outcome: LIMITATION_RECORDED

**Status:** h-m4 marked as COMPLETED with limitation noted

**Pipeline Action:** Continue to Phase 5 (baseline comparison)

**Limitation Note:** Functional coupling between loss landscape geometry and worst-group accuracy not validated. While geometric phenomena (H-E1 through H-M3) demonstrated, the final link to robustness phenotype remains unproven. Future work should explore:
- Alternative geometric-behavioral coupling mechanisms
- Longer training regimes for endpoint differentiation
- Different interpolation methodologies

**Serena Memory:** `limitation_h-m4_run1.md` created for cross-phase learning

---

## Next Steps

### Immediate (Step 7)
- Generate Phase 4 completion report
- Update verification_state.yaml with LIMITATION_RECORDED status

### Phase 5
- Proceed to baseline comparison with h-m4 limitation documented
- Include limitation in Phase 6 discussion section

### Future Research
- If Phase 5 routes back to Phase 0, this limitation informs brainstorming
- Consider whether geometry-robustness coupling needs reconceptualization in Phase 2A

---

*Reflection completed: 2026-04-24T19:12:00Z*
*Step-06b-reflection executed with LLM self-assessment*
*Proceeding to Step 7 (Report Generation)...*
