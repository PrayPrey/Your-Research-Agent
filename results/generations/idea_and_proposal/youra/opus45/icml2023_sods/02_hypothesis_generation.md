# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-12
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-GSGF-v1
**Confidence Level:** 0.85

**Main Hypothesis:**
Under black-box discrete optimization settings where explicit gradients are unavailable, if we apply Gumbel-Softmax relaxation to create a unified gradient interface, then GFlowNets, Discrete Langevin, and SVGD will achieve comparable or better optimization quality with a single implementation, because Gumbel-Softmax provides differentiable sampling that enables gradient-based updates across all three paradigms through continuous relaxation of discrete variables.

**Alternative Hypothesis (H0):**
The three discrete sampling paradigms (GFlowNet, Discrete Langevin, SVGD) have fundamentally incompatible gradient requirements that cannot be unified through a single relaxation mechanism, and any unified framework will perform significantly worse than paradigm-specific implementations.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| Gradient estimation method | Independent | Choice of GSGF unified interface vs individual method-specific gradients | Binary: GSGF / Baseline |
| Update rule | Independent | GFlowNet flow matching, Langevin drift-diffusion, or SVGD kernel repulsion | Categorical: {GFlowNet, Langevin, SVGD} |
| Temperature τ | Independent | Gumbel-Softmax temperature parameter | Continuous: 0.1 to 1.0 |
| Population size N | Independent | Number of parallel samples/particles | Integer: 16-256 |
| Optimization quality | Dependent | Gap to optimal solution (%) on TSP/MIS benchmarks | 0-100%, lower is better |
| Sample diversity | Dependent | Number of unique solutions in top-k samples | Integer: 1 to k |
| Convergence rate | Dependent | Iterations to reach 95% of final performance | Integer: 100-10000 |
| Problem instance | Controlled | Fixed benchmark instances | TSP-50, TSP-100, MIS-500, MIS-1000 |
| Random seed | Controlled | Fixed seeds for reproducibility | Integer: 0-4 |
| Computational budget | Controlled | Fixed function evaluations per run | 10000 evaluations |

### 1.3 Causal Mechanism

**Causal Chain (N=4 steps):**

```
Step 1: Discrete Variables → Gumbel-Softmax Relaxation → Continuous Simplex
    ↓
Step 2: Continuous Simplex → Gradient Computation → Update Direction
    ↓
Step 3: Update Direction → Method-Specific Rule → Parameter Update
    ↓
Step 4: Parameter Update + Temperature Annealing → Discrete Solution → Outcome
```

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step1 → Step2 | Jang et al. 2017 (5994 cites) | Gumbel-Softmax provides unbiased gradient estimates as τ→0 | Strong |
| Step2 → Step3 | Decoupled ST-GS (ICLR 2025) | Decoupled temperatures improve gradient fidelity | Strong |
| Step3 → Step4 | Tiapkin 2023, Sun 2022, Liu 2016 | All three paradigms accept gradient-based updates | Strong |
| Step4 → Outcome | Tang 2024 (Eyring-Kramers) | Discrete-time annealing has convergence guarantees | Medium |

**Key Tension:**
- **Tension:** Jang et al. 2017 shows Gumbel-Softmax works well for categorical distributions, but Sun et al. 2022 uses Wasserstein gradient flow for discrete Langevin which may have different mathematical foundations.
- **Resolution:** This verification plan tests whether the unified GSGF gradient interface produces equivalent optimization trajectories across all three paradigms, directly comparing against paradigm-specific gradients.

### 1.4 Key Assumptions

1. **Gradient Signal Sufficiency:** Gumbel-Softmax relaxation provides sufficient gradient signal for discrete optimization at practical temperatures (τ ≥ 0.1).
   - *Consequence if violated:* Optimization will converge to suboptimal solutions or fail to converge

2. **Temperature Annealing Generality:** Temperature schedule can be designed problem-agnostically using standard schedules.
   - *Consequence if violated:* Each problem class requires custom tuning, reducing practical value

3. **Paradigm Structural Similarity:** GFlowNet, Langevin, and SVGD share enough structural similarity to accept a common gradient interface.
   - *Consequence if violated:* Unification is fundamentally impossible; must use separate implementations

4. **Computational Overhead Acceptability:** GSGF overhead is negligible compared to objective function evaluation.
   - *Consequence if violated:* Unified approach is slower than individual methods

### 1.5 Scope & Boundaries

**Where Hypothesis Applies:**
- Combinatorial optimization: TSP, MIS, Maximum Cut, Graph Coloring
- Discrete sampling: Ising models, Potts models, graph generation
- Black-box settings: Objective function available only through evaluation
- Problem sizes: Up to ~10000 discrete variables

**Where Hypothesis Does NOT Apply:**
- Continuous optimization problems
- Mixed-integer problems with continuous variables requiring exact gradients
- Problems with hard constraints requiring feasibility guarantees
- Very large discrete spaces (>10^6 states)

### 1.6 Testable Predictions

**Primary Prediction:**

**P1 (Unification Validity):**
The GSGF unified framework will achieve optimization quality (optimality gap) within 5% of the best individual method on standard benchmarks.

*Measurement*: |GSGF_gap - min(GFlowNet_gap, Langevin_gap, SVGD_gap)| < 5%
*Statistical test*: Paired t-test, n ≥ 20 runs, p < 0.05
*Falsification*: Gap difference > 15% triggers rejection

**Secondary Predictions:**

**P2 (Adaptive Selection Advantage):**
GSGF with adaptive method selection will outperform any single fixed method across diverse problem types, achieving at least 3% better average performance.

**P3 (Implementation Efficiency):**
GSGF will require ≤1.5x the computational cost of individual methods while supporting all three paradigms.

**Falsification Criteria:**

The hypothesis will be **REJECTED** if any occur:
1. **Primary Failure:** GSGF optimality gap > 15% worse than best individual method (p < 0.05)
2. **Mechanism Failure:** Gradient signal produces divergent optimization trajectories
3. **Unification Failure:** Any paradigm fails to integrate with GSGF interface

### 1.7 SOTA Baseline (Optional)

*Not applicable - validates framework unification rather than SOTA comparison.*

### 1.8 Statistical Verification Design

**Sample Size:** n ≥ 20 per condition (Cohen's d = 0.5, power = 0.8)
**Test:** Paired t-test, α = 0.05, Bonferroni correction for 3 comparisons
**Report:** Mean ± Std Dev, 95% CI, Cohen's d, p-value

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Does Gumbel-Softmax relaxation produce valid gradient signals for discrete optimization?"
- Verification type: Empirical
- Critical: MUST PASS for Phase 2B to proceed

**SH2 (Mechanism):**
"Is the proposed 4-step causal mechanism the actual cause of successful unification?"
- Maps to: 4 sub-hypotheses (H-M1 to H-M4)
- Verification type: Ablation studies

**SH3 (Comparison):**
"Does GSGF achieve comparable or better performance than individual implementations?"
- Verification type: Comparative empirical

**Total sub-hypotheses:** 6 (SH1: 1, SH2: 4, SH3: 1)

### Readiness Checklist

- [x] Hypothesis in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID assigned: H-GSGF-v1
- [x] Confidence level: 0.85
- [x] Alternative hypothesis (H0) defined
- [x] All variables operationalized
- [x] Causal mechanism with evidence (N=4 steps)
- [x] Key tension identified with resolution
- [x] Key assumptions with consequences
- [x] 3 testable predictions (P1, P2, P3)
- [x] Falsification criteria defined
- [x] Baselines identified
- [x] SH1, SH2, SH3 defined

### Open Questions

1. **Resource Requirements:** 8GB VRAM estimated sufficient for N=256 on TSP-100
2. **Data Availability:** TSPLIB, DIMACS benchmarks confirmed available
3. **Technical Feasibility:** GFlowNet integration requires Phase 2B investigation
4. **Priority Order:** SH1 → SH2 → SH3 recommended

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow*
*2026-02-12*
