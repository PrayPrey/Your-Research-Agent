# H-M2 Validation Report

**Date:** 2026-08-10
**Hypothesis:** Token masking excludes non-executed code from gradient updates
**Type:** MECHANISM
**Gate:** MUST_WORK

---

## Executive Summary

H-M2 validates that FGO (Fine-Grained Optimization) token masking correctly excludes non-executed code tokens from gradient computation. The core mechanism is **VERIFIED**:

- **Gradient Exclusion:** PASS - Masked tokens receive exactly zero gradient
- **Trace-Based Masking:** Working - Average 80% of tokens masked (non-executed)
- **Random Masking Control:** Working - Sparsity-matched random masks generated

**Gate Result:** CONDITIONAL_PASS

The gradient exclusion mechanism is verified. Statistical comparison (trace vs random pass@1) requires actual model training, which is deferred to Phase 5 baseline comparison.

---

## Experiment Configuration

| Parameter | Value |
|-----------|-------|
| Seeds | 42, 123, 456 |
| Problems | 500 (HumanEval + MBPP) |
| Episodes per Condition | 50 |
| Conditions | none, random, trace |
| Tokenizer | GPT-2 (mechanism validation) |

---

## Results

### Gradient Exclusion Verification

| Seed | Condition | Executed Grad Norm | Non-Executed Grad Norm | Verified |
|------|-----------|-------------------|------------------------|----------|
| 42 | trace | 0.0099 | 0.0 | TRUE |
| 123 | trace | 0.0082 | 0.0 | TRUE |
| 456 | trace | 0.0072 | 0.0 | TRUE |
| 42 | random | 0.0094 | 0.0 | TRUE |
| 123 | random | 0.0082 | 0.0 | TRUE |
| 456 | random | 0.0072 | 0.0 | TRUE |

**Key Finding:** Non-executed token gradients are exactly 0.0 in all cases. The FGO masking mechanism correctly excludes masked tokens from gradient computation.

### Masking Coverage

| Condition | Avg Masked % | Avg Executed Tokens |
|-----------|--------------|---------------------|
| none | 0.0% | 100% |
| random | 81.2% | 18.8% |
| trace | 81.2% | 18.8% |

**Key Finding:** Trace-based masking identifies ~80% of tokens as non-executed, consistent with H-M1 findings. Random masking matches this sparsity exactly.

### Performance (Canonical Solutions)

| Condition | Pass@1 |
|-----------|--------|
| none | 1.0 |
| random | 1.0 |
| trace | 1.0 |

Note: Using canonical solutions (ground truth), all conditions achieve 100% pass rate. Actual model training required for pass@1 comparison.

---

## Gate Evaluation

### MUST_WORK Gate Conditions

| Condition | Requirement | Status | Evidence |
|-----------|-------------|--------|----------|
| Gradient Exclusion | Masked tokens gradient = 0 | PASS | All 6 checks verified |
| Trace Masking Works | Trace identifies ~20% executed | PASS | 18.8% executed avg |
| Random Control Works | Sparsity matches trace | PASS | 81.2% = 81.2% |
| Code Executes | No runtime errors | PASS | All 9 runs complete |

### Statistical Comparison (Deferred)

Trace vs Random pass@1 comparison requires actual PPO training with model gradients. This is deferred to Phase 5 (Baseline Comparison) where full training runs will be executed.

---

## Mechanism Validation Details

### 1. FGO Loss Implementation

The `fgo_ppo_loss` function correctly implements masked PPO loss:
```python
masked_loss = per_token_loss * mask
return masked_loss.sum() / (mask.sum() + 1e-8)
```

Verified: Only positions with mask=1 contribute to loss.

### 2. Gradient Flow

Gradient verification confirms:
- Executed tokens (mask=1): Mean gradient norm 0.008-0.010
- Non-executed tokens (mask=0): Gradient norm exactly 0.0

This proves the mechanism works as designed.

### 3. Trace Collection

Using H-M1's validated trace collection mechanism:
- sys.settrace captures executed lines
- Token-to-line mapping via offset_mapping
- Binary mask construction per token

---

## Files Generated

| File | Description |
|------|-------------|
| code/outputs/experiment_results.json | Full experiment results |
| code/outputs/results.csv | Summary CSV |
| code/outputs/figures/pass_at_1_comparison.png | Bar chart visualization |
| code/outputs/figures/gradient_distribution.png | Gradient norm histograms |

---

## Conclusions

1. **Mechanism Verified:** FGO token masking successfully excludes non-executed tokens from gradient updates
2. **Implementation Correct:** The fgo_ppo_loss function works as designed
3. **Trace Integration:** H-M1 trace collection integrates correctly with masking
4. **Ready for Training:** Code is ready for full PPO training in Phase 5

---

## Next Steps

1. **Phase 5:** Run full PPO training with all 3 conditions
2. **Baseline Comparison:** Compare trace-based FGO against random masking
3. **Statistical Validation:** Paired t-test for trace vs random performance

---

## Gate Verdict

| Gate Type | Result | Reason |
|-----------|--------|--------|
| MUST_WORK | CONDITIONAL_PASS | Gradient exclusion mechanism verified; full training deferred to Phase 5 |

**Proceed to Phase 5 for baseline comparison.**
