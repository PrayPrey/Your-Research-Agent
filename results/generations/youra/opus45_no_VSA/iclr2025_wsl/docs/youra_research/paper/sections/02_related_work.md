# Related Work

We position our work at the intersection of spectral analysis of neural networks and model quality prediction. Existing approaches either compute spectral features directly without examining estimator variance, or predict model properties without testing the stability-quality relationship.

## Spectral Analysis of Neural Networks

Martin and Mahoney [Martin & Mahoney, 2019] pioneered spectral analysis of weight matrices, showing that heavy-tailed eigenvalue distributions emerge during training and correlate with generalization. Their alpha exponent captures power-law decay—but alpha failed to discriminate model quality in our prior attempts (p = 0.55), motivating the shift to participation ratio variance. The WeightWatcher tool [Martin et al., 2021] operationalized this framework, computing spectral metrics across layers. However, these methods compute features directly; they do not examine what the *variance* of randomized estimators reveals about model quality.

Li et al. [Li et al., 2018] estimated intrinsic dimensionality of objective landscapes using random subspace training. Their participation ratio (PR = (Σλ)² / Σλ²) captures effective rank—how concentrated eigenvalue mass is across dimensions. We adopt PR but focus on its coefficient of variation across SVD seeds, which prior work did not examine.

Randomized SVD algorithms [Halko et al., 2011] underpin our extraction methodology. By projecting onto random subspaces, these algorithms trade exactness for speed. The projection introduces variance: different random matrices yield different singular value approximations. This variance is typically treated as noise to minimize; we treat it as a signal.

## Model Quality Prediction

Unterthiner et al. [Unterthiner et al., 2020] established the state-of-the-art for predicting model accuracy from weights, achieving R² > 0.98 using simple statistics (mean, variance, spectral properties) aggregated across layers. Their approach is architecture-agnostic, pooling diverse model families. We complement their work by testing whether spectral *variance*—not just spectral features—adds interpretable signal.

Recent work has explored neural network fingerprinting [Eilertsen et al., 2020], model zoo analysis [Wortsman et al., 2022], and training dynamics for quality assessment [Frankle et al., 2020]. These methods focus on different aspects of model characterization. None examines randomized SVD variance as a quality predictor.

## Architecture-Aware Analysis

The timm library [Wightman, 2019] provides a unified interface to 1,000+ pretrained models with documented accuracy, enabling large-scale studies. Model soups [Wortsman et al., 2022] and Git Re-Basin [Ainsworth et al., 2023] explore weight-space relationships across models but focus on interpolation and alignment, not spectral variance.

Architecture-family effects remain underexplored in spectral analysis. BatchNorm, GroupNorm, and LayerNorm create different spectral signatures [Wu & He, 2018]. We observe CV\_PR variation across architecture families (ResNet, ViT, EfficientNet, ConvNeXt) but do not yet control for these effects systematically.

## Our Position

Our work fills a specific gap: no prior study has tested the directional relationship between randomized SVD variance and model quality. We hypothesized negative correlation (stability → quality); experiments revealed positive correlation. This falsification itself is a contribution, redirecting future research away from the stability-as-quality assumption.
