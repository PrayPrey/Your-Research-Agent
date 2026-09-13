# Hypothesis Context: H-E1

**Date:** 2026-08-19
**Hypothesis ID:** h-e1
**Type:** EXISTENCE
**Gate:** MUST_WORK

---

## Hypothesis Statement

Under controlled RL fine-tuning on APPS, if fine-grained feedback is applied only to U_line errors, then training reaches 30% pass@1 >10% faster than unconditional application.

## Rationale

This establishes whether error-type gating produces any measurable benefit before testing mechanism. RLTF shows multi-granularity helps; we test whether selective application further improves efficiency.

## Variables

- **Independent:** feedback_gating_strategy (fine_always vs fine_gated)
- **Dependent:** sample_efficiency (steps to 30% pass@1)
- **Controlled:** base_model, dataset, compute_budget, coarse_reward

## Success Criteria

- **Primary:** Efficiency ratio > 0.10 (Fine-gated 10%+ faster)
- **Secondary:** p<0.05 on paired t-test

## Verification Protocol

1. Train CodeT5-large on APPS with Fine-always (RLTF default) for 5 epochs across 3-5 seeds
2. Train identical setup with Fine-gated (U_line only) across 3-5 seeds
3. Log pass@1 at each checkpoint; record steps to reach 30% threshold
4. Compare distributions with paired t-test (p<0.05)
5. Compute efficiency ratio: (Steps_fine_always - Steps_fine_gated) / Steps_fine_always

## Failure Response

IF fails: PIVOT to examining other efficiency thresholds (20%, 40%)

---

## Experimental Setup

### Dataset
- **Name:** APPS
- **Type:** standard
- **Source:** https://github.com/hendrycks/apps
- **Training Size:** 5000 problems

### Model
- **Name:** CodeT5-large
- **Type:** encoder-decoder
- **Source:** Salesforce/codet5-large
- **Parameters:** 770M

### Compute
- **GPU-Days:** 12
- **Seeds per Condition:** 5
- **Conditions:** 4

---

## Dependencies

- **Prerequisites:** None (root hypothesis)
- **Dependents:** H-M1, H-M2, H-M3, H-M4

## Gate Condition

**Type:** MUST_WORK
- If this hypothesis fails, verification stops entirely
- Must demonstrate >10% efficiency improvement

---

## Key References

- RLTF paper: Multi-granularity feedback advantage
- VeRPO paper: Aggregation bias effects
- CodeRL: Baseline comparison

## Risks

- **R4 (High):** U_ignore frequency too low (<10%) for detectable effect
  - Mitigation: Use 5 seeds for statistical power
- **R5 (Low):** RLTF implementation bugs
  - Mitigation: Code review against paper equations
