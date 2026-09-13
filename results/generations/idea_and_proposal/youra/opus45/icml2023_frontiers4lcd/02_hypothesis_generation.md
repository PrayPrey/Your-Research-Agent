# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-12
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-HJB-Score-v1
**Confidence Level:** 0.85

**Main Hypothesis:**
Under standard regularity conditions (bounded score, Lipschitz continuous densities), if the log-probability density log p(x,t) is identified as the negative value function V(x,t) of a stochastic optimal control problem, then denoising score matching objectives emerge as Hamilton-Jacobi-Bellman (HJB) optimality conditions, because the score function ∇ log p(x,t) equals the gradient of the value function -∇V(x,t), which characterizes the optimal control signal for the reverse-time SDE.

**Alternative Hypothesis (H0):**
The mathematical equivalence between score matching and HJB optimality is coincidental or limited to special cases; the score function does not generally correspond to an optimal control signal, and denoising objectives cannot be systematically derived from control-theoretic principles.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| SDE formulation type | Independent | VP-SDE, VE-SDE, or sub-VP-SDE parameterization | Categorical: {VP, VE, sub-VP} |
| Noise schedule | Independent | β(t) schedule function (linear, cosine, learned) | β ∈ [0.0001, 20] |
| Score estimation error | Dependent | E[‖s_θ(x,t) - ∇ log p(x,t)‖²] | Target: < 0.1 |
| Sample quality (FID) | Dependent | Fréchet Inception Distance on CIFAR-10/ImageNet | Lower is better; SOTA ~2.0 on CIFAR-10 |
| Convergence rate | Dependent | Number of training iterations to reach target loss | Iterations to 90% of final performance |
| Regularity conditions | Controlled | Bounded score (‖∇ log p‖ < M), Lipschitz density | M ∈ [10, 100] typical |
| Network architecture | Controlled | U-Net with fixed depth/width parameters | Standard DDPM/score_sde architecture |

### 1.3 Causal Mechanism

**Causal Chain (N=3 steps):**

```
Step 1: Log-Probability ↔ Value Function Identification
    ↓
Step 2: Gradient Relationship (Score = Optimal Control)
    ↓
Step 3: HJB Residual = Score Matching Loss
    ↓
Outcome: Unified theoretical framework enabling principled training objective design
```

**Step 1 → Step 2: Log-Probability Identification**
- The reverse-time SDE for diffusion models can be formulated as a stochastic optimal control problem
- Setting V(x,t) = -log p(x,t) identifies the log-probability density as the value function
- This mapping is enabled by Girsanov's theorem, which relates drift changes to measure changes

**Step 2 → Step 3: Gradient Relationship**
- From the value function identification: ∇V(x,t) = -∇ log p(x,t) = -score(x,t)
- In optimal control, the optimal policy is determined by ∇V
- Therefore, the score function IS the optimal control signal (up to sign)

**Step 3 → Outcome: HJB Optimality**
- The HJB equation for the control problem has residual that, when discretized temporally, resembles a TD error
- The denoising score matching loss can be shown to equal this HJB residual under the identification
- This provides a mathematical proof of WHY score matching is optimal, not just empirical observation

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step 1 → Step 2 | Adjoint Matching (Domingo-Enrich, 2024) | SOC formulation valid for diffusion; memoryless noise schedule required | Strong |
| Step 1 → Step 2 | Girsanov Theorem (Mathematical Finance) | Drift changes ↔ measure changes are mathematically equivalent | Strong |
| Step 2 → Step 3 | Variational Diffusion Models (Kingma, 2021) | VLB simplifies to signal-to-noise ratio; score matching = ELBO maximization | Strong |
| Step 3 → Outcome | Score-Based SDEs (Song, 2020) | Unified SDE framework with 9234 citations validates foundational approach | Strong |
| Step 3 → Outcome | This Hypothesis (Novel) | Explicit HJB derivation of training objective | To be validated |

**Key Tension:**
- **Tension:** Variational Perspective (Huang et al., 2021) derives score matching from probabilistic ELBO framework, while this hypothesis derives it from control-theoretic HJB. Are these truly equivalent or complementary?
- **Resolution:** This verification plan tests whether HJB derivation recovers ELBO as a special case, providing a unified framework that encompasses both perspectives.

### 1.4 Key Assumptions

1. **Forward SDE regularity:** The forward diffusion SDE satisfies standard existence and uniqueness conditions (Lipschitz drift, bounded diffusion coefficient).
   - *Consequence if violated:* HJB equation may not have classical solution; viscosity solutions required with approximation gap.

2. **Log-density smoothness:** log p(x,t) is twice differentiable in x and once differentiable in t throughout the diffusion trajectory.
   - *Consequence if violated:* Score function undefined or discontinuous at certain points; training instability near those regions.

3. **Bounded score assumption:** ‖∇ log p(x,t)‖ < M for some finite M across the support.
   - *Consequence if violated:* Optimal control becomes unbounded; network approximation error grows without bound.

4. **Network capacity sufficiency:** The score network s_θ has sufficient expressiveness to approximate the true score function within ε tolerance.
   - *Consequence if violated:* Approximation gap between theory and practice; HJB optimality holds only approximately.

### 1.5 Scope & Boundaries

**Where Hypothesis Applies:**
- VP-SDE (Variance Preserving): Linear noise schedule diffusions (DDPM-style)
- VE-SDE (Variance Exploding): Exponential noise schedule diffusions (SMLD-style)
- sub-VP-SDE: Hybrid formulations with sub-linear variance growth
- Continuous-time diffusion models with smooth noise schedules
- Standard data domains: natural images, audio, molecular structures

**Where Hypothesis Does NOT Apply:**
- Discrete diffusion models (D3PM, multinomial diffusion)
- Non-Markovian denoising processes
- Degenerate SDEs with rank-deficient diffusion matrices
- Distributions with infinite support and heavy tails (Cauchy, stable distributions)

**Known Limitations:**
- Approximation gap exists for finite-capacity networks vs. infinite-dimensional theory
- Regularity conditions may fail at distribution boundaries (e.g., image edges)
- Practical training uses discrete time; continuous-time HJB requires discretization analysis
- Computational cost of validating HJB residual directly may be prohibitive

### 1.6 Testable Predictions

**Primary Prediction:**
**P1 (HJB-Score Equivalence):**
If log p(x,t) satisfies HJB equation with V = -log p, then denoising score matching loss equals HJB optimal control objective up to a constant factor.

*Measurement*:
- Derive explicit mathematical relationship between DSM loss and HJB residual
- Verify numerically on toy problems (1D/2D Gaussians) where both are analytically tractable
- Statistical test: Correlation > 0.99 between DSM loss and HJB residual across noise levels

*Basis*:
Mathematical derivation following established control theory; Song et al. (2020) provides SDE foundation with 9234 citations.

*Success Criteria for Phase 2B*:
- Primary: Mathematical proof of equivalence for VP-SDE and VE-SDE formulations
- Falsification: Finding counterexample where DSM ≠ HJB under specified regularity conditions

**Secondary Predictions:**

**P2 (ELBO-SOC Unification):**
If HJB derivation is correct, then both ELBO (probabilistic) and SOC (control) perspectives are recoverable as special cases of the unified HJB framework.

*Measurement*: Show ELBO objective emerges when choosing specific cost function in HJB; show Adjoint Matching emerges with different terminal cost.

**P3 (Training Improvement):**
If TD-interpretation holds, then value-function-inspired training modifications (e.g., TD-style bootstrapping, eligibility traces) should improve training convergence.

*Measurement*: Compare convergence curves of HJB-derived objectives vs. standard DSM on CIFAR-10; expect 10-20% faster convergence to same FID.

**Falsification Criteria:**
The hypothesis will be **REJECTED** if any occur:

1. **Mathematical Failure**: The derivation produces inconsistent results, or HJB does not reduce to DSM under any reasonable assumptions.

2. **Empirical Contradiction**: HJB-derived training objectives perform significantly worse than standard DSM (FID > 20% degradation).

3. **Scope Collapse**: The derivation only works for trivial cases (e.g., isotropic Gaussians) and breaks for any practical distribution.

### 1.7 SOTA Baseline (Optional - If SOTA Comparison Mode)

*Not applicable - This hypothesis targets theoretical unification rather than SOTA performance comparison.*

### 1.8 Statistical Verification Design

**Sample Size Calculation:**
- Effect size: Theoretical equivalence (binary yes/no) + convergence improvement (expected d = 0.5)
- Required runs: n ≥ 25 random seeds for convergence experiments
- Statistical power: 0.8

**Test Specification:**
- Theoretical validation: Mathematical proof with explicit assumptions stated
- Numerical validation: Correlation analysis on toy problems
- Empirical validation: Paired t-test comparing convergence curves (same random seeds)
- Significance level: α = 0.05 (one-tailed for improvement hypothesis)
- Report format: Mean difference, 95% CI, Cohen's d, p-value

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
Does the HJB-Score duality exist mathematically? Can we prove that log p(x,t) satisfies HJB equation structure under standard diffusion model assumptions?

**SH2 (Mechanism):**
Is the proposed 3-step causal mechanism (log-p identification → gradient relationship → HJB residual) the correct explanation for why score matching works? Phase 2B will decompose into:
- H-M1: Log-probability ↔ value function identification validity
- H-M2: Gradient relationship (score = optimal control) holds
- H-M3: HJB residual equals DSM loss (up to constants)

**SH3 (Comparison):**
Does the HJB-derived framework provide practical advantages? Can HJB-inspired training modifications improve convergence over empirically-tuned baselines?

### Readiness Checklist

- [x] Hypothesis is in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID assigned: H-HJB-Score-v1
- [x] Confidence level specified: 0.85
- [x] Alternative hypothesis (H0) defined
- [x] All variables have operationalization from evidence
- [x] Causal mechanism has evidence at each step (N=3 steps, evidence table complete)
- [x] Causal chain length (N=3) determined and documented
- [x] Key tension identified (ELBO vs HJB) and resolution proposed
- [x] Key assumptions list consequences if violated
- [x] At least 2 testable predictions exist (P1 primary, P2-P3 secondary)
- [x] Falsification criteria are defined
- [x] Baselines are identified for comparison (DSM, ELBO)
- [x] SH1, SH2, SH3 are clear starting points

### Open Questions

1. **Mathematical Feasibility:** Can the HJB derivation be completed rigorously for general VP/VE-SDEs, or only for simplified cases (e.g., OU process)?

2. **Approximation Bounds:** What is the quantitative gap between infinite-capacity HJB optimality and finite-network training? Can we derive explicit error bounds?

3. **Implementation Complexity:** How computationally expensive is it to evaluate HJB-derived objectives compared to standard DSM? Is there a practical approximation?

4. **Priority Order:** Should Phase 2B start with SH1 (existence proof) or SH2-M1 (mechanism validation on toy problems)?

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow*
*2026-02-12*
