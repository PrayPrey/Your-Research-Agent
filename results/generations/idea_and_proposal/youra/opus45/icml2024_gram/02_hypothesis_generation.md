# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-12
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md (Round 1 - FEASIBLE)
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H1-UCAN
**Confidence Level:** 0.83

**Main Hypothesis:**
Joint relaxation and progressive annealing of geometric equivariance constraints and physics law constraints through a unified scheduling mechanism improves neural network training convergence while guaranteeing constraint satisfaction at convergence, compared to approaches that enforce either constraint type in isolation or through fixed hard constraints.

**Alternative Hypothesis (H0):**
Treating geometric equivariance and physics constraints separately (or with fixed hard enforcement) achieves equivalent or better training convergence and final model quality compared to unified soft constraint annealing, and the joint optimization of both constraint types provides no additional benefit over optimizing them independently.

### 1.2 Variables

| Variable Type | Name | Description | Measurement |
|--------------|------|-------------|-------------|
| **Independent** | α(t) | Unified annealing parameter | Scalar ∈ [0, 1], t ∈ [0, T] |
| **Independent** | λ_max | Maximum equivariance relaxation magnitude | Scalar > 0 |
| **Independent** | β_max | Maximum physics constraint weight | Scalar > 0 |
| **Dependent** | E_eq | Equivariance violation error | ||f(gx) - ρ(g)f(x)||² averaged over group samples |
| **Dependent** | E_phys | Physics constraint violation | PDE residual L² norm |
| **Dependent** | L_task | Task performance loss | Energy/Force MAE (molecular), velocity MSE (fluid) |
| **Dependent** | C_conv | Convergence speed | Epochs to reach target loss threshold |
| **Control** | Architecture | Base neural network | EGNN or e3nn (held constant per experiment) |
| **Control** | Dataset | Training/test data | MD17, QM9, or Navier-Stokes (held constant per experiment) |
| **Control** | Schedule type | Annealing function form | Linear α(t) = t/T (primary), cosine as ablation |

### 1.3 Causal Mechanism

```
[Early Training: α(t) ≈ 0]
         ↓
Relaxed Equivariance (λ_eq = λ_max × (1 - α))
    → Enlarged solution space
    → Escape local minima
         ↓
Low Physics Weight (β = β_max × α)
    → Reduced conflicting gradients
    → Focus on representation learning
         ↓
[Progressive Training: α(t) → 1]
         ↓
Annealing Schedule Advances
    → Gradually tighten equivariance
    → Gradually increase physics weight
         ↓
Network adapts incrementally
    → Smooth optimization trajectory
    → Avoids hard constraint shock
         ↓
[Convergence: α(T) = 1]
         ↓
Exact Equivariance (λ_eq = 0)
    → f(gx) = ρ(g)f(x) ∀g ∈ G
         ↓
Maximum Physics Enforcement (β = β_max)
    → PDE residual minimized
         ↓
[Final Model]
    → Satisfies BOTH constraints
    → Better generalization than hard-constraint training
```

**Evidence for Causal Links:**
1. **Relaxation → Better optimization:** Pertigkiozoglou et al. (2024) demonstrated 15-20% improvement in molecular property prediction with relaxed equivariance
2. **Adaptive weighting → PINN stability:** DB-PINN (2025) showed adaptive physics weighting resolves spectral bias and gradient imbalance
3. **Annealing → Constraint satisfaction:** Simulated annealing (Kirkpatrick 1983) and curriculum learning (Bengio 2009) establish theoretical foundations for progressive constraint tightening
4. **Joint optimization → Synergy:** Pseudo-symplectic neural networks (Cheng 2025) validate approximate-to-exact structure preservation paradigm

**Key Tension:**
The hypothesis assumes equivariance and physics constraints are **compatible** - that satisfying one does not inherently conflict with satisfying the other. If constraints are fundamentally incompatible for a given problem, the unified annealing may oscillate or fail to converge. This is the primary falsification target.

### 1.4 Key Assumptions

| # | Assumption | Justification | Risk Level |
|---|------------|---------------|------------|
| A1 | Equivariance and physics constraints are compatible | For physical systems, symmetries and physical laws should be mutually consistent by construction | LOW |
| A2 | Progressive annealing improves optimization landscape accessibility | Established in curriculum learning and simulated annealing literature | LOW |
| A3 | Linear schedule is sufficient for diverse problems | Simple baseline; can be relaxed to learnable schedules if needed | MEDIUM |
| A4 | Relaxed equivariance preserves sufficient structure during early training | Pertigkiozoglou 2024 demonstrates bounded deviation terms work in practice | LOW |
| A5 | Convergence to exact constraints is achievable | Requires appropriate λ_max and schedule length; may need tuning | MEDIUM |

### 1.5 Scope & Boundaries

**In-Scope:**
- E(n)-equivariant architectures (EGNN, e3nn variants)
- Continuous symmetry groups (translation, rotation, reflection)
- Differentiable physics constraints (PDE residuals)
- Supervised and self-supervised molecular/physical learning tasks

**Out-of-Scope:**
- Discrete symmetries (permutation groups handled separately in GNNs)
- Non-differentiable physics (contact mechanics, discrete event systems)
- Systems without known physical laws (pure data-driven settings)
- Very high-dimensional symmetry groups (gauge symmetries beyond SO(3))

**Boundary Conditions:**
- Minimum training duration: T must be sufficient for gradual annealing (≥100 epochs recommended)
- Maximum relaxation: λ_max should preserve approximate equivariance (≤0.5 deviation magnitude)
- Problem scale: Validated on small-to-medium datasets; scalability to large-scale TBD

### 1.6 Testable Predictions

**Primary Prediction:**
If unified constraint annealing is applied to physics-informed equivariant networks, then the combined model will achieve:
1. **Faster convergence** (≥10% fewer epochs to target loss) compared to hard-constraint baselines
2. **Lower final task error** (≥5% improvement in energy/force MAE) compared to best single-constraint approach
3. **Dual constraint satisfaction** (E_eq < ε_eq AND E_phys < ε_phys at convergence)

**Secondary Predictions:**
1. **P2 (Ablation):** Unified schedule performs comparably to separately-tuned dual schedules with 50% fewer hyperparameters
2. **P3 (Transfer):** Annealing framework transfers across molecular (MD17, QM9) and fluid (Navier-Stokes) domains without architecture changes

**Falsification Criteria:**
| Criterion | Threshold | Interpretation if Failed |
|-----------|-----------|-------------------------|
| Convergence speed ≤ baseline | No improvement over hard constraints | Relaxation benefit is illusory |
| Final error ≥ baseline | Task performance degraded | Constraints are incompatible or annealing insufficient |
| E_eq(T) > ε_eq | Equivariance not restored | Schedule too fast or λ_max too large |
| E_phys(T) > ε_phys | Physics violated | β_max insufficient or schedule misaligned |
| Unified ≪ separate schedules | >10% worse with unified | Constraints require independent control |

### 1.7 SOTA Baseline (Optional - If SOTA Comparison Mode)

| Method | Year | Task | Key Result | Our Target |
|--------|------|------|------------|------------|
| NequIP | 2021 | MD17 | Energy MAE: 2.8 meV | ≤2.5 meV |
| Equiformer | 2022 | QM9 | HOMO MAE: 22 meV | ≤21 meV |
| DB-PINN | 2025 | Navier-Stokes | Velocity MSE: 1e-4 | ≤1e-4 |
| Relaxed E(n)-GNN | 2024 | MD17 | 15% improvement over EGNN | ≥15% |

**SOTA Comparison Strategy:** Beat best single-constraint method while satisfying both constraints (novel capability), OR achieve comparable performance with demonstrated dual-constraint satisfaction.

### 1.8 Statistical Verification Design

**Experimental Design:**
- **Type:** Randomized controlled experiment with ablations
- **Replicates:** 5 random seeds per condition
- **Conditions:** (1) Hard constraints, (2) Relaxed equivariance only, (3) Adaptive physics only, (4) UCANs unified

**Statistical Tests:**
| Comparison | Test | Significance Level | Power Target |
|------------|------|-------------------|--------------|
| UCANs vs Hard | Paired t-test | α = 0.05 | 0.80 |
| UCANs vs Single-constraint | Wilcoxon signed-rank | α = 0.05 | 0.80 |
| Schedule ablation | Two-way ANOVA | α = 0.05 | 0.80 |

**Sample Size Justification:**
- 5 seeds × 4 conditions = 20 runs per dataset
- 3 datasets = 60 total runs
- Based on Pertigkiozoglou 2024 effect sizes (d ≈ 0.8), n=5 provides 80% power

**Reporting:**
- Mean ± std across seeds
- 95% confidence intervals
- Effect sizes (Cohen's d)
- P-values with Bonferroni correction for multiple comparisons

---

## 2. Contribution Summary

| Type | Contribution | Novelty Level | Gap Addressed |
|------|--------------|---------------|---------------|
| **Theoretical** | Unified constraint optimization view treating geometric equivariance and physics laws as symmetric soft constraints amenable to joint annealing | HIGH | Gap 1 (PINN + GDL isolation) |
| **Methodological** | Joint annealing schedule with single α(t) parameter controlling both equivariance relaxation magnitude and physics constraint weight | MEDIUM-HIGH | Training instability in physics-informed equivariant models |
| **Empirical** | Demonstration of dual-constraint satisfaction with improved convergence across molecular and fluid dynamics domains | MEDIUM | Lack of unified benchmarks |

**Novelty Statement (Refined):**
"UCANs introduce the first unified optimization perspective for physics-informed equivariant neural networks, treating geometric symmetries and physical laws as symmetric soft constraints. Unlike prior work that relaxes equivariance only (Pertigkiozoglou 2024) or adapts physics loss weighting only (DB-PINN 2025), UCANs provide a principled joint annealing framework that bridges the PINN (14K+ citations) and Geometric Deep Learning (3.6K+ citations) research communities."

---

## 3. Key Related Work

| Paper | Year | Relation | Key Difference from UCANs |
|-------|------|----------|--------------------------|
| **E(n)-EGNN** (Satorras et al.) | 2021 | Foundation | Hard equivariance only, no physics |
| **NequIP** (Batzner et al.) | 2021 | Foundation | Hard equivariance, energy conservation via architecture |
| **PINNs** (Raissi et al.) | 2019 | Foundation | Physics only, no geometric structure |
| **DB-PINN** (Zhou et al.) | 2025 | Partial overlap | Adaptive physics weighting but no equivariance |
| **Relaxed Equivariance** (Pertigkiozoglou et al.) | 2024 | Partial overlap | Equivariance relaxation but no physics |
| **Bronstein 5G Framework** | 2021 | Theoretical | Unified theory but no unified optimization |
| **Symplectic Neural Flows** (Canizares et al.) | 2024 | Inspiration | Approximate-to-exact structure preservation |
| **Lagrangian Relaxation** (Boyd & Vandenberghe) | 2004 | Cross-domain | Source of unified constraint optimization view |

**Gap in Related Work:** No existing method jointly optimizes equivariance and physics constraints through unified annealing. The closest works address only one constraint type.

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
Does unified constraint annealing improve training convergence compared to hard-constraint baselines?
- Metric: Epochs to target loss threshold
- Dataset: MD17 (molecular)
- Baseline: EGNN with hard equivariance

**SH2 (Mechanism):**
Does the unified schedule α(t) simultaneously reduce equivariance violation E_eq and physics violation E_phys as training progresses?
- Metric: E_eq(t) and E_phys(t) trajectories
- Analysis: Correlation between α(t) and constraint satisfaction
- Ablation: Unified vs separate schedules

**SH3 (Comparison):**
Does UCANs achieve superior or comparable task performance to single-constraint SOTA while satisfying both constraints?
- Metric: Energy/Force MAE
- Baselines: NequIP (equivariant), DB-PINN (physics-informed)
- Novel capability: Dual constraint satisfaction (neither baseline achieves)

### Readiness Checklist

| Item | Status | Notes |
|------|--------|-------|
| Hypothesis clearly stated | ✅ | Main hypothesis + H0 defined |
| Variables identified | ✅ | IV, DV, control all specified |
| Causal mechanism described | ✅ | Flow diagram + evidence |
| Assumptions explicit | ✅ | 5 assumptions with risk levels |
| Scope bounded | ✅ | In/out of scope clear |
| Predictions testable | ✅ | Quantitative thresholds provided |
| Falsification criteria defined | ✅ | 5 falsification conditions |
| Statistical design outlined | ✅ | Tests, sample sizes, power |
| Contributions differentiated | ✅ | Theoretical/methodological/empirical |
| Related work mapped | ✅ | 8 key papers with relations |
| Sub-hypotheses previewed | ✅ | SH1/SH2/SH3 structure |

### Open Questions

1. **Schedule optimization:** Should α(t) be learned during training or fixed?
   - Recommendation: Start with fixed linear, explore learned as future work

2. **λ_max selection:** How to choose maximum relaxation magnitude?
   - Recommendation: Grid search {0.1, 0.3, 0.5} in SH1 experiments

3. **Domain generalization:** Does the framework extend to non-Euclidean manifolds?
   - Recommendation: Out of scope for initial verification; future extension

---

*Generated using YouRA Research Phase 2A Extended Workflow (Focused)*
*2026-02-12*
