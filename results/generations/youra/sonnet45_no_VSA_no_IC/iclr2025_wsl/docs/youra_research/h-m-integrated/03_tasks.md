# Implementation Tasks: h-m-integrated
## Hierarchical VAE for Cross-Architecture Model Zoo Analysis

**Hypothesis ID:** h-m-integrated  
**Complexity Tier:** HIGH (Score: 4.0)  
**Estimated Total Budget:** 20 tasks  
**Date:** 2026-08-20

---

## Task Allocation Summary

| Category | Count | Budget |
|----------|-------|--------|
| Data Preparation | 4 | 20% |
| Environment Setup | 2 | 10% |
| Epic Tasks (Level 1-3 + Integration) | 7 | 35% |
| Epic Subtasks (Training, Evaluation) | 7 | 35% |
| Total | 20 | 100% |

---

## Phase 0: Data Preparation (4 tasks, 20%)

### TASK-DATA-01: Download ModelZooDataset
**Type:** DATA_SETUP  
**Priority:** CRITICAL (blocks all)  
**Complexity:** 2/10  
**Estimated Time:** 2 hours

**Description:**
Download CIFAR-10 ModelZooDataset from Zenodo and verify integrity.

**Acceptance Criteria:**
- [ ] Download `dataset_cifar_small_hyp_rand.pt` (1.8 GB)
- [ ] Download `dataset_cifar_large_hyp_rand.pt` (5.5 GB)
- [ ] Download `index_dict_small.json` and `index_dict_large.json`
- [ ] Verify file hashes (SHA256)
- [ ] Store in `data/raw/modelzoo/`

**Dependencies:** None

**Implementation Notes:**
- Use Zenodo API or direct download: https://doi.org/10.5281/zenodo.6620868
- Add download script: `src/data/download_modelzoo.py`

---

### TASK-DATA-02: Download ResNet Models from SANE
**Type:** DATA_SETUP  
**Priority:** HIGH  
**Complexity:** 3/10  
**Estimated Time:** 3 hours

**Description:**
Download ResNet-18/34 models from SANE repository for cross-architecture validation.

**Acceptance Criteria:**
- [ ] Download CIFAR-10 ResNet-18 models (.tar file)
- [ ] Download CIFAR-100 ResNet-18 models (.tar file)
- [ ] Extract and convert to PyTorch .pt format
- [ ] Verify model count: ≥120 models per task
- [ ] Store in `data/raw/sane/`

**Dependencies:** None

**Implementation Notes:**
- SANE URL: https://ai.unisg.ch/files/tar_files/
- Add extraction script: `src/data/download_sane.py`

---

### TASK-DATA-03: Create Train/Val/Test Splits
**Type:** DATA_SETUP  
**Priority:** CRITICAL  
**Complexity:** 4/10  
**Estimated Time:** 4 hours

**Description:**
Split 2,120 models into train/val/test (70/15/15) with architecture-task stratification.

**Acceptance Criteria:**
- [ ] Stratified split maintains architecture-task proportions
- [ ] Train: 1,484 models, Val: 318 models, Test: 318 models
- [ ] No data leakage between splits
- [ ] Save split indices to `data/processed/splits.json`
- [ ] Validate coverage: all 4 architectures × 9 tasks represented

**Dependencies:** TASK-DATA-01, TASK-DATA-02

**Implementation Notes:**
- Use sklearn.model_selection.StratifiedShuffleSplit
- Save indices (not raw data) to enable reproducibility

---

### TASK-DATA-04: Implement Triplet Sampling DataLoader
**Type:** DATA_SETUP  
**Priority:** CRITICAL  
**Complexity:** 5/10  
**Estimated Time:** 5 hours

**Description:**
Create PyTorch DataLoader that yields triplets (anchor, positive, negative) for contrastive training.

**Acceptance Criteria:**
- [ ] Sample anchor randomly from batch
- [ ] Sample positive: same-task, different-architecture
- [ ] Sample negative: different-task (any architecture)
- [ ] Balance positive/negative counts per batch
- [ ] Support Phase 1 pair sampling (200 pairs: 100 same-task, 100 diff-task)
- [ ] Add unit tests for triplet validity

**Dependencies:** TASK-DATA-03

**Implementation Notes:**
- File: `src/data/triplet_sampler.py`
- Cache precomputed pairs for Phase 1 (faster CKA gate)

---

## Phase 1: Environment Setup (2 tasks, 10%)

### TASK-ENV-01: Setup Python Environment
**Type:** ENV_SETUP  
**Priority:** CRITICAL  
**Complexity:** 2/10  
**Estimated Time:** 1 hour

**Description:**
Create conda environment with all dependencies.

**Acceptance Criteria:**
- [ ] Create `environment.yml` with pinned versions
- [ ] Install PyTorch 2.0+ with CUDA 11.8
- [ ] Install NumPy, SciPy, tqdm, tensorboard
- [ ] Verify GPU detection (2x V100)
- [ ] Test CUDA operations (simple matrix multiply)

**Dependencies:** None

**Implementation Notes:**
- Environment name: `h-m-integrated`
- Pin PyTorch to 2.0.1 (tested version)

---

### TASK-ENV-02: Setup Project Structure
**Type:** ENV_SETUP  
**Priority:** HIGH  
**Complexity:** 1/10  
**Estimated Time:** 1 hour

**Description:**
Create directory structure and configuration files.

**Acceptance Criteria:**
- [ ] Create `src/` with subdirectories: data/, models/, training/, evaluation/
- [ ] Create `config/` for YAML configs
- [ ] Create `checkpoints/` for model saves
- [ ] Create `logs/` for tensorboard
- [ ] Add `README.md` with setup instructions

**Dependencies:** None

**Implementation Notes:**
- Match structure from architecture document Section 3

---

## Phase 2: Epic Implementation (7 tasks, 35%)

### EPIC-01: Implement Level 1 NFN/UNF Encoders
**Type:** MODEL_COMPONENT  
**Priority:** CRITICAL  
**Complexity:** 8/10  
**Estimated Time:** 16 hours

**Description:**
Implement architecture-specific encoders with permutation invariance.

**Acceptance Criteria:**
- [ ] NFNEncoder class (DeepSets phi/rho aggregation)
- [ ] Support variable-length inputs (10K-200K neurons)
- [ ] Per-architecture encoder variants (CNN-small, CNN-large, ResNet-18, ResNet-34)
- [ ] Output: (batch, num_neurons, 512) embeddings
- [ ] Unit tests for permutation invariance
- [ ] Benchmark memory usage (<2 GB VRAM per encoder)

**Dependencies:** TASK-ENV-01

**Implementation Notes:**
- File: `src/models/encoders.py`
- Reuse PyTorch DeepSets pattern (no custom CUDA kernels)
- Reference: https://github.com/AllanYangZhou/nfn (simplify to DeepSets)

---

### EPIC-02: Implement Level 2 Hierarchical Pooling
**Type:** MODEL_COMPONENT  
**Priority:** CRITICAL  
**Complexity:** 6/10  
**Estimated Time:** 8 hours

**Description:**
Implement layer-wise pooling to create fixed-length layer summaries.

**Acceptance Criteria:**
- [ ] HierarchicalPooling class
- [ ] Layer-wise mean pooling over neuron embeddings
- [ ] MLP projection: Linear(512→512) + ReLU + LayerNorm
- [ ] Output: (batch, num_layers, 512)
- [ ] Handle variable layer counts (18-34 layers)
- [ ] Unit tests for output shape invariance

**Dependencies:** EPIC-01

**Implementation Notes:**
- File: `src/models/pooling.py`
- Use `torch.split` with layer indices from metadata

---

### EPIC-03: Implement Level 3 Transformer
**Type:** MODEL_COMPONENT  
**Priority:** CRITICAL  
**Complexity:** 7/10  
**Estimated Time:** 12 hours

**Description:**
Implement Transformer with CLS token extraction for VAE latent projection.

**Acceptance Criteria:**
- [ ] TransformerRelational class
- [ ] 6-layer Transformer encoder (8 heads, d_model=512)
- [ ] Learnable CLS token + architecture-type token
- [ ] Pre-norm architecture (LayerNorm before attention)
- [ ] Output: mu, logvar each (batch, 512)
- [ ] Unit tests for gradient flow

**Dependencies:** EPIC-02

**Implementation Notes:**
- File: `src/models/transformer.py`
- Use `torch.nn.TransformerEncoder` (standard PyTorch)
- Add dropout=0.1 for regularization

---

### EPIC-04: Implement Shared Decoder
**Type:** MODEL_COMPONENT  
**Priority:** HIGH  
**Complexity:** 4/10  
**Estimated Time:** 4 hours

**Description:**
Implement shared MLP decoder for weight reconstruction.

**Acceptance Criteria:**
- [ ] SharedDecoder class
- [ ] MLP: Linear(512→1024→2048→max_weight_dim)
- [ ] Support variable-length outputs (slice to actual weight_dim)
- [ ] Output: (batch, weight_dim)
- [ ] Unit tests for reconstruction shape matching

**Dependencies:** EPIC-03

**Implementation Notes:**
- File: `src/models/decoder.py`
- max_weight_dim = 200,000 (ResNet-34)

---

### EPIC-05: Integrate Hierarchical VAE
**Type:** MODEL_INTEGRATION  
**Priority:** CRITICAL  
**Complexity:** 9/10  
**Estimated Time:** 12 hours

**Description:**
Integrate all 3 levels + decoder into single HierarchicalVAE module.

**Acceptance Criteria:**
- [ ] HierarchicalVAE class
- [ ] Forward pass: weights → (z, mu, logvar, reconstructed)
- [ ] Reparameterization trick: z = mu + eps * exp(0.5 * logvar)
- [ ] Support multi-GPU DataParallel
- [ ] End-to-end gradient flow test
- [ ] Memory profiling (target: <7 GB VRAM per GPU)

**Dependencies:** EPIC-01, EPIC-02, EPIC-03, EPIC-04

**Implementation Notes:**
- File: `src/models/hierarchical_vae.py`
- Use `nn.ModuleDict` for encoder registry

---

### EPIC-06: Implement Multi-Objective Loss
**Type:** TRAINING_COMPONENT  
**Priority:** CRITICAL  
**Complexity:** 7/10  
**Estimated Time:** 8 hours

**Description:**
Implement combined loss function with 4 components + beta annealing.

**Acceptance Criteria:**
- [ ] ComposedLoss class
- [ ] Reconstruction: MSE(reconstructed, input)
- [ ] KL Divergence: -0.5 * sum(1 + logvar - mu^2 - exp(logvar))
- [ ] Contrastive Triplet: max(0, d(a,p) - d(a,n) + margin)
- [ ] Task Classification: CrossEntropy(task_logits, task_labels)
- [ ] Beta annealing schedule: 1.0 → 0.1 linear over 200 epochs
- [ ] Unit tests for loss weighting

**Dependencies:** EPIC-05

**Implementation Notes:**
- File: `src/training/losses.py`
- Return dict: `{total, recon, kl, contrastive, task}`

---

### EPIC-07: Implement Training Loop
**Type:** TRAINING_COMPONENT  
**Priority:** CRITICAL  
**Complexity:** 9/10  
**Estimated Time:** 16 hours

**Description:**
Implement full training pipeline with checkpointing, logging, early stopping.

**Acceptance Criteria:**
- [ ] TrainingPipeline class
- [ ] Support multi-GPU DataParallel
- [ ] Gradient clipping (max_norm=1.0)
- [ ] Checkpoint saving (every 10 epochs, keep last 5)
- [ ] Tensorboard logging (losses, learning rate, beta schedule)
- [ ] Validation loop (no gradient)
- [ ] Early stopping (patience=20 epochs)
- [ ] Resume from checkpoint

**Dependencies:** EPIC-05, EPIC-06, TASK-DATA-04

**Implementation Notes:**
- File: `src/training/trainer.py`
- Use AdamW optimizer (lr=1e-4, weight_decay=1e-5)

---

## Phase 3: Evaluation Implementation (7 tasks, 35%)

### EVAL-01: Implement CKA Computation
**Type:** EVALUATION  
**Priority:** CRITICAL  
**Complexity:** 6/10  
**Estimated Time:** 6 hours

**Description:**
Implement linear CKA similarity metric with centered Gram matrices.

**Acceptance Criteria:**
- [ ] linear_cka(X, Y) function
- [ ] Compute centered Gram matrices: H @ K @ H
- [ ] HSIC estimator: trace(K_c @ L_c) / (n-1)^2
- [ ] CKA formula: HSIC(X,Y) / sqrt(HSIC(X,X) * HSIC(Y,Y))
- [ ] Numerical stability checks (regularization)
- [ ] Unit tests vs reference implementation

**Dependencies:** EPIC-01

**Implementation Notes:**
- File: `src/evaluation/cka.py`
- Reference: https://github.com/numpee/CKA.pytorch

---

### EVAL-02: Implement Phase 1 CKA Gate
**Type:** EVALUATION  
**Priority:** CRITICAL  
**Complexity:** 7/10  
**Estimated Time:** 8 hours

**Description:**
Implement CKA feasibility test with 200 model pairs.

**Acceptance Criteria:**
- [ ] Sample 200 pairs (100 same-task, 100 diff-task)
- [ ] Encode using Level 1 encoders only
- [ ] Compute pairwise CKA for all pairs
- [ ] Calculate median CKA for same-task and diff-task groups
- [ ] Gate decision: PASS if same-task >0.6 AND diff-task <0.4
- [ ] Save CKA matrix heatmap (visualization)
- [ ] Report: `{pass: bool, same_task_cka: float, diff_task_cka: float}`

**Dependencies:** EVAL-01, TASK-DATA-04

**Implementation Notes:**
- File: `src/evaluation/phase1_cka_gate.py`
- Early stop if gate fails (save $700 GPU cost)

---

### EVAL-03: Implement WCSS Bootstrap Test
**Type:** EVALUATION  
**Priority:** CRITICAL  
**Complexity:** 8/10  
**Estimated Time:** 10 hours

**Description:**
Implement statistical clustering test with bootstrap resampling.

**Acceptance Criteria:**
- [ ] Extract latent embeddings from test set (318 models)
- [ ] Bootstrap resample: 100 iterations
- [ ] Compute WCSS for same-task clusters vs random clusters
- [ ] T-test + Cohen's d effect size
- [ ] Gate criterion: p<0.01 AND Cohen's d>0.5
- [ ] Save bootstrap distribution plots
- [ ] Report: `{mean_same_task_wcss, mean_diff_task_wcss, p_value, cohen_d, pass}`

**Dependencies:** EPIC-05

**Implementation Notes:**
- File: `src/evaluation/wcss_bootstrap.py`
- Use `scipy.stats.ttest_ind` for statistical test

---

### EVAL-04: Implement Architecture Token Ablation
**Type:** EVALUATION  
**Priority:** HIGH  
**Complexity:** 7/10  
**Estimated Time:** 10 hours

**Description:**
Retrain VAE without architecture tokens and measure clustering degradation.

**Acceptance Criteria:**
- [ ] Create TransformerNoArchToken variant (remove arch token)
- [ ] Retrain VAE with ablated transformer (200 epochs)
- [ ] Re-evaluate WCSS clustering
- [ ] Measure degradation: `(wcss_ablation - wcss_baseline) / wcss_baseline * 100`
- [ ] Success criterion: degradation ≥15%
- [ ] Report: `{degradation_pct: float, pass: bool}`

**Dependencies:** EVAL-03

**Implementation Notes:**
- File: `src/evaluation/ablation_arch_token.py`
- Reuse training pipeline, swap transformer module

---

### EVAL-05: Implement Reconstruction Task Accuracy Test
**Type:** EVALUATION  
**Priority:** MEDIUM  
**Complexity:** 5/10  
**Estimated Time:** 5 hours

**Description:**
Train classifier on reconstructed weights to validate pooling preserves task information.

**Acceptance Criteria:**
- [ ] Simple MLP classifier: Linear(weight_dim→512→9)
- [ ] Train on decoder outputs from validation set
- [ ] Test on decoder outputs from test set
- [ ] Measure task prediction accuracy
- [ ] Success criterion: accuracy >70%
- [ ] Report: `{accuracy: float, pass: bool}`

**Dependencies:** EPIC-07

**Implementation Notes:**
- File: `src/evaluation/reconstruction_accuracy.py`
- Train classifier for 50 epochs (lightweight)

---

### EVAL-06: Implement UMAP Visualization
**Type:** EVALUATION  
**Priority:** LOW  
**Complexity:** 4/10  
**Estimated Time:** 4 hours

**Description:**
Create 2D UMAP projection of latent space for visualization.

**Acceptance Criteria:**
- [ ] Extract latent embeddings from test set
- [ ] Compute UMAP projection (n_components=2)
- [ ] Color by task label, shape by architecture
- [ ] Save high-resolution plot (PNG + PDF)
- [ ] Add legend and annotations

**Dependencies:** EPIC-07

**Implementation Notes:**
- File: `src/evaluation/visualize_latent.py`
- Use `umap-learn` package

---

### EVAL-07: Generate Phase 4 Validation Report
**Type:** EVALUATION  
**Priority:** HIGH  
**Complexity:** 3/10  
**Estimated Time:** 3 hours

**Description:**
Compile all evaluation results into final validation report.

**Acceptance Criteria:**
- [ ] Aggregate results from EVAL-02, EVAL-03, EVAL-04, EVAL-05
- [ ] Generate summary table (gates, metrics, pass/fail)
- [ ] Include visualizations (CKA heatmap, UMAP, WCSS plots)
- [ ] Save as Markdown: `docs/youra_research/h-m-integrated/04_validation.md`
- [ ] Include training curves (loss plots)

**Dependencies:** EVAL-02, EVAL-03, EVAL-04, EVAL-05, EVAL-06

**Implementation Notes:**
- File: `src/evaluation/generate_report.py`
- Auto-generate plots using matplotlib

---

## Task Dependency Graph

```
TASK-DATA-01, TASK-DATA-02 → TASK-DATA-03 → TASK-DATA-04
                                                     ↓
TASK-ENV-01, TASK-ENV-02 → EPIC-01 → EPIC-02 → EPIC-03 → EPIC-04 → EPIC-05 → EPIC-06 → EPIC-07
                             ↓                                         ↓         ↓         ↓
                          EVAL-01 → EVAL-02                          EVAL-03 → EVAL-04 → EVAL-05
                                                                                           ↓
                                                                                        EVAL-06
                                                                                           ↓
                                                                                        EVAL-07
```

**Critical Path:** 
TASK-DATA-01 → TASK-DATA-03 → TASK-DATA-04 → EPIC-01 → EPIC-02 → EPIC-03 → EPIC-05 → EPIC-07 → EVAL-03 → EVAL-07

**Estimated Critical Path Duration:** 88 hours (11 days at 8 hours/day)

---

## Implementation Budget Allocation

| Task ID | Complexity | Hours | % of Budget |
|---------|-----------|-------|-------------|
| TASK-DATA-01 | 2 | 2 | 2.2% |
| TASK-DATA-02 | 3 | 3 | 3.3% |
| TASK-DATA-03 | 4 | 4 | 4.4% |
| TASK-DATA-04 | 5 | 5 | 5.6% |
| TASK-ENV-01 | 2 | 1 | 1.1% |
| TASK-ENV-02 | 1 | 1 | 1.1% |
| EPIC-01 | 8 | 16 | 17.8% |
| EPIC-02 | 6 | 8 | 8.9% |
| EPIC-03 | 7 | 12 | 13.3% |
| EPIC-04 | 4 | 4 | 4.4% |
| EPIC-05 | 9 | 12 | 13.3% |
| EPIC-06 | 7 | 8 | 8.9% |
| EPIC-07 | 9 | 16 | 17.8% |
| EVAL-01 | 6 | 6 | 6.7% |
| EVAL-02 | 7 | 8 | 8.9% |
| EVAL-03 | 8 | 10 | 11.1% |
| EVAL-04 | 7 | 10 | 11.1% |
| EVAL-05 | 5 | 5 | 5.6% |
| EVAL-06 | 4 | 4 | 4.4% |
| EVAL-07 | 3 | 3 | 3.3% |
| **Total** | **116** | **138** | **153%** |

**Note:** 138 hours exceeds budget estimate (complexity score 4.0 suggests ~100-120 hours). Tasks EVAL-04, EVAL-05, EVAL-06 can be deprioritized if time-constrained (total savings: 19 hours).

---

## Execution Phases

### Week 1-2: Data + Environment + Level 1
- Days 1-2: TASK-DATA-01, TASK-DATA-02, TASK-ENV-01, TASK-ENV-02
- Days 3-5: TASK-DATA-03, TASK-DATA-04
- Days 6-9: EPIC-01 (NFN encoders)
- Days 10-11: EVAL-01, EVAL-02 (CKA gate) **← GATE DECISION**

### Week 3-4: Level 2-3 + Integration + Training
- Days 12-13: EPIC-02 (Hierarchical pooling)
- Days 14-16: EPIC-03 (Transformer)
- Days 17-18: EPIC-04 (Decoder) + EPIC-05 (Integration)
- Days 19-20: EPIC-06 (Loss function)
- Days 21-28: EPIC-07 (Training 200 epochs)

### Week 5-6: Evaluation + Validation
- Days 29-31: EVAL-03 (WCSS bootstrap) **← GATE DECISION**
- Days 32-34: EVAL-04 (Ablation)
- Days 35-36: EVAL-05 (Reconstruction accuracy)
- Day 37: EVAL-06 (UMAP visualization)
- Day 38: EVAL-07 (Final report)

---

## Success Criteria Checklist

**Phase 1 CKA Gate (Week 2):**
- [ ] Same-task median CKA >0.6
- [ ] Different-task median CKA <0.4
- [ ] **Decision:** PROCEED or STOP

**Phase 4 WCSS Gate (Week 5):**
- [ ] Mean WCSS(same-task) < Mean WCSS(different-task)
- [ ] p-value <0.01
- [ ] Cohen's d >0.5
- [ ] **Decision:** PASS or FAIL

**Secondary Validation:**
- [ ] Architecture token ablation: degradation ≥15%
- [ ] Reconstruction task accuracy: >70%
- [ ] Training completes without NaN gradients
- [ ] All checkpoints saved successfully

---

**Document Version:** 1.0  
**Last Updated:** 2026-08-20  
**Status:** APPROVED - Ready for Phase 4 Implementation
