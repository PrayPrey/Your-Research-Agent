# 2. Related Work

We situate our work within three streams: equivariant weight-space encoders, plain weight-space learning with augmentation, and the theoretical expressivity of permutation-equivariant networks.

## 2.1 Equivariant Weight-Space Encoders

The observation that neural network weights carry a permutation symmetry — interchanging neurons within a layer leaves the function unchanged — motivates encoder architectures that respect this symmetry by construction. **DWSNets** [Navon et al., 2023] introduced the first permutation-equivariant layers for homogeneous MLP weight spaces, achieving R²≈0.89 for accuracy prediction on a private MNIST model zoo. **GNN-NFN** [Kofinas et al., 2024] extended this idea to diverse architectures by treating neural networks as computational graphs (nodes = neurons, edges = weight matrices) and applying graph neural network operations that are equivariant to the permutation group of each layer. GNN-NFN achieves state-of-the-art property prediction across multiple architecture families. **NFN** [Zhou et al., 2023] and its universal extension [Zhou, Finn, and Harrison, 2024] auto-construct equivariant layers for arbitrary weight spaces, enabling rapid prototyping of equivariant encoders for new architectures. **Monomial-NFN** [Tran et al., 2024] further extends symmetry handling to scaling and sign-flipping, achieving 34% parameter reduction via theory-guided construction.

However, none of these works conduct a controlled comparison with plain encoders on shared train/test splits, and none report sample efficiency curves across systematically varied training set sizes. Their performance is measured at full-data scale on custom or private splits, which prevents direct comparison with plain baselines or cross-paper efficiency claims.

## 2.2 Plain Weight-Space Learning and Augmentation

The ModelZooDataset [Schürholt et al., 2022] provides the standardized model zoos used in our study: CIFAR-10 CNN zoo (~9,000 models) and MNIST MLP zoo (~4,860 models), with ground-truth performance metrics and reproducible train/test splits. Building on this resource, **Schürholt et al. [2021]** demonstrated that self-supervised representation learning on flattened weights can predict model accuracy (R²≈0.83) and generalization gap on the ModelZooDataset MNIST zoo — establishing that plain encoders are competitive baselines that should not be dismissed. Meynent et al. [2025] showed that combining behavioral and structural signals in weight autoencoders outperforms structure alone, suggesting the representation space contains exploitable information beyond raw weights.

Permutation augmentation — randomly permuting neuron orderings during training to force the encoder to learn approximate invariance from data — is analogous to random crops in image learning: it achieves some but not all benefits of architectural invariance [general augmentation literature]. Its role as an intermediate condition between plain and structural equivariance has been discussed conceptually but never tested in a controlled weight-space learning study. Our work provides the first such test.

These plain encoder works share a key limitation: no equivariant encoder comparison on the same shared splits. The efficiency comparison is impossible without common ground.

## 2.3 Expressivity Theory and Sample Complexity

**Dayan, Eitan, and Maron [2026]** proved a striking result: all permutation-equivariant weight-space networks — regardless of architecture — are equivalent in expressivity. Their theorem implies that equivariant and plain encoders share the same function class ceiling when data is abundant. However, expressivity equivalence does not imply sample complexity equivalence. A smaller, symmetry-consistent hypothesis space can be traversed with fewer training examples even if it is ultimately as expressive as the unconstrained space — analogous to why CNNs (shift-equivariant) outperform plain MLPs on images even though both classes are universal approximators.

Our work provides the empirical counterpart to Dayan et al.'s theoretical result: we measure the practical sample complexity gap (6.8×) and show it is data-regime dependent, consistent with the theoretical prediction that the gap should close at full data (Δ<0.01 R² at N=full; see Section 5.4). The N=100 crossover, where augmentation dominates structure, provides new constraints on theories of when structural inductive biases activate.

Herrmann, Faccio, and Schmidhuber [2024] contributed the first RNN model zoo datasets, finding that functionalist representations outperform mechanistic ones — an insight that parallels our finding that data-level augmentation can outperform structural encoding at small zoo sizes, where the mechanistic (equivariant) approach lacks sufficient signal.

## 2.4 Positioning

Our work is the first to: (1) compare equivariant and plain weight-space encoders on shared ModelZooDataset splits, (2) measure sample efficiency via systematic training size ablation, (3) include permutation augmentation as an explicit intermediate condition, and (4) report a data-regime crossover that qualifies the conventional wisdom that equivariant inductive bias helps most at low data.
