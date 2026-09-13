# Related Work

## Influence Functions and Data Attribution

Influence functions (Koh & Liang, 2017) estimate training example influence by approximating leave-one-out retraining through the inverse Hessian-vector product (IHVP). While theoretically principled, IHVP computation is prohibitively expensive for modern deep networks. Subsequent work developed three main approximation strategies, each trading different accuracy-efficiency characteristics.

**First-order methods** bypass curvature entirely. TracIn (Pruthi et al., 2020) approximates influence via gradient dot-products at training checkpoints, achieving O(1) complexity per example pair. While computationally attractive, TracIn ignores second-order information that may be crucial for accurate attribution.

**Curvature approximation methods** factorize or approximate the Hessian. EK-FAC (Grosse et al., 2023) extends KFAC's Kronecker factorization to influence estimation, scaling to 52B parameter LLMs with 0.85 Spearman correlation. However, their evaluation focused exclusively on decoder-only architectures (LLaMA-2), leaving encoder behavior unexplored.

**Random projection methods** project gradients to lower-dimensional spaces. TRAK (Park et al., 2023) uses random feature regression to estimate datamodel coefficients, achieving state-of-the-art accuracy on vision and language benchmarks. Their evaluation included BERT and CLIP, but tested each architecture in isolation without controlled comparison.

A critical gap exists: no prior work has systematically compared these methods across architectures at matched conditions. Each method was validated on its "home" architecture—EK-FAC on decoders, TracIn and TRAK on various models—without controlling for architecture-specific effects.

## Transformer Architectures and Attention Structure

The transformer architecture (Vaswani et al., 2017) uses attention mechanisms that fundamentally differ between encoder and decoder variants. Encoder-only models (Devlin et al., 2019) employ bidirectional attention where each token attends to all positions. Decoder-only models (Radford et al., 2019) use causal attention masks that prevent attending to future tokens.

This architectural difference has implications for gradient computation. Bidirectional attention creates O(n²) dense attention weights, while causal attention computes only O(n²/2) non-zero weights. Prior work has noted that causal structure creates "block-diagonal-ish" attention Jacobians (Grosse et al., 2023), but the downstream effect on attribution accuracy remained unexplored.

## Benchmarking Data Attribution

Mislabeled detection is a standard benchmark for data attribution methods (Koh & Liang, 2017; Pruthi et al., 2020; Park et al., 2023). Synthetic label noise is injected into training data, and methods are evaluated by their ability to rank mislabeled examples highly using influence scores. This task directly tests whether attribution identifies harmful training examples.

Other benchmarks include leave-one-out correlation (datamodels), proponent identification, and data cleaning effectiveness. We focus on mislabeled detection as it is well-established and allows direct comparison with prior work.

## Our Contribution

We provide the first systematic matched cross-architecture comparison of data attribution methods. By controlling for model size (both ~110-125M parameters), depth (both 12 layers), task (SST-2 classification), and training procedure (identical hyperparameters), we isolate the effect of attention structure on attribution performance. This reveals architecture-method interactions that were invisible in prior single-architecture evaluations.
