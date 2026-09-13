# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-13
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md (Round 1 - Linear-PCCP)
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-LinearPCCP-v1
**Confidence Level:** 0.82

**Main Hypothesis:**
Under the condition that physics constraints are expressible as linear equations (Ax=b), if conformal prediction calibration is performed on prediction sets projected onto the constraint manifold, then the resulting prediction intervals will achieve both (1) rigorous finite-sample coverage guarantees and (2) zero physics constraint violations, because projection onto linear constraint manifolds preserves the exchangeability property required for conformal prediction coverage while restricting predictions to the physically valid subspace.

**Alternative Hypothesis (H0):**
Projecting conformal prediction sets onto linear physics constraint manifolds does NOT preserve coverage guarantees, OR the computational overhead of projection negates the practical benefits of physics-constrained uncertainty quantification.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| Constraint Type | Independent | Linear constraints Ax=b derived from conservation laws (mass, momentum, energy), boundary conditions | Mass conservation, momentum balance, Dirichlet/Neumann BCs |
| Calibration Set Size | Independent | Number of calibration samples n from PINN predictions | 100-1000 samples |
| PINN Architecture | Controlled | Fixed MLP architecture for fair comparison | 4 layers × 50 neurons, tanh activation |
| PDE Benchmark | Controlled | Standard PINN benchmark equations | Burgers, Navier-Stokes 2D, Heat equation |
| Coverage Rate | Dependent | Proportion of true values within prediction intervals | Target: 1-α (e.g., 90%, 95%) |
| Interval Width | Dependent | Average width of prediction intervals | Minimize while maintaining coverage |
| Physics Violation Rate | Dependent | Proportion of predictions violating Ax=b constraint | Target: 0% (hard constraint) |

### 1.3 Causal Mechanism

**Causal Chain (N=3 steps):**

```
Step 1: Physics-Aware Nonconformity Scoring
    ↓
Step 2: Linear Manifold Projection
    ↓
Step 3: Conditional Coverage Preservation
    ↓
[Outcome]: Rigorous UQ with Zero Violations
```

**Step 1 → Step 2:** PINN generates base predictions, then physics-aware nonconformity score R(x,y) = ||y-ŷ||₂ + λ||Aŷ-b||₂ is computed.

**Step 2 → Step 3:** Nonconformity scores on calibration set are computed, then prediction sets are projected onto constraint manifold using P = I - A'(AA')⁻¹A.

**Step 3 → Outcome:** Projected prediction sets undergo coverage quantile computation. Conditional CP theory shows coverage is preserved under affine transformations when exchangeability holds.

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step 1 → Step 2 | Yu et al. 2025 (arXiv:2509.13717) | CP framework for PINNs with nonconformity scores achieves distribution-free UQ | Strong |
| Step 2 → Step 3 | Podina et al. 2024 (ICLR Workshop) | C-PINNs provide valid coverage for forward/inverse problems | Strong |
| Step 3 → Outcome | Amann 2025 (Conditional CP) | Coverage preserved under stable transformations with conditional validity | Strong |

**Key Tension:**
- **Tension:** Yu et al. 2025 treats physics as soft regularization, while Linear-PCCP proposes hard constraint projection.
- **Resolution:** This verification plan tests whether HARD constraint projection achieves strictly better physics validity while maintaining coverage.

### 1.4 Key Assumptions

1. **Conservation laws expressible as linear constraints** - Consequence if violated: Cannot apply linear projection; breaks tractability
2. **Exchangeability of calibration data** - Consequence if violated: Coverage guarantees fail
3. **Base PINN provides reasonable predictions** - Consequence if violated: CP cannot fix fundamentally broken models
4. **Constraint matrix A is known/derivable** - Consequence if violated: Cannot construct projection operator

### 1.5 Scope & Boundaries

**Applies to:** PDEs with LINEAR conservation laws, linear boundary conditions, safety-critical physics simulations

**Does NOT apply to:** Nonlinear constraints, unknown governing equations, non-exchangeable data

**Limitations:** Linear constraint scope, requires explicit A, O(n³) projection overhead

### 1.6 Testable Predictions

**Primary Prediction:**

**P1 (Coverage + Zero Violations):**
Linear-PCCP will achieve target coverage rate (1-α) while maintaining physics violation rate = 0%.

*Measurement:*
- Coverage rate ≥ (1-α) with p < 0.05
- Physics violation rate = 0%
- Sample size: n ≥ 500 test points across multiple PDEs

*Falsification:* Coverage < (1-α - 0.05) OR violation rate > 0%

**Secondary Predictions:**

**P2:** Linear-PCCP achieves equivalent coverage to soft-constraint CP with strictly better (zero) physics violation rate.

**P3:** Linear-PCCP intervals are narrower than unconstrained CP for same coverage level.

**Falsification Criteria:**

1. **Coverage Failure:** Empirical coverage < (1-α - 0.05)
2. **Projection Failure:** Physics violation rate > 0%
3. **Efficiency Failure:** Intervals >20% wider with no coverage improvement

### 1.8 Statistical Verification Design

**Sample Size:** n = 500 test points per PDE benchmark, 3 benchmarks = 1500 total
**Tests:** One-sided binomial (coverage), exact count (violations), paired t-test (width)
**Significance:** α = 0.05

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Does Linear-PCCP achieve valid coverage (≥ 1-α) on standard PINN benchmark PDEs with linear constraints?"
- Verification type: Empirical
- Critical: MUST PASS

**SH2 (Mechanism):**
"Is the linear manifold projection the mechanism enabling simultaneous coverage + zero violations?"
- Sub-hypotheses: H-M1 (nonconformity scoring), H-M2 (projection), H-M3 (coverage preservation)
- Verification type: Ablation studies + theoretical analysis

**SH3 (Comparison):**
"Does Linear-PCCP outperform soft-constraint CP on physics validity while maintaining competitive coverage?"
- Verification type: Comparative empirical

**Total Sub-Hypotheses:** 5 (SH1: 1, SH2: 3, SH3: 1)

### Readiness Checklist

- [x] Hypothesis in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID: H-LinearPCCP-v1
- [x] Confidence: 0.82
- [x] H0 defined
- [x] Variables operationalized
- [x] Causal mechanism with evidence (N=3)
- [x] Key tension identified
- [x] Assumptions with consequences (4)
- [x] Testable predictions (3, P1 primary)
- [x] Falsification criteria (3)
- [x] Baselines identified
- [x] SH1/SH2/SH3 defined

### Open Questions

1. **Implementation:** Algorithm for extracting constraint matrix A from PDE discretizations?
2. **Computation:** Is O(n³) projection acceptable for large-scale problems?
3. **Priority:** Verify SH1 on simple PDEs first before SH2 on complex PDEs?

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow (YOLO Mode)*
*2026-02-13*
