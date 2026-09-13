# Verification Plan: Classical Variance Baseline for Neural Network Training Stochasticity

**Date:** 2026-03-20
**Hypothesis ID:** H-ClassicalVarianceBaseline-v1
**Confidence:** 0.85
**Total Hypotheses:** 4

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement
Under deterministic neural network training with controlled randomness (PyTorch seed control, deterministic algorithms), if we replicate training N=30 times with independent random seeds on simple MLPs (1-layer and 2-layer) across dual datasets (MNIST and Fashion-MNIST), then test accuracy variance σ² will be (1) statistically non-zero (p < 0.05), (2) measurably stable via bootstrap resampling (CI width ≤ 50%), and (3) practically detectable (CV ≥ 0.1%), because variance arises solely from stochastic weight initialization under full determinism, and N=30 provides sufficient sample size for stable classical statistical estimation per Rajput 2023's validated criterion.

### 1.2 Alternative Hypothesis (H0)
There is no significant test accuracy variance across 30 independent training runs (σ² = 0), OR bootstrap estimation is unstable (CI width > 50%), OR variance is below practical detectability threshold (CV < 0.1%).

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | MNIST + Fashion-MNIST (Dual-Dataset Design) (standard) | MNIST provides clean pedagogical baseline (simple task, ~98% accuracy), Fashion-MNIST provides task difficulty sensitivity test (same dimensionality, harder task ~90% accuracy). Isomorphic datasets (28×28, 10 classes, 60K train) enable controlled comparison of variance vs task difficulty without confounding architecture changes. |
| **Model** | Simple MLPs (Dual-Architecture Design) | 1-layer MLP (784→128→10): Simplest non-trivial architecture, ~196K params, pedagogical baseline. 2-layer MLP (784→256→128→10): Slightly deeper (~400K params) to test architecture sensitivity. Both use ReLU activation, cross-entropy loss, fixed initialization (controlled by seed). Rationale: 1-layer alone may be too simple (variance too small), 2-layer provides robustness check while maintaining <25min runtime. |

**Dataset Details:**
- Source: torchvision.datasets.MNIST / torchvision.datasets.FashionMNIST
- Path: Downloaded automatically via PyTorch

**Model Details:**
- Type: Feedforward Neural Network
- Source: Custom PyTorch implementation

### 1.4 Baseline Methods (for Phase 5 comparison)

| Method | Performance | Dataset |
|--------|-------------|---------|
| Picard 2021 - torch.manual_seed(3407) optimal seed search | Scanned 10^4 seeds on CIFAR-10 ResNet-18, found seed-dependent variance despite determinism | CIFAR-10 |
| Rajput 2023 - Decided sample size validation | Validated N≥30 criterion across 15 ML benchmarks (effect size ≥0.5, accuracy ≥80%) | 15 diverse datasets (medical imaging, tabular, etc.) |
| Ghasemzadeh 2023 - Generalizable ML Models via nested k-fold | Nested k-fold reduces required sample size by ~50% for stable model selection | Multiple benchmarks |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | Bootstrap resampling with B=1000 provides valid confidence intervals for variance estimation on neural network test accuracies | Bootstrap assumes i.i.d. samples. Our 30 training runs share dataset/optimizer but differ only in seed initialization. Prof. Rex raised i.i.d. violation concern - we address via permutation test robustness check. | CI width estimates could be biased. Mitigation: Run permutation test + Bayesian variance estimation in parallel - if all three methods (bootstrap, permutation, Bayesian) agree, assumption violation is negligible. |
| A2 | N=30 seeds provides sufficient sample size for stable variance estimation (power ≥ 80% to detect σ=0.1%) | Rajput 2023 empirically validated N≥30 across 15 ML benchmark datasets with effect size ≥0.5. Power analysis: For one-sample variance test with N=30, α=0.05, σ_true=0.1%, power ≈ 0.85 (chi-squared distribution). | Underpowered experiment may fail to detect real but small variance. Mitigation: Pre-register minimum detectable effect σ_min=0.1%, document power=85% upfront, add N sensitivity analysis (retroactive plot CI width vs N ∈ [10,20,30]) to guide future work. |
| A3 | MNIST and Fashion-MNIST are representative enough to demonstrate generalizable variance measurement methodology | Both datasets are 28×28 grayscale, 10 classes, 60K train - isomorphic structure with different task difficulty (MNIST ~98% vs Fashion-MNIST ~90% accuracy). Prof. Rex critique: MNIST alone too narrow; Exchange 7 resolution: dual-dataset design tests task difficulty sensitivity. | Findings may not generalize to CNNs, Transformers, or higher-dimensional datasets. Mitigation: Explicitly position as 'simple architecture baseline' in intro, acknowledge limitation, propose CIFAR-10 CNN baseline as future work in Discussion. |
| A4 | Variance magnitude is practically significant (CV ≥ 0.1%) rather than numerically trivial | Prof. Pax's critique: σ²=0.0001 would be 'who cares?' result. Dr. Ally's defense: Low variance is valid negative information (MNIST MLP is remarkably stable). CV ≥ 0.1% criterion ensures detectability relative to mean. | Hypothesis technically passes (σ² > 0, CI < 50%) but lacks practical impact. Mitigation: Report BOTH outcomes as valid - Scenario A (high variance σ≥0.3%): UQ methods address real problem; Scenario B (low variance σ≤0.1%): simple MLPs inherently stable, UQ must demonstrate value on complex architectures. |
| A5 | The experimental protocol completes in <25 minutes on single H100 GPU | Prof. Pax's feasibility analysis: MNIST MLP (784→128→10) = ~196K params, 10 epochs = 5-10 sec/seed on H100. 30 seeds × 2 architectures × 2 datasets × 6min = ~24 minutes (conservative estimate). | Computational infeasibility (>1 hour) risks Run 2-style failure (code ready but never executed). Mitigation: Computational feasibility already validated in discussion - no risk unless GPU availability changes. |

### 1.6 Research Gap & Novelty

**Preserved Novelty:** First validated classical variance baseline for neural network training stochasticity using dual-dataset (MNIST + Fashion-MNIST), dual-architecture (1-layer + 2-layer MLP) experimental design with statistical triangulation (bootstrap + permutation + Bayesian)

**Key Innovation:** **Measurement Infrastructure as Contribution:** Rather than inventing new UQ methods, we establish the BASELINE that all UQ methods should be compared against. The innovation is positioning radical simplicity as a methodological contribution after 7 complex-framework failures (IB-EDL, UQ meta-learning, CLT convergence) - demonstrating that measurement validation must precede theoretical innovation.

**Statistical Triangulation:** Novel use of three complementary variance estimation methods (bootstrap, permutation, Bayesian) to validate which statistical assumptions matter for neural network variance - if they agree, bootstrap is validated; if they disagree, we've identified assumption violations as publishable methodological findings.

**Dual-Dataset Task Sensitivity:** MNIST + Fashion-MNIST isomorphism tests whether variance scales with task difficulty while controlling architecture - addresses generalizability without computational explosion.

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| H-E1 | EXISTENCE | MUST_WORK | None | READY |
| H-M1 | MECHANISM | MUST_WORK | H-E1 | BLOCKED |
| H-M2 | MECHANISM | MUST_WORK | H-M1 | BLOCKED |
| H-M3 | MECHANISM | SHOULD_WORK | H-M2 | BLOCKED |

---

### 2.2 Hypothesis Specifications

---
**H-E1: Test Accuracy Variance Existence**

**Statement**: Under deterministic neural network training with controlled randomness (PyTorch seed control), if we replicate training N=30 times with independent random seeds on simple MLPs across dual datasets (MNIST and Fashion-MNIST), then test accuracy variance σ² will be statistically non-zero (p < 0.05) for all 4 conditions (2 architectures × 2 datasets), because variance arises solely from stochastic weight initialization.

**Rationale**: This validates that measurable variance exists in deterministic training despite full environmental control. It establishes the phenomenon that all UQ methods attempt to quantify. Without this, the entire variance measurement framework would be meaningless.

**Variables**:
- Independent: Random Seed (30 levels: 0-29), Architecture Depth (1-layer, 2-layer), Dataset (MNIST, Fashion-MNIST)
- Dependent: Test Accuracy Variance σ² = Var(test_accuracies)
- Controlled: Training Epochs (10), Optimizer (SGD lr=0.01), Determinism (full PyTorch control)

**Verification Protocol**:
1. Train each MLP architecture for 10 epochs with 30 different seeds (0-29) on both MNIST and Fashion-MNIST
2. Record test accuracy for each of the 30 runs per condition (4 conditions total: 2 architectures × 2 datasets)
3. Compute variance σ² = Var(test_accuracies) for each of the 4 conditions
4. Perform one-sample variance test (chi-squared distribution) with H0: σ²=0 vs H1: σ²>0, α=0.05
5. Verify p < 0.05 for all 4 conditions

**Success Criteria (PoC Direction-based)**:
- Primary: p < 0.05 for all 4 conditions (variance statistically distinguishable from zero)
- Secondary: At least 2 conditions show CV ≥ 0.1% (practical detectability)

**Failure Response**:
- IF fails: ABANDON - variance measurement infrastructure invalid, cannot proceed

**Dependencies**: None (foundation hypothesis)

**Source**: Phase 2A Section 1.6 Prediction P1

---

**H-M1: Seed Initialization Creates Stochastic Weight Configurations**

**Statement**: Under full determinism (PyTorch seed control), if different random seeds are used for initialization, then initial weight configurations will differ measurably across the 30 training runs, because torch.manual_seed(seed) is the ONLY source of variance under deterministic training.

**Rationale**: This validates the first link in the causal chain. If initial weights don't differ, there's no mechanism to produce test accuracy variance. Confirms that PyTorch determinism is working correctly and seed initialization is the controlled randomness source.

**Variables**:
- Independent: Random Seed (30 levels: 0-29)
- Dependent: Initial Weight Configuration (weight tensor Euclidean distances between seed pairs)
- Controlled: Model architecture, initialization method (PyTorch defaults)

**Verification Protocol**:
1. Initialize the same MLP architecture with all 30 seeds (0-29)
2. Extract initial weight tensors immediately after model initialization (before any training)
3. Compute pairwise Euclidean distances between all weight configurations (30 choose 2 = 435 pairs)
4. Test if mean pairwise distance > 0 with statistical significance (t-test vs null hypothesis of zero distance)

**Success Criteria (PoC Direction-based)**:
- Primary: Mean pairwise distance > 0 with p < 0.05 (weights differ across seeds)
- Secondary: Distance distribution shows no clustering (confirms independence)

**Failure Response**:
- IF fails: PIVOT - investigate PyTorch determinism failures, check seed control implementation

**Dependencies**: H-E1 (variance must exist for mechanism to be relevant)

**Source**: Phase 2A Section 1.3 Causal Mechanism Step 1

---

**H-M2: Different Initializations Lead to Different Optimization Trajectories**

**Statement**: Under deterministic SGD with different initial weights (from H-M1), if training proceeds for 10 epochs, then optimization trajectories will diverge measurably, converging to different local minima, because non-convex loss landscapes have multiple minima and initialization determines which basin of attraction the optimizer enters.

**Rationale**: This validates the second causal link. Even with deterministic training, different initializations must traverse different paths through the loss landscape. This explains how initial weight variance propagates through training to final model variance.

**Variables**:
- Independent: Initial Weight Configuration (from H-M1)
- Dependent: Final Weight Configuration (after 10 epochs), Training Loss Trajectory
- Controlled: Learning rate (0.01), Momentum (0.9), Batch size (64), Epochs (10)

**Verification Protocol**:
1. Track training loss at each epoch for all 30 training runs per condition
2. Compute pairwise Euclidean distances between final weight configurations
3. Test if final weight distance correlates with initial weight distance (Pearson correlation)
4. Verify that loss trajectories diverge across seeds (coefficient of variation of loss values at epoch 10)

**Success Criteria (PoC Direction-based)**:
- Primary: Final weight configurations differ significantly across seeds (mean pairwise distance > 0, p < 0.05)
- Secondary: Loss trajectories show measurable divergence (CV of final loss ≥ 1%)

**Failure Response**:
- IF fails: EXPLORE - MNIST MLP may have dominant attractor despite different initializations

**Dependencies**: H-M1 (initial weight variance must exist)

**Source**: Phase 2A Section 1.3 Causal Mechanism Step 2

---

**H-M3: Different Local Minima Yield Stable Variance Estimates**

**Statement**: Under bootstrap resampling (B=1000) of the 30 test accuracy values from different local minima (H-M2), if we estimate confidence intervals on variance σ², then CI width will be ≤ 50% of the point estimate for all 4 conditions, because N=30 provides sufficient sample size for stable variance estimation per Rajput 2023's criterion.

**Rationale**: This validates the third causal link and measurement stability. Measurable variance (H-E1) arising from distinct minima (H-M2) must be reliably estimable. This proves the methodology can be used as a baseline for UQ method comparison.

**Variables**:
- Independent: Test Accuracy Sample (30 values per condition from H-E1)
- Dependent: Bootstrap CI Width = (CI_upper - CI_lower) / σ² × 100%
- Controlled: Bootstrap resamples (B=1000), Confidence level (95%)

**Verification Protocol**:
1. For each of the 4 conditions, take the 30 test accuracy values from H-E1
2. Perform bootstrap resampling with B=1000 resamples to estimate variance σ²
3. Compute 95% confidence interval as [percentile(2.5), percentile(97.5)]
4. Calculate CI width = (CI_upper - CI_lower) / σ² × 100% for each condition
5. Verify CI width ≤ 50% for all 4 conditions

**Success Criteria (PoC Direction-based)**:
- Primary: CI width ≤ 50% for all 4 conditions (stable variance estimation)
- Secondary: Statistical triangulation agreement (bootstrap, permutation, Bayesian methods agree within 10%)

**Failure Response**:
- IF fails: EXPLORE - N=30 may be insufficient for stable estimation despite Rajput 2023, add N sensitivity analysis

**Dependencies**: H-M2 (different minima must exist to produce variance to estimate)

**Source**: Phase 2A Section 1.3 Causal Mechanism Step 3, Prediction P2

---

---

## 3. Execution

### 3.1 Dependency Chain
```
H-E1 → H-M1 → H-M2 → H-M3
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | p < 0.05 for all 4 conditions | ABANDON |
| H-M1 | MUST_WORK | Mean pairwise distance > 0, p < 0.05 | PIVOT |
| H-M2 | MUST_WORK | Final weight distance > 0, p < 0.05 | EXPLORE |
| H-M3 | SHOULD_WORK | CI width ≤ 50% for all 4 conditions | EXPLORE |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 2C | Experiment Design (all 4 hypotheses) | ~30 min |
| Phase 3 | Implementation Planning (PRD + Architecture) | ~45 min |
| Phase 4 | Coding + Validation (H-E1 → H-M1 → H-M2 → H-M3) | ~90 min |
| Phase 5 | Baseline Comparison (deferred - MC Dropout PoC) | ~60 min |

**Total Duration:** ~225 minutes (~3.75 hours for full pipeline Phases 2C-5)

---

*Generated by YouRA Phase 2B (Compact v1.0) | 2026-03-20*
