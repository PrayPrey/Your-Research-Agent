# Implementation Task List: H-E1 Gradient Abnormality Detection

**Hypothesis:** h-e1  
**Type:** EXISTENCE  
**Gate:** MUST_WORK  
**Date:** 2026-08-20  
**Budget Tier:** 2 (Medium Complexity)

---

## Budget Allocation

**Total Estimated Effort:** 60 story points  
**Epic Tasks:** 7  
**Subtasks:** 28  
**Failsafe Tasks:** 3

**Complexity Breakdown:**
- Data preparation: 8 points (1 Epic)
- Environment setup: 4 points (1 Epic)
- Core implementation: 36 points (4 Epics)
- Validation & testing: 8 points (1 Epic)
- Failsafe: 4 points (3 tasks)

---

## Task Hierarchy

### EPIC-1: Environment Setup
**Effort:** 4 points  
**Priority:** HIGH  
**Blocking:** All other tasks

#### TASK-1.1: Create Project Structure
- **Effort:** 1 point
- **Description:** Create directory structure for h_e1_detection experiment
- **Deliverables:**
  - `experiments/h_e1_detection/` with subdirs: configs, checkpoints, outputs, plots, utils, tests
  - Empty `__init__.py` files for Python modules
  - `README.md` with setup instructions
- **Acceptance:** Directory structure matches 03_architecture.md specification

#### TASK-1.2: Install Dependencies
- **Effort:** 2 points
- **Description:** Set up Python environment and install required libraries
- **Deliverables:**
  - `requirements.txt` with pinned versions (torch==2.0.1, wilds==2.0.0, grad-cam==1.5.0, scipy, matplotlib, seaborn, pandas, pyyaml, tqdm)
  - Conda/venv environment creation script
  - Verification script to test imports
- **Acceptance:** All imports succeed, CUDA available if GPU present

#### TASK-1.3: Configuration File
- **Effort:** 1 point
- **Description:** Create config.yaml with all hyperparameters from 03_config.md
- **Deliverables:**
  - `configs/config.yaml` with sections: paths, model, training, evaluation, gaia_z, statistics, reproducibility
- **Acceptance:** Config loads without errors, all required keys present

---

### EPIC-2: Data Pipeline
**Effort:** 8 points  
**Priority:** HIGH  
**Depends on:** EPIC-1

#### TASK-2.1: WILDS Dataset Loader
- **Effort:** 3 points
- **Description:** Implement Waterbirds dataset loading with WILDS API
- **Deliverables:**
  - `utils/data_utils.py::load_waterbirds()` - Returns train/val/test datasets
  - `utils/data_utils.py::get_group_labels()` - Extract group membership from metadata
- **Acceptance:**
  - Dataset downloads automatically to ~/.wilds/
  - Train: 4795, Val: 1199, Test: 5794 samples verified
  - Metadata accessible: class, background, group_id

#### TASK-2.2: Data Transforms
- **Effort:** 2 points
- **Description:** Implement ImageNet normalization and augmentation
- **Deliverables:**
  - `utils/data_utils.py::get_train_transforms()` - RandomResizedCrop, RandomHorizontalFlip, ColorJitter, Normalize
  - `utils/data_utils.py::get_eval_transforms()` - Resize(256), CenterCrop(224), Normalize
- **Acceptance:** Transforms produce 224×224 RGB tensors with ImageNet normalization

#### TASK-2.3: DataLoader Creation
- **Effort:** 3 points
- **Description:** Create PyTorch DataLoaders with proper batching
- **Deliverables:**
  - `utils/data_utils.py::create_dataloaders()` - Returns train/val/test loaders
  - Supports configurable batch_size, num_workers, pin_memory
- **Acceptance:**
  - Loaders iterate correctly over full dataset
  - Batch shapes: images [B,3,224,224], labels [B], metadata [B,3]

---

### EPIC-3: Model Training
**Effort:** 12 points  
**Priority:** HIGH  
**Depends on:** EPIC-2

#### TASK-3.1: ResNet-50 Model Initialization
- **Effort:** 2 points
- **Description:** Load pretrained ResNet-50 and modify for binary classification
- **Deliverables:**
  - `utils/model_utils.py::create_model()` - Load ResNet-50, replace fc layer: 2048 → 2 classes
  - Model moves to GPU if available
- **Acceptance:** Model outputs shape [B, 2], pretrained weights loaded

#### TASK-3.2: Group Accuracy Tracker
- **Effort:** 3 points
- **Description:** Implement per-group accuracy tracking during training
- **Deliverables:**
  - `utils/training.py::GroupTracker` class with update() and compute_metrics() methods
  - Tracks correct/total for groups 0-3
  - Computes: group_acc (0-3), WGA, minority_acc, majority_acc, avg_acc
- **Acceptance:** Metrics computed correctly on synthetic test data

#### TASK-3.3: Training Loop
- **Effort:** 4 points
- **Description:** Implement standard ERM training with early stopping
- **Deliverables:**
  - `train_model.py` script with argparse CLI
  - `utils/training.py::train_epoch()` - Standard forward/backward pass
  - `utils/training.py::validate()` - Compute group metrics on val set
  - Early stopping: patience=50 epochs on WGA metric
  - Checkpoint saving: best WGA and last epoch
- **Acceptance:**
  - Training completes 300 epochs or early stops
  - Checkpoints saved with model_state_dict, optimizer, epoch, metrics

#### TASK-3.4: Training Validation
- **Effort:** 3 points
- **Description:** Validate trained model meets quality gates
- **Deliverables:**
  - `utils/training.py::validate_training()` - Check WGA < 80%, minority_acc ≥ 60%, avg_acc > 95%
  - Raise clear error if validation fails with diagnostic info
  - Log training_log.csv with per-epoch metrics
- **Acceptance:**
  - Validation checks enforce all 3 thresholds
  - training_log.csv contains all required columns

---

### EPIC-4: GradCAM Gradient Extraction
**Effort:** 10 points  
**Priority:** HIGH  
**Depends on:** EPIC-3

#### TASK-4.1: GradCAM Wrapper
- **Effort:** 3 points
- **Description:** Implement GradCAM gradient extraction using pytorch-grad-cam
- **Deliverables:**
  - `utils/gradcam.py::GradCAMExtractor` class
  - Initialize with model and target_layer (layer4)
  - `extract_gradients()` method returns raw gradients [2048, 7, 7]
- **Acceptance:**
  - GradCAM initializes without errors
  - Gradients extracted from cam.activations_and_grads.gradients[0]
  - Shape verified: [1, 2048, 7, 7] per sample

#### TASK-4.2: Gradient Collection Script
- **Effort:** 4 points
- **Description:** Collect gradients for all test samples
- **Deliverables:**
  - `collect_gradients.py` script with argparse CLI
  - Load trained model checkpoint
  - Iterate test set: forward → GradCAM → store gradient
  - Optional: save gradients.npz (5794 × 2048 × 7 × 7)
- **Acceptance:**
  - All 5794 test samples processed
  - Gradients stored with group_id and prediction metadata

#### TASK-4.3: Memory Optimization
- **Effort:** 3 points
- **Description:** Handle OOM during gradient collection
- **Deliverables:**
  - Batch inference with configurable batch_size (default 32)
  - CUDA cache clearing every 100 samples
  - Fallback to single-sample processing if OOM
- **Acceptance:** Gradient collection completes on 8GB GPU without OOM

---

### EPIC-5: GAIA-Z Computation
**Effort:** 8 points  
**Priority:** HIGH  
**Depends on:** EPIC-4

#### TASK-5.1: GAIA-Z Metric Implementation
- **Effort:** 3 points
- **Description:** Implement zero-deflation ratio computation
- **Deliverables:**
  - `utils/gaia_metrics.py::compute_gaia_z()` - Single sample, epsilon=1e-6
  - `utils/gaia_metrics.py::compute_gaia_z_batch()` - Vectorized for batch
  - Formula: count(|g| < epsilon) / total_elements
- **Acceptance:**
  - Output in range [0, 1]
  - Vectorized version matches single-sample results
  - Unit tests: all zeros → 1.0, no near-zeros → ≈0

#### TASK-5.2: GAIA-Z Computation Script
- **Effort:** 3 points
- **Description:** Compute GAIA-Z for all test samples
- **Deliverables:**
  - `compute_gaia_z.py` script with argparse CLI
  - Load gradients (from npz or recompute on-the-fly)
  - Compute GAIA-Z for each sample
  - Create DataFrame: [sample_id, group_id, is_minority, gaia_z, prediction, ground_truth, correct]
  - Save gaia_z_scores.csv
- **Acceptance:**
  - CSV contains 5794 rows
  - All GAIA-Z scores in [0, 1]

#### TASK-5.3: GAIA-Z Validation
- **Effort:** 2 points
- **Description:** Validate GAIA-Z scores are non-degenerate
- **Deliverables:**
  - `utils/gaia_metrics.py::validate_gaia_z_scores()` - Check std > 0.01, range [0,1], median ∈ [0.1, 0.9]
  - Raise error with diagnostic if validation fails
- **Acceptance:** Validation catches degenerate distributions (all same value, out of range)

---

### EPIC-6: Statistical Analysis
**Effort:** 10 points  
**Priority:** HIGH  
**Depends on:** EPIC-5

#### TASK-6.1: Group Separation
- **Effort:** 2 points
- **Description:** Separate GAIA-Z scores by minority/majority groups
- **Deliverables:**
  - `utils/statistical.py::separate_by_group()` - Returns (minority_scores, majority_scores)
  - minority: groups 1, 2; majority: groups 0, 3
- **Acceptance:** Correct sample counts for each group

#### TASK-6.2: Hypothesis Test
- **Effort:** 4 points
- **Description:** Perform two-sample t-test and compute effect size
- **Deliverables:**
  - `utils/statistical.py::perform_hypothesis_test()` - Welch's t-test via scipy.stats.ttest_ind
  - Compute: mean_minority, mean_majority, divergence, p_value, t_statistic
  - Compute Cohen's d: divergence / pooled_std
  - pooled_std = sqrt((var_minority + var_majority) / 2)
- **Acceptance:**
  - All metrics computed correctly
  - Returns dict with all required fields

#### TASK-6.3: Gate Evaluation
- **Effort:** 2 points
- **Description:** Evaluate success criteria and gate decision
- **Deliverables:**
  - Primary: (divergence ≥ 0.2) AND (p_value < 0.01)
  - Secondary: (cohens_d ≥ 0.8)
  - gate_pass = primary AND secondary
  - Print PASS/FAIL with diagnostic reasons
- **Acceptance:** Gate logic matches 03_prd.md specification

#### TASK-6.4: Statistical Test Script
- **Effort:** 2 points
- **Description:** End-to-end statistical analysis script
- **Deliverables:**
  - `statistical_test.py` script with argparse CLI
  - Load gaia_z_scores.csv
  - Run hypothesis test and gate evaluation
  - Save statistical_results.json
  - Print final verdict
- **Acceptance:** JSON contains all required fields, gate decision correct

---

### EPIC-7: Visualization & Reporting
**Effort:** 8 points  
**Priority:** MEDIUM  
**Depends on:** EPIC-6

#### TASK-7.1: Box Plots
- **Effort:** 3 points
- **Description:** Generate GAIA-Z distribution box plots
- **Deliverables:**
  - `utils/visualization.py::plot_boxplot_by_type()` - Minority vs majority
  - `utils/visualization.py::plot_boxplot_by_group()` - 4 groups with mean overlays
  - Save plots/gaia_z_boxplot_by_type.png, plots/gaia_z_boxplot_by_group.png
- **Acceptance:** Plots generated, visually correct

#### TASK-7.2: Histogram
- **Effort:** 2 points
- **Description:** Overlapping GAIA-Z histograms
- **Deliverables:**
  - `utils/visualization.py::plot_histogram()` - Minority (red, alpha=0.5) vs majority (blue, alpha=0.5)
  - Save plots/gaia_z_histogram.png
- **Acceptance:** Histogram shows both distributions, legend present

#### TASK-7.3: Summary Table
- **Effort:** 2 points
- **Description:** Per-group statistical summary table
- **Deliverables:**
  - `utils/visualization.py::create_summary_table()` - CSV with columns: [Group, N, GAIA-Z Mean, GAIA-Z Std, Accuracy]
  - Rows for groups 0-3, minority avg, majority avg, divergence
  - Save plots/statistical_summary.csv
- **Acceptance:** Table formatted correctly, all values present

#### TASK-7.4: Pipeline Script
- **Effort:** 1 point
- **Description:** End-to-end bash script
- **Deliverables:**
  - `run_experiment.sh` - Runs train → collect → compute → analyze
  - Checks for errors at each stage
- **Acceptance:** Script runs all 4 stages without manual intervention

---

## Failsafe Tasks

### FAILSAFE-1: Checkpoint Resume
- **Effort:** 2 points
- **Description:** Handle interrupted training
- **Deliverables:**
  - `train_model.py --resume` flag to load last checkpoint and continue
  - Restore model, optimizer, epoch counter
- **Acceptance:** Training resumes from correct epoch

### FAILSAFE-2: OOM Recovery
- **Effort:** 1 point
- **Description:** Graceful degradation on GPU memory errors
- **Deliverables:**
  - Catch RuntimeError("out of memory") during training
  - Reduce batch_size by half and retry
  - Log warning message
- **Acceptance:** Training continues with smaller batch if OOM

### FAILSAFE-3: Retrain on WGA Failure
- **Effort:** 1 point
- **Description:** Automatic retrain if WGA ≥ 80%
- **Deliverables:**
  - `train_model.py --auto-retry` flag
  - If WGA ≥ 80%, retrain with different seed (seed + 1)
  - Max 3 retries
- **Acceptance:** Retrain attempted if validation fails

---

## Execution Order

**Phase 1: Setup (Day 1)**
1. EPIC-1 (Environment) → EPIC-2 (Data)

**Phase 2: Training (Day 2-3)**
2. EPIC-3 (Training) + FAILSAFE-1,2,3

**Phase 3: Analysis (Day 3)**
3. EPIC-4 (GradCAM) → EPIC-5 (GAIA-Z) → EPIC-6 (Statistics) → EPIC-7 (Viz)

**Critical Path:** EPIC-1 → EPIC-2 → EPIC-3 → EPIC-4 → EPIC-5 → EPIC-6  
**Parallelizable:** EPIC-7 can start after EPIC-6.1 completes

---

## Success Criteria Checklist

**Training:**
- [ ] WGA < 80%
- [ ] Minority acc ≥ 60%
- [ ] Avg acc > 95%
- [ ] Checkpoint saved at `checkpoints/trained_model.pth`

**Gradient Collection:**
- [ ] 5794 gradients extracted
- [ ] Shapes verified: [2048, 7, 7] per sample
- [ ] No OOM errors

**GAIA-Z:**
- [ ] All scores in [0, 1]
- [ ] std > 0.01 (non-degenerate)
- [ ] CSV saved with 5794 rows

**Statistics:**
- [ ] Divergence computed
- [ ] p-value from Welch's t-test
- [ ] Cohen's d effect size
- [ ] Gate evaluation: PASS or FAIL

**Gate Decision:**
- [ ] IF (divergence ≥ 0.2) AND (p < 0.01) AND (d ≥ 0.8): h-e1 PASSES
- [ ] ELSE: h-e1 FAILS → ABANDON

---

**Document Status:** Complete  
**Version:** 1.0  
**Total Tasks:** 31 (7 Epics + 21 Subtasks + 3 Failsafe)  
**Estimated Effort:** 60 story points  
**Archon Task ID:** 28693385-e2a4-42df-ba9a-8f8e903c76bb
