# Conclusion

We asked a simple question: does respecting neural network structure improve weight embedding quality? The answer is unambiguously yes.

Through systematic ablation on the CIFAR-10 Model Zoo (N = 61,335), we demonstrate that layer-wise encoding—computing per-layer statistics rather than flattening all weights—improves accuracy prediction correlation by Δr = 0.126 (from r = 0.421 to r = 0.547, p < 0.001). This 30% relative improvement holds across all five random seeds tested.

The finding has a simple interpretation: neural network layers encode different functional abstractions, and their weight statistics reflect these differences. Flattening destroys this hierarchy. Preserving layer boundaries preserves predictive information.

Our ablation ladder provides a methodology for future comparisons. By isolating one structural bias per step (none → layer-aware → aligned → equivariant), we enable direct measurement of each component's contribution. We complete two of four planned steps; the remaining evaluation requires GPU infrastructure for Git Re-Basin alignment at scale.

Three practical implications emerge:

1. **Layer-wise encoding should be the default baseline** for weight embedding, not flattening
2. **Structural preservation matters** in weight space as in input space
3. **Controlled ablation enables fair comparison** across embedding methods

Looking forward, the goal is universal weight embeddings: representations that generalize across architectures, predict multiple properties, and enable efficient model selection from massive model zoos. Our results suggest that structural inductive biases—starting with layer boundaries—are essential ingredients.

The simplest structural bias we tested provided substantial benefit. We expect richer structural biases (alignment, equivariance) to provide further improvements, pending computational validation. The ablation framework we establish enables systematic evaluation of these and future embedding innovations.
