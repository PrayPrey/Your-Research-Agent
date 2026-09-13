# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-12
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-BCBMV-v1
**Confidence Level:** 0.85

**Main Hypothesis:**
Under the condition of medical imaging classification with concept annotations, if we replace deterministic concept prediction layers with variational layers that output Gaussian parameters (μ, σ²), then concept-level calibration (ECE) will improve by >30% compared to vanilla CBM because variational inference naturally captures predictive uncertainty through learned distribution parameters.

**Alternative Hypothesis (H0):**
Variational concept layers provide no significant improvement in concept-level calibration (ECE) compared to deterministic concept prediction layers, and any observed differences are due to random variation or increased model capacity.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| Variational Concept Layer Architecture | Independent | Replace standard linear concept prediction with dual-head output (μ_c, log σ²_c) using reparameterization trick | Architecture: {variational, deterministic, MC-dropout} |
| KL Weight (β) | Independent | Coefficient for KL divergence term in ELBO loss | β ∈ [0.001, 0.1] |
| MC Sample Count | Independent | Number of Monte Carlo samples during inference | K ∈ {5, 10, 20, 50} |
| Concept-Level ECE | Dependent | |confidence - accuracy| averaged over binned predictions per concept | ECE ∈ [0, 0.5], lower is better |
| Prediction Accuracy | Dependent | Final label classification accuracy on test set | Accuracy ∈ [0.7, 0.95] |
| Clinical Utility Score | Dependent | Physician survey rating intervention usefulness | Likert scale 1-5 |
| Dataset | Controlled | CheXpert (224K) or MIMIC-CXR (377K) with fixed concept annotations | Fixed per experiment |
| Base Encoder | Controlled | DenseNet-121 pretrained on ImageNet | Fixed architecture |
| Evaluation Protocol | Controlled | 5-fold cross-validation with fixed random seeds | Seeds: {42, 123, 456, 789, 1011} |

### 1.3 Causal Mechanism

```
┌─────────────────────────────────────────────────────────────────┐
│  CAUSAL CHAIN (N=2 steps)                                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  [Input Image x]                                                │
│        │                                                        │
│        ▼                                                        │
│  ┌───────────────┐                                              │
│  │ Base Encoder  │  (DenseNet-121)                              │
│  └───────────────┘                                              │
│        │                                                        │
│        ▼                                                        │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ STEP 1: Variational Concept Layer                         │  │
│  │  x → (μ_c, log σ²_c) for each concept c                   │  │
│  │  Reparameterization: c = μ_c + σ_c * ε, ε ~ N(0,1)        │  │
│  └───────────────────────────────────────────────────────────┘  │
│        │                                                        │
│        │  Per-concept uncertainty estimates                     │
│        ▼                                                        │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ STEP 2: Uncertainty → Calibration                         │  │
│  │  σ_c reflects epistemic uncertainty for concept c         │  │
│  │  Confidence = f(μ_c, σ_c) → aligns with accuracy          │  │
│  └───────────────────────────────────────────────────────────┘  │
│        │                                                        │
│        ▼                                                        │
│  [Improved ECE: calibrated concept predictions]                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step1 → Step2 | Kingma & Welling (2013) VAE | Reparameterization trick enables gradient flow through stochastic sampling | Strong |
| Step1 → Step2 | torch-uncertainty library | Production-ready implementation of variational layers | Strong |
| Step2 → Outcome | Zhang (2025) Uncertainty-Aware CBM | Uncertainty propagation improves robustness in CBMs | Medium |
| Step2 → Outcome | López (2025) UQ Healthcare Survey | UQ improves calibration in healthcare ML systems | Strong |

**Key Tension:**
- **Tension:** Zhang (2025) uses prototype-based distance for uncertainty, while our approach uses learned Gaussian parameters. It's unclear whether parametric (Gaussian) or non-parametric (prototype) uncertainty better captures concept-level confidence.
- **Resolution:** This verification plan will test both approaches as ablations, with primary focus on variational layers.

### 1.4 Key Assumptions

| Assumption | Supporting Evidence | Consequence if Violated |
|------------|--------------------|-----------------------|
| **A1: Gaussian distributions adequately capture concept prediction uncertainty** | Medical imaging concepts have continuous confidence levels; VAE literature validates Gaussian latent spaces | If concepts are inherently binary, variance estimates will be uninformative. Mitigation: CheXpert uses multi-level labels |
| **A2: ECE can be meaningfully computed at concept level** | Zhang 2023 demonstrates ECE for medical imaging; Sambyal 2023 validates calibration metrics | If concept predictions lack sufficient samples per bin, ECE estimates will be noisy. Mitigation: Adaptive binning |
| **A3: Clinicians can interpret confidence intervals on concepts** | Medical practice already reports findings with confidence levels | If confidence intervals confuse clinicians, clinical utility will be low. Mitigation: User study |
| **A4: Training overhead is acceptable (~2x)** | VAE training on similar scale datasets is well-established | If training exceeds reasonable limits, practical adoption is limited |

### 1.5 Scope & Boundaries

**Where Hypothesis Applies:**
- Medical imaging classification with pre-defined concept annotations
- Datasets with continuous or multi-level concept labels
- Settings where interpretability and uncertainty are valued over pure accuracy

**Where Hypothesis Does NOT Apply:**
- Domains without interpretable intermediate concepts
- Real-time inference requirements (<10ms per image)
- Purely binary concept annotations without confidence levels

**Known Limitations:**
- Concept correlation not explicitly modeled
- ~10x inference overhead with MC sampling
- Requires concept annotations during training

### 1.6 Testable Predictions

**Primary Prediction:**

**P1 (Concept-Level ECE Improvement):**
If we add variational concept layers to CBM, then concept-level ECE will improve by >30% compared to vanilla CBM.

*Measurement:* ECE reduction > 30% (relative), p < 0.05, n ≥ 20 runs
*Success Criteria:* ECE_variational < 0.7 × ECE_vanilla

**Secondary Predictions:**

**P2 (Intervention Utility):**
If concept uncertainty is high, clinician intervention on that concept will improve accuracy more than random intervention (>2x improvement).

**P3 (OOD Detection):**
Variational concept uncertainty will outperform prediction-level entropy for OOD detection by >15% AUROC.

**Falsification Criteria:**

1. **Primary Failure:** ECE_variational ≥ ECE_vanilla
2. **Mechanism Failure:** High-uncertainty concepts show no correlation with prediction errors
3. **Baseline Failure:** MC Dropout outperforms variational layers on all metrics

### 1.7 SOTA Baseline

*Not applicable - Absolute performance validation mode*

### 1.8 Statistical Verification Design

**Sample Size:** n ≥ 20 (5-fold CV × 4 random seeds)
**Statistical Test:** Paired t-test, α = 0.05 (Bonferroni corrected to α = 0.017)
**Effect Size:** Cohen's d > 0.8 (large effect expected)
**Report Format:** Mean difference, 95% CI, Cohen's d, p-value

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Does variational concept layer produce valid uncertainty estimates under medical imaging conditions?"
- Maps to: Primary prediction (ECE improvement)
- Verification type: Empirical
- Critical: MUST PASS for Phase 2B to proceed

**SH2 (Mechanism):**
"Is variational inference the actual cause of improved calibration?"
- Decomposes into N=2 sub-hypotheses:
  - **H-M1:** Variational layers → Per-concept uncertainty (Step 1)
  - **H-M2:** Per-concept uncertainty → Improved ECE (Step 2)
- Verification type: Causal analysis with ablations

**SH3 (Comparison):**
"Does B-CBM-V outperform baselines (vanilla CBM, MC Dropout) on calibration?"
- Maps to: Secondary predictions
- Verification type: Comparative empirical

### Readiness Checklist

- [x] Hypothesis is in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID assigned (H-BCBMV-v1)
- [x] Confidence level specified (0.85)
- [x] Alternative hypothesis (H0) defined
- [x] All variables have operationalization from evidence
- [x] Causal mechanism has evidence at each step (N=2 steps)
- [x] Causal chain length (N=2) determined
- [x] Key tension identified and resolution proposed
- [x] Key assumptions list consequences if violated
- [x] At least 2 testable predictions exist (3 predictions)
- [x] Falsification criteria defined (3 conditions)
- [x] Baselines identified (vanilla CBM, MC Dropout)
- [x] SH1, SH2, SH3 are clear starting points

### Open Questions

1. **KL Weight Tuning:** Optimal β ∈ [0.001, 0.1] for medical imaging?
2. **MC Sample Efficiency:** How many samples (K) for stable uncertainty?
3. **Multi-Domain Validation:** Generalization across imaging domains?
4. **Clinical Visualization:** How to display per-concept confidence intervals?

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow*
*2026-02-12*
