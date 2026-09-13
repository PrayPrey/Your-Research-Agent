# Conclusion

We began with a counterintuitive bet: that a neural network encoder trained on nothing but small MLP and CNN checkpoints could predict ViT model accuracy better than the state of the art — without ever seeing a transformer. Our experiments confirm the bet pays off, and the mechanism is both simpler and more surprising than we anticipated. It is the coordinate system, not the symmetry group.

Graph-based SSL with permutation equivariance achieves R²=0.231 on 53 held-out ViT-S/16 ImageNet models, versus R²=0.072 for SANE's flat tokenization — a +221% improvement with no ViT training data. The directed computational graph schema, representing neurons and scalar weights with shared relational structure across architecture families, provides the architecture-agnostic coordinate system that flat tokenization cannot. This is the primary contribution of this work.

The secondary contribution is a principled negative result: scale+permutation equivariance (ScaleGMN) does not improve over permutation-only (neural-graphs) in the ViT cross-architecture SSL setting (ΔR²=-0.143). We attribute this to LayerNorm's gauge-fixing property, which removes the physical scale symmetry that scale equivariance encodes. This finding constrains when scale equivariance is a useful inductive bias — an empirical result with clear theoretical grounding that benefits practitioners designing weight-space encoders.

The third contribution is methodological: we identify and characterize the MMD confounding problem in cross-architecture SSL evaluation, where representation collapse produces artificially low MMD without improving actual transfer quality. We recommend R²-based evaluation as more reliable for assessing cross-architecture property prediction utility.

**Future Directions.** Three threads emerge directly from our experimental evidence:

*Normalization-conditional equivariance.* Our results suggest that the appropriate symmetry group for weight encoding is architecture-normalization-dependent: permutation for LayerNorm architectures (ViT), scale+permutation for post-ReLU MLPs or BatchNorm CNNs. Direct experimental validation requires training encoders on CNN/MLP training zoos and evaluating on non-LayerNorm test zoos — if scale equivariance recovers its benefit there, the gauge-fixing hypothesis is confirmed.

*Multi-seed, full-zoo statistical validation.* Our results are based on a single seed and 53 ViT models — proof-of-concept level evidence. Full evaluation with 5 seeds and 250+ ViT models (the full ViT Model Zoo) is required to establish statistical significance and calibrate magnitude estimates. Training on the full SANE MultiZoo (~30k models) rather than our 3k-model subset is also expected to improve R².

*Functional decoder design for weight generation.* The latent interpolation failure is a decoder issue, not a latent space issue. The current graph decoder, trained for edge-attribute statistics reconstruction, cannot generate functional weight tensors. A hypernetwork-style decoder with architecture-aware output projections — mapping from latent codes to actual weight matrices — is the natural next step, and may unlock the latent interpolation capability that our R² results suggest is encoded in the latent space.

In a field that increasingly treats model checkpoints as data, the ability to analyze an arbitrary new architecture using only existing model zoo data is a fundamental primitive. This work demonstrates that the primitive exists — the coordinate system is the key — and opens a research agenda for understanding exactly when and how it works.
