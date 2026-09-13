# Methodology

## Overview

Our approach rests on a single architectural commitment: represent every neural network as a directed computation graph before encoding its weights. This choice is motivated by the key insight established in the introduction — the graph schema (node=neuron, edge=weight) is architecture-agnostic in a way that flat tokenization is not. We combine this graph representation with permutation-equivariant graph neural network encoding and a contrastive autoencoder SSL objective, trained on MLP/CNN model zoos and evaluated zero-shot on ViT model zoos.

## 3.1 Problem Setup

Let *Z_train* = {θ₁, ..., θ_N} be a collection of trained neural network checkpoints from a set of architecture families *A_train* (MLPs and CNNs in our experiments). Let *Z_test* = {φ₁, ..., φ_M} be checkpoints from a held-out architecture family *A_test* (ViT-S/16 in our experiments), where *A_test* ∩ *A_train* = ∅ — no ViT model appears during SSL training.

Our goal is to learn an encoder f_θ: θ → z ∈ ℝ^d via SSL on Z_train, such that f_θ(φ) is useful for predicting properties of held-out test models φ ∈ Z_test without any supervised signal from Z_test. We evaluate using a RidgeCV linear probe on the extracted embeddings, predicting ViT-S/16 ImageNet accuracy from the learned representations.

## 3.2 Graph Encoding

**Schema.** We convert each neural network checkpoint into a directed attributed graph G = (V, E, x_v, x_e) where:
- Nodes v ∈ V correspond to neurons. Each node carries a 4-dimensional attribute vector x_v = [bias_mean, bias_std, bias_min, bias_max], capturing the distribution of bias values across the local neighborhood of that neuron.
- Directed edges (u, v) ∈ E represent scalar weights from neuron u to neuron v. Each edge carries a 4-dimensional attribute x_e = [weight_mean, weight_std, weight_min, weight_max], encoding the statistical distribution of the corresponding weight tensor.

**Architecture homomorphism.** This schema is architecture-agnostic because all the architecture families we consider — MLP linear layers, CNN convolutional filters, and ViT attention projections (Q, K, V, and MLP sublayers) — consist of linear maps from a set of source neurons to a set of target neurons. A ViT attention head's weight matrix W_Q ∈ ℝ^{d_k × d} defines exactly the same edge structure as an MLP linear layer W ∈ ℝ^{d_out × d_in}. The directed graph representation preserves this shared structure across architecture families.

**Rationale.** The 4-dimensional per-element statistics (mean, std, min, max) were chosen to capture the scale and distribution of weights without requiring identical tensor shapes. This encoding is sufficient for the linear probe to detect accuracy-predictive patterns: the encoder can learn that, e.g., high weight standard deviation at a particular graph position correlates with specific functional behaviors, without requiring the exact weight values.

## 3.3 Permutation-Equivariant SSL (EquiSSL-perm)

**Encoder architecture.** We use the neural-graphs encoder [Kofinas et al., 2024] with 4 message-passing layers, hidden dimension 256, and latent dimension 128. This encoder is permutation-equivariant: for any permutation π of neurons within a layer, f_θ(π(G)) = π(f_θ(G)) — the latent representation changes equivariantly with neuron relabeling. This symmetry is fundamental for weight-space encoding: two networks that differ only in the labeling of neurons within a layer are functionally identical, and their embeddings should reflect this.

**SSL objective.** We train with a composite loss:

ℒ = ℒ_NT-Xent(z, z+) + λ · ℒ_MSE(ê, e)

where z and z+ are embeddings of two augmented views of the same network graph, ℒ_NT-Xent is the normalized temperature-scaled cross-entropy contrastive loss [Chen et al., 2020] with temperature τ=0.07, and ℒ_MSE is a mean-squared error reconstruction loss between the decoder's predicted edge attributes ê and the original edge attributes e. The reconstruction term (λ=0.1) prevents representational collapse and provides a self-supervised signal beyond the contrastive objective.

**Augmentation.** Positive pairs are constructed by applying random neuron permutations to the same graph. Specifically, for each training example G, we generate G+ by independently permuting the neuron indices within each layer. We do NOT apply scale augmentation (see Section 3.4). This creates training pairs (G, G+) that are functionally identical (same network) but differ in representation, forcing the encoder to learn permutation-invariant features.

**Training configuration.** We train on SANE MultiZoo CIFAR-10 CNN checkpoints (~3,000 models), using Adam with learning rate 1e-3, weight decay 1e-4, batch size 64, for 100 epochs with CosineAnnealingLR (T_max=100, η_min=1e-5). These hyperparameters were selected via grid search on the contrastive loss (λ ∈ {0.01, 0.1, 1.0}, temperature ∈ {0.05, 0.07, 0.1}).

## 3.4 Why Permutation-Only: The LayerNorm Gauge Argument

Our initial hypothesis followed Kalogeropoulos et al. [2024] in using scale+permutation equivariance (the monomial matrix group), which achieved +8-12 R² points in supervised same-architecture settings. However, the scale symmetry of a neural network is the equivalence θ ~ cθ for scalar c > 0: two networks related by scaling of a neuron's incoming and outgoing weights are functionally equivalent (for ReLU-like activations, which are scale-homogeneous).

This symmetry breaks down in the presence of LayerNorm. LayerNorm normalizes each neuron's activations to zero mean and unit variance at inference time, which fixes the scale of the weight tensors entering the normalization. In ViT architectures, LayerNorm appears after every attention sublayer and MLP sublayer — essentially every neuron's output is scale-normalized. This "gauge fixing" [arXiv:2510.08300] eliminates the scale degree of freedom: two ViT weight tensors that differ by a scalar factor c are NOT functionally equivalent, because LayerNorm will normalize them to the same activation scale. Therefore, scale equivariance is not an appropriate inductive bias for ViT weight encoders.

Imposing scale equivariance in this setting introduces unnecessary invariance: the encoder maps weight tensors that differ by scale to the same latent code, even though those tensors may correspond to functionally distinct ViT models. This reduces the encoder's discriminative power for ViT accuracy prediction.

Based on this theoretical argument, our primary method (EquiSSL-perm) uses permutation-only equivariance. We include EquiSSL (scale+permutation, ScaleGMN backbone) as an ablation baseline to empirically verify this prediction.

## 3.5 SANE Baseline with VICReg Fix

As our primary baseline, we use SANE [Schürholt et al., 2024] with a modification required to prevent representation collapse. Without regularization, SANE's flat tokenizer maps all cross-architecture inputs to near-constant latent codes (std≈0.0014) — a collapse that makes R²-based evaluation trivial (all predictions equal the mean). We apply a VICReg variance regularization term [Bardes et al., 2022]:

ℒ_VICReg = 0.1 · max(0, 1 - σ(z))

where σ(z) is the standard deviation of the batch latents along each dimension. This prevents variance collapse while preserving the flat tokenization architecture. We treat SANE + VICReg as the strongest possible flat tokenization baseline.

## 3.6 Evaluation: RidgeCV Linear Probe

We evaluate representation quality using a linear probe on accuracy prediction. After SSL training on Z_train (CNN checkpoints), we extract embeddings f_θ(φ) for all φ ∈ Z_test (ViT checkpoints). We then fit a RidgeCV regressor (α ∈ {0.1, 1.0, 10.0, 100.0}, 80/20 train/test split) to predict ViT-S/16 ImageNet validation accuracy from these embeddings. The evaluation metric is R² (coefficient of determination). R² > 0 indicates above-chance prediction; R² = 1 is perfect prediction.

This protocol is intentionally conservative: the linear probe uses only the test-set ViT models (53 models) with no additional fine-tuning of the encoder on ViT data. The SSL encoder receives zero supervision from the target architecture family.
