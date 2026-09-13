# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-12
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-AEC-v1
**Confidence Level:** 0.85

**Main Hypothesis:**
Under condition of neural networks with recurrent dynamics constrained to specific manifold topologies, if the attractor manifold is topologically isomorphic to the task's symmetry group, then the network will exhibit equivariant representations by construction, because the activity bump position on the attractor encodes a group element and bump translation implements the group action.

**Alternative Hypothesis (H0):**
There is no systematic relationship between attractor manifold topology and equivariance; any observed equivariance in attractor networks is incidental rather than a consequence of manifold-group isomorphism.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| Attractor manifold topology | Independent | Ring (SO(2)), Torus (T²), or Sphere (SO(3)) enforced via soft topological loss | Discrete choices: {ring, torus, sphere} |
| Equivariance error | Dependent | ‖f(g·x) - g·f(x)‖ measured using Lie derivative | 0.0 (perfect) to 1.0+ (no equivariance) |
| Task accuracy | Dependent | Classification accuracy or path integration error | 0-100% or RMSE in degrees |
| Network architecture | Controlled | Fixed layer count, hidden dimension, activation | Standard: 3-5 layers, 128-512 hidden |
| Training procedure | Controlled | Learning rate, batch size, epochs | LR=1e-4, batch=32, 100 epochs |

### 1.3 Causal Mechanism

**Causal Chain (N=3):**

```
Step 1: Soft Topological Constraints
    ↓ (loss term penalizes deviation from target topology)
Step 2: Manifold-Group Isomorphism
    ↓ (each point on manifold M corresponds to group element in G)
Step 3: Group Action via Bump Dynamics
    ↓ (input transformations translate activity bump = group action)
Outcome: Equivariant Representations
```

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step 1 → Step 2 | Xu et al. (2025) Principle of Isomorphism | Toroidal topology emerges from task constraints; population activity preserves mathematical structure | Strong |
| Step 2 → Step 3 | Biswas et al. (2024) Fly Connectome | Ring attractor dynamics from biological connectivity implement SO(2) heading representation | Strong |
| Step 3 → Outcome | Bronstein et al. (2021) GDL Blueprint | Group action on representations defines equivariance; mathematical foundation established | Strong |

**Key Tension:**
- **Tension:** Exact equivariance requires hard architectural constraints (e3nn approach), but biological plausibility and gradient-based training require soft constraints (CANN approach)
- **Resolution:** This verification plan tests whether soft constraints achieve "good enough" equivariance (<0.1 error via Lie derivative) while enabling differentiable training. The tradeoff between exactness and trainability is quantified.

### 1.4 Key Assumptions

1. **Continuous attractor dynamics approximation**
   - Statement: Discrete neural networks can approximate continuous attractor dynamics with sufficient precision
   - Evidence: Biswas et al. (2024) successfully derived ring attractor from discrete connectome
   - Consequence if violated: Manifold structure becomes fragmented; equivariance degrades proportionally to approximation error

2. **Soft constraint sufficiency**
   - Statement: Loss terms penalizing topological deviation are sufficient to induce target manifold structure
   - Evidence: Persistent homology regularization has been used for manifold learning in TDA literature
   - Consequence if violated: Network dynamics remain unconstrained; no manifold structure emerges; hypothesis cannot be tested

3. **Lie derivative validity**
   - Statement: Equivariance error measured via Lie derivative is meaningful for representation quality
   - Evidence: Gruver et al. (2022) validated Lie derivative correlates with generalization across CNN, ViT, Mixer architectures
   - Consequence if violated: Measured equivariance does not predict downstream task performance; need alternative metric

4. **Topology-group bijection for Lie groups**
   - Statement: For compact Lie groups, manifold topology uniquely determines the equivariance type
   - Evidence: Mathematical fact from Lie theory (compact Lie groups characterized by topology)
   - Consequence if violated: Framework limited to specific group classes; extension to non-compact or discrete groups requires modification

### 1.5 Scope & Boundaries

**Applies to:**
- Continuous symmetries (Lie groups): SO(2) rotations, T² translations (grid cells), SO(3) 3D rotations, SE(3) rigid motions
- Tasks with clear geometric structure: rotation-invariant image classification, spatial navigation/path integration, molecular property prediction
- Networks with recurrent or attractor-like dynamics: RNNs, reservoir computing, biologically-inspired architectures

**Does NOT apply to:**
- Discrete symmetries (initially): permutation groups, crystallographic point groups, graph automorphisms
- Symbolic/abstract reasoning: language modeling, logical inference without spatial grounding
- Purely feedforward architectures: standard CNNs, MLPs without recurrent connections

**Known limitations:**
- Soft constraints yield approximate (not exact) equivariance; error bounds need empirical characterization
- Initial validation limited to low-dimensional groups (SO(2), T²); scaling to SO(3), SE(3) increases complexity
- Biological realism features (spiking neurons, synaptic delays, neuromodulation) traded for computational tractability

### 1.6 Testable Predictions

**Primary Prediction:**
**P1 (Equivariance Error):**
Attractor-Equivariant Layers (AELs) with ring manifold topology will achieve equivariance error < 0.1 (measured via Lie derivative) on rotation tasks, demonstrating that soft manifold constraints induce meaningful equivariance.

*Measurement*: Lie derivative equivariance error < 0.1 with p < 0.05 (n ≥ 20 runs)
*Basis*: Gruver et al. (2022) showed well-trained vision models achieve ~0.05-0.15 equivariance error; our target is at the lower end.
*Success Criteria*: Equivariance error < 0.1 AND statistically significant difference from random baseline

**Secondary Predictions:**
**P2 (Mechanism Validation):**
Disrupting manifold topology (removing topological loss term) will increase equivariance error by >50%, confirming the causal role of manifold constraints.

*Measurement*: Ablation study comparing full model vs. no-topology-loss variant
*Basis*: If mechanism is correct, removing key component degrades target property

**P3 (Comparative Performance):**
AELs will achieve task accuracy within 2% of e3nn baselines on RotMNIST and similar benchmarks, while providing interpretable attractor dynamics.

*Measurement*: Classification accuracy comparison, paired t-test
*Basis*: Soft equivariance should not dramatically harm task performance

**Falsification Criteria:**
The hypothesis will be **REJECTED** if any of the following occur:

1. **Primary Failure**: Equivariance error > 0.5 with topological constraints (no meaningful equivariance induced despite manifold constraints)

2. **Mechanism Failure**: Removing topological constraints does NOT significantly increase equivariance error (p > 0.1), indicating manifold structure is not the causal factor

3. **Baseline Failure**: Task accuracy more than 10% below e3nn baseline on standard benchmarks, indicating the approach is not competitive

### 1.7 SOTA Baseline (Optional - If SOTA Comparison Mode)

*Not applicable - This hypothesis targets theoretical framework establishment, not SOTA performance comparison*

### 1.8 Statistical Verification Design

**Sample Size Calculation:**
- Effect size target: Large (Cohen's d > 0.8) for equivariance improvement
- Required runs: n ≥ 20 per condition (power = 0.8, α = 0.05)
- Random seeds: Fixed set for reproducibility

**Test Specification:**
- Primary test: One-sample t-test (equivariance error < 0.1)
- Ablation test: Paired t-test (with vs. without topology loss)
- Comparison test: Independent t-test (AEL vs. e3nn)
- Significance level: α = 0.05 (one-tailed for primary)
- Report format: Mean ± Std Dev, 95% CI, Cohen's d, p-value

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Does soft topological constraint induce measurable manifold structure in neural network dynamics?"
- Verification: Measure topology of learned representations using persistent homology
- Success: Betti numbers match target manifold (β₁=1 for ring, β₁=2 for torus)

**SH2 (Mechanism):**
"Is manifold-group isomorphism the actual cause of equivariant representations?"
- Decomposes to N=3 sub-hypotheses in Phase 2B:
  - H-M1: Soft constraints → Manifold emergence
  - H-M2: Manifold topology → Group element encoding
  - H-M3: Group encoding → Equivariant output
- Verification: Ablation studies removing each causal link

**SH3 (Comparison):**
"Does AEL achieve comparable performance to e3nn while providing biological plausibility?"
- Verification: Benchmark on RotMNIST, ModelNet40
- Success: Accuracy within 2% of e3nn; interpretable dynamics demonstrated

### Readiness Checklist

- [x] Hypothesis in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID assigned (H-AEC-v1)
- [x] Confidence level specified (0.85)
- [x] Alternative hypothesis (H0) defined
- [x] All variables operationalized with measurement methods
- [x] Causal mechanism with evidence at each step (N=3)
- [x] Causal chain length determined (N=3)
- [x] Key tension identified with resolution
- [x] Assumptions list consequences if violated
- [x] 3 testable predictions with primary marked
- [x] Falsification criteria defined
- [x] Baselines identified (e3nn, GE-CNN, DeepMind RNN)
- [x] SH1, SH2, SH3 defined as Phase 2B starting points

### Open Questions

1. **Resource Requirements:** What compute is needed for training attractor layers with topological loss?
   - Estimate: Single GPU sufficient for SO(2); multi-GPU recommended for SO(3)
   - Topological loss (persistent homology) adds ~20% training overhead

2. **Data Availability:** Which benchmarks to prioritize?
   - Candidates: RotMNIST (rotation), ModelNet40 (3D), QM9 (molecular)
   - Recommendation: Start with RotMNIST for fastest iteration

3. **Implementation Priority:** SO(2) ring attractor vs. T² grid cells first?
   - Recommendation: SO(2) first as minimal proof-of-concept before T²
   - Reasoning: Simpler topology, faster training, clearer validation

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow (Focused)*
*2026-02-12*
