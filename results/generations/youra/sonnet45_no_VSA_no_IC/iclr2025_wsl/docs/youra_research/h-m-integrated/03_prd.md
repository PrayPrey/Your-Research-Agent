# Product Requirements Document: h-m-integrated
## Hierarchical VAE for Cross-Architecture Model Zoo Analysis

**Hypothesis ID:** h-m-integrated  
**Type:** MECHANISM  
**Date:** 2026-08-20  
**Prerequisite:** h-e1 (VALIDATED - 72.2% coverage)

---

## 1. Executive Summary

### 1.1 Purpose
Implement a 3-level hierarchical Variational Autoencoder (VAE) to validate that task constraints create architecture-invariant weight patterns in heterogeneous model zoos. The system encodes neural network weights from different architectures (CNN, ResNet) trained on different tasks (CIFAR-10, ImageNet, etc.) into a shared latent space and measures task-based clustering via CKA similarity and WCSS metrics.

### 1.2 Success Criteria (MUST_WORK Gate)
- **Phase 1 CKA Gate:** Same-task CKA >0.6 AND different-task CKA <0.4
- **Phase 4 WCSS Gate:** Mean WCSS(same-task) < Mean WCSS(different-task) with p<0.01 and Cohen's d>0.5
- **Reconstruction Accuracy:** Task prediction from pooled representations >70%
- **Ablation Test:** Architecture token removal degrades clustering ≥15pp

### 1.3 Core Components
1. **Level 1:** Architecture-specific encoders (NFN for CNNs, UNF for ResNets)
2. **Level 2:** Hierarchical pooling (layer-wise aggregation)
3. **Level 3:** Transformer relational modeling (6-layer with CLS token)
4. **Training:** Multi-objective loss (reconstruction + KL + contrastive + task classification)
5. **Evaluation:** CKA feasibility gate, WCSS bootstrap test, ablation studies

---

## 2. Product Overview

### 2.1 Problem Statement
Current meta-learning approaches assume homogeneous model families (all CNNs or all Transformers). Heterogeneous model zoos contain diverse architectures trained on different tasks. **Research Question:** Do task constraints dominate architecture-specific implementation details at coarse-grained weight space scale?

### 2.2 Proposed Solution
A hierarchical VAE with three levels:
1. **Architecture-specific encoding** via Neural Functional Networks (NFN) for permutation invariance
2. **Hierarchical pooling** to create fixed-length layer summaries
3. **Transformer sequence modeling** to discover cross-architecture relational structure

**Key Innovation:** Multi-objective training with contrastive supervision forces same-task models to cluster tightly regardless of architecture.

### 2.3 Target Users
- ML researchers studying model zoo organization
- Meta-learning practitioners designing cross-architecture transfer methods
- Neural architecture search (NAS) teams analyzing architecture-task relationships

---

## 3. Functional Requirements

### 3.1 Data Pipeline (Priority: CRITICAL)
**FR-1.1: Dataset Download and Caching**
- Download ModelZooDataset from Zenodo (https://doi.org/10.5281/zenodo.6620868)
- Cache files: `dataset_cifar_small_hyp_rand.pt` (1.8 GB), `dataset_cifar_large_hyp_rand.pt` (5.5 GB)
- Load index dictionaries: `index_dict_small.json`, `index_dict_large.json`
- Download ResNet-18 models from SANE (https://ai.unisg.ch/files/tar_files/)

**FR-1.2: Architecture-Task Pairing**
- Generate same-task pairs: identical task labels, different architectures
- Generate different-task pairs: different task labels, same architecture
- Balance pair counts: 100 same-task, 100 different-task for Phase 1

**FR-1.3: Data Splits**
- Phase 1 (CKA gate): 200 model pairs
- Phase 2-3 (VAE training): 70% train (1,484 models), 15% val (318), 15% test (318)
- Maintain architecture-task stratification across splits

**FR-1.4: Normalization**
- Per-architecture z-score normalization (mean=0, std=1)
- Preserve architecture-specific scale information

### 3.2 Model Architecture (Priority: CRITICAL)

**FR-2.1: Level 1 - Architecture-Specific Encoders**
- NFN encoder for CNN-small, CNN-large (permutation-equivariant)
- UNF encoder for ResNet-18, ResNet-34 (graph-structured)
- Output: Per-neuron embeddings (batch, num_neurons, dim=512)

**FR-2.2: Level 2 - Hierarchical Pooling**
- Layer-wise mean pooling over neuron embeddings
- MLP projection to fixed-length representation
- Output: Layer summaries (batch, num_layers, dim=512)

**FR-2.3: Level 3 - Transformer Relational Modeling**
- 6-layer Transformer encoder with 8 attention heads
- Architecture-type token (learnable parameter)
- CLS token for final latent representation
- Output: VAE mu/logvar (batch, latent_dim=512)

**FR-2.4: Decoder**
- Shared MLP decoder across architectures
- Maps latent z to reconstructed weight vector
- Output: (batch, weight_dim)

**FR-2.5: Baselines**
- **Baseline 1:** Architecture-Conditioned MLP (no task labels)
- **Baseline 2:** NFN-only single architecture (CNN-small only)
- **Baseline 3:** CKA Direct Comparison (no learned model)

### 3.3 Training Pipeline (Priority: CRITICAL)

**FR-3.1: Multi-Objective Loss**
- **Reconstruction Loss:** MSE between input weights and decoded weights
- **KL Divergence:** Standard VAE latent regularization with beta annealing (1.0 → 0.1)
- **Contrastive Triplet Loss:** Margin-based loss (margin=0.3) for same-task (positive) vs different-task (negative) pairs
- **Task Classification Loss:** Cross-entropy for coarse task labels

**FR-3.2: Loss Weighting**
```
total_loss = recon_loss + beta_kl * kl_loss + lambda_contrast * contrast_loss + gamma_task * task_loss
```
- beta_kl: 1.0 (start) → 0.1 (end, linear anneal)
- lambda_contrast: 0.5
- gamma_task: 0.1

**FR-3.3: Training Configuration**
- Optimizer: AdamW
- Learning rate: 1e-4
- Batch size: 32
- Epochs: 200
- Gradient clipping: 1.0
- Checkpoint frequency: Every 10 epochs

**FR-3.4: Triplet Sampling Strategy**
- Anchor: random model from batch
- Positive: same-task different-architecture model
- Negative: different-task model (can be same or different architecture)

### 3.4 Evaluation Pipeline (Priority: CRITICAL)

**FR-4.1: Phase 1 - CKA Feasibility Gate**
- Encode 200 model pairs using NFN encoders
- Compute linear CKA similarity (centered Gram matrices)
- Calculate median CKA for same-task pairs (threshold: >0.6)
- Calculate median CKA for different-task pairs (threshold: <0.4)
- **GATE:** If fails, STOP before Phase 2-3 (saves $700 GPU cost)

**FR-4.2: Phase 4 - WCSS Bootstrap Test**
- Extract latent embeddings from test set (318 models)
- Bootstrap resample: 100 iterations
- Compute WCSS for same-task clusters vs random clusters
- Statistical test: t-test + Cohen's d effect size
- **GATE:** Require p<0.01 AND Cohen's d>0.5

**FR-4.3: Architecture Token Ablation**
- Retrain VAE with Transformer architecture token removed
- Measure clustering degradation (WCSS difference)
- Threshold: ≥15pp degradation validates token utility

**FR-4.4: Reconstruction Task Accuracy**
- Train simple MLP classifier on reconstructed weights
- Predict task label from decoder output
- Threshold: >70% accuracy (validates pooling preserves task information)

### 3.5 Visualization and Reporting (Priority: HIGH)

**FR-5.1: CKA Heatmap**
- Pairwise CKA matrix for architecture pairs
- Color-coded by same-task vs different-task

**FR-5.2: UMAP Latent Space Visualization**
- 2D projection of latent embeddings
- Color by task label, shape by architecture

**FR-5.3: WCSS Comparison Plot**
- Box plots for same-task WCSS vs different-task WCSS
- Annotate p-value and Cohen's d

**FR-5.4: Training Curves**
- Loss curves (4 components + total)
- Validation reconstruction accuracy over epochs

---

## 4. Non-Functional Requirements

### 4.1 Performance
**NFR-1.1:** Phase 1 CKA gate completes in ≤2 days on 1x V100 GPU  
**NFR-1.2:** Phase 2-3 VAE training completes in ≤7 days on 2x V100 GPUs  
**NFR-1.3:** Checkpoint loading time <30 seconds  

### 4.2 Scalability
**NFR-2.1:** Support up to 4 architecture families (extensible to 8)  
**NFR-2.2:** Handle variable-length weight vectors (10K-200K neurons)  
**NFR-2.3:** Batch size auto-scaling based on available VRAM  

### 4.3 Reliability
**NFR-3.1:** Checkpoint autosave every 10 epochs (prevent training loss)  
**NFR-3.2:** Gradient NaN detection with early stopping  
**NFR-3.3:** Data corruption checks (hash verification for downloaded files)  

### 4.4 Usability
**NFR-4.1:** Single-command training script (`python train.py --config config.yaml`)  
**NFR-4.2:** Automatic GPU device detection and multi-GPU support  
**NFR-4.3:** Progress bars for all long-running operations (tqdm)  

### 4.5 Maintainability
**NFR-5.1:** Modular code structure (separate files per level)  
**NFR-5.2:** Type hints for all function signatures  
**NFR-5.3:** Docstrings for all public functions (Google style)  

---

## 5. Data Requirements

### 5.1 Input Data
**Dataset:** ModelZooDataset + SANE  
**Size:** 2,120 models (from h-e1 validation)  
**Architectures:** CNN-small, CNN-large, ResNet-18, ResNet-34  
**Tasks:** CIFAR-10, CIFAR-100, TinyImageNet, MNIST, FashionMNIST, SVHN, USPS, STL10, EuroSAT  

### 5.2 Data Schema
```python
{
    'weights': Tensor,          # (weight_dim,) - vectorized weights
    'architecture': str,        # 'cnn_small', 'cnn_large', 'resnet18', 'resnet34'
    'task': str,                # 'cifar10', 'cifar100', etc.
    'metadata': {
        'learning_rate': float,
        'batch_size': int,
        'optimizer': str,
        'num_epochs': int
    }
}
```

### 5.3 Storage Requirements
- Raw dataset: 7.3 GB (PT files)
- Processed pairs: 10 GB (Phase 1 cache)
- Checkpoints: 50 GB (20 checkpoints × 2.5 GB each)
- Final model: 2.5 GB
- **Total:** 70 GB disk space

---

## 6. Technical Constraints

### 6.1 Hardware Requirements
- **Minimum:** 1x NVIDIA V100 (16 GB VRAM) for Phase 1
- **Recommended:** 2x NVIDIA V100 (32 GB total VRAM) for Phase 2-3
- **Storage:** 70 GB SSD (recommended for I/O speed)

### 6.2 Software Dependencies
- Python ≥3.9
- PyTorch ≥2.0
- NumPy, SciPy (statistical tests)
- tqdm (progress bars)
- tensorboard (logging)

### 6.3 External Code Repositories
- NFN reference: https://github.com/AllanYangZhou/nfn
- CKA implementation: https://github.com/numpee/CKA.pytorch
- Contrastive loss: https://github.com/lucidrains/DALLE2-pytorch

---

## 7. Risk Mitigation

### 7.1 Risk R1: Insufficient Coverage (MITIGATED)
- **Status:** h-e1 validated 72.2% coverage
- **Action:** No additional mitigation needed

### 7.2 Risk R2: Noisy Task Labels (MEDIUM)
- **Detection:** Zero-shot transfer test (train without labels, measure clustering)
- **Threshold:** <85% zero-shot accuracy indicates label noise
- **Mitigation:** Pivot to unsupervised contrastive learning

### 7.3 Risk R3: Information Loss in Pooling (MEDIUM)
- **Detection:** Reconstruction task accuracy <70%
- **Mitigation:** Replace mean pooling with Set Transformer (learnable aggregation)
- **Abort Criterion:** Degradation >50% (pooling fundamentally incompatible)

### 7.4 Risk R4: Training Procedure Confound (HIGH)
- **Detection:** Same-augmentation clustering dominates same-task clustering
- **Mitigation:** Include training hyperparameters as conditioning variables
- **Ablation:** Test same-task different-procedure vs different-task same-procedure

### 7.5 Risk R5: Architecture Subspace Incompatibility (CRITICAL - GATED)
- **Detection:** Phase 1 CKA gate (same-task <0.6 OR different-task >0.4)
- **Mitigation:** Try nonlinear alignment (RBF kernel CKA), scope to CNN-only
- **Abort Criterion:** CKA <0.4 after all mitigation attempts

---

## 8. Implementation Phases

### Phase 1: CKA Feasibility Gate (Weeks 1-2)
**Deliverables:**
- NFN encoders trained for 4 architectures
- CKA computation script
- Feasibility test results (pass/fail)

**Success Criteria:**
- Same-task median CKA >0.6
- Different-task median CKA <0.4
- Gate decision: PROCEED or STOP

### Phase 2-3: Hierarchical VAE Training (Weeks 3-4)
**Deliverables:**
- Full 3-level VAE implementation
- Training loop with multi-objective loss
- Validation monitoring (reconstruction accuracy, loss curves)

**Success Criteria:**
- Training converges (loss stabilizes by epoch 150)
- Validation reconstruction accuracy >60%
- No gradient explosions (clipping effective)

### Phase 4: PoC Validation (Weeks 5-6)
**Deliverables:**
- WCSS bootstrap test results
- Architecture token ablation results
- Reconstruction task accuracy report
- UMAP visualizations

**Success Criteria:**
- WCSS gate passes (p<0.01, Cohen's d>0.5)
- Ablation shows ≥15pp degradation
- Reconstruction accuracy >70%

---

## 9. Acceptance Criteria

### 9.1 Primary (MUST_WORK)
- [ ] Phase 1 CKA gate: same-task >0.6 AND different-task <0.4
- [ ] Phase 4 WCSS test: p<0.01 AND Cohen's d>0.5
- [ ] Mean WCSS(same-task) < Mean WCSS(different-task)

### 9.2 Secondary (Validation)
- [ ] Architecture token ablation: ≥15pp degradation
- [ ] Reconstruction task accuracy: >70%
- [ ] Training completes without NaN gradients

### 9.3 Tertiary (Risk Mitigation)
- [ ] Zero-shot transfer: >85% accuracy (validates task labels)
- [ ] Training procedure ablation: procedure effect <60%

---

## 10. Out of Scope

### 10.1 Explicitly Excluded
- Fine-grained neuron-level analysis (only layer-summary level)
- Cross-dataset transfer (only ModelZooDataset)
- Real-time inference optimization (research PoC only)
- Production deployment infrastructure

### 10.2 Future Considerations
- Extension to Transformer architectures (ViT, BERT)
- Cross-task transfer learning applications
- Latent space arithmetic for model editing
- Scaling to 1M+ model zoo datasets

---

## 11. Glossary

**CKA (Centered Kernel Alignment):** Metric measuring similarity between two representations via centered Gram matrices. Range: [0, 1], higher = more similar.

**WCSS (Within-Cluster Sum of Squares):** Clustering metric measuring compactness. Lower WCSS = tighter cluster.

**NFN (Neural Functional Networks):** Permutation-equivariant encoders for neural network weights.

**Contrastive Triplet Loss:** Loss function encouraging anchor-positive similarity while pushing anchor-negative apart by margin.

**Beta Annealing:** Gradually reducing KL divergence weight to prevent posterior collapse in VAE training.

**Cohen's d:** Standardized effect size metric. d>0.5 = medium effect, d>0.8 = large effect.

---

## 12. Appendix

### 12.1 Compute Budget
- Phase 1: 48 GPU-hours ($50)
- Phase 2-3: 336 GPU-hours ($700)
- Phase 4: 48 GPU-hours ($50)
- **Total:** 432 GPU-hours, $800

### 12.2 Timeline
- Week 1: NFN encoder training
- Week 2: CKA feasibility gate (GATE 1)
- Week 3: VAE Levels 1-2 training
- Week 4: VAE Level 3 training (FULL CHECKPOINT)
- Week 5: WCSS bootstrap test (GATE 2)
- Week 6: Ablations + reconstruction test

### 12.3 References
- ModelZooDataset: https://doi.org/10.5281/zenodo.6620868
- NFN Paper: Zhou et al. 2023, "Neural Functional Networks"
- CKA Paper: Kornblith et al. 2019, "Similarity of Neural Network Representations"
- NVAE: Vahdat & Kautz 2020, "NVAE: A Deep Hierarchical VAE"

---

**Document Version:** 1.0  
**Last Updated:** 2026-08-20  
**Status:** APPROVED - Ready for Architecture Design
