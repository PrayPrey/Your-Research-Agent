# H-M2 MUST_WORK Gate Failure

**Hypothesis ID:** h-m2
**Date:** 2026-03-27
**Gate Type:** MUST_WORK
**Gate Result:** FAIL

## Hypothesis Statement
Under MQAR with increasing N, if multiple key-value associations share fixed state capacity, then effective state rank r_eff will correlate with collapse threshold N*, because associations compete for limited representational dimensions.

## What Failed
- **Gate Condition:** CV(N*/r_eff) < 0.2
- **Actual CV:** 0.680 (3.4x above threshold)

## Root Cause
Cross-architecture MQAR evaluation is **not valid** with pretrained models:

1. **GLA-1.3B (fla-hub):** 0% accuracy on MQAR across all N values
2. **RetNet-1.3B (fla-hub):** 0% accuracy on MQAR across all N values
3. **RWKV-6-1.6B:** Works (22% at N=4, monotonic degradation), r_eff=39.14

The FLA models (GLA, RetNet) are pretrained language models that cannot perform associative recall tasks without fine-tuning. Only RWKV-World models have some capability due to their training mixture.

## Technical Issues
1. **State extraction:** FLA models return None for `past_key_values` in parallel mode; fallback to `hidden_states` gives degenerate r_eff=1.0
2. **Tokenization:** Different tokenizers (RWKV-World vs GPT-2-style) make direct comparison invalid
3. **Task format:** MQAR requires specific prompt format that FLA models don't understand

## Lessons Learned
1. **Do not assume pretrained models can perform novel tasks** - MQAR is not in GLA/RetNet training distribution
2. **Cross-architecture scaling laws require controlled conditions** - either fine-tune all models on same task, or use synthetic state manipulation
3. **State extraction differs by architecture** - need architecture-specific extraction, not generic fallback

## Recommendation
For future cross-architecture scaling law validation:
- Fine-tune all architectures on MQAR first
- Or use single architecture with controlled state rank manipulation
- Or compare architectures on tasks within their training distribution

## Files
- Report: `h-m2/04_validation.md`
- Results: `h-m2/code/results/results.json`
- Figures: `h-m2/code/figures/`
