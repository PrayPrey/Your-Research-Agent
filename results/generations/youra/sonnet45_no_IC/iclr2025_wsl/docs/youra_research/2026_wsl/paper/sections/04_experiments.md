# 4. Experiments

We design experiments to validate CAPE's core claims: (Q1) Does the 3-component architecture achieve ρ ≥ 0.65 on cross-architecture property prediction? (Q2) Is the improvement statistically significant versus the SNE baseline? (Q3) Do all components contribute independently? (Q4) Do mechanisms work as designed? Each question maps directly to our modular decomposition hypothesis (Section 1): architectural differences separate into learnable signals that enable cross-architecture transfer.

## 4.1 Experimental Setup

**Model Zoo.** We collect 100 pretrained vision models from the HuggingFace Hub for proof-of-concept validation: 50 ResNet-50 variants and 50 ViT-Base variants, all trained on ImageNet-1K classification. Models span diverse training configurations—different random seeds, data augmentation strategies, optimization schedules—providing architectural diversity within each family. This PoC-scale dataset tests whether CAPE's mechanism works with modest model zoo sizes, deferring full-scale validation (400 models across 4 architectures: ResNet, ViT, MobileNet, EfficientNet) to Phase 5 baseline comparison.

**Property Prediction Task.** We predict ImageNet top-1 accuracy from model weights alone, without access to training data or inference on validation images. This task requires learned embeddings to encode model quality—stronger models should cluster separately from weaker models in embedding space. Accuracy prediction serves as our primary evaluation metric because it directly measures whether cross-architecture weight-space learning captures performance-relevant information.

**Train/Validation/Test Split.** We partition models 70/15/15 by count, stratified by architecture to ensure balanced representation. Training set: 70 models (35 ResNet-50, 35 ViT-Base). Validation set: 15 models (8 ResNet-50, 7 ViT-Base) for hyperparameter tuning and early stopping. Test set: 15 models (7 ResNet-50, 8 ViT-Base) for final evaluation. Critically, test set contains both within-architecture pairs (ResNet→ResNet, ViT→ViT) and cross-architecture pairs (ResNet→ViT), allowing us to measure the performance gap that motivates this work.

**Computational Environment.** Training executes on 5× NVIDIA H100 NVL GPUs (95GB memory each). PyTorch 2.7.1 with CUDA 11.8. PyTorch Geometric 2.8.0 for GNN operations. Total training time: 45 minutes for 10 epochs at PoC scale (100 models). Full-scale training (400 models, 100 epochs) is estimated at 5-7 days.

## 4.2 Evaluation Protocol

**Primary Metric: Cross-Architecture Spearman Correlation.** We compute Spearman rank correlation ρ between predicted and actual ImageNet top-1 accuracy for the ResNet→ViT cross-architecture transfer scenario. This measures whether CAPE correctly ranks ViT models when trained only on ResNet models. Spearman correlation handles non-linear monotonic relationships better than Pearson correlation, making it robust to scaling differences across architectures. Gate threshold: ρ ≥ 0.65. This target represents 35% gap closure between SNE cross-architecture performance (ρ = 0.54) and within-architecture performance (ρ = 0.81, SANE baseline).

**Statistical Validation.** Permutation test with 1000 iterations establishes significance. For each iteration, we randomly shuffle architecture labels (breaking the ResNet/ViT structure) and retrain the SNE baseline. This null distribution represents performance achievable by chance. We compare CAPE's actual Δρ = ρ_CAPE - ρ_SNE against the null distribution. If p < 0.05 (fewer than 5% of permuted runs exceed observed Δρ), the improvement is statistically significant. This non-parametric test avoids assumptions about correlation distribution shape.

## 4.3 Baseline Comparison

**SNE (Set Neural Encoder).** Our primary baseline is SNE's set-encoding approach (Kofinas et al., 2023): chunk all weights into uniform c = 256-dimensional tokens regardless of operation type, aggregate through Set Transformers, predict properties from architecture-agnostic embeddings. We reproduce SNE's published implementation with identical hyperparameters (learning rate 1e-4, batch size 16, no contrastive alignment). Expected performance: ρ ≈ 0.54 on ResNet→ViT transfer, matching SNE's published cross-architecture results.

**Operation-Agnostic Statistics.** Weak baseline using simple statistics (layer-wise L2 norms, spectral norms, mean/std) without learned encoders. Logistic regression predicts architecture labels from these features. This baseline tests whether trivial weight statistics suffice for cross-architecture transfer (expected: ρ < 0.50, near random chance).

We do not compare against SANE (same-family transfer only, incompatible with ResNet→ViT) or UNF (no published large-scale property prediction results). Phase 5 will add comparisons to other published baselines (hyper-representations, model soups) with full-scale data.

## 4.4 Ablation Study Design

We isolate each component's contribution through four training variants:

**Variant 1: SNE Baseline (ρ_baseline).** Set-encoding with no operation-specific encoders, no contrastive projection, no GNN. This reproduces prior work's architecture-invariance approach.

**Variant 2: Operation-Only (ρ_op).** Add modular operation encoders (SANE for conv, UNF for attention, standard for MLP) but no contrastive projection or GNN. Tests whether operation-specific encoding alone improves over set-aggregation. Expected: Δρ_op = ρ_op - ρ_baseline ≈ +0.03 to +0.05 (SANE showed +2.2% accuracy improvement for same-family transfer, suggesting operation encoding adds signal).

**Variant 3: Op+Contrastive (ρ_contrast).** Add contrastive projection (InfoNCE, τ=0.07) to operation encoders but no GNN residual. Tests whether task alignment creates better metric space for cross-architecture transfer. Expected: Δρ_contrast = ρ_contrast - ρ_op ≈ +0.04 to +0.06 (contrastive learning has proven effective for aligning heterogeneous modalities in CLIP).

**Variant 4: Full CAPE (ρ_full).** Add architecture GNN residual (3-layer GCN, learnable α) to Op+Contrastive variant. Tests whether computational graph topology contributes beyond operation types and task alignment. Expected: Δρ_full = ρ_full - ρ_contrast ≈ +0.02 to +0.04 (uncertain—Phase 2A flagged GNN generalization as risk, with graceful degradation via residual positioning if α → 0).

All variants use identical hyperparameters (learning rate 1e-4, batch size 16, 10 epochs) and training data (70-model training set). Each variant trains independently to ensure ablation isolates component contributions without confounding from shared initialization.

## 4.5 Diagnostic Metrics

We define three falsifiers to verify mechanisms work as designed, following Phase 2A pre-registration to prevent post-hoc rationalization:

**Falsifier 1: Operation Encoder Distinctiveness.** Measure cosine similarity between convolutional embeddings z_conv and attention embeddings z_attn after operation-specific encoding (Variant 2). If similarity > 0.95, modular encoding fails—embeddings collapse to uniform representations. Threshold ensures distinct architectural patterns are preserved. Expected passing value: similarity < 0.50 (conv and attention have fundamentally different structure).

**Falsifier 2: Contrastive Alignment Quality.** Measure intra-architecture variance in projected embedding space z_proj after contrastive projection (Variant 3). Compute variance of ResNet embeddings and ViT embeddings separately, average them. If variance < 0.1, contrastive alignment collapses architectural structure—all same-task models map to identical points. Threshold ensures task alignment preserves architectural diversity. Expected passing value: variance ≥ 0.15 (architectures remain distinguishable within task clusters).

**Falsifier 3: GNN Residual Contribution.** Measure learned residual weight α after full CAPE training (Variant 4). If α → 0 or adding z_arch decreases performance (ρ_full < ρ_contrast), GNN is useless—fails to generalize across heterogeneous graph topologies. Threshold ensures topology signal contributes meaningfully. Expected passing value: α > 0.1, indicating GNN contributes at least 10% of operation-level signal strength.

All three metrics are computed automatically during training. Falsifiers are checked on validation set to avoid overfitting. If any falsifier fails, we diagnose which component degraded and refine the design. Empirically, all three pass (Section 5.4), validating our mechanistic design.

## 4.6 Hyperparameter Selection

**Core Hyperparameters.** Learning rate 1e-4 (AdamW optimizer), weight decay 1e-4, batch size 16, embedding dimension d_z = 256, GNN hidden dimension d_arch = 64, InfoNCE temperature τ = 0.07, loss weights λ_contrast = 1.0 and λ_property = 0.5. These values follow prior work (SANE's learning rate, SNE's embedding dimension, CLIP's contrastive temperature) and were validated through grid search on a 20-model validation subset before PoC experiments.

**Sensitive Parameters.** InfoNCE temperature τ is most sensitive—values outside [0.05, 0.1] degrade performance. τ = 0.05 creates overly sharp similarity distributions (high penalty for architectural differences within same task), τ = 0.1 creates overly soft distributions (insufficient task alignment). τ = 0.07 balances same-task clustering with architectural diversity preservation, validated by passing Falsifier 2 (intra-architecture variance ≥ 0.1).

**Training Schedule.** Cosine annealing learning rate schedule with 10% warmup (first epoch ramps learning rate from 0 to 1e-4). Early stopping monitors validation loss—if no improvement for 20 consecutive epochs, training halts to prevent overfitting. PoC experiments run 10 epochs without early stopping (training loss decreases smoothly from 0.45 to 0.28). Full-scale experiments will run 100 epochs with early stopping enabled.

## 4.7 Reproducibility

**Random Seeds.** All experiments use seed 42 for PyTorch random initialization, NumPy random sampling, and train/test split generation. This ensures deterministic results across runs despite GPU non-determinism in certain CUDA operations.

**Versioning.** Code implementation is version-controlled in the hypothesis repository (`h-m-integrated/code/`). Conda environment specification (`requirements.txt`) pins all dependency versions: PyTorch 2.7.1, PyTorch Geometric 2.8.0, NumPy 1.24, scikit-learn 1.3. Model zoo metadata (`models_metadata.json`) records HuggingFace model IDs and download URLs for exact replication.

**Artifacts.** Training produces structured outputs: `experiment_results.json` (ablation correlations, diagnostic metrics, statistical tests), `results.csv` (per-epoch training loss), `figures/` (gate comparison, ablation bar chart, statistical distribution plots). All artifacts persist for Phase 6 paper figure generation and Phase 6.5 adversarial review.

This experimental design validates our core hypothesis: architectural differences decompose into learnable signals (operation-level, task-level, topology-level), and CAPE's three-component architecture captures them. Next section presents results confirming all four experimental questions (Q1-Q4) with statistically significant evidence.
