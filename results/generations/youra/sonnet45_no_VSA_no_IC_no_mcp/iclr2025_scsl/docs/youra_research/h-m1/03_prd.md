# Product Requirements Document (PRD)

**Hypothesis ID**: h-m1  
**Generated**: 2026-08-24  
**Phase**: 3 (Implementation Planning)  
**Tier**: 1.5 (Simple-to-Moderate)  
**Budget**: 350-550 tokens

---

## Executive Summary

Implement gradient flow measurement experiment to test whether BN amplifies early spurious learning via batch-level statistics. Measures gradient magnitude to spurious vs core features during epochs 1-20 of ResNet-BN and ResNet-LN training on Waterbirds dataset. Reuses 80% of h-e1 codebase (data loader, models, training loop). Adds backward hooks to capture gradient norms on majority/minority groups.

---

## User Story

**As a** researcher investigating spurious correlation learning mechanisms  
**I want to** measure gradient flow to spurious vs core features during early training  
**So that** I can test whether BN's batch-level statistics amplify spurious correlation learning compared to LN's instance-level statistics

---

## Problem Statement

h-e1 validated that ResNet-BN shows 9.41pp higher worst-group gap than ResNet-LN at 90% average accuracy (p < 0.001). The mechanism causing this gap is unknown. This experiment tests the hypothesis that BN amplifies batch-level spurious correlations during early training, making spurious features easier to learn than core features.

---

## Requirements

### Functional Requirements

#### FR1: Data Loading
- **FR1.1**: Load Waterbirds dataset with group labels (4 groups: landbird-land, landbird-water, waterbird-land, waterbird-water)
- **FR1.2**: Apply standard ImageNet normalization (mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
- **FR1.3**: Reuse h-e1 data loader (no modifications)
- **FR1.4**: Cache dataset at ./data/waterbirds/ to avoid re-downloading

#### FR2: Model Definition
- **FR2.1**: Implement ResNet-18-BN (torchvision ResNet-18 with BatchNorm2d)
- **FR2.2**: Implement ResNet-18-LN (ResNet-18 with LayerNorm replacement)
- **FR2.3**: Use He normal initialization (kaiming_normal with fan_out, relu mode)
- **FR2.4**: Reuse h-e1 model definitions (no modifications)
- **FR2.5**: Output 2 classes (landbird, waterbird)

#### FR3: Gradient Measurement Infrastructure
- **FR3.1**: Register backward hooks on normalization layers (BN and LN)
- **FR3.2**: Capture gradient norms during backward pass
- **FR3.3**: Log per-layer gradient magnitudes (conv1, first norm, last norm)
- **FR3.4**: Compute mean gradient norm over batch
- **FR3.5**: Remove hooks after epoch 20 (reduce overhead)

#### FR4: Group-Stratified Gradient Analysis
- **FR4.1**: Split validation set into majority group (spurious-aligned: groups 0,3) and minority group (spurious-misaligned: groups 1,2)
- **FR4.2**: Compute loss separately on majority and minority samples
- **FR4.3**: Measure gradient magnitude for each group via backward hooks
- **FR4.4**: Calculate gradient ratio: grad_majority / grad_minority
- **FR4.5**: Log gradient ratio per epoch (epochs 1-20)

#### FR5: Training Loop
- **FR5.1**: Train both architectures for 100 epochs (measure gradients on epochs 1-20 only)
- **FR5.2**: Use SGD optimizer (lr=0.01, momentum=0.9, weight_decay=1e-4)
- **FR5.3**: Use CrossEntropyLoss (no class reweighting)
- **FR5.4**: Train with 10 seeds (0-9) for statistical power
- **FR5.5**: Log metrics per epoch: average accuracy, worst-group accuracy, per-group accuracy, worst-group gap
- **FR5.6**: Add gradient metrics (epochs 1-20): grad_majority_norm, grad_minority_norm, grad_ratio, conv1_grad_norm, first_norm_grad_norm, last_norm_grad_norm

#### FR6: Statistical Analysis
- **FR6.1**: Compute mean gradient ratio per architecture across 10 seeds (epochs 1-20)
- **FR6.2**: Perform independent t-test (BN gradient ratios vs LN gradient ratios)
- **FR6.3**: Compute effect size (Cohen's d)
- **FR6.4**: Evaluate success criterion: BN ratio ≥ 20% higher than LN ratio, p < 0.05, Cohen's d ≥ 0.5
- **FR6.5**: Output statistical test results (t-statistic, p-value, Cohen's d, mean gradient ratios)

#### FR7: Visualization
- **FR7.1**: Plot gradient ratio over time (epochs 1-20): two lines (BN, LN) with ±1 std shaded region
- **FR7.2**: Plot gradient ratio comparison (box plot): 10 points per architecture
- **FR7.3**: Plot per-layer gradient norms (heatmap): conv1, first_norm, last_norm for BN and LN

### Non-Functional Requirements

#### NFR1: Code Reuse
- **NFR1.1**: Reuse ≥80% of h-e1 codebase (data_loader.py, models.py, train.py, evaluate.py)
- **NFR1.2**: New components (gradient hooks, group analysis) <200 LoC each
- **NFR1.3**: No code duplication (use functions/modules)

#### NFR2: Reproducibility
- **NFR2.1**: Set all RNG seeds before model/data creation (torch, numpy, random)
- **NFR2.2**: Enable cudnn.deterministic
- **NFR2.3**: Gradient measurement must not alter training dynamics (hooks are read-only)

#### NFR3: Performance
- **NFR3.1**: Training time ≤ 12 hours/seed on CPU (gradient hooks add ≤20% overhead)
- **NFR3.2**: GPU acceleration supported (CUDA if available)
- **NFR3.3**: Hooks removed after epoch 20 (prevent memory leak)

#### NFR4: Documentation
- **NFR4.1**: All functions have docstrings (Args, Returns, Description)
- **NFR4.2**: README explains how to run experiment
- **NFR4.3**: Comments explain non-obvious gradient measurement logic

---

## Acceptance Criteria

### AC1: Gradient Measurement
- [ ] Backward hooks capture non-zero gradient norms for all normalization layers
- [ ] Majority/minority group split is correct (groups 0,3 vs 1,2)
- [ ] Gradient ratio computed correctly (no division by zero)
- [ ] Gradient metrics logged for epochs 1-20 only

### AC2: Training
- [ ] Both architectures (BN, LN) train for 100 epochs across 10 seeds (20 runs total)
- [ ] All runs complete without NaN gradients or CUDA errors
- [ ] Training metrics CSV includes gradient columns (grad_majority_norm, grad_minority_norm, grad_ratio)
- [ ] Hooks removed after epoch 20 (verified via memory profiling)

### AC3: Statistical Test
- [ ] Mean gradient ratio computed for BN and LN (epochs 1-20)
- [ ] Independent t-test performed (10 BN samples vs 10 LN samples)
- [ ] Effect size (Cohen's d) computed
- [ ] Success/falsification criterion evaluated

### AC4: Visualization
- [ ] Gradient ratio over time plot shows two lines (BN, LN) with shaded std regions
- [ ] Box plot shows 10 points per architecture
- [ ] Heatmap shows per-layer gradients for epochs 1-20

### AC5: Code Quality
- [ ] All modules compile without syntax errors
- [ ] All imports resolve correctly
- [ ] Type consistency (tensor shapes match specifications)
- [ ] ≥80% code reuse from h-e1 verified

---

## Out of Scope

- Custom autograd functions (use standard backward hooks)
- Batch-level spurious correlation measurement (focus on gradient flow only)
- Gradient variance analysis (focus on mean gradient magnitude)
- Model checkpointing (optional; not required for analysis)
- Hyperparameter tuning (use fixed h-e1 hyperparameters)

---

## Constraints

### Technical Constraints
- Must use PyTorch ≥1.10 (backward hook API)
- Must use wilds library for Waterbirds dataset
- Must reuse h-e1 model definitions (no architectural changes)
- Gradient measurement limited to epochs 1-20 (computational efficiency)

### Resource Constraints
- Training time: ~200 hours on CPU (acceptable for single-machine run)
- GPU optional but recommended (~10 hours with GPU)
- Storage: ~500 MB dataset + ~1 MB metrics
- No model checkpointing required (saves ~900 MB)

### Design Constraints
- Majority/minority group definition fixed (groups 0,3 vs 1,2)
- Gradient ratio defined as grad_majority / grad_minority (not core/spurious)
- Independent t-test (not paired; BN and LN are independent models)
- Statistical significance threshold: p < 0.05

---

## Dependencies

### External Dependencies
- torch >= 1.10
- torchvision >= 0.11
- wilds >= 2.0
- numpy >= 1.20
- scipy >= 1.7
- matplotlib >= 3.4
- tqdm >= 4.60

### Internal Dependencies
- h-e1 data_loader.py (Waterbirds dataset loading)
- h-e1 models.py (ResNet-18-BN, ResNet-18-LN)
- h-e1 train.py (training loop scaffold)
- h-e1 evaluate.py (per-group accuracy computation)

### Prerequisite Validation
- h-e1 must be VALIDATED before h-m1 implementation begins
- h-e1 codebase must be available for reuse (files readable)

---

## Success Metrics

### Hypothesis Validation Metrics
- **Primary**: Gradient ratio difference (BN - LN) ≥ 20% AND p < 0.05 AND Cohen's d ≥ 0.5
- **Secondary**: Visual separation in gradient ratio trajectories (epochs 1-20)

### Implementation Quality Metrics
- Code reuse ≥ 80%
- New code ≤ 400 LoC
- Training completion rate: 100% (20/20 runs succeed)
- Zero NaN gradients or CUDA OOM errors

### Reproducibility Metrics
- Same-seed runs produce identical gradient ratios (deterministic)
- Gradient measurement does not alter final worst-group gap (validated against h-e1)

---

## Risks and Mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Gradient measurement noise (high variance) | Medium | Medium | Average over 10 seeds, 5-epoch smoothing |
| Spurious/core feature proxy invalid | Medium | High | Validate: majority/minority gradient should differ |
| Gradient vanishing in early layers | Low | Medium | Use gradient norm (not raw), log scale if needed |
| Computational overhead (hooks) | Low | Low | Measure on validation set only, remove after epoch 20 |
| h-e1 code unavailable | Low | Low | h-e1 already validated in Phase 4 |

---

## Timeline

**Estimated Implementation Time**: 2-3 days (with 80% code reuse)

- Day 1: Implement gradient hooks, group-stratified analysis
- Day 2: Integrate into training loop, run 20 experiments (or 10 hours on GPU)
- Day 3: Statistical analysis, visualization, validation

**Validation Time**: ~200 hours (CPU) or ~10 hours (GPU)

---

## Deliverables

1. **Code**:
   - gradient_hooks.py (backward hook registration)
   - group_gradients.py (majority/minority gradient computation)
   - train_with_gradients.py (training loop with gradient logging)
   - analyze_gradients.py (statistical test)
   - plot_gradients.py (visualization)

2. **Results**:
   - training_metrics.csv (extended with gradient columns)
   - gradient_analysis.txt (statistical test results)
   - gradient_ratio_over_time.png
   - gradient_ratio_boxplot.png
   - layer_gradient_heatmap.png

3. **Documentation**:
   - README.md (how to run experiment)
   - Docstrings (all functions)
   - Comments (non-obvious gradient logic)

---

## Approval

**Status**: APPROVED for Phase 3 implementation planning  
**Reviewed**: 2026-08-24  
**Next Phase**: Architecture design (03_architecture.md)
