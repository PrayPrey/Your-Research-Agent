# Phase 2A Extended: Hypothesis Clarification - Summary

**Date:** 2026-02-06
**Author:** Pray
**Hypothesis ID:** H-RBOPT-Gap2-R1
**Status:** ✅ READY FOR PHASE 2B

---

## Core Hypothesis

A robust Bayesian optimization framework with learnable confidence parameters for domain knowledge sources can maintain provable **O(√T log T) regret bounds** under ε-bounded prior mismatch by treating domain priors (physics models, LLM suggestions, expert constraints) as uncertain information sources with time-varying weights, detecting mismatch via online posterior predictive checks, and dynamically down-weighting mismatched priors using parameter-free coin betting algorithms.

**Target Gap:** Gap 2 - Domain Knowledge Integration Without Theoretical Guarantee Degradation

**Key Innovation:** Bridges theory-practice gap between provably convergent but sample-inefficient data-driven BO (GP-UCB) and empirically successful but theoretically unguaranteed domain-informed approaches (Xiang et al. 0.124% sampling, Duan et al. 1000x acceleration).

---

## Testable Predictions

**P1 (Regret Bound):** R_T ≤ O(√T log T)·(1 + C·ε_bound) with high probability
- **Validation:** Synthetic benchmarks with controlled prior mismatch ε ∈ {0, 0.5, 1, 2, 5}
- **Success Criteria:** Exponent α ∈ [0.45, 0.55], linear ε-dependence (R²>0.9)

**P2 (Sample Efficiency):** N_ε^RoBO ≤ 2·N_ε^domain for good priors (ε≤1.0)
- **Validation:** Xiang et al. (2023) molecular design + Duan et al. (2022) materials discovery benchmarks
- **Success Criteria:** Within 2x of domain-informed SOTA (GPR-MGK, consensus AL)

**P3 (Graceful Degradation):** N_ε^RoBO ≤ 2·N_ε^GP-UCB for poor priors (ε≥3.0)
- **Validation:** Synthetic experiments with intentionally incorrect priors
- **Success Criteria:** Fixed BO catastrophic failure (>10x worse); RoBO-AKW maintains 2x overhead

**P4 (Weight Convergence):** |w_k(T_adapt) - w_k^optimal| < 0.1 within T_adapt ≤ 50 iterations
- **Validation:** Track weight trajectories on synthetic benchmarks with known ε_k
- **Success Criteria:** Convergence within 50 iterations; final error <0.1

---

## Sub-Hypotheses for Phase 2B

| ID | Statement | Verification | Success Criteria |
|----|-----------|--------------|------------------|
| **SH1** | Adaptive weighting converges to optimal weights w_k^* ∝ exp(-ε_k) | Theory + synthetic experiments | T_adapt ≤ 50; error < 0.1 |
| **SH2** | Posterior predictive checks detect mismatch with power >0.8 | Statistical power analysis + simulation | Power >0.8 for t≥20; FPR ≤0.05 |
| **SH3** | Regret bound R_T ≤ O(√T log T)·(1 + C·ε) holds under bounded error | Extend GP-UCB analysis + fit R_T model | α≈0.50±0.03; linear ε-scaling |
| **SH4** | Sample efficiency competitive on real-world benchmarks | Xiang/Duan experiments | N_ε within 2x of SOTA |
| **SH5** | Per-iteration cost O(n³ + n²K) remains feasible | Runtime profiling | Overhead <10% for n≤500 |

**Dependency:** SH1 → SH2 → SH3 → SH4; SH5 parallel

---

## Key Contributions

**Theoretical:**
1. First regret analysis for BO with ε-bounded prior mismatch
2. Extension of parameter-free online learning (coin betting) to GP/RKHS setting
3. Conditions for guarantee-preserving domain knowledge integration

**Algorithmic:**
1. RoBO-AKW algorithm with adaptive weighting mechanism
2. Online posterior predictive check for mismatch detection
3. Mixture of experts formulation for multi-source GP priors

**Empirical:**
1. Validation on real-world benchmarks (molecular design, materials discovery, LLM-augmented robotics)
2. Demonstration of graceful degradation under incorrect priors
3. Ablation studies isolating adaptive weighting contribution

**Practical Impact:**
- Risk mitigation for domain-informed BO in safety-critical applications
- Framework for LLM-augmented experimental design with quality control
- 50-100x cost savings vs. data-driven BO in expensive domains

---

## Critical Assumptions

1. **Domain knowledge formalizable** as GP priors μ_k(x) - Valid for physics models, molecular features; challenging for implicit knowledge
2. **Bounded error model:** KL(p_true ‖ p_prior) ≤ ε_bound - Excludes adversarial priors; may need outlier detection
3. **Detectability** via posterior predictive checks - Standard Bayesian diagnostic; power depends on sample size
4. **Standard GP-UCB assumptions** - RKHS boundedness, sub-Gaussian noise
5. **Computational feasibility** - O(n³ + n²K) per iteration acceptable for expensive BO

---

## Scope

**In Scope:**
- Expensive black-box optimization (T=50-1000 evaluations)
- Multi-source domain knowledge (K=2-5 sources)
- Applications: molecular design, materials science, LLM-augmented experimentation
- Knowledge types: physics models, data-driven priors, LLM suggestions, expert constraints

**Out of Scope:**
- Cheap function evaluations (use gradient-based methods)
- Very high-dimensional spaces (d>1000, Gap 1 territory)
- Adversarial prior mismatch (ε_bound → ∞)
- Implicit tacit knowledge not formalizable as priors

---

## Key Related Work

**Foundational:**
- Srinivas et al. (2010) - GP-UCB algorithm (2500+ citations) - RoBO-AKW extends
- Orabona & Pál (2016) - Coin betting parameter-free learning (183 citations) - Weighting mechanism
- Alon et al. (2015) - Feedback graphs (169 citations) - Multi-source theory

**Domain-Informed Motivation:**
- Xiang et al. (2023) - 0.124% molecular sampling (3 citations) - Benchmark
- Duan et al. (2022) - 1000x materials acceleration (23 citations) - Benchmark
- Xia et al. (2025) - LLM-augmented BO (0 citations) - Benchmark

**Review:**
- Greenhill et al. (2020) - BO review (345 citations) - Identifies Gap 2

**Total:** 15 papers + 2 code repositories

---

## Statistical Verification Design

**Phase 1: Synthetic Validation**
- Experiment 1.1: Regret scaling (N=50 runs × 60 conditions)
- Experiment 1.2: Graceful degradation (N=50 runs × 6 ε levels)

**Phase 2: Real-World Validation**
- Experiment 2.1: Molecular design - Xiang et al. reproduction (N=20 splits)
- Experiment 2.2: LLM-augmented - Xia et al. benchmark (N=10 tasks)
- Experiment 2.3: Multi-source ablation - Duan et al. (N=30 runs)

**Phase 3: Computational Profiling**
- Experiment 3.1: Runtime scaling (135 configurations)

**Total Burden:** ~3200 BO runs; estimated 4-6 months with parallelization

---

## Falsification Criteria

**Hypothesis FALSIFIED if:**
1. **F1:** Regret scales worse than O(T^0.6) even with ε_bound≤2.0
2. **F2:** Sample efficiency >5x worse than domain-informed methods for ε≤1.0
3. **F3:** No robustness benefit when ε≥3.0 (similar to fixed BO catastrophic failure)
4. **F4:** Per-iteration runtime exceeds function evaluation time
5. **F5:** Critical hyperparameter sensitivity (>50% performance drop with misspecified α or ε_bound)

---

## Open Questions for Phase 2B

**High-Priority (Must Resolve):**
- Q1: Exact constant C in regret bound R_T ≤ O(√T log T)·(1 + C·ε_bound)?
- Q2: Is coin betting minimax-optimal or heuristic?
- Q4: Can real-world domain knowledge (LLM, expert) be formalized as GP priors?
- Q5: Sensitivity to detection threshold α?
- Q7: Computational bottlenecks (predictive checks vs. GP updates)?

**Medium-Priority (Should Resolve):**
- Q3: Extension to non-stationary priors (region-specific weights)?
- Q6: Scalability to many sources (K>5)?
- Q8: Integration with existing BO libraries (BoTorch, GPyOpt)?
- Q9: Practical ε_bound selection when true posterior unknown?

**Low-Priority (Nice to Have):**
- Q10: Interplay with kernel choice (squared exponential vs. Matérn)?

---

## Phase 2B Execution Plan

**Round 1:** SH1 (Weight Convergence) - Foundational
**Round 2:** SH2 (Mismatch Detection) + SH5 (Computational Cost) - Parallel
**Round 3:** SH3 (Regret Bound) - Depends on SH1, SH2
**Round 4:** SH4 (Real-World Validation) - Depends on SH1-3

**Total Verification Time:** 4-6 months (theory + implementation + experiments)

---

## Readiness Confirmation

**✅ Phase 2B Ready:**
- [x] Core hypothesis with measurable variables
- [x] Testable predictions (P1-P4) + falsification criteria (F1-F5)
- [x] Sub-hypotheses (SH1-SH5) with success criteria
- [x] Statistical design with power analysis
- [x] SOTA baselines identified
- [x] Key assumptions explicit and testable
- [x] Scope boundaries clear
- [x] All Phase 1 sources integrated (7/7 = 100%)

**Confidence Level:** MEDIUM-HIGH (0.78/1.0 from Phase 2A Judge)

---

*Full Document: 02a_extended_hypothesis_full.md*
*Next Phase: Phase 2B - Verification Planning*
*Generated: 2026-02-06*
