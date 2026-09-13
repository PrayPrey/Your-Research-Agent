# Product Requirements Document: H-M1

**Hypothesis ID:** H-M1
**Type:** MECHANISM (Curvature Timing Analysis)
**Date:** 2026-04-14
**Author:** Anonymous
**Phase:** 3 - Implementation Planning
**Prerequisite:** H-E1 (PASSED - AUROC = 0.9452)

---

## Executive Summary

This PRD defines the implementation requirements for validating hypothesis H-M1: that minority samples exhibit delayed curvature stabilization in their loss trajectories compared to majority samples during standard ERM training.

**Core Claim:** Under ERM training, if we compute the second derivative of normalized loss curves, then minority samples will show delayed curvature stabilization (sign-flip epoch ≥3 epochs later than majority in ≥70% of seeds), because prolonged optimization conflict delays the transition from convex to stable loss landscape.

**Gate:** SHOULD_WORK - If this fails, pivot to alternative temporal signatures (e.g., variance patterns).

**Continuation:** This experiment extends H-E1's validated infrastructure (per-sample loss tracking) with curvature analysis.

---

## Problem Statement

### Background
H-E1 demonstrated that loss trajectory features can predict minority group membership with AUROC = 0.9452, establishing that trajectory divergence exists. H-M1 investigates the *mechanism* behind this divergence: specifically, whether minority samples show delayed curvature stabilization due to prolonged optimization conflict when spurious features contradict learned shortcuts.

### Opportunity
Understanding the curvature timing mechanism enables:
- Theoretical grounding for trajectory-based detection
- Potential early stopping criteria based on curvature patterns
- Insight into when/how minority samples diverge from majority

### Success Criteria
- **Primary:** Curvature timing gap ≥3 epochs in ≥70% of seeds
- **Baseline:** No systematic timing difference (gap = 0)
- **Statistical Requirement:** Multiple seeds (5+) for percentage-based criterion

---

## Functional Requirements

### FR-1: H-E1 Infrastructure Reuse

**FR-1.1: Dataset Loading (Inherited from H-E1)**
- Reuse Waterbirds dataset loading from H-E1
- Dataset path: `.data_cache/datasets/waterbirds/waterbird_complete95_forest2water2/`
- Preserve 4,795 training, 1,199 validation, 5,794 test samples
- Maintain group labels (4 groups: bird_type × background)

**FR-1.2: Model Architecture (Inherited from H-E1)**
- Reuse ResNet-50 with ImageNet pretrained weights
- Final layer: Linear(2048, 2) for binary classification
- No architectural modifications

**FR-1.3: Training Protocol (Extended from H-E1)**
- Optimizer: SGD (momentum=0.9, weight_decay=0.0001)
- Learning rate: 0.001
- Batch size: 128
- **Epochs: 20** (extended from H-E1's 5 epochs for full curvature analysis)
- Loss function: CrossEntropyLoss with `reduction='none'`

### FR-2: Extended Loss Trajectory Logging

**FR-2.1: Full Epoch Coverage**
- Log per-sample losses for ALL 20 epochs (not just epochs 1-5)
- Maintain loss history matrix: shape (num_samples, 20)
- Use deterministic evaluation pass after each training epoch

**FR-2.2: Multi-Seed Execution**
- Run training with 5+ different random seeds
- Seeds: [42, 123, 456, 789, 1011] minimum
- Store loss trajectories independently per seed
- Aggregate results across seeds for final evaluation

### FR-3: Curvature Computation

**FR-3.1: Loss Normalization**
- Normalize loss by initial value: L_norm[t] = L[t] / L[1]
- Handle edge cases: add epsilon (1e-8) to avoid division by zero
- Normalization provides scale invariance across samples

**FR-3.2: Second Derivative Computation**
- Apply optional Gaussian smoothing (sigma=1.0) to reduce noise
- Compute curvature via central differences: κ[t] = L[t+1] - 2*L[t] + L[t-1]
- Output shape: (num_samples, num_epochs - 2)

**FR-3.3: Curvature Parameters**
- Default smoothing sigma: 1.0
- Support configurable sigma for ablation (0.5, 1.0, 1.5, 2.0)

### FR-4: Sign-Flip Detection

**FR-4.1: Sign-Flip Definition**
- Sign-flip epoch: First epoch where curvature exceeds threshold for consecutive epochs
- Represents transition from convex (negative curvature) to stable (near-zero curvature)
- Default threshold: κ > -0.002

**FR-4.2: Detection Algorithm**
- Consecutive epochs requirement: 2 (default)
- For each sample, find first epoch t where:
  - curvature[t:t+consecutive] > threshold for all epochs in window
- If no sign-flip found, set to max_epoch + 2 (never stabilized)

**FR-4.3: Detection Parameters**
- Default curvature threshold: -0.002
- Default consecutive epochs: 2
- Support configurable parameters for ablation

### FR-5: Timing Gap Analysis

**FR-5.1: Group Classification**
- Minority groups: G2 (label=1) and G4 (label=3) - same as H-E1
- Majority groups: G1 (label=0) and G3 (label=2)
- Binary minority mask: (group_label == 1) | (group_label == 3)

**FR-5.2: Timing Gap Computation**
- Compute median sign-flip epoch for minority samples
- Compute median sign-flip epoch for majority samples
- Timing gap = median(minority) - median(majority)

**FR-5.3: Per-Seed Evaluation**
- Compute timing gap independently for each seed
- Track which seeds pass the ≥3 epoch criterion
- Compute pass rate: fraction of seeds with gap ≥ 3

### FR-6: Gate Evaluation

**FR-6.1: Success Criterion**
- **PASS:** Timing gap ≥ 3 epochs in ≥ 70% of seeds
- With 5 seeds: need 4/5 (80%) to pass
- With 10 seeds: need 7/10 (70%) to pass

**FR-6.2: Gate Output**
- pass_rate: Fraction of seeds meeting criterion
- mean_gap: Average timing gap across seeds
- std_gap: Standard deviation of timing gaps
- gate_passed: Boolean (pass_rate >= 0.70)

**FR-6.3: Failure Handling**
- If FAIL: Document actual gap values
- Pivot recommendation: Alternative temporal signatures

### FR-7: Visualization

**FR-7.1: Required Figures (Mandatory)**
- **Gate Metrics Comparison:** Bar chart showing:
  - Timing gap vs 3-epoch threshold (per seed)
  - Pass rate vs 70% threshold

**FR-7.2: Recommended Figures**
- **Curvature Trajectory Comparison:** 
  - Mean ± std curvature over epochs
  - Separate curves for minority vs majority
  - Sign-flip epoch markers

- **Sign-Flip Epoch Distribution:**
  - Histogram/violin of sign-flip epochs
  - Minority vs majority comparison

- **Per-Seed Timing Gap:**
  - Bar chart of gaps per seed
  - 3-epoch threshold line

**FR-7.3: Optional Figures**
- Normalized loss curves with curvature annotations
- Curvature heatmaps per group

**FR-7.4: Output**
- Save all figures to `{hypothesis_folder}/figures/`
- Format: PNG at 300 DPI

### FR-8: Results Logging

**FR-8.1: Metrics Output**
- Timing gap (mean ± std across seeds)
- Pass rate (fraction of seeds meeting criterion)
- Per-seed gap values
- Minority/majority median epochs

**FR-8.2: Results File**
- Save to `{hypothesis_folder}/code/outputs/results.json`
- Include all computed metrics
- Include gate evaluation result

**FR-8.3: Verification State Update**
- Update verification_state.yaml with:
  - validation.status = "COMPLETED"
  - gate.satisfied = (pass_rate >= 0.70)
  - gate.result = "PASS" or "FAIL"

---

## Non-Functional Requirements

### NFR-1: Reproducibility
- Fixed random seeds for all stochastic operations
- Same seed list across runs for comparability
- Deterministic CUDA operations where possible

### NFR-2: Performance
- Single GPU execution (select lowest memory usage GPU)
- Training completion within 60 minutes per seed (20 epochs vs H-E1's 5)
- Total runtime: ~5 hours for 5 seeds
- Memory usage < 16GB GPU RAM

### NFR-3: Code Quality
- Extend H-E1's codebase (LossTrajectoryTracker)
- Type hints for all function signatures
- Docstrings with tensor shape documentation
- Modular CurvatureTimingAnalyzer class

### NFR-4: Logging
- Console progress for epoch completion
- Per-seed progress indication
- Final metrics summary per seed and aggregate

---

## Technical Dependencies

### Python Packages (Same as H-E1 + additions)
- PyTorch >= 2.0
- torchvision >= 0.15
- scikit-learn >= 1.0
- numpy >= 1.20
- scipy >= 1.7 (for gaussian_filter1d)
- matplotlib >= 3.5
- tqdm (progress bars)

### Hardware
- Single NVIDIA GPU (8GB+ VRAM recommended)
- 32GB+ system RAM
- 10GB+ disk space for results (5 seeds × 20 epochs)

### Code Dependencies
- H-E1 codebase (dataset loading, model, training loop)
- H-E1 LossTrajectoryTracker class

---

## Data Flow

```
[H-E1 Infrastructure]
        ↓
[Waterbirds Dataset + ResNet-50]
        ↓
[ERM Training × 5 Seeds] ←→ [Per-Epoch Loss Logging (20 epochs)]
        ↓                            ↓
[Trained Models]          [Loss Trajectory Matrix (N, 20) × 5 seeds]
                                     ↓
                          [Loss Normalization (L / L₁)]
                                     ↓
                          [Gaussian Smoothing (σ=1.0)]
                                     ↓
                          [Curvature Computation (κ = d²L/dt²)]
                                     ↓
                          [Sign-Flip Detection per Sample]
                                     ↓
                          [Timing Gap: median(minority) - median(majority)]
                                     ↓
                          [Gate Check: gap ≥ 3 in ≥ 70% seeds]
```

---

## Success Metrics

| Metric | Target | Baseline | Gate |
|--------|--------|----------|------|
| Timing Gap | ≥ 3 epochs | 0 (no difference) | SHOULD_WORK |
| Pass Rate | ≥ 70% of seeds | N/A | SHOULD_WORK |
| Training Time | < 60 min/seed | N/A | Soft |
| Memory Usage | < 16GB | N/A | Soft |

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| No curvature timing difference | Medium | Medium (pivot to variance) | Multiple smoothing sigmas |
| Noisy curvature estimates | Medium | Low | Gaussian smoothing, consecutive epoch filter |
| Insufficient seeds for statistics | Low | Medium | Run 10 seeds if 5 inconclusive |
| Training instability across seeds | Low | Low | Fixed hyperparameters from H-E1 |
| Sign-flip not detectable | Medium | Medium | Adjust threshold, consecutive epochs |

---

## Implementation Priority

1. **P0 (Critical Path):**
   - Extend H-E1 training to 20 epochs
   - Multi-seed execution
   - Loss normalization
   - Curvature computation (second derivative)
   - Sign-flip detection
   - Timing gap computation
   - Gate evaluation

2. **P1 (Required):**
   - Visualization generation
   - Results logging
   - Verification state update

3. **P2 (Ablation/Nice to have):**
   - Variable smoothing sigma
   - Variable curvature threshold
   - Variable consecutive epochs

---

## Appendix: Traceability to Phase 2C

| PRD Section | Phase 2C Source |
|-------------|-----------------|
| Dataset specs | Continuation Context > Reusable Components |
| Model architecture | Continuation Context > Reusable Components |
| Training protocol | Training Protocol (extended to 20 epochs) |
| Curvature computation | Core Mechanism Implementation |
| Sign-flip detection | Core Mechanism Implementation |
| Success criteria | Gate Condition (gap ≥ 3 in ≥ 70% seeds) |
| Visualization | Visualization Requirements |

---

## Appendix: H-E1 Dependency Map

| H-E1 Component | Reuse in H-M1 | Modification |
|----------------|---------------|--------------|
| Dataset loading | Full reuse | None |
| Model architecture | Full reuse | None |
| Training loop | Extend | 20 epochs instead of 5 |
| LossTrajectoryTracker | Extend | Log all 20 epochs |
| Feature extraction | Not used | Replaced by curvature analysis |
| AUROC evaluation | Not used | Replaced by timing gap |

---

*Generated by Phase 3 Implementation Planning*
*Source: h-m1/02c_experiment_brief.md*
*Prerequisite: h-e1 (PASSED - AUROC = 0.9452)*
*Next: Architecture Design*
