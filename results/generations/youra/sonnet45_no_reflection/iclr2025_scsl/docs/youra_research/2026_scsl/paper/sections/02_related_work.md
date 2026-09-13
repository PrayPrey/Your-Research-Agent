# Related Work

Our work sits at the intersection of spectral regularization methods, parameter-efficient fine-tuning, and stochastic trace estimation. We review each area to position our failed gradient-based Jacobian stable rank regularization approach within the broader landscape and clarify how our implementation differs from successful methods.

## Spectral Normalization of Weight Matrices

Spectral normalization has proven highly successful when applied to weight matrices directly. Miyato et al. (2018) introduced spectral normalization for GANs, constraining the spectral norm of weight matrices W to stabilize discriminator training. Their approach computes σ(W) = max_||v||=1 ||Wv|| via power iteration and rescales weights as W_SN = W/σ(W) at each training iteration. Critically, this normalization is applied to static weight tensors, not dynamic Jacobians computed via autodiff. The power iteration operates on fixed matrices with well-defined spectra, avoiding the gradient pathologies we encountered when differentiating through spectral estimation in deep computation graphs.

Our work extends spectral normalization from weight matrices to layer-wise Jacobians J_ℓ = ∂h_ℓ/∂h_{ℓ-1}, attempting to control the stable rank of representation transformations rather than individual parameter matrices. This extension introduces fundamental challenges: Jacobians are implicit functions of all upstream weights, requiring differentiation through attention mechanisms, MLPs, and LayerNorm operations. Where Miyato et al. (2018) achieved stability by normalizing isolated matrices, we attempted to regularize dynamic computational structures—a distinction that proved fatal to our implementation.

## Low-Rank Adaptation Methods

Parameter-efficient fine-tuning via low-rank methods has become standard practice for foundation model adaptation. LoRA (Hu et al., 2021) represents weight updates ΔW as low-rank decompositions ΔW = BA where B ∈ R^{d×r}, A ∈ R^{r×d}, and r << d. The rank r is treated as a fixed hyperparameter chosen before training, not a gradient-optimized metric. LoRA's success demonstrates that low-rank structures are beneficial for parameter efficiency, but it operates on small adapter matrices during fine-tuning, not on full layer Jacobians during pretraining.

ARD-LoRA (Shinwari et al., 2025) advances LoRA by introducing automatic rank determination during fine-tuning, achieving 99.3% of full fine-tuning performance with only 0.32% trainable parameters. However, ARD-LoRA optimizes rank allocation across pre-defined adapter matrices, assuming a pretrained model as given. In contrast, we attempted to control Jacobian rank during pretraining itself, aiming for models that emerge naturally ready for efficient adaptation. This pretraining-time control proved infeasible with our Hutchinson trace + power iteration approach—the measurement infrastructure returned degenerate zero values, blocking all downstream optimization.

The success of LoRA and ARD-LoRA on small, isolated low-rank matrices contrasts sharply with our failure on global Jacobian structures. This suggests a fundamental measurement-control gap: rank constraints work when applied to explicit structural parameters (adapter matrices with dimensions d×r), but fail when applied to implicit properties (Jacobian spectral rank) estimated via stochastic methods and differentiated via autodiff.

## KV Cache Compression and Long-Context Methods

Managing KV cache memory for long-context transformers has motivated recent work on learnable compression. Gelberg et al. (2026) introduce KV-CAT (KV-Compression Aware Training), which incentivizes compressible KV representations during pretraining through auxiliary losses. KV-CAT operates on activation statistics—measuring and regularizing the effective rank of key-value covariance matrices—rather than Jacobian spectral properties. Their success demonstrates that training-time objectives can shape representation compressibility, but they optimize KV structure in isolation without considering parameter efficiency or attention sparsity.

Flash Attention (Dao et al., 2022) addresses KV cache management through algorithmic optimization rather than learned compression, achieving 2-4× speedup via IO-aware exact attention computation. These methods successfully optimize specific efficiency dimensions but treat them as independent optimization problems. Our hypothesis was that these properties might be correlated manifestations of Jacobian stable rank, enabling unified optimization—but we could not test this hypothesis because the stable rank measurement infrastructure itself failed.

## Hutchinson Trace Estimation

Our implementation relied on Hutchinson's stochastic trace estimator (Bekas et al., 2007), which approximates Tr(A) via E[z^T Az] where z is a random vector (typically Rademacher or Gaussian). For an m×m matrix, Hutchinson trace requires O(1/ε²) samples for ε-accuracy in expectation. For our 768-dimensional embeddings, achieving coefficient of variation below 15% requires approximately 100+ probe vectors—but we used only 10 probes due to computational constraints, resulting in high-variance estimates that returned degenerate zero values.

Recent work on improved trace estimators like Hutch++ (Meyer et al., 2021) combines Hutchinson sampling with low-rank deflation to reduce variance. However, these methods still require careful tuning of probe counts and are typically applied to post-hoc Hessian analysis, not real-time gradient-based regularization in training loops. The coupling of noisy trace estimation with gradient descent optimization introduces instabilities not present in post-hoc analysis settings.

## State Space Models and Sub-Quadratic Architectures

Mamba-2 (Dao & Gu, 2024) achieves 2-8× speedup over transformers by replacing attention with structured state space models, demonstrating that sub-quadratic architectures can match transformer performance. MoE-Mamba (Pióro et al., 2024) combines state space models with mixture-of-experts routing, achieving faster training convergence while preserving inference efficiency. These architectural approaches achieve efficiency through structural design rather than gradient-based spectral regularization.

Importantly, Mamba's recurrent state formulation avoids the explicit KV cache present in transformers, making direct comparison of "KV compressibility" infeasible. This highlights a limitation of our Jacobian-centric hypothesis—it assumes architectural invariants (residual connections, layer-wise Jacobians) that do not hold universally across efficient model families. Alternative architectures achieve efficiency through fundamentally different mechanisms that may not be captured by Jacobian spectral properties.

## Positioning Our Work

Our work represents the first rigorous attempt to apply gradient-based residual-corrected Jacobian stable rank regularization during transformer pretraining. We tested a natural extension of spectral normalization (Miyato et al., 2018) from static weight matrices to dynamic Jacobians, combined with the parameter efficiency insights of LoRA (Hu et al., 2021) and KV compression objectives of KV-CAT (Gelberg et al., 2026). This extension failed catastrophically, revealing critical limitations of gradient-based spectral control via Hutchinson trace and power iteration in deep computation graphs.

Unlike prior work that successfully optimizes individual efficiency dimensions in isolation, we attempted unified pretraining-time control—and discovered that the measurement infrastructure itself is fundamentally unsound for this application. Our negative result complements the literature by documenting which implementation strategies fail and why, preventing wasteful replication and guiding future work toward viable alternatives like post-hoc SVD observational studies or architectural constraints that avoid stochastic spectral estimation entirely.
