# Product Requirements Document (PRD)
# Experiment: h-m1

---

## Document Metadata

**Document Type:** Product Requirements Document (PRD)  
**Experiment ID:** h-m1  
**Hypothesis Statement:** Asymmetric digit degradation increases monotonically with flip probability (dose-response relationship)  
**Author:** Anonymous  
**Date:** 2026-07-11  
**Version:** 1.0  
**Phase:** Phase 3 - Implementation Planning  

**Frontmatter:**
```yaml
stepsCompleted:
  - executive_summary
  - problem_statement
  - functional_requirements
  - non_functional_requirements
  - success_criteria
  - dependencies
  - milestones
```

---

## 1. Executive Summary

### 1.1 Purpose

Implement a controlled experiment to test the **mechanism** behind asymmetric digit degradation in MNIST classification under horizontal flip augmentation. This experiment validates the dose-response relationship between flip probability and accuracy degradation, establishing the complete causal chain from augmentation parameters to model performance.

### 1.2 Scope

**In Scope:**
- MNIST dataset loading and preprocessing
- Standard CNN baseline model (PyTorch official architecture)
- Four experimental conditions with varying flip probabilities (p=0.0, 0.3, 0.5, 0.9)
- Multi-seed training (n=5 seeds per condition, 20 total training runs)
- Asymmetric digit accuracy evaluation
- Statistical dose-response analysis (Spearman correlation)
- Visualization suite (dose-response curve, per-digit breakdown, degradation magnitude)

**Out of Scope:**
- Alternative augmentation techniques (rotation, scaling, etc.)
- Other datasets beyond MNIST
- Novel model architectures (architecture held constant across conditions)
- Hyperparameter optimization (fixed parameters for controlled comparison)

### 1.3 Target Users

**Primary:**
- Research validation: Confirms/refutes mechanism hypothesis (H-M1)
- Paper writing (Phase 6): Results feed into empirical evidence section

**Secondary:**
- Machine learning practitioners: Documents semantic validity issues in data augmentation
- Deep learning educators: Demonstrates controlled experimental methodology

---

## 2. Problem Statement

### 2.1 Background

Horizontal flip augmentation is a standard technique in computer vision training, applied to increase dataset diversity and improve generalization. However, **semantic validity** of augmented samples is often assumed rather than tested. For MNIST digits, horizontal flips create visually valid but semantically invalid images:
- Digit "6" horizontally flipped → visually resembles "9" but retains label "6" (label noise)
- Asymmetric digits {2, 3, 5, 6, 7, 9} are all affected
- Symmetric digits {0, 1, 8} remain valid under flip

**Research Gap:** While the existence of this degradation effect can be demonstrated (H-E1), the **mechanism** (dose-response relationship between flip probability and degradation magnitude) has not been tested. Understanding this mechanism is critical for:
1. Quantifying label noise severity as a function of augmentation strength
2. Establishing causality (not just correlation) in augmentation-induced performance loss
3. Providing actionable guidance on augmentation probability thresholds

### 2.2 User Needs

| User Type | Need | Success Metric |
|-----------|------|----------------|
| Research Pipeline | Validate H-M1 mechanism hypothesis | Gate satisfied: Spearman ρ < 0, p < 0.05 |
| Phase 6 Paper | Empirical evidence for dose-response claim | Complete results table + figures |
| ML Practitioners | Quantified degradation vs flip probability | Degradation curve with error bars |
| Reproducibility | Full code for independent verification | Complete implementation + README |

### 2.3 Hypothesis Gate

**Gate Type:** MUST_WORK  
**Gate Condition:** Spearman rank correlation (flip probability vs asymmetric accuracy) significantly negative (p < 0.05)

**If Gate Satisfied (ρ < 0, p < 0.05):**
- Mechanism confirmed: dose-response relationship proven
- H-M1 marked as PASS
- Continue to Phase 4.5 (Synthesis)

**If Gate Fails (ρ ≥ 0 or p ≥ 0.05):**
- Mechanism refuted: effect exists (per H-E1) but not monotonic
- H-M1 marked as PARTIAL
- Document limitation in 04_validation.md
- Continue workflow (SHOULD_WORK gate allows continuation with documented limitation)

---

## 3. Functional Requirements

### 3.1 Data Pipeline Requirements

**FR-D1: MNIST Dataset Loading**
- **Description:** Download and load MNIST dataset from torchvision.datasets
- **Input:** None (auto-download)
- **Output:** 60,000 training images, 10,000 test images (28×28 grayscale)
- **Acceptance Criteria:**
  - Dataset cached to `./data/MNIST/` directory
  - Train/test split preserved (60k/10k)
  - All 10 classes present with correct distribution

**FR-D2: Baseline Preprocessing**
- **Description:** Apply standard MNIST normalization to all samples
- **Input:** PIL Images from MNIST dataset
- **Output:** Normalized PyTorch tensors
- **Implementation:**
  ```python
  transforms.Compose([
      transforms.ToTensor(),
      transforms.Normalize((0.1307,), (0.3081,))  # MNIST standard
  ])
  ```
- **Acceptance Criteria:** Output tensor range approximately [-2, 2] after normalization

**FR-D3: Flip Augmentation Conditions (Dose Manipulation)**
- **Description:** Create four augmentation pipelines with varying flip probabilities
- **Conditions:**
  1. **Baseline (p=0.0):** No flip augmentation (ToTensor + Normalize only)
  2. **Flip30 (p=0.3):** RandomHorizontalFlip(p=0.3) + Normalize
  3. **Flip50 (p=0.5):** RandomHorizontalFlip(p=0.5) + Normalize
  4. **Flip90 (p=0.9):** RandomHorizontalFlip(p=0.9) + Normalize
- **Implementation:**
  ```python
  def create_transform(flip_prob):
      return transforms.Compose([
          transforms.RandomHorizontalFlip(p=flip_prob),
          transforms.ToTensor(),
          transforms.Normalize((0.1307,), (0.3081,))
      ])
  ```
- **Acceptance Criteria:**
  - Each condition uses same normalization parameters
  - Only flip probability varies across conditions
  - Transform pipelines deterministic given seed

**FR-D4: DataLoader Configuration**
- **Description:** Create DataLoader instances for training and testing
- **Parameters:**
  - Batch size: 64
  - Shuffle: True (training), False (test)
  - Num workers: 4 (parallel loading)
- **Acceptance Criteria:** Batches yield (images, labels) tuples with correct shapes

### 3.2 Model Requirements

**FR-M1: Baseline CNN Architecture**
- **Description:** Implement standard CNN architecture from PyTorch MNIST official example
- **Architecture Specification:**
  ```python
  class StandardCNN(nn.Module):
      Conv1: 1 → 32 channels, kernel 3×3, ReLU
      Conv2: 32 → 64 channels, kernel 3×3, ReLU
      MaxPool2d: 2×2
      Dropout2d: p=0.25
      Flatten: 64×7×7 → 9216
      FC1: 9216 → 128, ReLU
      Dropout: p=0.5
      FC2: 128 → 10 (output logits)
      Output: Log-softmax (log probabilities)
  ```
- **Parameters:** ~1.2M total
- **Acceptance Criteria:**
  - Input shape: (B, 1, 28, 28)
  - Output shape: (B, 10) log probabilities
  - Forward pass completes without error
  - Baseline (p=0.0) achieves ~99% test accuracy

**FR-M2: Model Initialization**
- **Description:** Initialize model weights consistently across all seeds
- **Implementation:** PyTorch default initialization (no custom init)
- **Acceptance Criteria:** Different seeds produce different initial weights

### 3.3 Training Requirements

**FR-T1: Training Loop**
- **Description:** Implement standard supervised training loop
- **Process:**
  1. Forward pass: model(batch_images)
  2. Loss computation: CrossEntropyLoss(logits, labels)
  3. Backward pass: loss.backward()
  4. Optimizer step: optimizer.step()
  5. Learning rate schedule: scheduler.step() (per epoch)
- **Acceptance Criteria:**
  - Training loss decreases over epochs
  - Test accuracy improves over epochs
  - No NaN or Inf in loss values

**FR-T2: Optimizer Configuration**
- **Description:** Use Adam optimizer with fixed learning rate
- **Parameters:**
  - Learning rate: 0.001
  - Beta1: 0.9, Beta2: 0.999 (Adam defaults)
  - Weight decay: 0 (no L2 regularization beyond dropout)
- **Acceptance Criteria:** Optimizer updates all model parameters

**FR-T3: Learning Rate Schedule**
- **Description:** Apply StepLR decay schedule
- **Parameters:**
  - Step size: 1 epoch
  - Gamma: 0.7 (multiply lr by 0.7 every epoch)
- **Rationale:** From PyTorch official example, ensures stable convergence
- **Acceptance Criteria:** Learning rate logged per epoch shows exponential decay

**FR-T4: Early Stopping**
- **Description:** Stop training if validation accuracy plateaus
- **Parameters:**
  - Patience: 5 epochs
  - Monitor metric: Validation accuracy
- **Acceptance Criteria:**
  - Training stops before epoch 30 if no improvement for 5 epochs
  - Best model checkpoint saved (highest validation accuracy)

**FR-T5: Multi-Seed Execution**
- **Description:** Train 5 independent models per flip probability condition
- **Seeds:** [42, 43, 44, 45, 46] (arbitrary but fixed for reproducibility)
- **Total Training Runs:** 4 conditions × 5 seeds = 20 runs
- **Acceptance Criteria:**
  - Each seed produces different model (weight initialization varies)
  - Results stored per (condition, seed) pair
  - All 20 training runs complete without error

### 3.4 Evaluation Requirements

**FR-E1: Test Set Evaluation**
- **Description:** Evaluate each trained model on MNIST test set
- **Input:** Trained model checkpoint, test dataset (no augmentation)
- **Output:** Predictions for all 10,000 test samples
- **Acceptance Criteria:**
  - Test transform uses NO flip augmentation (only ToTensor + Normalize)
  - Predictions shape: (10000,) integer class labels

**FR-E2: Asymmetric Digit Accuracy**
- **Description:** Compute accuracy on asymmetric digit subset
- **Asymmetric Digits:** {2, 3, 5, 6, 7, 9}
- **Formula:**
  ```python
  mask = np.isin(y_true, [2, 3, 5, 6, 7, 9])
  accuracy_asymmetric = accuracy_score(y_true[mask], y_pred[mask])
  ```
- **Acceptance Criteria:**
  - Accuracy computed per (condition, seed)
  - Mean and std computed across 5 seeds per condition
  - Results stored in structured format (DataFrame or dict)

**FR-E3: Overall Test Accuracy (Secondary)**
- **Description:** Compute accuracy on full test set (all digits)
- **Purpose:** Verify baseline performance matches literature (~99%)
- **Acceptance Criteria:** Baseline (p=0.0) mean accuracy ≥ 98.5%

**FR-E4: Per-Digit Accuracy Breakdown**
- **Description:** Compute accuracy per digit class
- **Output:** 10 accuracy values per (condition, seed) pair
- **Purpose:** Visualize which asymmetric digits degrade most under flip
- **Acceptance Criteria:** Results stored in (condition, seed, digit) indexed table

### 3.5 Statistical Analysis Requirements

**FR-S1: Dose-Response Correlation Test**
- **Description:** Test monotonic relationship between flip probability and accuracy
- **Method:** Spearman rank correlation
- **Input:** 
  - X: [0.0, 0.3, 0.5, 0.9] (flip probabilities)
  - Y: [mean_acc_p0, mean_acc_p3, mean_acc_p5, mean_acc_p9] (mean asymmetric accuracy per condition)
- **Output:** (ρ, p-value)
- **Gate Criterion:** ρ < 0 AND p < 0.05 (negative monotonic relationship, significant)
- **Acceptance Criteria:**
  - Spearman correlation computed correctly
  - P-value reported with 3 decimal places
  - Results logged and saved to results JSON

**FR-S2: Accuracy Degradation Quantification**
- **Description:** Compute degradation magnitude vs baseline
- **Formula:**
  ```python
  degradation[p] = mean_accuracy[p=0.0] - mean_accuracy[p]
  ```
- **Output:** Degradation values for p=0.3, 0.5, 0.9
- **Acceptance Criteria:** Degradation values non-negative (accuracy decreases or stays same)

### 3.6 Visualization Requirements

**FR-V1: Dose-Response Curve (Mandatory)**
- **Description:** Line plot showing mean asymmetric accuracy vs flip probability
- **Axes:**
  - X: Flip probability {0.0, 0.3, 0.5, 0.9}
  - Y: Mean asymmetric digit accuracy
- **Elements:**
  - Line connecting mean accuracies
  - Error bars: ± 1 standard deviation across 5 seeds
  - Markers at each data point
- **Acceptance Criteria:**
  - Plot saved to `{hypothesis_folder}/figures/dose_response_curve.png`
  - Expected pattern: downward trend (monotonic decrease)
  - Axis labels clear and readable

**FR-V2: Per-Digit Accuracy Heatmap**
- **Description:** Heatmap showing accuracy per digit and flip probability
- **Dimensions:**
  - Rows: Digits {0, 1, 2, 3, 4, 5, 6, 7, 8, 9}
  - Columns: Flip probabilities {0.0, 0.3, 0.5, 0.9}
  - Color: Accuracy (0-1 scale, colormap: viridis or coolwarm)
- **Purpose:** Identify which asymmetric digits degrade most
- **Acceptance Criteria:**
  - Saved to `{hypothesis_folder}/figures/per_digit_heatmap.png`
  - Color scale labeled (0.0 = low accuracy, 1.0 = high accuracy)
  - Asymmetric digits {2,3,5,6,7,9} show degradation pattern

**FR-V3: Degradation Magnitude Bar Chart**
- **Description:** Bar chart showing accuracy degradation vs baseline
- **Axes:**
  - X: Flip probability {0.3, 0.5, 0.9} (baseline excluded)
  - Y: Degradation (baseline_accuracy - condition_accuracy)
- **Elements:**
  - Bars with error bars (standard error across seeds)
- **Acceptance Criteria:**
  - Saved to `{hypothesis_folder}/figures/degradation_bars.png`
  - Bars increase in height from p=0.3 to p=0.9 (dose-response effect)

**FR-V4: Gate Metrics Comparison (Mandatory - Phase 4 validation)**
- **Description:** Bar chart comparing target vs actual gate metrics
- **Metrics:**
  - Target: Spearman ρ < 0, p < 0.05
  - Actual: Measured ρ and p-value
- **Acceptance Criteria:**
  - Saved to `{hypothesis_folder}/figures/gate_metrics.png`
  - Visual pass/fail indicator (green if gate satisfied, red if not)

### 3.7 Output Requirements

**FR-O1: Results Logging**
- **Description:** Save all results to structured JSON file
- **File:** `{hypothesis_folder}/results.json`
- **Contents:**
  - Per-condition, per-seed accuracies (asymmetric + overall)
  - Mean and std per condition
  - Spearman correlation result (ρ, p-value)
  - Degradation values
  - Gate status (PASS/FAIL)
- **Acceptance Criteria:** JSON valid and parseable

**FR-O2: Model Checkpoints**
- **Description:** Save best model checkpoint per (condition, seed)
- **Path:** `{hypothesis_folder}/checkpoints/model_p{flip_prob}_seed{seed}.pt`
- **Contents:** model.state_dict() + optimizer state + epoch number
- **Acceptance Criteria:** Checkpoint loadable and produces same predictions

**FR-O3: Training Logs**
- **Description:** Log training progress per epoch
- **Format:** CSV per (condition, seed)
- **Columns:** epoch, train_loss, val_accuracy, lr
- **Path:** `{hypothesis_folder}/logs/training_p{flip_prob}_seed{seed}.csv`
- **Acceptance Criteria:** One log file per training run (20 total)

---

## 4. Non-Functional Requirements

### 4.1 Performance Requirements

**NFR-P1: Training Time**
- **Target:** ≤ 5 minutes per training run on GPU (≤ 100 minutes total for 20 runs)
- **Hardware Assumption:** CUDA-capable GPU (e.g., RTX 3090, V100)
- **Acceptance Criteria:** MNIST CNN training is lightweight, easily meets target

**NFR-P2: Memory Usage**
- **Target:** ≤ 2 GB GPU memory per training run
- **Rationale:** MNIST (28×28) + small CNN fit easily in modern GPU memory
- **Acceptance Criteria:** Training completes without OOM errors

### 4.2 Reproducibility Requirements

**NFR-R1: Deterministic Execution**
- **Description:** Results must be reproducible given same seeds
- **Implementation:**
  - Set PyTorch seed: `torch.manual_seed(seed)`
  - Set NumPy seed: `np.random.seed(seed)`
  - Set CUDA seed: `torch.cuda.manual_seed_all(seed)`
  - Deterministic algorithms: `torch.backends.cudnn.deterministic = True`
- **Acceptance Criteria:** Running same seed twice produces identical results (within float precision)

**NFR-R2: Experiment Configuration Tracking**
- **Description:** Save all hyperparameters and configuration to config file
- **File:** `{hypothesis_folder}/config.yaml`
- **Contents:** flip_probabilities, seeds, batch_size, lr, epochs, patience, model_architecture
- **Acceptance Criteria:** Config file sufficient to reproduce experiment

### 4.3 Code Quality Requirements

**NFR-Q1: Modularity**
- **Description:** Separate concerns into modules
- **Structure:**
  - `data.py`: Dataset loading, transforms
  - `model.py`: CNN architecture definition
  - `train.py`: Training loop
  - `evaluate.py`: Evaluation and metrics
  - `visualize.py`: Plotting functions
  - `main.py`: Orchestration (run all conditions/seeds)
- **Acceptance Criteria:** Each module independently testable

**NFR-Q2: Documentation**
- **Description:** Docstrings for all functions
- **Format:** Google-style docstrings (Args, Returns, Raises)
- **Acceptance Criteria:** 100% function coverage with docstrings

**NFR-Q3: Error Handling**
- **Description:** Graceful failure handling
- **Cases:**
  - CUDA unavailable → fallback to CPU with warning
  - Dataset download failure → retry with exponential backoff
  - Training divergence (loss NaN) → log error and skip seed
- **Acceptance Criteria:** No silent failures, all errors logged

### 4.4 Compatibility Requirements

**NFR-C1: Python Version**
- **Target:** Python 3.8+
- **Rationale:** PyTorch 2.0+ compatibility

**NFR-C2: Dependency Versions**
- **Core Dependencies:**
  - PyTorch 2.0+
  - torchvision 0.15+
  - NumPy 1.24+
  - SciPy 1.10+ (for Spearman correlation)
  - Matplotlib 3.7+ (for visualization)
  - pandas 2.0+ (for results tables)
- **Acceptance Criteria:** `requirements.txt` specifies version constraints

---

## 5. Success Criteria

### 5.1 Gate Success (Primary)

**Gate Criterion:** Spearman ρ < 0, p < 0.05

| Outcome | ρ | p-value | Gate Status | Interpretation |
|---------|---|---------|-------------|----------------|
| Success | < 0 | < 0.05 | PASS | Dose-response mechanism confirmed |
| Partial | < 0 | ≥ 0.05 | PARTIAL | Trend present but not significant |
| Partial | ≥ 0 | any | PARTIAL | No monotonic relationship (mechanism refuted) |

### 5.2 Baseline Performance Validation

**Criterion:** Baseline (p=0.0) mean test accuracy ≥ 98.5%

**Purpose:** Verify implementation correctness against literature

**If Failed:** Implementation bug likely (standard MNIST CNN should achieve ~99%)

### 5.3 Code Execution

**Criterion:** All 20 training runs complete without errors

**Components:**
- Data loading works
- Model trains to completion
- Evaluation produces valid metrics
- Visualizations generated

### 5.4 Documentation Completeness

**Criterion:** All outputs documented in 04_validation.md

**Contents:**
- Results summary table
- Gate status interpretation
- Figure references
- Limitations (if any)

---

## 6. Dependencies and Constraints

### 6.1 External Dependencies

| Dependency | Type | Purpose | Availability |
|------------|------|---------|--------------|
| MNIST Dataset | Data | Training/test samples | torchvision auto-download |
| PyTorch | Library | Deep learning framework | pip install |
| CUDA | Hardware | GPU acceleration | Optional (CPU fallback) |

### 6.2 Internal Dependencies

**Prerequisite Hypothesis:** H-E1 (Asymmetric digit degradation effect)
- **Status:** Not yet validated (experiment design prepared in parallel)
- **Dependency Type:** Conceptual (H-M1 tests mechanism of effect confirmed by H-E1)
- **Impact:** H-M1 execution waits for H-E1 completion per Phase 4 workflow

### 6.3 Constraints

**Constraint 1: Fixed Architecture**
- **Limitation:** Cannot modify CNN architecture across conditions
- **Rationale:** Controlled experiment requires only augmentation to vary

**Constraint 2: MNIST-Specific**
- **Limitation:** Results only apply to MNIST digit classification
- **Rationale:** Hypothesis explicitly tests semantic validity of MNIST horizontal flips

**Constraint 3: Computational Budget**
- **Limitation:** 20 training runs (4 conditions × 5 seeds)
- **Rationale:** Statistical power (n=5) balanced with compute cost

---

## 7. Milestones and Deliverables

### Milestone 1: Environment Setup (Phase 4 - Step 1)
- **Deliverables:**
  - Python environment created
  - Dependencies installed (requirements.txt)
  - MNIST dataset downloaded
- **Acceptance:** `pytest tests/test_data.py` passes

### Milestone 2: Code Implementation (Phase 4 - Steps 2-3)
- **Deliverables:**
  - `data.py`, `model.py`, `train.py`, `evaluate.py`, `visualize.py` implemented
  - Unit tests for each module
  - `main.py` orchestration script
- **Acceptance:** `pytest tests/` passes all tests

### Milestone 3: Training Execution (Phase 4 - Step 4)
- **Deliverables:**
  - 20 training runs completed
  - Model checkpoints saved (20 files)
  - Training logs saved (20 CSV files)
- **Acceptance:** All runs complete without errors, logs show convergence

### Milestone 4: Results Analysis (Phase 4 - Step 5)
- **Deliverables:**
  - `results.json` with all metrics
  - Spearman correlation computed
  - Gate status determined
- **Acceptance:** Gate criterion evaluated, results logged

### Milestone 5: Validation Report (Phase 4 - Step 6)
- **Deliverables:**
  - `04_validation.md` written
  - All figures generated and referenced
  - Gate status documented
- **Acceptance:** Phase 4 validator agent confirms completeness

---

## 8. Appendix

### 8.1 Hypothesis Traceability

| PRD Section | Phase 2C Source Section | Traceability |
|-------------|------------------------|--------------|
| FR-D1 (Dataset) | Experiment Specification → Dataset | MNIST specification |
| FR-D3 (Flip conditions) | Dataset → Augmentation | Four flip probabilities |
| FR-M1 (Model architecture) | Models → Baseline Model | Standard CNN architecture |
| FR-T2-T4 (Training protocol) | Training Protocol | Optimizer, scheduler, epochs |
| FR-E2 (Asymmetric accuracy) | Evaluation → Primary Metrics | Metric definition |
| FR-S1 (Dose-response test) | Evaluation → Statistical Test | Spearman correlation |
| FR-V1-V3 (Visualizations) | Visualization Requirements | Three required figures |

### 8.2 Risk Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Training divergence (NaN loss) | Low | High | Early stopping, gradient clipping if needed |
| CUDA unavailable | Medium | Low | CPU fallback implemented |
| Dataset download failure | Low | Medium | Retry logic with exponential backoff |
| Insufficient statistical power | Low | High | n=5 seeds per condition (established practice) |
| Baseline accuracy below 98.5% | Low | High | Code review, architecture verification |

### 8.3 References

**Phase 2C Experiment Brief:**
- `/workspace/TEST_scsl/docs/youra_research/h-m1/02c_experiment_brief.md`

**PyTorch Official MNIST Example:**
- https://github.com/PyTorch/examples/blob/main/mnist/main.py

**RandomHorizontalFlip Documentation:**
- https://pytorch.org/vision/stable/generated/torchvision.transforms.RandomHorizontalFlip.html

---

**Document Status:** ✅ Complete  
**Next Phase:** Phase 3 - Architecture Design (Step 3)  
**Approval:** Ready for implementation planning
