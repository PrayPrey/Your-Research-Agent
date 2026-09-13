# Product Requirements Document (PRD)
# Horizontal Flip Augmentation Semantic Validity Study (h-e1)

**Date:** 2026-07-11
**Author:** Anonymous
**Hypothesis:** h-e1 (EXISTENCE - PoC)
**Gate Type:** MUST_WORK

---

## Executive Summary

### Product Vision
A proof-of-concept experimental validation system to test whether horizontal flip augmentation causes differential performance degradation between symmetric and asymmetric digits in MNIST classification.

### Problem Statement
Data augmentation is widely used to improve model generalization, but the semantic validity of specific augmentation operations remains underexplored. Horizontal flip is commonly applied to natural images but conspicuously absent from MNIST training pipelines. This suggests practitioners may implicitly understand that horizontal flip creates semantically invalid training data for asymmetric digits (2, 3, 5, 6, 7, 9), yet no formal research validates this intuition.

**Hypothesis**: When horizontal flip augmentation is applied to MNIST training data, asymmetric digits {2,3,5,6,7,9} will show reduced test accuracy compared to baseline, while symmetric digits {0,1,8} remain unaffected.

### Success Criteria (EXISTENCE - PoC Level)
1. **Primary**: Code executes without errors
2. **Primary**: `asymmetric_acc(Baseline) > asymmetric_acc(Flip50)` (directional effect)
3. **Secondary**: `symmetric_acc(Baseline) ≈ symmetric_acc(Flip50)` (stability check)
4. **Positive Control**: `asymmetric_acc(Rotation) ≈ asymmetric_acc(Baseline)` (rotation should NOT harm asymmetric digits)

### Key Stakeholders
- Research Pipeline: Phase 4 validation → Phase 4.5 synthesis → Phase 6 paper writing
- Gate Decision: MUST_WORK - failure causes ABANDON

---

## Product Overview

### What We're Building
An experimental framework consisting of:
1. Five augmentation conditions (Baseline, Flip30, Flip50, Flip90, Rotation)
2. Standard CNN classifier (PyTorch official architecture)
3. Per-class accuracy evaluation system with symmetry-based grouping
4. Automated visualization generation for results communication

### What We're NOT Building
- Novel model architectures (using standard CNN)
- Production-ready augmentation library (research PoC only)
- Multi-seed statistical validation (single seed n=1 for EXISTENCE level)
- Interactive experiment interface (batch execution only)

### Core Mechanism
**Type**: Data augmentation (not model modification)
**Implementation**: `torchvision.transforms.RandomHorizontalFlip(p)`
**Integration Point**: Training data pipeline (applied before ToTensor+Normalize)
**Test Set**: NO augmentation (evaluate on clean test data)

---

## Functional Requirements

### FR-1: Dataset Preparation
**Priority**: P0 (Blocking)
**Description**: Load MNIST dataset with condition-specific augmentation pipelines

#### FR-1.1: Baseline Condition (No Augmentation)
- **Input**: MNIST raw images (28×28 grayscale)
- **Transform Pipeline**:
  1. `ToTensor()` - convert to [0, 1] range
  2. `Normalize(mean=0.1307, std=0.3081)` - MNIST-specific normalization
- **Output**: Preprocessed tensors (B, 1, 28, 28)
- **Acceptance**: Baseline model achieves ~99% test accuracy (literature standard)

#### FR-1.2: Flip Augmentation Conditions (Flip30, Flip50, Flip90)
- **Input**: MNIST raw images
- **Transform Pipeline**:
  1. `RandomHorizontalFlip(p=0.3/0.5/0.9)` - core mechanism
  2. `ToTensor()`
  3. `Normalize(mean=0.1307, std=0.3081)`
- **Output**: Augmented tensors for training
- **Acceptance**: Augmentation applied only to training set, NOT test set

#### FR-1.3: Rotation Control Condition
- **Input**: MNIST raw images
- **Transform Pipeline**:
  1. `RandomRotation(degrees=15)` - semantically valid augmentation
  2. `ToTensor()`
  3. `Normalize(mean=0.1307, std=0.3081)`
- **Output**: Rotated tensors for training
- **Acceptance**: Rotation should NOT differentially harm asymmetric digits

#### FR-1.4: Data Loading
- **Source**: `torchvision.datasets.MNIST(root='./data', download=True)`
- **Splits**: 60,000 train, 10,000 test (standard MNIST splits)
- **Batch Size**: 64 (from PyTorch official example)
- **Shuffle**: Training=True, Test=False
- **Acceptance**: DataLoader yields batches without errors

---

### FR-2: Model Architecture
**Priority**: P0 (Blocking)
**Description**: Implement standard CNN classifier following PyTorch official MNIST example

#### FR-2.1: Network Layers
- **Conv1**: Conv2d(in=1, out=32, kernel=3, stride=1) + ReLU + MaxPool2d(2)
  - Input: (B, 1, 28, 28)
  - Output: (B, 32, 13, 13)
- **Conv2**: Conv2d(in=32, out=64, kernel=3, stride=1) + ReLU + MaxPool2d(2)
  - Input: (B, 32, 13, 13)
  - Output: (B, 64, 5, 5)
- **Dropout1**: Dropout(p=0.25) - regularization after conv layers
- **Flatten**: (B, 64×5×5) → (B, 1600)
- **FC1**: Linear(1600→128) + ReLU
- **Dropout2**: Dropout(p=0.5) - regularization before output
- **FC2**: Linear(128→10) - output logits
- **Output**: log_softmax for NLLLoss compatibility

#### FR-2.2: Initialization
- **Random Seed**: 42 (fixed across all conditions)
- **Weight Init**: PyTorch default (Kaiming for conv, uniform for linear)
- **Acceptance**: Same initialization state across all 5 experimental conditions

---

### FR-3: Training Procedure
**Priority**: P0 (Blocking)
**Description**: Train 5 independent models (one per condition) with identical hyperparameters

#### FR-3.1: Optimizer Configuration
- **Type**: Adadelta
- **Learning Rate**: 1.0
- **Scheduler**: StepLR(step_size=1, gamma=0.7)
- **Source**: PyTorch official MNIST example
- **Acceptance**: Training loss decreases monotonically

#### FR-3.2: Training Loop
- **Epochs**: 14 (sufficient for MNIST convergence)
- **Loss Function**: NLLLoss
- **Device**: Auto-detect CUDA/CPU
- **Logging**: Print train loss per epoch
- **Acceptance**: All 5 conditions train to completion without errors

#### FR-3.3: Independent Condition Execution
- **Execution**: For each condition (Baseline, Flip30, Flip50, Flip90, Rotation):
  1. Initialize fresh model with seed=42
  2. Load dataset with condition-specific transform
  3. Train for 14 epochs
  4. Evaluate on test set
  5. Record per-class accuracy
- **Acceptance**: 5 trained models with corresponding accuracy profiles

---

### FR-4: Evaluation System
**Priority**: P0 (Blocking)
**Description**: Compute per-class and group-level accuracy metrics

#### FR-4.1: Per-Class Accuracy
- **Input**: Model predictions + ground truth labels (10,000 test samples)
- **Computation**:
  ```python
  for class_id in range(10):
      correct = sum(pred == target for pred, target in zip(predictions, targets) if target == class_id)
      total = sum(target == class_id for target in targets)
      accuracy[class_id] = correct / total * 100
  ```
- **Output**: 10-element array [acc_0, acc_1, ..., acc_9]
- **Acceptance**: Baseline condition achieves >98% per-class for all digits

#### FR-4.2: Symmetry-Based Grouping
- **Symmetric Digits**: {0, 1, 8}
- **Asymmetric Digits**: {2, 3, 5, 6, 7, 9}
- **Group Metrics**:
  - `symmetric_mean = mean(acc_0, acc_1, acc_8)`
  - `asymmetric_mean = mean(acc_2, acc_3, acc_5, acc_6, acc_7, acc_9)`
- **Output**: Dict with keys: `{symmetric_mean, asymmetric_mean, per_class}`
- **Acceptance**: Group means computed correctly for all 5 conditions

#### FR-4.3: Differential Effect Detection
- **Primary Comparison**: `Baseline.asymmetric_mean` vs `Flip50.asymmetric_mean`
- **Expected**: Baseline > Flip50 (degradation under flip)
- **Secondary Comparison**: `Baseline.symmetric_mean` vs `Flip50.symmetric_mean`
- **Expected**: Baseline ≈ Flip50 (stability for symmetric digits)
- **Control Comparison**: `Rotation.asymmetric_mean` vs `Baseline.asymmetric_mean`
- **Expected**: Rotation ≈ Baseline (rotation is semantically valid)
- **Acceptance**: Results stored in structured format for Phase 4.5 synthesis

---

### FR-5: Visualization Generation
**Priority**: P1 (Important)
**Description**: Generate publication-ready figures for hypothesis validation

#### FR-5.1: Per-Class Accuracy Heatmap
- **Type**: Conditions (rows) × Digits (columns) heatmap
- **Rows**: Baseline, Flip30, Flip50, Flip90, Rotation
- **Columns**: 0, 1, 2, 3, 4, 5, 6, 7, 8, 9
- **Cell Color**: Accuracy percentage (0-100%)
- **Colormap**: Sequential (e.g., viridis)
- **Annotations**: Accuracy values in cells
- **Acceptance**: Visual pattern shows asymmetric digit degradation under flip

#### FR-5.2: Group-Level Comparison Bar Chart
- **Type**: Grouped bar chart
- **X-Axis**: 5 conditions
- **Y-Axis**: Mean accuracy (%)
- **Groups**: Symmetric (blue) vs Asymmetric (orange)
- **Error Bars**: None (single seed, n=1)
- **Acceptance**: Clear visual separation between symmetric/asymmetric under flip conditions

#### FR-5.3: Dose-Response Plot (Flip Probability)
- **Type**: Line plot
- **X-Axis**: Flip probability [0.0, 0.3, 0.5, 0.9]
- **Y-Axis**: Group mean accuracy
- **Lines**: Symmetric (stable line), Asymmetric (declining line)
- **Markers**: Circle (symmetric), Triangle (asymmetric)
- **Acceptance**: Demonstrates monotonic degradation with flip probability

#### FR-5.4: Figure Outputs
- **Format**: PNG (300 DPI) + PDF (vector)
- **Save Location**: `{hypothesis_folder}/figures/`
- **Filenames**: `heatmap.png`, `group_comparison.png`, `dose_response.png`
- **Acceptance**: All figures saved without errors

---

### FR-6: Results Logging
**Priority**: P1 (Important)
**Description**: Save experimental results in structured format for Phase 4.5 synthesis

#### FR-6.1: Accuracy Results JSON
- **Filename**: `{hypothesis_folder}/results_accuracy.json`
- **Structure**:
  ```json
  {
    "baseline": {"per_class": [...], "symmetric_mean": 99.2, "asymmetric_mean": 99.1},
    "flip30": {"per_class": [...], "symmetric_mean": 99.0, "asymmetric_mean": 97.5},
    "flip50": {"per_class": [...], "symmetric_mean": 98.9, "asymmetric_mean": 95.2},
    "flip90": {"per_class": [...], "symmetric_mean": 98.7, "asymmetric_mean": 91.8},
    "rotation": {"per_class": [...], "symmetric_mean": 99.1, "asymmetric_mean": 99.0}
  }
  ```
- **Acceptance**: JSON file parseable and contains all required fields

#### FR-6.2: Training Logs
- **Filename**: `{hypothesis_folder}/training_logs.txt`
- **Content**: Epoch-wise train loss, test accuracy for each condition
- **Acceptance**: Logs show convergence patterns

---

## Non-Functional Requirements

### NFR-1: Performance
- **Training Time**: <10 minutes per condition on CPU, <2 minutes on GPU
- **Memory**: <2GB RAM (MNIST is small)
- **Disk**: <500MB (including cached dataset)

### NFR-2: Reproducibility
- **Random Seed**: Fixed at 42 for all conditions
- **Deterministic Ops**: Use `torch.manual_seed(42)` and `np.random.seed(42)`
- **Environment**: Document Python version, PyTorch version, hardware

### NFR-3: Code Quality
- **Structure**: Modular functions (load_data, build_model, train, evaluate)
- **Logging**: Clear progress indicators during training
- **Error Handling**: Graceful failures with informative messages

### NFR-4: Output Organization
- **Hypothesis Folder**: `docs/youra_research/h-e1/`
- **Figures**: `docs/youra_research/h-e1/figures/`
- **Results**: `docs/youra_research/h-e1/results_accuracy.json`
- **Logs**: `docs/youra_research/h-e1/training_logs.txt`

---

## Dependencies

### External Libraries
- **PyTorch**: ≥1.10 (torchvision.datasets, torchvision.transforms, torch.nn)
- **torchvision**: ≥0.11 (MNIST dataset, transforms)
- **NumPy**: ≥1.20 (array operations)
- **Matplotlib**: ≥3.4 (visualization)
- **scikit-learn**: ≥0.24 (metrics, optional statistical tests)

### Data Dependencies
- **MNIST Dataset**: Auto-downloaded via torchvision (60MB)
- **No pretrained models required** (training from scratch)

### Hypothesis Dependencies
- **Prerequisites**: None (foundational hypothesis)
- **Dependent Hypotheses**: None yet (first in sequence)

---

## Technical Constraints

### EXISTENCE (PoC) Constraints
- **Sample Size**: Single seed (n=1) - directional evidence only
- **Statistical Testing**: Optional (PoC focuses on effect direction)
- **Hyperparameter Tuning**: None (use PyTorch official defaults)

### Implementation Scope
- **Architecture**: Fixed (PyTorch official MNIST CNN)
- **Dataset**: Fixed (MNIST only, no EMNIST/Fashion-MNIST)
- **Augmentation**: Horizontal flip + rotation only (no other transforms)

---

## Success Metrics

### MUST_WORK Gate Criteria
1. ✅ Code executes without errors
2. ✅ Baseline model achieves ~99% test accuracy (validates implementation)
3. ✅ `Baseline.asymmetric_mean > Flip50.asymmetric_mean` (effect direction confirmed)
4. ✅ `Baseline.symmetric_mean ≈ Flip50.symmetric_mean` (symmetric digits stable)
5. ✅ `Rotation.asymmetric_mean ≈ Baseline.asymmetric_mean` (control condition passes)

**If ANY criterion fails**: ABANDON hypothesis (core phenomenon does not exist)

### Quantitative Targets (Expected)
- **Baseline Accuracy**: ~99% overall
- **Flip50 Asymmetric Degradation**: 2-5% reduction (small but measurable)
- **Flip50 Symmetric Stability**: <1% change
- **Rotation Control**: <1% change for asymmetric digits

---

## Risk Assessment

### High Risk
- **Risk**: Baseline model fails to reach 99% accuracy
  - **Mitigation**: Use exact PyTorch official architecture and hyperparameters
  - **Contingency**: Debug dataset loading, verify normalization constants

### Medium Risk
- **Risk**: Effect size too small to detect with n=1
  - **Mitigation**: Use extreme condition (Flip90) to amplify effect
  - **Contingency**: If no directional effect, hypothesis is falsified (ABANDON)

### Low Risk
- **Risk**: Visualization code errors
  - **Mitigation**: Use standard matplotlib patterns, test on dummy data first
  - **Contingency**: Generate plots manually in Phase 4.5 if needed

---

## Appendix: Reference Implementations

### Primary Reference
- **Source**: PyTorch Official MNIST Example
- **URL**: https://github.com/PyTorch/examples/blob/main/mnist/main.py
- **Components**: CNN architecture, Adadelta optimizer, training loop, StepLR scheduler
- **Validation**: ~99% test accuracy (literature standard)

### Augmentation API
- **Source**: torchvision.transforms.RandomHorizontalFlip
- **URL**: https://pytorch.org/vision/stable/generated/torchvision.transforms.RandomHorizontalFlip.html
- **Usage**: Well-documented, widely-used, no custom implementation needed

### Critical Insight from Research
- **Observation**: Kaggle MNIST competition winners (99.689% accuracy) use extensive augmentation (rotation, affine, perspective) but **systematically avoid horizontal flip**
- **Implication**: Practitioners implicitly understand semantic invalidity, confirming hypothesis premise
- **Source**: https://github.com/emrebaranarca/computer-vision-mnist-cnn

---

## Approval & Sign-off

**Phase 2C Completion**: ✅ Experiment brief validated
**Task Budget**: LIGHT (EXISTENCE) - Maximum 15 implementation tasks
**Next Phase**: Phase 3 Architecture Design → Logic → Config → Task Breakdown

---

*Document generated via BMAD PRD workflow for YouRA Research Pipeline*
*Hypothesis: h-e1 (EXISTENCE - PoC)*
*MUST_WORK Gate: Validates core phenomenon existence*
