# Product Requirements Document: h-m2

**Date:** 2026-08-29  
**Hypothesis:** CNNs show larger temporal gaps than Vision Transformers (Δ_ResNet > Δ_ViT by ≥2 epochs) due to architectural inductive bias differences  
**Type:** MECHANISM  
**Gate:** SHOULD_WORK

---

## Objective

Validate whether CNN inductive biases create larger temporal gaps between spurious and core feature convergence compared to Vision Transformers.

---

## Success Criteria

**Primary Gate:**
- Statistical significance: p < 0.05 (independent t-test)
- Effect size: Δ_ResNet - Δ_ViT ≥ 2 epochs

Where:
- Δ_ResNet = E_core(ResNet-50) - E_spurious(ResNet-50)
- Δ_ViT = E_core(ViT-B/16) - E_spurious(ViT-B/16)

**PoC Pass Condition:**
1. Code runs without error
2. Δ_ResNet > Δ_ViT (any margin)

---

## Requirements

### Functional Requirements

**FR1: Architecture Comparison**
- Train ResNet-50 and ViT-B/16 from scratch (no pretrained weights)
- Identical optimizer configuration (SGD + momentum 0.9)
- Architecture-specific hyperparameters (learning rate, batch size)

**FR2: Temporal Gap Measurement**
- Convergence detection: gradient norm < 10% of peak for 3 consecutive epochs
- Track E_spurious and E_core separately per architecture
- Compute Δ per architecture per seed

**FR3: Ablation Training**
- Spurious-only model: masks out core features
- Core-only model: masks out spurious features
- 2 architectures × 2 ablation types = 4 model variants

**FR4: Statistical Validation**
- 10 random seeds per experiment
- Independent t-test on (Δ_ResNet, Δ_ViT) pairs

**FR5: Dataset Support**
- Primary: Waterbirds (WILDS package)
- Secondary: CelebA (WILDS or torchvision)
- Standard splits: train/val/test

### Non-Functional Requirements

**NFR1: Reproducibility**
- Seed control for model initialization, data shuffling
- Logged hyperparameters per run

**NFR2: Efficiency**
- Batch size tuning for GPU utilization
- Mixed precision training (optional)

**NFR3: Monitoring**
- Log gradient norms per epoch
- Track convergence status per model

---

## Technical Specifications

### Models

**ResNet-50:**
- Source: timm library (`resnet50`)
- Parameters: ~25.6M
- Input: (B, 3, 224, 224)
- Output: (B, 2) logits

**ViT-B/16:**
- Source: timm library (`vit_base_patch16_224`)
- Parameters: ~86M
- Input: (B, 3, 224, 224)
- Output: (B, 2) logits

### Training Protocol

**Shared Hyperparameters:**
- Optimizer: SGD
- Momentum: 0.9
- Epochs: 50
- Loss: CrossEntropyLoss
- Seeds: 10

**Architecture-Specific:**

| Parameter | ResNet-50 | ViT-B/16 |
|-----------|-----------|----------|
| Learning rate | 0.001 | 0.0003 |
| Batch size | 256 | 512 |
| Weight decay | 1e-4 | 0.05 |
| Schedule | Cosine (T_max=50) | Cosine (T_max=50) |

### Datasets

**Waterbirds:**
- Train: 4,795 images
- Val: 1,199 images
- Test: 5,794 images
- Spurious correlation: 95%+ background-label

**CelebA:**
- Train: ~162,770 images
- Val: ~19,867 images
- Test: ~19,962 images
- Spurious correlation: gender-attribute

**Preprocessing:**
- Resize: 224×224
- Normalization: ImageNet statistics (mean=[0.485,0.456,0.406], std=[0.229,0.224,0.225])
- Augmentation: Random horizontal flip (p=0.5)

---

## Evaluation Metrics

**Primary:**
- Temporal gap Δ (epochs): E_core - E_spurious

**Secondary:**
- Overall accuracy: Binary classification accuracy on test set
- Worst-group accuracy: min(accuracy per {target × spurious} group)

**Statistical Test:**
- Independent samples t-test on (Δ_ResNet, Δ_ViT) across 10 seeds
- Null: Δ_ResNet = Δ_ViT
- Alternative: Δ_ResNet > Δ_ViT
- Significance: p < 0.05

---

## Visualization Requirements

**Mandatory:**
- Gate metrics comparison: Target vs actual bar chart

**Recommended:**
1. Temporal gap comparison: Δ_ResNet vs Δ_ViT (mean ± std)
2. Convergence curves: Gradient norms over epochs (spurious/core × architecture)
3. Per-seed scatter: (Δ_ResNet, Δ_ViT) pairs with diagonal line
4. Architecture performance: Worst-group accuracy comparison

All figures save to `h-m2/figures/`.

---

## Dependencies

**Prerequisites:**
- h-e1 validated (temporal ordering exists)

**Python Libraries:**
- torch, timm (models)
- wilds (datasets)
- torchmetrics, sklearn (evaluation)
- matplotlib, seaborn (visualization)

---

## Risk Assessment

**Risk Level:** MEDIUM  
**Rationale:** SHOULD_WORK gate - failure does not block Phase 5

**Technical Risks:**
1. ViT may need larger batch sizes than GPU memory allows → fallback to smaller ViT variant
2. Waterbirds dataset download may fail → use CelebA as primary
3. Convergence may not occur within 50 epochs → extend to 100 epochs

**Mitigation:**
- Batch size: Use gradient accumulation if memory-constrained
- Dataset: Test download in environment setup phase
- Epochs: Monitor convergence in pilot run, adjust if needed

---

## Timeline Estimate

**Estimated Duration:** 2 weeks  
**Breakdown:**
- Environment setup: 1 day
- Dataset download/verification: 1 day
- Implementation: 5 days
- Validation (10 seeds × 2 architectures × 2 ablations): 7 days

---

## Implementation Notes

**Code Reuse from h-e1:**
- Convergence detection logic (gradient norm tracking)
- Ablation training framework (spurious-only, core-only)
- Statistical validation (t-test implementation)

**New Components:**
- ViT-B/16 integration (timm API)
- Architecture-specific hyperparameter management
- Dual-architecture training pipeline

**Quality Checks:**
- Unit test: Convergence detection function
- Integration test: Ablation model forward pass
- End-to-end test: Single-seed run completes without error

---

## Appendix: Traceability

| Requirement | Source |
|-------------|--------|
| ResNet-50, ViT-B/16 | 02c_experiment_brief.md (timm library) |
| Waterbirds, CelebA | 02c_experiment_brief.md (WILDS package) |
| Convergence detection | h-e1 validation report (gradient norm method) |
| Hyperparameters | 02c_experiment_brief.md (group_DRO + timm defaults) |
| Statistical test | 02b_context.md (Test 7, independent t-test) |
| Gate threshold | 02b_context.md (Δ≥2 epochs, p<0.05) |

---

**Status:** READY FOR IMPLEMENTATION  
**Next Phase:** Phase 3 - Architecture/Logic/Config Design
