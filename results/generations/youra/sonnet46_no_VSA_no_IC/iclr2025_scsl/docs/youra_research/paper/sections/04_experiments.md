## 4. Experimental Setup

### 4.1 Research Questions

We design experiments to answer the following questions:

**RQ1 (Existence):** Does SSL-SGD training create severe worst-group accuracy degradation on spurious correlation benchmarks, relative to supervised training? (H-E1 gate)

**RQ2 (Geometric Diagnosis):** Does the sharpness anisotropy ratio of converged SSL models exceed 1.2, and does it correlate negatively with worst-group accuracy across training checkpoints? (H-E1 anisotropy test)

**RQ3 (Geometric Intervention):** Does replacing SGD with SAM during SSL pretraining reduce the anisotropy ratio and improve worst-group accuracy, without group annotations? (H-M2 intervention test)

Each RQ corresponds directly to a mechanism step in the causal chain: SSL-SGD creates anisotropy (RQ1/RQ2), SAM reduces it (RQ3).

### 4.2 Datasets

**Waterbirds** [Sagawa et al., 2019] is our primary benchmark. It superimposes CUB-200-2011 bird images onto Places365 backgrounds with 95% spurious correlation: 95% of waterbirds appear on water backgrounds and 95% of landbirds appear on land backgrounds at training time. The four demographic groups are (waterbird, water), (waterbird, land), (landbird, water), (landbird, land), with training sizes 3498, 184, 56, 1057 respectively. Validation and test sets are balanced across groups. We use the standard splits from kohpangwei/group_DRO.

Waterbirds is the primary benchmark because it has well-characterized spurious (background) vs. core (bird morphology) feature structure, enabling H-E1's anisotropy measurement. The 95% spurious correlation provides a strong signal.

**CelebA** [Liu et al., 2015] (planned) correlates hair color (blonde/non-blonde) with gender. We use WILDS [Koh et al., 2021] for downloading. CelebA was excluded from the initial experiment due to a WILDS server HTTP 500 error; results are deferred to an extended evaluation.

**CMNIST** [Arjovsky et al., 2019] (planned) correlates digit color with binary label at 99% strength. Excluded from the initial fast run due to speed constraints; included in the full 9-combination evaluation protocol.

### 4.3 Models and Baselines

**SSL Methods:**
- **DINO** [Caron et al., 2021]: Self-distillation SSL using ViT-S/8 backbone (384-dim features). Primary model in H-E1 validation.
- **SimCLR** [Chen et al., 2020]: NT-Xent contrastive loss on ResNet-50 (2048-dim). Linear probe evaluated at 10 epochs (fast run); 200-epoch full run ongoing.
- **MoCo-v2** [Chen et al., 2020]: InfoNCE with momentum encoder. Included in full 9-combination protocol.

**Baselines:**
- **SGD-trained SSL** (primary): Standard SSL pretraining with SGD optimizer, followed by linear probe evaluation. This is the baseline that H-E1 establishes as the problem.
- **Supervised** (oracle upper bound): Supervised cross-entropy training (ViT-S/16) with identical evaluation protocol. WGA 81.9% on Waterbirds — establishes the magnitude of the gap.
- **LFR** [Ghaznavi et al., 2023]: Annotation-free post-hoc resampling applied to SSL features. Annotation-free baseline for comparison with SAM-SSL.
- **EVaLS** [Ghaznavi et al., 2024]: Extended LFR with environment inference. Annotation-free baseline.
- **Group DRO** [Sagawa et al., 2019]: Oracle baseline requiring group labels (84.6% WGA on Waterbirds). Upper bound for label-aware methods.

### 4.4 Implementation Details

**SSL pretraining:** ResNet-50 backbone with identity final layer (2048-dim features). DINO uses ViT-S/8 with pre-trained weights from the official DINO repository. Standard augmentation: RandomResizedCrop(224), RandomHorizontalFlip, ColorJitter(0.4,0.4,0.4,0.1), RandomGrayscale(p=0.2), GaussianBlur. Batch size 256, cosine learning rate schedule, 200 pretraining epochs (10-epoch fast run for initial validation).

**SAM configuration:** rho=0.05 using davda54/sam wrapper [davda54, 2021]; ASAM variant (rho=0.5, adaptive) included as secondary variant (h-m4 hypothesis).

**Linear probe evaluation:** SGD optimizer, lr=0.01, 100 epochs (10 epochs in fast run), no group labels used. Worst-group accuracy computed over 4 groups using kohpangwei/group_DRO protocol.

**Anisotropy measurement:** N=100 random direction samples, probe epochs=100, SAM rho=0.05, checkpoint epochs {50, 100, 150, 200}. Fast run used N=5, probe epochs=10 (preliminary).

**Hardware:** Experiments ran on GPU cluster (CUDA 12.9, PyTorch with cuDNN disabled due to torch+cu124 / CUDA 12.9 driver mismatch — numerically equivalent to cuDNN-enabled training).

**Reproducibility:** Seed 1 for initial PoC run. Code built on izmailovpavel/spurious_feature_learning and kohpangwei/group_DRO frameworks.

### 4.5 Evaluation Metrics

**Primary:**
- **Worst-group accuracy (WGA):** Minimum accuracy across 4 demographic groups on test set. Evaluated using kohpangwei/group_DRO protocol. Reported as percentage.
- **Sharpness anisotropy ratio (AR):** $\text{AR}(\theta) = \Delta\mathcal{L}_{\text{spur}} / \Delta\mathcal{L}_{\text{rand}}$. Gate threshold: AR > 1.2.
- **Pearson correlation (r):** Correlation between AR and WGA across 4 checkpoints (epochs 50/100/150/200). Significance: p < 0.05.

**Secondary:**
- **Average accuracy:** Mean accuracy across all groups. Monitors core feature preservation under SAM.
- **Linear probe proxy precision/recall:** Precision and recall of top-25% high-loss samples against held-out group labels. Validates assumption A2.
