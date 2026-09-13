# 4. Experimental Setup

We design experiments to answer three research questions that together characterize the paradigm effect on spurious feature encoding:

**RQ1:** Does pretraining paradigm significantly modulate the spurious/task probe accuracy ratio on frozen ResNet-50 features? (Waterbirds)

**RQ2:** Is this effect consistent across datasets with different spurious attribute types, and does the paradigm ranking change? (CelebA cross-dataset comparison)

**RQ3:** Is augmentation a functional mechanism for modulating spurious encoding in contrastive SSL? (Background-replacement ablation)

Each RQ maps directly to claims in the Introduction: RQ1 tests the existence claim (Contribution 1), RQ2 tests cross-dataset generalization and the interaction claim (Contribution 2), and RQ3 tests the mechanistic lever claim (Contribution 4).

### 4.1 Datasets

| Dataset | Train | Test (balanced) | Task | Spurious | Train Correlation |
|---------|-------|----------------|------|----------|------------------|
| Waterbirds | 4,795 | 5,794 | Bird species | Background type | 95% |
| CelebA | 162,770 | 720 (180×4 groups) | Blond_Hair | Male | ~85% |

Waterbirds is the primary dataset for RQ1–RQ3 due to its strong spurious correlation (95%) and controlled construction. CelebA provides a cross-dataset test with a different spurious attribute type (demographic rather than texture-based), enabling RQ2.

### 4.2 Baselines and Paradigms

We compare four pretraining paradigms, each as a separate independent variable level:

| Paradigm | Type | Checkpoint Source | ImageNet Top-1 (reported) |
|----------|------|-------------------|--------------------------|
| ERM | Supervised | torchvision.models.resnet50 | 76.1% |
| MoCo-v3 | Contrastive SSL | Official r-50-1000ep.pth.tar | 74.3% |
| DINO | Self-distillation SSL | facebookresearch/dino Hub | 75.3% |
| BarlowTwins | Non-contrastive SSL | facebookresearch/barlowtwins | 73.5% |

All use ResNet-50 backbone (2048-dim output) frozen throughout. We include all four paradigms to span the design space of pretraining objectives: label-supervised (ERM), contrastive label-agnostic (MoCo-v3), self-distillation (DINO), and redundancy-reduction (BarlowTwins).

**Why these specific checkpoints?** Official checkpoints from the original papers ensure reproducibility and represent each paradigm's intended training protocol. MoCo-v3 required a custom weight-loading workaround (Hub not available); weights were loaded directly from the official `.pth.tar` checkpoint. This is noted as a limitation in Section 6.

### 4.3 Implementation Details

**Feature extraction:** Each ResNet-50 extracts 2048-dimensional features from the penultimate layer (global average pool, fc=Identity). Features are extracted once per model and cached; probe training uses cached features across all 5 seeds.

**Probe training:** Logistic regression (scikit-learn) with L2 regularization (C=1.0, lbfgs solver, max_iter=1000, n_jobs=-1). Trained on group-balanced validation subset; evaluated on balanced test split. 5 seeds per probe (0–4).

**Statistical analysis:** One-way ANOVA on ratio values across all paradigms; Bonferroni-corrected pairwise t-tests (6 pairs, C(4,2)); Cohen's d with pooled standard deviation; α=0.05.

**SimCLR mechanism experiment (RQ3):** From-scratch training on Waterbirds train split. Both conditions: SGD (momentum=0.9, weight_decay=1e-4), learning rate=0.03 (cosine annealing, T_max=50, η_min=0), batch=256, epochs=50, NT-Xent temperature=0.5, projection head 2048→2048→128 (L2-normalized). Places365 pool: 10,000 images sampled randomly. CUB-200-2011 segmentation masks used for foreground identification.

**Compute:** NVIDIA H100 NVL; feature extraction ~5 min per model; probe training ~1 sec per seed per paradigm.

### 4.4 Evaluation Metrics

**Primary metric:** Spurious/task probe accuracy ratio (ratio = spurious_acc / task_probe_acc on balanced test split). Higher ratio indicates stronger spurious feature encoding relative to task encoding.

**Gate criterion:** At least one pairwise comparison satisfying p_bonf < 0.05 AND mean_diff ≥ 0.02 (2 percentage points).

**Effect size:** Cohen's d with pooled standard deviation; d > 3 indicates very large effect by any convention.

**Mechanism metric (RQ3):** Pixel difference between views with and without background replacement (mechanism detection threshold: 0.05). Ratio difference (SimCLR-NoBackground vs SimCLR-Original) with paired t-test across 5 seeds.
