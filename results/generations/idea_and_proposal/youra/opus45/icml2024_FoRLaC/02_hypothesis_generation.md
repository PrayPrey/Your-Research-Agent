# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-12
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-ContractionRegret-v1
**Confidence Level:** 0.83

**Main Hypothesis:**
Under the condition of incrementally stabilizable nonlinear systems with state dimension ≤10, if a neural contraction metric M_φ(x) is jointly learned with a controller π_θ(x) and verified to have contraction rate ρ ∈ (0,1) via α,β-CROWN, then the adaptive control regret will scale as R(T) ≤ O(√T · poly(1/(1-ρ), d)) because the verified contraction rate bounds trajectory perturbation decay, enabling trajectory sensitivity analysis that connects parameter estimation error to regret.

**Alternative Hypothesis (H0):**
The contraction rate ρ does not provide a sufficient quantitative characterization of system behavior to derive finite-time regret bounds for nonlinear adaptive control. That is, either (a) no polynomial relationship exists between ρ and regret, or (b) the constants in such a bound are so large as to be practically meaningless (e.g., exponential in system dimension).

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| Contraction rate ρ | Independent | Verified via α,β-CROWN neural network verifier on learned metric M_φ(x) | ρ ∈ (0.5, 0.99) - tighter ρ gives better bounds |
| State dimension d | Independent | Number of state variables in dynamical system | d ∈ {2, 4, 6, 8, 10} |
| Time horizon T | Independent | Total discrete time steps during online learning | T ∈ {1000, 5000, 10000, 50000} |
| Regret R(T) | Dependent | Cumulative suboptimality: R(T) = Σ_{t=1}^T [c(x_t, u_t) - c*(x_t, u*_t)] | Expected: O(√T) scaling |
| Verification time | Dependent | Computational time for α,β-CROWN to certify contraction | Expected: <10 min for d≤10 |
| Training convergence | Dependent | Epochs to achieve target contraction rate | Expected: 100-500 epochs |
| System dynamics class | Controlled | Incrementally stabilizable nonlinear systems | Fixed per experiment |
| NN architecture | Controlled | 2-layer MLP, ReLU activations, width 64-128 | Fixed: [d, 64, 64, d×d] |
| Learning rate | Controlled | Optimizer step size for joint training | Fixed: 1e-3 (Adam) |

### 1.3 Causal Mechanism

**Causal Chain (N=3 steps):**

```
[Step 1: Learn Neural Contraction Metric]
         ↓
[Step 2: Obtain Verified Contraction Rate ρ]
         ↓
[Step 3: Derive Trajectory Perturbation Decay Bound]
         ↓
[Outcome: Regret Bound R(T) ≤ O(√T · poly(1/(1-ρ), d))]
```

**Step 1 → Step 2:** Joint training of controller π_θ(x) and metric M_φ(x) with contraction regularization, followed by post-hoc verification using α,β-CROWN to certify the contraction rate ρ. The verification provides rigorous mathematical guarantee that the learned metric satisfies the contraction condition.

**Step 2 → Step 3:** The verified contraction rate ρ implies that trajectory deviations decay exponentially: ||δx(t)|| ≤ ρ^t ||δx(0)||. This is a direct consequence of contraction theory (Lohmiller & Slotine 1998) - the metric M(x) defines a Riemannian distance that contracts along system trajectories.

**Step 3 → Outcome:** Bounded trajectory sensitivity enables perturbation-based regret analysis. Parameter estimation errors cause trajectory perturbations, which decay at rate ρ. Integrating these perturbations over horizon T yields the regret bound, analogous to the LQR analysis by Dean et al. 2018 but generalized via contraction structure.

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step 1 → Step 2 | Li et al. 2025 (Neural Contraction Metrics) | α,β-CROWN successfully verifies contraction for discrete-time nonlinear systems with ReLU networks | Strong |
| Step 2 → Step 3 | Lohmiller & Slotine 1998 (Contraction Theory) | Contraction rate directly bounds trajectory convergence: ||δx(t)|| ≤ ρ^t ||δx(0)|| | Strong |
| Step 3 → Outcome | Boffi et al. 2020 (Regret for Nonlinear Control) | Proved √T regret for certainty equivalence control using contraction/Lyapunov stability | Strong |

**Key Tension:**
- **Tension:** Boffi et al. 2020 achieves √T regret for nonlinear systems but requires KNOWN dynamics with UNKNOWN disturbances. Our hypothesis extends to UNKNOWN dynamics, which may require stronger assumptions.
- **Resolution:** This verification plan tests whether the contraction metric learning framework can achieve similar regret bounds when dynamics are learned online. The key is that the verified contraction rate provides a quantitative stability certificate even for learned dynamics.

### 1.4 Key Assumptions

| # | Assumption | Evidence | Consequence if Violated |
|---|------------|----------|------------------------|
| A1 | System admits a contraction metric (incrementally stabilizable) | Tsukamoto et al. 2021 showed robotic systems, vehicle dynamics satisfy this | Hypothesis does not apply; must use alternative stability frameworks (Lyapunov) |
| A2 | Neural network can approximate true contraction metric with bounded error ε | Universal approximation theorem; Li et al. 2025 practical demonstration | Verification may fail or produce loose bounds; regret may not scale as predicted |
| A3 | α,β-CROWN can verify contraction conditions for d≤10 in practical time | Li et al. 2025 demonstrated feasibility for discrete-time systems | Scalability limitation; must resort to probabilistic/sampling-based verification |
| A4 | Parameter estimation error decays at rate related to contraction | Boffi et al. 2020 theoretical foundation | Core regret derivation fails; bound structure may be different |

### 1.5 Scope & Boundaries

**Where Hypothesis Applies:**
- Incrementally stabilizable nonlinear dynamical systems
- State dimension d ≤ 10 (verification scalability limit)
- Discrete-time systems (continuous-time extension as future work)
- Systems with full state observation (output feedback as extension)
- Deterministic or stochastic dynamics with bounded disturbances

**Where Hypothesis Does NOT Apply:**
- Systems with limit cycles or multi-stable attractors (violate incremental stability)
- High-dimensional systems (d > 10) without scalability improvements
- Systems with discontinuous dynamics (violate smooth contraction)
- Output feedback settings (require observer design)
- Systems that do not admit any contraction metric

**Known Limitations:**
1. **Verification scalability:** α,β-CROWN verification time scales exponentially with network size; practical for d≤10
2. **Contraction existence:** Not all systems admit contraction metrics; this is a structural requirement
3. **Constant factors:** The poly(1/(1-ρ), d) term may have large constants that affect practical utility
4. **Linear reduction proof:** The claim that bounds reduce to LQR in linear case requires formal proof

### 1.6 Testable Predictions

**Primary Prediction:**
**P1 (Regret Scaling):**
Our approach will achieve regret R(T) that scales as O(√T) with respect to time horizon T.

*Measurement:*
- Fit log(R(T)) vs log(T) across multiple time horizons {1000, 5000, 10000, 50000}
- Success criterion: Slope ≤ 0.55 (allowing for constants, true √T gives slope 0.5)
- Statistical test: Linear regression with 95% CI on slope
- Required runs: n ≥ 20 per time horizon

*Basis:*
Boffi et al. 2020 achieved √T regret for known dynamics with contraction. Simchowitz 2020 proved √T is optimal for LQR. Our extension to learned dynamics should preserve this scaling.

*Falsification Criteria:*
- **REJECT** if slope > 0.7 (closer to linear T scaling)
- **REJECT** if variance is too high for meaningful fit (R² < 0.8)

**Secondary Predictions:**

**P2 (Contraction Rate Dependence):**
Regret scales polynomially with 1/(1-ρ). Systems with tighter contraction (smaller ρ) achieve lower regret.

*Measurement:*
- Train controllers on systems with varying ρ ∈ {0.5, 0.7, 0.8, 0.9, 0.95}
- Fit R(T) vs 1/(1-ρ) at fixed T=10000
- Success criterion: Polynomial relationship (degree 1-3)

**P3 (Linear Case Reduction):**
For linear systems (LQR), our bound reduces to known LQR regret bounds (Dean et al. 2018).

*Measurement:*
- Apply method to linear systems and compare regret to LQR baseline
- Success criterion: Regret within 2× of LQR-specific bound
- Validates theoretical reduction proof

**Falsification Criteria:**

The hypothesis will be **REJECTED** if any occur:

1. **Primary Failure:** Regret slope > 0.7 (not √T scaling)
   - This indicates fundamental flaw in regret derivation mechanism

2. **Mechanism Failure:** Verification fails for majority of trained networks
   - Indicates contraction learning is not reliably achievable

3. **Baseline Failure:** Performance worse than simple model-based RL (e.g., PILCO) without theoretical guarantees
   - Indicates practical utility is negative despite theory

### 1.7 SOTA Baseline (Optional - If SOTA Comparison Mode)

*Not applicable - Absolute Performance Mode*

### 1.8 Statistical Verification Design

**Sample Size Calculation:**
- Target effect: √T regret scaling (slope = 0.5 in log-log plot)
- Alternative: Linear scaling (slope = 1.0)
- Effect size (Cohen's d): ~1.0 (large effect)
- Required runs: n ≥ 20 per condition
- Statistical power: 0.9

**Test Specification:**
- Primary test: Linear regression on log(R(T)) vs log(T)
- Secondary test: ANOVA across contraction rate conditions
- Significance level: α = 0.05
- Multiple comparison correction: Bonferroni

**Report Format:**
- Regret vs T plot (log-log scale) with fitted slope and 95% CI
- Regret vs 1/(1-ρ) plot with polynomial fit
- Comparison table: Our method vs LQR baseline (linear case)
- Verification time statistics

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Does neural contraction metric learning achieve verified contraction rates for incrementally stabilizable nonlinear systems?"
- Maps to: Primary prediction P1 prerequisites
- Verification type: Empirical (training + verification experiments)
- Critical: MUST PASS for Phase 2B to proceed

**SH2 (Mechanism):**
"Is the causal chain [learned metric → verified ρ → trajectory decay → regret bound] the actual mechanism producing √T regret?"

Phase 2B will decompose into N=3 sub-hypotheses:
- **H-M1:** Verified contraction rate ρ from neural metric learning
- **H-M2:** Trajectory perturbation decay bounded by ρ^t
- **H-M3:** Perturbation integration yields √T regret scaling

**SH3 (Comparison):**
"Does our contraction-based approach achieve regret bounds competitive with or better than LQR bounds for linear systems?"
- Maps to: Secondary prediction P3
- Verification type: Comparative empirical
- Critical: Determines theoretical consistency

### Readiness Checklist

- [x] Hypothesis is in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID assigned: H-ContractionRegret-v1
- [x] Confidence level specified: 0.83
- [x] Alternative hypothesis (H0) defined
- [x] All variables have operationalization from evidence
- [x] Causal mechanism has evidence at each step (N=3 steps, evidence table)
- [x] Causal chain length (N=3) determined and stored
- [x] Key tension identified and resolution proposed
- [x] Key assumptions list consequences if violated
- [x] At least 2 testable predictions exist (3 predictions, P1 marked primary)
- [x] Falsification criteria are defined (3 failure conditions)
- [x] Baselines identified: LQR (Dean 2018), Boffi 2020, Tsukamoto 2021
- [x] SH1, SH2, SH3 are clear starting points

### Open Questions

1. **Computational Resources:** What GPU/compute is needed for α,β-CROWN verification on 10-dimensional systems? Estimated 1-10 hours per verification.

2. **Benchmark Selection:** Which nonlinear control benchmarks best demonstrate the hypothesis? Candidates: Pendulum, CartPole, Acrobot (MuJoCo), or custom polynomial dynamics.

3. **Verification Priority:** Should we first prove theoretical regret bound (formal proof) or empirically validate √T scaling? Recommend: Parallel execution - theory (SH2) + empirics (SH1, SH3).

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow (Focused)*
*2026-02-12*
