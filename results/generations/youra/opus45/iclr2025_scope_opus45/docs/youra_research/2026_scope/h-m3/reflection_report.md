# Reflection Report: H-M3

**Hypothesis:** Eigenmode Energy Redistribution via Projection-Only LoRA
**Gate Type:** SHOULD_WORK
**Gate Result:** FAIL
**Reflection Outcome:** LIMITATION_RECORDED
**Date:** 2026-03-28

---

## Summary

Step 06b reflection was triggered for hypothesis H-M3 after the SHOULD_WORK gate failed. Since SHOULD_WORK gates are designed for non-critical mechanisms, the failure is recorded as a **limitation** rather than routing to Phase 0 or Phase 2A-Dialogue.

---

## Gate Evaluation Details

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| ΔE (nats) | 5.93e-07 | > 0.1 | FAIL |
| Pre slow fraction | 1.97e-05 | - | Baseline |
| Post slow fraction | 1.91e-05 | - | No change |

**Failed Checks:**
- `delta_e_nats = 5.93e-07 << 0.1 threshold`

---

## Reflection Analysis

### What Succeeded
- Experiment executed without errors
- Energy measurement methodology worked correctly
- LoRA training converged successfully
- Perplexity remained in expected range (14.35)
- All figures and metrics were generated

### What Failed
- ΔE metric was essentially zero (5.93e-07 nats vs 0.1 threshold)
- Slow mode fraction actually decreased slightly (-5.93e-07)
- Only 2/48 layers had any slow mode energy at all
- No evidence of energy redistribution toward slow eigenmodes

### Root Cause Analysis
1. **Structural Constraint:** Energy distribution is determined by the A matrix eigenvalues, which are frozen during projection-only LoRA training
2. **Sparse Slow Modes:** Only 2 layers (18-19) have slow modes (|λ| > 0.99), representing only 0.002% of total energy
3. **Mechanism Non-Operative:** Projection-only LoRA modifies input/output mappings but cannot route energy to specific eigenmodes

### Key Insights
- EUH (Eigenmode Utilization Hypothesis) is NOT supported for projection-only LoRA
- This is a valid negative result that eliminates one explanatory pathway
- Supports MHSH (Memory Horizon Separation Hypothesis) as the dominant mechanism

---

## Decision: LIMITATION_RECORDED

### Rationale
Per step-06b Section 1b for SHOULD_WORK gates:
- Gate type: SHOULD_WORK (non-critical mechanism test)
- No improvement path found after analysis
- Scientific value in negative result

### Actions Taken
1. Recorded limitation in checkpoint
2. Saved to Serena Memory: `global/phase45/limitation_h-m3_scope_opus45_run1`
3. Pipeline continues to next hypothesis (H-M4)

---

## Scientific Value

**Negative Result Contribution:**
- Eliminates EUH mechanism as explanation for projection-only LoRA behavior
- Strengthens MHSH hypothesis (task success depends on spectral horizon fit)
- Narrows hypothesis space for H-M4 discriminative test

**Implications:**
- If tasks require memory > H_spec, projection-only LoRA will fail (per MHSH)
- Extending memory horizon would require modifying A matrix (spectral surgery)
- H-M4 will test this discriminative prediction

---

## Next Action

**Continue to H-M4:** The pipeline continues with the next hypothesis in the verification plan. H-M4 will test the discriminative MHSH prediction using MQAR tasks that exceed the spectral horizon.

---

## Files Generated

| File | Status |
|------|--------|
| 04_checkpoint.yaml | Complete |
| 04_validation.md | Complete |
| reflection_report.md | Complete |
| code/results.yaml | Complete |
| code/figures/*.png | 5 figures generated |

---

## Serena Memory Record

**Memory File:** `global/phase45/limitation_h-m3_scope_opus45_run1`
**Memory Type:** limitation
**Written At:** 2026-03-28T00:15:00Z

---

*Reflection completed: 2026-03-28T00:15:00Z*
*Step 08 completed: 2026-03-28T00:16:00Z*
