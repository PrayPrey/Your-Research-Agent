# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-12
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-GI-SS-PAC-RL-v1
**Confidence Level:** 0.82

**Main Hypothesis:**
Under continuous control RL with neural network policies (millions of parameters), if we project policy posteriors onto Fisher information-guided low-dimensional subspaces and apply bio-inspired gradual magnitude pruning, then we achieve non-vacuous PAC-Bayesian bounds with O(d) computational complexity instead of O(D), because intrinsic low-dimensionality of deep RL policies enables compression without information loss and structured sparsity further reduces effective parameter count.

**Alternative Hypothesis (H0):**
There is no relationship between sparse subspace posterior representation and PAC-Bayesian bound tractability; either (a) projecting to low-dimensional subspaces introduces sufficient approximation error to invalidate bound guarantees, or (b) the computational savings do not materialize due to hidden costs in Fisher information computation and pruning overhead.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| Subspace dimensionality (d) | Independent | Number of top Fisher information eigenvectors used for projection | d ∈ {100, 500, 1000, 2000}, where d << D |
| Sparsity ratio (s) | Independent | Fraction of parameters pruned via gradual magnitude pruning | s ∈ {0.7, 0.8, 0.9, 0.95} |
| Network architecture (D) | Controlled | Total parameter count of policy network | D ~ 10^5 to 10^6 (MLP: ~100K, CNN: ~1M) |
| RL algorithm | Controlled | Base algorithm for policy optimization | SAC (Soft Actor-Critic) |
| Environment | Controlled | MuJoCo benchmark task | HalfCheetah, Ant, Humanoid |
| Training budget | Controlled | Total environment steps | 1M steps per task |
| PAC-Bayes bound value | Dependent | Generalization bound via subspace KL + mixing correction | Target: < 1.0 (non-vacuous) |
| Computational cost | Dependent | Wall-clock time for bound computation | Target: O(d) scaling verified empirically |
| Policy performance | Dependent | Average return on benchmark tasks | Within 5% of dense SAC baseline |

### 1.3 Causal Mechanism

**Causal Chain (N=4 steps):**

```
Step 1: Fisher Information Eigenvector Projection
    ↓ (identifies policy-relevant subspace)
Step 2: Low-d Subspace Posterior Representation
    ↓ (reduces KL computation from O(D) to O(d))
Step 3: Gradual Magnitude Pruning with Rollback
    ↓ (further compresses while preserving performance)
Step 4: Markov Mixing Time Correction
    ↓ (validates bounds under sequential RL data)
Outcome: Non-vacuous, computationally tractable PAC-Bayes bounds
```

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step 1 → Step 2 | Zakerinia et al. 2025 | Multi-task networks have low intrinsic dimensionality; learning occurs in small subspace | Strong |
| Step 2 → Step 3 | Lotfi et al. 2022 | Subspace quantization yields state-of-the-art non-vacuous bounds for deep networks (76 citations) | Strong |
| Step 3 → Step 4 | FastHebb 2024 | Bio-inspired training scales to large networks; synaptic pruning analogy validated | Medium |
| Step 4 → Outcome | Zitouni et al. 2025 | Markov mixing time correction provides valid PAC-Bayes bounds for RL | Strong |

**Key Tension:**
- **Tension:** Lotfi et al. 2022 demonstrates non-vacuous bounds for supervised learning, but Zitouni et al. 2025 notes that "sequential nature of data breaks independence assumptions" in RL. The combination of subspace compression (supervised) with mixing time correction (RL) is novel and untested.
- **Resolution:** This verification plan tests whether the subspace compression approach maintains validity when combined with mixing time correction by empirically comparing bound tightness against full-dimensional bounds on matched RL tasks.

### 1.4 Key Assumptions

| # | Assumption | Supporting Evidence | Consequence if Violated |
|---|------------|---------------------|------------------------|
| A1 | Deep RL policies have low intrinsic dimensionality | Zakerinia 2025: "high-accuracy solutions found with much smaller intrinsic dimensionality" | Subspace projection loses critical policy information; bounds become vacuous |
| A2 | Fisher information eigenvectors capture policy-relevant directions | General result from natural gradient literature; empirically validated in optimization | Subspace misses generalization-critical dimensions; bound-performance gap increases |
| A3 | Markov mixing time is finite for continuous control tasks | Standard assumption in RL theory; MuJoCo environments are ergodic | Mixing correction term becomes infinite; bound computation fails |
| A4 | Gradual pruning preserves policy gradient signal | FastHebb 2024 demonstrates bio-inspired training maintains performance | Aggressive pruning destroys policy; performance degradation > 5% threshold |

### 1.5 Scope & Boundaries

**Applies to:**
- Continuous control RL with neural network policies (MLP, CNN)
- Off-policy algorithms with stochastic policies (SAC, TD3 variants)
- Environments with finite mixing time (ergodic MDPs)
- Parameter counts D ~ 10^5 to 10^6

**Does NOT Apply to:**
- Discrete action spaces (without modification to posterior representation)
- Non-neural policies (linear, tabular)
- On-policy algorithms (PPO, A2C) - different trajectory distribution
- Non-ergodic environments (episodic-only, absorbing states)

**Known Limitations:**
- Fisher information computation requires O(D) one-time cost at initialization
- Gradual pruning extends training time by ~20%
- Novel synthesis means limited prior implementations to reference
- Bound tightness may degrade for very large networks (D > 10^7)

### 1.6 Testable Predictions

**Primary Prediction:**

**P1 (Non-Vacuous Bounds with O(d) Complexity)**:
If subspace dimensionality d is set to capture ≥95% of Fisher information variance, then PAC-Bayes bounds will be non-vacuous (bound value < 1.0) with computational cost scaling as O(d).

*Measurement*:
- Bound value < 1.0 with p < 0.05 across n ≥ 20 independent runs
- Timing analysis confirms O(d) scaling via linear regression on d vs. compute time

*Success Criteria for Phase 2B*:
- Primary: Bound < 1.0 for d ≤ 1000 on HalfCheetah
- Falsification: Bound ≥ 1.0 for all d ≤ 2000 triggers hypothesis rejection

**Secondary Predictions:**

**P2 (Sparsity-Performance Trade-off)**:
If sparsity ratio s > 0.9 is achieved via gradual magnitude pruning with rollback, then policy performance will remain within 5% of dense SAC baseline.

**P3 (Bound Tightness vs. Full-Dimensional)**:
If subspace compression maintains bound validity, then bound tightness will be comparable to or better than full-dimensional PAC-Bayes bounds.

**Falsification Criteria:**

The hypothesis will be **REJECTED** if any of the following occur:

1. **Primary Failure**: PAC-Bayes bound ≥ 1.0 (vacuous) for all tested subspace dimensions d ≤ 2000
2. **Mechanism Failure**: Sparsity ratio s > 0.9 causes policy performance degradation > 10%
3. **Computational Failure**: Bound computation time does not scale as O(d)
4. **Comparative Failure**: Subspace bounds are consistently worse than full-dimensional bounds by > 20%

### 1.7 SOTA Baseline

| Method | Paper | Expected Baseline |
|--------|-------|-------------------|
| PB-SAC | Zitouni et al. 2025 | Bound < 1.0, competitive return |
| PBAC | Tasdighi et al. 2024 | Ensemble approximation baseline |
| Standard SAC | Haarnoja et al. 2018 | Performance ceiling |

### 1.8 Statistical Verification Design

**Sample Size Calculation:**
- Effect size (Cohen's d): 0.8 (large effect expected)
- Required runs: n ≥ 20 per configuration
- Statistical power: 0.8

**Test Specification:**
- Method: One-sample t-test (H0: bound ≥ 1.0) and paired t-test (vs baseline)
- Significance level: α = 0.05 (one-tailed for primary prediction)
- Report format: Mean bound value, 95% CI, Cohen's d, p-value

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Does sparse subspace posterior representation enable non-vacuous PAC-Bayes bounds for deep RL policies?"
- Maps to: Primary prediction P1
- Verification type: Empirical
- Critical: MUST PASS for Phase 2B to proceed

**SH2 (Mechanism):**
"Is the proposed 4-step causal mechanism the actual cause of tractable non-vacuous bounds?"

Will decompose into 4 sub-hypotheses in Phase 2B:
- H-M1: Fisher information eigenvectors capture policy-relevant directions
- H-M2: Subspace representation reduces KL computation to O(d)
- H-M3: Gradual pruning preserves performance at s > 0.9
- H-M4: Mixing time correction maintains bound validity for RL

**SH3 (Comparison):**
"Does GI-SS-PAC-RL outperform existing PAC-Bayes RL methods (PBAC, PB-SAC) in bound tightness and/or computational efficiency?"
- Maps to: Secondary predictions P2, P3
- Verification type: Comparative empirical
- Critical: Determines practical value

**Total Sub-Hypotheses for Phase 2B:** 2 + 4 = 6 hypotheses

### Readiness Checklist

- [x] Hypothesis is in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID assigned: H-GI-SS-PAC-RL-v1
- [x] Confidence level specified: 0.82
- [x] Alternative hypothesis (H0) defined
- [x] All variables have operationalization from evidence
- [x] Causal mechanism has evidence at each step (N=4 steps)
- [x] Causal chain length determined: N=4
- [x] Key tension identified and resolution proposed
- [x] Key assumptions list consequences if violated
- [x] At least 2 testable predictions exist with primary marked
- [x] Falsification criteria defined (4 conditions)
- [x] Baselines identified: PBAC, PB-SAC, Standard SAC
- [x] SH1, SH2, SH3 are clear starting points

### Open Questions for Phase 2B

1. **Resource Requirements:** What is the one-time cost of Fisher information eigendecomposition for D ~ 10^6 parameters? Is diagonal or K-FAC approximation sufficient?

2. **Data Availability:** Are MuJoCo benchmark results for PBAC and PB-SAC publicly available for direct comparison, or do we need to re-implement baselines?

3. **Priority Order:** Should we verify SH1 (existence) first before mechanism sub-hypotheses, or can SH2 components be tested in parallel?

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow*
*2026-02-12*
