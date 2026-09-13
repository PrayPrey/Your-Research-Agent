# Hypothesis Completion Snapshot: h-m3

**Date:** 2026-08-05T16:15:00Z
**Hypothesis:** h-m3
**Statement:** Under the EquiSSL setting trained on SANE MultiZoo, if contrastive autoencoder training (NT-Xent + MSE reconstruction) is applied, then the resulting latent space enables functional model interpolation: decoded midpoint model (z = (zA + zB)/2) achieves higher task accuracy than naive weight-space averaging ((θA + θB)/2), averaged over 500+ MLP pairs from the training zoo (p < 0.05, paired t-test).
**Final Status:** COMPLETED
**Gate Result:** DOCUMENT
**Gate Type:** SHOULD_WORK
**Reflection Outcome:** LIMITATION_RECORDED

## Results
- N = 501 same-task MLP pairs (MNIST/SVHN/CIFAR-10, 167/task)
- mean(acc_latent) = 0.1209 vs mean(acc_ws) = 0.4654
- mean(delta) = −0.3445 ± 0.2007
- t = −38.38, p ≈ 0.0, Cohen d = −1.72
- % pairs positive: 0.0%
- Gate: DOCUMENT — pipeline continues to H-M4

## Root Cause (Limitation)
GraphDecoder (from H-E1/H-M1) was trained for edge-attribute reconstruction (512-dim stats vector), not raw weight generation. The decode_latent_to_state_dict() tile/slice mapping produces near-random weight initializations (acc ≈ 0.10, chance level for 10-class).

## Key Lessons
1. Contrastive SSL creates structured latent space but paired decoder must be trained with weight-reconstruction objective for functional interpolation
2. EquiSSL-perm encoder likely encodes good representations (H-M2: R²=0.327) — failure is in decoder, not encoder
3. Weight-space averaging achieves reasonable accuracy (46.5%) confirming MLP pairs are valid
4. Prediction P3 (functional latent geometry for model interpolation) disconfirmed in this configuration with frozen H-E1 decoder

## Pipeline Status
DOCUMENT — pipeline continues to H-M4 as specified. No routing to Phase 0/2A.

---
*Per-hypothesis snapshot for Phase 2A reference*
