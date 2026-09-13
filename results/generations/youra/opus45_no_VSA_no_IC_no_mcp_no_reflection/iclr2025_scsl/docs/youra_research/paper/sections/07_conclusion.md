# Conclusion

We began by asking whether gradient-based interventions could provide single-run robustification against spurious correlations without group labels. Our investigation reveals that before this question can be answered, a prerequisite must be met: gradient subspace methods require sufficient accumulation density to produce meaningful directional measurements.

## Summary

In this work, we tested the foundational assumption of Progressive Gradient Orthogonalization: that early training gradients capture spurious feature directions more strongly than core feature directions. Our experiments on Waterbirds with ResNet-50 yielded a surprising null result—spurious and core alignments were both approximately 0.05, statistically indistinguishable from each other.

Investigation traced this to measurement apparatus failure rather than absence of the hypothesized effect. Accumulating one gradient per epoch produced a 10-dimensional subspace in a 25-million-parameter space, insufficient to capture meaningful variance in any direction. The measurement resolution was too low to test the hypothesis.

Our contributions are methodological:

1. We establish minimum requirements for gradient subspace analysis: multi-batch accumulation within early epochs, not single-batch sampling.

2. We document a reproducible failure case that future gradient-based methods should avoid.

3. We provide guidance for valid testing of gradient orthogonalization hypotheses.

## Future Directions

**Fixing the accumulation:** The immediate next step is re-implementing gradient accumulation using streaming SVD across all batches during epochs 1-10. With ~38 batches per epoch, this yields ~380 gradient samples—sufficient for meaningful rank-50 subspaces.

**Testing the hypothesis:** If valid measurement confirms spurious-core separation, the full PGO mechanism (progressive gradient orthogonalization) can be implemented and evaluated against JTT, DFR, and Group DRO baselines on worst-group accuracy.

**Extending the scope:** Gradient subspace properties may differ across architectures (Vision Transformers vs CNNs), scales (larger models may require proportionally larger subspaces), and domains (language vs vision).

## Closing

The promise of gradient-based robustification—exploiting training dynamics without group labels in a single run—remains unrealized. What we have established is what valid measurement requires. Future work building on gradient subspace methods should validate accumulation density before claiming directional findings. The question of whether early gradients capture spurious directions remains open, but now we know how to test it properly.
