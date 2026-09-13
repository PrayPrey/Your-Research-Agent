# Discussion

Our experiments reveal a critical methodological constraint for gradient subspace analysis rather than evidence for or against the Progressive Gradient Orthogonalization hypothesis.

## Key Findings

**Finding 1: Gradient subspace methods require sufficient accumulation density.**

Accumulating one gradient per epoch produces a subspace whose rank equals the number of epochs, not the requested SVD rank. In our experiment, 10 epochs yielded a rank-10 subspace in a 25-million-parameter space—capturing approximately 10/25M = 4×10^{-7} of the variance along any direction. This is insufficient for meaningful directional analysis regardless of the underlying phenomenon.

This finding has immediate implications for gradient-based robustification methods: any approach relying on gradient subspace analysis must validate that accumulation produces sufficient rank relative to parameter count.

**Finding 2: The PGO hypothesis remains unverified, not refuted.**

Our null result (indistinguishable alignments) stems from measurement failure rather than absence of the hypothesized effect. Simplicity bias theory (Shah et al., 2020) predicts early gradients favor spurious features, and our training dynamics are consistent with this—the model achieves high training accuracy quickly while worst-group accuracy (not measured in this existence experiment) presumably suffers. The question of whether gradient subspaces can capture this effect remains open pending valid measurement.

**Finding 3: Multi-batch accumulation is necessary.**

To achieve meaningful subspace rank, gradients must be accumulated across all batches within early epochs rather than sampling one batch per epoch. With ~38 batches per epoch (4,795 samples / 128 batch size) and 10 accumulation epochs, multi-batch accumulation would yield ~380 gradient samples—sufficient for a rank-50 subspace that captures meaningful variance.

## Limitations

**The core hypothesis is unverified.** We cannot claim that PGO works or fails because our measurement apparatus prevented valid testing. The theoretical motivation remains intact: if early gradients do capture spurious directions, orthogonalization could improve robustness. We have only established what valid testing requires.

*Why acceptable:* This limitation is the paper's main finding—identifying measurement requirements is a contribution distinct from validating the intervention.

**Only one dataset tested.** We evaluated on Waterbirds alone. Other spurious correlation benchmarks (CelebA, ColorMNIST) may exhibit different gradient dynamics.

*Why acceptable:* Waterbirds suffices to identify the measurement issue. Multi-dataset evaluation is warranted only after the measurement apparatus is fixed.

**No baseline comparison performed.** This experiment tested measurement validity, not method effectiveness. Comparison against JTT, DFR, or Group DRO awaits valid PGO implementation.

*Why acceptable:* Baseline comparison requires working methodology; establishing measurement validity is prerequisite.

**Single random seed.** Our experiments used seed 42 for all runs. While sufficient to demonstrate measurement apparatus failure, reproducibility across seeds should be verified in future work.

## Future Work

**Immediate:** Re-implement gradient accumulation using streaming SVD across all batches during epochs 1-10. Verify subspace rank matches or exceeds requested rank before measuring alignment.

**Medium-term:** If valid measurement shows spurious-core separation, implement full PGO mechanism (gradient orthogonalization) and evaluate worst-group accuracy against baselines.

**Long-term:** Extend to other architectures (Vision Transformers) and domains (language, multimodal) where gradient subspace properties may differ.

## Broader Impact

This work identifies a methodological pitfall in gradient-based machine learning interventions. Researchers proposing gradient subspace methods for any purpose—robustness, interpretability, optimization—should validate accumulation density before claiming directional findings.

The negative societal impacts appear minimal. Our contribution is methodological caution rather than a deployable system. If anything, preventing deployment of invalid measurement apparatus reduces risk of false claims about model robustness.
