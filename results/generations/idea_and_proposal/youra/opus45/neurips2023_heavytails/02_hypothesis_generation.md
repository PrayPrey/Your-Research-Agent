# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-12
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md (Round 1 - FEASIBLE)
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-HαC-001
**Confidence Level:** 0.82

**Main Hypothesis:**
An optimizer wrapper that monitors the tail index (α) of naturally emerging gradient noise using online Hill estimation and dynamically adjusts the learning rate via homeostatic feedback control to maintain α within the beneficial range [1.5, 1.9] will achieve statistically significantly better test accuracy (≥1% improvement) and smaller generalization gap compared to baseline SGD and Adam optimizers on standard image classification benchmarks (CIFAR-10, CIFAR-100), without requiring external noise injection.

**Alternative Hypothesis (H0):**
Monitoring and controlling gradient noise tail index (α) through learning rate adjustment does not produce statistically significant improvements in generalization compared to standard optimizers with well-tuned fixed hyperparameters, OR the computational overhead of online α estimation (>10% of training time) makes the approach impractical.

### 1.2 Variables

| Variable Type | Variable | Operationalization | Measurement |
|---------------|----------|-------------------|-------------|
| **Independent** | Learning rate multiplier | Adjusted by feedback: mult = f(α_target - α_measured) | Logged per step |
| **Independent** | Target α range | [α_low, α_high] = [1.5, 1.9] | Fixed hyperparameter |
| **Dependent** | Test accuracy | Top-1 accuracy on held-out test set | % at end of training |
| **Dependent** | Generalization gap | Train accuracy - Test accuracy | Percentage points |
| **Dependent** | α trajectory | Smoothed tail index over training | Time series plot |
| **Controlled** | Architecture | ResNet-18, VGG-16 | Fixed per experiment |
| **Controlled** | Dataset | CIFAR-10, CIFAR-100 | Fixed per experiment |
| **Controlled** | Batch size | 128 | Fixed |
| **Controlled** | Training epochs | 200 | Fixed |
| **Controlled** | Base learning rate | 0.1 (SGD), 0.001 (Adam) | Fixed per optimizer |

### 1.3 Causal Mechanism

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        HαC Causal Mechanism                                  │
└─────────────────────────────────────────────────────────────────────────────┘

[Gradient Computation] → [Gradient Statistics Buffer] → [Hill Estimator]
                                                              │
                                                              ▼
                                                    [α_t (tail index)]
                                                              │
                                                              ▼
                                              ┌───────────────────────────────┐
                                              │   Homeostatic Comparator      │
                                              │   α_t vs [α_low, α_high]      │
                                              └───────────────────────────────┘
                                                              │
                           ┌──────────────────────────────────┼──────────────────┐
                           │                                  │                  │
                           ▼                                  ▼                  ▼
                    α_t < α_low                     α_low ≤ α_t ≤ α_high    α_t > α_high
                    (Too heavy)                     (Optimal zone)         (Too light)
                           │                                  │                  │
                           ▼                                  ▼                  ▼
                    Increase LR                          No change          Decrease LR
                    (More exploration)                                      (Less noise)
                           │                                  │                  │
                           └──────────────────────────────────┼──────────────────┘
                                                              │
                                                              ▼
                                              [Adjusted Learning Rate]
                                                              │
                                                              ▼
                                              [Parameter Update]
                                                              │
                                                              ▼
                                              [Training Dynamics Shift]
                                                              │
                                              ┌───────────────┴───────────────┐
                                              │                               │
                                              ▼                               ▼
                               [Wider Minima Preference]          [Regularization Effect]
                                              │                               │
                                              └───────────────┬───────────────┘
                                                              │
                                                              ▼
                                              [Improved Generalization]
```

**Evidence for Causal Links:**

1. **α → Generalization Connection:**
   - Simsekli et al. (2019): Heavy-tailed gradient noise (low α) causes SGD to escape narrow minima, preferring wider basins that generalize better
   - Raj et al. (2022): Established non-monotonic relationship with optimal threshold—too heavy (α<1.5) hurts, moderate (1.5-1.9) helps
   - Martin & Mahoney (2019): Heavy-tailed ESDs correlate with better generalization in trained networks (146 citations)

2. **LR → α Connection:**
   - Higher learning rate → larger effective step size → more exploration → gradient statistics shift toward heavier tails
   - Lower learning rate → smaller steps → less exploration → gradient statistics become more Gaussian (larger α)
   - Simsekli et al. (2019): Models SGD as Lévy-driven SDE where step size influences tail behavior

3. **Feedback Control → Stability:**
   - Homeostatic control with EMA smoothing (β=0.99) prevents oscillation
   - Bounded adjustment (max 5% per step) ensures gradual transitions
   - Confidence-weighted gain reduces response to unreliable estimates

**Key Tension:**
The hypothesis assumes that (1) α can be reliably estimated online from mini-batch gradients, and (2) the α-LR relationship is sufficiently monotonic to enable stable feedback control. If estimation noise is too high or the relationship is non-monotonic in practice, the feedback loop could amplify instability rather than regulate it.

### 1.4 Key Assumptions

| # | Assumption | Evidence Level | Risk if Violated |
|---|------------|----------------|------------------|
| A1 | α-generalization link holds across architectures (ResNet, VGG) | STRONG: Simsekli et al. (66 citations), Martin & Mahoney (146 citations) tested on multiple architectures | High: Core mechanism fails |
| A2 | Hill estimator provides accurate online α estimates with ~1000 gradient samples | MEDIUM: Hill estimator is standard; online application less studied | Medium: Feedback becomes noisy |
| A3 | Optimal α range [1.5, 1.9] generalizes across CIFAR tasks | WEAK: Extrapolated from Raj et al. least squares results | Medium: May need task-specific tuning |
| A4 | LR adjustment affects α monotonically (higher LR → lower α) | MEDIUM: Theoretically expected from SDE models | High: Feedback could destabilize |
| A5 | Warm-up period (1000 steps) provides sufficient initial estimates | MEDIUM: Standard practice for statistics accumulation | Low: Can extend if needed |

### 1.5 Scope & Boundaries

**In Scope:**
- Image classification on CIFAR-10, CIFAR-100
- CNN architectures: ResNet-18, VGG-16
- SGD and Adam as base optimizers
- Single-GPU training with batch size 128
- Standard data augmentation (random crop, horizontal flip)

**Out of Scope:**
- Large-scale datasets (ImageNet full) - deferred to future work
- Transformer architectures - different gradient dynamics
- Natural language processing tasks
- Distributed training
- Second-order optimizers
- Non-gradient methods

**Boundary Conditions:**
- Requires at least 1000 gradient samples for reliable α estimation
- Assumes training runs long enough for feedback effects (>10,000 steps)
- May not apply when gradient noise is naturally Gaussian (very large batches)

### 1.6 Testable Predictions

**Primary Prediction:**
P1: HαC-wrapped SGD will achieve test accuracy ≥1% higher than baseline SGD on CIFAR-10 and CIFAR-100 with ResNet-18, measured over 5 random seeds with p<0.05 (paired t-test).

**Secondary Predictions:**
P2: The generalization gap (train accuracy - test accuracy) for HαC will be at least 20% smaller than baseline SGD, indicating better regularization effect.

P3: The α trajectory of HαC-controlled training will remain within [1.5, 1.9] for >80% of training steps after warm-up, while baseline SGD's α will drift outside this range.

P4: HαC will show comparable or better performance than AHTSGD (noise injection baseline) while using only monitoring (no external noise injection).

**Falsification Criteria:**
The hypothesis is FALSIFIED if ANY of the following occur:
- F1: HαC shows no statistically significant improvement over baseline SGD (p≥0.05) on CIFAR-10/100
- F2: HαC's α trajectory fails to maintain target range (>50% of steps outside [1.5, 1.9])
- F3: HαC's computational overhead exceeds 10% of baseline training time
- F4: HαC causes training instability (loss divergence) in >20% of runs

### 1.7 SOTA Baseline (Optional - If SOTA Comparison Mode)

*Not applicable - this is a methodological contribution, not SOTA-chasing*

### 1.8 Statistical Verification Design

**Experiment Design:** Randomized controlled experiment with multiple seeds

**Sample Size:**
- 5 random seeds per condition
- 4 conditions: {SGD, SGD+HαC, Adam, Adam+HαC}
- 2 datasets: CIFAR-10, CIFAR-100
- 2 architectures: ResNet-18, VGG-16
- Total: 80 training runs

**Statistical Tests:**
- Primary: Paired t-test comparing HαC vs baseline (within optimizer family)
- Secondary: Two-way ANOVA for optimizer × HαC interaction
- Effect size: Cohen's d for practical significance
- Significance threshold: α=0.05 (Bonferroni corrected for multiple comparisons)

**Power Analysis:**
- Expected effect size: d=0.8 (large, based on 1% accuracy improvement with ~0.5% std)
- With n=5 per condition, power ≈ 0.80 for detecting d=0.8
- If effect is smaller, will increase to n=10

**Reporting:**
- Mean ± std for all metrics
- 95% confidence intervals
- p-values with effect sizes
- α trajectory plots with confidence bands

---

## 2. Contribution Summary

| Contribution Type | Description | Novelty Claim | Validation Method |
|-------------------|-------------|---------------|-------------------|
| **Theoretical** | Framework connecting real-time emergent α to learning rate for generalization control | First theoretical formulation of α-based homeostatic learning rate adaptation | Mathematical analysis of feedback stability |
| **Methodological** | Online tail index estimation integrated into optimizer step with confidence weighting | Novel integration of Hill estimator into optimizer with warm-up and bounded adjustment | Ablation study of components |
| **Practical** | Drop-in optimizer wrapper (HαC) compatible with any base optimizer | First practical "observe and adapt" heavy-tail aware optimizer (vs AHTSGD's "inject and control") | Benchmark comparison on CIFAR |

**Differentiation from AHTSGD:**

| Aspect | AHTSGD (Gong et al., 2025) | HαC (Proposed) |
|--------|---------------------------|----------------|
| Philosophy | Inject controlled heavy-tailed noise | Monitor emergent α, adapt lr |
| Mechanism | Add Lévy noise to gradients | Adjust lr based on measured α |
| Intervention | External noise injection | Hyperparameter adaptation |
| Overhead | Noise generation per step | Statistics collection + Hill estimator |
| Tuning | Noise parameters (α_inject, scale) | Target range, feedback gain |

---

## 3. Key Related Work

| Paper | Year | Relation | Gap Addressed |
|-------|------|----------|---------------|
| Simsekli et al. "Heavy-Tailed Theory of SGD" | 2019 | Foundation: α-stable gradient noise framework | Theoretical basis for α-generalization link |
| Raj et al. "Algorithmic Stability of Heavy-Tailed SGD" | 2022 | Foundation: Threshold of beneficial α | Defines target range [1.5, 1.9] |
| Martin & Mahoney "Heavy-Tailed Self-Regularization" | 2019 | Foundation: HT-SR theory | Establishes α as generalization predictor |
| Gong et al. "AHTSGD" | 2025 | Comparison: Noise injection approach | Novelty differentiation baseline |
| Cohen et al. "Edge of Stability" | 2021 | Related: Training dynamics | Potential future integration |
| Hirashima "Mechanical Feedback Control" | 2022 | Inspiration: Homeostatic regulation | Cross-domain design principle |

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"The Hill estimator can reliably estimate gradient noise tail index (α) online during training with sufficient accuracy (coefficient of variation <0.2) using a rolling buffer of 1000 gradient samples."

**SH2 (Mechanism):**
"Learning rate adjustment via homeostatic feedback (increasing lr when α<1.5, decreasing when α>1.9) effectively maintains α within the target range [1.5, 1.9] for >80% of training steps after warm-up."

**SH3 (Comparison):**
"HαC achieves statistically significantly better test accuracy (≥1%, p<0.05) than baseline SGD/Adam on CIFAR-10/100 with ResNet-18/VGG-16, with computational overhead <10%."

### Readiness Checklist

- [x] Core hypothesis statement is specific and testable
- [x] Variables are clearly defined and operationalized
- [x] Causal mechanism is articulated with evidence
- [x] Key assumptions are identified with risk assessment
- [x] Scope and boundaries are defined
- [x] Testable predictions with falsification criteria exist
- [x] Statistical verification design is specified
- [x] Contributions are clearly differentiated from prior work
- [x] Related work is mapped with gap connections
- [x] Sub-hypothesis decomposition is previewed

### Open Questions

1. **Hill Estimator Variant:** Which specific Hill estimator variant (simple, adaptive, kernel-based) provides best bias-variance tradeoff for online gradient analysis?

2. **Layer-wise vs Global α:** Should α be estimated globally across all parameters or layer-wise? Layer-wise may capture architecture-specific dynamics but increases complexity.

3. **Momentum Interaction:** Raj et al. (2023) showed SGD with momentum may behave differently under heavy tails. How does HαC interact with momentum-based optimizers?

4. **Adaptive Target Range:** Is [1.5, 1.9] optimal for all architectures, or should the target range be architecture-adaptive?

5. **Long Training Dynamics:** How does HαC behave in very long training (>1000 epochs)? Does α naturally stabilize or require continued adjustment?

---

*Generated using YouRA Research Phase 2A Extended Workflow (Focused)*
*2026-02-12*
