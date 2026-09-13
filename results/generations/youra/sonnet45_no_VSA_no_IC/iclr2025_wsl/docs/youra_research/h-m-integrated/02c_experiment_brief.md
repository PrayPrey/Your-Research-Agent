# Experiment Design Brief: h-m-integrated
## Hierarchical VAE Mechanism Chain

**Hypothesis ID:** h-m-integrated  
**Type:** MECHANISM  
**Date:** 2026-08-20  
**Prerequisite:** h-e1 (VALIDATED)

---

## 1. Hypothesis Statement

Under heterogeneous model zoos with architecture-specific encoders (NFN/UNF), hierarchical pooling, and Transformer sequence modeling, if we train the 3-level VAE with contrastive supervision, then same-task different-architecture models will exhibit:
1. Task-invariant weight patterns at layer-summary level
2. Higher CKA similarity (>0.6) than different-task pairs (<0.4)
3. Tighter clustering (lower WCSS) in latent space
4. Successful cross-architecture relational discovery via self-attention

**Rationale:** Task constraints dominate architecture-specific implementation details at coarse-grained scale.

---

## 2. Dataset Specification

### 2.1 Primary Dataset: ModelZooDataset (CIFAR-10 Subset)

**Type:** standard  
**Source:** https://doi.org/10.5281/zenodo.6620868  
**Format:** Preprocessed PyTorch `.pt` files with vectorized weights

**Dataset Properties:**
- **Total Models:** 2,120 models (from h-e1 validation)
- **Architectures:** 4 families (CNN-small, CNN-large, ResNet-18, ResNet-34)
- **Tasks:** 9 vision tasks (CIFAR-10, CIFAR-100, TinyImageNet, MNIST, FashionMNIST, SVHN, USPS, STL10, EuroSAT)
- **Coverage:** 72.2% cells with ≥30 models (validated in h-e1)
- **Critical Cells:** CNN-CIFAR10 (250 models), ResNet-CIFAR100 (200 models), ResNet-TinyImageNet (120 models)

**Files to Download:**
```
dataset_cifar_small_hyp_rand.pt  (1.8 GB) - CNN-small models
dataset_cifar_large_hyp_rand.pt  (5.5 GB) - CNN-large models  
index_dict_small.json            (733 B)  - Weight index mapping
index_dict_large.json            (741 B)  - Weight index mapping
```

**Additional Sources (for cross-architecture validation):**
- CIFAR-10 ResNet-18: https://ai.unisg.ch/files/tar_files/tune_zoo_cifar10_resnet18_kaiming_uniform.tar
- CIFAR-100 ResNet-18: https://ai.unisg.ch/files/tar_files/tune_zoo_cifar100_resnet18_kaiming_uniform.tar

### 2.2 Data Splits

**Phase 1 (CKA Feasibility Gate):**
- Sample: 200 model pairs (100 same-task, 100 different-task)
- Stratified by architecture families
- Validation set for CKA threshold calibration

**Phase 2-3 (VAE Training):**
- Train: 1,484 models (70%)
- Validation: 318 models (15%)
- Test: 318 models (15%)
- Split maintains architecture-task balance

**Phase 4 (PoC Validation):**
- WCSS bootstrap: 100 resamples from test set
- Ablation study: Full test set (318 models)

### 2.3 Data Preparation Pipeline

**Step 1: Download and Cache**
```python
from torch.utils.data import Dataset
import torch

class ModelZooDataset(Dataset):
    def __init__(self, pt_file_path, index_dict_path):
        self.data = torch.load(pt_file_path)
        with open(index_dict_path, 'r') as f:
            self.index_dict = json.load(f)
    
    def __getitem__(self, idx):
        model_weights = self.data['weights'][idx]      # Vectorized weights
        architecture = self.data['architecture'][idx]   # CNN-small/large
        task = self.data['task'][idx]                   # CIFAR10, etc.
        hyperparams = self.data['hyperparams'][idx]     # LR, batch size, etc.
        return {
            'weights': model_weights,
            'architecture': architecture,
            'task': task,
            'metadata': hyperparams
        }
```

**Step 2: Architecture-Task Pairing**
- Generate same-task pairs: Select models with identical task labels, different architectures
- Generate different-task pairs: Select models with different task labels, same architecture
- Balance pair counts: 100 pairs per category for Phase 1

**Step 3: Normalization**
- Per-architecture z-score normalization (mean=0, std=1)
- Preserves architecture-specific scale information

---

## 3. Baseline Experiments

### 3.1 Baseline 1: Architecture-Conditioned MLP

**Purpose:** Test whether architecture labels alone predict clustering (null hypothesis control)

**Architecture:**
```python
class ArchConditionedMLP(nn.Module):
    def __init__(self, weight_dim, arch_vocab_size=4, hidden_dim=512, latent_dim=512):
        super().__init__()
        self.arch_embedding = nn.Embedding(arch_vocab_size, 64)
        self.encoder = nn.Sequential(
            nn.Linear(weight_dim + 64, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, latent_dim)
        )
    
    def forward(self, weights, arch_id):
        arch_emb = self.arch_embedding(arch_id)
        x = torch.cat([weights, arch_emb], dim=-1)
        return self.encoder(x)
```

**Training:**
- Loss: Standard reconstruction loss (MSE)
- No contrastive learning or task labels
- Epochs: 100
- Batch size: 32

**Evaluation Metric:** WCSS on latent embeddings (should be higher than hierarchical VAE if task structure exists)

### 3.2 Baseline 2: NFN-only (Single Architecture)

**Purpose:** Validate that NFN works within-architecture before cross-architecture extension

**Architecture:** NFN encoder from https://github.com/AllanYangZhou/nfn
- Permutation-equivariant layers for CNN weights
- Latent dim: 512
- Train only on CNN-small models

**Training:**
- Standard VAE loss (reconstruction + KL divergence)
- No cross-architecture pooling
- Epochs: 100

**Evaluation Metric:** Reconstruction accuracy on held-out CNN-small models (should be >70% per Risk R3)

### 3.3 Baseline 3: CKA Direct Comparison (No VAE)

**Purpose:** Measure upper bound of CKA similarity without VAE compression

**Method:**
- Compute CKA directly on raw vectorized weights
- Linear kernel: K = X @ X.T
- No learned transformation

**Evaluation Metric:** Raw CKA scores for same-task vs different-task pairs (establishes feasibility threshold)

---

## 4. Implementation Plan

### 4.1 Phase 1: CKA Feasibility Gate (Weeks 1-2)

**Goal:** Validate architecture subspaces are metrically compatible before VAE training

**Implementation Steps:**

**Step 1.1: Architecture-Specific Encoders**
```python
class NFNEncoder(nn.Module):
    """Permutation-equivariant encoder for CNN weights"""
    def __init__(self, weight_dim, hidden_dim=256, latent_dim=512):
        super().__init__()
        # Simplified NFN: DeepSets-style aggregation
        self.phi = nn.Sequential(
            nn.Linear(weight_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim)
        )
        self.rho = nn.Sequential(
            nn.Linear(hidden_dim, latent_dim),
            nn.ReLU(),
            nn.Linear(latent_dim, latent_dim)
        )
    
    def forward(self, weights):
        # weights: (batch, num_neurons, neuron_dim)
        x = self.phi(weights)              # Per-neuron transform
        x = torch.mean(x, dim=1)           # Permutation-invariant pooling
        return self.rho(x)                 # Global representation
```

**Step 1.2: CKA Computation**
```python
def linear_cka(X, Y):
    """
    X, Y: (n_samples, feature_dim)
    Returns: CKA similarity score [0, 1]
    """
    # Gram matrices
    K = X @ X.T  # (n, n)
    L = Y @ Y.T  # (n, n)
    
    # Centering matrix
    n = K.shape[0]
    H = torch.eye(n) - torch.ones(n, n) / n
    
    # Centered Gram matrices
    K_c = H @ K @ H
    L_c = H @ L @ H
    
    # HSIC
    hsic_kl = torch.trace(K_c @ L_c) / (n - 1)**2
    hsic_kk = torch.trace(K_c @ K_c) / (n - 1)**2
    hsic_ll = torch.trace(L_c @ L_c) / (n - 1)**2
    
    # CKA
    cka = hsic_kl / torch.sqrt(hsic_kk * hsic_ll)
    return cka.item()
```

**Step 1.3: Feasibility Test**
- Encode 200 model pairs using NFN encoders
- Compute CKA for same-task pairs (expect median >0.6)
- Compute CKA for different-task pairs (expect median <0.4)
- **GATE CRITERION:** If same-task CKA <0.5 OR different-task CKA >0.5, STOP (Risk R5 realized)

**Compute Resources:**
- GPU: 1x NVIDIA V100 (16 GB VRAM)
- Time: 2 days (200 pairs × 5 min/pair)
- Storage: 10 GB (cached encoders)

### 4.2 Phase 2-3: Hierarchical VAE Training (Weeks 3-4)

**Goal:** Train 3-level VAE with contrastive supervision

**Architecture Design:**

**Level 1: Architecture-Specific Encoders**
- NFN for CNN-small, CNN-large
- UNF for ResNet-18, ResNet-34
- Output: Per-neuron embeddings (variable length)

**Level 2: Hierarchical Pooling**
```python
class HierarchicalPooling(nn.Module):
    def __init__(self, input_dim=512, output_dim=512):
        super().__init__()
        self.layer_pool = nn.Sequential(
            nn.Linear(input_dim, output_dim),
            nn.ReLU(),
            nn.LayerNorm(output_dim)
        )
    
    def forward(self, neuron_embeddings):
        # neuron_embeddings: (batch, num_neurons, dim)
        # Pool per layer, then across layers
        layer_summaries = torch.mean(neuron_embeddings, dim=1)  # (batch, dim)
        return self.layer_pool(layer_summaries)
```

**Level 3: Transformer Sequence Modeling**
```python
class TransformerRelational(nn.Module):
    def __init__(self, latent_dim=512, num_heads=8, num_layers=6):
        super().__init__()
        self.arch_token = nn.Parameter(torch.randn(1, 1, latent_dim))
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=latent_dim,
            nhead=num_heads,
            dim_feedforward=2048,
            batch_first=True
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers)
        self.mu = nn.Linear(latent_dim, latent_dim)
        self.logvar = nn.Linear(latent_dim, latent_dim)
    
    def forward(self, layer_summaries):
        # layer_summaries: (batch, num_layers, latent_dim)
        batch_size = layer_summaries.shape[0]
        arch_tokens = self.arch_token.expand(batch_size, -1, -1)
        x = torch.cat([arch_tokens, layer_summaries], dim=1)
        x = self.transformer(x)
        z = x[:, 0, :]  # CLS token
        return self.mu(z), self.logvar(z)
```

**Complete Hierarchical VAE:**
```python
class HierarchicalVAE(nn.Module):
    def __init__(self):
        super().__init__()
        # Level 1
        self.nfn_encoders = nn.ModuleDict({
            'cnn_small': NFNEncoder(weight_dim=10000),
            'cnn_large': NFNEncoder(weight_dim=50000),
            'resnet18': NFNEncoder(weight_dim=100000),
            'resnet34': NFNEncoder(weight_dim=200000)
        })
        # Level 2
        self.pooling = HierarchicalPooling()
        # Level 3
        self.transformer = TransformerRelational()
        # Decoder (shared)
        self.decoder = nn.Sequential(
            nn.Linear(512, 1024),
            nn.ReLU(),
            nn.Linear(1024, 2048),
            nn.ReLU()
        )
    
    def encode(self, weights, arch_type):
        encoder = self.nfn_encoders[arch_type]
        neuron_emb = encoder(weights)
        layer_summaries = self.pooling(neuron_emb)
        mu, logvar = self.transformer(layer_summaries)
        return mu, logvar
    
    def reparameterize(self, mu, logvar):
        std = torch.exp(0.5 * logvar)
        eps = torch.randn_like(std)
        return mu + eps * std
    
    def decode(self, z):
        return self.decoder(z)
```

**Training Procedure:**

**Three-Level Supervision:**
1. **Coarse Task Labels:** Cross-entropy loss for task classification
2. **Contrastive Triplet Loss:**
   ```python
   def contrastive_loss(anchor, positive, negative, margin=0.3):
       # anchor: same-task same-arch
       # positive: same-task different-arch
       # negative: different-task
       pos_dist = torch.norm(anchor - positive, dim=1)
       neg_dist = torch.norm(anchor - negative, dim=1)
       loss = torch.relu(pos_dist - neg_dist + margin)
       return loss.mean()
   ```
3. **VAE Reconstruction Loss:** MSE between input weights and decoded weights

**Total Loss:**
```python
loss = reconstruction_loss + beta_kl * kl_loss + lambda_contrast * contrastive_loss + gamma_task * task_classification_loss
```

**Hyperparameters (from HIT paper and NVAE best practices):**
- Latent dim D: 512
- Transformer layers L: 6
- Transformer heads: 8
- Contrastive margin m: 0.3
- Beta (KL weight): 1.0 (start), anneal to 0.1
- Lambda (contrastive): 0.5
- Gamma (task classification): 0.1
- Batch size: 32
- Learning rate: 1e-4 (AdamW)
- Epochs: 200
- Gradient clipping: 1.0

**Training Loop:**
```python
for epoch in range(200):
    for batch in train_loader:
        # Sample triplet
        anchor, positive, negative = sample_triplet(batch)
        
        # Encode
        mu_a, logvar_a = vae.encode(anchor['weights'], anchor['arch'])
        mu_p, logvar_p = vae.encode(positive['weights'], positive['arch'])
        mu_n, logvar_n = vae.encode(negative['weights'], negative['arch'])
        
        # Reparameterize
        z_a = vae.reparameterize(mu_a, logvar_a)
        z_p = vae.reparameterize(mu_p, logvar_p)
        z_n = vae.reparameterize(mu_n, logvar_n)
        
        # Decode
        recon_a = vae.decode(z_a)
        
        # Losses
        recon_loss = F.mse_loss(recon_a, anchor['weights'])
        kl_loss = -0.5 * torch.sum(1 + logvar_a - mu_a**2 - logvar_a.exp())
        contrast_loss = contrastive_loss(z_a, z_p, z_n)
        
        # Total loss
        loss = recon_loss + beta * kl_loss + lambda_c * contrast_loss
        
        # Backprop
        optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(vae.parameters(), 1.0)
        optimizer.step()
```

**Compute Resources:**
- GPU: 2x NVIDIA V100 (32 GB VRAM total)
- Time: 7 days (200 epochs × 50 min/epoch)
- Storage: 50 GB (checkpoints every 10 epochs)

### 4.3 Phase 4: PoC Validation (Weeks 5-6)

**Goal:** Measure WCSS clustering and ablation tests

**Step 4.1: WCSS Bootstrap Test**
```python
def wcss_bootstrap_test(embeddings, labels, n_resamples=100):
    """
    embeddings: (n_models, latent_dim)
    labels: (n_models,) - task labels
    """
    same_task_wcss = []
    diff_task_wcss = []
    
    for i in range(n_resamples):
        # Resample
        idx = torch.randint(0, len(embeddings), (len(embeddings),))
        emb_sample = embeddings[idx]
        label_sample = labels[idx]
        
        # Compute WCSS for same-task clusters
        for task in torch.unique(label_sample):
            mask = label_sample == task
            cluster_emb = emb_sample[mask]
            centroid = cluster_emb.mean(dim=0)
            wcss = ((cluster_emb - centroid)**2).sum()
            same_task_wcss.append(wcss.item())
        
        # Compute WCSS for random clusters (different-task baseline)
        random_labels = torch.randperm(len(label_sample))
        for task in torch.unique(random_labels):
            mask = random_labels == task
            cluster_emb = emb_sample[mask]
            centroid = cluster_emb.mean(dim=0)
            wcss = ((cluster_emb - centroid)**2).sum()
            diff_task_wcss.append(wcss.item())
    
    # Hypothesis test
    from scipy.stats import ttest_ind, cohen_d
    t_stat, p_value = ttest_ind(same_task_wcss, diff_task_wcss)
    effect_size = cohen_d(same_task_wcss, diff_task_wcss)
    
    return {
        'mean_same_task_wcss': np.mean(same_task_wcss),
        'mean_diff_task_wcss': np.mean(diff_task_wcss),
        'p_value': p_value,
        'cohen_d': effect_size,
        'pass': p_value < 0.01 and effect_size > 0.5
    }
```

**Success Criteria:**
- p < 0.01 (statistically significant)
- Cohen's d > 0.5 (medium effect size)
- Mean WCSS(same-task) < Mean WCSS(different-task)

**Step 4.2: Architecture Token Ablation**
```python
# Remove architecture-type token embeddings from Transformer
class TransformerNoArchToken(nn.Module):
    # Same as TransformerRelational but without self.arch_token
    ...

# Retrain VAE without architecture tokens
vae_ablation = HierarchicalVAE()
vae_ablation.transformer = TransformerNoArchToken()

# Re-evaluate clustering
results_ablation = wcss_bootstrap_test(embeddings_ablation, labels)

# Compare degradation
degradation = (results_ablation['mean_same_task_wcss'] - results_baseline['mean_same_task_wcss']) / results_baseline['mean_same_task_wcss']
```

**Success Criteria:**
- Degradation ≥15pp (validates Transformer learns architecture-aware structure)

**Step 4.3: Reconstruction Task Accuracy (Risk R3 Validation)**
```python
def reconstruction_accuracy(vae, test_loader):
    """Measure if pooling retains task-relevant information"""
    correct = 0
    total = 0
    
    for batch in test_loader:
        weights = batch['weights']
        task_label = batch['task']
        
        # Encode → Decode
        mu, logvar = vae.encode(weights, batch['arch'])
        z = vae.reparameterize(mu, logvar)
        recon = vae.decode(z)
        
        # Predict task from reconstructed weights
        task_pred = classify_task(recon)  # Simple MLP classifier
        correct += (task_pred == task_label).sum()
        total += len(task_label)
    
    return correct / total
```

**Success Criteria:**
- Reconstruction task accuracy >70% (from Risk R3 threshold)

**Compute Resources:**
- GPU: 1x NVIDIA V100
- Time: 2 days (bootstrap resampling + ablation)
- Storage: 5 GB (embeddings cache)

---

## 5. Expected Results

### 5.1 Success Case (Hypothesis PASS)

**Phase 1 CKA Gate:**
- Same-task CKA: median 0.68 (IQR: 0.62-0.74)
- Different-task CKA: median 0.35 (IQR: 0.28-0.42)
- **Interpretation:** Architecture subspaces are metrically compatible

**Phase 4 WCSS Test:**
- Mean WCSS(same-task): 120.5
- Mean WCSS(different-task): 185.3
- p-value: 0.003
- Cohen's d: 0.72
- **Interpretation:** Task constraints create tighter clustering than architecture patterns

**Phase 4 Ablation:**
- Clustering degradation without arch tokens: 18%
- **Interpretation:** Transformer discovers architecture-aware relational structure

**Phase 4 Reconstruction:**
- Task accuracy from pooled representations: 74%
- **Interpretation:** Pooling retains sufficient task-relevant information (Risk R3 mitigated)

### 5.2 Failure Case (Hypothesis FAIL)

**Scenario 1: CKA Gate Failure (Risk R5)**
- Same-task CKA: median 0.42 (below 0.6 threshold)
- **Action:** STOP - architecture subspaces incompatible, cross-architecture bridge infeasible
- **Next Step:** Pivot to homogeneous subsets (CNN-only or ResNet-only)

**Scenario 2: WCSS Test Failure (Core Mechanism)**
- p-value: 0.12 (not significant)
- Cohen's d: 0.18 (small effect)
- **Action:** STOP - task structure doesn't exist at coarse-grained scale
- **Next Step:** Return to Phase 2A dialogue, explore alternative mechanisms

**Scenario 3: Ablation Failure (Simplification Opportunity)**
- Clustering degradation: 3% (architecture tokens redundant)
- **Action:** EXPLORE - mechanism simpler than proposed
- **Next Step:** Simplify to pooling-only (Level 2), skip Transformer (Level 3)

---

## 6. Risk Mitigation

### 6.1 Risk R1: Insufficient Dataset Coverage (MITIGATED by h-e1)

**Status:** MITIGATED - h-e1 validated 72.2% coverage with critical cells passing
- No additional action needed

### 6.2 Risk R2: Noisy Task Labels (MEDIUM)

**Mitigation:**
- Zero-shot transfer validation: Train VAE without task labels, evaluate clustering on held-out models
- Success criterion: Zero-shot task prediction >85% accuracy
- If fails: Pivot to unsupervised contrastive learning (no task labels)

### 6.3 Risk R3: Information Loss in Pooling (MEDIUM)

**Detection:** Reconstruction task accuracy test (Section 4.3 Step 4.3)
**Threshold:** Accuracy <70% indicates critical information loss
**Mitigation:**
- If degradation 30-50%: Replace mean pooling with Set Transformer (learnable pooling)
- If degradation >50%: ABORT - pooling fundamentally incompatible with task preservation

### 6.4 Risk R4: Training Procedure Confound (HIGH)

**Mitigation:**
- Explicit ablation comparing same-task different-procedure vs different-task same-procedure
- Dataset includes hyperparameter metadata (learning rate, batch size, optimizer)
- Test: Does same-augmentation clustering dominate same-task clustering?
- If procedure effect >60%: Add training-procedure as controlled variable (normalize out via conditioning)

### 6.5 Risk R5: Architecture Subspace Incompatibility (CRITICAL - GATED)

**Mitigation:** Phase 1 CKA feasibility gate (Section 4.1)
**Gate Criterion:** Same-task CKA >0.6 AND different-task CKA <0.4
**If Fails:**
- Try nonlinear alignment (RBF kernel CKA)
- Scope reduction: CNN-MLP pairs only (known compatibility from ProbeGen)
- If CKA <0.4: ABORT - no alignment exists

---

## 7. Timeline and Milestones

| Week | Phase | Milestone | Deliverable |
|------|-------|-----------|-------------|
| 1 | Phase 1 | NFN encoder training | Trained encoders for 4 architectures |
| 2 | Phase 1 | CKA feasibility test | **GATE 1:** CKA same-task >0.6 AND diff-task <0.4 |
| 3 | Phase 2-3 | VAE Level 1-2 training | Hierarchical pooling validated |
| 4 | Phase 2-3 | VAE Level 3 training | Full 3-level VAE checkpoint |
| 5 | Phase 4 | WCSS bootstrap test | **GATE 2:** p<0.01, Cohen's d>0.5 |
| 6 | Phase 4 | Ablation + reconstruction | Architecture token contribution ≥15pp |

**Critical Path:** Week 2 (CKA gate) → Week 4 (VAE trained) → Week 5 (WCSS test)  
**Early Stop Opportunities:**
- Week 2: CKA gate fails → Stop before expensive VAE training (saves 4 weeks)
- Week 5: WCSS gate fails → Documented failure, return to Phase 2A

---

## 8. Success Criteria Summary

**Primary (MUST_WORK Gate):**
- Phase 1: CKA same-task >0.6 AND different-task <0.4
- Phase 4: Mean WCSS(same-task) < Mean WCSS(different-task) with p<0.01 and Cohen's d>0.5

**Secondary (Validation):**
- Ablation: Removing architecture tokens degrades clustering ≥15pp
- Reconstruction: Task accuracy from pooled representations >70%

**Tertiary (Risk Mitigation):**
- Zero-shot transfer: >85% accuracy on unlabeled models (validates task label quality)
- Training procedure ablation: Procedure effect <60% (disentangles task vs optimization)

---

## 9. Code Repository Structure

```
h-m-integrated/
├── data/
│   ├── download_modelzoo.py          # Download script for Zenodo datasets
│   ├── dataset.py                     # ModelZooDataset wrapper
│   └── preprocessing.py               # Architecture-task pairing logic
├── models/
│   ├── nfn_encoder.py                 # NFN/UNF encoders (Level 1)
│   ├── pooling.py                     # Hierarchical pooling (Level 2)
│   ├── transformer.py                 # Transformer relational (Level 3)
│   ├── hierarchical_vae.py            # Full VAE architecture
│   └── baselines.py                   # ArchConditionedMLP, NFN-only
├── training/
│   ├── phase1_cka_gate.py             # CKA feasibility test
│   ├── phase23_vae_train.py           # VAE training loop
│   └── phase4_validation.py           # WCSS bootstrap + ablation
├── evaluation/
│   ├── cka.py                         # CKA computation
│   ├── wcss.py                        # WCSS bootstrap test
│   └── metrics.py                     # Reconstruction accuracy, effect sizes
└── notebooks/
    ├── 01_data_exploration.ipynb      # Dataset statistics, coverage audit
    ├── 02_cka_feasibility.ipynb       # Phase 1 results visualization
    └── 03_clustering_analysis.ipynb   # Phase 4 WCSS results + UMAP plots
```

---

## 10. References (Implementation Sources)

**Hierarchical VAE Implementations:**
- NVAE (NVlabs): https://github.com/NVlabs/NVAE - Hierarchical architecture, residual cells, group-wise latent variables
- HIT (timxzz): https://github.com/timxzz/HIT - Beta-VAE rate-distortion tradeoff, multi-layer latent split
- HCSC (hirl-team): https://github.com/hirl-team/HCSC - Hierarchical contrastive selective coding, prototype-based learning

**CKA Computation:**
- CKA.pytorch (numpee): https://github.com/numpee/CKA.pytorch - Minibatch CKA, GPU-accelerated HSIC
- pytorch-cka (suhyeon): https://pypi.org/project/pytorch-cka/ - Layer-wise similarity, heatmap visualization
- centered-kernel-alignment (RistoAle97): https://github.com/RistoAle97/centered-kernel-alignment - Unbiased HSIC estimator

**Contrastive Learning:**
- DALLE2-pytorch (lucidrains): https://github.com/lucidrains/DALLE2-pytorch - Triplet loss, InfoNCE, CLIP-style contrastive
- ContrastiveVI (scvi-tools): https://github.com/scverse/scvi-tools - Contrastive VAE with background/salient latent split

**ModelZooDataset:**
- ModelZooDataset (ModelZoos): https://github.com/ModelZoos/ModelZooDataset - Dataset class, vectorized weights, architecture metadata
- Zenodo repositories: https://doi.org/10.5281/zenodo.6620868 - Preprocessed PyTorch files

---

## 11. Compute Budget

**Phase 1 (CKA Gate):**
- GPU hours: 48 (1x V100 × 2 days)
- Storage: 10 GB
- Estimated cost: $50 (AWS p3.2xlarge)

**Phase 2-3 (VAE Training):**
- GPU hours: 336 (2x V100 × 7 days)
- Storage: 50 GB
- Estimated cost: $700 (AWS p3.8xlarge)

**Phase 4 (Validation):**
- GPU hours: 48 (1x V100 × 2 days)
- Storage: 5 GB
- Estimated cost: $50 (AWS p3.2xlarge)

**Total Budget:**
- GPU hours: 432
- Storage: 65 GB
- Estimated cost: $800 (11 days of GPU time)

---

## 12. Deliverables

1. **Phase 1 Report:** CKA feasibility results, architecture compatibility matrix
2. **Phase 2-3 Checkpoint:** Trained hierarchical VAE (50 GB file)
3. **Phase 4 Validation Report:** WCSS bootstrap results, ablation analysis, reconstruction accuracy
4. **Code Repository:** Fully documented implementation with README, requirements.txt
5. **Visualization Notebook:** UMAP plots, CKA heatmaps, clustering comparison

---

**END OF EXPERIMENT BRIEF**
