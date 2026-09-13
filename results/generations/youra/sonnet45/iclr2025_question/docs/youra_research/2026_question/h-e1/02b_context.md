# Phase 2B Context: h-e1

**Hypothesis ID:** h-e1
**Type:** EXISTENCE
**Gate:** MUST_WORK

## Hypothesis Statement

Under deterministic neural network training with controlled randomness (PyTorch seed control), if we replicate training N=30 times with independent random seeds on simple MLPs across dual datasets (MNIST and Fashion-MNIST), then test accuracy variance σ² will be statistically non-zero (p < 0.05) for all 4 conditions (2 architectures × 2 datasets), because variance arises solely from stochastic weight initialization.

## Rationale

This validates that measurable variance exists in deterministic training despite full environmental control. It establishes the phenomenon that all UQ methods attempt to quantify. Without this, the entire variance measurement framework would be meaningless.

## Variables

- **Independent:** Random Seed (30 levels: 0-29), Architecture Depth (1-layer, 2-layer), Dataset (MNIST, Fashion-MNIST)
- **Dependent:** Test Accuracy Variance σ² = Var(test_accuracies)
- **Controlled:** Training Epochs (10), Optimizer (SGD lr=0.01), Determinism (full PyTorch control)

## Experimental Setup

### Dataset
- **Primary:** MNIST + Fashion-MNIST (Dual-Dataset Design)
- **Type:** standard
- **Source:** torchvision.datasets.MNIST / torchvision.datasets.FashionMNIST
- **Justification:** MNIST provides clean pedagogical baseline (simple task, ~98% accuracy), Fashion-MNIST provides task difficulty sensitivity test (same dimensionality, harder task ~90% accuracy). Isomorphic datasets (28×28, 10 classes, 60K train) enable controlled comparison of variance vs task difficulty without confounding architecture changes.

### Model
- **Primary:** Simple MLPs (Dual-Architecture Design)
- **Architecture 1:** 1-layer MLP (784→128→10): Simplest non-trivial architecture, ~196K params, pedagogical baseline
- **Architecture 2:** 2-layer MLP (784→256→128→10): Slightly deeper (~400K params) to test architecture sensitivity
- **Activation:** ReLU
- **Loss:** Cross-entropy
- **Initialization:** Fixed (controlled by seed)

## Verification Protocol

1. Train each MLP architecture for 10 epochs with 30 different seeds (0-29) on both MNIST and Fashion-MNIST
2. Record test accuracy for each of the 30 runs per condition (4 conditions total: 2 architectures × 2 datasets)
3. Compute variance σ² = Var(test_accuracies) for each of the 4 conditions
4. Perform one-sample variance test (chi-squared distribution) with H0: σ²=0 vs H1: σ²>0, α=0.05
5. Verify p < 0.05 for all 4 conditions

## Success Criteria (PoC Direction-based)

- **Primary:** p < 0.05 for all 4 conditions (variance statistically distinguishable from zero)
- **Secondary:** At least 2 conditions show CV ≥ 0.1% (practical detectability)

## Failure Response

- **IF fails:** ABANDON - variance measurement infrastructure invalid, cannot proceed

## Dependencies

None (foundation hypothesis)

## Baseline Methods

| Method | Performance | Dataset |
|--------|-------------|---------|
| Picard 2021 - torch.manual_seed(3407) optimal seed search | Scanned 10^4 seeds on CIFAR-10 ResNet-18, found seed-dependent variance despite determinism | CIFAR-10 |
| Rajput 2023 - Decided sample size validation | Validated N≥30 criterion across 15 ML benchmarks (effect size ≥0.5, accuracy ≥80%) | 15 diverse datasets (medical imaging, tabular, etc.) |

## Previous Version Results

**Version 1:**
- Status: PARTIAL
- Variance: 0.128%
- Issue: Kurtosis violation
- Recommendation: Use Fashion-MNIST for higher variance

**Version 2:**
- Status: IMPLEMENTATION_COMPLETE → FAILED
- Code quality: VERIFIED
- Integration tests: PASSED
- Experiment scale: 40 runs total
- Issue: NTK β=-0.391 (95% CI [-0.448, -0.333]) does not contain CLT prediction of -0.50
- Gate result: FAIL - systematic deviation from CLT prediction across both training regimes

## Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A2 | N=30 seeds provides sufficient sample size for stable variance estimation (power ≥ 80% to detect σ=0.1%) | Rajput 2023 empirically validated N≥30 across 15 ML benchmark datasets | Underpowered experiment may fail to detect real but small variance |
| A3 | MNIST and Fashion-MNIST are representative enough to demonstrate generalizable variance measurement methodology | Both datasets are 28×28 grayscale, 10 classes, 60K train - isomorphic structure | Findings may not generalize to CNNs, Transformers, or higher-dimensional datasets |
| A4 | Variance magnitude is practically significant (CV ≥ 0.1%) rather than numerically trivial | CV ≥ 0.1% criterion ensures detectability relative to mean | Hypothesis technically passes but lacks practical impact |

---

*Generated: 2026-03-21 | Phase 2B Context for h-e1*
