# Product Requirements Document: h-e1 Weight-Based Depth Classification

**Hypothesis:** h-e1 (Existence)  
**Date:** 2026-04-21  
**Author:** Anonymous
**Status:** Draft  

---

## Executive Summary

This PRD defines the implementation requirements for validating hypothesis h-e1: testing whether layer-wise weight norm statistics can classify pretrained CNN architectural depth (shallow ≤34 layers vs deep ≥50 layers) with ≥70% accuracy.

**Success Criteria:** Test accuracy ≥70% on 4 held-out models (MUST_WORK gate)

**Scope:** Single experiment validating weight-based depth classification using 20 pretrained ImageNet models.

---

## Problem Statement

### Context
Previous correlation analysis (Run 3) showed promising signal (|ρ| = 0.859) but failed statistical significance due to small sample size (n=5). Binary classification with n=20 models should provide clearer validation.

### Hypothesis
Under the scope of pretrained ImageNet CNNs, if we extract layer-wise weight norm statistics (mean, std, min, max of Frobenius norms) and train a binary classifier on 16 models, then test accuracy on 4 held-out models will exceed 70%, because weight distributions encode architectural depth through training history.

### Requirements Driver
Gate Type: MUST_WORK - If accuracy <70%, entire workflow stops.

---

## Functional Requirements

### FR-1: Dataset Preparation
**Priority:** P0 (Critical)

Load 20 pretrained ImageNet CNN models from PyTorch torchvision:

**Shallow Models (≤34 layers, n=10):**
- resnet18, resnet34
- vgg11, vgg13, vgg16, vgg19
- alexnet, squeezenet1_0
- mobilenet_v2, densenet121

**Deep Models (≥50 layers, n=10):**
- resnet50, resnet101, resnet152
- densenet161, densenet169, densenet201
- wide_resnet50_2, wide_resnet101_2
- resnext50_32x4d, resnext101_32x8d

**Acceptance Criteria:**
- All 20 models loaded successfully via `torchvision.models.{model_name}(pretrained=True)`
- Models auto-download to `~/.cache/torch/hub/` on first use
- No manual file downloads required

### FR-2: Feature Extraction
**Priority:** P0 (Critical)

Extract layer-wise Frobenius norm statistics from each model:

**Process:**
1. Iterate through `model.named_parameters()`
2. Filter for trainable weight parameters (`'weight' in name and param.requires_grad`)
3. Compute Frobenius norm per layer: `torch.norm(param.data, p='fro').item()`
4. Aggregate statistics: mean, std, min, max across all layer norms

**Output:** Feature vector of shape (4,) per model: [mean, std, min, max]

**Acceptance Criteria:**
- Feature extraction works for all 20 models
- Feature vectors have consistent shape (4,)
- All layer norms are positive non-zero values

### FR-3: Data Splitting
**Priority:** P0 (Critical)

Stratified 80/20 train-test split:
- Training: 16 models (8 shallow + 8 deep)
- Testing: 4 models (2 shallow + 2 deep)

**Configuration:**
- Stratification: Maintain class balance in both splits
- Random seed: 42 (reproducibility)
- Method: `sklearn.model_selection.train_test_split(test_size=0.2, stratify=y, random_state=42)`

**Acceptance Criteria:**
- Training set: 16 samples (8 per class)
- Test set: 4 samples (2 per class)
- Class balance maintained in both splits

### FR-4: Feature Normalization
**Priority:** P0 (Critical)

Apply StandardScaler normalization:
- Fit scaler on training features
- Transform training features (mean=0, std=1)
- Transform test features using same scaler

**Rationale:** Weight magnitudes vary by orders of magnitude (10³-10⁴) across architectures

**Acceptance Criteria:**
- Training features: mean ≈ 0, std ≈ 1
- Test features: transformed using training statistics
- No data leakage (test data not used in scaler fitting)

### FR-5: Binary Classification
**Priority:** P0 (Critical)

Train logistic regression classifier:

**Configuration:**
- Model: `sklearn.linear_model.LogisticRegression`
- Solver: lbfgs (efficient for small datasets)
- Regularization: L2, C=1.0 (inverse regularization strength)
- Max iterations: 1000 (ensure convergence)
- Random state: 42 (reproducibility)

**Input:** Normalized 4-feature vectors  
**Output:** Binary prediction (0=shallow, 1=deep)

**Acceptance Criteria:**
- Classifier trains without convergence warnings
- Training completes in <5 seconds
- Model produces probability estimates

### FR-6: Evaluation Metrics
**Priority:** P0 (Critical)

**Primary Metric (Gate Condition):**
- Test Accuracy: correct_predictions / total_predictions
- Target: ≥70%
- Baseline: 50% (random guessing)

**Secondary Metrics:**
- Confusion Matrix: TP, FP, TN, FN counts
- Per-Class Precision, Recall, F1-score
- Training Accuracy: overfitting check

**Acceptance Criteria:**
- Test accuracy computed on held-out 4 models
- Gate status clearly marked (PASS ≥70%, FAIL <70%)
- Training accuracy reported for overfitting assessment

### FR-7: Visualization
**Priority:** P1 (High)

Generate 5 analysis figures:

1. **Gate Metrics Comparison** (Mandatory)
   - Bar chart: Baseline (50%) vs Actual vs Target (70%)
   - Horizontal line at 70% threshold
   - Color: Red (fail <70%), Green (pass ≥70%)

2. **Confusion Matrix Heatmap**
   - 2×2 matrix with counts and percentages
   - Annotated cells

3. **Feature Distribution Comparison**
   - Box plots for 4 features (mean, std, min, max)
   - Separate distributions: shallow vs deep

4. **Feature Importance**
   - Bar chart of logistic regression coefficients
   - Shows which statistics contribute most

5. **Training vs Test Accuracy**
   - Bar chart comparing train/test accuracy
   - Overfitting indicator

**Output:** All figures saved to `h-e1/figures/`

**Acceptance Criteria:**
- Gate metrics figure generated and saved
- All 5 figures use consistent color scheme
- Figures are publication-quality (300 DPI)

### FR-8: Control Experiments
**Priority:** P2 (Medium)

**P2: Within-Family Accuracy**
- Train classifiers on single families (ResNet-only, VGG-only, DenseNet-only)
- Target: ≥65% accuracy
- Purpose: Test if depth signal exists within family (not just across families)

**P3: Random Labels**
- Train classifier with shuffled labels
- Target: ≤55% accuracy (near random baseline)
- Purpose: Sanity check - ensure signal is real, not spurious

**Acceptance Criteria:**
- P2 results reported per family
- P3 confirms no learning on random labels
- Control results included in final report

---

## Non-Functional Requirements

### NFR-1: Reproducibility
- Random seed: 42 (all stochastic operations)
- Deterministic feature extraction (no randomness)
- Environment: Python 3.8+, PyTorch 1.10+, sklearn 0.24+

### NFR-2: Performance
- Total execution time: <10 minutes (feature extraction + training)
- Model loading: Auto-download on first run (cached thereafter)
- Memory: Fits on single GPU (models loaded sequentially)

### NFR-3: Error Handling
- Graceful handling of model loading failures
- Clear error messages for feature extraction issues
- Validation checks for feature vector shapes

### NFR-4: Logging
- Print feature extraction progress (1-20)
- Log training start/completion
- Display final metrics clearly

---

## Data Specifications

### Input Data
- **Source:** PyTorch torchvision pretrained models
- **Format:** PyTorch model objects
- **Access:** `torchvision.models.{model_name}(pretrained=True)`
- **Storage:** Auto-cached in `~/.cache/torch/hub/`

### Output Data
- **Features:** NumPy arrays (20, 4) - 20 models × 4 statistics
- **Labels:** NumPy array (20,) - binary labels (0=shallow, 1=deep)
- **Predictions:** NumPy array (4,) - test set predictions
- **Metrics:** Python dict with accuracy, confusion matrix, classification report

### Intermediate Artifacts
- `h-e1/features.npy` - Extracted features
- `h-e1/labels.npy` - Binary labels
- `h-e1/scaler.pkl` - Fitted StandardScaler
- `h-e1/classifier.pkl` - Trained LogisticRegression model

---

## Success Criteria

### Primary Success (MUST_WORK Gate)
✅ **Test accuracy ≥ 70%** on 4 held-out models

### Secondary Success
- Mechanism verification: All 4 indicators TRUE
  - Features extracted for 20 models
  - Layer norms valid (non-zero)
  - Classifier trained successfully
  - Effect detected (accuracy > 50%)

### Failure Scenarios
- Test accuracy 50-70%: Mechanism works but hypothesis not supported (negative result)
- Test accuracy ≤50%: Mechanism failed, no discriminative power
- Code error: Debug and fix

---

## Dependencies

### External Libraries
- **PyTorch:** 1.10+ (model loading, tensor operations)
- **torchvision:** 0.11+ (pretrained models)
- **scikit-learn:** 0.24+ (classification, preprocessing, metrics)
- **NumPy:** 1.20+ (array operations)
- **Matplotlib:** 3.3+ (visualization)

### System Requirements
- Python: 3.8+
- Disk space: ~5GB (model cache)
- RAM: 8GB minimum
- GPU: Optional (CPU sufficient for this experiment)

### Phase Dependencies
- **Prerequisite:** Phase 2C completed (02c_experiment_brief.md exists)
- **Blocking:** None (foundation hypothesis)
- **Successor:** Phase 4 implementation

---

## Constraints and Assumptions

### Constraints
- Sample size: Fixed at n=20 (available pretrained models)
- Train-test split: Fixed 80/20 (small sample size)
- Single random seed: 42 (no multi-seed validation for EXISTENCE PoC)

### Assumptions
- All torchvision models use standard ImageNet 1K training
- Weight statistics are architecture-invariant (work across ResNet/VGG/DenseNet)
- Frobenius norm captures meaningful depth signal
- Linear classifier sufficient for binary depth separation

---

## Out of Scope

- Multi-class depth classification (only binary: shallow vs deep)
- Custom-trained models (only pretrained ImageNet models)
- Cross-validation (single 80/20 split sufficient for EXISTENCE)
- Hyperparameter tuning (default sklearn settings)
- Model interpretation beyond feature importance
- Deployment or production considerations

---

## Appendix: Traceability

| Requirement | Source Document | Section |
|-------------|-----------------|---------|
| Dataset (20 models) | 02c_experiment_brief.md | Dataset |
| Feature extraction | 02c_experiment_brief.md | Models → Proposed Model |
| Success criterion (70%) | 02c_experiment_brief.md | Evaluation |
| Control experiments | 02c_experiment_brief.md | Evaluation |
| Baseline (50%) | 02c_experiment_brief.md | Baseline & Comparison |
| Gate type (MUST_WORK) | 02b_context.md | Gate Information |

---

**Document Version:** 1.0  
**Last Updated:** 2026-04-21  
**Next Phase:** Phase 3 - Architecture Design
