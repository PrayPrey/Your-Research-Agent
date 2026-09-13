# Conclusion

We began with a puzzle: permutation equivariant networks achieve τ > 0.93 on CNN generalization
benchmarks yet fall below 0.50 cross-architecture — not because the symmetry group is wrong for
Conv2d layers (ratio = 0.637 confirms it is right), but because the same group is fundamentally
insufficient for Linear/attention layers (ratio = 0.133, GL-dominated). The cross-architecture
transfer gap is a symptom of weight space geometry stratification, not of an architectural mismatch
that requires entirely separate methods.

This paper contributes three empirical findings that collectively characterize orbit-PE for
cross-architecture weight space learning:

**Exact symmetry validation (H-E1).** The input/output channel permutation group is a functionally
exact symmetry for all linear operator types — |Δacc| = 0.000000 across 4,500 permutation runs
on CNN Zoo and Transformer Zoo checkpoints. This result is stronger than the theoretical threshold
by orders of magnitude and confirms the mathematical foundation for orbit-PE.

**Practical computability (H-M1).** Orbit-PE is computable at 1.167× overhead relative to
sequential PE, using a unified codebase with no architecture-specific branches. The overhead is
consistent across Conv2d (1.168×), Linear (1.168×), and MultiheadAttention (1.147×) — preserving
SANE's efficiency while adding structured symmetry information.

**Layer-type variance stratification (H-M2).** The first zoo-scale measurement of permutation
vs. GL variance decomposition by layer type reveals a 4.8× stratification: Conv2d ratio = 0.637
(permutation-dominant) versus Linear ratio = 0.133 (GL-dominant) over 1,000 CNN Zoo models × 50
training epochs. The overall ratio (0.3479, below the 0.60 threshold) refutes the assumption
of permutation orbit dominance across all layer types.

The training trajectory finding — ratio decreasing from ~0.49 to ~0.28 during training — was not
anticipated and suggests that optimizers progressively exploit GL-type reparameterizations, making
the permutation variance deficit more pronounced in well-trained models.

**The path forward.** These results motivate a hybrid positional encoding: permutation orbit-PE
for Conv2d layers (where it is validated) and GL-invariant trace features for Linear/attention
layers (where GL orbits dominate). This hybrid design is the immediate next step — H-OrbitPE-v2 —
enabled by all infrastructure developed in this work: the orbit projector, variance decomposer,
and zoo-scale evaluation pipeline. Whether this hybrid encoding achieves the τ_retention ≥ 0.65
target remains the open question that this paper's findings directly ground.

The broader lesson is architectural: weight space representation methods should treat symmetry
group selection as an empirical question, measured per layer type at model zoo scale, rather
than as a theoretical assumption applied uniformly. The geometry of weight space depends on
layer structure, and cross-architecture methods must respect this stratification.
