# Methodology

Our approach operationalizes the insight that attribution methods embed different mathematical operations, creating different sensitivities to influence modes. We design contrastive probes to isolate each mode, compute mode profiles per method, and quantify dissociation through variance analysis.

## Overview

Given an attribution method $A$, a trained model $M$, and a set of contrastive probe pairs $\mathcal{P}$, we measure the method's sensitivity to each influence mode by computing attribution scores on probes designed to isolate that mode. The resulting *mode profile* is a vector $\mathbf{p}_A = [s_\text{mem}, s_\text{transfer}, s_\text{spurious}]$ capturing the method's relative sensitivity to memorization, feature transfer, and spurious association.

## Influence Modes

We define three modes of training data influence, each with distinct computational signatures:

**Memorization:** Training examples influence test predictions through direct memorization—the model learns the specific input-output mapping rather than generalizable features. Attribution methods sensitive to memorization assign high influence to near-duplicate or highly similar training examples.

**Feature Transfer:** Training examples contribute features that generalize to test examples in the same category. Attribution methods sensitive to feature transfer assign influence based on shared high-level representations rather than surface similarity.

**Spurious Association:** Training examples share spurious correlations (e.g., background features, co-occurring attributes) with test examples. Attribution methods sensitive to spurious association may incorrectly attribute influence to examples sharing these shortcuts.

## Contrastive Probe Construction

For each mode $m \in \{\text{mem}, \text{transfer}, \text{spurious}\}$, we construct contrastive probe pairs $(t, s^+, s^-)$ where $t$ is a test point, $s^+$ is a training point exhibiting mode $m$ relationship with $t$, and $s^-$ is a matched control lacking this relationship.

**Memorization probes:** Select $s^+$ as training examples with high pixel-level similarity to $t$ (near-duplicates). Select $s^-$ from the same class with low surface similarity.

**Feature transfer probes:** Select $s^+$ from the same semantic class as $t$ but with different surface features (e.g., different viewpoint, lighting). Select $s^-$ from a different class but similar surface statistics.

**Spurious probes:** Select $s^+$ sharing a spurious correlation with $t$ (e.g., same background, co-occurring attribute). Select $s^-$ from the same class without the spurious correlation.

Mode sensitivity is computed as:
$$s_m = \frac{1}{|\mathcal{P}_m|} \sum_{(t, s^+, s^-) \in \mathcal{P}_m} \text{sign}(A(s^+; t) - A(s^-; t))$$

where $A(s; t)$ is the attribution score for training point $s$ given test point $t$.

## Mode Profile Computation

For each attribution method, we compute mode sensitivities across all probe pairs and construct the mode profile vector:
$$\mathbf{p}_A = \left[\bar{s}_\text{mem}, \bar{s}_\text{transfer}, \bar{s}_\text{spurious}\right]$$

We L2-normalize profiles to unit vectors for fair comparison:
$$\hat{\mathbf{p}}_A = \frac{\mathbf{p}_A}{\|\mathbf{p}_A\|_2}$$

## Dissociation Analysis

To test whether methods produce dissociable fingerprints, we run each method with multiple random seeds and apply ANOVA analysis:

**Between-group variance (inter-method):** Variance of method means around the grand mean, capturing how different methods' average profiles are.

**Within-group variance (intra-method):** Variance of individual runs around each method's mean, capturing random variation across seeds.

The F-ratio $F = \text{MS}_\text{between} / \text{MS}_\text{within}$ quantifies dissociation. An F-ratio significantly greater than 1 indicates that method identity explains more variance than random seed—i.e., methods produce systematic fingerprints.

We set thresholds based on standard statistical practice: F > 4.0 for meaningful dissociation (corresponds to $p < 0.05$ with our degrees of freedom), and Cohen's d > 0.5 for medium-to-large effect size in pairwise comparisons.

## Cross-Architecture Transfer

To test whether fingerprints are method-intrinsic rather than model-specific, we compute mode profiles for each method across multiple architectures (ResNet-18, ViT-Small, ConvNeXt-Tiny) and measure Pearson correlation between profiles of the same method on different architectures.

High correlation (r > 0.7) indicates that a method's fingerprint transfers across architectures—the same mathematical operations create similar mode sensitivities regardless of the underlying model structure.

## Attribution Methods

We evaluate three representative methods spanning different computational approaches:

**TRAK** [Park et al., 2023]: Computes influence via random projection of gradients, preserving gradient direction while reducing dimensionality. Emphasizes directional alignment in parameter space.

**TracIn** [Pruthi et al., 2020]: Sums gradient dot products weighted by learning rate across checkpoints. Captures temporal patterns in how influence accumulates during training.

**Kronfluence** [Grosse et al., 2023]: Inverts Fisher information matrix using K-FAC approximation. Emphasizes curvature structure in the loss landscape.

These methods represent the major computational paradigms in current attribution research: projection-based, checkpoint-based, and curvature-based.
