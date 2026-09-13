# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-13
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-G2PC-v1
**Confidence Level:** 0.82

**Main Hypothesis:**
Under the condition of having a differentiable simulator that provides gradients ∂x/∂θ, if we use these gradients as layer-wise error signals in a Predictive Coding Network (PCN) architecture for posterior estimation, then we will achieve superior sample efficiency (>50% fewer simulations to target accuracy) and posterior quality (lower C2ST) compared to standard NPE, because the gradient information constrains the posterior landscape through biologically-inspired local error minimization at each hierarchical layer.

**Alternative Hypothesis (H0):**
Incorporating differentiable simulator gradients into a PCN architecture provides no statistically significant improvement in sample efficiency or posterior quality compared to standard Neural Posterior Estimation (NPE), because gradient information does not effectively constrain the posterior learning process when combined with hierarchical local error minimization.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| Simulator gradient availability | Independent | Binary: differentiable simulator provides ∂x/∂θ vs black-box simulator | {0, 1} |
| PCN settling iterations (T_settle) | Independent | Integer count of ODE solver iterations during inference | 5-50 iterations |
| Hierarchical depth (L) | Independent | Number of PCN layers | 3-7 layers |
| Posterior accuracy (C2ST) | Dependent | Classifier Two-Sample Test score (lower is better) | 0.5-1.0 |
| Sample efficiency | Dependent | Number of simulations required to reach target C2ST < 0.55 | 100-10,000 simulations |
| Inference time | Dependent | Wall-clock time per posterior sample | 1-100 ms |
| Training data distribution | Controlled | Fixed SBI benchmark priors | Two Moons, SLCP, Lotka-Volterra |
| Network capacity | Controlled | Matched total parameters across all methods | ~500K parameters |

### 1.3 Causal Mechanism

**Causal Chain (N=4 steps):**

```
[Gradient Computation] → [Error Signal Generation] → [Local Parameter Updates] → [Hierarchical Refinement] → [Improved Posterior Estimate]
```

**Step 1: Gradient Computation → Error Signal Generation**
- Simulator gradients ∂x/∂θ are computed via autodiff
- Gradients are transformed into prediction error signals at each PCN layer
- Evidence: Zeghal 2022 demonstrated gradient computation is tractable for differentiable simulators

**Step 2: Error Signal Generation → Local Parameter Updates**
- Each PCN layer minimizes its local prediction error using gradient-guided updates
- Updates follow ODE-based settling dynamics (adaptive 2nd-order solvers)
- Evidence: JPC library (2024) shows ODE-based settling achieves fast convergence

**Step 3: Local Parameter Updates → Hierarchical Refinement**
- Layer-wise updates propagate through the hierarchy
- Precision-weighted optimization balances updates across depths
- Evidence: DCPC (Sennesh 2024) proves structured PCN updates are mathematically principled

**Step 4: Hierarchical Refinement → Improved Posterior Estimate**
- Refined latent representation produces more accurate posterior
- Fewer training simulations required because gradient information constrains solution space
- Evidence: Zeghal 2022 achieved 2x sample efficiency improvement with gradient-augmented NPE

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step1 → Step2 | Zeghal et al. 2022 | Gradients improve NPE sample efficiency by 2x | Strong |
| Step2 → Step3 | JPC library 2024 | 2nd-order ODE solvers achieve faster settling | Strong |
| Step3 → Step4 | van Zwol et al. 2024 | PCN mathematically equivalent to variational inference | Strong |
| Step4 → Outcome | Zeghal 2022 + PCN theory | Gradient constraints reduce simulation requirements | Medium |

**Key Tension:**
- **Tension:** Zeghal 2022 uses gradients only during training, not during inference, while PCN theory (van Zwol 2024) emphasizes iterative inference settling. It is unclear whether gradient injection during inference provides additional benefit beyond training-time gradient use.
- **Resolution:** This verification plan tests gradient injection at both training AND inference time to determine the incremental benefit of inference-time gradient guidance.

### 1.4 Key Assumptions

1. **Gradient Informativeness:** Differentiable simulator gradients ∂x/∂θ contain meaningful information about the posterior landscape structure.
   - Evidence: Zeghal 2022 empirically validated gradient utility
   - Consequence if violated: G2PC reduces to standard PCN with no sample efficiency gain

2. **PCN-Gradient Compatibility:** PCN-style local error minimization can effectively incorporate external gradient signals without destabilizing the settling dynamics.
   - Evidence: PCN theory allows external error injection (van Zwol 2024)
   - Consequence if violated: Training diverges or produces poor posteriors

3. **Settling Convergence:** Iterative settling converges within reasonable time budget (T_settle < 50 iterations).
   - Evidence: JPC library achieves convergence in 10-30 iterations typically
   - Consequence if violated: Inference becomes prohibitively slow, negating efficiency gains

4. **Overhead Amortization:** Gradient computation overhead is offset by sample efficiency gains in total wall-clock training time.
   - Evidence: Zeghal 2022 showed net benefit despite gradient overhead
   - Consequence if violated: G2PC is theoretically interesting but practically inferior

### 1.5 Scope & Boundaries

**Where Hypothesis Applies:**
- Any problem with a differentiable simulator (physics, engineering, scientific modeling)
- Simulators implemented in autodiff frameworks (JAX, PyTorch, TensorFlow)
- Low-to-medium dimensional parameter spaces (d < 50)
- Settings where simulation budget is the primary constraint

**Where Hypothesis Does NOT Apply:**
- Black-box simulators without gradient access
- Non-differentiable dynamics (hard contact, discrete events without relaxation)
- Very high-dimensional parameter spaces (d > 100) where PCN scaling is untested
- Settings where inference latency is more critical than sample efficiency

**Known Limitations:**
- Requires simulator to be differentiable (not always available)
- PCN settling adds inference latency compared to feedforward NPE
- Deep PCN scaling (L > 7) remains an active research area
- Performance on complex, multi-modal posteriors is unknown

### 1.6 Testable Predictions

**Primary Prediction:**

**P1 (Sample Efficiency vs NPE Baseline):**
G2PC will achieve target posterior accuracy (C2ST < 0.55) with >50% fewer simulations than standard NPE.

*Measurement:*
- Metric: Number of simulations to reach C2ST < 0.55
- Statistical test: Paired t-test across 5 random seeds, α = 0.05
- Required sample size: n ≥ 25 runs per method

*Basis:*
Zeghal 2022 demonstrated 2x (100%) improvement with gradient-augmented NPE. G2PC's hierarchical structure should achieve at least 50% of this improvement.

*Success Criteria for Phase 2B:*
- Primary: Simulation count < 50% of NPE baseline (p < 0.05)
- Falsification: Simulation count ≥ 90% of NPE baseline triggers rejection

**Secondary Predictions:**

**P2 (Mechanism Validation - Settling Dynamics):**
PCN settling iterations T_settle > 10 will produce significantly better C2ST than T_settle = 1 (feedforward), demonstrating that iterative refinement contributes to posterior quality.

*Measurement:* Compare C2ST at T_settle ∈ {1, 5, 10, 20, 50}
*Expected:* C2ST monotonically improves up to T_settle ≈ 20, then plateaus

**P3 (Depth Scaling):**
Hierarchical depth L ∈ {3, 5} will achieve stable training with balanced layer updates, while L > 7 may show gradient instability without precision weighting.

*Measurement:* Track layer-wise gradient norms and final C2ST across depths
*Expected:* Optimal depth L ∈ [3, 5] for standard benchmarks

**Falsification Criteria:**

The hypothesis will be **REJECTED** if any of the following occur:

1. **Primary Failure:** G2PC requires ≥90% of NPE's simulation budget to achieve comparable C2ST
2. **Mechanism Failure:** T_settle > 10 provides no improvement over T_settle = 1
3. **Stability Failure:** Training diverges for L ≥ 3 without additional stabilization techniques
4. **Efficiency Failure:** Total training wall-clock time exceeds 2x NPE despite sample efficiency gains

### 1.7 SOTA Baseline (Optional - If SOTA Comparison Mode)

*Not applicable - targeting sample efficiency improvement over NPE baseline.*

### 1.8 Statistical Verification Design

**Sample Size Calculation:**
- Effect size target: 50% reduction in simulation count (Cohen's d ≈ 0.8)
- Required runs per condition: n ≥ 25 (power = 0.8, α = 0.05)
- Total experiments: 25 runs × 4 methods × 3 benchmarks = 300 runs

**Test Specification:**
- Primary test: Paired t-test (same random seeds across methods)
- Significance level: α = 0.05 (one-tailed)
- Multiple comparison correction: Bonferroni (α_adj = 0.017)

**Report Format:**
- Mean simulation count ± Std Dev
- 95% Confidence Interval
- Cohen's d effect size
- p-value

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Does gradient-guided posterior refinement via PCN achieve target accuracy (C2ST < 0.55) on standard SBI benchmarks?"
- Maps to: Primary prediction P1
- Verification type: Empirical
- Critical: MUST PASS for Phase 2B to proceed

**SH2 (Mechanism):**
"Is the proposed 4-step causal mechanism the actual cause of improved sample efficiency?"
- Maps to: Causal mechanism (N=4 steps)
- Phase 2B will decompose into 4 sub-hypotheses: H-M1, H-M2, H-M3, H-M4
- Verification type: Ablation studies + mechanism probes

**SH3 (Comparison):**
"Does G2PC outperform gradient-augmented NPE and standalone PCN baselines?"
- Maps to: Secondary predictions P2, P3
- Verification type: Comparative empirical

**Total Sub-Hypotheses in Phase 2B:** 2 + 4 = 6

### Readiness Checklist

- [x] Hypothesis in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID assigned: H-G2PC-v1
- [x] Confidence level: 0.82
- [x] Alternative hypothesis (H0) defined
- [x] All 8 variables operationalized
- [x] Causal mechanism with N=4 steps and evidence table
- [x] Key tension identified with resolution
- [x] 4 assumptions with consequences
- [x] 3 testable predictions (primary marked)
- [x] 4 falsification criteria defined
- [x] 3 baselines identified (NPE, Gradient-NPE, PCN)
- [x] SH1, SH2, SH3 ready for Phase 2B

### Open Questions

1. **Resource Requirements:** ~100 GPU-hours on A100 for 300 runs
2. **Data Availability:** Two Moons, SLCP, Lotka-Volterra in sbi toolkit (confirmed)
3. **Priority:** Recommend SH1 first for go/no-go decision

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow*
*2026-02-13*
