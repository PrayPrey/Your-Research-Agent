# Related Work

Our work builds on three research threads: weight-space learning for property prediction, permutation-equivariant neural architectures, and inductive biases in deep learning.

## Weight-Space Learning

The idea of learning from neural network weights directly has gained traction with the availability of large model collections. Schürholt et al. [2022] introduced hyper-representations—learned embeddings of model weights trained via contrastive learning. Their work demonstrated that weight-space features can predict properties like accuracy and robustness, establishing the feasibility of the paradigm. However, their architecture uses standard attention mechanisms without explicit permutation equivariance guarantees.

Unterthiner et al. [2020] pioneered predicting generalization from weights alone using simple statistics (mean, variance, norm of weight tensors). While computationally efficient, such hand-crafted features cannot capture complex weight-function relationships. The Model Zoo dataset [Schürholt et al., 2022] provided a benchmark with 50K+ models trained under varying conditions, enabling systematic evaluation of weight-space methods. Our work uses this dataset to study scale-dependent properties of equivariant versus non-equivariant architectures.

## Permutation-Equivariant Architectures

Zhou et al. [2023] introduced Neural Functional Networks (NFN), which process neural network weights using equivariant layers that respect the permutation symmetry of hidden neurons. Their NPLinear layer linearly transforms weight tensors while maintaining equivariance, and HNPPool produces permutation-invariant representations via pooling. NFN demonstrated state-of-the-art performance on weight-space generation tasks.

However, NFN's original evaluation focused primarily on generation rather than property prediction, and systematic comparison against matched-capacity non-equivariant baselines was limited. Our work addresses this gap by evaluating sample efficiency specifically—asking whether equivariant architectures provide advantages that persist across data scales or whether non-equivariant methods can catch up given sufficient data.

Related architectures include Graph Neural Networks on weight-space graphs [Kofinas et al., 2024] and the SANE framework for scalable weight-space learning [Andreis et al., 2024]. These approaches handle permutation symmetry through different mechanisms but share the goal of exploiting weight-space structure.

## Inductive Biases and Symmetry

The role of inductive biases in deep learning has been extensively studied. Cohen and Welling [2016] showed that encoding symmetries via equivariant layers improves sample efficiency for image classification. Battaglia et al. [2018] argued that relational inductive biases are crucial for structured domains. The general principle—that architectural constraints matching problem structure improve learning—is well established.

Less understood is whether such biases are *necessary* or merely *convenient*. Universal approximation theorems suggest that given infinite data, any continuous function can be learned without explicit structural constraints. Our work provides empirical evidence for a specific case: permutation invariance in weight-space learning cannot be learned from data regardless of scale, suggesting that some symmetries require architectural encoding.

## Positioning Our Work

Prior work established the feasibility of weight-space learning (hyper-representations), introduced equivariant architectures for weights (NFN), and provided benchmarks (Model Zoo). What remains unclear is whether equivariant architectures provide lasting advantages or whether the gap closes at scale. We address this by:

1. Conducting the first systematic sample efficiency study across scales (1K to 40K models)
2. Introducing mechanism verification via probe invariance tests
3. Demonstrating that MLPs achieve high R² without learning invariance—dissociating task performance from representation quality

This reveals that the equivariance benefit is structural, not merely about sample efficiency in early training.
