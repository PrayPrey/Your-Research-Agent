# Experiment Design: h-e1 — Clusterability Diagnostic for Fairness Intervention

**Date:** 2026-03-19
**Author:** Claude (Phase 2C Auto-Execution)
**Hypothesis Statement:** Standard SSL training on Waterbirds creates geometrically separable spurious feature clusters measurable via AMI, with AMI ≥0.4 predicting cluster-balanced retraining efficacy (≥2pp WGA gain) and AMI <0.3 yielding <0.5pp gain
**Phase 2B Source:** 02b_verification_plan.md (Section 2.2, H-E1)
**Specification Level:** 1.5 (Concrete + Implementation-Ready)

> 🧪 **EXISTENCE (PoC) Template** - Validates whether spurious correlation clusterability predicts fairness intervention efficacy

---

## Workflow Status

**Verification State:** h-e1 IN_PROGRESS (experiment_design phase)
**Prerequisites Satisfied:** None (foundation hypothesis)
**Gate Status:** MUST_WORK gate active

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-e1
- **Type:** EXISTENCE
- **Prerequisites:** None (foundational)

### Gate Condition
**MUST_WORK** - If AMI ≈ 0 consistently (clustering fails), STOP pipeline and PIVOT to continuous density metrics

**Success Criteria (PoC):**
- **Primary**: High-AMI group (≥0.4) mean ΔWGA ≥2pp with 95% CI excluding zero; Low-AMI group (<0.3) <0.5pp
- **Secondary**: AMI diagnostic AUROC >0.80 vs simpler baselines; AMI and linear separability dissociated (r<0.9)

---

## Continuation Context

This is the foundation hypothesis - no previous hypothesis results to build upon. This hypothesis validates the core existence claim that spurious correlations in SSL embeddings manifest as geometric clusters that predict fairness intervention efficacy.

### Previous Hypothesis Results
N/A - Foundation hypothesis

**CRITICAL LESSONS from Past h-e1 Attempts (Different Hypotheses):**
1. **GNR-LLR Pipeline (2026-03-16)**: balance_deviation criterion was design flaw - use minority recall instead
2. **SAM Optimizer (2026-03-16)**: Flat minima ≠ group-robust minima - flatness regularization failed
3. **Common Pattern**: WaterbirdsDataset infrastructure proven and reusable

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: "spurious correlation SSL clusterability"**
- Limited direct results (diffusion models, ControlNet training)
- **Gap Identified**: No existing SSL clusterability fairness benchmarks
- **Implication**: Novel research direction confirmed from Phase 2A/2B

**Query 2: "AMI clustering fairness intervention"**
- No relevant SSL fairness clustering studies found
- **Key Insight**: Adjusted Mutual Information (AMI) is standard metric in sklearn
- **Action**: Use sklearn.metrics.adjusted_mutual_info_score

**Query 3: "Waterbirds dataset GroupDRO"**
- Limited results (butterfly dataset, diffusion training)
- **Known Infrastructure**: WaterbirdsDataset class exists in archived code
- **Action**: Reuse proven data loader from 20260315_scsl pipeline

**Summary**: Archon searches confirm novelty. No existing SSL clusterability-fairness studies. Standard clustering metrics (AMI, k-means) well-established in sklearn.

---

### Archon Code Examples

**Query 1: "Waterbirds SimCLR training"**
- No SimCLR code found in Archon (returned ControlNet, diffusion training)
- **Known Repository**: sthalles/SimCLR (2480 stars) from Phase 2A
- **Action**: Implement SimCLR from scratch using PyTorch + torchvision ResNet-50

**Query 2: "cluster-balanced retraining"**
- No cluster reweighting code found in Archon
- **Pattern Identified**: Standard reweighting pattern from distributed training examples
- **Implementation**: Compute cluster weights = 1 / (cluster_size * num_clusters), apply to loss

**Query 3: "k-means AMI sklearn"**
- No k-means examples found in Archon (returned CUDA BLAS, embedding code)
- **Standard Library**: sklearn.cluster.KMeans + sklearn.metrics.adjusted_mutual_info_score
- **Example Pattern**:
  ```python
  from sklearn.cluster import KMeans
  from sklearn.metrics import adjusted_mutual_info_score
  kmeans = KMeans(n_clusters=4, random_state=42)
  cluster_labels = kmeans.fit_predict(embeddings)
  ami = adjusted_mutual_info_score(true_groups, cluster_labels)
  ```

**Query 4: "ResNet-50 PyTorch training"**
- Multiple training examples found (ControlNet, diffusion models)
- **Key Pattern**: Use torchvision.models.resnet50(pretrained=True) as backbone
- **Frozen Embeddings**: model.eval(), no gradient updates during linear probe

**Code Pattern Insights**:
- SSL training: Freeze backbone → extract embeddings → k-means clustering → compute AMI
- Linear ERM: Freeze backbone → train linear head with grid search (LR, WD)
- Cluster reweighting: Same as group reweighting but using cluster assignments

**Conclusion**: SimCLR must be implemented from scratch. Standard sklearn for clustering/AMI. Reuse WaterbirdsDataset infrastructure.

---

### Exa GitHub Implementations

**Query: "SimCLR contrastive learning PyTorch"**

**Repository 1**: `sthalles/SimCLR` ⭐ 2,480 stars (RECOMMENDED)
- **URL**: https://github.com/sthalles/SimCLR
- **Relevance**: Official unofficial PyTorch SimCLR implementation
- **Architecture**: ResNet-50 encoder + projection head + NT-Xent loss
- **Key Features**:
  - InfoNCE contrastive loss
  - Multi-GPU support
  - LARS optimizer
  - Standard augmentations (RandomResizedCrop, ColorJitter, Gaussian blur)
- **Implementation Reference**:
  ```python
  # Projection head
  self.projector = nn.Sequential(
      nn.Linear(2048, 2048),
      nn.ReLU(),
      nn.Linear(2048, 128)
  )

  # NT-Xent loss
  def nt_xent_loss(z_i, z_j, temperature=0.5):
      batch_size = z_i.shape[0]
      z = torch.cat([z_i, z_j], dim=0)  # 2N x D
      sim_matrix = F.cosine_similarity(z.unsqueeze(1), z.unsqueeze(0), dim=2)
      sim_matrix = sim_matrix / temperature
      # Mask out self-similarity
      mask = torch.eye(2 * batch_size, dtype=torch.bool).to(z.device)
      sim_matrix.masked_fill_(mask, -9e15)
      # Positive pairs: (i, i+N) and (i+N, i)
      pos_sim = torch.cat([sim_matrix[range(batch_size), range(batch_size, 2*batch_size)],
                           sim_matrix[range(batch_size, 2*batch_size), range(batch_size)]])
      # Negative pairs: all others
      neg_sim = sim_matrix[~mask].view(2 * batch_size, -1)
      logits = torch.cat([pos_sim.unsqueeze(1), neg_sim], dim=1)
      labels = torch.zeros(2 * batch_size, dtype=torch.long).to(z.device)
      return F.cross_entropy(logits, labels)
  ```

**Repository 2**: `google-research/simclr` (TensorFlow - reference only)
- **URL**: https://github.com/google-research/simclr
- **Relevance**: Original Google implementation (TF 2.x)
- **Key Insights**: Batch size = 4096, temperature = 0.5, LARS optimizer critical
- **Adaptation**: PyTorch equivalent with smaller batch size (256-512) for single GPU

**Repository 3**: `PyTorchLightning/lightning-bolts` (Production-ready)
- **URL**: https://github.com/PyTorchLightning/lightning-bolts
- **Relevance**: Lightning implementation with clean modular code
- **Key Features**: Automatic mixed precision, multi-GPU, gradient clipping
- **Installation**: `pip install lightning-bolts`

**Code Reuse Strategy**:
1. Adapt `sthalles/SimCLR` NT-Xent loss + projection head
2. Use `torchvision.models.resnet50(pretrained=False)` for fair SSL training
3. Standard augmentations: RandomResizedCrop(224), ColorJitter, RandomGrayscale, GaussianBlur

---

**Query: "linear probe frozen embeddings fairness"**

**Pattern from Literature (Mehta et al. 2023)**:
- Freeze SSL encoder after pretraining
- Extract embeddings: `with torch.no_grad(): embeddings = encoder(images)`
- Train linear classifier: `linear = nn.Linear(2048, 2).to(device)`
- Grid search: LR ∈ {0.01, 0.001, 0.0001}, WD ∈ {1e-4, 1e-5, 1e-6}
- 20 epochs, batch 32, SGD optimizer, 5 random seeds

**Code Pattern** (from Phase 2B protocol):
```python
def extract_embeddings(model, dataloader, device):
    model.eval()
    embeddings, labels, groups = [], [], []
    with torch.no_grad():
        for batch in dataloader:
            imgs, y, g = batch
            emb = model(imgs.to(device))  # ResNet-50 output: 2048-dim
            embeddings.append(emb.cpu())
            labels.append(y)
            groups.append(g)
    return torch.cat(embeddings), torch.cat(labels), torch.cat(groups)

def linear_probe_grid_search(embeddings, labels, groups, device):
    best_wga = 0
    for lr in [0.01, 0.001, 0.0001]:
        for wd in [1e-4, 1e-5, 1e-6]:
            for seed in range(5):
                set_seed(seed)
                linear = nn.Linear(2048, 2).to(device)
                optimizer = optim.SGD(linear.parameters(), lr=lr, weight_decay=wd)
                # Train 20 epochs...
                wga = evaluate_worst_group_accuracy(linear, test_embeddings, test_groups)
                if wga > best_wga:
                    best_wga = wga
                    best_hparams = (lr, wd, seed)
    return best_wga, best_hparams
```

---

**Query: "cluster-balanced reweighting group fairness"**

**Pattern from GroupDRO (Sagawa et al. 2020)**:
```python
def get_cluster_weights(cluster_labels, num_clusters=4):
    """Inverse cluster frequency weighting"""
    cluster_counts = torch.bincount(cluster_labels, minlength=num_clusters)
    cluster_weights = 1.0 / (cluster_counts.float() + 1e-8)
    cluster_weights /= cluster_weights.sum()  # Normalize
    return cluster_weights

def cluster_balanced_loss(logits, targets, cluster_labels, cluster_weights):
    """Reweight loss by cluster membership"""
    ce_loss = F.cross_entropy(logits, targets, reduction='none')
    sample_weights = cluster_weights[cluster_labels]
    return (ce_loss * sample_weights).mean()
```

**Adaptation for Cluster-Balanced Retraining**:
1. After linear ERM baseline, get baseline WGA
2. Run k-means (k=4) on frozen embeddings → cluster_labels
3. Retrain linear head with cluster_balanced_loss for 20 epochs
4. Measure ΔWGA = WGA_cluster_balanced - WGA_baseline

---

## Dataset Specifications

### Primary Dataset: Waterbirds (Standard)

**Source**: GroupDRO benchmark (Sagawa et al. 2020)
- **Paper**: https://arxiv.org/abs/1911.08731
- **Official Split**: Train 4,795 | Val 1,199 | Test 5,794
- **Download**: https://nlp.stanford.edu/data/dro/waterbird_complete95_forest2water2.tar.gz

**Dataset Structure**:
```
Waterbirds/
├── train/
│   ├── landbird_on_land/    # G0: majority (spurious corr)
│   ├── landbird_on_water/   # G1: minority (no spurious)
│   ├── waterbird_on_land/   # G2: minority (no spurious)
│   └── waterbird_on_water/  # G3: majority (spurious corr)
├── val/
└── test/
```

**4-Group Structure**:
| Group | Bird Type | Background | Count (train) | Spurious? |
|-------|-----------|------------|---------------|-----------|
| G0 | Landbird | Land | 3,498 (73%) | Yes (majority) |
| G1 | Landbird | Water | 184 (4%) | No (minority) |
| G2 | Waterbird | Land | 56 (1%) | No (minority) |
| G3 | Waterbird | Water | 1,057 (22%) | Yes (majority) |

**Spurious Correlation**: 95% of landbirds on land, 95% of waterbirds on water

**Ground Truth for AMI**: 4 true subgroups (G0, G1, G2, G3) → AMI compares k-means (k=4) clusters vs true groups

**Type**: standard (real dataset, established benchmark)
**Sample Size**: 5,794 test samples (statistically meaningful, full standard test set)
**Cache Path**: `.data_cache/datasets/waterbirds/` (from proven infrastructure)

**Data Loader** (reuse from archived code):
```python
class WaterbirdsDataset(Dataset):
    def __init__(self, root_dir, split='train', transform=None):
        self.root_dir = root_dir
        self.split = split
        self.transform = transform
        # Load metadata: image paths, labels, groups, spurious attributes
        self.metadata = pd.read_csv(f"{root_dir}/metadata.csv")
        self.metadata = self.metadata[self.metadata['split'] == self._split_map[split]]

    def __getitem__(self, idx):
        img_path = self.metadata.iloc[idx]['img_path']
        label = self.metadata.iloc[idx]['y']  # 0=landbird, 1=waterbird
        group = self.metadata.iloc[idx]['group']  # 0-3
        img = Image.open(img_path).convert('RGB')
        if self.transform:
            img = self.transform(img)
        return img, label, group
```

---

### Baseline Dataset: None (h-e1 is foundational)

No baseline comparison needed for existence hypothesis.

---

## Model Specifications

### Model 1: SimCLR (ResNet-50 backbone) — Standard SSL

**Architecture**: SimCLR v2 (Chen et al. 2020)
- **Encoder**: ResNet-50 (pretrained=False, train from scratch for SSL)
- **Projection Head**: MLP (2048 → 2048 → 128) with ReLU
- **Output**: 128-dim embedding for contrastive loss, 2048-dim for linear probe

**Training Protocol**:
- **Augmentations**:
  - RandomResizedCrop(224, scale=(0.08, 1.0))
  - ColorJitter(brightness=0.8, contrast=0.8, saturation=0.8, hue=0.2)
  - RandomGrayscale(p=0.2)
  - GaussianBlur(kernel_size=23, sigma=(0.1, 2.0))
  - RandomHorizontalFlip(p=0.5)
- **Loss**: NT-Xent (InfoNCE) with temperature=0.5
- **Optimizer**: LARS (or SGD with momentum=0.9 if LARS unavailable)
- **Batch Size**: 256 (single GPU) or 512 (multi-GPU)
- **Epochs**: 200 (standard SSL pretraining)
- **Learning Rate**: 0.3 × (batch_size / 256) with cosine decay
- **Weight Decay**: 1e-6

**Implementation Source**: Adapted from sthalles/SimCLR (GitHub, 2480 stars)

**Frozen Embeddings**: After SSL training, freeze encoder and extract 2048-dim embeddings for all experiments

---

### Model 2: LA-SSL (ResNet-50) — Learning-Speed Intervention (Future)

**Status**: NOT NEEDED for h-e1 (required for h-m-integrated)
- h-e1 only tests standard SimCLR
- LA-SSL deferred to h-m-integrated (mechanism hypothesis)

---

### Linear Probe Baseline (ERM)

**Architecture**: Linear classifier (2048 → 2)
**Training Protocol** (Mehta et al. 2023):
- Freeze SimCLR encoder
- Extract embeddings: `embeddings = encoder(images).detach()`
- Grid search:
  - LR ∈ {0.01, 0.001, 0.0001}
  - WD ∈ {1e-4, 1e-5, 1e-6}
  - Seeds: 5 random seeds per config
- Epochs: 20
- Batch Size: 32
- Optimizer: SGD (no momentum for linear probe)
- Evaluation: Select best config by validation WGA

**Baseline WGA Target**: ~88-90% (mid-capacity ResNet-50 range from Phase 2B)

---

### Model 3: ViT-H-14 (High-Capacity Baseline) — Future

**Status**: NOT NEEDED for h-e1 (required for h-c1 boundary conditions)
- h-e1 uses ResNet-50 only
- ViT-H-14 deferred to h-c1 (capacity ceiling test)

---

## Experiment Procedures

### Phase 1: SSL Pretraining (SimCLR)

**Objective**: Train SimCLR on Waterbirds to create embeddings with potential spurious clusters

**Steps**:
1. **Data Preparation**:
   - Download Waterbirds dataset to `.data_cache/datasets/waterbirds/`
   - Verify metadata.csv contains: img_path, y (label), group (0-3), place (background)
   - Create train/val/test splits (4795/1199/5794)

2. **Model Setup**:
   - Initialize ResNet-50 encoder (pretrained=False)
   - Add projection head: nn.Sequential(nn.Linear(2048, 2048), nn.ReLU(), nn.Linear(2048, 128))
   - Implement NT-Xent loss with temperature=0.5

3. **Training**:
   - Apply dual augmentations to each image (two views)
   - Compute NT-Xent loss over batch
   - Train 200 epochs with LARS optimizer (lr=0.3 × batch_size/256, cosine decay)
   - Save checkpoint every 50 epochs

4. **Checkpoint Selection**:
   - Use final epoch (200) checkpoint for main experiments
   - Freeze encoder: `encoder.eval()` and `encoder.requires_grad_(False)`

**Expected Output**:
- Checkpoint: `simclr_resnet50_waterbirds_ep200.pth`
- Embedding dimension: 2048 (before projection head)
- Training time: ~6-8 hours on single V100 GPU

---

### Phase 2: Embedding Extraction & AMI Computation

**Objective**: Measure clusterability (AMI) of frozen SSL embeddings vs true subgroups

**Steps**:
1. **Extract Frozen Embeddings**:
   ```python
   encoder.eval()
   with torch.no_grad():
       embeddings = []
       labels = []
       groups = []
       for batch in test_loader:
           imgs, y, g = batch
           emb = encoder(imgs.to(device))  # 2048-dim
           embeddings.append(emb.cpu())
           labels.append(y)
           groups.append(g)
       embeddings = torch.cat(embeddings)  # (5794, 2048)
       groups = torch.cat(groups)  # (5794,)
   ```

2. **K-Means Clustering**:
   ```python
   from sklearn.cluster import KMeans
   kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
   cluster_labels = kmeans.fit_predict(embeddings.numpy())
   ```

3. **Compute AMI**:
   ```python
   from sklearn.metrics import adjusted_mutual_info_score
   ami = adjusted_mutual_info_score(groups.numpy(), cluster_labels)
   print(f"AMI: {ami:.3f}")  # Target: ≥0.4 for high-AMI
   ```

4. **Stratify Models**:
   - High-AMI: AMI ≥ 0.4
   - Low-AMI: AMI < 0.3
   - (If 0.3 ≤ AMI < 0.4: inconclusive, exclude from primary analysis)

**Expected Output**:
- AMI value: [Hypothesis predicts ≥0.4 for standard SimCLR]
- Cluster purity per group: Optional diagnostic
- Silhouette score: Optional sanity check (should be >0.3 if clusters exist)

---

### Phase 3: Linear ERM Baseline

**Objective**: Measure baseline WGA with standard linear probe (no cluster reweighting)

**Steps**:
1. **Grid Search Setup**:
   - LR grid: [0.01, 0.001, 0.0001]
   - WD grid: [1e-4, 1e-5, 1e-6]
   - Seeds: [0, 1, 2, 3, 4]
   - Total configs: 3 × 3 × 5 = 45 runs

2. **Training Loop** (per config):
   ```python
   linear = nn.Linear(2048, 2).to(device)
   optimizer = optim.SGD(linear.parameters(), lr=lr, weight_decay=wd)
   for epoch in range(20):
       for embeddings, labels, groups in train_loader:
           logits = linear(embeddings.to(device))
           loss = F.cross_entropy(logits, labels.to(device))
           optimizer.zero_grad()
           loss.backward()
           optimizer.step()
   ```

3. **Evaluation** (per config):
   - Compute WGA on test set:
     ```python
     def worst_group_accuracy(linear, embeddings, labels, groups):
         with torch.no_grad():
             logits = linear(embeddings.to(device))
             preds = logits.argmax(dim=1)
             correct = (preds == labels.to(device))
         group_accs = []
         for g in range(4):
             mask = (groups == g)
             if mask.sum() > 0:
                 group_accs.append(correct[mask].float().mean().item())
         return min(group_accs)  # WGA = min over 4 groups
     ```

4. **Select Best Config**:
   - Choose config with highest validation WGA
   - Retrain on train+val, evaluate on test
   - Record: baseline_WGA, best_lr, best_wd, best_seed

**Expected Output**:
- Baseline WGA: ~88-90% (ResNet-50 mid-capacity range)
- Best hyperparameters: (lr, wd, seed)
- Per-group accuracies: [G0, G1, G2, G3]

---

### Phase 4: Cluster-Balanced Retraining

**Objective**: Apply cluster-based reweighting and measure ΔWGA

**Steps**:
1. **Get Cluster Assignments** (from Phase 2):
   - Use k-means cluster_labels from frozen embeddings
   - Map each training sample to cluster ∈ {0, 1, 2, 3}

2. **Compute Cluster Weights**:
   ```python
   cluster_counts = torch.bincount(torch.tensor(cluster_labels), minlength=4)
   cluster_weights = 1.0 / cluster_counts.float()
   cluster_weights /= cluster_weights.sum()  # Normalize to sum=1
   ```

3. **Reweighted Training**:
   ```python
   linear = nn.Linear(2048, 2).to(device)
   optimizer = optim.SGD(linear.parameters(), lr=best_lr, weight_decay=best_wd)
   for epoch in range(20):
       for embeddings, labels, cluster_ids in train_loader:
           logits = linear(embeddings.to(device))
           ce_loss = F.cross_entropy(logits, labels.to(device), reduction='none')
           sample_weights = cluster_weights[cluster_ids].to(device)
           loss = (ce_loss * sample_weights).mean()
           optimizer.zero_grad()
           loss.backward()
           optimizer.step()
   ```

4. **Evaluation**:
   - Compute WGA_cluster_balanced on test set
   - Compute ΔWGA = WGA_cluster_balanced - baseline_WGA

**Expected Output**:
- WGA_cluster_balanced: [Hypothesis: baseline_WGA + 2pp if AMI ≥0.4]
- ΔWGA: [Hypothesis: ≥2pp for high-AMI, <0.5pp for low-AMI]

---

### Phase 5: Stratified Analysis (AMI Threshold Test)

**Objective**: Verify AMI ≥0.4 predicts ΔWGA ≥2pp; AMI <0.3 yields <0.5pp

**Steps**:
1. **Stratify Results**:
   - High-AMI group: All runs with AMI ≥0.4
   - Low-AMI group: All runs with AMI <0.3
   - (For h-e1, only 1 SimCLR model, so stratification is single-point)

2. **Compute Statistics**:
   - High-AMI: mean ΔWGA, 95% CI (bootstrap if n>1 model)
   - Low-AMI: mean ΔWGA, 95% CI
   - Test: CI for high-AMI excludes zero, mean ≥2pp

3. **Gate Evaluation**:
   - **PASS**: High-AMI mean ≥2pp, Low-AMI <0.5pp
   - **FAIL**: AMI ≈0 (clustering invalid) → PIVOT to density metrics

**Expected Output**:
- High-AMI ΔWGA: ≥2pp (95% CI: [lower_bound, upper_bound])
- Low-AMI ΔWGA: <0.5pp
- Gate result: PASS/FAIL

---

### Phase 6: Secondary Metrics (Dissociation Test)

**Objective**: Verify AMI is dissociable from linear separability (not redundant)

**Steps**:
1. **Linear Separability (AUC)**:
   - Train linear probe to predict minority group (G1 or G2) vs majority (G0 or G3)
   - Compute AUROC for minority detection
   ```python
   from sklearn.metrics import roc_auc_score
   is_minority = (groups == 1) | (groups == 2)  # Binary: minority vs majority
   logits = linear(embeddings)
   probs = torch.softmax(logits, dim=1)[:, 1]  # P(waterbird)
   auc = roc_auc_score(is_minority.numpy(), probs.numpy())
   ```

2. **Dissociation Test**:
   - Compute Pearson correlation: r(AMI, AUC)
   - **PASS**: r < 0.9 (independent metrics)
   - **FAIL**: r ≥ 0.9 (AMI redundant with linear separability)

**Expected Output**:
- Linear AUC: [value]
- Pearson r(AMI, AUC): <0.9 (dissociation confirmed)

---

### Phase 7: Baseline Comparison (Simple Diagnostics)

**Objective**: Verify AMI AUROC >0.80 vs loss variance/skewness baselines

**Steps**:
1. **Compute Simple Diagnostics**:
   - **Loss Variance**: Variance of per-sample CE losses
     ```python
     with torch.no_grad():
         logits = linear(embeddings)
         losses = F.cross_entropy(logits, labels, reduction='none')
         loss_variance = losses.var().item()
     ```
   - **Loss Skewness**: Skewness of loss distribution
     ```python
     from scipy.stats import skew
     loss_skewness = skew(losses.numpy())
     ```

2. **AUROC Comparison**:
   - Predict "high ΔWGA" (≥1pp) using:
     - AMI threshold (AMI ≥0.4)
     - Loss variance threshold
     - Loss skewness threshold
   - Compute AUROC for each predictor
   - **Target**: AMI AUROC > 0.80 AND better than baselines

**Expected Output**:
- AMI AUROC: >0.80
- Loss variance AUROC: [value]
- Loss skewness AUROC: [value]
- AMI outperforms simple baselines: True/False

---

## Metrics & Evaluation

### Primary Metrics

**1. Adjusted Mutual Information (AMI)**
- **Definition**: AMI(true_groups, cluster_labels) ∈ [-1, 1]
- **Interpretation**:
  - AMI = 1: Perfect agreement
  - AMI = 0: Random clustering
  - AMI < 0: Worse than random (rare)
- **Implementation**: `sklearn.metrics.adjusted_mutual_info_score`
- **Success Threshold**: AMI ≥0.4 for high clusterability

**2. Worst-Group Accuracy (WGA)**
- **Definition**: WGA = min(Acc_G0, Acc_G1, Acc_G2, Acc_G3)
- **Interpretation**: Fairness metric - lowest-performing subgroup
- **Success Target**: ΔWGA ≥2pp after cluster-balanced retraining

**3. WGA Improvement (ΔWGA)**
- **Definition**: ΔWGA = WGA_cluster_balanced - WGA_baseline
- **Interpretation**: Percentage point gain from cluster reweighting
- **Success Criteria**:
  - High-AMI (≥0.4): ΔWGA ≥2pp
  - Low-AMI (<0.3): ΔWGA <0.5pp
- **Statistical Test**: 95% confidence interval excludes zero for high-AMI

---

### Secondary Metrics

**4. Linear Separability (AUROC)**
- **Definition**: AUROC for minority group detection using linear probe
- **Purpose**: Dissociation test (AMI vs linear separability)
- **Success**: r(AMI, AUROC) < 0.9 (independent metrics)

**5. AMI Diagnostic AUROC**
- **Definition**: AUROC for predicting ΔWGA ≥1pp using AMI threshold
- **Purpose**: Diagnostic utility comparison vs baselines
- **Success**: AMI AUROC > 0.80

**6. Silhouette Score (Sanity Check)**
- **Definition**: Mean silhouette coefficient for k-means clusters
- **Purpose**: Verify cluster quality (optional)
- **Interpretation**: >0.3 indicates reasonable cluster separation

---

### Evaluation Protocols

**Per-Group Accuracy**:
```python
def compute_group_accuracies(preds, labels, groups):
    group_accs = {}
    for g in range(4):
        mask = (groups == g)
        if mask.sum() > 0:
            correct = (preds[mask] == labels[mask]).float().mean()
            group_accs[f'G{g}'] = correct.item()
    return group_accs
```

**Worst-Group Accuracy**:
```python
def compute_wga(group_accs):
    return min(group_accs.values())
```

**95% Confidence Interval** (Bootstrap if n>1 model):
```python
from scipy.stats import bootstrap
def bootstrap_ci(deltas, n_bootstrap=1000, confidence=0.95):
    result = bootstrap((deltas,), np.mean, n_resamples=n_bootstrap)
    return result.confidence_interval
```

---

## Success Criteria

### Primary Success (Gate: MUST_WORK)

**Criterion 1: High-AMI Efficacy**
- **Metric**: Mean ΔWGA for high-AMI group (AMI ≥0.4)
- **Target**: ≥2pp with 95% CI excluding zero
- **Evaluation**: Compute mean ΔWGA across high-AMI runs, bootstrap CI
- **Gate PASS**: Mean ≥2pp AND CI lower bound >0

**Criterion 2: Low-AMI Inefficacy**
- **Metric**: Mean ΔWGA for low-AMI group (AMI <0.3)
- **Target**: <0.5pp
- **Evaluation**: Compute mean ΔWGA across low-AMI runs
- **Gate PASS**: Mean <0.5pp

**Combined Gate**:
- **PASS**: Both criteria 1 and 2 satisfied → Clustering predicts intervention efficacy
- **FAIL**: AMI ≈0 consistently (clustering assumption violated) → STOP, PIVOT to density metrics

---

### Secondary Success (Informative, Not Gate-Blocking)

**Criterion 3: AMI-Linear Dissociation**
- **Metric**: Pearson r(AMI, Linear AUC)
- **Target**: r < 0.9
- **Evaluation**: Compute correlation across models/seeds
- **Outcome**:
  - r < 0.9: AMI provides independent diagnostic value
  - r ≥ 0.9: AMI redundant with linear separability (document as finding)

**Criterion 4: AMI Diagnostic Utility**
- **Metric**: AUROC for predicting ΔWGA ≥1pp using AMI
- **Target**: >0.80
- **Baseline**: Loss variance, loss skewness
- **Outcome**:
  - AUROC >0.80 AND > baselines: AMI is superior diagnostic
  - AUROC ≤0.80: AMI weak predictor (document limitation)

---

## Expected Outcomes

### If Hypothesis Passes (AMI ≥0.4 predicts ΔWGA ≥2pp)

**Implications**:
1. Spurious correlations in SSL embeddings manifest as geometric clusters
2. AMI is a valid label-free diagnostic for fairness intervention efficacy
3. Cluster-balanced retraining is a practical fairness intervention
4. Proceed to h-m-integrated (3-step mechanism validation)

**Next Steps**:
- h-m-integrated: Test M1 (InfoNCE creates clusters), M2 (AMI→ΔWGA correlation), M3 (LA-SSL geometry reshaping)
- Publish Tier 1: "Clusterability as Fairness Diagnostic" (NeurIPS/ICML workshop)

---

### If Hypothesis Fails (AMI ≈0, clustering invalid)

**Root Causes**:
- Spurious features form continuous manifolds, not discrete clusters
- K-means assumption violated (non-spherical geometry)
- ResNet-50 embeddings too high-dimensional for cluster separation

**Reflection & Routing**:
- **Gate Type**: MUST_WORK
- **Action**: STOP pipeline, PIVOT to Phase 2A-Dialogue
- **Alternative Hypotheses**:
  - Replace k-means with DBSCAN/HDBSCAN (density-based)
  - Use kernel density estimation instead of discrete clusters
  - Test dimensionality reduction (PCA, UMAP) before clustering

**Serena Memory**: Record clustering failure, AMI distribution, alternative metrics to explore

---

## Implementation Estimates

### Computational Resources

**GPU Requirements**:
- **SimCLR Training**: 1x V100 (32GB) or A100 (40GB)
  - Batch size 256: 1 GPU sufficient
  - Training time: 6-8 hours for 200 epochs
- **Linear Probe Grid Search**: 1x V100 or CPU
  - 45 configs × 20 epochs × 5 min = ~4 hours
- **Total GPU hours**: ~12 hours (single V100)

**Storage**:
- Waterbirds dataset: ~1.2 GB
- SimCLR checkpoint: ~100 MB
- Frozen embeddings: ~45 MB (5794 × 2048 × 4 bytes)
- Total: ~1.5 GB

---

### Code Complexity

**Lines of Code Estimate**:
- **data_loader.py**: ~150 lines (WaterbirdsDataset, augmentations)
- **simclr.py**: ~200 lines (ResNet-50 + projection head, NT-Xent loss)
- **train_ssl.py**: ~150 lines (SimCLR training loop)
- **linear_probe.py**: ~200 lines (grid search, cluster-balanced retraining)
- **evaluate.py**: ~150 lines (AMI, WGA, AUROC, dissociation test)
- **run_experiment.py**: ~100 lines (orchestration)
- **tests/**: ~200 lines (unit tests for each module)
- **Total**: ~1,150 lines

**Implementation Difficulty**: Medium
- SimCLR from scratch: Moderate (NT-Xent loss tricky)
- K-means + AMI: Easy (sklearn one-liners)
- Cluster reweighting: Easy (GroupDRO pattern)

---

### Timeline Estimate

**Week 1: SSL Pretraining**
- Day 1-2: Data preparation, WaterbirdsDataset
- Day 3-4: SimCLR implementation (encoder, projection, NT-Xent)
- Day 5-7: Training (200 epochs), checkpoint validation

**Week 2: Experiments**
- Day 1: Embedding extraction, k-means, AMI computation
- Day 2-3: Linear ERM baseline (grid search)
- Day 4: Cluster-balanced retraining
- Day 5: Stratified analysis, dissociation test
- Day 6-7: Secondary metrics, diagnostic AUROC, report generation

**Total Duration**: 2 weeks (conservative estimate for single-hypothesis PoC)

---

## Risk Mitigation

### Risk 1: AMI ≈0 (Clustering Fails)

**Probability**: Medium (R1 from Phase 2B)
**Impact**: High (MUST_WORK gate failure)

**Mitigation**:
- **Early Detection**: Compute AMI on epoch 50, 100, 150, 200 checkpoints
- **Sanity Check**: Silhouette score >0.3 (cluster quality)
- **Fallback**: If AMI <0.2 across all checkpoints → STOP early, save 1 week

---

### Risk 2: SimCLR Training Instability

**Probability**: Low (established method)
**Impact**: Medium (delays Week 1)

**Mitigation**:
- **Use Proven Hyperparameters**: sthalles/SimCLR defaults
- **Gradient Clipping**: max_norm=1.0 to prevent explosion
- **Checkpoint Frequently**: Every 50 epochs for recovery

---

### Risk 3: Low Baseline WGA (<85%)

**Probability**: Low (ResNet-50 proven)
**Impact**: Low (doesn't block gate, affects headroom only)

**Mitigation**:
- **Use Pretrained Weights**: If from-scratch SSL underperforms, use ImageNet pretrained encoder
- **Document**: Record baseline WGA, proceed with ΔWGA analysis regardless

---

### Risk 4: Compute Resource Constraints

**Probability**: Low (single GPU sufficient)
**Impact**: Medium (delays timeline)

**Mitigation**:
- **Reduce Batch Size**: 128 instead of 256 (adjust LR proportionally)
- **Mixed Precision**: Use torch.cuda.amp for 2x speedup
- **Cloud Backup**: Google Colab Pro or Lambda Labs if local GPU unavailable

---

## Open Questions

### Q1: How many random seeds for SimCLR training?

**Answer**: 1 seed for h-e1 (PoC mode)
- Full publication: 5 seeds recommended
- h-e1 purpose: Existence proof (does clustering work at all?)
- If AMI ≥0.4 with 1 seed → hypothesis supported, proceed to h-m-integrated for robustness

---

### Q2: Should we use ImageNet pretrained or train from scratch?

**Answer**: Train from scratch (fair SSL evaluation)
- Mehta et al. used pretrained ViT-H-14, but for SSL fairness research, training SSL from scratch is standard
- Pretrained weights may have different spurious feature structure
- If training fails (AMI ≈0), fallback to pretrained as sanity check

---

### Q3: What if AMI is in gray zone (0.3 ≤ AMI < 0.4)?

**Answer**: Report as inconclusive, proceed conditionally
- Gray zone: Weak clusterability, uncertain prediction
- Test ΔWGA anyway, report actual correlation
- If ΔWGA ≥2pp: Hypothesis supported despite moderate AMI
- If ΔWGA <0.5pp: Clustering threshold needs refinement

---

## Appendix: Code Pseudo-code

### A1: SimCLR Training Loop

```python
# simclr.py
class SimCLR(nn.Module):
    def __init__(self, base_encoder='resnet50', projection_dim=128):
        super().__init__()
        self.encoder = torchvision.models.resnet50(pretrained=False)
        self.encoder.fc = nn.Identity()  # Remove classification head
        self.projector = nn.Sequential(
            nn.Linear(2048, 2048),
            nn.ReLU(),
            nn.Linear(2048, projection_dim)
        )

    def forward(self, x):
        h = self.encoder(x)  # 2048-dim
        z = self.projector(h)  # 128-dim
        return h, z

def nt_xent_loss(z_i, z_j, temperature=0.5):
    batch_size = z_i.shape[0]
    z = torch.cat([z_i, z_j], dim=0)  # 2N × 128
    sim_matrix = F.cosine_similarity(z.unsqueeze(1), z.unsqueeze(0), dim=2)
    sim_matrix = sim_matrix / temperature

    # Mask self-similarity
    mask = torch.eye(2 * batch_size, dtype=torch.bool).to(z.device)
    sim_matrix.masked_fill_(mask, -1e9)

    # Positive pairs: (i, i+N)
    pos_indices = torch.arange(batch_size)
    pos_sim = sim_matrix[pos_indices, pos_indices + batch_size]

    # Negatives: all others
    neg_sim = sim_matrix[~mask].view(2 * batch_size, -1)

    # InfoNCE: -log(exp(pos) / sum(exp(all)))
    logits = torch.cat([pos_sim.unsqueeze(1), neg_sim], dim=1)
    labels = torch.zeros(2 * batch_size, dtype=torch.long).to(z.device)
    return F.cross_entropy(logits, labels)

# train_ssl.py
model = SimCLR().to(device)
optimizer = optim.SGD(model.parameters(), lr=0.3, momentum=0.9, weight_decay=1e-6)
scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=200)

for epoch in range(200):
    for (img1, img2), labels, groups in train_loader:
        h_i, z_i = model(img1.to(device))
        h_j, z_j = model(img2.to(device))
        loss = nt_xent_loss(z_i, z_j)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
    scheduler.step()
    if epoch % 50 == 0:
        torch.save(model.state_dict(), f'simclr_ep{epoch}.pth')
```

---

### A2: Embedding Extraction & AMI

```python
# evaluate.py
def extract_embeddings(model, dataloader, device):
    model.encoder.eval()
    embeddings, labels, groups = [], [], []
    with torch.no_grad():
        for imgs, y, g in dataloader:
            h, _ = model(imgs.to(device))  # h = 2048-dim encoder output
            embeddings.append(h.cpu())
            labels.append(y)
            groups.append(g)
    return torch.cat(embeddings), torch.cat(labels), torch.cat(groups)

def compute_ami(embeddings, groups):
    from sklearn.cluster import KMeans
    from sklearn.metrics import adjusted_mutual_info_score

    kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
    cluster_labels = kmeans.fit_predict(embeddings.numpy())
    ami = adjusted_mutual_info_score(groups.numpy(), cluster_labels)
    return ami, cluster_labels

# Usage
embeddings, labels, groups = extract_embeddings(model, test_loader, device)
ami, cluster_labels = compute_ami(embeddings, groups)
print(f"AMI: {ami:.3f}")
```

---

### A3: Cluster-Balanced Retraining

```python
# linear_probe.py
def cluster_balanced_retraining(embeddings, labels, cluster_labels, lr, wd, device):
    # Compute cluster weights
    cluster_counts = torch.bincount(torch.tensor(cluster_labels), minlength=4)
    cluster_weights = 1.0 / cluster_counts.float()
    cluster_weights /= cluster_weights.sum()
    cluster_weights = cluster_weights.to(device)

    # Linear classifier
    linear = nn.Linear(embeddings.shape[1], 2).to(device)
    optimizer = optim.SGD(linear.parameters(), lr=lr, weight_decay=wd)

    # Training loop
    dataset = TensorDataset(embeddings, labels, torch.tensor(cluster_labels))
    loader = DataLoader(dataset, batch_size=32, shuffle=True)

    for epoch in range(20):
        for emb, y, c in loader:
            logits = linear(emb.to(device))
            ce_loss = F.cross_entropy(logits, y.to(device), reduction='none')
            sample_weights = cluster_weights[c.to(device)]
            loss = (ce_loss * sample_weights).mean()
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

    return linear

# Evaluation
def compute_wga(linear, embeddings, labels, groups, device):
    linear.eval()
    with torch.no_grad():
        logits = linear(embeddings.to(device))
        preds = logits.argmax(dim=1).cpu()

    group_accs = []
    for g in range(4):
        mask = (groups == g)
        if mask.sum() > 0:
            acc = (preds[mask] == labels[mask]).float().mean().item()
            group_accs.append(acc)
    return min(group_accs)

# Usage
linear_baseline = train_linear_erm(...)  # Standard ERM
linear_cluster = cluster_balanced_retraining(embeddings, labels, cluster_labels, lr, wd, device)
wga_baseline = compute_wga(linear_baseline, test_embeddings, test_labels, test_groups, device)
wga_cluster = compute_wga(linear_cluster, test_embeddings, test_labels, test_groups, device)
delta_wga = wga_cluster - wga_baseline
print(f"ΔWGA: {delta_wga:.1f} pp")
```

---

## Document Metadata

**Version**: 1.0
**Status**: COMPLETE
**Next Phase**: Phase 3 (Implementation Planning)
**Estimated Completion**: 2 weeks from Phase 3 start
**Critical Dependencies**: Single V100 GPU, Waterbirds dataset access

---

**END OF EXPERIMENT DESIGN DOCUMENT**
