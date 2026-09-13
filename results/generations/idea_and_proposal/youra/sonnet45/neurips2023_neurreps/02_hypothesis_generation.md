# Phase 2A Extended: Hypothesis Clarification - Summary

**Date:** 2026-02-06
**Author:** Pray
**Source Round:** Round 1 - Equivariant Neural Dynamical Systems (ENDS)
**Status:** Ready for Phase 2B Verification Planning

---

## Executive Summary

**Hypothesis ID:** H1-ENDS
**Original Title:** Equivariant Neural Dynamical Systems (ENDS) with Projection-Based Integration
**Confidence Level:** 0.80 → 0.85 (increased after clarification)

**Clarified Core Hypothesis:**

For sequential molecular dynamics prediction tasks, E(n)-equivariant graph neural networks augmented with neural ODE temporal integration will achieve equivalent predictive accuracy (≤15% MAE) with **30-50% fewer training examples** compared to static E(n)-EGNN baselines, measured on MD17 and ISO17 benchmarks.

**Scope Narrowing Applied:**
- From: Broad claim about equivariance + neural ODEs + manifold learning on all graph tasks
- To: **Focused claim about neural ODE temporal integration improving sample efficiency on sequential molecular dynamics**

---

## 1. Clarified Hypothesis Statement

### 1.1 Core Statement

**Main Hypothesis (H1):**
Neural networks that model molecular dynamics as continuous-time trajectories via neural ODEs with E(n)-equivariant vector fields will require 30-50% fewer training examples than discrete layer-wise E(n)-equivariant baselines to achieve equivalent prediction accuracy (MAE ≤15%) on MD17 and ISO17 benchmarks.

**Alternative Hypothesis (H0):**
Neural ODE temporal integration provides no sample efficiency advantage (requires ≥95% of baseline training examples) over static E(n)-EGNN architectures for molecular dynamics prediction.

### 1.2 Variables

| Variable Type | Variable | Operationalization |
|---------------|----------|-------------------|
| **Independent** | Temporal integration method | Static E(n)-EGNN (discrete layers) vs. ENDS (neural ODE) |
| **Dependent** | Sample efficiency | Number of training examples to reach MAE ≤15% |
| **Dependent** | Prediction accuracy | Mean Absolute Error (MAE) on force prediction (kcal/mol/Å) |
| **Controlled** | Equivariance type | E(3) equivariance (rotation + translation invariance) |
| **Controlled** | Molecular datasets | MD17 (aspirin, benzene, ethanol, malonaldehyde, naphthalene) + ISO17 |
| **Controlled** | Training procedure | Adam optimizer, learning rate 1e-4, batch size 32 |
| **Controlled** | Model capacity | ~500k parameters for both architectures |

### 1.3 Causal Mechanism

**Proposed Causal Chain:**

```
Neural ODE modeling
    → Continuous trajectory representation z(t)
    → Temporal smoothness constraints (dz/dt Lipschitz continuous)
    → Reduced hypothesis space (bounded derivatives)
    → Exploitation of temporal autocorrelation in molecular dynamics
    → Fewer training examples needed for convergence
```

**Evidence for Causal Links:**

1. **Neural ODEs → Smoothness:** ODE solvers enforce error control requiring Lipschitz continuous vector fields (mathematical necessity)
2. **Smoothness → Sample Efficiency:** Biological evidence from grid cells (Gao 2020) maintaining temporal coherence, motor cortex smooth trajectories (Zhu 2025)
3. **Molecular Dynamics Autocorrelation:** Adjacent timesteps in MD simulations are highly correlated (forces change gradually with atomic positions)

**Key Tension (Identified):**
- **Assumption:** Molecular trajectories are sufficiently smooth (C¹ differentiable) to benefit from ODE modeling
- **Counter-evidence:** Molecular collisions, stiff bonds create discontinuities and multi-scale dynamics
- **Resolution:** Test on MD17/ISO17 which use pre-computed smooth trajectories (no explicit collision handling)

### 1.4 Key Assumptions

1. **Smoothness Assumption:** Molecular force fields produce trajectories smooth enough for neural ODE modeling (requires empirical validation)
2. **Equivariance Preservation:** Projection operator π_E(3) can restore approximate equivariance after ODE integration with acceptable error (ε < 0.01)
3. **Temporal Structure:** Sequential molecular dynamics contain exploitable temporal autocorrelation not captured by static models
4. **Computational Feasibility:** 5-10x training overhead is acceptable for research validation (not deployment)
5. **Sample Size:** ≥3,000 training examples provide sufficient signal for statistical comparison

### 1.5 Scope & Boundaries

**Applies To:**
- Sequential/temporal graph prediction tasks (molecular dynamics, protein folding trajectories)
- Datasets with E(n) symmetries (translation + rotation invariance)
- Settings where training data is limited (100-10k examples)

**Does NOT Apply To:**
- Static graph tasks (molecular property prediction without dynamics)
- Non-geometric data (language, images without 3D structure)
- Real-time inference applications (5-10x overhead prohibitive)
- Non-Euclidean symmetry groups (SO(3) only, SE(3) requires extension)

**Limitations:**
- Computational cost: 5-10x slower than baseline during training
- Projection artifacts: Approximate equivariance (not perfect)
- Data requirement: Minimum 3,000 examples for convergence
- Domain specificity: Molecular dynamics only (generalization untested)

### 1.6 Testable Predictions

**Primary Prediction (P1):**
ENDS will achieve MAE ≤15% on MD17 test sets using 3,000-7,000 training examples, while baseline E(n)-EGNN requires 10,000 examples for equivalent performance.

**Secondary Predictions:**
- **P2 (OOD Generalization):** ENDS will show 10-20% lower MAE on out-of-distribution molecular configurations (unseen conformations, extrapolated temperatures)
- **P3 (Temporal Accuracy):** ENDS will predict future molecular states (t+Δt) with <15% error, outperforming baseline by 15-25%

**Falsification Criteria:**
- **Reject H1 if:** ENDS requires ≥9,500 training examples (≥95% of baseline) to reach MAE ≤15%
- **Reject H1 if:** ENDS shows no OOD generalization advantage (<5% improvement)
- **Reject H1 if:** Projection-based integration violates equivariance by >5% (beyond acceptable tolerance)

### 1.7 Statistical Verification Design

**Experimental Design:**
- **Benchmark:** MD17 (5 molecules) + ISO17 (1 molecule) = 6 systems total
- **Sample Sizes:** Training set sizes: {1k, 3k, 5k, 7k, 10k} examples
- **Replication:** 3 random seeds per configuration
- **Total Runs:** 6 molecules × 5 sample sizes × 2 methods × 3 seeds = 180 experiments

**Statistical Test:**
- **Test Type:** Paired t-test (ENDS vs. baseline on same molecule/seed)
- **Null Hypothesis:** μ_ENDS - μ_baseline ≥ 0 (no sample efficiency improvement)
- **Significance Level:** α = 0.05 with Bonferroni correction (α/6 = 0.0083 per molecule)
- **Effect Size:** Cohen's d > 0.5 (medium effect) expected for 30-50% reduction

**Power Analysis:**
- Expected effect size: d = 0.7 (30-40% reduction)
- Required sample: n = 15 paired comparisons (5 molecules × 3 seeds)
- Statistical power: 1-β = 0.85 (85% chance of detecting true effect)

---

## 2. Contribution Summary

**Three Distinct Contributions:**

### 2.1 Theoretical Contribution
**What:** First framework unifying group-theoretic symmetry constraints (E(n)-equivariance) with continuous-time temporal dynamics (neural ODEs) in neural representations.

**Why Novel:** Phase 1 gap analysis confirmed no prior work combines static equivariance (Satorras 2021 E(n)-EGNN) with temporal dynamics. Kondor 2025 equivariance theory explicitly noted absence of temporal aspects.

**Validation Criterion:** Formal proof that equivariant vector fields on Riemannian manifolds preserve E(n) symmetries under continuous evolution (with projection-based restoration).

### 2.2 Methodological Contribution
**What:** Projection-based integration algorithm maintaining approximate E(n)-equivariance during neural ODE solving.

**Technical Details:**
- **Projection Operator:** π_E(3)(z) = argmin_{z' ∈ M_E(3)} ||z - z'||²
- **Integration Scheme:** Adaptive Runge-Kutta 4(5) with projection after each accepted step
- **Equivariance Tolerance:** ε < 0.01 (1% violation threshold)

**Validation Criterion:** Empirical measurement of equivariance violation across test trajectories, ablation study comparing projection vs. no projection.

### 2.3 Empirical Contribution
**What:** Demonstration that neural ODE temporal modeling improves sample efficiency by 30-50% on MD17/ISO17 molecular dynamics benchmarks.

**Quantification:**
- Baseline: 10,000 examples → MAE 15%
- ENDS: 5,000 examples → MAE 15% (50% reduction)
- Conservative estimate: 7,000 examples (30% reduction)

**Validation Criterion:** Statistical significance (p < 0.0083 per molecule, Bonferroni corrected) across 6 molecular systems with medium-to-large effect size (Cohen's d > 0.5).

**Ablation Studies:**
1. **ODE vs. Discrete:** Isolate benefit of continuous-time modeling
2. **Projection vs. No Projection:** Validate projection necessity
3. **Manifold vs. Euclidean:** Test learned Riemannian metric contribution

---

## 3. Key Related Work

### 3.1 Direct Baselines

**E(n) Equivariant Graph Neural Networks (Satorras+ 2021)**
- SS ID: 8ea9cb53779a8c1bb0e53764f88669bd7edf38f0
- Citations: 1315
- **Relation:** Primary baseline (static, no temporal dynamics)
- **Gap:** Does not model temporal evolution, treats each timestep independently

**Neural Ordinary Differential Equations (Chen+ 2018)** ⚠️ CITATION GAP
- **Relation:** Foundational neural ODE work (requires citation)
- **Gap:** Not applied to equivariant architectures or graph neural networks

### 3.2 Biological Motivation

**On Path Integration of Grid Cells (Gao+ 2020)**
- SS ID: 0a86759e37fd9b7494758223120af3e2d1aecb99
- Citations: 22
- **Relation:** Shows biological systems combine group symmetries with temporal integration
- **Transfer:** Equivariant vector fields inspired by grid cell dynamics

**Cerebellar Manifold Contractions (Zhu+ 2025)**
- SS ID: 2a51a9c01b7d33874cf4175da4491ce7af6c086d
- Citations: 3
- **Relation:** Demonstrates dynamic manifold geometry during learning
- **Transfer:** Motivates learned Riemannian manifolds in ENDS

**Hippocampal Hyperbolic Geometry (Zhang+ 2022)**
- SS ID: e4834b6a872dff3e3d15f63cd2a63d65c1669ff7
- Citations: 49
- **Relation:** Shows geometric structure evolves temporally
- **Transfer:** Evidence for temporal dynamics in geometric representations

### 3.3 Citation Gaps (Require Literature Review)

**Missing Citations:**
- [ ] **Chen+ 2018:** Neural ODEs original paper (CRITICAL)
- [ ] **Geometric Integration Theory:** Symplectic integrators, Lie group methods (HIGH PRIORITY)
- [ ] **Riemannian Neural Networks:** e3nn extensions, gauge-equivariant CNNs (MEDIUM)
- [ ] **MD17/ISO17 Benchmarks:** Original dataset papers (MEDIUM)
- [ ] **Equivariant RNNs/LSTMs:** Discrete-time temporal equivariance comparisons (LOW - different approach)

### 3.4 Theoretical Foundations

**Principles of Equivariant Neural Networks (Kondor 2025)**
- SS ID: a26840e13f3ab6f45933aad505c15b7fc95b7dbc
- Citations: 5
- **Relation:** Derives general form of equivariant operations
- **Gap Confirmation:** Does not address temporal/dynamical aspects (validates Gap 2)

---

## 4. Phase 2B Readiness

### 4.1 Decomposition Preview

The main hypothesis H1 will decompose into 3 sub-hypotheses for Phase 2B verification:

**SH1 (Existence):**
Neural ODE integration of E(n)-equivariant vector fields can be implemented with projection-based symmetry restoration achieving equivariance violation ε < 0.01.

- **Verification Method:** Unit tests on synthetic data with known symmetries
- **Success Criterion:** ||g·π(z) - π(g·z)|| < 0.01 for all g ∈ E(3), z ∈ test set

**SH2 (Mechanism):**
Temporal smoothness imposed by neural ODE modeling reduces overfitting on sequential molecular dynamics compared to discrete layer-wise architectures.

- **Verification Method:** Learning curve analysis + gradient norm statistics
- **Success Criterion:** ENDS shows lower validation loss variance and faster convergence on held-out timesteps

**SH3 (Comparison):**
ENDS achieves 30-50% sample efficiency improvement over static E(n)-EGNN baseline on MD17/ISO17 benchmarks.

- **Verification Method:** Full experimental protocol (180 runs, statistical testing)
- **Success Criterion:** p < 0.0083 (Bonferroni corrected), Cohen's d > 0.5

### 4.2 Readiness Checklist

- [x] **Hypothesis Statement:** Clear, testable, quantified predictions
- [x] **Variables Operationalized:** IV (temporal method), DV (sample efficiency), controls defined
- [x] **Causal Mechanism:** Specified with evidence and identified tensions
- [x] **Assumptions Explicit:** 5 key assumptions listed with validation plans
- [x] **Scope Boundaries:** Clear applicability and limitations
- [x] **Falsification Criteria:** Quantitative rejection thresholds defined
- [x] **Statistical Design:** Power analysis, sample size, significance testing
- [x] **Contributions Separated:** Theoretical, methodological, empirical contributions distinct
- [x] **Related Work Mapped:** Baselines, foundations, gaps identified
- [x] **Phase 2B Preview:** Sub-hypothesis decomposition outlined

**Overall Readiness:** ✅ **READY FOR PHASE 2B**

### 4.3 Open Questions for Phase 2B

1. **Projection Operator Implementation:** Which optimization algorithm for π_E(3) minimization? (Gradient descent vs. closed-form solution)
2. **ODE Solver Choice:** Adaptive RK45 vs. symplectic integrator for better equivariance preservation?
3. **Manifold Metric Parameterization:** Neural network architecture for learning φ(x) (MLP vs. equivariant layers)?
4. **Baseline Fairness:** Should baseline also use 500k parameters or match ENDS training time instead?
5. **Generalization Beyond Molecules:** Can results transfer to other sequential graph tasks (protein folding, robot trajectories)?

---

## 5. Confidence Assessment

**Initial Confidence (Phase 2A):** 0.80
**Post-Clarification Confidence:** 0.85

**Confidence Increase Rationale:**
- Scope narrowing reduced risk (focused on sample efficiency, not all claims)
- Causal mechanism made explicit with testable intermediate predictions
- Statistical design ensures rigor (power analysis, Bonferroni correction)
- Falsification criteria prevent post-hoc rationalization

**Remaining Uncertainty:**
- Smoothness assumption validity (15% uncertainty)
- Projection operator feasibility (10% uncertainty)
- Generalization beyond MD17/ISO17 (25% uncertainty - but out of scope)

---

**Generated:** 2026-02-06
**Workflow:** Phase 2A Extended (Focused, 8-step)
**Next Phase:** Phase 2B - Verification Planning (Sub-Hypothesis Decomposition)
