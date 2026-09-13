# Product Requirements Document: h-m-integrated Mechanism Analysis

**Date:** 2026-03-20
**Author:** Phase 3 Implementation Planning
**Hypothesis:** h-m-integrated - 3-step causal mechanism (InfoNCE clustering → Clusterability predicts efficacy → LA-SSL disperses)
**Source:** 02c_experiment_brief.md (Phase 2C)
**Status:** Draft

---

## Executive Summary

### Purpose
Validate the complete 3-step causal mechanism explaining HOW InfoNCE creates spurious clusters (M1), WHY clusterability predicts intervention efficacy (M2), and HOW LA-SSL learning-speed resampling reshapes embedding geometry (M3).

### Scope
- Standard SimCLR SSL training (InfoNCE loss, ResNet-50, 100 epochs)
- LA-SSL variant with learning-speed aware sampling
- K-means clustering analysis (k=4) on frozen embeddings
- Linear probe baseline (ERM) with grid search
- Cluster-balanced retraining intervention
- Comprehensive mechanism validation (AMI evolution, correlation analysis, geometry visualization)

### Success Criteria
**Primary (MUST_WORK Gate - M1+M2):**
- M1 (InfoNCE clustering): AMI ≥0.4 on standard SimCLR embeddings
- M2 (Efficacy prediction): Significant positive correlation between AMI and ΔWGA (p<0.05), high-AMI models gain ≥2pp WGA

**Secondary (M3 - can fail gracefully):**
- M3 (LA-SSL dispersion): AMI reduction ≥30% with ΔAUC <0.05 (geometry reshaping not signal suppression)

### Out of Scope (h-m-integrated)
- ViT-H-14 high-capacity baseline (deferred to h-c1)
- Alternative SSL methods (MoCo, BYOL, SwAV)
- Non-contrastive learning approaches

---

## Problem Statement

### Research Question
Can we explain the complete causal chain from InfoNCE contrastive loss to fairness intervention efficacy through spurious cluster formation, and validate LA-SSL as a geometric reshaping mechanism?

### Current Limitations
- InfoNCE's role in creating spurious clusters unconfirmed
- Missing link between clusterability and intervention success
- LA-SSL mechanism (geometry vs signal) unclear

### Hypothesis to Validate
The 3-step causal mechanism operates as: (M1) InfoNCE contrastive loss creates dense spurious feature clusters (shared backgrounds) leading to high AMI, (M2) High clusterability enables minority groups to occupy distinct density modes exploitable by linear ERM and further improved by cluster-based reweighting, (M3) LA-SSL learning-speed resampling disperses spurious density structure (reducing AMI by ≥30%) while preserving linear separability (ΔAUC <0.05).

---

## Functional Requirements

### FR-1: Data Pipeline (Reuse from h-e1)
**ID:** FR-1
**Priority:** P0 (Critical)
**Description:** Reuse validated Waterbirds dataset pipeline from h-e1

**Acceptance Criteria:**
- Load from existing cache: `/home/anonymous/YouRA_results_new_4_sonnet45/TEST_scsl/docs/youra_research/20260318_scsl/.data_cache/datasets/waterbird_complete95_forest2water2`
- Verify splits: Train 4,795 | Val 1,199 | Test 5,794
- Reuse WaterbirdsDataset class from h-e1 codebase
- Apply identical transforms as h-e1 for controlled comparison

**Dependencies:** None (h-e1 prerequisite validated)

---

### FR-2: Standard SimCLR SSL Pretraining (M1 Baseline)
**ID:** FR-2
**Priority:** P0 (Critical)
**Description:** Train standard SimCLR model to validate InfoNCE creates spurious clusters

**Acceptance Criteria:**
- Implement ResNet-50 encoder (pretrained=False) with projection head (2048 → 2048 → 128)
- Implement NT-Xent contrastive loss with temperature=0.5
- Apply dual augmentations: RandomResizedCrop(224), ColorJitter(0.8), RandomGrayscale(0.2), GaussianBlur(kernel=23)
- Train 100 epochs with SGD optimizer (optimal LR from h-e1 grid search, cosine decay)
- Save checkpoints every 10 epochs for AMI evolution analysis
- Freeze encoder after training for downstream tasks

**Dependencies:** FR-1

---

### FR-3: LA-SSL Learning-Speed Aware Training (M3 Intervention)
**ID:** FR-3
**Priority:** P0 (Critical)
**Description:** Implement LA-SSL with learning-speed aware sampling to test geometry dispersion

**Acceptance Criteria:**
- Implement LASSLSampler class tracking per-sample loss history (window=10 epochs)
- Compute sampling probabilities inversely proportional to learning speed (alpha=0.5)
- Train identical architecture as FR-2 (ResNet-50 + projection head)
- Same hyperparameters as SimCLR except custom sampler
- Save checkpoints every 10 epochs aligned with SimCLR for comparison
- Track per-sample loss deltas for validation

**Dependencies:** FR-1, FR-2

---

### FR-4: Embedding Extraction & Clustering Analysis
**ID:** FR-4
**Priority:** P0 (Critical)
**Description:** Extract frozen embeddings and perform k-means clustering for all checkpoints

**Acceptance Criteria:**
- Extract 2048-dim embeddings from frozen encoder for test samples (5,794 × 2048)
- Run k-means with k=4, random_state=42, n_init=10 for each checkpoint
- Compute AMI using sklearn.metrics.adjusted_mutual_info_score
- Track AMI evolution across training epochs (epoch 10, 20, ..., 100)
- Compute Silhouette score as cluster quality metric
- Store cluster assignments for all checkpoints

**Dependencies:** FR-2, FR-3

---

### FR-5: Linear Probe Baseline (ERM)
**ID:** FR-5
**Priority:** P0 (Critical)
**Description:** Train linear probe on frozen embeddings as fairness baseline

**Acceptance Criteria:**
- Freeze encoder, train linear classifier (2048 → 2 classes)
- Grid search: LR [0.01, 0.001, 0.0001], WD [1e-4, 1e-5, 1e-6]
- Train 20 epochs with early stopping on validation WGA
- Compute baseline WGA (worst-group accuracy) for all 4 groups
- Track group-wise accuracies separately
- Apply to all checkpoints (SimCLR and LA-SSL)

**Dependencies:** FR-4

---

### FR-6: Cluster-Balanced Retraining Intervention
**ID:** FR-6
**Priority:** P0 (Critical)
**Description:** Apply cluster-balanced retraining to measure ΔWGA improvement

**Acceptance Criteria:**
- Use k-means cluster assignments from FR-4
- Reweight training samples to balance cluster membership
- Retrain linear classifier for 20 epochs with cluster-balanced weights
- Compute intervention WGA and calculate ΔWGA = (intervention WGA - baseline WGA)
- Apply to checkpoints with AMI ≥0.4 and AMI <0.3 for diagnostic validation
- Track improvement across all checkpoints

**Dependencies:** FR-4, FR-5

---

### FR-7: M1 Validation (InfoNCE Creates Clusters)
**ID:** FR-7
**Priority:** P0 (Critical - MUST_WORK)
**Description:** Validate that standard SimCLR creates high AMI spurious clusters

**Acceptance Criteria:**
- Measure AMI on SimCLR epoch-100 checkpoint
- Success: AMI ≥0.4
- Compute Silhouette score as secondary validation (expect >0.3)
- Visualize embeddings via t-SNE/UMAP colored by true groups

**Dependencies:** FR-4

---

### FR-8: M2 Validation (Clusterability Predicts Efficacy)
**ID:** FR-8
**Priority:** P0 (Critical - MUST_WORK)
**Description:** Validate that AMI predicts cluster-balanced retraining improvement

**Acceptance Criteria:**
- Collect (AMI, ΔWGA) pairs across all SimCLR checkpoints (10 epochs × 10 = 10 points)
- Compute Pearson correlation between AMI and ΔWGA
- Success: Correlation significant (p<0.05) AND positive
- High-AMI checkpoints (≥0.4): mean ΔWGA ≥2pp
- Create scatter plot with regression line

**Dependencies:** FR-6, FR-7

---

### FR-9: M3 Validation (LA-SSL Disperses Clusters)
**ID:** FR-9
**Priority:** P1 (Secondary - can fail gracefully)
**Description:** Validate that LA-SSL reduces AMI while preserving linear separability

**Acceptance Criteria:**
- Compare AMI: SimCLR vs LA-SSL at epoch 100
- Compute AMI reduction: (AMI_SimCLR - AMI_LASSL) / AMI_SimCLR
- Success: AMI reduction ≥30%
- Measure linear separability: AUC of linear probe for subgroup classification
- Compute ΔAUC = |AUC_SimCLR - AUC_LASSL|
- Success: ΔAUC <0.05 (geometry reshaping not signal suppression)

**Dependencies:** FR-3, FR-4

---

### FR-10: AMI Evolution Tracking
**ID:** FR-10
**Priority:** P1 (Secondary)
**Description:** Track AMI evolution during training to understand cluster emergence

**Acceptance Criteria:**
- Compute AMI at epochs [10, 20, 30, ..., 100] for both SimCLR and LA-SSL
- Plot AMI evolution line chart (x=epoch, y=AMI, color=method)
- Identify when clustering emerges (AMI crosses 0.4 threshold)
- Identify if LA-SSL prevents emergence or disperses existing clusters

**Dependencies:** FR-4

---

### FR-11: Visualization Suite
**ID:** FR-11
**Priority:** P1 (Secondary)
**Description:** Generate comprehensive visualizations for mechanism validation

**Acceptance Criteria:**
- t-SNE/UMAP embeddings: SimCLR vs LA-SSL (colored by true groups, spurious groups, k-means clusters)
- AMI evolution line plot (epoch vs AMI for both methods)
- AMI-ΔWGA correlation scatter plot (with regression line)
- Group-wise accuracy bar chart (4 groups × {Linear ERM, Cluster-balanced, LA-SSL})
- Linear separability vs clusterability scatter (AMI vs Linear AUC)
- Save all figures to `{hypothesis_folder}/figures/`

**Dependencies:** FR-4, FR-6, FR-9

---

## Non-Functional Requirements

### NFR-1: Reproducibility
- Fix all random seeds (PyTorch, NumPy, sklearn)
- Use 3 random seeds for stability (MECHANISM hypothesis)
- Document all hyperparameters in config files

### NFR-2: GPU Efficiency
- Use single GPU (check nvidia-smi for empty GPU)
- Set CUDA_VISIBLE_DEVICES before training
- Batch size: 128 (with gradient accumulation if needed)

### NFR-3: Checkpointing
- Save model checkpoints every 10 epochs
- Save optimizer state for resumable training
- Store embeddings and cluster assignments per checkpoint

### NFR-4: Logging
- Log AMI, WGA, ΔWGA, Silhouette score per checkpoint
- Track training loss, learning rate per epoch
- Save metrics to JSON for post-analysis

### NFR-5: Code Reuse
- Inherit from h-e1 codebase (dataset, base model, evaluation)
- Only add LA-SSL sampler and mechanism-specific analysis
- Maintain compatibility with h-e1 checkpoint format

---

## Success Criteria

### Primary Success (MUST_WORK Gate)
1. **M1 Pass**: AMI ≥0.4 on SimCLR epoch-100
2. **M2 Pass**: Significant AMI-ΔWGA correlation (p<0.05) with high-AMI gaining ≥2pp WGA

### Secondary Success (M3 - can fail)
3. **M3 Pass**: LA-SSL AMI reduction ≥30% with ΔAUC <0.05

### Graceful Degradation
- M1+M2 passing → Tiers 1-2 publishable (clusterability diagnostic validated)
- M3 failing → LA-SSL mechanism unexplained, but core contribution intact

---

## Dependencies

### External Dependencies
- PyTorch ≥2.0
- torchvision
- sklearn (k-means, AMI, Silhouette)
- WILDS library (dataset loading)
- matplotlib, seaborn (visualization)

### Internal Dependencies
- **h-e1 codebase** (prerequisite validated):
  - Dataset loader
  - ResNet-50 + projection head architecture
  - Optimal hyperparameters from grid search
  - Evaluation metrics (AMI, WGA)

---

## Data Requirements

### Primary Dataset
- **Name**: Waterbirds
- **Source**: h-e1 cache (validated)
- **Path**: `/home/anonymous/YouRA_results_new_4_sonnet45/TEST_scsl/docs/youra_research/20260318_scsl/.data_cache/datasets/waterbird_complete95_forest2water2`
- **Size**: 11,788 images (Train 4,795 | Val 1,199 | Test 5,794)

### Checkpoints
- SimCLR checkpoints: 10 files (epoch 10-100, every 10 epochs)
- LA-SSL checkpoints: 10 files (aligned with SimCLR)
- Storage estimate: ~500MB per checkpoint × 20 = ~10GB total

---

## Testing Requirements

### Unit Tests
- LASSLSampler probability computation
- Loss history tracking correctness
- Cluster-balanced weight calculation

### Integration Tests
- End-to-end SimCLR training (1 epoch, small batch)
- LA-SSL training with sampler
- AMI computation on mock embeddings

### Validation Tests
- M1 gate check: AMI ≥0.4
- M2 gate check: correlation p<0.05, ΔWGA ≥2pp
- M3 gate check: AMI reduction ≥30%, ΔAUC <0.05

---

## Deliverables

1. **Code Implementation**
   - `simclr_trainer.py` - Standard SimCLR training
   - `lassl_sampler.py` - LA-SSL learning-speed sampler
   - `lassl_trainer.py` - LA-SSL training loop
   - `clustering_analysis.py` - AMI computation, k-means
   - `linear_probe.py` - ERM baseline and cluster-balanced retraining
   - `mechanism_validation.py` - M1/M2/M3 gate checks
   - `visualization.py` - All figures

2. **Artifacts**
   - 20 model checkpoints (SimCLR + LA-SSL)
   - `metrics.json` - All AMI, WGA, ΔWGA values
   - 5+ figures in `figures/` directory

3. **Validation Report**
   - `04_validation.md` - Gate check results, test pass rates, mechanism validation

---

## Timeline & Milestones

**Note**: No time estimates per BMAD guidelines. Focus on completion not duration.

**Milestone 1**: Data & Environment Setup
- FR-1 complete (dataset loading verified)
- Environment with PyTorch, WILDS, sklearn ready

**Milestone 2**: Baseline Training
- FR-2 complete (SimCLR trained, checkpoints saved)
- FR-4 complete (embeddings extracted, AMI computed)

**Milestone 3**: Intervention Training
- FR-3 complete (LA-SSL trained)
- FR-5, FR-6 complete (linear probes and cluster-balanced retraining)

**Milestone 4**: Mechanism Validation
- FR-7, FR-8, FR-9 complete (M1/M2/M3 gate checks)
- FR-10, FR-11 complete (visualizations and analysis)

**Final**: Validation report with gate results

---

## Risks & Mitigations

### Risk 1: M1 Fails (AMI <0.4)
**Impact**: MUST_WORK gate violated, hypothesis invalid
**Mitigation**: Verify SimCLR implementation matches h-e1 (already validated), check temperature parameter, ensure sufficient training epochs

### Risk 2: M2 Fails (No AMI-ΔWGA correlation)
**Impact**: MUST_WORK gate violated, core mechanism unvalidated
**Mitigation**: Collect enough checkpoints (10+ points), verify cluster-balanced retraining logic, check if variance across seeds masks signal

### Risk 3: M3 Fails (LA-SSL doesn't disperse)
**Impact**: Secondary failure, M3 mechanism unexplained
**Mitigation**: Graceful degradation - M1+M2 sufficient for Tiers 1-2 publication

### Risk 4: GPU Availability
**Impact**: Training delays
**Mitigation**: Check nvidia-smi before starting, queue jobs if needed, use gradient accumulation for memory constraints

---

## Appendix A: Hyperparameters

### SimCLR Training
- Optimizer: SGD
- Learning Rate: {optimal from h-e1 grid search}
- Momentum: 0.9
- Weight Decay: 1e-4
- Batch Size: 128
- Epochs: 100
- Temperature: 0.5
- Seeds: 3 random seeds

### LA-SSL Training
- Same as SimCLR except:
- Sampler: LASSLSampler(alpha=0.5, window_size=10)

### Linear Probe
- Optimizer: SGD
- LR Grid: [0.01, 0.001, 0.0001]
- WD Grid: [1e-4, 1e-5, 1e-6]
- Epochs: 20
- Early stopping: patience=5

---

## Appendix B: Reused Components from h-e1

| Component | h-e1 File | Reuse Strategy |
|-----------|-----------|----------------|
| Dataset Loader | `dataset.py` | Direct import |
| ResNet-50 Architecture | `models.py` | Direct import |
| Augmentations | `transforms.py` | Direct import |
| AMI Computation | `metrics.py` | Direct import |
| WGA Evaluation | `evaluation.py` | Direct import |
| Optimal Hyperparameters | `03_config.md` | Read and apply |

---

*PRD v1.0 - Ready for Phase 3 Architecture Planning*
