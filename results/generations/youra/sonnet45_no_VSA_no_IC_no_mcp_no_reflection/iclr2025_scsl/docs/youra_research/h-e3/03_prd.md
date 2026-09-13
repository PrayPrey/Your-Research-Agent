# Product Requirements Document (PRD)

**Date:** 2026-08-28
**Hypothesis:** h-e3
**Author:** Anonymous

---

## Executive Summary

Implement GradCAM temporal ratio tracking system to validate hypothesis h-e3: "GradCAM temporal ratio R_temporal(t) decreases monotonically from epoch 5 to 50 (Kendall τ < -0.7, p < 0.05)". This extends h-e1's gradient convergence findings to continuous saliency-based monitoring.

**Core Deliverable:** PyTorch implementation of GradCAM attribution tracking during training on Waterbirds dataset, producing R_temporal(t) measurements every 5 epochs to demonstrate monotonic decrease from spurious to core features.

**Success Criteria:** R_temporal downward trend observed with Delta ≥ 0.1 between epoch 5 and epoch 50 (PoC validation for SHOULD_WORK gate).

---

## Problem Statement

### Research Question
Does visual attention (measured by GradCAM saliency) shift from spurious to core features during training in a continuous monotonic pattern?

### Context
- Prerequisite h-e1 validated temporal ordering via gradient convergence: E_spurious=13, E_core=17
- h-e3 extends to continuous monitoring using GradCAM attribution maps
- SHOULD_WORK gate: Supporting evidence, failure does not block pipeline

### Constraints
- PoC scope: Waterbirds only (single seed)
- Budget: LIGHT tier (≤15 tasks)
- No architectural modification to ResNet-50
- Reuse h-e1 training protocol for controlled comparison

---

## Functional Requirements

### FR-1: Dataset Preparation
**Priority:** P0
**Description:** Load and preprocess Waterbirds dataset from WILDS benchmark
**Acceptance Criteria:**
- WILDS Waterbirds dataset downloaded and cached
- Standard splits: 4795 train, 1199 val, 5794 test
- Preprocessing: Resize(224×224), Normalize(ImageNet mean/std)
- Training augmentation: RandomHorizontalFlip, ColorJitter

### FR-2: Baseline Model Training
**Priority:** P0
**Description:** Train ResNet-50 baseline with standard ERM protocol
**Acceptance Criteria:**
- ResNet-50 pretrained on ImageNet, final layer replaced (2 classes)
- Optimizer: SGD (momentum=0.9, weight_decay=1e-4)
- Learning rate: 0.001, StepLR decay at epochs [30, 60]
- Batch size: 128, Epochs: 50
- Loss: CrossEntropyLoss
- Single seed (seed=0) for PoC

### FR-3: GradCAM Temporal Ratio Tracker
**Priority:** P0
**Description:** Implement GradCAM attribution tracking system
**Acceptance Criteria:**
- PyTorch Captum LayerGradCam integration at ResNet-50 layer4
- Temporal ratio: R_temporal(t) = A_spurious / (A_spurious + A_core)
- Attribution computation: Sum of absolute GradCAM values per region
- Tracking schedule: Every 5 epochs (epochs 5, 10, 15, ..., 50)
- Sample 100 validation batches per epoch for efficiency

### FR-4: Region Mask Definition
**Priority:** P0
**Description:** Define spurious and core regions for attribution separation
**Acceptance Criteria:**
- Spurious mask: Background segmentation (WILDS metadata)
- Core mask: Bird bounding box or segmentation
- Fallback: GradCAM peak activation region as core proxy
- Masks compatible with (B, H, W) GradCAM output shape

### FR-5: Temporal Ratio Computation
**Priority:** P0
**Description:** Compute R_temporal per epoch during training
**Acceptance Criteria:**
- Per-sample attribution: A_spurious, A_core from masked GradCAM
- Batch aggregation: Average R_temporal across 100 sampled batches
- Storage: R_temporal values saved per epoch for analysis
- Numerical stability: epsilon=1e-8 in denominator

### FR-6: PoC Validation Metrics
**Priority:** P0
**Description:** Evaluate PoC success criteria
**Acceptance Criteria:**
- Monotonicity check: Visual inspection of R_temporal(t) plot
- Effect direction: R_temporal(epoch 5) > R_temporal(epoch 50)
- Delta threshold: Delta ≥ 0.1 (10% decrease)
- Sanity check: Worst-group accuracy ≥ 70% (model convergence)

### FR-7: Visualization Generation
**Priority:** P1
**Description:** Generate figures for validation report
**Acceptance Criteria:**
- R_temporal vs Epoch line plot (mandatory)
- GradCAM heatmap evolution at epochs 5, 25, 50
- Worst-group accuracy vs epoch plot
- All figures saved to h-e3/figures/

### FR-8: Validation Report
**Priority:** P0
**Description:** Generate 04_validation.md report
**Acceptance Criteria:**
- PoC pass condition documented
- R_temporal trend analysis
- Delta calculation: R_temporal(5) - R_temporal(50)
- Gate result: PASS/PARTIAL/FAIL
- Figures embedded in report

---

## Non-Functional Requirements

### NFR-1: Computational Efficiency
- GradCAM computation batched for GPU utilization
- Tracking limited to 100 batches per epoch
- Total runtime: ~2 hours for 50 epochs (estimated)

### NFR-2: Reproducibility
- Fixed seed: seed=0
- Deterministic training (torch.manual_seed)
- Environment specification in requirements.txt

### NFR-3: Code Quality
- Modular design: Separate GradCAM tracker class
- Type hints for function signatures
- Docstrings for core mechanisms

### NFR-4: Maintainability
- Clear separation: training loop / GradCAM tracking
- Configuration-based hyperparameters
- Logging of R_temporal per epoch

---

## Data Specifications

### Input Data
**Dataset:** Waterbirds (WILDS benchmark)
- Source: WILDS library (get_dataset)
- Format: Images (224×224×3), binary labels, group metadata
- Size: ~1.2GB download
- Cache path: ./data/waterbirds

### Derived Data
**GradCAM Attributions:**
- Format: (B, 1, H, W) activation maps
- Type: float32
- Storage: Per-epoch aggregates (R_temporal values)

### Output Data
**Temporal Ratios:**
- Format: CSV or JSON (epoch, R_temporal)
- Epochs: 10 values (epochs 5, 10, ..., 50)
- Example: {5: 0.78, 10: 0.72, ..., 50: 0.45}

**Figures:**
- R_temporal plot: PNG, 1200×800
- GradCAM heatmaps: PNG, 3 samples × 3 epochs
- Accuracy plot: PNG, 1200×800

---

## Dependencies

### External Libraries
- pytorch >= 2.0.0
- torchvision >= 0.15.0
- captum >= 0.6.0 (GradCAM implementation)
- wilds >= 2.0.0 (Waterbirds dataset)
- torchmetrics >= 0.11.0
- matplotlib >= 3.5.0
- numpy >= 1.23.0
- scipy >= 1.10.0 (for Kendall tau in full validation)

### Prerequisite Artifacts (h-e1)
- Training protocol: SGD + StepLR schedule
- Dataset: CMNIST (reference, not reused)
- Validation method: Gradient convergence (cross-method comparison)

### Hardware Requirements
- GPU: 1× NVIDIA GPU with 8GB+ VRAM (e.g., RTX 2080, V100)
- Storage: 5GB (dataset + checkpoints)
- RAM: 16GB

---

## Success Criteria

### PoC Pass Condition (SHOULD_WORK Gate)
1. ✅ Code runs without error
2. ✅ R_temporal(epoch 5) > R_temporal(epoch 50)
3. ✅ Delta ≥ 0.1 (10% decrease)
4. ✅ Downward trend observed in plot

### Extended Validation (If PoC Passes)
- Kendall τ < -0.7, p < 0.05 (statistical test)
- Multi-seed validation (10 seeds)
- Cross-method consistency with h-e1 (Spearman ρ > 0.7)

### Failure Modes
- No monotonic decrease → PARTIAL (report findings)
- Delta < 0.1 → PARTIAL (weak evidence)
- Runtime error → FAIL (implementation issue)

---

## Out of Scope

- CelebA and NICO++ datasets (deferred to full validation)
- Multi-seed statistical testing (PoC uses single seed)
- Alternative attribution methods (Integrated Gradients, SHAP)
- Architectural modifications to ResNet-50
- DRO or other debiasing training methods

---

## Timeline & Milestones

**Phase 3:** Implementation Planning (current)
**Phase 4:** Coding & PoC Validation
- Milestone 1: Dataset + environment setup
- Milestone 2: GradCAM tracker implementation
- Milestone 3: Training run + R_temporal tracking
- Milestone 4: Validation report + figures

**Estimated Effort:** 2-3 hours (implementation) + 2 hours (training) = ~5 hours total

---

## Appendix

### Reference Implementations
- **pytorch/captum:** LayerGradCam API for attribution extraction
- **kohpangwei/group_DRO:** Waterbirds benchmark training protocol
- **h-e1:** Gradient convergence method for cross-validation

### Key Design Decisions
1. **PyTorch Captum over custom GradCAM:** Battle-tested, GPU-optimized
2. **Layer4 target layer:** Deepest conv features for best attribution quality
3. **100 batch sampling:** Balance between stability and computational cost
4. **Every 5 epochs:** Sufficient granularity for monotonic trend detection
5. **Single seed PoC:** Direction check only, statistical test in full validation

---

## Revision History

| Date | Version | Changes | Author |
|------|---------|---------|--------|
| 2026-08-28 | 1.0 | Initial PRD from Phase 2C experiment brief | Anonymous |
