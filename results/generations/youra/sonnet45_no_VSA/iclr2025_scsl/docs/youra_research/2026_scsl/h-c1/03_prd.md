# Product Requirements Document (PRD): h-c1

**Hypothesis ID:** h-c1  
**Date:** 2026-07-11  
**Author:** Phase 3 Implementation Planning  
**Experiment Brief Source:** 02c_experiment_brief.md

---

## Executive Summary

### Hypothesis Statement
Rotation ±15° augmentation does NOT cause differential degradation on asymmetric digits (positive control isolating semantic effect)

### Hypothesis Type
**CONDITION (Positive Control)**

This hypothesis validates that rotation augmentation, which preserves semantic validity (rotated digits remain recognizable), does NOT selectively harm asymmetric digits. It serves as a positive control for H-E1, isolating the semantic invalidity mechanism.

### Success Criteria (PoC - Direction-based)
- Rotation condition does NOT create larger asymmetric accuracy gap than baseline
- Formally: `|asymmetric_gap_rotation| ≤ |asymmetric_gap_baseline|` OR both gaps < 2%
- Where: `asymmetric_gap = (asymmetric_accuracy - symmetric_accuracy)`
- **PASS** = Rotation does NOT selectively harm asymmetric digits
- **FAIL** = Rotation DOES harm asymmetric digits differentially (invalidates H-E1 interpretation)

### Gate Information
**Gate Type:** MUST_WORK

**Consequence if Fails:** CRITICAL - If rotation DOES cause differential degradation on asymmetric digits, the semantic invalidity mechanism is NOT isolated. This invalidates H-E1's interpretation that horizontal flip harms asymmetric digits due to semantic invalidity (not just general augmentation effects or digit asymmetry itself).

**Recovery Action:** Use alternative positive control (translation, brightness) or ABORT main hypothesis.

---

## Background & Motivation

### Research Context
This hypothesis is part of a broader investigation into semantic validity in data augmentation. The key question is: does horizontal flip (which creates semantically invalid labels for asymmetric digits like 2→?) harm model performance due to semantic invalidity, or merely due to general augmentation effects?

**Positive Control Logic:**
- **H-E1 (main hypothesis):** Horizontal flip DOES harm asymmetric digits differentially
- **H-C1 (this hypothesis):** Rotation DOES NOT harm asymmetric digits differentially
- **Joint interpretation:** Semantic invalidity (flip creates ambiguous labels) causes harm, not general augmentation or asymmetry

### Why This Experiment Matters
1. **Validates semantic invalidity mechanism** - Confirms rotation (semantically valid) behaves differently than flip (semantically invalid)
2. **Controls for augmentation effects** - Isolates semantic validity from general augmentation effects
3. **Controls for digit asymmetry** - Shows asymmetric digits can handle some augmentations (just not semantically invalid ones)

### Prior Work
**From Implementation Research (02c_experiment_brief.md):**
- **facundoq/rotational_invariance_data_augmentation**: Rotation augmentation does NOT harm MNIST accuracy
- **emrebaranarca/computer-vision-mnist-cnn**: ±15° rotation with maintained high accuracy
- **PyTorch Official Tutorial**: Standard MNIST CNN architecture (~99% baseline accuracy)

**Key Finding:** Rotation augmentation is a standard, well-validated technique that maintains or improves MNIST accuracy across all digit classes.

---

## Functional Requirements

### FR1: Dataset Management
**Priority:** P0 (Critical)

**Requirements:**
- **FR1.1:** Load MNIST dataset (60k train, 10k test) via torchvision.datasets
- **FR1.2:** Apply baseline transform (ToTensor + Normalize(0.1307, 0.3081)) for baseline condition
- **FR1.3:** Apply rotation transform (RandomRotation(15°) + ToTensor + Normalize) for rotation condition
- **FR1.4:** Use baseline transform for test set (no augmentation) in both conditions
- **FR1.5:** Implement train/val split from training set (e.g., 90%/10% or use full train set)

**Success Metric:** DataLoader successfully loads batches of shape (batch_size, 1, 28, 28)

---

### FR2: Model Architecture
**Priority:** P0 (Critical)

**Requirements:**
- **FR2.1:** Implement Standard CNN architecture (PyTorch Official pattern):
  - Conv2d(1→32, kernel=3, stride=1) + ReLU
  - Conv2d(32→64, kernel=3, stride=1) + ReLU
  - MaxPool2d(2×2)
  - Dropout2d(0.25)
  - Flatten
  - Linear(9216→128) + ReLU
  - Dropout(0.5)
  - Linear(128→10)
  - LogSoftmax(dim=1)
- **FR2.2:** Initialize model with default PyTorch initialization (no custom init)
- **FR2.3:** Total parameters ~1.2M (suitable for MNIST)
- **FR2.4:** Use SAME architecture for baseline and rotation conditions

**Success Metric:** Model forward pass produces output shape (batch_size, 10) with log probabilities

---

### FR3: Training Protocol
**Priority:** P0 (Critical)

**Requirements:**
- **FR3.1:** Optimizer: Adam (lr=0.001, default betas, no weight decay)
- **FR3.2:** Loss Function: CrossEntropyLoss (expects log probabilities from LogSoftmax)
- **FR3.3:** Batch Size: 64
- **FR3.4:** Epochs: 30 (maximum)
- **FR3.5:** Learning Rate: Fixed (no scheduler)
- **FR3.6:** Early Stopping: Patience 5 epochs on validation accuracy
- **FR3.7:** Random Seed: Fixed (seed=42 for reproducibility)
- **FR3.8:** Train TWO separate models:
  - Model 1: Baseline (no augmentation, only normalization)
  - Model 2: Rotation (±15° rotation augmentation during training)

**Success Metric:** 
- Both models converge within 30 epochs
- Baseline model achieves ~99% test accuracy (validation of implementation)
- Rotation model achieves ≥99% test accuracy (validates rotation does not harm overall performance)

---

### FR4: Evaluation & Metrics
**Priority:** P0 (Critical)

**Requirements:**
- **FR4.1:** Compute per-class test accuracy for all 10 digit classes {0-9}
- **FR4.2:** Compute symmetric digit accuracy: mean over {0, 1, 8}
- **FR4.3:** Compute asymmetric digit accuracy: mean over {2, 3, 5, 6, 7, 9}
- **FR4.4:** Compute differential effect: (asymmetric - symmetric) accuracy gap
- **FR4.5:** Collect metrics for BOTH baseline and rotation conditions
- **FR4.6:** Generate comparison: `|asymmetric_gap_rotation| vs |asymmetric_gap_baseline|`
- **FR4.7:** Implement direction-based success check (no statistical test for PoC):
  - PASS if `|asym_gap_rotation| ≤ |asym_gap_baseline|` OR both gaps < 2%
  - FAIL otherwise

**Success Metric:** 
- Per-class accuracy computed correctly (sum to 10 classes)
- Differential effect values computed for both conditions
- Success check correctly identifies PASS/FAIL

---

### FR5: Visualization
**Priority:** P0 (Critical)

**Requirements:**
- **FR5.1:** **Gate Metrics Comparison** (mandatory figure):
  - Bar chart comparing baseline vs rotation conditions
  - X-axis: Condition (Baseline, Rotation)
  - Y-axis: Absolute differential effect `|asymmetric - symmetric|` accuracy
  - Target line at 2% threshold
  - Title: "H-C1 Gate Metrics: Rotation Differential Effect vs Baseline"
- **FR5.2:** **Per-Class Accuracy Bar Chart**:
  - X-axis: Digit classes {0-9}
  - Y-axis: Test accuracy (%)
  - Two bars per class: Baseline (blue), Rotation (orange)
  - Background shading: Symmetric {0,1,8} vs Asymmetric {2,3,5,6,7,9}
- **FR5.3:** **Accuracy Gap Comparison**:
  - Bar chart: (Asymmetric - Symmetric) accuracy for both conditions
  - Expected: Both near zero
- **FR5.4:** **Training Curves**:
  - Train/Val loss over epochs for both conditions
  - Shows convergence behavior
- **FR5.5:** Save all figures to `docs/youra_research/h-c1/figures/`

**Success Metric:** All 4 figures generated and saved to disk

---

### FR6: Experiment Artifacts
**Priority:** P1 (High)

**Requirements:**
- **FR6.1:** Save trained model checkpoints for both conditions:
  - `h-c1/checkpoints/baseline_model.pt`
  - `h-c1/checkpoints/rotation_model.pt`
- **FR6.2:** Save training logs (loss per epoch) as JSON:
  - `h-c1/logs/baseline_training.json`
  - `h-c1/logs/rotation_training.json`
- **FR6.3:** Save evaluation results as JSON:
  - `h-c1/results/evaluation_metrics.json` containing:
    - Per-class accuracy (baseline & rotation)
    - Symmetric/asymmetric group accuracy
    - Differential effects
    - Success check result (PASS/FAIL)
- **FR6.4:** Generate validation report (04_validation.md) with:
  - Summary of results
  - Success check outcome
  - Key findings
  - Figures (embedded or linked)

**Success Metric:** All artifacts saved to correct paths, validation report generated

---

## Non-Functional Requirements

### NFR1: Reproducibility
**Priority:** P0 (Critical)

**Requirements:**
- **NFR1.1:** Set random seeds (Python, NumPy, PyTorch) to 42
- **NFR1.2:** Use deterministic algorithms where possible (torch.use_deterministic_algorithms)
- **NFR1.3:** Document hardware used (CPU/GPU model, PyTorch version)
- **NFR1.4:** Log all hyperparameters to JSON file

**Success Metric:** Re-running experiment produces identical results (±0.1% accuracy variance)

---

### NFR2: Performance & Efficiency
**Priority:** P2 (Medium)

**Requirements:**
- **NFR2.1:** Training should complete within 30 minutes on modern GPU (e.g., NVIDIA RTX 3090)
- **NFR2.2:** Training should complete within 2 hours on CPU (fallback)
- **NFR2.3:** Memory footprint ≤ 2GB GPU VRAM (MNIST is small)

**Success Metric:** Experiment completes within time budget

---

### NFR3: Code Quality
**Priority:** P1 (High)

**Requirements:**
- **NFR3.1:** Code follows PEP 8 style guide
- **NFR3.2:** Functions have docstrings (Google style)
- **NFR3.3:** Type hints for function signatures
- **NFR3.4:** Error handling for file I/O, data loading, device availability
- **NFR3.5:** Logging to console (tqdm progress bars, epoch summaries)

**Success Metric:** Code passes static analysis (pylint, mypy) with minimal warnings

---

### NFR4: Documentation
**Priority:** P1 (High)

**Requirements:**
- **NFR4.1:** README.md in h-c1/ folder with:
  - Hypothesis statement
  - How to run the experiment
  - Expected output files
  - Dependencies (requirements.txt)
- **NFR4.2:** Inline comments for non-obvious logic (e.g., differential effect calculation)
- **NFR4.3:** Validation report (04_validation.md) with clear PASS/FAIL determination

**Success Metric:** User can reproduce experiment from README without external guidance

---

## User Stories

### US1: Baseline Training
**As a** researcher  
**I want to** train a baseline MNIST CNN without augmentation  
**So that** I can establish expected performance (~99% accuracy)

**Acceptance Criteria:**
- Baseline model trains on MNIST with only normalization (no augmentation)
- Achieves ~99% test accuracy
- Per-class accuracy computed and saved

---

### US2: Rotation Augmentation Training
**As a** researcher  
**I want to** train a MNIST CNN with ±15° rotation augmentation  
**So that** I can test whether rotation causes differential degradation on asymmetric digits

**Acceptance Criteria:**
- Rotation model trains on MNIST with RandomRotation(15°)
- Achieves ≥99% test accuracy (validates rotation does not harm overall performance)
- Per-class accuracy computed and saved

---

### US3: Differential Effect Analysis
**As a** researcher  
**I want to** compare asymmetric vs symmetric digit accuracy between baseline and rotation conditions  
**So that** I can determine if rotation causes differential degradation

**Acceptance Criteria:**
- Differential effect computed for baseline: (asym_acc - sym_acc)
- Differential effect computed for rotation: (asym_acc - sym_acc)
- Comparison shows rotation effect ≤ baseline effect (or both near zero)

---

### US4: Visualization & Reporting
**As a** researcher  
**I want to** see visual comparisons of baseline vs rotation performance  
**So that** I can quickly assess whether the positive control passed

**Acceptance Criteria:**
- Gate metrics comparison figure shows rotation effect vs baseline
- Per-class accuracy bar chart shows no selective harm to asymmetric digits
- Validation report clearly states PASS/FAIL with reasoning

---

## Technical Constraints

### TC1: Dataset
- **Constraint:** Must use MNIST standard split (60k train, 10k test)
- **Rationale:** Standard benchmark for reproducibility
- **Impact:** Cannot use custom train/test splits

### TC2: Model Architecture
- **Constraint:** Must use Standard CNN (PyTorch Official pattern)
- **Rationale:** Baseline architecture from 02c_experiment_brief.md research
- **Impact:** Cannot use ResNet, VGG, or other architectures (would invalidate comparison to researched baselines)

### TC3: Augmentation
- **Constraint:** Rotation must be exactly ±15° (RandomRotation(15))
- **Rationale:** Matches researched implementation (emrebaranarca/computer-vision-mnist-cnn)
- **Impact:** Cannot use different rotation ranges

### TC4: Evaluation
- **Constraint:** Must use direction-based success check (no statistical test)
- **Rationale:** This is a PoC positive control (CONDITION hypothesis), not a main effect test
- **Impact:** Cannot use Wilcoxon test, t-test, or Cohen's d (reserved for H-E1)

---

## Dependencies

### External Libraries
- **PyTorch ≥ 2.0:** Core deep learning framework
- **torchvision ≥ 0.15:** MNIST dataset, transforms
- **torchmetrics ≥ 1.0:** Accuracy metrics
- **matplotlib ≥ 3.5:** Visualization
- **numpy ≥ 1.24:** Numerical operations
- **tqdm ≥ 4.65:** Progress bars

### Data Dependencies
- **MNIST Dataset:** Auto-downloaded via torchvision.datasets.MNIST
- **Cache Path:** ./data/MNIST (auto-created if missing)

### Compute Resources
- **GPU (Recommended):** CUDA-capable GPU (1-2GB VRAM sufficient)
- **CPU (Fallback):** Multi-core CPU (experiment will take longer)

---

## Risk Assessment

### R1: Baseline Model Underperforms
**Risk:** Baseline model achieves <99% accuracy (expected ~99%)  
**Probability:** LOW (Standard CNN on MNIST is well-validated)  
**Impact:** MEDIUM (invalidates implementation quality, not hypothesis)  
**Mitigation:** 
- Verify data loading (correct normalization parameters)
- Check model architecture matches PyTorch Official pattern
- Increase epochs if needed (up to 50)

---

### R2: Rotation Model Underperforms
**Risk:** Rotation model achieves <99% accuracy  
**Probability:** VERY LOW (rotation augmentation is known to maintain/improve accuracy)  
**Impact:** HIGH (could falsely indicate rotation harms overall performance)  
**Mitigation:**
- Verify RandomRotation is applied only during training (not test)
- Check rotation range is ±15° (not ±90° or other extreme values)
- Inspect augmented images visually (ensure digits remain recognizable)

---

### R3: Rotation Creates Differential Effect
**Risk:** Rotation DOES harm asymmetric digits differentially (hypothesis FAILS)  
**Probability:** VERY LOW (rotation preserves semantic validity)  
**Impact:** CRITICAL (invalidates H-E1 interpretation, requires alternative control)  
**Mitigation:**
- Re-run with different random seed to rule out fluke
- Try alternative positive control (translation ±2px, brightness ±20%)
- If confirmed: ABORT H-E1 hypothesis, re-evaluate semantic validity mechanism

---

### R4: Small Sample Size (Edge Case Variance)
**Risk:** Some digit classes (e.g., class 5) have high variance in per-class accuracy  
**Probability:** LOW (MNIST test set has 1000 samples per class)  
**Impact:** LOW (differential effect is averaged over 3 symmetric and 6 asymmetric classes)  
**Mitigation:**
- Use full MNIST test set (10k samples, ~1000 per class)
- Report per-class accuracy variance
- Focus on group-level differential effect (not individual class variance)

---

## Success Metrics & KPIs

### Primary Success Metric
**Differential Effect Comparison:**
- Rotation condition differential effect ≤ Baseline differential effect
- OR both differential effects < 2%

**Target:** PASS (rotation does NOT selectively harm asymmetric digits)

---

### Secondary Success Metrics
1. **Overall Accuracy (Baseline):** ~99% ± 0.5%
   - Validates implementation quality
2. **Overall Accuracy (Rotation):** ≥99%
   - Validates rotation is a valid augmentation
3. **Symmetric Digit Accuracy Stability:** No degradation in {0,1,8} accuracy between conditions
   - Validates rotation does not harm any digit group

---

### Validation Checkpoints
- [ ] Baseline model converges within 30 epochs
- [ ] Rotation model converges within 30 epochs
- [ ] Baseline achieves ~99% test accuracy
- [ ] Rotation achieves ≥99% test accuracy
- [ ] Per-class accuracy computed for all 10 classes
- [ ] Differential effect computed for both conditions
- [ ] Gate metrics comparison figure generated
- [ ] Success check determines PASS/FAIL
- [ ] Validation report (04_validation.md) written

---

## Timeline & Milestones

### Phase 4 (Coding & PoC Validation)
**Estimated Duration:** 2-4 hours (implementation + validation)

**Milestones:**
1. **M1: Environment Setup** (30 min)
   - Install dependencies
   - Verify CUDA availability
   - Download MNIST dataset
2. **M2: Baseline Training** (30 min)
   - Implement Standard CNN
   - Train baseline model
   - Evaluate on test set
3. **M3: Rotation Training** (30 min)
   - Implement rotation augmentation
   - Train rotation model
   - Evaluate on test set
4. **M4: Evaluation & Visualization** (1 hour)
   - Compute per-class accuracy
   - Calculate differential effects
   - Generate all 4 required figures
5. **M5: Validation Report** (30 min)
   - Write 04_validation.md
   - Document success check outcome
   - Archive artifacts

---

## Appendix: Reference Implementations

### A.1: PyTorch Official MNIST Tutorial
**URL:** https://docs.pytorch.org/tutorials/recipes/recipes/defining_a_neural_network.html  
**Used For:** Baseline CNN architecture, optimizer configuration

### A.2: emrebaranarca/computer-vision-mnist-cnn
**URL:** https://github.com/emrebaranarca/computer-vision-mnist-cnn  
**Used For:** Rotation parameter (±15°), training protocol (Adam lr=0.001, epochs=30, batch=128)

### A.3: facundoq/rotational_invariance_data_augmentation
**URL:** https://github.com/facundoq/rotational_invariance_data_augmentation  
**Used For:** Validation that rotation does NOT harm MNIST accuracy

---

## Document History

| Version | Date       | Author               | Changes                          |
|---------|------------|----------------------|----------------------------------|
| 1.0     | 2026-07-11 | Phase 3 Planning     | Initial PRD creation             |

---

**Next Step:** Phase 3 Architecture Design (03_architecture.md)  
**Status:** READY FOR IMPLEMENTATION PLANNING
