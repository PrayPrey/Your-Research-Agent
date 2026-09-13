# Methodology

Building on our observation that spurious correlations create sharp curvature in specific loss landscape subspaces, we design a geometric diagnostic framework based on Marchenko-Pastur random matrix theory. Our approach quantifies how minority-group gradients align with sharp curvature directions, revealing whether a trained model exploits spurious correlations.

## Overview

Our method consists of three components: (1) Hessian eigenvalue spectrum analysis to identify sharp versus flat curvature subspaces using Marchenko-Pastur bulk edge detection, (2) minority-gradient computation to probe spurious correlation structure, and (3) alignment metric calculation to quantify spurious exploitation. The key insight enabling this approach is that Marchenko-Pastur theory provides an *intrinsic* threshold—the bulk edge—separating signal (outlier eigenvalues indicating concentrated curvature) from noise (bulk spectrum indicating diffuse curvature), with no arbitrary hyperparameters.

## Marchenko-Pastur Curvature Subspace Detection

**Rationale:** Hessian eigenvalues reveal loss landscape curvature, but distinguishing meaningful structure from random noise requires principled threshold selection. Marchenko-Pastur random matrix theory predicts that for over-parameterized networks (M parameters, N samples, M ≥ N), eigenvalues of a random matrix follow a bulk distribution with upper edge λ₊ = (1 + √(N/M))². Eigenvalues exceeding λ₊ represent *signal*—concentrated curvature from data structure—while eigenvalues within the bulk represent *noise*.

Given a trained model with parameters θ, we compute the Hessian eigenvalue spectrum via power iteration with deflation (avoiding full eigendecomposition, which is O(M³)). We fit a Marchenko-Pastur distribution to the empirical spectrum using maximum likelihood estimation, obtaining bulk edge λ₊. Eigenvalues λᵢ > λ₊ define the *outlier subspace* S_out spanned by corresponding eigenvectors vᵢ.

**Technical Details:** For a dataset with N = 11,788 samples and ResNet-50 with M = 25.6M parameters, we compute the top-K eigenvalues (K = 100) using Lanczos iteration. The Marchenko-Pastur fit requires estimating aspect ratio γ = N/M and bulk scale σ² from the empirical distribution. We validate fit quality by computing Kolmogorov-Smirnov statistic between empirical and fitted distributions.

## Minority-Group Gradient Computation

**Rationale:** Group-DRO theory establishes that minority groups—subgroups with spurious features misaligned with labels—expose spurious correlations. For example, on Waterbirds, "landbirds on water backgrounds" are minority because the spurious correlation (background → label) fails for them. Gradients computed on minority samples should point toward spurious-feature directions if the model exploits shortcuts.

For a model f(x; θ) with loss L(f(x; θ), y), we compute per-sample gradients g(x) = ∇θ L(f(x; θ), y) on a batch of minority-group samples. We average these gradients to obtain g_minority = (1/|B_minority|) Σ g(x) for batch B_minority. Similarly, we compute g_majority for majority groups.

**Implementation:** Using the Waterbirds dataset, minority groups are {group 1: landbirds on water, group 2: waterbirds on land} comprising ~240 samples. We use batch size 240 to ensure statistical stability of gradient estimates. Gradients are extracted from the model's final linear layer before classification, providing representation-level sensitivity.

## Alignment Metric Calculation

**Rationale:** To quantify spurious correlation exploitation, we measure what fraction of minority-gradient variance falls into the sharp curvature subspace (outliers). High alignment indicates the model has concentrated curvature in directions that minority gradients point toward—a signature of spurious correlation learning.

The alignment metric is defined as:

A(θ) = ||P_S_out g_minority||² / ||g_minority||²

where P_S_out is the projection operator onto the outlier subspace S_out. This metric has intuitive interpretation: A(θ) = 0.72 means 72% of minority-gradient variance lies in sharp curvature directions.

**Computation:** Given outlier eigenvectors {v₁, ..., vₖ} and minority gradient g_minority, we compute:
1. Project: p = Σᵢ (vᵢᵀ g_minority) vᵢ
2. Alignment: A(θ) = ||p||² / ||g_minority||²

**Alternative Metrics Considered:** We evaluated cosine similarity (not variance-weighted), projection magnitude (not normalized), and top-K eigenvector alignment (arbitrary K). The variance-explained formulation was chosen because it provides scale-invariant, interpretable quantification: "what fraction of minority information is in sharp subspace?"

## SGD Trajectory Analysis

**Rationale:** To validate that SGD dynamics contribute to the geometric signature, we track optimization trajectories and measure directional bias—whether gradient steps preferentially align with flat (bulk) directions over sharp (outlier) directions.

During training, we log gradient directions every 10 epochs and compute alignment to both bulk and outlier subspaces. Directional bias is defined as:

Bias = Alignment_bulk - Alignment_outlier

Positive bias indicates preference for flat directions, validating SGD's implicit flatness bias in the spurious correlation context.

## Experimental Protocol

**Dataset:** Waterbirds benchmark (11,788 images, 4 groups: landbirds/land, landbirds/water, waterbirds/land, waterbirds/water). Ground-truth spurious correlation: background correlates with bird type.

**Model:** ResNet-50 pretrained on ImageNet, fine-tuned with standard data augmentation (random crop, horizontal flip). Training uses SGD with learning rate 0.001, momentum 0.9, batch size 128.

**Baselines:** 
- **ERM:** Standard cross-entropy loss, expected to exploit spurious correlation
- **Group-DRO:** Robust optimization minimizing worst-group loss, expected to learn core features

**Metrics:**
- Alignment A(θ): Geometric signature (primary)
- Worst-group accuracy: Robustness measure
- Outlier count: Curvature concentration
- Directional bias: SGD trajectory preference

**Computational Cost:** Hessian eigenvalue computation (top-100 via Lanczos): ~2 hours on V100 GPU. Gradient computation: ~5 minutes. Total per-model analysis: ~2.5 hours, parallelizable across models.
