# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-13
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-CurvatureHomeostasis-v1
**Confidence Level:** 0.83

**Main Hypothesis:**
Under overparameterized neural network training with constant learning rate η, if SGD is applied with batch size B, then Batch Sharpness self-regulates toward 2/η (Edge of Stochastic Stability), which implicitly minimizes curvature complexity C(θ), thereby causing convergence to flat minima with smaller generalization gap, because the learning rate acts as feedback gain in a self-regulating dynamical system that drives curvature toward the stability boundary.

**Alternative Hypothesis (H0):**
The observed correlation between flat minima and generalization is coincidental; SGD does not systematically regulate curvature, and any relationship between sharpness and generalization is due to confounding factors (e.g., training duration, data properties) rather than a causal mechanism through curvature self-regulation.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| Learning rate η | Independent | Constant learning rate value set before training | 0.001 - 1.0 (typical: 0.01, 0.1) |
| Batch size B | Independent | Number of samples per mini-batch | 32, 64, 128, 256, 512 |
| Network architecture | Controlled | Fixed architecture held constant (e.g., ResNet-18) | Standard architectures |
| Batch Sharpness | Dependent | Expected directional curvature along stochastic gradients via Hutchinson estimator | Range: 0 to 2/η at equilibrium |
| Curvature complexity C(θ) | Dependent | PAC-Bayes complexity: log-det(I + β·H) or Tr(H) | Lower = flatter minimum |
| Generalization gap | Dependent | Test accuracy - Training accuracy at convergence | Target: < 5% for good generalization |
| Dataset | Controlled | Fixed dataset with standard splits (CIFAR-10/100) | 50K train / 10K test |
| Loss function | Controlled | Cross-entropy loss for classification | Standard CE loss |

### 1.3 Causal Mechanism

**4-Step Causal Chain:**

```
Step 1: Large η exceeds stability threshold
    ↓
Step 2: Oscillations drive optimizer to low-curvature regions
    ↓
Step 3: Low curvature → Low PAC-Bayes complexity C(θ)
    ↓
Step 4: Low C(θ) → Tighter generalization bound → Small gap
```

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step1 → Step2 | Cohen et al. 2021 | λ_max hovers at 2/η, non-monotonic training loss | Strong |
| Step2 → Step3 | Arora et al. 2022 | GD evolves to minimize λ₁ on loss manifold | Strong |
| Step3 → Step4 | Foret et al. 2020 | SAM generalization bound involves sharpness | Strong |
| Step4 → Outcome | PAC-Bayes theory | Complexity measures predict generalization | Medium |

**Key Tension:**
- **Tension:** Andriushchenko et al. (2023) found sharpness does not always correlate with generalization in transformers.
- **Resolution:** This verification plan tests the mechanistic CAUSAL chain in the specific setting of overparameterized CNNs with constant LR, where EoS is well-established.

### 1.4 Key Assumptions

1. **Overparameterization:** Network capacity >> data size
   - *Consequence if violated:* Underfitting; EoS may not occur

2. **Smoothness:** Loss is twice-differentiable with Lipschitz Hessian
   - *Consequence if violated:* Hessian analysis ill-defined

3. **Constant LR:** No learning rate schedules
   - *Consequence if violated:* Equilibrium 2/η becomes moving target

4. **Batch Sharpness Validity:** EoSS measure extends EoS to SGD
   - *Consequence if violated:* Cannot extend full-batch results to mini-batch

### 1.5 Scope & Boundaries

**Applies To:** Overparameterized CNNs/MLPs, SGD, classification, constant LR, CIFAR-10/100

**Does NOT Apply To:** Under-parameterized models, Adam, regression, LR schedules, transformers (without validation)

### 1.6 Testable Predictions

**Primary Prediction:**

**P1 (Curvature Homeostasis Existence):**
Batch Sharpness stabilizes near 2/η (within ±10%) after initial transient.

*Measurement:* Hutchinson estimator, |BS - 2/η| / (2/η) < 0.10
*Statistical:* n ≥ 20 runs, one-sample t-test, p < 0.05

**Secondary Predictions:**

**P2:** Lower Batch Sharpness → Lower C(θ) (Pearson r > 0.7)
**P3:** Lower C(θ) → Smaller generalization gap (Pearson r > 0.5)

**Falsification Criteria:**

1. **Primary Failure:** BS not near 2/η (deviation > 30%)
2. **Mechanism Failure:** |r| < 0.3 between BS and C(θ)
3. **Generalization Failure:** C(θ)-gap correlation < 0.2 or negative

### 1.8 Statistical Verification Design

- Effect size target: Cohen's d > 0.8
- Runs per condition: n ≥ 20
- Power: 0.80, α = 0.05
- Correction: Bonferroni for 3 predictions

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Does Batch Sharpness self-regulate toward 2/η during SGD training?"
- Verification: Empirical
- Critical: MUST PASS

**SH2 (Mechanism):**
"Is the 4-step causal chain the actual mechanism?"
- Decomposes to 4 sub-hypotheses (H-M1 to H-M4)
- Verification: Causal analysis

**SH3 (Comparison):**
"Does curvature homeostasis predict generalization better than sharpness correlation?"
- Verification: Comparative empirical

**Total sub-hypotheses in Phase 2B:** 6 (SH1 + 4×SH2 + SH3)

### Readiness Checklist

- [x] Hypothesis in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID: H-CurvatureHomeostasis-v1
- [x] Confidence: 0.83
- [x] H0 defined
- [x] Variables operationalized
- [x] Causal mechanism: 4 steps with evidence
- [x] Key tension + resolution
- [x] Assumptions with consequences
- [x] 3 testable predictions (P1 primary)
- [x] Falsification criteria defined
- [x] Baselines: GenEFT, EoSS, sharpness-correlation
- [x] SH1/SH2/SH3 defined

### Open Questions

1. **Resources:** ~2-4 GPU-days for 20+ runs on CIFAR-10/ResNet-18
2. **Data:** CIFAR-10 available; Batch Sharpness needs custom implementation
3. **Feasibility:** Hutchinson estimator accuracy for Hessian trace
4. **Priority:** SH1 → SH2.H-M1/M2 → SH2.H-M3/M4 → SH3

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow*
*2026-02-13*
