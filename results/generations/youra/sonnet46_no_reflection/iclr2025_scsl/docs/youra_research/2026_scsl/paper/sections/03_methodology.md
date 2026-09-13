# 3. Methodology

## 3.1 Overview

Our goal is to characterize the conditions under which annotation-free spurious direction discovery via representation clustering succeeds or fails. The key insight motivating our design is that clustering success depends not on the algorithm but on whether the spurious attribute is encoded as a separable dimension in the pretrained initialization prior. To test this cleanly, we hold every experimental factor constant — model, optimizer, clustering algorithm, probe epoch, hyperparameters — and vary only the dataset's spurious feature type (dominant scene-level background vs. fine-grained local texture). This isolates spurious feature salience as the causal variable.

We follow established methodology from GEORGE [Bao et al., 2022] and related work: train an ERM model with a pretrained backbone, extract penultimate-layer embeddings at a fixed early epoch, apply k-means clustering, and evaluate cluster-to-group alignment using Adjusted Mutual Information (AMI) and worst-cluster purity. This is the annotation-free detection pipeline used by multiple downstream robustification methods.

## 3.2 Spurious Direction Discovery Pipeline

**Step 1 — ERM Training.** We fine-tune a pretrained ResNet-50 (ImageNet weights from torchvision) on each dataset using standard ERM (cross-entropy loss, SGD optimizer). Training proceeds for 5 epochs, after which we save the model checkpoint.

**Rationale:** Epoch 5 is chosen following the simplicity bias literature [Shah et al., 2020], which predicts that high-SNR spurious features are acquired early in training. Prior work (GEORGE, PruSC) uses embeddings after full convergence; we probe at epoch 5 to test whether early-epoch embeddings already carry sufficient spurious structure — a prerequisite for early-phase gradient interventions such as GSB.

**Step 2 — Embedding Extraction.** We extract the penultimate-layer (pre-classifier) representations for all training samples, yielding a matrix of shape (N, 2048). Global average pooling is applied to reduce spatial dimensions. No dimensionality reduction is applied before clustering.

**Rationale:** The penultimate layer captures the richest representation of learned features [Kirichenko et al., 2022]. Applying PCA or other reduction before clustering would confound the clustering result with a dimensionality reduction choice.

**Step 3 — k-Means Clustering.** We apply k-means with k=2, n\_init=10, and random seed 42 to the extracted embeddings. We set k=2 to match the binary spurious attribute structure (spurious present vs. absent) and to follow published methodology.

**Rationale:** k=2 is the minimal, cleanest setting — one cluster per expected spurious group. We acknowledge this may underspecify datasets with more complex group structure (see Section 6). We use this setting to match published methods and thus make the comparison to PruSC/GEORGE directly meaningful.

**Step 4 — Evaluation.** We compute two metrics against ground-truth group labels (used only for evaluation, never for training or clustering):

- **Adjusted Mutual Information (AMI):** Measures the agreement between cluster assignments and group labels, adjusted for chance. AMI=0 corresponds to random assignment; AMI=1 corresponds to perfect alignment. Threshold: AMI ≥ 0.5.
- **Worst-Cluster Purity:** For each cluster, the fraction of samples belonging to the majority group within that cluster. Worst-cluster purity reports the minimum across clusters. Threshold: purity ≥ 0.75.

**Random baseline:** We compute AMI and purity for randomly shuffled cluster assignments to establish the chance-level floor.

## 3.3 Datasets

**Waterbirds** [Sagawa et al., 2020]: Binary classification of waterbirds vs. landbirds. The spurious attribute is the background (water vs. land habitat). The spurious correlation is 95%: 95% of waterbirds appear on water backgrounds and 95% of landbirds on land. The spurious feature is a global, scene-level attribute that ImageNet pretraining encodes strongly (ImageNet contains scene/background categories).

**CelebA** [Liu et al., 2015]: Binary prediction of hair color (blonde vs. non-blonde). The spurious attribute is biological sex (female is spuriously correlated with blonde). The spurious feature is hair color — a local, fine-grained texture attribute. ImageNet pretraining does not directly encode hair color as a primary semantic category.

These two datasets are intentionally chosen to contrast in spurious feature salience while sharing the same model family, benchmark status, and role in the robustification literature. The variation in spurious attribute type (scene-level vs. texture-level) is the key independent variable in our study.

## 3.4 Model and Training Configuration

| Hyperparameter | Value |
|---|---|
| Architecture | ResNet-50 |
| Initialization | ImageNet pretrained (torchvision) |
| Optimizer | SGD |
| Learning rate | 1e-3 |
| Weight decay | 1e-3 |
| Momentum | 0.9 |
| Batch size | 32 |
| Probe epoch | 5 |
| Clustering (k) | 2 |
| Clustering (n\_init) | 10 |
| Random seed | 42 |

This configuration follows the GroupDRO/DFR repository [Sagawa et al., 2020; Kirichenko et al., 2022] for Waterbirds and CelebA. No per-dataset hyperparameter tuning is performed — using the same configuration on both datasets is essential for the conditionality comparison.

## 3.5 Evaluation Protocol

We evaluate on the training split, using ground-truth group labels exclusively for metric computation. Group labels are never used during training or clustering. This mirrors the annotation-free deployment setting: the practitioner has access to the data but not the group annotations; we use the annotations only to assess clustering quality post-hoc.

The **feature-strength conditionality hypothesis** predicts: datasets whose spurious attributes are strongly aligned with the ImageNet pretraining prior will yield AMI ≥ 0.5 and purity ≥ 0.75 at epoch 5; datasets whose spurious attributes are misaligned will fall substantially below these thresholds. Both thresholds are established by prior work [Bao et al., 2022] as the minimum criteria for reliable spurious direction discovery.
