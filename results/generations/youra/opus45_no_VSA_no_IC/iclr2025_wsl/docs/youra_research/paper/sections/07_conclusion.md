# Conclusion

Can neural networks learn to predict model accuracy directly from weights? Our experiments provide a decisive answer: only if they respect permutation symmetry.

We compared three approaches to weight-to-accuracy prediction across training sizes from 100 to 5,000 models. The permutation-equivariant NFN architecture achieves R² > 0.99 at all sample sizes. The non-equivariant MLP baseline fails categorically—R² < 0 at every training size, including N=5000. The 2.5 R² gap at N=500 is not a data efficiency advantage; it is the difference between learning and complete failure.

The original framing—that equivariance reduces sample requirements—understated the finding. Our results show equivariance is a prerequisite, not an optimization. Non-equivariant methods cannot generalize across the exponentially many permutation-equivalent weight configurations that represent identical network functions.

This has direct implications for weight-space learning. Systems that process neural network weights—for model selection, zoo curation, or architecture search—must either compute permutation-invariant features or use permutation-equivariant architectures. Treating weights as arbitrary vectors is fundamentally incompatible with the structure of the problem.

The 2.5 R² gap we observed is not just large—it represents the boundary between methods that work and methods that cannot work. For practitioners building weight-space tools, respecting permutation symmetry is not optional.
