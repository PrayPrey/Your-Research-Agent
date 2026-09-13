# Methodology

We describe the extraction methodology for CV\_PR (coefficient of variation of participation ratio), designed to measure randomized SVD estimator variance across pretrained models.

## Overview

The core idea is simple: if spectral shape affects randomized SVD convergence, then flat spectra should yield consistent participation ratio estimates across random projections, while peaked spectra should not. We compute participation ratio 20 times per weight matrix (with different random seeds), measure the coefficient of variation, and aggregate across layers to obtain a per-model CV\_PR score. This score is then correlated with ImageNet accuracy.

## Randomized SVD

For a weight matrix W ∈ ℝ^{m×n}, randomized SVD [Halko et al., 2011] approximates the truncated singular value decomposition by projecting onto a random subspace:

1. Draw random matrix Ω ∈ ℝ^{n×k} where k = rank + oversampling
2. Form Y = WΩ
3. Orthonormalize: Q = orth(Y)
4. Form B = Q^T W
5. Compute SVD of small matrix: B = UΣV^T
6. Recover approximate singular values from Σ

Different random matrices Ω yield different approximations. For well-conditioned matrices with flat spectral decay, these approximations converge quickly and vary little across seeds. For ill-conditioned matrices with peaked spectra, variance is higher.

**Implementation**: We use `torch.linalg.svd` with QR-based random projection. Rank is fixed at 50; oversampling is 10. For 4D convolutional weights (c\_out × c\_in × h × w), we reshape to 2D by flattening spatial dimensions: (c\_out, c\_in × h × w).

## Participation Ratio

Given singular values σ = (σ\_1, ..., σ\_k) from the truncated SVD, the participation ratio is:

PR = (Σσ\_i²)² / Σσ\_i⁴

This equals n for uniform singular values (σ\_i = σ\_j ∀i,j) and approaches 1 when one singular value dominates. PR captures effective rank—how many dimensions carry significant energy.

**Design choice**: We use squared singular values (eigenvalues of W^T W), not singular values directly. This matches the standard participation ratio definition in random matrix theory.

## Coefficient of Variation

For each weight matrix, we compute PR across 20 random seeds (fixed sequence starting at seed 0 for reproducibility) and measure:

CV\_PR = std(PR) / mean(PR)

Low CV indicates stable estimates; high CV indicates sensitivity to random projection direction.

## Model-Level Aggregation

Each model contains multiple weight matrices (convolutional and linear layers). We aggregate layer-wise CV\_PR values via mean:

CV\_PR\_model = (1/L) Σ CV\_PR\_layer

**Rationale**: Mean aggregation is simple and interpretable. Alternative schemes (median, attention-weighted, size-weighted) are deferred to ablation studies.

**Layer selection**: We include all Conv2d and Linear layers with ≥100 elements. BatchNorm, LayerNorm, and bias vectors are excluded.

## Model Selection

We extract CV\_PR from pretrained models in the timm library satisfying:
- Pretrained on ImageNet-1K
- Has reported top-1 accuracy in timm metadata
- Architecture families: ResNet, ViT, EfficientNet, ConvNeXt, DenseNet, etc.

Target: 100 models minimum, stratified across architecture families.

## Correlation Test

The primary hypothesis test is Pearson correlation between CV\_PR\_model and ImageNet top-1 accuracy. We also compute Spearman correlation (robust to outliers) and 95% confidence intervals via bootstrap.

**Success criterion (original)**: r < -0.3, p < 0.05
**Falsification criterion**: r ≥ 0 or p ≥ 0.05

Figure 1 shows the distribution of CV\_PR values across extracted models.
