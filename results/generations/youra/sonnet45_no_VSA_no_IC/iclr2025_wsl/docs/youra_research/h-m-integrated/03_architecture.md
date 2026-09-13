# Architecture Design: h-m-integrated
## Hierarchical VAE for Cross-Architecture Model Zoo Analysis

**Hypothesis ID:** h-m-integrated  
**Type:** MECHANISM  
**Date:** 2026-08-20  
**Complexity:** HIGH (Score: 4.0)

**Applied Patterns:** Standard PyTorch VAE structure, modular encoder design, phased training pipeline  
**Codebase:** Green-field implementation extending h-e1 data structures

---

## 1. System Overview

3-level VAE encoding heterogeneous neural network weights into shared latent space:
- **Level 1:** Architecture-specific encoders (NFN/UNF) convert variable-length weights to per-neuron embeddings
- **Level 2:** Hierarchical pooling aggregates neurons into fixed-length layer summaries
- **Level 3:** Transformer models cross-layer relations, outputs VAE latent (mu, logvar)

**Data Flow:** ModelZoo weights (10K-200K params) → Level 1 (batch, N, 512) → Level 2 (batch, L, 512) → Level 3 (batch, 512) → Decoder → Reconstructed weights

---

## 2. Module Interfaces

### DataModule (`src/data/loader.py`)

**Dependencies:** None

```python
class ModelZooDataset(torch.utils.data.Dataset):
    def __init__(self, pt_file: str, index_dict: str, split: str): ...
    def __getitem__(self, idx: int) -> dict: ...  # {weights, architecture, task, metadata}
    def __len__(self) -> int: ...

def create_triplet_sampler(dataset: ModelZooDataset, batch_size: int) -> DataLoader: ...
```

### Level1Encoders (`src/models/encoders.py`)

**Dependencies:** None

```python
class NFNEncoder(nn.Module):
    def __init__(self, weight_dim: int, hidden_dim: int = 256, output_dim: int = 512): ...
    def forward(self, weights: Tensor) -> Tensor: ...  # (batch, num_neurons, 512)

class EncoderRegistry(nn.Module):
    def __init__(self): ...
    def register_encoder(self, arch_name: str, encoder: nn.Module): ...
    def encode(self, weights: Tensor, arch_name: str) -> Tensor: ...
```

### Level2Pooling (`src/models/pooling.py`)

**Dependencies:** Level1Encoders

```python
class HierarchicalPooling(nn.Module):
    def __init__(self, input_dim: int = 512, output_dim: int = 512): ...
    def forward(self, neuron_embeddings: Tensor) -> Tensor: ...  # (batch, num_layers, 512)
```

### Level3Transformer (`src/models/transformer.py`)

**Dependencies:** Level2Pooling

```python
class TransformerRelational(nn.Module):
    def __init__(self, latent_dim: int = 512, num_heads: int = 8, num_layers: int = 6): ...
    def forward(self, layer_summaries: Tensor) -> Tuple[Tensor, Tensor]: ...  # (mu, logvar)
```

### HierarchicalVAE (`src/models/vae.py`)

**Dependencies:** Level1Encoders, Level2Pooling, Level3Transformer

```python
class HierarchicalVAE(nn.Module):
    def __init__(self, encoder_registry: EncoderRegistry, pooling: HierarchicalPooling, 
                 transformer: TransformerRelational, decoder_dims: List[int]): ...
    def encode(self, weights: Tensor, arch_type: str) -> Tuple[Tensor, Tensor]: ...
    def reparameterize(self, mu: Tensor, logvar: Tensor) -> Tensor: ...
    def decode(self, z: Tensor) -> Tensor: ...
    def forward(self, weights: Tensor, arch_type: str) -> dict: ...  # {z, mu, logvar, recon}
```

### TrainingLoop (`src/training/train.py`)

**Dependencies:** HierarchicalVAE, LossModule

```python
class MultiObjectiveLoss(nn.Module):
    def __init__(self, beta_kl: float = 1.0, lambda_contrast: float = 0.5, 
                 gamma_task: float = 0.1): ...
    def forward(self, recon: Tensor, target: Tensor, mu: Tensor, logvar: Tensor, 
                z_anchor: Tensor, z_pos: Tensor, z_neg: Tensor, 
                task_logits: Tensor, task_labels: Tensor) -> dict: ...

def train_epoch(model: HierarchicalVAE, loader: DataLoader, 
                optimizer: Optimizer, loss_fn: MultiObjectiveLoss, 
                epoch: int) -> dict: ...
```

### Phase1CKA (`src/evaluation/cka.py`)

**Dependencies:** Level1Encoders

```python
def linear_cka(X: Tensor, Y: Tensor) -> float: ...
def compute_pairwise_cka(embeddings: Tensor, labels: Tensor) -> Tuple[float, float]: ...  # same_task, diff_task
def run_phase1_gate(encoder_registry: EncoderRegistry, dataset: ModelZooDataset, 
                    n_pairs: int = 200) -> dict: ...  # {pass: bool, same_task_cka, diff_task_cka}
```

### Phase4Evaluation (`src/evaluation/wcss.py`)

**Dependencies:** HierarchicalVAE

```python
def compute_wcss(embeddings: Tensor, labels: Tensor) -> float: ...
def bootstrap_wcss_test(embeddings: Tensor, labels: Tensor, n_resamples: int = 100) -> dict: ...
def ablation_arch_token(vae: HierarchicalVAE, test_loader: DataLoader) -> float: ...  # degradation %
def reconstruction_task_accuracy(vae: HierarchicalVAE, test_loader: DataLoader) -> float: ...
```

### Baselines (`src/models/baselines.py`)

**Dependencies:** None

```python
class ArchConditionedMLP(nn.Module):
    def __init__(self, weight_dim: int, arch_vocab_size: int = 4, 
                 hidden_dim: int = 512, latent_dim: int = 512): ...
    def forward(self, weights: Tensor, arch_id: int) -> Tensor: ...
```

---

## 3. File Organization

```
h-m-integrated/
├── config.yaml                    # Hyperparameters, paths
├── main.py                        # CLI entry point (phase selector)
├── requirements.txt               # torch>=2.0, scipy, tqdm
├── src/
│   ├── data/
│   │   ├── loader.py             # ModelZooDataset, triplet sampler
│   │   └── download.py           # Zenodo/SANE download scripts
│   ├── models/
│   │   ├── encoders.py           # NFNEncoder, EncoderRegistry
│   │   ├── pooling.py            # HierarchicalPooling
│   │   ├── transformer.py        # TransformerRelational
│   │   ├── vae.py                # HierarchicalVAE
│   │   └── baselines.py          # ArchConditionedMLP
│   ├── training/
│   │   ├── train.py              # train_epoch, MultiObjectiveLoss
│   │   ├── phase1_cka_gate.py    # CKA feasibility test
│   │   └── phase23_vae.py        # Full VAE training script
│   └── evaluation/
│       ├── cka.py                # linear_cka, pairwise computation
│       ├── wcss.py               # WCSS bootstrap, ablations
│       └── visualize.py          # UMAP, CKA heatmaps
├── checkpoints/                   # Model checkpoints (2.5 GB each)
├── outputs/
│   ├── phase1/                   # CKA gate results
│   ├── phase23/                  # Training logs, loss curves
│   └── phase4/                   # WCSS results, ablation plots
└── notebooks/
    ├── 01_data_exploration.ipynb
    ├── 02_cka_results.ipynb
    └── 03_clustering_analysis.ipynb
```

---

## 4. Data Pipeline Architecture

### 4.1 Download and Cache (`src/data/download.py`)

```python
def download_modelzoo(cache_dir: Path) -> List[Path]: ...
    # Downloads: dataset_cifar_small_hyp_rand.pt (1.8 GB)
    #            dataset_cifar_large_hyp_rand.pt (5.5 GB)
    #            index_dict_small.json, index_dict_large.json
    # From: https://doi.org/10.5281/zenodo.6620868

def download_sane_resnets(cache_dir: Path, tasks: List[str]) -> List[Path]: ...
    # Downloads: tune_zoo_cifar10_resnet18_kaiming_uniform.tar (ResNet-18)
    #            tune_zoo_cifar100_resnet18_kaiming_uniform.tar
    # From: https://ai.unisg.ch/files/tar_files/
```

### 4.2 Dataset Loader

**Schema:** Each sample contains:
```python
{
    'weights': Tensor,           # (weight_dim,) - vectorized weights
    'architecture': str,         # 'cnn_small', 'cnn_large', 'resnet18', 'resnet34'
    'task': str,                 # 'cifar10', 'cifar100', etc.
    'metadata': dict             # {learning_rate, batch_size, optimizer, num_epochs}
}
```

**Normalization:** Per-architecture z-score normalization (mean=0, std=1) applied in `__getitem__`.

### 4.3 Triplet Sampler

**Strategy:**
- Anchor: random sample from batch
- Positive: same-task, different-architecture (find via task label match)
- Negative: different-task (any architecture)

**Implementation:** Custom collate function for DataLoader batching triplets.

---

## 5. Training Architecture

### 5.1 Multi-Objective Loss

```
total_loss = recon_loss + beta_kl * kl_loss + lambda_contrast * triplet_loss + gamma_task * task_ce_loss
```

**Component Losses:**
1. **Reconstruction:** `MSE(decoded_weights, input_weights)`
2. **KL Divergence:** `-0.5 * sum(1 + logvar - mu^2 - exp(logvar))`
3. **Triplet Contrastive:** `max(0, ||z_anchor - z_pos|| - ||z_anchor - z_neg|| + margin)`
4. **Task Classification:** `CrossEntropyLoss(task_logits, task_labels)`

**Loss Weighting Schedule:**
- `beta_kl`: 1.0 → 0.1 (linear anneal over 200 epochs, prevent posterior collapse)
- `lambda_contrast`: 0.5 (fixed)
- `gamma_task`: 0.1 (fixed)

### 5.2 Training Configuration

```yaml
optimizer:
  type: AdamW
  lr: 1e-4
  weight_decay: 1e-5

training:
  epochs: 200
  batch_size: 32
  gradient_clip: 1.0
  checkpoint_freq: 10

data:
  train_split: 0.70  # 1,484 models
  val_split: 0.15    # 318 models
  test_split: 0.15   # 318 models
```

### 5.3 Training Loop Pseudocode

```python
for epoch in range(200):
    for batch in train_loader:
        anchor, positive, negative = sample_triplet(batch)
        
        # Encode
        z_a, mu_a, logvar_a = model(anchor['weights'], anchor['arch'])
        z_p, mu_p, logvar_p = model(positive['weights'], positive['arch'])
        z_n, mu_n, logvar_n = model(negative['weights'], negative['arch'])
        
        # Decode anchor
        recon_a = model.decode(z_a)
        
        # Compute losses
        losses = loss_fn(recon_a, anchor['weights'], mu_a, logvar_a, 
                        z_a, z_p, z_n, task_logits, anchor['task'])
        
        # Backprop with gradient clipping
        optimizer.zero_grad()
        losses['total'].backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
```

---

## 6. Evaluation Architecture

### 6.1 Phase 1: CKA Feasibility Gate

**Purpose:** Validate architecture subspaces are metrically compatible before expensive VAE training.

**Process:**
1. Sample 200 model pairs (100 same-task, 100 different-task)
2. Encode using Level 1 encoders only (skip pooling/transformer)
3. Compute pairwise linear CKA: `HSIC(X, Y) / sqrt(HSIC(X, X) * HSIC(Y, Y))`
4. **Gate Criterion:** `median(same_task_cka) > 0.6 AND median(diff_task_cka) < 0.4`

**Output:** `{pass: bool, same_task_cka: float, diff_task_cka: float, cka_matrix: ndarray}`

**Early Stop:** If gate fails, STOP before Phase 2-3 (saves $700 GPU cost).

### 6.2 Phase 4: WCSS Bootstrap Test

**Purpose:** Statistical test that same-task clusters are tighter than different-task.

**Process:**
1. Extract latent embeddings from test set (318 models)
2. Bootstrap resample: 100 iterations
3. For each resample:
   - Compute WCSS for same-task clusters
   - Compute WCSS for random clusters (different-task baseline)
4. T-test + Cohen's d effect size

**Gate Criterion:** `p < 0.01 AND cohen_d > 0.5`

**Output:** `{mean_same_task_wcss: float, mean_diff_task_wcss: float, p_value: float, cohen_d: float, pass: bool}`

### 6.3 Architecture Token Ablation

**Purpose:** Validate Transformer learns architecture-aware structure.

**Process:**
1. Retrain VAE with architecture token removed from Transformer
2. Re-evaluate clustering (WCSS test)
3. Measure degradation: `(wcss_ablation - wcss_baseline) / wcss_baseline * 100`

**Success Criterion:** `degradation >= 15%`

### 6.4 Reconstruction Task Accuracy

**Purpose:** Validate pooling retains task-relevant information (Risk R3 mitigation).

**Process:**
1. Train simple MLP classifier on reconstructed weights
2. Predict task label from decoder output
3. Measure accuracy on held-out test set

**Success Criterion:** `accuracy > 70%`

---

## 7. Baseline Architectures

### Baseline 1: Architecture-Conditioned MLP

**Purpose:** Test whether architecture labels alone predict clustering (null hypothesis).

**Architecture:**
- Architecture embedding (4 architectures → 64-dim)
- 3-layer MLP encoder: `[weight_dim + 64] → [512] → [512] → [512]`
- Standard VAE decoder

**Training:** Reconstruction loss only (no contrastive, no task labels).

**Evaluation:** Compare WCSS to hierarchical VAE (should be higher if task structure exists).

### Baseline 2: NFN-only (Single Architecture)

**Purpose:** Validate NFN works within-architecture before cross-architecture extension.

**Architecture:** NFN encoder + standard VAE (CNN-small models only).

**Training:** Standard VAE loss (reconstruction + KL).

**Evaluation:** Reconstruction accuracy on held-out CNN-small models (threshold: >70%).

### Baseline 3: CKA Direct Comparison

**Purpose:** Measure upper bound of CKA similarity without VAE compression.

**Method:** Compute CKA directly on raw vectorized weights (no learned transformation).

**Evaluation:** Raw CKA scores establish feasibility threshold for Phase 1 gate.

---

## 8. Checkpoint Strategy

**Frequency:** Every 10 epochs (20 checkpoints total).

**Checkpoint Contents:**
```python
{
    'epoch': int,
    'model_state_dict': dict,
    'optimizer_state_dict': dict,
    'loss_history': dict,
    'val_metrics': dict,
    'config': dict
}
```

**Storage:** 2.5 GB per checkpoint (50 GB total).

**Resume Logic:** Detect latest checkpoint in `checkpoints/`, load state, resume from epoch+1.

---

## 9. Multi-GPU Strategy

**Data Parallelism:** `torch.nn.DataParallel` for Phase 2-3 training (2x V100).

**Batch Size Scaling:** 32 per GPU (effective batch = 64).

**Gradient Accumulation:** Not needed (batch size sufficient for stable training).

**Distributed Data Parallel (DDP):** Not implemented (overkill for 2 GPUs).

---

## 10. Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Data Pipeline | Download ModelZoo, implement triplet sampler, data splits | 9 | Module(3) + Deps(2) + Algo(2) + Integ(2) |
| A-2 | Level 1 Encoders | Implement NFNEncoder, EncoderRegistry, per-arch normalization | 12 | Module(4) + Deps(2) + Algo(4) + Integ(2) |
| A-3 | Level 2 Pooling | Hierarchical pooling with layer-wise aggregation | 8 | Module(2) + Deps(2) + Algo(2) + Integ(2) |
| A-4 | Level 3 Transformer | 6-layer Transformer with CLS token, architecture token | 10 | Module(3) + Deps(2) + Algo(3) + Integ(2) |
| A-5 | HierarchicalVAE | Integrate 3 levels, decoder, reparameterization | 11 | Module(3) + Deps(3) + Algo(2) + Integ(3) |
| A-6 | Multi-Objective Loss | Implement 4 loss components, beta annealing | 9 | Module(2) + Deps(2) + Algo(3) + Integ(2) |
| A-7 | Phase 1 CKA Gate | CKA computation, pairwise matrix, gate logic | 10 | Module(2) + Deps(2) + Algo(4) + Integ(2) |
| A-8 | Phase 2-3 Training | Training loop, gradient clipping, checkpoint autosave | 13 | Module(3) + Deps(3) + Algo(3) + Integ(4) |
| A-9 | Phase 4 WCSS Test | Bootstrap resampling, statistical tests, ablations | 11 | Module(3) + Deps(2) + Algo(4) + Integ(2) |
| A-10 | Baselines | Implement 3 baseline models for comparison | 8 | Module(3) + Deps(1) + Algo(2) + Integ(2) |
| A-11 | Visualization | UMAP plots, CKA heatmaps, training curves | 7 | Module(2) + Deps(1) + Algo(2) + Integ(2) |
| A-12 | CLI and Config | Main entry point, YAML config, phase selector | 6 | Module(2) + Deps(1) + Algo(1) + Integ(2) |

**Distribution:**
- VeryHigh (18-20): []
- High (14-17): [A-8]
- Medium (9-13): [A-1, A-2, A-4, A-5, A-6, A-7, A-9]
- Low (4-8): [A-3, A-10, A-11, A-12]

**Critical Path:** A-1 → A-2 → A-7 (Phase 1 gate) → A-3 → A-4 → A-5 → A-6 → A-8 (Phase 2-3) → A-9 (Phase 4)

**Parallel Opportunities:** A-10, A-11, A-12 can be developed concurrently with A-3, A-4.

---

## 11. Risk Architecture

### Risk R1: Insufficient Coverage (MITIGATED by h-e1)
**Status:** VALIDATED - h-e1 confirmed 72.2% coverage.  
**Architecture Impact:** None (no additional handling needed).

### Risk R2: Noisy Task Labels
**Detection:** Zero-shot transfer test (train without labels, measure clustering).  
**Mitigation in Code:** Add `--no-task-labels` flag to training script, skip task classification loss.  
**Abort Criterion:** Zero-shot accuracy <85%.

### Risk R3: Information Loss in Pooling
**Detection:** `reconstruction_task_accuracy()` in Phase 4.  
**Mitigation in Code:** Swap `HierarchicalPooling` with `SetTransformerPooling` (learnable aggregation).  
**Abort Criterion:** Accuracy <70%.

### Risk R4: Training Procedure Confound
**Detection:** Explicit ablation comparing same-task different-procedure vs different-task same-procedure.  
**Mitigation in Code:** Add hyperparameter conditioning to model (extend metadata dict).  
**Abort Criterion:** Procedure effect >60%.

### Risk R5: Architecture Subspace Incompatibility (GATED)
**Detection:** Phase 1 CKA gate.  
**Mitigation in Code:** Implement RBF kernel CKA as fallback, scope reduction to CNN-only.  
**Abort Criterion:** CKA <0.4 after all mitigation attempts.

---

## 12. Compute Resource Allocation

| Phase | Duration | GPUs | Storage | Cost |
|-------|----------|------|---------|------|
| Phase 1 (CKA Gate) | 2 days | 1x V100 | 10 GB | $50 |
| Phase 2-3 (VAE Training) | 7 days | 2x V100 | 50 GB | $700 |
| Phase 4 (Validation) | 2 days | 1x V100 | 5 GB | $50 |
| **Total** | **11 days** | - | **65 GB** | **$800** |

**Memory Budget per Model Component:**
- Level 1 Encoders: 4 × 100 MB = 400 MB
- Level 2 Pooling: 50 MB
- Level 3 Transformer: 300 MB (6 layers × 8 heads)
- Decoder: 200 MB
- **Total Model:** ~1 GB

**Batch Size VRAM:**
- Batch=32, weight_dim=100K, latent_dim=512
- Forward pass: ~6 GB
- Backward pass: ~10 GB
- **Total per GPU:** 16 GB (fits 1x V100)

---

## 13. Validation Gates

### Gate 1: Phase 1 CKA Feasibility (Week 2)
**Criterion:** `same_task_cka > 0.6 AND diff_task_cka < 0.4`  
**Action on Fail:** STOP before Phase 2-3 (saves $700).  
**Fallback:** Try RBF kernel CKA, scope to CNN-only subset.

### Gate 2: Phase 4 WCSS Test (Week 5)
**Criterion:** `p < 0.01 AND cohen_d > 0.5`  
**Action on Fail:** Document failure, return to Phase 2A (alternative mechanisms).  
**No Fallback:** This is the core hypothesis test.

### Soft Gate: Reconstruction Task Accuracy (Week 6)
**Criterion:** `accuracy > 70%`  
**Action on Fail:** Replace mean pooling with Set Transformer.  
**Abort if:** `accuracy < 50%` (pooling fundamentally incompatible).

---

## 14. Architecture Decision Log

| Decision | Rationale | Alternative Considered |
|----------|-----------|------------------------|
| 3-level hierarchy | Matches NVAE best practices, separates concerns | 2-level (encoder+decoder only) - insufficient expressiveness |
| NFN for Level 1 | Permutation invariance required for neural network weights | Graph Neural Networks - more complex, no reference code |
| 6-layer Transformer | HIT paper recommendation for relational modeling | 2-layer - may lack capacity; 12-layer - overkill for 512-dim |
| Triplet loss | Explicit same-task/different-task supervision | InfoNCE - requires large negative batches (GPU memory issue) |
| Beta annealing 1.0→0.1 | Prevents posterior collapse (VAE best practice) | Fixed beta - risks collapse or over-regularization |
| Mean pooling | Simplest aggregation, validates hypothesis minimally | Set Transformer - adds complexity, defer to Risk R3 mitigation |
| Data Parallelism | Simple, works for 2 GPUs | DistributedDataParallel - overkill, more complex setup |

---

## 15. External Dependencies

| Dependency | Version | Purpose | Source |
|------------|---------|---------|--------|
| PyTorch | >=2.0 | Core DL framework | Standard package |
| NumPy | >=1.24 | Array operations | Standard package |
| SciPy | >=1.11 | Statistical tests (t-test, cohen_d) | Standard package |
| tqdm | >=4.65 | Progress bars | Standard package |
| tensorboard | >=2.13 | Training logs, loss curves | Standard package |
| PyYAML | >=6.0 | Config file parsing | Standard package |

**External Code References (for study, not direct import):**
- NFN: https://github.com/AllanYangZhou/nfn (DeepSets pattern for permutation invariance)
- CKA: https://github.com/numpee/CKA.pytorch (HSIC computation)
- Contrastive: https://github.com/lucidrains/DALLE2-pytorch (Triplet loss implementation)

**Note:** No external repos are directly imported. Reference implementations guide our custom code.

---

## 16. Testing Strategy

**Unit Tests:** Not in scope for PoC (research code, rapid iteration).

**Integration Tests:**
- Phase 1 CKA gate outputs expected format
- Phase 4 WCSS test completes without NaN
- Checkpoint save/load preserves training state

**Validation Tests:**
- Gradient flow check (detect NaN/Inf in backward pass)
- Loss component magnitudes (ensure no single loss dominates)
- Architecture token ablation (verify degradation threshold)

**Smoke Tests:**
- `main.py --phase 1 --dry-run` (validate config loading)
- Single batch forward/backward pass (detect shape mismatches)

---

**END OF ARCHITECTURE DOCUMENT**

**Next Phase:** Phase 4 (Coder) will implement modules following these interfaces.

**Document Metadata:**
- Total Modules: 12
- Total Epic Tasks: 12
- Estimated LOC: 2,500
- Timeline: 6 weeks (11 GPU days)
- Critical Path Length: 9 tasks
