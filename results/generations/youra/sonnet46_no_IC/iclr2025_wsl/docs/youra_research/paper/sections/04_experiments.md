# Experimental Setup

We design four experiments, each testing a specific prediction of our approach. The experiments address the following research questions:

**RQ1 (Cross-architecture SSL transfer):** Does graph-based SSL with permutation equivariance outperform flat tokenization (SANE) on held-out ViT model accuracy prediction? This is the core test of whether the graph coordinate system enables cross-architecture generalization.

**RQ2 (Distribution shift measurement):** Does graph encoding reduce the measurable distribution shift between CNN training zoo and ViT test zoo representations, as hypothesized by the MMD-based mechanism? This tests the causal mechanism underlying RQ1.

**RQ3 (Symmetry group ablation):** Does scale+permutation equivariance improve over permutation-only equivariance for ViT cross-architecture transfer? This tests whether the more complex symmetry group (ScaleGMN) provides additional benefit for the cross-architecture SSL setting.

**RQ4 (Latent interpolation capability):** Does latent-space model interpolation produce more accurate models than weight-space averaging? This tests whether the SSL encoder's latent space supports functional model editing.

## Datasets

**Training Zoo — SANE MultiZoo CIFAR-10 CNN Subset.** We train all SSL encoders on a subset of the SANE MultiZoo benchmark [Schürholt et al., 2024], specifically the CIFAR-10 convolutional neural network checkpoints (tune_zoo_cifar10_uniform_small, approximately 3,000 models). This dataset contains CNN checkpoints with diverse hyperparameter configurations (learning rate, depth, width, optimizer), providing training distribution diversity for SSL. We use these models exclusively during encoder training; no ViT models appear at training time.

*Why this training set:* SANE MultiZoo represents the largest publicly available heterogeneous model zoo for weight-space SSL. The CIFAR-10 CNN subset provides maximum architectural distance from the ViT test zoo, making this the hardest reasonable cross-architecture transfer benchmark.

**Test Zoo — ViT Model Zoo.** We evaluate property prediction on 53 ViT-S/16 ImageNet checkpoint from the ViT Model Zoo dataset [Zhu et al., arXiv:2504.10231], which provides real trained checkpoints with validated ImageNet accuracy labels. The original dataset contains 250 models; we use 53 due to local availability constraints. All ViT models are from the same ViT-S/16 (Vision Transformer Small, 16×16 patches) architecture, ensuring that variation in accuracy reflects genuine functional differences rather than architectural heterogeneity within the test set.

*Why ViT-S/16:* Maximum architectural difference from the CNN training zoo (no convolutional layers, attention-based, LayerNorm normalization) provides the strongest test of cross-architecture generalization. Success here is a lower bound on performance for architecturally closer transfer targets.

**Interpolation Dataset (RQ4) — SANE ModelZoo CIFAR-10 CNN.** For the latent interpolation experiment, we use 200 real CNN checkpoints from the SANE ModelZoo (zenodo:13144018), forming 501 model pairs for interpolation evaluation.

## Baselines

**SANE [Schürholt et al., 2024].** The state-of-the-art weight-space SSL method, using a hierarchical transformer with flat weight tokenization. We apply VICReg variance regularization (weight=0.1) to prevent latent collapse under cross-architecture inputs. Without this fix, SANE produces constant latent codes for ViT inputs. We report results for this regularized SANE throughout.
*Why included:* Direct comparison to SOTA establishes whether graph encoding provides benefit over the best existing flat tokenization approach.

**EquiSSL (scale+permutation equivariance, ScaleGMN backbone).** Our implementation using the ScaleGMN encoder [Kalogeropoulos et al., 2024] with the full monomial matrix group (scale+permutation) equivariance. Trained with the same NT-Xent + MSE objective as EquiSSL-perm, but with both scale and permutation augmentation.
*Why included:* Tests whether the more expressive symmetry group (which improves supervised same-architecture property prediction by +8-12pp [Kalogeropoulos et al., 2024]) provides benefit in the cross-architecture SSL setting. This is an ablation on the symmetry group, not an external baseline.

**Weight-space averaging (RQ4 only).** Given two CNN model checkpoints θ_A and θ_B, the weight-space average is (θ_A + θ_B)/2, then evaluated on CIFAR-10. This is compared to latent-space interpolation via the graph encoder+decoder.
*Why included:* Naive baseline for model merging. If latent interpolation outperforms this, the latent space supports functional model editing.

## Implementation Details

All graph encoders use node input dimension 4 ([bias_mean, bias_std, bias_min, bias_max]) and edge input dimension 4 ([weight_mean, weight_std, weight_min, weight_max]). **EquiSSL-perm** uses the neural-graphs permutation-equivariant encoder (hidden_dim=256, latent_dim=128, num_layers=4). **EquiSSL** uses the ScaleGMN monomial-equivariant encoder with the same hidden/latent dimensions.

Both graph encoders are trained with Adam (lr=1e-3, weight_decay=1e-4), batch_size=64, for 100 epochs with CosineAnnealingLR (T_max=100, η_min=1e-5). The SSL objective is ℒ = ℒ_NT-Xent(τ=0.07) + 0.1 · ℒ_MSE. Augmentation for EquiSSL-perm: random neuron permutation per layer (no scale augmentation). Augmentation for EquiSSL: random neuron permutation AND random scale augmentation per layer.

All experiments use seed 0 (single seed due to training data availability constraints; see Section 6 for discussion). Training was performed on a single NVIDIA GPU. Code available at [ANONYMOUS REPOSITORY].

## Evaluation Metrics

**R² (coefficient of determination).** Primary metric for property prediction (RQ1, RQ2, RQ3). We fit a RidgeCV linear probe (α ∈ {0.1, 1.0, 10.0, 100.0}, 80/20 train/test split) on extracted embeddings, predicting ViT-S/16 ImageNet validation accuracy. R²=0 indicates prediction equal to mean; R²=1 is perfect prediction. R²<0 indicates worse than constant prediction.

*Why R²:* R² is the standard metric for property prediction in weight-space SSL literature [Schürholt et al., 2024; Kofinas et al., 2024]. Unlike accuracy metrics, R² captures both the variance explained and the direction of effect. It is more informative than correlation alone for assessing practical utility.

**MMD (Maximum Mean Discrepancy, RBF kernel).** Secondary metric for distribution shift measurement (RQ2). We compute MMD between the CNN training zoo embeddings and ViT test zoo embeddings for each encoder. Lower MMD indicates smaller distributional gap between training and test latent distributions.

*Caveat:* As we report in Section 5, MMD is confounded by latent variance scale. We compute it for completeness but rely on R² as the primary metric.

**Interpolation accuracy delta (RQ4).** For each model pair (θ_A, θ_B), we compute acc_latent (accuracy of the interpolated model, decoded from the latent midpoint) and acc_ws (accuracy of the weight-space average model). The metric is mean(acc_latent - acc_ws) over N=501 pairs, with paired t-test for significance.
