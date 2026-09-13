# Introduction

Two neural network architectures designed for the same purpose—processing neural network weights while respecting permutation symmetry—produce measurably different internal representations. Yet this inductive bias difference only translates to performance advantages on global statistics tasks, not on local anomaly detection. This counterintuitive finding challenges the assumption that architectural differences uniformly manifest across all downstream tasks, and provides the first empirical guidance for practitioners selecting weight-space architectures.

Weight-space learning has emerged as a powerful paradigm for analyzing neural networks directly through their parameters, enabling applications from model property prediction to weight editing [Zhou et al., 2024; Navon et al., 2023]. Central to this paradigm is the observation that neural network weights exhibit permutation symmetry—reordering neurons within a layer yields functionally equivalent networks. Two prominent architectures exploit this symmetry differently: Deep Weight Space (DWS) uses equivariant layers that preserve weight locality through structured operations [Navon et al., 2023], while Neural Functional Transformers (NFT) flatten weights into tokens and apply global self-attention [Zhou et al., 2024].

**The surface problem** is well-recognized: multiple permutation-equivariant architectures exist, but no systematic comparison evaluates them on model property prediction tasks. Prior work evaluates each architecture in isolation—NFT on implicit neural representation tasks, DWS on weight editing—leaving practitioners without guidance for tasks like backdoor detection or accuracy prediction.

**The deeper problem** we identify is that different architectures encode fundamentally different inductive biases, and how these translate to task performance remains unexplored. DWS's equivariant layers should preserve spatial relationships within weight matrices, potentially advantageous for detecting localized anomalies. NFT's global attention should capture aggregate statistics across all weights, potentially advantageous for holistic property prediction. But these theoretical expectations have never been empirically tested.

**The gap** we address is the absence of controlled experiments testing whether locality (DWS) helps local pattern detection while global attention (NFT) helps holistic property aggregation. This requires matching parameters, training procedures, and evaluation metrics across architectures—infrastructure that did not exist.

Our key insight is that inductive bias differences are quantifiable through training dynamics: DWS produces weight updates with coefficient of variation (CoV) 1.44 across layers, while NFT produces more uniform updates with CoV 1.35. This 7% difference in layer-wise update variance confirms that DWS preserves locality while NFT distributes information globally. Critically, this measured difference translates to a 12.3% advantage for NFT on accuracy prediction (RMSE 82.9 vs 94.5), demonstrating that global attention directly benefits holistic property regression.

Building on this insight, we make the following contributions:

1. **First quantitative measurement of inductive bias differences** in permutation-equivariant weight-space architectures, operationalizing "locality vs global attention" through training dynamics analysis (CoV 1.44 vs 1.35).

2. **Empirical demonstration of task-dependent architecture advantage**: NFT's global attention yields 12.3% better accuracy prediction, while the hypothesized DWS locality advantage on backdoor detection remains plausible but unconfirmed due to experimental design limitations.

3. **Methodology for comparing weight-space architectures** via controlled 2×3 factorial experiments isolating architecture-task interaction effects.

We organize the paper as follows: Section 2 discusses related work on weight-space learning and inductive biases. Section 3 presents our methodology for measuring inductive bias differences and testing task-dependent performance. Sections 4-5 detail experiments and results. Section 6 discusses implications and limitations. Section 7 concludes with directions for future work.
