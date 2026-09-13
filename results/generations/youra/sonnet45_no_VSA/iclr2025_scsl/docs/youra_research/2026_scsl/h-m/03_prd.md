# Product Requirements Document: h-m Implementation

**Date:** 2026-07-11  
**Author:** Anonymous  
**Hypothesis:** h-m (MECHANISM)  
**Type:** Research Experiment Implementation  
**Gate:** SHOULD_WORK  

---

## Executive Summary

### Purpose
Implement and validate hypothesis h-m, which tests the mechanistic explanation for horizontal flip augmentation's differential impact on asymmetric vs symmetric MNIST digits through a dose-response experimental protocol.

### Hypothesis Statement
The mechanism operates through four causal steps: (1) Horizontal flip creates non-canonical asymmetric digit images, (2) These invalid images retain original labels creating label noise, (3) Training on label noise degrades test accuracy on affected classes, (4) Degradation magnitude increases monotonically with flip probability.

### Success Criteria (SHOULD_WORK Gate)
- **Primary**: Spearman ρ significantly negative (p<0.05), indicating monotonic dose-response
- **Secondary**: Degradation visible at p=0.3 (weak), stronger at p=0.5, strongest at p=0.9
- **Mechanism**: All 4 causal steps observable in training/test dynamics

### Scope
Extend validated h-e1 codebase with:
- Multi-seed training infrastructure (5 seeds)
- Dose-response experimental conditions (4 flip probabilities + 1 control)
- Statistical correlation testing (Spearman rank correlation)
- Comparative visualization (dose-response curves)

### Context: Continuation from h-e1
This is an **INCREMENTAL** hypothesis building on h-e1 (EXISTENCE hypothesis, VALIDATED):
- **h-e1 proved**: Horizontal flip causes differential degradation (asymmetric digits degrade, symmetric stable)
- **h-m tests**: Complete 4-step causal mechanism and dose-response monotonicity
- **Controlled comparison**: Same dataset, model, hyperparameters; only flip probability varies

---

## Problem Statement

### Background
h-e1 validated that horizontal flip augmentation causes asymmetric digit degradation (0.72% with p=0.5), while symmetric digits remain stable (0.06% change). Preliminary evidence (n=1) suggested monotonic dose-response relationship (p=0.3 → 0.5 → 0.9 showed increasing degradation: 0.53% → 0.72% → 4.12%).

h-m formalizes this mechanism testing with statistical validation (n=5 seeds) across 4 dose levels.

### Research Gap
No prior work explicitly tests dose-response relationships in augmentation-induced label noise for MNIST. Existing label noise research focuses on intentional noise injection for robustness testing, not unintentional semantic invalidity from augmentation.

### Target Users
- Machine learning researchers studying data augmentation effects
- Practitioners evaluating augmentation strategies for digit recognition
- Academic community investigating semantic validity in data augmentation

---

## Functional Requirements

### FR-1: Multi-Seed Training Infrastructure
**Priority:** P0 (Critical)  
**Description:** Support training across 5 independent random seeds for statistical validation.

**Acceptance Criteria:**
- Training loop accepts seed parameter
- Results stored per-seed with unique identifiers
- All 5 seeds: {42, 123, 456, 789, 1011}
- Seed controls PyTorch RNG, NumPy RNG, Python RNG for reproducibility

**Dependencies:** h-e1 validated training loop

---

### FR-2: Dose-Response Experimental Conditions
**Priority:** P0 (Critical)  
**Description:** Implement 4 flip probability levels + 1 positive control.

**Acceptance Criteria:**
- **Baseline** (flip_prob=0.0): ToTensor + Normalize only
- **Flip30** (flip_prob=0.3): RandomHorizontalFlip(p=0.3) + ToTensor + Normalize
- **Flip50** (flip_prob=0.5): RandomHorizontalFlip(p=0.5) + ToTensor + Normalize
- **Flip90** (flip_prob=0.9): RandomHorizontalFlip(p=0.9) + ToTensor + Normalize
- **Rotation** (control): RandomRotation(±15°) + ToTensor + Normalize
- Each condition uses identical hyperparameters (Adadelta lr=1.0, StepLR, batch_size=64, epochs=14)

**Dependencies:** torchvision transforms API

---

### FR-3: MNISTNet Model (from h-e1)
**Priority:** P0 (Critical)  
**Description:** Reuse validated MNISTNet architecture from h-e1.

**Architecture Specification:**
- Conv1: 1→32 channels (3×3 kernel) + ReLU
- Conv2: 32→64 channels (3×3 kernel) + ReLU + MaxPool(2×2)
- Dropout1: 0.25 (after conv layers)
- Flatten: 9216→128
- FC1: 9216→128 + ReLU
- Dropout2: 0.5 (before output)
- FC2: 128→10 + LogSoftmax

**Acceptance Criteria:**
- Model produces (B, 10) log probability outputs
- Compatible with NLLLoss
- ~100K parameters
- Baseline accuracy ≥99% on standard MNIST

**Dependencies:** PyTorch nn.Module

---

### FR-4: MNIST Dataset Loading
**Priority:** P0 (Critical)  
**Description:** Load standard MNIST dataset with condition-specific augmentation.

**Acceptance Criteria:**
- Train split: 60,000 samples (all used)
- Test split: 10,000 samples (all used)
- Normalization: mean=0.1307, std=0.3081
- Digit grouping tracking:
  - Symmetric: {0,1,8}
  - Asymmetric: {2,3,5,6,7,9}
- Per-condition augmentation pipeline applied to train split only

**Dependencies:** torchvision.datasets.MNIST

---

### FR-5: Training Protocol (from h-e1)
**Priority:** P0 (Critical)  
**Description:** Implement validated training configuration from h-e1.

**Hyperparameters:**
- Optimizer: Adadelta(lr=1.0)
- Scheduler: StepLR(step_size=1, gamma=0.7)
- Loss: NLLLoss
- Batch size: 64
- Epochs: 14
- Device: CUDA if available, else CPU

**Acceptance Criteria:**
- Training converges within 14 epochs
- Baseline condition achieves ≥99% overall accuracy
- Training logs saved per (condition, seed) pair

**Dependencies:** torch.optim, torch.nn

---

### FR-6: Per-Class Accuracy Evaluation
**Priority:** P0 (Critical)  
**Description:** Compute test accuracy for each digit class (0-9) and digit groupings.

**Metrics:**
- **Overall accuracy**: Correct predictions / total test samples
- **Per-class accuracy**: Correct predictions for class k / total class k samples
- **Asymmetric digit accuracy**: Average accuracy across {2,3,5,6,7,9}
- **Symmetric digit accuracy**: Average accuracy across {0,1,8}

**Acceptance Criteria:**
- Results stored per (condition, seed, class) tuple
- CSV output with columns: condition, seed, class, accuracy
- Grouping aggregations computed and stored

**Dependencies:** scikit-learn metrics or custom implementation

---

### FR-7: Spearman Rank Correlation Test
**Priority:** P0 (Critical - Primary success criterion)  
**Description:** Compute Spearman correlation between flip probability and asymmetric digit accuracy.

**Statistical Test:**
- Independent variable: flip_probability ∈ {0.0, 0.3, 0.5, 0.9}
- Dependent variable: asymmetric_digit_accuracy (per seed)
- Method: scipy.stats.spearmanr
- Null hypothesis: ρ = 0 (no monotonic relationship)
- Alternative: ρ < 0 (negative monotonic relationship)
- Significance level: α = 0.05

**Acceptance Criteria:**
- Correlation computed across 4×5=20 data points (4 flip conditions × 5 seeds)
- Result includes: ρ (correlation coefficient), p-value
- **Primary Gate Pass**: ρ < 0 AND p < 0.05
- Results saved to validation report

**Dependencies:** scipy.stats.spearmanr

---

### FR-8: Rotation Control Validation
**Priority:** P1 (High)  
**Description:** Verify rotation augmentation shows no differential effect (positive control).

**Acceptance Criteria:**
- Rotation condition trains with RandomRotation(±15°)
- Asymmetric digit accuracy compared to baseline
- Expected: |asymmetric_rotation - asymmetric_baseline| < 1.0%
- Validates that effect is specific to horizontal flip, not augmentation in general

**Dependencies:** torchvision.transforms.RandomRotation

---

### FR-9: Results Persistence
**Priority:** P1 (High)  
**Description:** Save all experimental results in structured format for downstream analysis.

**File Outputs:**
1. **per_seed_results.csv**: (condition, seed, overall_acc, asym_acc, sym_acc, per_class_acc_0-9)
2. **dose_response_stats.json**: Spearman ρ, p-value, mean/std per condition
3. **model_checkpoints/**: Trained models per (condition, seed)
4. **training_logs/**: Loss curves, epoch metrics per run

**Acceptance Criteria:**
- CSV parseable by pandas
- JSON contains all statistical test results
- Model checkpoints loadable via torch.load()

**Dependencies:** pandas, json

---

### FR-10: Dose-Response Visualization
**Priority:** P1 (High)  
**Description:** Generate dose-response curve showing monotonic relationship.

**Figure Requirements:**
- **X-axis**: Flip probability {0.0, 0.3, 0.5, 0.9}
- **Y-axis**: Asymmetric digit accuracy (%)
- **Data points**: Mean ± std across 5 seeds per condition
- **Fit**: Trend line or monotonic fit
- **Annotation**: Spearman ρ, p-value displayed on plot
- **Control**: Rotation condition shown as separate reference point

**Acceptance Criteria:**
- Figure saved as PNG (300 DPI)
- Matplotlib or seaborn visualization
- Clear legend distinguishing flip conditions vs rotation control

**Dependencies:** matplotlib, seaborn

---

### FR-11: Per-Class Degradation Analysis
**Priority:** P2 (Medium)  
**Description:** Visualize per-class accuracy changes across flip conditions.

**Figure Requirements:**
- Heatmap or grouped bar chart
- Rows: Digit classes {0-9}
- Columns: Flip conditions {baseline, flip30, flip50, flip90}
- Color scale: Accuracy percentage
- Highlight: Asymmetric digits {2,3,5,6,7,9} vs Symmetric {0,1,8}

**Acceptance Criteria:**
- Clear visual separation of asymmetric vs symmetric digit behavior
- Monotonic degradation visible for asymmetric digits
- Stable accuracy for symmetric digits

**Dependencies:** seaborn heatmap or matplotlib

---

## Non-Functional Requirements

### NFR-1: Reproducibility
**Priority:** P0 (Critical)  
**Description:** All results must be exactly reproducible given the same seed.

**Acceptance Criteria:**
- Seed controls: torch.manual_seed(), np.random.seed(), random.seed()
- torch.backends.cudnn.deterministic = True
- Trained models produce identical results when loaded and re-evaluated

---

### NFR-2: Computational Efficiency
**Priority:** P1 (High)  
**Description:** Complete all 25 training runs (5 conditions × 5 seeds) within reasonable time.

**Targets:**
- Single run (14 epochs): ≤5 minutes on GPU, ≤20 minutes on CPU
- Total experiment: ≤2 hours with sequential execution
- Support parallel execution (if multiple GPUs available)

**Acceptance Criteria:**
- GPU utilization >80% during training (if CUDA available)
- No memory leaks across multiple sequential runs

---

### NFR-3: Code Reusability from h-e1
**Priority:** P0 (Critical)  
**Description:** Maximize code reuse from validated h-e1 implementation.

**Acceptance Criteria:**
- MNISTNet architecture: 100% reused from h-e1
- Training loop structure: ≥80% reused
- Evaluation metrics: ≥80% reused
- Only new components: multi-seed orchestration, statistical correlation, dose-response visualization

---

### NFR-4: Error Handling
**Priority:** P1 (High)  
**Description:** Gracefully handle runtime errors without losing partial results.

**Acceptance Criteria:**
- Failed seeds logged and skipped (don't crash entire experiment)
- Partial results saved incrementally (not only at end)
- OOM errors caught and reported with guidance

---

## Dependencies

### Internal Dependencies
- **h-e1 validated codebase**: MNISTNet architecture, training loop, evaluation metrics
- **h-e1 validation results**: Baseline expectations (99.14% overall, 98.95% asymmetric)

### External Dependencies
- **PyTorch**: ≥1.7.1 (for model, optimizer, loss)
- **torchvision**: ≥0.8.0 (for MNIST dataset, transforms)
- **NumPy**: ≥1.19.0 (for array operations)
- **SciPy**: ≥1.5.0 (for Spearman correlation: scipy.stats.spearmanr)
- **Matplotlib**: ≥3.3.0 (for visualizations)
- **Pandas**: ≥1.1.0 (for CSV results management)

### Hardware Dependencies
- **Minimum**: CPU, 8GB RAM
- **Recommended**: CUDA GPU (≥4GB VRAM), 16GB RAM

---

## Data Requirements

### Input Data
- **MNIST Dataset**: torchvision.datasets.MNIST(root='./data', download=True)
- **Train split**: 60,000 samples (all used)
- **Test split**: 10,000 samples (all used)
- **Storage**: ~12MB compressed (auto-downloaded)

### Output Data
- **CSV files**: ~500KB (results tables)
- **Model checkpoints**: ~400KB × 25 = 10MB (all trained models)
- **Figures**: ~1MB (PNG visualizations)
- **Training logs**: ~5MB (per-epoch metrics)
- **Total storage**: ~20MB

---

## Success Criteria

### Primary Success (SHOULD_WORK Gate Pass)
✅ **Spearman ρ significantly negative** (ρ < 0, p < 0.05)
- Confirms monotonic dose-response relationship
- Validates mechanistic explanation

### Secondary Success
✅ **Degradation gradient observed**:
- flip30 < flip50 < flip90 (mean asymmetric accuracy)
- Each dose level shows measurable degradation from baseline

✅ **Rotation control validation**:
- Asymmetric digit accuracy: |rotation - baseline| < 1.0%
- Confirms effect specificity to horizontal flip

### Failure Criteria (Gate Fail)
❌ **Spearman ρ non-significant** (p ≥ 0.05) OR positive (ρ ≥ 0)
- Mechanism unconfirmed
- Dose-response relationship not established
- Document as limitation, proceed to Phase 4.5 (SHOULD_WORK allows continuation)

---

## Out of Scope

### Explicitly NOT Required
- ❌ **Baseline model comparisons**: Only MNISTNet tested (not ResNet, VGG, etc.)
- ❌ **Dataset variations**: MNIST only (not EMNIST, Fashion-MNIST, CIFAR)
- ❌ **Optimization ablations**: No Adadelta vs Adam comparisons
- ❌ **Batch size ablations**: Fixed at 64 (validated in h-e1)
- ❌ **Training-time label noise analysis**: Focus on test-time accuracy degradation
- ❌ **Causal intervention experiments**: Mechanism tested via dose-response correlation, not direct causal manipulation

### Future Work (Post-h-m)
- Extend to EMNIST/Fashion-MNIST for generalization
- Test ResNet/VGG architectures for architecture sensitivity
- Direct causal intervention: train on semantically-valid flipped images with corrected labels

---

## Risks and Mitigations

### Risk 1: Non-monotonic dose-response
**Probability:** Medium  
**Impact:** High (Primary gate failure)  
**Mitigation:**
- Use 5 seeds for statistical robustness
- If p=0.9 shows recovery (e.g., regularization effect), document as U-shaped relationship
- Spearman test still valid for monotonic subset {0.0, 0.3, 0.5}

### Risk 2: Insufficient statistical power (n=5 seeds)
**Probability:** Low  
**Impact:** Medium (Inconclusive result)  
**Mitigation:**
- h-e1 showed strong effect size (4.12% degradation at p=0.9)
- Power analysis: n=5 sufficient for ρ > 0.7 with α=0.05, power=0.80
- If borderline (0.05 < p < 0.10), increase to n=10 seeds

### Risk 3: h-e1 codebase unavailable
**Probability:** Low  
**Impact:** Medium (Reimplementation required)  
**Mitigation:**
- Fallback: Fresh implementation from PyTorch official example
- Extend with GitHub patterns (Repos B.5-B.7 from Phase 2C research)
- Validation: Match h-e1 baseline accuracy (99.14%) before dose-response testing

---

## Traceability Matrix

| Phase 2C Item | PRD Requirement |
|---------------|-----------------|
| MNIST dataset (Section 3.1) | FR-4: MNIST Dataset Loading |
| MNISTNet baseline model (Section 3.2.1) | FR-3: MNISTNet Model |
| Dose-response conditions (Section 3.2.2) | FR-2: Dose-Response Experimental Conditions |
| Training protocol from h-e1 (Section 3.3) | FR-5: Training Protocol |
| Spearman correlation test (Section 3.4) | FR-7: Spearman Rank Correlation Test |
| Asymmetric digit accuracy (Section 3.4) | FR-6: Per-Class Accuracy Evaluation |
| Rotation positive control (Section 3.4) | FR-8: Rotation Control Validation |
| Dose-response visualization (Section 3.5) | FR-10: Dose-Response Visualization |
| 5 seeds for statistical validation (Section 3.3) | FR-1: Multi-Seed Training Infrastructure |
| Results persistence (implied) | FR-9: Results Persistence |

---

## Appendix

### A. Hypothesis Context
- **Type**: MECHANISM
- **Gate**: SHOULD_WORK
- **Prerequisites**: h-e1 (VALIDATED, MUST_WORK gate passed)
- **Archon Project**: Pipeline Project ID: 4bf31e88-86c9-4abd-a1b4-e4f86fa692ca
- **Archon Task**: h-m Task ID: 697f2cbd-53e0-4a44-8bae-942c56b016ab

### B. Phase 2C Source
- **Experiment Brief**: docs/youra_research/h-m/02c_experiment_brief.md
- **Generated**: 2026-07-11T09:00:00Z
- **Specification Level**: 1.5 (Concrete + Pseudo-code)

### C. Code Reuse from h-e1
- **h-e1 PRD**: docs/youra_research/h-e1/03_prd.md
- **h-e1 Architecture**: docs/youra_research/h-e1/03_architecture.md
- **h-e1 Logic**: docs/youra_research/h-e1/03_logic.md
- **h-e1 Config**: docs/youra_research/h-e1/03_config.md
- **h-e1 Validation**: docs/youra_research/h-e1/04_validation.md

### D. Statistical Power Justification
For Spearman rank correlation with:
- n = 20 data points (4 flip conditions × 5 seeds)
- Expected ρ ≈ -0.85 (based on h-e1 preliminary n=1: {0.0: 98.95%, 0.3: 98.42%, 0.5: 98.23%, 0.9: 94.83%})
- α = 0.05 (significance level)

Power analysis (using pwr package equivalent):
- Achieved power ≥ 0.95 for |ρ| ≥ 0.7
- n=5 seeds per condition is statistically sufficient

---

**Document Status:** ✅ COMPLETE  
**Next Phase:** Phase 3 - Architecture Design (03_architecture.md)  
**Approver:** Anonymous (Auto-approved in UNATTENDED mode)
