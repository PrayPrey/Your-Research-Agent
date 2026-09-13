# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-12
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-IQC-Pareto-v1
**Confidence Level:** 0.78

**Main Hypothesis:**
Under LoRA fine-tuning conditions for transformer-based LLMs, if stochastic Integral Quadratic Constraints (IQCs) are applied to jointly bound robustness (Lipschitz constraint on Jacobian) and privacy (high-probability sensitivity constraint on gradients), then certifiable guarantees for both properties can be achieved with controllable trade-offs via Pareto multi-objective optimization, because the IQC framework from control theory provides a unified mathematical structure that subsumes both deterministic robustness bounds and probabilistic privacy bounds under quadratic constraint formalism.

**Alternative Hypothesis (H0):**
There is no unified mathematical framework that can jointly certify robustness and privacy in LLM fine-tuning; the two properties require fundamentally incompatible constraint structures (deterministic vs. probabilistic), making joint certification with controlled trade-offs infeasible.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| Stochastic IQC formulation | Independent | Define Lipschitz IQC on Jacobian for robustness, high-probability sensitivity IQC on gradients for privacy; parameterized via direct reparameterization (avoiding SDP) | Matrix parameters Π ∈ ℝ^(d×d) |
| Pareto preference vectors | Independent | User-specified weight vectors [w_rob, w_priv, w_util] that determine position on Pareto frontier; implemented via MGDA-style gradient projection | w_i ∈ [0,1], Σw_i = 1 |
| LoRA rank | Independent | Low-rank adapter dimension r applied to attention layers | r ∈ {4, 8, 16, 32, 64} |
| Certified robustness radius | Dependent | Lipschitz constant L such that ‖f(x+δ) - f(x)‖ ≤ L‖δ‖ for ‖δ‖ ≤ ε_rob | L ∈ [1, 100], ε_rob ∈ [0.01, 0.1] |
| Privacy budget (ε-DP) | Dependent | Differential privacy parameter ε derived from high-probability sensitivity bound; computed via concentrated DP accounting | ε ∈ [1, 10] |
| Utility (accuracy) | Dependent | Task accuracy on held-out test set, measured as percentage correct | 85-95% (target: <5% degradation from baseline) |
| Model architecture | Controlled | Fixed transformer architecture (e.g., Llama-2-7B) with frozen base weights | Fixed |
| Training hyperparameters | Controlled | Fixed learning rate, batch size, optimizer (AdamW), training epochs | lr=1e-4, bs=32, epochs=3 |

### 1.3 Causal Mechanism

**Causal Chain (N=4 steps):**

```
[Step 1: Stochastic IQC Formulation]
        ↓
[Step 2: Unified Constraint Representation]
        ↓
[Step 3: Joint Optimization Objective]
        ↓
[Step 4: Pareto-Efficient Training]
        ↓
[Outcome: Certified Joint Guarantees]
```

**Step 1 → Step 2:** Stochastic IQC formulation enables unified constraint representation because quadratic constraints can express both Lipschitz bounds (robustness) and high-probability sensitivity bounds (privacy) in the same mathematical framework.

**Step 2 → Step 3:** Unified constraint representation enables joint optimization objective because having both properties as quadratic constraints allows defining a multi-objective loss function with explicit constraint satisfaction terms.

**Step 3 → Step 4:** Joint optimization objective enables Pareto-efficient training because MGDA-style gradient projection finds descent directions that improve all objectives or identify Pareto-optimal trade-offs.

**Step 4 → Outcome:** Pareto-efficient training produces certified joint guarantees because training converges to solutions that satisfy both IQC constraints simultaneously, yielding provable bounds on robustness and privacy.

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step1 → Step2 | Zhang 2020 (Stochastic IQC) | IQC theory extends to stochastic games with high-probability bounds | Strong |
| Step2 → Step3 | Manchester 2026 | IQC provides built-in certification; direct parameterization avoids SDP | Strong |
| Step3 → Step4 | Du 2025 (CPT Algorithm) | Moving average gradient stabilization enables stable multi-objective training | Medium |
| Step4 → Outcome | Grönqvist 2022 | IQC library for neural network activations validates certification approach | Medium |

**Key Tension:**
- **Tension:** Zhang 2020 demonstrates stochastic IQC for games, but application to DP-style privacy bounds in neural networks is novel and untested. Manchester 2026 provides IQC for robustness but does not address privacy.
- **Resolution:** This verification plan tests whether the mathematical structure of concentrated DP (sub-Gaussian tail bounds) can be expressed as high-probability quadratic constraints compatible with the IQC framework.

### 1.4 Key Assumptions

| # | Assumption | Supporting Evidence | Consequence if Violated |
|---|------------|---------------------|------------------------|
| A1 | Stochastic IQC can mathematically express DP-style privacy as high-probability sensitivity bounds | Zhang 2020 shows stochastic IQC extension exists for probabilistic bounds | Core theoretical contribution fails; must fall back to separate robustness and privacy methods |
| A2 | Pareto multi-objective optimization converges for non-convex LoRA fine-tuning objectives | Du 2025 CPT algorithm demonstrates stable convergence | No controllable trade-offs; must use fixed weighting or alternating optimization |
| A3 | Direct parameterization of IQC constraints avoids computational burden of SDP solvers | Manchester 2026 demonstrates direct parameterization for robustness IQC | Framework becomes computationally infeasible for LLM-scale models |
| A4 | LoRA adapters capture sufficient model capacity for satisfying trustworthiness constraints | DP-FedLoRA 2025 shows DP-compatible LoRA fine-tuning is practical | Must apply constraints to full model, increasing computational cost 10-100x |

### 1.5 Scope & Boundaries

**Applies to:**
- Transformer-based large language models (decoder-only, encoder-decoder)
- LoRA fine-tuning scenarios (not pre-training)
- Joint robustness + privacy certification
- Controllable trade-off selection via Pareto optimization

**Does NOT apply to:**
- Pre-training from scratch (computational constraints)
- Three-property joint optimization (fairness deferred to extension)
- Non-transformer architectures (CNNs, RNNs)
- Certified guarantees against all attack types (focuses on Lipschitz robustness)

**Known Limitations:**
- High-probability bounds are weaker than deterministic guarantees
- Fairness requires future extension (batch-aggregated constraint formulation)
- Approximation errors in direct parameterization may loosen certified bounds
- Computational overhead of IQC constraint enforcement during training

### 1.6 Testable Predictions

**Primary Prediction:**

**P1 (Joint Certification Achievement):**
Our Stochastic-IQC-Pareto framework will achieve joint certification of robustness (Lipschitz bound L ≤ 50) and privacy (ε-DP with ε ≤ 8) in LoRA fine-tuning with utility degradation < 5% compared to unconstrained fine-tuning.

*Measurement:*
- Certified robustness: Compute Lipschitz constant via IQC constraint verification
- Privacy: Compute ε via concentrated DP accounting from sensitivity bounds
- Utility: Task accuracy on held-out test set
- Statistical test: Paired t-test vs. unconstrained baseline, n ≥ 20 runs, p < 0.05

*Success Criteria for Phase 2B:*
- Primary: L ≤ 50 AND ε ≤ 8 AND accuracy ≥ 90% of baseline (p < 0.05)
- Falsification: L > 100 OR ε > 15 OR accuracy < 80% of baseline

**Secondary Predictions:**

**P2 (Pareto Frontier Existence):**
Varying Pareto preference vectors [w_rob, w_priv, w_util] will produce distinct points on a non-trivial Pareto frontier, demonstrating controllable trade-offs between robustness, privacy, and utility.

**P3 (Computational Feasibility):**
The framework will complete LoRA fine-tuning on a 7B parameter model within 2x the wall-clock time of unconstrained fine-tuning on a single A100 GPU.

**Falsification Criteria:**

The hypothesis will be **REJECTED** if any occur:

1. **Primary Failure:** Cannot achieve joint certification (L ≤ 100 AND ε ≤ 15) with accuracy ≥ 80% of baseline

2. **Mechanism Failure:** Privacy sensitivity bounds cannot be expressed as quadratic constraints compatible with robustness IQC

3. **Trade-off Failure:** All Pareto preference vectors produce identical solutions (no trade-off curve)

4. **Computational Failure:** Training requires >10x baseline time or exceeds single-GPU memory

### 1.7 SOTA Baseline (Optional)

*Not applicable - Novel framework development, not performance improvement over SOTA.*

Comparison baselines: Unconstrained LoRA, DP-FedLoRA (privacy only), Self-Denoising (robustness only), Lagrangian dual (Tran 2020)

### 1.8 Statistical Verification Design

**Sample Size:** n ≥ 20 runs per configuration
**Statistical Test:** Paired t-test, α = 0.05, power = 0.8
**Effect Size:** Cohen's d ≥ 0.8 (large effect expected)
**Experimental Design:** 5 preference vectors × 3 LoRA ranks × 20 seeds = 300 runs minimum
**Report Format:** Mean ± Std Dev, 95% CI, Cohen's d, p-value

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Can stochastic IQC constraints be mathematically formulated to jointly bound robustness (Lipschitz) and privacy (high-probability sensitivity) in transformer architectures?"
- Maps to: Primary prediction P1
- Verification type: Theoretical + Empirical
- Critical: MUST PASS for Phase 2B to proceed

**SH2 (Mechanism):**
"Is the 4-step causal chain (IQC Formulation → Unified Constraints → Joint Optimization → Pareto Training → Certified Guarantees) the actual mechanism producing joint certification?"
- Maps to: Causal mechanism (4 sub-hypotheses: H-M1 through H-M4)
- Verification type: Ablation studies + mechanism isolation
- Critical: Determines explanatory power

**SH3 (Comparison):**
"Does Stochastic-IQC-Pareto outperform separate robustness-only and privacy-only methods in terms of joint guarantee quality and controllability?"
- Maps to: Secondary predictions P2, P3
- Verification type: Comparative empirical
- Critical: Determines practical value

**Total sub-hypotheses in Phase 2B:** 2 + 4 = 6 (SH1, H-M1, H-M2, H-M3, H-M4, SH3)

### Readiness Checklist

- [x] Hypothesis is in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID assigned: H-IQC-Pareto-v1
- [x] Confidence level specified: 0.78
- [x] Alternative hypothesis (H0) defined
- [x] All variables have operationalization from evidence (8 variables)
- [x] Causal mechanism has evidence at each step (4 steps, evidence table complete)
- [x] Causal chain length (N=4) determined and stored
- [x] Key tension identified and resolution proposed
- [x] Key assumptions list consequences if violated (4 assumptions)
- [x] At least 2 testable predictions exist with primary marked (P1, P2, P3)
- [x] Falsification criteria are defined (4 criteria)
- [x] Baselines are identified for comparison (4 baselines)
- [x] SH1, SH2, SH3 are clear starting points

### Open Questions

1. **Mathematical Formalization:** What is the exact form of the high-probability quadratic constraint for DP-style privacy? Need to derive from concentrated DP theory.

2. **Implementation Complexity:** How to implement direct parameterization for joint robustness-privacy IQC without introducing numerical instability during backpropagation?

3. **Verification Priority:** Should SH1 (existence) be verified theoretically first before empirical SH2/SH3, or should all proceed in parallel?

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow (Focused)*
*2026-02-12*
