# Limitation Record: h-m2

**Hypothesis ID:** h-m2
**Type:** MECHANISM
**Gate:** SHOULD_WORK
**Date:** 2026-08-28
**Outcome:** LIMITATION_RECORDED

## Limitation Summary

Sample efficiency hypothesis could not be validated due to dataset ceiling effect.

## Details

- **Dataset:** Synthetic MNIST-INR (10-class weight classification)
- **Observation:** All architectures (MLP, DWS, NFT) achieve 100% AUC at all training fractions (25%, 50%, 100%)
- **Root Cause:** Dataset too easy - no variance to measure sample efficiency differences

## Hypothesis Status

The hypothesis "locality bias reduces sample complexity" remains **plausible but unconfirmed**. The ceiling effect prevents both validation and falsification.

## Recommendation for Future Work

1. Test on TrojAI benchmark (binary backdoor detection, harder task)
2. Or generate more difficult synthetic INR classification tasks
3. Consider using accuracy as proxy metric (may show variance before AUC ceiling)

## Learning for Pipeline

- Phase 2C dataset selection should verify expected difficulty range
- Add "expected baseline accuracy" sanity check before full experiment

## Cross-Reference

- Related: h-m1 (VALIDATED) - showed architecture encodes different inductive biases
- Continuation: h-m3 (NOT_STARTED) - may need similar dataset considerations
