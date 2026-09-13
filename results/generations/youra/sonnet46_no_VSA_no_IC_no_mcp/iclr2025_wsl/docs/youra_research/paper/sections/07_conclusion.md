# Conclusion

We opened with two neural networks that compute the same function yet occupy nearly orthogonal positions in weight space — a cosine distance of 1.07. Whether a weight space encoder should treat these networks as similar is not a philosophical question but an empirical one. We have made it measurable.

## Summary

Weight space learning methods that process raw neural network weights implicitly contend with scaling and sign-flip symmetry orbits — geometric regions in weight space where functionally identical networks reside. Prior theoretical characterization established that these orbits exist; our work establishes how large they are in practice, how a state-of-the-art equivariant encoder responds to them, and what happens when you try to remove them.

Our four main findings:

1. **Orbits are geometrically large.** Scaling orbits have mean cosine distance 0.32; sign-flip orbits 1.07. Every oracle orbit pair (N=2,500) exceeds the 0.05 geometric significance threshold. The motivation for canonicalization is empirically confirmed.

2. **NFT's response is asymmetric.** The Neural Functional Transformer is measurably non-invariant to scaling orbits (embedding gap=+0.024, 95% CI=[0.023,0.024]) but approximately invariant to sign-flip orbits by construction (gap=-0.0007). This asymmetry — not designed, but emergent from row-level tokenization — implies that scaling canonicalization is the actionable preprocessing target for NFT-family encoders.

3. **Canonicalization concentrates geometric structure.** Scaling canonicalization increases PCA explained variance ratio from 0.055 to 0.086 at k=20, confirming that geometric redundancy is removed. The downstream property prediction improvement remains directionally consistent (Δρ=+0.05–0.08) but statistically undetectable at N=500.

4. **The standard sign-flip algorithm fails structurally for even d_in.** The majority-sign canonicalization produces a unique canonical form for only 14.4% of Schürholt MNIST zoo models (d_in=784, even). The 85.6% tie rate is accurately predicted by binomial combinatorics — this is a property of the architecture, not the data. Condition D in our property prediction experiments applied a non-unique transformation to the majority of models, likely explaining why the random normalization control (Condition E) outperformed full canonicalization.

## Future Directions

The most actionable next step is scaling-only canonicalization (Condition B) on the full Schürholt zoo (N≥5,000), which provides both adequate statistical power and avoids the sign-flip uniqueness issue. This single experiment can confirm or refute the core mechanism at appropriate scale. Second, implementing odd-d_in architectures (e.g., padding MNIST to d_in=785) enables a clean evaluation of sign-flip canonicalization with the uniqueness problem eliminated. Third, extending the invariance probe protocol to other encoders — DWSNets, Universal Neural Functionals, Hyper-Representations — will reveal whether the sign-flip emergent invariance is specific to NFT's row-level tokenization or a broader property of weight-tokenizing architectures.

The longer-term vision is orbit characterization as a standard diagnostic: before designing a weight space encoder, measure which symmetry orbits are large in your zoo, and probe whether your encoder naturally handles them or not. The answer should inform architecture choices, not be discovered post hoc.

## Final Thought

Two networks that compute the same function are geometrically near-orthogonal in weight space — and NFT already knows they are different. Scaling canonicalization can correct this for the symmetry where it matters most. The path from here to an empirically verified improvement is now precisely specified: more models, cleaner canonicalization, same experimental design.
