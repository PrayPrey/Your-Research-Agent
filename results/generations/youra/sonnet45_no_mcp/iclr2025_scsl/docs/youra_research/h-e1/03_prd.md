# Product Requirements Document (PRD)
# Hypothesis h-e1: MI Growth Rate Asymmetry Across Paradigms

**Version:** 1.0  
**Date:** 2026-04-24  
**Author:** Anonymous
**Hypothesis Type:** EXISTENCE (PoC)  
**Task Budget:** LIGHT (≤15 tasks)

---

## Executive Summary

Implement a proof-of-concept experiment to test whether simpler features exhibit faster mutual information (MI) growth rates than complex features across supervised, self-supervised, and reinforcement learning paradigms. This is a foundation hypothesis validating the core phenomenon before mechanism exploration.

**Success Criteria:** Code runs without error across 3 paradigms, with effect direction d/dt I(Z_s; H_t) > d/dt I(Z_c; H_t) observed in at least 2 paradigms (PoC validation - no statistical testing required).

---

## Problem Statement

### Research Question
Do models trained via gradient descent preferentially encode simpler features faster than complex features, and does this phenomenon generalize across supervised, self-supervised, and reinforcement learning paradigms?

### Hypothesis
In controlled generative environments with pre-registered complexity C(Z_s) < C(Z_c), early-phase MI growth rates satisfy d/dt I(Z_s; H_t) > d/dt I(Z_c; H_t) across supervised, SSL, and RL paradigms.

### Gate Condition
**MUST_WORK**: If this hypothesis fails, the entire research direction is invalid (no cross-paradigm MI asymmetry exists).

---

## Functional Requirements

### FR-1: Dataset Generation - Colored MNIST
**Priority:** P0 (Critical)  
**Complexity:** Medium

**Description:** Create Colored MNIST dataset with controlled spurious correlation.

**Acceptance Criteria:**
- Load MNIST dataset (60k train, 10k test)
- Apply color assignment with 90% spurious correlation to digit labels
- Return 4-tuple: (colored_image, digit_label, color_factor, shape_factor)
- Verify ground-truth factor access for MI computation
- Confirm programmatic-api type (real MNIST + controlled color factors)

**Dependencies:** torchvision.datasets.MNIST

**Technical Specification:**
```python
# ColoredMNISTWrapper class
# Input: MNIST dataset, spurious_prob=0.9
# Output: (B, 3, 28, 28) RGB images with color/shape factors
# Complexity: C(color) = 1 dimension, C(shape) ≈ 14-20 dimensions
```

---

### FR-2: Model Architecture - ResNet-18 (Modified)
**Priority:** P0 (Critical)  
**Complexity:** Low

**Description:** Implement ResNet-18 baseline modified for 28×28 MNIST input.

**Acceptance Criteria:**
- Load torchvision ResNet-18 architecture
- Modify conv1: kernel_size=3, stride=1, padding=1 (28×28 input)
- Remove maxpool layer (replace with Identity)
- Modify final layer: Linear(512, 10) for digit classification
- Train from scratch (no pretrained weights)

**Dependencies:** torchvision.models.resnet18

**Technical Specification:**
```python
# Input: (B, 3, 28, 28) colored MNIST
# Encoder output: (B, 512) from layer4
# Final output: (B, 10) class logits
```

---

### FR-3: MI Tracking Infrastructure
**Priority:** P0 (Critical)  
**Complexity:** High

**Description:** Implement MI tracker to measure I(Z; H_t) during training.

**Acceptance Criteria:**
- Extract representations from layer4 at checkpoint intervals (every 50 steps)
- Compute I(Z_s; H_t) and I(Z_c; H_t) using sklearn mutual_info_score
- Discretize continuous representations (KBinsDiscretizer, n_bins=20)
- Store MI trajectories for all 3 paradigms
- Log timesteps for derivative computation

**Dependencies:** sklearn.metrics.mutual_info_score, sklearn.preprocessing.KBinsDiscretizer

**Technical Specification:**
```python
# MITracker class
# Methods: compute_mi_checkpoint(dataloader, step)
# Output: mi_history dict with Z_spurious, Z_causal, timesteps arrays
# Integration: Hook into training loop as callback
```

---

### FR-4: Training Protocol - Supervised Learning
**Priority:** P0 (Critical)  
**Complexity:** Medium

**Description:** Implement supervised digit classification training.

**Acceptance Criteria:**
- Task: Predict digit from colored MNIST image
- Optimizer: SGD(momentum=0.9, weight_decay=5e-4)
- Learning rate: 0.1 with cosine annealing
- Batch size: 128
- Epochs: 200
- Loss: CrossEntropyLoss
- Seed: 1 (fixed for PoC)
- Call MI tracker every 50 steps

**Dependencies:** torch.optim.SGD, torch.nn.CrossEntropyLoss

---

### FR-5: Training Protocol - Self-Supervised Learning (SimCLR)
**Priority:** P0 (Critical)  
**Complexity:** High

**Description:** Implement contrastive self-supervised learning.

**Acceptance Criteria:**
- Task: Contrastive learning on colored MNIST
- Optimizer: SGD(momentum=0.9)
- Learning rate: 0.03 with cosine annealing
- Batch size: 256
- Epochs: 200
- Loss: NT-Xent (normalized temperature-scaled cross entropy)
- Temperature: 0.5
- Seed: 1 (fixed for PoC)
- Call MI tracker every 50 steps

**Dependencies:** Custom NT-Xent loss implementation

**Technical Specification:**
```python
# NT-Xent loss: -log(exp(sim(z_i, z_j)/τ) / Σ_k exp(sim(z_i, z_k)/τ))
# Augmentation: Random crops, color jitter (preserve spurious correlation)
```

---

### FR-6: Training Protocol - Reinforcement Learning (Policy Gradient)
**Priority:** P0 (Critical)  
**Complexity:** Very High

**Description:** Implement policy gradient RL with colored digit cues.

**Acceptance Criteria:**
- Task: Grid navigation with colored digit state representations
- Optimizer: Adam(lr=3e-4)
- Policy network: ResNet-18 encoder + actor-critic heads
- Batch size: 32 episodes
- Epochs: 200 (equivalent training steps)
- Loss: Policy gradient + value loss
- Entropy coefficient: 0.01
- Seed: 1 (fixed for PoC)
- Call MI tracker every 50 steps

**Dependencies:** Custom RL environment, torch.optim.Adam

**Technical Specification:**
```python
# Environment: Grid navigation (10×10 grid)
# State: Colored digit image at current position
# Action space: {Up, Down, Left, Right}
# Reward: +1 for goal, -0.01 per step
# Policy: Actor-critic with shared ResNet-18 encoder
```

---

### FR-7: MI Derivative Estimation
**Priority:** P0 (Critical)  
**Complexity:** Medium

**Description:** Compute d/dt I(Z; H_t) via spline fitting.

**Acceptance Criteria:**
- Fit UnivariateSpline to MI trajectories (smoothing factor s=0.1)
- Compute analytic derivative using spline.derivative()
- Extract early-phase derivatives (first 10% of training steps)
- Compare d/dt I(Z_s; H_t) vs d/dt I(Z_c; H_t)
- Store results for visualization

**Dependencies:** scipy.interpolate.UnivariateSpline

**Technical Specification:**
```python
# Input: timesteps array, mi_values array
# Spline smoothing: s=0.1 (balanced smoothness/fidelity)
# Output: mi_derivative array (same length as timesteps)
```

---

### FR-8: Evaluation Metrics Computation
**Priority:** P0 (Critical)  
**Complexity:** Low

**Description:** Compute standard task performance metrics.

**Acceptance Criteria:**
- Supervised: Test accuracy (expect ~98-99%)
- SSL: Linear probing accuracy after training (expect ~95%+)
- RL: Episode return and policy convergence
- Log all metrics to CSV files

**Dependencies:** torchmetrics.Accuracy

---

### FR-9: Visualization Generation
**Priority:** P1 (High)  
**Complexity:** Medium

**Description:** Generate required and recommended figures.

**Acceptance Criteria:**
- **Required**: Gate metrics bar chart (d/dt I comparison across paradigms)
- MI trajectory curves (3 subplots for 3 paradigms)
- Derivative comparison across paradigms
- Complexity vs MI growth rate scatter plot
- Gradient norm validation plot
- Save all figures to h-e1/figures/

**Dependencies:** matplotlib, seaborn

---

### FR-10: Early-Phase Window Detection
**Priority:** P1 (High)  
**Complexity:** Medium

**Description:** Identify early-phase window t_0 for each paradigm.

**Acceptance Criteria:**
- Method 1: First 10% of training steps
- Method 2: Time to reach 30% of final performance
- Validate via gradient norm tracking (ensure active gradient flow)
- Store t_0 for each paradigm
- Use paradigm-adaptive windows for derivative extraction

**Dependencies:** None (analysis logic)

---

## Non-Functional Requirements

### NFR-1: Reproducibility
- Fixed random seeds (seed=1) for all paradigms
- Deterministic data loading and augmentation
- Log all hyperparameters to config file

### NFR-2: Performance
- Single GPU training (CUDA_VISIBLE_DEVICES set before execution)
- GPU memory efficient (ResNet-18 fits on 8GB GPU)
- Training time: ~2-4 hours per paradigm on single GPU

### NFR-3: Code Quality
- LIGHT tier infrastructure: Hardcoded configs, print logging, CSV outputs
- Minimal testing: Smoke tests only (data loading, forward pass)
- No complex abstractions (direct implementation preferred for PoC)

### NFR-4: Documentation
- Docstrings for MITracker class
- Inline comments for MI computation and derivative estimation
- README with execution instructions

---

## Success Criteria

### PoC Pass Condition
1. **Code execution**: All 3 paradigms run without error
2. **Effect direction**: d/dt I(Z_s; H_t) > d/dt I(Z_c; H_t) in at least 2 out of 3 paradigms

**Note:** Statistical significance testing NOT required for EXISTENCE PoC. Observing the effect direction is sufficient for gate validation.

### Expected Baseline Performance
- Supervised MNIST: ~98-99% test accuracy
- SSL MNIST: ~95%+ linear probing accuracy
- RL Grid Navigation: Policy convergence within 200 episodes

---

## Dependencies

### External Libraries
- **PyTorch**: Core deep learning framework (≥1.12)
- **torchvision**: ResNet-18 model and MNIST dataset
- **sklearn**: Mutual information computation and discretization
- **scipy**: Spline fitting for derivatives
- **torchmetrics**: Accuracy computation
- **matplotlib**: Visualization
- **numpy**: Array operations

### Hardware Requirements
- Single GPU with ≥8GB memory
- CPU: 4+ cores recommended for data loading
- RAM: ≥16GB

### Data Requirements
- MNIST dataset (auto-download via torchvision)
- Storage: ~50MB for dataset + ~500MB for checkpoints and outputs

---

## Scope & Limitations

### In Scope
- Proof-of-concept implementation testing existence of MI growth rate asymmetry
- Single seed (seed=1) per paradigm (PoC validation)
- Three paradigms: Supervised, SSL, RL
- Colored MNIST with controlled spurious correlation

### Out of Scope
- Statistical significance testing (reserved for future hypotheses)
- Multi-seed experiments (LIGHT tier budget)
- Hyperparameter tuning (use standard configurations)
- Ablation studies (reserved for mechanism hypotheses)
- Comparison with baseline methods (JTT, GroupDRO)

### Known Limitations
- PoC uses single seed - effect may not generalize
- Colored MNIST is simplified - real-world spurious correlations more complex
- Early-phase window definition is heuristic-based
- MI estimation accuracy depends on discretization (n_bins=20 tradeoff)

---

## Risk Assessment

### R1: MI Estimator Inaccuracy
- **Severity:** HIGH
- **Mitigation:** Use histogram-based MI for discrete factors (exact computation)
- **Status:** PLANNED (discretization validation in FR-3)

### R2: Early-Phase Misidentification
- **Severity:** MEDIUM
- **Mitigation:** Dual criteria (10% steps OR 30% performance) + gradient norm validation
- **Status:** PLANNED (FR-10)

### R3: RL Exploration Bias
- **Severity:** HIGH
- **Mitigation:** Entropy regularization (coeff=0.01), track exploration metrics
- **Status:** PLANNED (FR-6)

### R4: Derivative Instability
- **Severity:** MEDIUM
- **Mitigation:** Spline smoothing (s=0.1), sufficient checkpoint frequency (every 50 steps)
- **Status:** PLANNED (FR-7)

---

## Implementation Phases

### Phase 1: Data + Model Infrastructure (Epics 1-2)
- FR-1: Colored MNIST dataset generation
- FR-2: ResNet-18 architecture

### Phase 2: MI Tracking Core (Epic 3)
- FR-3: MI tracker implementation
- FR-7: Derivative estimation
- FR-10: Early-phase window detection

### Phase 3: Paradigm Training (Epics 4-6)
- FR-4: Supervised training
- FR-5: SSL training (SimCLR)
- FR-6: RL training (Policy gradient)

### Phase 4: Evaluation + Visualization (Epics 7-8)
- FR-8: Metrics computation
- FR-9: Figure generation

---

## Appendix: Traceability

All functional requirements map directly to Phase 2C experiment brief sections:
- Dataset: FR-1 ← Section "Dataset"
- Models: FR-2 ← Section "Models / Baseline Model"
- Training: FR-4, FR-5, FR-6 ← Section "Training Protocol"
- Evaluation: FR-7, FR-8, FR-9, FR-10 ← Section "Evaluation"
- MI Tracking: FR-3 ← Section "Models / Proposed Model (MI Tracking Pseudo-code)"

---

**Document Status:** Complete  
**Next Phase:** Phase 3 - Implementation Planning (Architecture, Logic, Config)
