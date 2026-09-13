# Related Work

## Weight Space Property Prediction

The task of predicting held-out model properties from neural network weights was established by Unterthiner et al. [2020], who showed that layer-wise statistics (mean, variance, higher moments of weight distributions per layer) achieve Spearman ρ ≈ 0.9 on simple model zoo tasks. While remarkably effective as a baseline, layer statistics are permutation-agnostic — they ignore the geometric structure of weight space entirely. They establish the task's feasibility but provide no information about which aspects of weight space geometry encode property-relevant information.

The Schürholt et al. [2022] model zoo dataset introduced a large-scale benchmark of diverse MLP populations trained with varying hyperparameters, making systematic comparison of weight space encoders possible. Schürholt et al. [2021] further proposed Hyper-Representations: self-supervised pretraining on model weight populations to learn shared representations. These methods treat weight populations as datasets for unsupervised learning but do not directly address symmetry structure.

## Equivariant and Invariant Encoders for Weights

A theoretically principled line of work builds encoders that are *equivariant* or *invariant* to the symmetries of weight space. Zhou et al. [2023] introduced Neural Functional Networks (NFN), characterizing the complete class of linear maps equivariant to neuron permutations for MLP weights. Their Neural Functional Transformer (NFT) variant applies attention over weight tokens, achieving state-of-the-art property prediction while preserving permutation equivariance. NFT achieves Spearman ρ ≈ 0.11 on the Schürholt MNIST zoo — well below the layer statistics baseline (ρ ≈ 0.9), suggesting that permutation equivariance alone does not solve the problem.

Navon et al. [2023] extended the theoretical analysis to the full symmetry group of MLP weight spaces, including *scaling* and *sign-flip* symmetries beyond permutation. For a 2-layer ReLU MLP with hidden dimension h, the scaling symmetry group has dimension h (one free scale per hidden neuron) while the sign-flip symmetry group has order 2^h. Navon et al.'s DWSNets architecture builds in equivariance to these additional symmetries, but is restricted to networks with M≥3 layers and is incompatible with the M=2 Schürholt MNIST zoo. Critically, while the theoretical characterization is complete, **no prior work has empirically measured the geometric diameter of scaling or sign-flip orbits in a real model zoo**, nor has any prior work probed whether existing equivariant encoders like NFT are naturally invariant to these orbits in practice.

Our work bridges this gap: we provide the first empirical orbit diameter measurements and the first mechanistic probe of NFT's symmetry handling, complementing the theoretical characterization of Navon et al. [2023] with data-grounded analysis.

## Symmetry and Canonicalization in Neural Networks

The role of weight space symmetries in neural network optimization and representation has been studied from multiple angles. Ainsworth et al. [2022] showed that permutation symmetry can be exploited via "Git Re-Basin" to reduce loss barriers between independently trained networks, suggesting that permutation orbits have significant geometric diameter in practice. Entezari et al. [2022] proved that, with permutation alignment, loss barriers between networks approach zero under mild conditions. These results motivate orbit-aware processing but focus on permutation, not scaling or sign-flip.

Symmetry canonicalization as a preprocessing step has been proposed in the context of molecular geometry (where canonical atom orderings improve learning) and 3D point clouds (where SO(3) canonicalization removes rotational ambiguity). In weight space, canonicalization was proposed theoretically by Navon et al. [2023] but not empirically evaluated for property prediction. Our work provides the first such evaluation, including a structural limitation analysis of the majority-sign algorithm that has not appeared in prior literature.

## Model Zoo Benchmarks

Kofinas et al. [2024] proposed Universal Neural Functionals (UNF), extending equivariant processing across architectures. While UNF addresses the cross-architecture generalization gap, it still operates on raw weights without addressing scaling or sign-flip canonicalization. Our work is orthogonal: canonicalization is a preprocessing step applicable to any encoder, including UNF and NFT, and our probe methodology can be applied to characterize any encoder's symmetry handling.

**Positioning.** We do not compete with NFN, DWSNets, or UNF on property prediction performance. Rather, we add an empirical measurement layer that all these methods implicitly need: orbit characterization tells practitioners which symmetries require canonicalization, how large the orbits are, and whether a given encoder already handles them. For NFT specifically, our finding that sign-flip invariance emerges naturally while scaling invariance does not is immediately actionable — it suggests that scaling canonicalization is the productive preprocessing target for NFT-family encoders.
