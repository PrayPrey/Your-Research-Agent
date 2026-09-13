# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-03-20T23:45:27
- **Workflow**: phase2a-dialogue v10.0.0
- **Architecture**: Self-Contained Tikitaka Loop v10.0.0
- **Gap ID**: gap_1
- **Gap Title**: Validated Classical Variance Baseline for Simple Neural Networks
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 7

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 7

**Convergence Reason**: All 6 convergence criteria met (SPECIFIC, MECHANISM, PREDICTIONS, NOVELTY, FEASIBILITY, OBJECTIONS)

### Key Insights

1. **Radical simplicity as contribution**: After 7 complex-framework failures (IB-EDL, UQ meta-learning, CLT convergence), measurement infrastructure itself becomes the innovation
2. **Measurement-first paradigm**: Validate baseline variance exists before inventing epistemic uncertainty frameworks
3. **Low variance is valid result**: If σ² is small, that's publishable negative information about MNIST MLP stability, not a failure
4. **Statistical triangulation reveals assumptions**: Bootstrap, permutation, Bayesian agreement validates i.i.d. assumption; disagreement identifies methodological gaps
5. **Dual-dataset isomorphism**: MNIST + Fashion-MNIST share structure but differ in task difficulty, enabling clean task sensitivity test

### Breakthrough Moments

- **Exchange 5 (Dr. Ally)**: Reframed "low variance problem" as valid negative result - MNIST MLP stability is publishable information, not pyrrhic victory
- **Exchange 7 (Dr. Nova)**: Transformed Prof. Rex's critiques into opportunities - MNIST limitation → dual-dataset design; bootstrap assumption → statistical triangulation; sample size concern → N sensitivity analysis
- **Exchange 4 (Prof. Pax)**: Feasibility validation (<10min is EASILY achievable) eliminated computational risk from Run 2-style failures

---

## Final Hypothesis

### Title
Classical Variance Baseline for Neural Network Training Stochasticity

### Core Claim
Under deterministic neural network training with controlled randomness (PyTorch seed control, deterministic algorithms), if we replicate training N=30 times with independent random seeds on simple MLPs (1-layer and 2-layer) across dual datasets (MNIST and Fashion-MNIST), then test accuracy variance σ² will be (1) statistically non-zero (p < 0.05), (2) measurably stable via bootstrap resampling (CI width ≤ 50%), and (3) practically detectable (CV ≥ 0.1%), because variance arises solely from stochastic weight initialization under full determinism, and N=30 provides sufficient sample size for stable classical statistical estimation per Rajput 2023's validated criterion.

### Mechanism

**Three-Step Causal Chain:**

1. **Random seed initialization creates stochastic weight configurations**
   Under full determinism (PyTorch seed control), the ONLY source of variance across training runs is the initial random weight draw controlled by `torch.manual_seed(seed)`. Different seeds → different initialization points in weight space.

2. **Different initialization points lead to different optimization trajectories**
   Even with deterministic SGD (fixed learning rate, momentum, batch order), distinct initial weights cause the optimizer to traverse different paths through loss landscape, converging to different local minima.

3. **Different local minima yield measurably different test accuracy values**
   The variance in final test accuracy σ² reflects the distribution of minima quality across the N=30 initialization samples. Bootstrap resampling (B=1000) estimates confidence intervals on this variance to assess stability.

---

## Predictions

### P1 (Primary): Variance Existence
**Statement**: Test accuracy variance σ² > 0 with statistical significance across 30 independent training runs for both 1-layer and 2-layer MLPs on MNIST and Fashion-MNIST

**Test Method**: One-sample variance test (chi-squared distribution, H0: σ²=0 vs H1: σ²>0, α=0.05)

**Success Criterion**: p < 0.05 for all 4 conditions (2 architectures × 2 datasets)

**Falsification**: If any condition yields p ≥ 0.05, variance is not statistically detectable

### P2: Measurement Stability
**Statement**: Bootstrap 95% confidence interval width ≤ 50% of variance point estimate (Rajput 2023 stability criterion)

**Test Method**: Bootstrap resampling (B=1000) on the 30 test accuracy values, compute CI width = (CI_upper - CI_lower) / σ² × 100%

**Success Criterion**: CI width ≤ 50% for all 4 conditions

**Falsification**: If CI width > 50% for any condition, bootstrap variance estimation is unstable despite N=30

### P3: Practical Detectability
**Statement**: Coefficient of Variation CV = σ/μ ≥ 0.1% (practical detectability threshold)

**Test Method**: Compute CV = (standard_deviation / mean_accuracy) × 100% for each condition

**Success Criterion**: CV ≥ 0.1% for at least 2 out of 4 conditions

**Falsification**: If CV < 0.1% for all conditions, variance is numerically trivial (but still publishable as "MNIST MLP stability" finding)

---

## Novelty

### What's New

**First validated classical variance baseline** for neural network training stochasticity using:
- Dual-dataset design (MNIST + Fashion-MNIST) testing task difficulty sensitivity
- Dual-architecture design (1-layer + 2-layer MLP) testing depth sensitivity
- Statistical triangulation (bootstrap + permutation + Bayesian) validating which assumptions matter

### Differentiation from Prior Work

| Prior Work | Our Difference |
|------------|----------------|
| **Picard 2021** - Seed variance on CIFAR-10 ResNet-18 (10^4 seeds) | N=30 (computationally feasible), MNIST/Fashion-MNIST (simpler baselines), statistical triangulation, dual-architecture robustness |
| **Rajput 2023** - N≥30 validation theoretical | Empirically test whether bootstrap CI width ≤ 50% applies to neural network variance specifically |
| **Ghasemzadeh 2023** - Nested k-fold reduces N by 50% | Test vanilla N=30 without k-fold optimization - establish simpler baseline first |
| **Complex UQ methods** (IB-EDL, ensemble-based, Bayesian NNs) | Provide the NULL HYPOTHESIS they should compare against |

### Key Innovation

**Measurement infrastructure as contribution**: Rather than inventing new UQ methods, we establish the BASELINE that all UQ methods should be compared against. The innovation is positioning radical simplicity as a methodological contribution after 7 complex-framework failures.

---

## Experimental Design

### Datasets
- **MNIST**: Clean pedagogical baseline (simple task, ~98% accuracy)
- **Fashion-MNIST**: Task difficulty sensitivity test (same dimensionality, harder task ~90% accuracy)
- Both: 28×28 grayscale, 10 classes, 60K train - isomorphic structure enables controlled comparison

### Models
- **1-layer MLP** (784→128→10): Simplest non-trivial architecture, ~196K params
- **2-layer MLP** (784→256→128→10): Slightly deeper (~400K params) to test architecture sensitivity
- Both: ReLU activation, cross-entropy loss, fixed initialization controlled by seed

### Training Protocol
- **Epochs**: 10 (fixed)
- **Optimizer**: SGD with lr=0.01, momentum=0.9, batch_size=64
- **Determinism**: `torch.manual_seed(seed)`, `cudnn.deterministic=True`, `use_deterministic_algorithms(True)`
- **Replication**: N=30 independent runs with seeds 0-29

### Baselines
- **Monte Carlo Dropout**: Proof-of-concept UQ method comparison to demonstrate baseline usage
- **Picard 2021**: Reference for seed-dependent variance on CIFAR-10 (we validate key finding on different dataset/architecture)

### Runtime
- **Target**: < 25 minutes on single H100 GPU
- **Estimate**: ~5-10 seconds per seed × 30 seeds × 2 architectures × 2 datasets ≈ 20-24 minutes

---

## Limitations

### Acknowledged Constraints

1. **Sample Size** (N=30 vs Picard's 10^4)
   Rare outlier seeds (<0.03% occurrence) may be undetected. Computationally unavoidable trade-off.

2. **Architecture Scope** (MLPs only)
   No CNNs, Transformers. Fashion-MNIST tests task difficulty but not architectural diversity. Positioned as "Phase 1 baseline" with CIFAR-10 CNN future work.

3. **Bootstrap i.i.d. Assumption**
   Training runs share dataset and optimizer transitions - "independence" is weak (seed initialization only). Addressed via permutation test + Bayesian robustness checks.

4. **Dataset Scope** (MNIST/Fashion-MNIST)
   Does not generalize to large-scale datasets (ImageNet), high-dimensional tasks, or stochastic regularization. Explicit scope statement in introduction.

### Mitigation Strategies

- Report all three variance estimation methods (bootstrap, permutation, Bayesian) - if they disagree, analyze assumption violations
- Add Discussion section "Generalizability Boundaries" acknowledging scope limits
- Propose CIFAR-10 CNN baseline as future work
- Frame as "Phase 1 baseline validation" not "comprehensive UQ infrastructure"

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | All 6 criteria met (SPECIFIC, MECHANISM, PREDICTIONS, NOVELTY, FEASIBILITY, OBJECTIONS) |
| **Clarity Verified** | Yes |
| **Remaining Objections** | None |

**All 4 Persona Verdicts**: STRONG (Novelty, Falsifiability, Significance, Feasibility)

**Confidence Level**: 0.85 (High)

---

*Generated by Phase 2A-Dialogue Workflow v10.0.0 (Self-Contained Tikitaka Loop, Free-Parse)*
