# Related Work

Our work sits at the intersection of weight-space learning, permutation equivariance, and representation learning across neural network architectures. We organize related work by the key challenges they address and highlight where gaps remain.

## Permutation Symmetries in Neural Networks

Neural networks exhibit well-documented permutation symmetries arising from the exchangeability of computational units. Hecht-Nielsen [1990] and Sussmann [1992] established that hidden unit ordering does not affect network function. The Lottery Ticket Hypothesis [Frankle & Carbin, 2019] demonstrated that sparse subnetworks maintain these symmetries during training. Recent work has leveraged these symmetries for model analysis and manipulation, but primarily within single architectures where the symmetry groups are well-understood.

Git Re-Basin [Ainsworth et al., 2022] exploits permutation symmetries for weight-space alignment by solving an explicit combinatorial optimization problem to find permutations that minimize distance between model weights. This approach successfully merges models trained from different initializations, but the explicit search is computationally expensive and has only been demonstrated on small models within single architecture families. Our approach differs by attempting to learn equivariance through gradient-based training, though our failure suggests explicit search may be necessary.

## Weight-Space Learning and Neural Functional Networks

Neural Functional Networks (NFN) [Zhou et al., 2024] introduced permutation-equivariant architectures for learning from model zoos, demonstrating strong performance on implicit neural representation (INR) datasets. NFN uses Deep Sets [Zaheer et al., 2017] as a backbone to process sets of weights in a permutation-invariant manner, achieving significant improvements over function-space baselines. However, NFN's evaluation focuses exclusively on homogeneous model populations—collections of INRs with identical architectures. This leaves the heterogeneous case (CNNs, Transformers, RNNs) completely unexplored.

Our work directly tests whether NFN's approach extends to heterogeneous populations. We augment Deep Sets with architecture embeddings to provide family-specific context and add an explicit MSE-based equivariance loss to encourage cross-architecture abstraction. The complete failure of this natural extension reveals that the homogeneous-to-heterogeneous gap is wider than anticipated, suggesting fundamental differences between intra-architecture and cross-architecture permutation groups.

## Model Merging and Weight-Space Arithmetic

Task arithmetic [Ilharco et al., 2022] and model merging techniques [Wortsman et al., 2022; Matena & Raffel, 2022] demonstrate that linearly combining model weights can transfer capabilities or improve performance. These methods work within the weight space directly, performing operations like $\theta_{\text{merged}} = \alpha \theta_1 + (1-\alpha) \theta_2$. However, all successful applications require models to have identical architectures—the weights must align element-wise for linear combinations to be meaningful.

Our quotient-level approach aims to enable merging across architectures by first projecting weights into a shared canonical space where linear operations become meaningful. While model merging shows that weight-space manipulations can work, it also highlights the constraint: architecture-specific coordinate systems must be factored out. Our failure to achieve this factorization suggests the quotient space hypothesis may require per-family canonicalization with post-hoc alignment rather than a single shared space.

## Representation Learning and Equivariance

Group-equivariant neural networks [Cohen & Welling, 2016] build equivariance directly into architectures through group convolutions rather than learning it through loss functions. This explicit construction guarantees equivariance by design. Slot Attention [Locatello et al., 2020] learns object-centric representations using attention-based set encoders, demonstrating that learned attention can outperform fixed aggregation (sum/mean pooling) for compositional structure.

Our MSE equivariance loss attempts to learn permutation invariance through gradient descent, similar to how contrastive learning [Chen et al., 2020] learns invariance to augmentations. However, our 0.00% kernel robustness suggests that MSE-based objectives are insufficient for weight-space permutations. This aligns with the success of explicit group-equivariant architectures and suggests that learned equivariance for weight space may require stronger objectives—contrastive learning with positive (permuted) and negative (different model) pairs, or explicit group constraints.

## Meta-Learning and Model Zoo Analysis

Meta-learning approaches [Finn et al., 2017; Nichol & Schulman, 2018] learn across tasks by processing model parameters, but typically operate on models with fixed architectures trained on different datasets. Model zoo analysis [Unterthiner et al., 2020] studies statistical properties of large collections of trained models, but focuses on function-space embeddings (outputs on probe inputs) rather than weight-space representations.

Our work differs by directly encoding weight-space structure across architectural boundaries. While function-space methods sidestep permutation symmetries by evaluating models on fixed inputs, they lose the ability to perform weight-space manipulations like merging or interpolation. Our failure suggests that for cross-architecture applications, function-space embeddings may currently be more viable than weight-space canonicalization.

## Positioning Our Contribution

No prior work has systematically tested cross-architecture quotient-level canonicalization or identified the specific failure modes that prevent simple extensions of homogeneous methods from working. Git Re-Basin succeeds through explicit search but doesn't scale; NFN succeeds on homogeneous populations but doesn't extend; model merging works but requires identical architectures. Our negative result fills this gap by demonstrating that Deep Sets + architecture embeddings + MSE equivariance loss fundamentally fails, and identifying root causes: equivariance loss design inadequacy, architecture embeddings harmful, and dimensionality underestimation.

This failure analysis provides concrete guidance for future work: contrastive learning for stronger equivariance signal, pure architecture-agnostic encoders, validation on homogeneous populations first, and potentially per-family quotient spaces with post-hoc alignment. By documenting this dead end, we prevent the community from wasting effort on similar approaches and point toward viable research directions.
