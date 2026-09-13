# Product Requirements Document: h-e1 Clusterability Diagnostic

**Date:** 2026-03-19
**Author:** Phase 3 Implementation Planning
**Hypothesis:** h-e1 - Standard SSL training on Waterbirds creates geometrically separable spurious feature clusters measurable via AMI
**Source:** 02c_experiment_brief.md (Phase 2C)
**Status:** Draft

---

## Executive Summary

### Purpose
Implement a proof-of-concept system to validate whether standard self-supervised learning (SimCLR) creates geometrically separable spurious feature clusters on the Waterbirds dataset, and whether cluster-based diagnostic (AMI ≥0.4) can predict fairness intervention efficacy (≥2pp WGA gain).

### Scope
- SimCLR SSL training (200 epochs, ResNet-50 backbone)
- K-means clustering analysis (k=4) on frozen embeddings
- Linear probe baseline (ERM) with grid search
- Cluster-balanced retraining intervention
- Comprehensive metric evaluation (AMI, WGA, ΔWGA, AUROC)

### Success Criteria
**Primary (MUST_WORK Gate):**
- High-AMI group (≥0.4): mean ΔWGA ≥2pp with 95% CI excluding zero
- Low-AMI group (<0.3): mean ΔWGA <0.5pp

**Secondary:**
- AMI-Linear Dissociation: r(AMI, Linear AUC) < 0.9
- AMI Diagnostic Utility: AUROC > 0.80

### Out of Scope (h-e1)
- LA-SSL learning-speed intervention (deferred to h-m-integrated)
- ViT-H-14 high-capacity baseline (deferred to h-c1)
- Alternative clustering algorithms (DBSCAN, HDBSCAN)

---

## Problem Statement

### Research Question
Does spurious correlation structure in SSL embeddings manifest as discrete geometric clusters that can predict fairness intervention efficacy without labels?

### Current Limitations
- No established diagnostic for when fairness interventions will work
- Cluster-based fairness approaches lack theoretical grounding
- Unclear whether clusterability is independent from linear separability

### Hypothesis to Validate
Standard SSL training on Waterbirds creates geometrically separable spurious feature clusters measurable via AMI, with AMI ≥0.4 predicting cluster-balanced retraining efficacy (≥2pp WGA gain) and AMI <0.3 yielding <0.5pp gain.

---

## Functional Requirements

### FR-1: Data Pipeline
**ID:** FR-1
**Priority:** P0 (Critical)
**Description:** Download, prepare, and load Waterbirds dataset with spurious correlation structure

**Acceptance Criteria:**
- Download Waterbirds dataset from https://nlp.stanford.edu/data/dro/waterbird_complete95_forest2water2.tar.gz
- Cache to `.data_cache/datasets/waterbirds/`
- Load metadata.csv with columns: img_path, y (label), group (0-3), place (background)
- Verify splits: Train 4,795 | Val 1,199 | Test 5,794
- Implement WaterbirdsDataset class with `__getitem__` returning (image, label, group)
- Apply appropriate transforms (train: augmentations, test: resize+normalize)

**Dependencies:** None

---

### FR-2: SimCLR SSL Pretraining
**ID:** FR-2
**Priority:** P0 (Critical)
**Description:** Train SimCLR model from scratch on Waterbirds to create SSL embeddings

**Acceptance Criteria:**
- Implement ResNet-50 encoder (pretrained=False) with projection head (2048 → 2048 → 128)
- Implement NT-Xent contrastive loss with temperature=0.5
- Apply dual augmentations: RandomResizedCrop(224), ColorJitter, RandomGrayscale, GaussianBlur
- Train 200 epochs with LARS/SGD optimizer (lr=0.3 × batch_size/256, cosine decay)
- Save checkpoint at epoch 200: `simclr_resnet50_waterbirds_ep200.pth`
- Freeze encoder after training: `encoder.eval()`, `encoder.requires_grad_(False)`

**Dependencies:** FR-1

---

### FR-3: Embedding Extraction & Clustering
**ID:** FR-3
**Priority:** P0 (Critical)
**Description:** Extract frozen 2048-dim embeddings and perform k-means clustering

**Acceptance Criteria:**
- Extract embeddings from frozen encoder for all test samples (5,794 × 2048)
- Run k-means with k=4, random_state=42, n_init=10
- Compute AMI using sklearn.metrics.adjusted_mutual_info_score
- Store cluster assignments for training samples
- Compute Silhouette score as sanity check (expect >0.3 if clusters valid)

**Dependencies:** FR-2

---

### FR-4: Linear ERM Baseline
**ID:** FR-4
**Priority:** P0 (Critical)
**Description:** Train linear probe with grid search to establish baseline WGA

**Acceptance Criteria:**
- Implement linear classifier (2048 → 2)
- Grid search over:
  - LR ∈ {0.01, 0.001, 0.0001}
  - WD ∈ {1e-4, 1e-5, 1e-6}
  - Seeds ∈ {0, 1, 2, 3, 4}
- Train 20 epochs per config, batch size 32, SGD optimizer
- Evaluate WGA on test set for each config
- Select best config by validation WGA
- Record: baseline_WGA, best_lr, best_wd, best_seed

**Dependencies:** FR-3

---

### FR-5: Cluster-Balanced Retraining
**ID:** FR-5
**Priority:** P0 (Critical)
**Description:** Apply cluster-based reweighting and measure ΔWGA

**Acceptance Criteria:**
- Compute cluster weights: 1 / (cluster_counts * num_clusters)
- Retrain linear head with weighted loss:
  - Use best hyperparameters from FR-4
  - Apply sample weights based on cluster membership
  - Train 20 epochs
- Compute WGA_cluster_balanced on test set
- Compute ΔWGA = WGA_cluster_balanced - baseline_WGA
- Verify ΔWGA ≥2pp for AMI ≥0.4 condition

**Dependencies:** FR-3, FR-4

---

### FR-6: Stratified Analysis
**ID:** FR-6
**Priority:** P0 (Critical)
**Description:** Verify AMI threshold predicts ΔWGA differential

**Acceptance Criteria:**
- Stratify results by AMI:
  - High-AMI group: AMI ≥0.4
  - Low-AMI group: AMI <0.3
- Compute mean ΔWGA for each group
- Bootstrap 95% CI for high-AMI group (if n>1 model)
- Verify high-AMI CI excludes zero
- Verify low-AMI mean <0.5pp

**Dependencies:** FR-5

---

### FR-7: Secondary Metrics - Dissociation Test
**ID:** FR-7
**Priority:** P1 (Important)
**Description:** Verify AMI is dissociable from linear separability

**Acceptance Criteria:**
- Train linear probe to predict minority group (G1 or G2) vs majority (G0 or G3)
- Compute AUROC for minority detection
- Compute Pearson correlation r(AMI, AUC)
- Verify r < 0.9 (independent metrics)

**Dependencies:** FR-3

---

### FR-8: Secondary Metrics - Diagnostic AUROC
**ID:** FR-8
**Priority:** P1 (Important)
**Description:** Verify AMI outperforms simple baseline diagnostics

**Acceptance Criteria:**
- Compute simple diagnostics:
  - Loss variance: variance of per-sample CE losses
  - Loss skewness: skewness of loss distribution
- Compute AUROC for predicting "high ΔWGA" (≥1pp) using:
  - AMI threshold (AMI ≥0.4)
  - Loss variance threshold
  - Loss skewness threshold
- Verify AMI AUROC > 0.80 AND > baseline AUROCs

**Dependencies:** FR-4

---

### FR-9: Evaluation & Reporting
**ID:** FR-9
**Priority:** P0 (Critical)
**Description:** Comprehensive metric computation and result reporting

**Acceptance Criteria:**
- Compute all primary metrics: AMI, WGA, ΔWGA
- Compute all secondary metrics: Linear AUC, AMI AUROC, Silhouette
- Generate per-group accuracy breakdown
- Create result summary table
- Save metrics to 04_validation.md
- Generate visualizations (optional): cluster UMAP, AMI distribution

**Dependencies:** FR-6, FR-7, FR-8

---

## Non-Functional Requirements

### NFR-1: Computational Efficiency
- **GPU**: Single V100 (32GB) or A100 (40GB)
- **Training Time**: SimCLR ≤8 hours, Linear probe ≤4 hours
- **Total GPU Hours**: ≤12 hours

### NFR-2: Reproducibility
- Set random seeds for all stochastic operations
- Document all hyperparameters in config file
- Save checkpoints with version metadata
- Log all experimental settings

### NFR-3: Code Quality
- Modular design: separate files for data, models, training, evaluation
- Unit tests for data loader, loss functions, metric computation
- Type hints for all functions
- Docstrings for all public functions

### NFR-4: Storage Requirements
- Waterbirds dataset: ~1.2 GB
- SimCLR checkpoint: ~100 MB
- Frozen embeddings cache: ~45 MB
- Total: ~1.5 GB

---

## Data Specifications

### Waterbirds Dataset
- **Source**: https://nlp.stanford.edu/data/dro/waterbird_complete95_forest2water2.tar.gz
- **Type**: Image classification with spurious correlations
- **Splits**: Train 4,795 | Val 1,199 | Test 5,794
- **Groups**: 4 subgroups (landbird/waterbird × land/water background)
- **Labels**: Binary (0=landbird, 1=waterbird)
- **Image Size**: Variable (resize to 224×224)
- **Cache Path**: `.data_cache/datasets/waterbirds/`

### Data Augmentations
**Training (SimCLR):**
- RandomResizedCrop(224, scale=(0.08, 1.0))
- ColorJitter(brightness=0.8, contrast=0.8, saturation=0.8, hue=0.2)
- RandomGrayscale(p=0.2)
- GaussianBlur(kernel_size=23, sigma=(0.1, 2.0))
- RandomHorizontalFlip(p=0.5)
- Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])

**Testing (Linear Probe):**
- Resize(256)
- CenterCrop(224)
- Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])

---

## Model Specifications

### SimCLR Model
- **Encoder**: ResNet-50 (pretrained=False)
- **Projection Head**: Linear(2048, 2048) → ReLU → Linear(2048, 128)
- **Embedding Dimension**: 2048 (encoder output, used for clustering)
- **Projection Dimension**: 128 (for contrastive loss)

### Linear Probe
- **Architecture**: Linear(2048, 2)
- **Input**: Frozen embeddings from SimCLR encoder
- **Output**: Logits for binary classification

---

## Evaluation Metrics

### Primary Metrics
1. **Adjusted Mutual Information (AMI)**
   - Range: [-1, 1], 1=perfect agreement, 0=random
   - Implementation: `sklearn.metrics.adjusted_mutual_info_score`
   - Threshold: AMI ≥0.4 for high clusterability

2. **Worst-Group Accuracy (WGA)**
   - Definition: min(Acc_G0, Acc_G1, Acc_G2, Acc_G3)
   - Fairness metric for minority group protection

3. **WGA Improvement (ΔWGA)**
   - Definition: WGA_cluster_balanced - WGA_baseline
   - Success: ≥2pp for high-AMI, <0.5pp for low-AMI

### Secondary Metrics
4. **Linear Separability (AUROC)**: Minority group detection
5. **AMI Diagnostic AUROC**: Predict ΔWGA ≥1pp
6. **Silhouette Score**: Cluster quality sanity check

---

## Dependencies

### Python Packages
- PyTorch ≥1.10
- torchvision ≥0.11
- scikit-learn ≥1.0
- numpy ≥1.21
- pandas ≥1.3
- scipy ≥1.7
- Pillow ≥8.3
- tqdm (progress bars)
- tensorboard (logging, optional)

### External Dependencies
- CUDA ≥11.0 (for GPU training)
- cuDNN ≥8.0
- LARS optimizer (optional, can use SGD)

---

## Success Criteria

### Primary Success (MUST_WORK Gate)
1. **High-AMI Efficacy**: Mean ΔWGA ≥2pp with 95% CI excluding zero
2. **Low-AMI Inefficacy**: Mean ΔWGA <0.5pp
3. **Gate Result**: Both criteria satisfied → PASS, AMI ≈0 consistently → FAIL

### Secondary Success (Informative)
3. **AMI-Linear Dissociation**: r(AMI, Linear AUC) < 0.9
4. **AMI Diagnostic Utility**: AUROC > 0.80 and better than baselines

### Failure Conditions (MUST_WORK Gate)
- AMI ≈0 across all checkpoints (clustering assumption violated)
- High-AMI group ΔWGA <2pp
- Low-AMI group ΔWGA ≥0.5pp (no differential)

---

## Implementation Notes

### Code Structure
```
h-e1/
├── src/
│   ├── data_loader.py       # WaterbirdsDataset, augmentations
│   ├── models.py            # SimCLR, Linear Probe
│   ├── losses.py            # NT-Xent loss, cluster-weighted loss
│   ├── train_ssl.py         # SimCLR training loop
│   ├── linear_probe.py      # Grid search, cluster retraining
│   ├── evaluate.py          # Metrics, AMI, WGA, AUROC
│   └── utils.py             # Seed setting, logging
├── configs/
│   └── simclr_waterbirds.yaml
├── tests/
│   ├── test_data_loader.py
│   ├── test_losses.py
│   └── test_metrics.py
└── run_experiment.py        # Main orchestration script
```

### Implementation References
- SimCLR: Adapted from sthalles/SimCLR (GitHub, 2480 stars)
- Clustering: sklearn.cluster.KMeans
- GroupDRO pattern: Cluster reweighting based on Sagawa et al. 2020

### Risk Mitigation
- Early AMI check at epoch 50, 100, 150, 200
- Gradient clipping (max_norm=1.0) for training stability
- Checkpoint frequently (every 50 epochs)
- Mixed precision training for 2x speedup if needed

---

## Timeline Estimate

**Week 1: SSL Pretraining**
- Data preparation, WaterbirdsDataset implementation
- SimCLR implementation (encoder, projection, NT-Xent)
- Training (200 epochs), checkpoint validation

**Week 2: Experiments**
- Embedding extraction, k-means, AMI computation
- Linear ERM baseline (grid search)
- Cluster-balanced retraining
- Stratified analysis, dissociation test
- Secondary metrics, report generation

**Total Duration**: 2 weeks (conservative estimate)

---

## Appendix: Key Code Patterns

### NT-Xent Loss (InfoNCE)
```python
def nt_xent_loss(z_i, z_j, temperature=0.5):
    batch_size = z_i.shape[0]
    z = torch.cat([z_i, z_j], dim=0)  # 2N × 128
    sim_matrix = F.cosine_similarity(z.unsqueeze(1), z.unsqueeze(0), dim=2) / temperature
    mask = torch.eye(2 * batch_size, dtype=torch.bool).to(z.device)
    sim_matrix.masked_fill_(mask, -1e9)
    pos_sim = sim_matrix[range(batch_size), range(batch_size, 2*batch_size)]
    neg_sim = sim_matrix[~mask].view(2 * batch_size, -1)
    logits = torch.cat([pos_sim.unsqueeze(1), neg_sim], dim=1)
    labels = torch.zeros(2 * batch_size, dtype=torch.long).to(z.device)
    return F.cross_entropy(logits, labels)
```

### Cluster-Balanced Loss
```python
def cluster_balanced_loss(logits, targets, cluster_labels, cluster_weights):
    ce_loss = F.cross_entropy(logits, targets, reduction='none')
    sample_weights = cluster_weights[cluster_labels]
    return (ce_loss * sample_weights).mean()
```

### AMI Computation
```python
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_mutual_info_score

kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
cluster_labels = kmeans.fit_predict(embeddings.numpy())
ami = adjusted_mutual_info_score(true_groups.numpy(), cluster_labels)
```

---

**Document Status:** Ready for Architecture Design (Step 3)
**Next Step:** Architecture Agent - Module structure and epic task breakdown
