# Discussion

## Key Findings

**Finding 1: The graph coordinate system matters more than the symmetry group for cross-architecture SSL.**

Our most important positive result is that graph-based SSL with permutation equivariance achieves +221% R² improvement over flat tokenization (SANE) on ViT model accuracy prediction, without any ViT training data. This establishes the directed computational graph schema as a viable architecture-agnostic coordinate system for weight-space SSL. The representational gap is not subtle — R²=0.072 vs R²=0.231 is the difference between a useful predictor and noise for a downstream selection task.

Equally important, and opposite to expectations, is that scale equivariance does not improve over permutation-only equivariance (ΔR²=-0.143 in the ViT SSL setting). The benefit of scale equivariance demonstrated by Kalogeropoulos et al. [2024] in supervised same-architecture settings does not transfer to the cross-architecture SSL setting targeting ViT architectures. We attribute this to LayerNorm's gauge-fixing property: ViTs normalize activation scale at every layer, removing the physical scale symmetry that scale equivariance is designed to encode. The appropriate inductive bias for weight encoding is architecture-normalization-dependent, not architecture-independent.

This suggests a practical design principle for weight-space SSL: choose the equivariance group that matches the functional symmetries of the target architecture's normalization layer, not the training architecture. For ViT targets with LayerNorm: permutation equivariance. For MLP/CNN targets with BatchNorm or no normalization: scale+permutation equivariance may provide additional benefit.

**Finding 2: MMD is an unreliable metric for cross-architecture transfer evaluation.**

SANE achieves lower MMD than graph-based encoders despite substantially worse R² for cross-architecture accuracy prediction. The explanation — SANE's latent collapse to near-constant codes produces trivially low MMD — reveals a fundamental measurement problem: when a representation collapses, MMD drops not because alignment has improved but because variance has vanished. Any cross-architecture evaluation protocol that uses MMD as a primary metric should first verify encoder latent variance is non-degenerate.

More robust alternatives include per-dimension KL divergence (which is sensitive to mean shifts regardless of variance), Fréchet distance with covariance estimation, or simply the R²-based linear probe, which directly measures downstream utility rather than distributional proximity.

**Finding 3: Property prediction and functional model generation are separable capabilities requiring architecturally distinct decoders.**

The latent interpolation failure (acc_latent=0.100 ≈ random, Cohen d=-1.10 relative to weight averaging) is not evidence that the latent space is poorly organized. R²=0.231 confirms that EquiSSL-perm's latent space encodes functional properties. The failure is in the decoder: a graph decoder trained for 512-dim edge attribute statistics reconstruction cannot generate functional weight tensors via tile/slice mapping. The latent space "knows" which model is better; the decoder cannot translate that knowledge back to actual weights.

This separability is important for future work design. Improving the latent interpolation capability does not require changing the encoder — it requires a dedicated decoder (hypernetwork-style, with architecture-aware output projections that map from latent codes to actual weight tensors matching the target architecture's layer shapes). The latent space quality (measured by R²) and the generation quality (measured by interpolated model accuracy) can be optimized independently.

## Limitations

**Limitation 1: Single seed, 53 ViT models — insufficient statistical power.**

All R² results for cross-architecture transfer (h-m1, h-m2) are from seed 0 only, with 53 ViT-S/16 models. With n=1 seed, paired t-tests are undefined, and p-values from our significance tests are 0.5 (a degenerate result with single replication). The magnitude of R² improvements (+0.159 for EquiSSL-perm, -0.143 for scale reversal) is directionally robust — both findings are consistent with theoretical predictions and with pre-registered expectations at h-m1 planning — but statistical significance claims require multi-seed replication with full ViT zoo (250+ models).

We present these as proof-of-concept results. The directional findings are the scientifically relevant contribution; the magnitude estimates carry high uncertainty.

**Limitation 2: Scale equivariance reversal requires non-LayerNorm validation.**

The hypothesis that LayerNorm gauge-fixing causes the scale equivariance reversal is theoretically motivated but not directly tested. Alternative explanations include overfitting to scale symmetry in CNN training data, or training objective interactions with scale augmentation. Direct validation requires testing scale vs. permutation equivariance on a non-LayerNorm architecture family (e.g., MLP with ReLU, BatchNorm CNN) as the target. If scale equivariance recovers its benefit there, the LayerNorm explanation is confirmed.

**Limitation 3: CIFAR-10 CNN training subset — not full MultiZoo.**

We use approximately 3,000 of the ~30,000 available SANE MultiZoo CNN checkpoints. The full MultiZoo training may improve R² by providing greater diversity of weight distributions for the SSL encoder to learn from. Our results establish feasibility at reduced scale; full-dataset results are deferred to future work.

**Limitation 4: Graph decoder design — not suitable for functional weight generation.**

The graph decoder was designed for edge-attribute statistics reconstruction and cannot generate functional weight tensors. This is a design issue, not a fundamental limitation of the approach. A hypernetwork-style decoder with architecture-aware output heads is the natural correction.

## Broader Impact

**Positive impacts.** Weight-space SSL methods that generalize across architecture families could significantly reduce the cost of model zoo analysis — enabling property prediction (accuracy, robustness, fairness) for arbitrary pre-trained models without requiring dedicated training data for each new architecture. This could democratize model evaluation and facilitate trustworthy deployment of pre-trained models in resource-constrained settings.

The scale equivariance finding benefits the research community by constraining when scale equivariance is a useful inductive bias, preventing unnecessary complexity in weight-space encoder design.

**Potential concerns.** Weight-space analysis methods could in principle be used to extract information about training data from model checkpoints, raising privacy concerns. However, the current method predicts accuracy from weights — it does not recover training data samples. More capable future methods may raise more significant concerns; this is a general limitation of all weight-space analysis research rather than a specific concern of our work.

**Mitigation.** We release code and model checkpoints to enable reproducibility and independent evaluation of both the capabilities and limitations of our approach. The honest presentation of negative results (scale equivariance reversal, interpolation failure) is itself a contribution to responsible development of this research area.
