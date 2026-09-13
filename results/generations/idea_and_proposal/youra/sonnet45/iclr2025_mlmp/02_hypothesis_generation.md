# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-08
**Author:** Pray
**Source Round:** 02a_round_2_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-SGSTL-v1
**Confidence Level:** 0.80

**Main Hypothesis:**
Under conditions of multi-scale physics problems with continuous symmetries, if we apply Lie group perturbation analysis to learned scale transition operators and construct equivariant architectures enforcing discovered symmetries, then conservation law violations will reduce by 100× compared to soft constraints and out-of-distribution generalization will improve by 15-30%, because structural enforcement of mathematically-derived symmetries guarantees exact invariance while discovered conservation laws capture fundamental physical constraints.

**Alternative Hypothesis (H0):**
There is no significant difference in conservation law violation or out-of-distribution generalization between neural operators with automatically discovered and structurally enforced symmetries versus neural operators using soft constraint regularization or no symmetry enforcement.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| Scale transition operator Φ(x) | Independent | Trained neural operator (FNO or DeepONet) mapping between scale levels, measured by forward pass outputs | Continuous function space, evaluated on test grids |
| Perturbation transformations (rotation δθ, translation δx, scaling δλ) | Independent | Infinitesimal transformations from Lie algebra generators, applied via autodiff | δθ ∈ [-0.1, 0.1] rad, δx ∈ [-0.1, 0.1] units, δλ ∈ [0.9, 1.1] |
| Symmetry detection threshold ε | Independent | Error threshold for approximate symmetry identification, measured as \|Φ(T(x)) - T(Φ(x))\| | ε ∈ [10⁻⁴, 10⁻²] (adaptive based on operator accuracy) |
| Discovered symmetry generators {g₁, ..., gₖ} | Dependent | Identified Lie algebra generators via perturbation analysis, counted as number of discovered generators | k = 0-10 generators (rotation, translation, scaling, gauge) |
| Conservation law violation error | Dependent | Measured as \|ΔC\| where C is conserved quantity, computed on held-out test data | Target: <10⁻⁵ (structural enforcement) vs. ~10⁻³ (soft constraints) |
| Out-of-distribution generalization improvement | Dependent | Percentage improvement in prediction accuracy on OOD test sets compared to baseline | Expected: 15-30% relative improvement in MSE/L2 error |
| Base operator architecture | Controlled | Fixed architecture choice across all experiments | FNO (Fourier Neural Operator) or DeepONet |
| Training data distribution | Controlled | Fixed dataset and training protocol across comparisons | Standard physics benchmarks (2D/3D fluids, N-body, EM) |
| Physics domain | Controlled | Specific problem class held constant per experiment | Fluid dynamics, quantum mechanics, materials science, climate |

### 1.3 Causal Mechanism

The causal pathway from intervention to outcome consists of 4 sequential steps:

**Step 1: Perturbation Analysis → Symmetry Discovery**
Infinitesimal transformations from Lie algebra generators (rotation δθ, translation δx, scaling δλ) are applied to the learned operator Φ(x). Transformations that leave operator output approximately invariant (|Φ(T(x)) - T(Φ(x))| < ε) reveal underlying symmetry structure. The perturbation analysis recovers Lie group generators by measuring operator response to infinitesimal perturbations across the transformation space.

**Step 2: Symmetry Discovery → Conservation Law Derivation**
Discovered symmetry generators are mapped to conserved quantities via discrete Noether's theorem. For each generator gᵢ, the discrete variational principle (Marsden & West 2001 formulation) derives the corresponding conservation law Cᵢ. The discrete formulation ensures that conservation holds up to discretization error: ΔCᵢ = O(Δt²).

**Step 3: Conservation Law Derivation → Equivariant Architecture Construction**
Discovered symmetries are structurally enforced by replacing standard neural network layers with group-equivariant layers. For discrete groups (rotations, reflections), e2cnn framework provides E(2)-equivariant convolutions. For continuous groups (Euclidean transformations), egnn-pytorch implements E(n)-equivariant message passing. The architecture is reconstructed to satisfy |Φ(T(x)) - T(Φ(x))| = 0 by construction (exact equivariance).

**Step 4: Equivariant Architecture → Improved Performance**
Structural enforcement guarantees exact symmetry satisfaction (vs. learned approximation in baseline), leading to:
- **Conservation violation reduction**: 100× lower error (<10⁻⁵ vs. ~10⁻³) because structural constraints cannot be violated by optimization
- **OOD generalization improvement**: 15-30% gain because conserved quantities provide inductive bias that generalizes beyond training distribution

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step 1 → Step 2 | Mathematical Physics (Lie Group Theory) | Perturbation analysis is standard method for symmetry identification in dynamical systems | Strong (100+ years of theory) |
| Step 2 → Step 3 | Marsden & West (2001) Discrete Variational Mechanics | Discrete Noether's theorem establishes symmetry-conservation correspondence with error bounds | Strong (rigorous mathematical framework) |
| Step 3 → Step 4 | Luo et al. (2020, 57 citations) Gauge Equivariant NNs | Equivariant architectures achieve exact symmetry preservation when symmetries are known | Strong (empirical validation in quantum systems) |
| Step 4 → Outcome | Zhao et al. (2024, 106 citations) PINNs Review | Manual constraint enforcement improves physics fidelity; automatic discovery addresses key limitation | Medium (motivational, not direct validation) |

**Key Tension:**

**Tension:** Zhao et al. (2024) identifies manual specification of conservation laws as a key limitation in PINNs, suggesting need for automatic discovery. However, Luo et al. (2020) and Ortali et al. (2024) demonstrate that equivariant networks require KNOWN symmetries as input - they don't discover them. This creates an apparent contradiction: manual specification is limiting, but existing equivariant methods can't discover automatically.

**Resolution:** This hypothesis bridges the gap by introducing a two-stage approach: (1) FIRST discover symmetries automatically via perturbation analysis (addressing Zhao's limitation), (2) THEN enforce them structurally via equivariant architectures (leveraging Luo's enforcement mechanism). The verification plan tests whether perturbation analysis can successfully discover symmetries that are subsequently enforced, validating both stages independently and jointly.

### 1.4 Key Assumptions

1. **Assumption:** Scale transition operators that generalize well respect underlying continuous symmetries
   - **Evidence:** Equivariant networks (Luo et al. 2020, 57 citations) demonstrate that respecting symmetries improves performance. Bronstein et al. (Geometric Deep Learning) establish that symmetries provide inductive biases for generalization.
   - **Consequences if violated:** If learned operators do not contain exploitable symmetries, perturbation analysis will find no patterns, and the method reduces to baseline (no harm, but no benefit).

2. **Assumption:** Lie group perturbation analysis can identify symmetries from finite operator samples
   - **Evidence:** Mathematical physics literature uses perturbation methods for symmetry analysis. Olver (1986) "Applications of Lie Groups to Differential Equations" provides theoretical foundation for infinitesimal generator recovery.
   - **Consequences if violated:** False positives (spurious symmetries) or false negatives (missed symmetries) in discovery phase. Mitigated by synthetic validation protocol where ground truth is known.

3. **Assumption:** Discrete Noether's theorem applies to neural networks with bounded error
   - **Evidence:** Marsden & West (2001) "Discrete Mechanics and Variational Integrators" establishes discrete variational mechanics framework with error bounds ΔC = O(Δt²).
   - **Consequences if violated:** Derived conservation laws may not be conserved in practice, reducing to soft constraints. Critical for 100× violation reduction claim - requires rigorous discrete formulation.

4. **Assumption:** Discovered symmetries are physically meaningful, not spurious artifacts of training or discretization
   - **Evidence:** Validation protocol includes comparison with known symmetries (rotation, translation, energy/momentum conservation) on benchmark problems.
   - **Consequences if violated:** Enforcing spurious symmetries may harm performance. Addressed through multi-criteria validation: (1) conservation under dynamics, (2) OOD generalization improvement, (3) physical interpretability.

5. **Assumption:** Equivariant architecture construction does not introduce prohibitive computational overhead or training instability
   - **Evidence:** e2cnn and egnn-pytorch are mature frameworks (669 and 519 GitHub stars) with established training protocols. Overhead is 1.2-1.5× standard training (documented in literature).
   - **Consequences if violated:** Theoretical benefits may not materialize in practice due to computational cost or optimization difficulties. Requires empirical validation on realistic problem scales.

### 1.5 Scope & Boundaries

**Where Hypothesis Applies:**
- Multi-scale physics problems with continuous symmetries (fluids, quantum mechanics, materials science, climate)
- Neural operator architectures that learn scale transition mappings (FNO, DeepONet, graph neural operators)
- Problems where conservation laws are known or expected (energy, momentum, angular momentum, mass, charge)
- Scenarios where training data captures symmetry structure (sufficient coverage of transformation space)
- Applications where exact symmetry enforcement is desirable (high-fidelity surrogate models, long-time integration)

**Where It Does NOT Apply:**
- Problems with only discrete symmetries without continuous group structure (permutation-only symmetries)
- Highly chaotic systems where no symmetries exist or are overwhelmed by chaos
- Domains where symmetries are explicitly broken (symmetry-breaking phase transitions, dissipative systems with friction)
- Problems where learned operators are too poorly trained (high approximation error prevents reliable symmetry detection)
- Applications where computational overhead of equivariant architectures is prohibitive (real-time inference constraints)

**Known Limitations:**
1. **Discovery accuracy depends on operator quality**: Poorly trained operators may yield spurious symmetries or miss true ones
2. **Discrete formulation introduces approximation**: Conservation holds up to O(Δt²) error, not exact
3. **Global symmetry assumption**: Standard equivariant architectures assume global symmetries; scale-dependent or local symmetries require hierarchical extensions
4. **Computational cost**: Perturbation analysis adds O(kN) forward passes (k generators, N samples); equivariant training has 1.2-1.5× overhead
5. **Emergent symmetry validation**: For symmetries not known a priori, validation relies on multi-criteria heuristics (conservation, generalization, interpretability) rather than ground truth

### 1.6 Testable Predictions

**Primary Prediction:**

**P1 (Conservation Law Violation - 100× Reduction Target)**

Our approach will achieve conservation law violation error |ΔC| < 10⁻⁵ (structural enforcement) compared to |ΔC| ~ 10⁻³ (soft constraint baseline), representing a 100× reduction.

*Measurement*:
- Metric: Mean absolute conservation violation |ΔC| on held-out test data
- Conserved quantities: Energy, momentum (linear and angular), mass (for applicable domains)
- Comparison: SGSTL (structural enforcement) vs. standard PINN (soft constraint loss term)
- Statistical test: Paired t-test across n ≥ 20 random seeds, α = 0.05
- Target: |ΔC|_SGSTL < 10⁻⁵ AND |ΔC|_SGSTL / |ΔC|_baseline ≤ 0.01 (100× reduction)

*Basis*:
Domain standard for physics neural networks: soft constraints achieve ~10⁻³ violation; structural enforcement should approach machine precision (~10⁻⁵ to 10⁻⁶ for float32).

*Success Criteria for Phase 2B*:
- Primary: 100× reduction in conservation violation (p < 0.05)
- Falsification: Violation reduction < 10× triggers hypothesis rejection

**Secondary Predictions:**

**P2 (Out-of-Distribution Generalization - 15-30% Improvement Target)**

Our approach will achieve 15-30% relative improvement in prediction accuracy on out-of-distribution test sets compared to symmetry-agnostic baseline.

*Measurement*:
- Metric: Relative L2 error or MSE on OOD test data (different Reynolds numbers, initial conditions, boundary conditions)
- Comparison: SGSTL vs. standard neural operator (FNO/DeepONet without symmetry enforcement)
- Statistical test: Improvement = (Error_baseline - Error_SGSTL) / Error_baseline × 100%
- Target: 15% ≤ Improvement ≤ 30% (modest but meaningful gain)

*Basis*:
Literature on equivariant networks shows 10-40% OOD improvement when symmetries are known (Cohen & Welling 2016); automatic discovery may achieve lower end due to imperfect symmetry identification.

**P3 (Symmetry Discovery Accuracy - >90% Recall on Known Symmetries)**

Perturbation analysis will recover >90% of known symmetries (rotation, translation, scaling) on synthetic benchmark problems with ground truth.

*Measurement*:
- Metric: Recall = (Discovered ∩ True) / True
- Synthetic validation: Create operators with known symmetry groups (E(2), SO(3), gauge symmetries)
- Target: Recall > 90%, False Positive Rate < 10%

*Basis*:
Synthetic validation establishes that discovery mechanism works before deployment on real problems where ground truth is unknown.

**P4 (Mechanism Validation - Causal Link Ablation)**

Each stage in the 4-step causal chain contributes independently:
- Discovery only (no enforcement): Identifies symmetries but doesn't reduce violation
- Enforcement of wrong symmetries: Harms performance (validates discovery is not spurious)
- Full pipeline: Achieves combined benefit (validates causal chain)

*Measurement*: Ablation study isolating each causal link's contribution

**Falsification Criteria:**

The hypothesis will be **REJECTED** if any of the following occur:

1. **Primary Failure**: Conservation violation reduction < 10× (target is 100×)
   - Indicates that structural enforcement does not provide meaningful advantage over soft constraints

2. **Mechanism Failure**: Perturbation analysis recall < 50% on synthetic validation
   - Indicates core discovery mechanism is fundamentally flawed

3. **Negative Transfer**: OOD generalization worsens compared to baseline (negative improvement)
   - Indicates discovered symmetries are spurious and harm rather than help

4. **Baseline Equivalence**: No statistically significant difference (p ≥ 0.05) from symmetry-agnostic baseline on any metric
   - Indicates method adds no value despite added complexity

5. **Computational Infeasibility**: Total overhead > 5× baseline training time
   - Indicates practical implementation is prohibitively expensive

### 1.7 SOTA Baseline (Optional - If SOTA Comparison Mode)

*Not applicable - Absolute performance validation mode (no SOTA comparison)*

### 1.8 Statistical Verification Design

**Sample Size Requirements:**
- Minimum n ≥ 20 runs (random seeds) per condition for statistical power 0.8
- For conservation violation: paired t-test (SGSTL vs. baseline on same problems)
- For OOD generalization: independent samples t-test (different test distributions)

**Statistical Tests:**
- Conservation violation: Paired t-test (α = 0.05, one-tailed test for "less than")
- OOD improvement: Independent t-test (α = 0.05, one-tailed test for "greater than")
- Symmetry discovery: Exact count on synthetic problems (no statistical test, deterministic)

**Effect Size Requirements:**
- Conservation violation: Cohen's d > 1.0 (large effect size expected for 100× reduction)
- OOD generalization: Cohen's d > 0.5 (medium effect size expected for 15-30% improvement)

**Reporting Format:**
- Mean ± Standard Deviation with 95% Confidence Intervals
- Effect sizes (Cohen's d) for all comparisons
- p-values with Bonferroni correction for multiple comparisons
- Full ablation study results (contribution of each causal link)

---

## 4. Phase 2B Readiness

### Decomposition Preview

**Total Sub-Hypotheses for Phase 2B:** 6 (SH1: 1, SH2: 4 mechanism steps, SH3: 1)

**SH1 (Existence - Foundation):**
"Does automatic symmetry discovery via Lie group perturbation analysis successfully identify continuous symmetries (rotation, translation, scaling) in learned neural scale transition operators with >90% recall on synthetic benchmarks?"

- Maps to: Primary prediction P3 (symmetry discovery accuracy)
- Verification type: Empirical (synthetic validation with ground truth)
- Critical: MUST PASS - if discovery doesn't work, entire pipeline fails

**SH2 (Mechanism - Core):**
"Is the 4-stage causal mechanism (Perturbation → Discovery → Derivation → Enforcement → Performance) the actual cause of 100× conservation violation reduction and 15-30% OOD generalization improvement?"

Phase 2B will decompose into 4 mechanism sub-hypotheses:

- **H-M1:** Perturbation analysis → Symmetry discovery (validates Step 1)
- **H-M2:** Symmetry discovery → Conservation law derivation via discrete Noether (validates Step 2)
- **H-M3:** Conservation laws → Equivariant architecture construction (validates Step 3)
- **H-M4:** Equivariant enforcement → Performance improvement (100× violation, 15-30% OOD) (validates Step 4)

- Verification type: Causal ablation study (isolate each link's contribution)
- Critical: Determines explanatory power and identifies which stage(s) drive benefit

**SH3 (Comparison - Validation):**
"Does SGSTL (automatic discovery + structural enforcement) outperform all baseline approaches: (1) manual equivariant networks, (2) soft constraint PINNs, (3) hard constraint PINNs, (4) symmetry-agnostic operators, (5) augmentation-based methods?"

- Maps to: Primary predictions P1-P2, comprehensive baseline comparison
- Verification type: Comparative empirical (head-to-head benchmarking)
- Critical: Determines practical value vs. existing SOTA methods

### Readiness Checklist

- [✓] Hypothesis is in "Under [C], if [X], then [Y] because [Z]" format
- [✓] Hypothesis ID assigned (H-SGSTL-v1)
- [✓] Confidence level specified (0.80)
- [✓] Alternative hypothesis (H0) defined (no difference vs. soft constraints)
- [✓] All variables have operationalization from evidence (9 variables with measurement methods)
- [✓] Causal mechanism has evidence at each step (4 steps with evidence table)
- [✓] Causal chain length (N=4) determined and documented
- [✓] Key tension identified (manual specification limitation vs. known symmetry requirement) and resolution proposed (two-stage discovery-then-enforcement)
- [✓] Key assumptions list consequences if violated (5 assumptions with mitigation strategies)
- [✓] At least 2 testable predictions exist with primary marked (4 predictions: P1-conservation, P2-OOD, P3-discovery, P4-mechanism)
- [✓] Falsification criteria are defined (5 rejection conditions with quantitative thresholds)
- [✓] Baselines are identified for comparison (6 baselines: manual equivariant, soft/hard PINNs, symmetry-agnostic, augmentation)
- [✓] SH1, SH2 (4 sub-hypotheses), SH3 are clear starting points for Phase 2B decomposition

**All Phase 2B input requirements satisfied.**

### Open Questions

1. **Resource Requirements:** What are the computational requirements for perturbation analysis across different problem scales?
   - Need to benchmark: O(kN) forward passes for k=10 generators, N=1000 samples
   - Estimate GPU-hours for 2D/3D fluid problems, N-body systems
   - Determine if parallelization across perturbations achieves near-linear speedup

2. **Data Availability:** Are there established benchmark datasets with known conservation laws and symmetries for validation?
   - Identify: Public datasets for 2D/3D Navier-Stokes, N-body gravitational systems, electromagnetic simulations
   - Verify: Ground truth symmetries are documented (rotation, translation, Galilean invariance, etc.)
   - Assess: Dataset quality and coverage of transformation space

3. **Technical Feasibility:** What are the implementation challenges for discrete Noether's theorem formulation?
   - Clarify: Discrete Lagrangian construction for neural operators
   - Investigate: Existing implementations of discrete variational integrators
   - Prototype: Simple 1D/2D toy problems before scaling to realistic physics

4. **Priority Verification Order:** Which sub-hypothesis should be verified first in Phase 2B?
   - Recommendation: SH1 (existence/discovery) FIRST - if perturbation analysis fails, entire pipeline fails
   - Then: SH2 mechanism steps sequentially (validate causal chain)
   - Finally: SH3 (comparison) after confirming method works

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow (Focused)*
*2026-02-08*
