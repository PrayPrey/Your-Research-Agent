# Phase 2A Extended: Hypothesis Summary
**Ready for Phase 2B Verification Planning**

---

## Core Hypothesis (H-DiffRelax-001)

**Main Statement:**
Dynamic, hardware-aware selection of differentiable relaxation methods during training, implemented through a Mixture-of-Relaxations (MoR) framework with learned switching policies, achieves superior trade-offs between computational cost and gradient quality compared to static relaxation selection, particularly at scale (n > 1000 elements).

**Confidence Level:** 0.85 (High Feasibility)

---

## Key Components

### 1. Variables
| Type | Variable | Measurement |
|------|----------|-------------|
| **Independent** | Relaxation Strategy | {static_STE, static_gumbel, static_permutahedron, adaptive_MoR} |
| **Independent** | Problem Scale (n) | [100, 1000, 10000, 100000] |
| **Independent** | Hardware Platform | {V100_GPU, A100_GPU, TPU_v4} |
| **Dependent** | Training Time | Wall-clock seconds to convergence |
| **Dependent** | Gradient Quality | SNR = μ(grad_norm) / σ(grad_norm) |
| **Dependent** | Final Model Performance | Task-specific accuracy/loss |

### 2. Causal Mechanism
```
Problem scale + hardware + training phase
  → Switching policy observes runtime profiling
  → MoR layer dynamically weights relaxation methods
  → Training receives appropriate quality-cost gradient signal
  → Improved convergence speed and/or final performance
```

**Key Tension:** Adaptive switching overhead vs efficiency gains

### 3. Testable Predictions

**P1 (Primary):** Adaptive MoR reduces training time by 20-40% vs "always high-quality" baseline, while maintaining within 2% final performance, on tasks with n > 1000 across 3+ domains.

**P2 (Hardware):** Adaptive MoR automatically selects GPU-friendly relaxations on GPU and TPU-friendly relaxations on TPU, resulting in 10-20% better hardware utilization.

**P3 (Phase-Aware):** Adaptive MoR uses cheaper approximations in early training (first 25% epochs) and transitions to high-quality relaxations in late training (last 25% epochs).

**Falsification Criteria:**
- REJECT if: <10% speedup AND >5% performance degradation, OR >10% overhead, OR training instability in >30% runs, OR static tuned baseline wins by >15%
- SUPPORT if: P1 AND (P2 OR P3) hold across majority of tasks

---

## Contributions

### Theoretical
- **T1:** Formalization of relaxation selection as contextual bandit problem with regret bounds
- **T2:** Convergence analysis of Mixture-of-Relaxations training
- **T3:** Complexity-aware method selection theory (Pareto frontier characterization)

### Methodological
- **M1:** Mixture-of-Relaxations (MoR) Layer Architecture - differentiable module computing weighted combination of relaxations
- **M2:** Scale-Conditional Profiling Infrastructure - lazy profiling activated only at n > 1000 or compute time > 100ms
- **M3:** Meta-Learned Switching Policy with Transfer Learning - pre-trained on diverse tasks, fine-tuned per-task
- **M4:** Hardware-Aware Cost Models - analytical + empirical models for GPU vs TPU selection

### Practical Applications
- **App1:** Large-scale Neural Architecture Search (30% faster NAS runs)
- **App2:** Differentiable Physics at Multiple Scales (multi-scale physics-based learning)
- **App3:** Learning-to-Rank at Web Scale (40% reduction in training cost)

---

## Phase 2B Decomposition Preview

**SH1 (Existence):** Adaptive selection outperforms static baselines
- Verification: Direct comparison experiments across 3 domains, 5 seeds
- Success: Paired t-test shows significant speedup (p < 0.05) with maintained performance

**SH2 (Mechanism):** MoR components (profiling, MoR layer, meta-learning) each contribute positively
- Verification: Ablation study removing each component
- Success: Full system outperforms all ablated variants by >10%

**SH3 (Comparison):** Hardware and phase adaptation occur as predicted
- Verification: Analyze switching policy decisions across contexts
- Success: ANOVA shows significant effects of hardware and phase on method selection

---

## Key Related Work

**Direct Predecessors:**
1. Blondel et al. (2020) - Fast Differentiable Sorting (permutahedron projection, O(n log n))
2. Petersen et al. (2021) - Differentiable Sorting Networks (O(n log² n), GPU-friendly)
3. Huh et al. (2023) - STE improvements (stability analysis)
4. Wan et al. (2020) - FBNetV2 (learns architectural choices, conceptual analogy)

**Gap Addressed:**
- **Gap 2 from Phase 1:** Scalability and Computational Trade-offs at Large Scale
- No prior work treats relaxation selection as learned, dynamic optimization problem
- No prior work proposes smooth interpolation between relaxation methods

---

## Experimental Design

**Design:** Factorial with repeated measures
- 4 strategies × 4 scales × 2 hardware × 3 tasks = 96 conditions × 5 seeds = 480 runs
- Estimated compute: ~2000 GPU-hours

**Statistical Tests:**
- Primary (P1): Paired t-test, α=0.05
- Secondary (P2): Mann-Whitney U test
- Secondary (P3): Repeated measures ANOVA with Bonferroni correction

**Baselines:**
1. Always STE (lower bound)
2. Always Permutahedron (upper bound)
3. Tuned static (hyperparameter search)
4. Adaptive MoR (proposed)

---

## Open Questions for Phase 2B/2C

1. Optimal profiling frequency (K=10 vs K=100 steps)?
2. Minimum task diversity for meta-learning generalization?
3. Hard vs soft interpolation in MoR?
4. Interaction with mixed-precision training?
5. Failure recovery mechanisms for catastrophic relaxation failures?
6. Meta-learning hyperparameter sensitivity?

---

## Readiness Status

**Ready for Phase 2B:** ✅
- [x] Falsifiable predictions with operationalized metrics
- [x] Variables and measurements defined
- [x] Causal mechanism articulated with evidence
- [x] Experimental design specified
- [x] Sub-hypotheses (SH1-3) identified
- [x] Computational feasibility confirmed (~2000 GPU-hours, 2-3 months engineering)

**Next Step:** Phase 2B - Verification Planning
- Decompose into detailed sub-hypotheses
- Establish verification roadmap with prioritized experiments
- Define success criteria and gates

---

*Source: Round 1 Discussion (02a_round_1_discussion.md)*
*Generated: 2026-02-06*
*Full Document: 02a_extended_hypothesis_full.md*
