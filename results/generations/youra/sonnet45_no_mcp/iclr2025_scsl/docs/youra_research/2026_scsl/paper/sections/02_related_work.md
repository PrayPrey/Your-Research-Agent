# Related Work

Our work provides geometric foundations for understanding spurious correlation exploitation, complementing existing robustification methods. We position our contribution at the intersection of three research areas: spurious correlation mitigation, loss landscape analysis, and sharpness-aware optimization.

## Spurious Correlation Robustification

Group Distributionally Robust Optimization (Group-DRO) [Sagawa et al., 2020] trains models to minimize worst-group loss, achieving 75-80% worst-group accuracy on Waterbirds compared to ERM's 60-75%. Invariant Risk Minimization (IRM) [Arjovsky et al., 2019] learns representations that are invariant across training environments. Just Train Twice (JTT) [Liu et al., 2021] identifies error-prone samples and upweights them during retraining. These methods effectively *fix* the spurious correlation problem but require either group labels during training (Group-DRO, JTT) or multiple training environments (IRM), and crucially, they do not explain *why* standard ERM fails.

Our geometric analysis provides the mechanistic foundation these methods implicitly address: Group-DRO works because it reduces curvature concentration in sharp outlier subspaces (as we validate in Section 4), shifting optimization toward flatter regions associated with core features. While Group-DRO is a solution, we explain the optimization dynamics that necessitate it.

## Loss Landscape Analysis

The geometry of neural network loss landscapes has been extensively studied. Li et al. [2018] introduced filter normalization for loss landscape visualization, revealing that ResNets with skip connections produce landscapes with flat, well-connected minima. Sagun et al. [2017] analyzed Hessian eigenvalue spectra using Marchenko-Pastur random matrix theory, showing that outlier eigenvalues correspond to data structure through Gauss-Newton decomposition. Garipov et al. [2018] demonstrated that distinct local minima are often mode-connected through low-loss paths, enabling Fast Geometric Ensembling (FGE).

These foundational works study how architecture and optimization affect landscape geometry *generally*. We apply their tools—Marchenko-Pastur bulk edge detection, Hessian eigenvalue analysis, mode connectivity sampling—to the spurious correlation domain *specifically*, revealing that robust versus non-robust solutions occupy geometrically distinct regions within the connected landscape manifold. Our novel synthesis is not in the methods but in their application to understanding distribution shift robustness.

## Sharpness-Aware Optimization

Sharpness-Aware Minimization (SAM) [Foret et al., 2020] explicitly seeks flat minima by perturbing weights in the direction of maximum loss increase, achieving better generalization across benchmarks. Keskar et al. [2016] showed that sharp minima correlate with poor generalization, motivating flatness-seeking methods. However, SAM targets *scalar* flatness—minimizing maximum eigenvalues regardless of direction—making it feature-agnostic.

Our approach analyzes curvature *orientation* relative to subgroup gradients, not just magnitude. We measure what fraction of minority-group gradient variance falls into sharp curvature subspaces (outlier eigenvectors), revealing spurious correlation structure that scalar flatness metrics miss. SAM may reduce overall sharpness, but our diagnostic reveals *whether* that sharpness reduction addresses spurious features versus core features—a distinction critical for distribution-shift robustness.

## Spurious Correlation Detection

GEORGE [Sohoni et al., 2020] detects spurious correlations by clustering error-prone samples, requiring iterative retraining. Learning from Failure (LfF) [Nam et al., 2020] trains a biased model to identify shortcut features. Environment Inference for Invariant Learning (EIIL) [Creager et al., 2021] infers latent environments from training data. These methods focus on *detecting* which samples or features are spurious, often requiring multiple training runs or environment diversity.

Our geometric diagnostic operates post-training on a single converged model: compute Hessian eigenvalues, identify Marchenko-Pastur bulk edge, measure minority-gradient alignment to outlier subspace. No retraining, no environment diversity, no iterative refinement—just loss landscape analysis. This complements detection methods by providing a geometric explanation for *why* certain features are shortcuts: they create sharp curvature that SGD avoids.

## Positioning Our Contribution

Existing work has established *what* spurious correlations are (dataset biases exploited by ERM), *how to mitigate* them (Group-DRO, IRM, SAM), and *how to detect* them (error clustering, biased models). Our contribution addresses the missing foundation: *why* gradient-descent optimization preferentially exploits spurious correlations. We provide a geometric diagnostic framework (Marchenko-Pastur alignment) with partial mechanistic validation (curvature concentration + SGD directional bias), enabling label-free detection and optimization-informed intervention design. We build on established tools (Sagun's Hessian analysis, Li's landscape visualization, Garipov's mode connectivity) and apply them to reveal the optimization dynamics underlying spurious correlation exploitation.
