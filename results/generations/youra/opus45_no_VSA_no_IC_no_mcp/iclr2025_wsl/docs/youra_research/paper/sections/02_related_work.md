# Related Work

We review three areas central to our investigation: permutation-equivariant architectures for weight-space learning, inductive biases in neural architectures, and model property prediction benchmarks.

## Permutation-Equivariant Weight Processing

Neural network weights exhibit permutation symmetry: reordering neurons within a hidden layer produces functionally equivalent networks. Early work by Zaheer et al. [2017] established Deep Sets as a foundational framework for processing set-structured inputs while respecting permutation equivariance. This insight was extended to weight matrices by Navon et al. [2023], who introduced Deep Weight Space (DWS) with equivariant layers that process weights while preserving their spatial structure within each layer.

Concurrently, Zhou et al. [2024] proposed Neural Functional Transformers (NFT), which tokenize weight matrices and apply transformer self-attention across all weight tokens. NFT demonstrated strong performance on implicit neural representation (INR) classification tasks, leveraging global attention to capture relationships across the entire weight space.

**Limitation we address:** DWS and NFT were evaluated on different tasks (weight editing vs INR classification), preventing direct comparison. No study has tested whether their architectural differences—locality-preserving layers vs global attention—translate to task-dependent performance advantages on model property prediction.

## Inductive Biases in Neural Architectures

The role of inductive biases in deep learning is well-established. Convolutional neural networks encode translation equivariance and locality, providing advantages on image tasks with limited data [LeCun et al., 1998]. Vision Transformers (ViT) lack explicit locality bias but can learn effective representations given sufficient data [Dosovitskiy et al., 2020]. This locality-vs-attention trade-off has been extensively studied in vision, with findings suggesting locality helps sample efficiency while global attention helps capture long-range dependencies [Chen et al., 2021].

Analogous trade-offs exist in weight-space learning. DWS's equivariant layers operate within each weight matrix, preserving layer-wise structure. NFT's attention operates across all tokens, enabling global information flow. Battaglia et al. [2018] provide a theoretical framework for understanding relational inductive biases, arguing that architectural constraints should match task structure.

**Limitation we address:** While the locality-vs-attention trade-off is understood in vision, it has not been empirically tested in weight-space learning. We provide the first measurement of how these inductive biases manifest in weight-space architectures.

## Model Property Prediction

Predicting properties of neural networks from their weights has practical applications including accuracy estimation, robustness assessment, and backdoor detection. Unterthiner et al. [2020] demonstrated that simple weight statistics (mean, variance, histogram features) can predict test accuracy, establishing a strong baseline for holistic property prediction.

The TrojAI benchmark [NIST] provides large-scale data for backdoor detection, with thousands of neural networks labeled for the presence of trojans. Prior work has used various approaches for trojan detection, from feature-based methods to meta-learning approaches [Wang et al., 2019]. However, equivariant architectures have not been systematically evaluated on this benchmark.

**Limitation we address:** Existing approaches either use handcrafted features (Unterthiner) or evaluate equivariant architectures on non-property-prediction tasks. We provide the first controlled comparison of equivariant architectures (DWS, NFT) against baselines on property prediction tasks.

## Our Position

Our work bridges these three areas by providing the first systematic comparison of permutation-equivariant architectures on model property prediction. Unlike prior work, we:

1. **Match experimental conditions:** Same parameter budgets, training procedures, and evaluation metrics across architectures
2. **Test task-dependent hypotheses:** Specifically test whether locality helps backdoor detection while global attention helps accuracy prediction
3. **Quantify inductive bias differences:** Measure how DWS and NFT differ through training dynamics analysis, not just final performance

This addresses the critical gap identified in Phase 1 research: no unified benchmark comparison exists between the leading permutation-equivariant architectures on model property prediction tasks.
