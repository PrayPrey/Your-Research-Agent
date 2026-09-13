# Reflection Report: H-M3

**Generated:** 2026-08-05T16:15:00Z
**Gate Type:** SHOULD_WORK
**Gate Result:** DOCUMENT
**Reflection Outcome:** LIMITATION_RECORDED

---

## Experiment Summary

- N = 501 same-task MLP pairs (MNIST/SVHN/CIFAR-10, 167/task)
- mean(acc_latent) = 0.1209 vs mean(acc_ws) = 0.4654
- mean(delta) = −0.3445 ± 0.2007
- t = −38.38, p ≈ 0.0, Cohen d = −1.72
- % pairs where latent > weight-space: 0.0%

---

## Root Cause Analysis

**What succeeded:**
- Encoder loaded and produced latent codes (z_a, z_b) without error
- Round-trip shape verification passed (key/shape match)
- Weight-space averaging worked correctly (mean acc_ws = 0.465)
- Statistical analysis completed over full 501-pair set

**What failed:**
- Latent interpolation accuracy ≈ 0.10 (near chance for 10-class classification)
- 0% of pairs showed latent interpolation outperforming weight-space average

**Root cause:**
The graph decoder (from H-E1/H-M1) was trained with an edge-attribute reconstruction objective, producing a 512-dimensional statistics vector rather than raw weight tensors. The decode_latent_to_state_dict() function uses tile/slice mapping to reshape this stats vector into weight tensor shapes — this produces near-random weight initializations that bear no functional relationship to the encoded models.

The decoder is structurally incompatible with functional weight generation. This is not a hyperparameter issue; it is an architectural mismatch between the decoder's training objective (edge-attr reconstruction) and the required output (functional weight tensors).

---

## Self-Recovery Assessment

**Can improvement be identified?** No.

- The decoder produces ~10% accuracy (chance level) regardless of latent code quality
- Parameter adjustment (λ, learning rate, etc.) cannot fix a structural objective mismatch
- The encoder/decoder are frozen — no retraining available in H-M3 scope
- SELF_MODIFY would require retraining the decoder with a weight-reconstruction loss, which is a new experiment (H-M4 scope or beyond)

**Conclusion:** LIMITATION_RECORDED. No self-recovery path within H-M3 constraints.

---

## Key Insights

1. Contrastive SSL (NT-Xent) + graph encoder creates structured latent space, but the paired graph decoder was optimized for edge-stat reconstruction, not weight generation
2. Latent interpolation for functional model generation requires an explicit weight-reconstruction decoder objective (e.g., MSE on flattened weight tensors)
3. H-M2 finding (EquiSSL-perm R²=0.327) confirms good latent representations exist — the failure is in decoding, not encoding
4. Weight-space averaging (naive baseline) achieves reasonable accuracy (46.5% mean) demonstrating the MLP pairs are functionally valid
5. The 0%/0%/0% per-task positive rate confirms this is a systematic decoder issue, not task-specific

---

## Limitation Record

**Hypothesis:** H-M3 — EquiSSL-perm latent interpolation outperforms weight-space averaging

**Limitation:** NT-Xent contrastive training + graph encoder does not create a decoder capable of functional weight generation when the decoder was trained with edge-attribute reconstruction objective. Prediction P3 (functional latent geometry for model interpolation) is disconfirmed in this configuration.

**Scope:** Specific to the current frozen H-E1/H-M1 encoder+decoder; does not rule out that a weight-reconstruction decoder could enable functional interpolation.

**Next step:** H-M4 (pipeline continues regardless of DOCUMENT result per gate specification).

---

## Pipeline Status

Gate result: **DOCUMENT** — pipeline continues to H-M4 as specified.
No routing to Phase 0 or Phase 2A (SHOULD_WORK gate does not trigger these routes).
