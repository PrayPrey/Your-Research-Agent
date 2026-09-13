# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-13
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-OscDEQ-v1
**Confidence Level:** 0.78

**Main Hypothesis:**
Under conditions of analog oscillator hardware with inherent noise, **if** Deep Equilibrium Model implicit layers are mapped to hierarchical coupled oscillator networks with phase-locking equilibrium and trained via Equilibrium Propagation, **then** classification accuracy comparable to digital DEQ (within 5% margin on MNIST/Fashion-MNIST/CIFAR-10) will be achieved with significantly lower energy consumption (target: 10-100x reduction), **because** oscillator phase-locking naturally implements fixed-point iteration required by DEQs, and Equilibrium Propagation enables gradient computation through nudged equilibria without backpropagation through analog dynamics.

**Alternative Hypothesis (H0):**
Mapping DEQ implicit layers to oscillator networks does NOT provide any advantage over digital DEQ implementations. Specifically: (1) oscillator networks fail to achieve equilibrium states encoding correct classifications, OR (2) EP training on oscillator networks does not converge to competitive accuracy, OR (3) energy consumption is not significantly lower than digital alternatives due to peripheral circuit overhead.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| Oscillator coupling matrix (K_ij) | Independent | Programmable coupling strengths between oscillator pairs, encoded as conductance values in analog hardware or simulation | K_ij ∈ [-1, 1], learnable via EP |
| Hierarchical topology structure | Independent | Multi-scale oscillator groupings with intra-group mean-field coupling and inter-group skip connections | 2-4 hierarchy levels; group sizes 8-64 |
| Noise injection level (σ²) | Independent | Hardware noise variance matched to training noise injection (Langevin dynamics parameter) | σ² ∈ [0.01, 0.5] relative to signal |
| Classification accuracy | Dependent | Test set accuracy (%) on benchmark datasets | Target: >95% MNIST, >90% Fashion-MNIST, >70% CIFAR-10 |
| Convergence time | Dependent | Time to reach equilibrium state (oscillation cycles or wall-clock time) | Target: <1000 cycles per inference |
| Energy consumption | Dependent | Energy per inference (nJ/inference) via hardware simulation | Target: <10 nJ/inference (vs ~100+ nJ digital) |
| Gradient approximation error | Dependent | ||EP gradient - true gradient|| / ||true gradient|| | Target: <10% relative error |
| Dataset | Controlled | Fixed progression: MNIST → Fashion-MNIST → CIFAR-10 | Standard train/test splits |
| Baseline methods | Controlled | TorchDEQ (digital), Standard EP (MLP), Vanilla OIM | Same hyperparameter budget |

### 1.3 Causal Mechanism

**Causal Chain (N=5 Steps):**

```
[DEQ Implicit Layer f(z,x)]
    → [Kuramoto Oscillator Coupling]
        → [Phase-Locked Equilibrium]
            → [Neural Activation Encoding]
                → [EP Gradient Generation]
                    → [Classification Accuracy]
```

**Step 1: DEQ → Oscillator Mapping**
DEQ residual function f(z, x) = σ(Wz + Ux + b) maps to Kuramoto-type dynamics:
dθ_i/dt = ω_i + Σ_j K_ij sin(θ_j - θ_i) + input_i

**Step 2: Oscillator → Equilibrium**
Coupled oscillators settle to phase-locked states via energy minimization (Kuramoto synchronization). The equilibrium phases θ* correspond to the DEQ fixed point z*.

**Step 3: Equilibrium → Activation Encoding**
Oscillator phases θ_i encode neural activations at equilibrium. Hierarchical topology enables multi-scale feature representation.

**Step 4: EP Nudge → Gradients**
Equilibrium Propagation computes gradients by nudging output toward target and measuring equilibrium shift.

**Step 5: Gradients → Classification**
Iterative weight updates via EP optimize coupling matrix K_ij to minimize classification loss.

**Evidence for Causal Links:**
| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| DEQ → Oscillator | Wang et al. 2024 | Kuramoto oscillators achieve 97% MNIST with EP training | **Strong** |
| Oscillator → Equilibrium | Gower 2025 (OIM+EP) | Phase-locking guaranteed; OIMs converge at GHz rates | **Strong** |
| Equilibrium → Encoding | MDEQ (Bai 2020) | Multi-scale equilibrium features match ResNet performance | **Strong** |
| EP Nudge → Gradients | Kendall 2020; Laborieux 2021 | EP on analog networks proven; scaled to ConvNets | **Strong** |
| Gradients → Classification | TorchDEQ; EqSpike | DEQ training converges; spike-driven EP achieves classification | **Medium** |

**Key Tension:**
- **Expressivity vs. Simplicity:** Simple Kuramoto couplings vs. complex residual functions → Test grouped oscillator interactions
- **EP Gradient Bias:** Finite nudge bias → Apply correction formula
- **Noise as Feature vs. Corruption:** → Match training noise to hardware statistics

### 1.4 Key Assumptions

**A1: DEQ-Oscillator Mathematical Equivalence** - If violated: entire mapping fails
**A2: Anderson Acceleration ≈ Oscillator Momentum** - If violated: slower convergence
**A3: EP Gradients Approximate Implicit Differentiation** - If violated: training fails
**A4: Hardware Noise as Beneficial Regularization** - If violated: hardware deployment infeasible

### 1.5 Scope & Boundaries

**Applies To:** Classification tasks, DEQs, CMOS OIM hardware, stable equilibria
**Does NOT Apply To:** Non-equilibrium dynamics, exact arithmetic, photonic systems, safety-critical

**Boundary Conditions:**
- Network size: 100 - 10,000 oscillators
- Noise level: σ² < 0.5
- Coupling strength: |K_ij| < 1

### 1.6 Testable Predictions

**P1 (Primary - Accuracy):** Within 5% of TorchDEQ baseline (MNIST >95%, Fashion-MNIST >88%, CIFAR-10 >65%)
**P2 (Mechanism):** EP gradient error <10%
**P3 (Noise Robustness):** >90% accuracy retention under 10x noise
**P4 (Energy):** <10 nJ/inference (10-100x reduction)

**Falsification:** MNIST <80%, EP error >50%, >50% accuracy drop at 2x noise, no advantage vs. digital DEQ

### 1.7 SOTA Baseline

| Method | MNIST | Fashion-MNIST | CIFAR-10 | Source |
|--------|-------|---------------|----------|--------|
| TorchDEQ | ~99% | ~93% | ~70% | Geng 2023 |
| OIM + EP | 97.2% | N/A | N/A | Gower 2025 |

### 1.8 Statistical Design

- Effect size: Cohen's d = 0.8
- Required runs: n ≥ 20
- Significance: α = 0.05 (Bonferroni: α' = 0.0125)
- Test: Paired t-test

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):** Does Oscillator-DEQ achieve accuracy within 5% of digital DEQ?
- Verification: Empirical | Critical: MUST PASS

**SH2 (Mechanism):** Is the 5-step causal mechanism the actual cause?
- **H-M1:** DEQ → Oscillator mapping correct
- **H-M2:** Oscillators converge to equilibrium
- **H-M3:** Phases encode activations
- **H-M4:** EP generates valid gradients
- **H-M5:** Training converges

**SH3 (Comparison):** Does Oscillator-DEQ provide energy/robustness advantages?
- Verification: Comparative empirical

### Readiness Checklist

| Requirement | Status |
|-------------|--------|
| "If [X], then [Y] because [Z]" format | ✅ |
| Hypothesis ID (H-OscDEQ-v1) | ✅ |
| Confidence level (0.78) | ✅ |
| Alternative hypothesis (H0) | ✅ |
| Variables operationalized | ✅ |
| Causal evidence (N=5 steps) | ✅ |
| Key assumptions + consequences | ✅ |
| Testable predictions (4) | ✅ |
| Falsification criteria | ✅ |
| Baselines identified | ✅ |
| SH1, SH2, SH3 ready | ✅ |

**Overall Status: ✅ READY FOR PHASE 2B**

### Open Questions

1. **Implementation:** Which ODE solver? TorchDEQ extension? GPU hours estimate?
2. **Data:** Additional datasets? Energy measurement without hardware?
3. **Priority:** SH1 → H-M1 → H-M2 → H-M4 → SH3
4. **Hardware:** Collaboration required? Timeline: 3-6mo simulation → 6-12mo hardware

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work (9 sources)

---

*Generated using YouRA Research Phase 2A Extended Workflow*
*2026-02-13*
