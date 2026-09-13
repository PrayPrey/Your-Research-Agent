# Product Requirements Document: H-E1

**Hypothesis ID:** H-E1
**Type:** EXISTENCE (Proof of Concept)
**Date:** 2026-04-14
**Author:** Anonymous
**Phase:** 3 - Implementation Planning

---

## Executive Summary

This PRD defines the implementation requirements for validating hypothesis H-E1: that per-sample loss trajectory features can predict minority group membership in spuriously correlated datasets with AUROC > 0.75.

**Core Claim:** Under standard ERM training on Waterbirds, per-sample loss trajectory features (L₁, slope, variance, time-to-convergence) extracted from epochs 1-5 will predict minority group membership with AUROC > 0.75.

**Gate:** MUST_WORK - If this fails, the main hypothesis (loss trajectory divergence for spurious correlation detection) is abandoned.

---

## Problem Statement

### Background
Spurious correlations in training data cause models to rely on shortcut features, leading to poor worst-group accuracy. Current detection methods require group labels or complex interventions. We hypothesize that minority samples exhibit distinctive loss trajectory patterns during standard ERM training that can be detected without explicit group supervision.

### Opportunity
If loss trajectories can identify minority samples, this enables:
- Unsupervised detection of spurious correlation effects
- Early identification of at-risk samples
- Foundation for trajectory-based robustness methods

### Success Criteria
- **Primary:** AUROC > 0.75 for predicting minority group membership from trajectory features
- **Baseline:** Random classifier AUROC = 0.50
- **Stretch:** Match literature baseline (Gradient norm detection AUROC ≈ 0.91)

---

## Functional Requirements

### FR-1: Dataset Loading and Preprocessing

**FR-1.1: Waterbirds Dataset Loading**
- Load Waterbirds dataset (4,795 training, 1,199 validation, 5,794 test samples)
- Support WILDS package or direct download from group_DRO repository
- Preserve group labels (4 groups: bird_type × background)
- Track sample indices for per-sample loss logging

**FR-1.2: Data Preprocessing**
- Training transforms: RandomResizedCrop(224), RandomHorizontalFlip(), Normalize(ImageNet)
- Evaluation transforms: Resize(256), CenterCrop(224), Normalize(ImageNet)
- ImageNet normalization: mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]

**FR-1.3: Deterministic Evaluation Mode**
- Disable data augmentation for loss logging passes
- Use fixed batch ordering with sample index tracking
- Ensure reproducible per-sample loss computation

### FR-2: Model Architecture

**FR-2.1: ResNet-50 Baseline**
- Load torchvision ResNet-50 with ImageNet pretrained weights
- Replace final FC layer: Linear(2048, 2) for binary classification
- No architectural modifications for trajectory extraction

**FR-2.2: Model Initialization**
- Use `torchvision.models.ResNet50_Weights.IMAGENET1K_V1`
- Set random seed for reproducibility (seed=42)
- Initialize new FC layer with default PyTorch initialization

### FR-3: Training Loop

**FR-3.1: ERM Training**
- Optimizer: SGD with momentum=0.9, weight_decay=0.0001
- Learning rate: 0.001 (constant, no scheduler for PoC)
- Batch size: 128
- Epochs: 20 total

**FR-3.2: Loss Computation**
- Use CrossEntropyLoss with `reduction='none'` for per-sample losses
- Aggregate with mean for backward pass
- Track individual sample losses separately

**FR-3.3: Per-Epoch Loss Logging**
- After each training epoch (1-5), run deterministic evaluation pass
- Compute per-sample losses on full training set
- Store losses indexed by sample ID in trajectory tracker

### FR-4: Trajectory Feature Extraction

**FR-4.1: Loss Trajectory Storage**
- Maintain loss history matrix: shape (num_samples, num_epochs)
- Log losses for epochs 1-5 minimum
- Support optional smoothing (3-point moving average)

**FR-4.2: Feature Computation**
- **F1 (Initial Loss):** L₁ = loss at epoch 1
- **F2 (Slope):** (L₅ - L₁) / 4
- **F3 (Variance):** var(L_normalized) where L_normalized = L / L₁
- **F4 (Convergence Time):** First epoch where loss reaches 95% of minimum

**FR-4.3: Feature Output**
- Return feature matrix: shape (num_samples, 4)
- Support per-feature extraction for ablation analysis

### FR-5: Evaluation

**FR-5.1: AUROC Computation**
- Use sklearn LogisticRegression as classifier
- Apply 5-fold stratified cross-validation
- Compute mean and std AUROC across folds

**FR-5.2: Minority Label Definition**
- Minority groups: G2 (landbirds on water) and G4 (waterbirds on land)
- Binary labels: 1 = minority, 0 = majority
- Preserve original group labels for analysis

**FR-5.3: Per-Feature Analysis**
- Compute individual AUROC for each of 4 features
- Extract logistic regression coefficients for feature importance

### FR-6: Visualization

**FR-6.1: Required Figures**
- Gate metrics comparison: Bar chart of target vs actual AUROC
- Loss trajectory comparison: Mean ± std curves for minority vs majority
- ROC curve with AUROC annotation and random baseline

**FR-6.2: Optional Figures**
- Feature distribution: Violin plots per feature by group
- Feature importance: Coefficient bar chart

**FR-6.3: Output**
- Save all figures to `{hypothesis_folder}/figures/`
- Support PNG format at 300 DPI

### FR-7: Results Logging

**FR-7.1: Metrics Output**
- Primary AUROC with 95% confidence interval
- Per-feature AUROC scores
- Feature importance coefficients

**FR-7.2: Gate Evaluation**
- Compare AUROC against threshold (0.75)
- Output PASS/FAIL determination
- Log to verification_state.yaml

---

## Non-Functional Requirements

### NFR-1: Reproducibility
- Fixed random seed (42) for all stochastic operations
- Deterministic CUDA operations where possible
- Version-locked dependencies

### NFR-2: Performance
- Single GPU execution (select lowest memory usage GPU)
- Training completion within 30 minutes on modern GPU
- Memory usage < 16GB GPU RAM

### NFR-3: Code Quality
- Type hints for all function signatures
- Docstrings with tensor shape documentation
- Modular design for component reuse in subsequent hypotheses

### NFR-4: Logging
- Console progress for epoch completion
- Loss values logged per epoch
- Final metrics summary printed

---

## Technical Dependencies

### Python Packages
- PyTorch >= 2.0
- torchvision >= 0.15
- scikit-learn >= 1.0
- numpy >= 1.20
- matplotlib >= 3.5
- WILDS >= 2.0 (or manual download)
- tqdm (progress bars)

### Hardware
- Single NVIDIA GPU (8GB+ VRAM recommended)
- 32GB+ system RAM
- 10GB+ disk space for dataset

### External Resources
- Waterbirds dataset (~1GB)
- ImageNet pretrained weights (auto-download)

---

## Data Flow

```
[Waterbirds Dataset]
        ↓
[DataLoader with index tracking]
        ↓
[ResNet-50 ERM Training] ←→ [Per-Epoch Loss Logging]
        ↓                            ↓
[Trained Model]           [Loss Trajectory Matrix (N, 5)]
                                     ↓
                          [Feature Extraction (N, 4)]
                                     ↓
                          [Logistic Regression + CV]
                                     ↓
                          [AUROC Score + Gate Check]
```

---

## Success Metrics

| Metric | Target | Baseline | Gate |
|--------|--------|----------|------|
| AUROC | > 0.75 | 0.50 (random) | MUST_WORK |
| Training Time | < 30 min | N/A | Soft |
| Memory Usage | < 16GB | N/A | Soft |

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Trajectory features not discriminative | Medium | High (abandon hypothesis) | Multiple feature variants prepared |
| Dataset loading issues | Low | Medium | Fallback to HuggingFace |
| Memory overflow | Low | Low | Reduce batch size |
| Non-reproducible results | Low | Medium | Fixed seeds, deterministic ops |

---

## Implementation Priority

1. **P0 (Critical Path):**
   - Dataset loading with group labels
   - Per-sample loss logging
   - Trajectory feature extraction
   - AUROC evaluation

2. **P1 (Required):**
   - Visualization generation
   - Results logging
   - Gate evaluation

3. **P2 (Nice to have):**
   - Per-feature analysis
   - Moving average smoothing

---

## Appendix: Traceability to Phase 2C

| PRD Section | Phase 2C Source |
|-------------|-----------------|
| Dataset specs | Experiment Specification > Dataset |
| Model architecture | Experiment Specification > Models |
| Training protocol | Experiment Specification > Training Protocol |
| Evaluation metrics | Experiment Specification > Evaluation |
| Visualization | Experiment Specification > Visualization Requirements |
| Success criteria | Gate Condition (AUROC > 0.75) |

---

*Generated by Phase 3 Implementation Planning*
*Source: h-e1/02c_experiment_brief.md*
*Next: Architecture Design*
