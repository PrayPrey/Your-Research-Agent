---
stepsCompleted:
  - executive_summary
  - problem_statement
  - functional_requirements
  - non_functional_requirements
  - success_criteria
  - data_specification
  - dependencies
hypothesis_id: h-e1
hypothesis_type: EXISTENCE
tier: LIGHT
created_at: '2026-05-20'
source: Phase 2C experiment brief (02c_experiment_brief.md)
---

# PRD: H-E1 — Spurious Direction Recovery via K-Means Clustering on Epoch-5 Embeddings

## 1. Executive Summary

This document specifies requirements for validating Hypothesis H-E1: that k-means clustering (k=2) on penultimate-layer embeddings extracted at epoch 5 of standard ERM training with a pretrained ResNet-50 recovers spurious feature axes with AMI ≥ 0.5 and worst-cluster purity ≥ 75% on both Waterbirds and CelebA datasets.

This is a **EXISTENCE (PoC)** experiment — the goal is to confirm the phenomenon exists before building the GSB mechanism on top of it. It is the foundation for all downstream hypotheses (H-M1 through H-C1).

Gate type: **MUST_WORK** — failure blocks the entire pipeline.

---

## 2. Problem Statement

The Gradient SNR Balancing (GSB) hypothesis relies on the assumption that spurious feature directions can be discovered annotation-free via k-means clustering on early-training embeddings. H-E1 validates this assumption directly: if pretrained ResNet-50 embeddings at epoch 5 of ERM training already encode spurious vs. invariant feature structure separably enough for k-means (k=2) to recover group membership, then annotation-free shortcut detection is viable.

**Research gap addressed:** Prior work (PruSC, DFR) demonstrates high purity at convergence (epoch 100). H-E1 tests whether this structure is detectable much earlier (epoch 5), which is the operative time window for GSB intervention.

---

## 3. Functional Requirements

### FR-1: ERM Training Pipeline (Waterbirds)
Train ResNet-50 (ImageNet-pretrained) on Waterbirds using standard ERM. Save model checkpoint at epoch 5.
- Optimizer: SGD, momentum=0.9, weight_decay=1e-3
- LR: 1e-3
- Batch size: 32
- Augmentation: RandomResizedCrop(224), RandomHorizontalFlip, ImageNet normalize
- Full training: up to 100 epochs (only epoch-5 checkpoint needed for H-E1)
- Source: PolinaKirichenko/deep_feature_reweighting (train_classifier.py)

### FR-2: ERM Training Pipeline (CelebA)
Train ResNet-50 (ImageNet-pretrained) on CelebA using standard ERM. Save model checkpoint at epoch 5.
- Optimizer: SGD, momentum=0.9, weight_decay=1e-4
- LR: 1e-3
- Batch size: 128
- Augmentation: RandomResizedCrop(224), RandomHorizontalFlip, ImageNet normalize
- Full training: up to 50 epochs (only epoch-5 checkpoint needed for H-E1)
- Source: PolinaKirichenko/deep_feature_reweighting (train_classifier.py)

### FR-3: Penultimate-Layer Embedding Extraction
Extract 2048-dim penultimate-layer embeddings for all training samples at epoch-5 checkpoint.
- Feature extractor: `torch.nn.Sequential(*list(model.children())[:-1])` (bypasses model.fc)
- Output shape per sample: (2048,) after AdaptiveAvgPool2d squeeze
- Must also extract: class labels (y), group labels (g) for evaluation
- Apply to both Waterbirds (train split, 4795 samples) and CelebA (train split, ~162K samples)

### FR-4: K-Means Clustering Probe
Run k-means (k=2) on extracted embeddings for each dataset.
- Library: sklearn.cluster.KMeans
- Parameters: n_clusters=2, n_init=10, random_state=42
- Input: embedding matrix (N, 2048)
- Output: cluster assignments (N,)

### FR-5: AMI Computation
Compute Adjusted Mutual Information between cluster assignments and ground-truth group labels.
- Library: sklearn.metrics.adjusted_mutual_info_score
- Compare cluster_assignments vs. group_ids (4-class group labels for both datasets)
- Threshold: AMI ≥ 0.5 (both datasets)

### FR-6: Worst-Cluster Purity Computation
Compute worst-cluster purity — minimum purity across all clusters.
- For each cluster c: purity(c) = counts.max() / cluster_size
- Worst-cluster purity = min(purity(c) for c in range(k))
- group_ids used for purity (not class labels)
- Threshold: worst-cluster purity ≥ 0.75 (both datasets)

### FR-7: Mechanism Verification
Implement activation verification checks:
- Embedding shape assert: shape[1] == 2048
- Cluster non-degeneracy: both clusters contain > 10 samples
- AMI above chance: ami_actual > ami_random + 0.1

### FR-8: Visualization Generation
Generate required figures and save to `h-e1/figures/`:
- **Required:** Bar chart of AMI and worst-cluster purity per dataset vs. threshold lines (AMI=0.5, purity=0.75)
- **Additional:** t-SNE plots (epoch-5 embeddings colored by class, group, cluster)
- **Additional:** AMI vs. Epoch curve (epochs 1, 3, 5, 7, 10)
- **Additional:** Per-cluster group composition stacked bar chart

### FR-9: Results Reporting
Generate JSON/YAML results file and print summary table with:
- Per-dataset: AMI, worst-cluster purity, PASS/FAIL per threshold
- Overall gate: PASS (both datasets pass) or FAIL

### FR-10: Baseline Reference (Random Clustering)
Compute random clustering baseline for comparison:
- AMI(random_assignments, group_ids) — expected ≈ 0
- Purity(random_assignments) — expected ≈ 0.5 for balanced k=2

---

## 4. Data Specification

### Dataset 1: Waterbirds (Primary)
- **Full name:** Waterbirds (waterbird_complete95_forest2water2)
- **Download:** `https://nlp.stanford.edu/data/dro/waterbird_complete95_forest2water2.tar.gz` OR WILDS: `wilds.get_dataset(dataset='waterbirds', root_dir='./data')`
- **Local path:** `./data/waterbirds/`
- **Download method:** Manual (requires script or WILDS package)
- **Train split:** 4,795 samples
- **Val split:** 1,199 samples
- **Test split:** 5,794 samples
- **Groups (4):** G0=landbird-land, G1=landbird-water, G2=waterbird-land, G3=waterbird-water
- **Classes:** 2 (landbird=0, waterbird=1)
- **Spurious correlation:** Background (land/water) spuriously correlated with bird class
- **Preprocessing:** Resize(256), CenterCrop(224), Normalize(mean=[0.485,0.456,0.406], std=[0.229,0.224,0.225])
- **Augmentation (train):** RandomResizedCrop(224), RandomHorizontalFlip
- **Loader:** wb_data.WaterBirdsDataset from DFR repo OR WILDS

### Dataset 2: CelebA (Secondary)
- **Full name:** CelebA (Large-scale Celeb Faces Attributes)
- **Download:** torchvision.datasets.CelebA(root='./data', split='train', download=True) OR Kaggle/HuggingFace
- **Metadata:** celeba_metadata.csv from DFR repo → rename to metadata.csv
- **Local path:** `./data/celeba/`
- **Download method:** torchvision (may require manual download of images)
- **Train split:** ~162,770 samples
- **Val split:** ~19,867 samples
- **Test split:** ~19,962 samples
- **Groups (4):** G0=non-blond female, G1=blond female, G2=non-blond male, G3=blond male (~1%)
- **Classes:** 2 (non-blond=0, blond=1)
- **Spurious correlation:** Gender spuriously correlated with hair color
- **Preprocessing:** Resize(256), CenterCrop(224), Normalize ImageNet stats
- **Augmentation (train):** RandomResizedCrop(224), RandomHorizontalFlip
- **Loader:** wb_data.CelebADataset from DFR repo

### Embedding Storage
- Waterbirds train embeddings: ~4,795 × 2048 float32 ≈ 37MB (save to .npy)
- CelebA train embeddings: ~162,770 × 2048 float32 ≈ 1.3GB (save to .npy, may need chunking)

---

## 5. Non-Functional Requirements

### NFR-1: Reproducibility
- Fixed random seed (seed=42 for k-means; seed=1 for training)
- Save epoch-5 checkpoint to disk; reload for embedding extraction
- Save embeddings to .npy for re-running clustering without re-training

### NFR-2: Performance
- Training time: Waterbirds ~2-3h on single GPU for 100 epochs; only need epoch 5 → stop early
- CelebA training: ~4-6h for 50 epochs; only need epoch 5 → stop early
- Embedding extraction: <10 min for Waterbirds; <30 min for CelebA

### NFR-3: Single GPU
- Must run on single GPU (CUDA_VISIBLE_DEVICES set externally)
- Memory requirement: ResNet-50 with batch_size=128 ≈ 8GB VRAM (CelebA)

### NFR-4: Early Stopping Option
- Can stop training at epoch 5+1 (save epoch 5 checkpoint, then stop) to save compute
- H-E1 only requires epoch-5 embeddings, not full convergence

### NFR-5: Logging
- Print epoch-by-epoch training metrics (loss, accuracy)
- Print embedding extraction progress
- Print clustering results with AMI and purity values

---

## 6. Success Criteria

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| AMI — Waterbirds | ≥ 0.5 | adjusted_mutual_info_score(group_ids, cluster_assignments) |
| Worst-cluster purity — Waterbirds | ≥ 0.75 | min(counts.max()/size for each cluster) |
| AMI — CelebA | ≥ 0.5 | adjusted_mutual_info_score(group_ids, cluster_assignments) |
| Worst-cluster purity — CelebA | ≥ 0.75 | min(counts.max()/size for each cluster) |
| Mechanism activated | TRUE | embeddings.shape[1] == 2048 AND both clusters > 10 samples |
| AMI above chance | TRUE | ami_actual > ami_random + 0.1 |

**Gate result:** PASS iff ALL 4 threshold criteria are met on BOTH datasets.

**Expected outcome (from literature):** HIGH CONFIDENCE. PruSC paper reports >95% purity on CelebA at convergence. DFR achieves 97% worst-group via penultimate embeddings. Pretrained backbone encodes background/gender axes from epoch 1.

**Failure pivot:** If AMI < 0.5 at epoch 5, try epochs 3 and 7 before declaring failure.

---

## 7. Dependencies

### 7.1 Python Packages

```
torch>=2.0.0
torchvision>=0.15.0
numpy>=1.24.0
scikit-learn>=1.2.0
matplotlib>=3.7.0
seaborn>=0.12.0
pyyaml>=6.0
tqdm>=4.65.0
Pillow>=9.5.0
wilds>=2.0.0
```

### 7.2 External Repositories (Reference Only)

| Repo | URL | Purpose |
|------|-----|---------|
| DFR (official) | https://github.com/PolinaKirichenko/deep_feature_reweighting | wb_data.py, train_classifier.py, imagenet_extract_embeddings.py |
| Spurious Feature Learning | https://github.com/izmailovpavel/spurious_feature_learning | Alternative training config |
| GroupDRO | https://github.com/kohpangwei/group_DRO | Dataset format reference |

**Implementation approach:** Build on DFR repo infrastructure (wb_data.py for data loaders, train_classifier.py adapted for epoch-5 checkpoint). Do NOT copy the full DFR repo; adapt key patterns into standalone scripts.

### 7.3 Hardware
- Single GPU (lowest memory usage per `nvidia-smi`)
- Minimum 8GB VRAM for CelebA (batch_size=128)
- Minimum 100GB disk for datasets + checkpoints + embeddings

---

## 8. Out of Scope

- Multiple random seeds (5 seeds required for Phase 5/MECHANISM validation, NOT for this PoC)
- GSB intervention (H-M4)
- Gradient SNR computation (H-M1)
- Worst-group accuracy evaluation (this is a clustering experiment, not a classification benchmark)
- ViT-B backbone (secondary model — H-M4 scope)
- ColoredMNIST dataset (H-C1 scope)

---

*PRD generated from Phase 2C experiment brief (02c_experiment_brief.md)*
*Sources: PolinaKirichenko/deep_feature_reweighting, izmailovpavel/spurious_feature_learning, kohpangwei/group_DRO, PruSC (openreview.net/pdf?id=EEeVYfXor5)*
