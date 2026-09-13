# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-12
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-MetaCal-v1
**Confidence Level:** 0.85

**Main Hypothesis:**
Under the condition of medical image classification tasks with varying disease prevalence and clinical risk profiles, if a parallel metacognitive module is trained to estimate confidence from feature statistics, logits, and clinical context embeddings using focal calibration loss, then the resulting confidence estimates will be better calibrated (lower ECE) than post-hoc methods because the module learns input-dependent calibration that accounts for clinical decision boundaries, analogous to human metacognitive monitoring in the medial prefrontal cortex.

**Alternative Hypothesis (H0):**
There is no significant difference in calibration quality (ECE) between the proposed MetaCal-Net architecture and post-hoc calibration methods (temperature scaling) when applied to medical image classification, regardless of clinical context conditioning.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| MetaCal module presence | Independent | Binary: architecture with/without parallel metacognitive pathway | {0, 1} |
| Clinical context embeddings | Independent | Learnable embeddings for disease prevalence (rare/common/very common) and risk asymmetry (FN>FP flag) | 3 prevalence levels × 2 risk flags |
| Calibration loss type | Independent | Focal calibration loss vs cross-entropy only | {focal_cal, ce_only} |
| Expected Calibration Error (ECE) | Dependent | 15-bin ECE computed on held-out test set | [0, 1], lower is better |
| Maximum Calibration Error (MCE) | Dependent | Maximum absolute difference between confidence and accuracy across bins | [0, 1], lower is better |
| OOD Detection AUROC | Dependent | Area under ROC for out-of-distribution detection using confidence scores | [0.5, 1.0] |
| Encoder architecture | Controlled | Fixed ResNet-50 or ViT-B/16 pretrained on ImageNet | Fixed |
| Dataset | Controlled | Fixed medical imaging benchmark (e.g., ChestX-ray14, ISIC) | Fixed |
| Training protocol | Controlled | Fixed epochs (100), learning rate (1e-4), batch size (32) | Fixed |

### 1.3 Causal Mechanism

**Causal Chain (N=4 steps):**

```
Feature Extraction → Uncertainty Signals → Raw Confidence → Contextualized Confidence → Calibrated Output
     (Step 1)            (Step 2)            (Step 3)              (Step 4)
```

**Step 1: Feature Extraction → Uncertainty Signals**
- Encoder extracts features; channel-wise statistics (mean, variance, max) capture feature-level uncertainty
- Evidence: Deep network feature statistics correlate with prediction difficulty (Guo et al. 2017)

**Step 2: Uncertainty Signals + Logits → Raw Confidence Estimate**
- MetaCal MLP [256 → 128 → 1] combines feature statistics with pre-softmax logits
- Evidence: ConfidNet shows auxiliary networks can learn confidence from hidden representations

**Step 3: Raw Confidence + Clinical Context → Contextualized Confidence**
- Clinical context embeddings (prevalence, risk) modulate raw confidence
- Evidence: Lambert et al. 2022 shows clinical calibration needs structural uncertainty awareness

**Step 4: Contextualized Confidence + Focal Loss → Calibrated Output**
- Focal calibration loss trains network end-to-end to minimize calibration error
- Evidence: Mukhoti et al. NeurIPS 2020 shows focal loss improves calibration over CE

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step 1 → Step 2 | Guo et al. 2017; Liang et al. 2020 | Feature statistics correlate with miscalibration | Strong |
| Step 2 → Step 3 | ConfidNet TPAMI 2021 | Auxiliary networks learn meaningful confidence | Strong |
| Step 3 → Step 4 | Lambert et al. 2022 | Clinical context affects calibration requirements | Medium |
| Step 4 → Outcome | Mukhoti et al. NeurIPS 2020 | Focal loss reduces ECE significantly | Strong |

**Key Tension:**
- Tension: ConfidNet (Corbière et al. 2021) suggests TCP-based targets suffice, but Lambert et al. 2022 suggests clinical context is essential
- Resolution: This verification plan tests whether clinical context embeddings provide additional benefit over TCP-based auxiliary confidence

### 1.4 Key Assumptions

1. **Calibration is learnable from data**
   - Evidence: ConfidNet empirical results show auxiliary networks learn confidence
   - Consequence if violated: MetaCal module will not improve over random confidence

2. **Feature statistics encode uncertainty information**
   - Evidence: Channel-wise variance correlates with prediction difficulty
   - Consequence if violated: MetaCal inputs lack information; must use alternative uncertainty signals

3. **Clinical context is available or approximatable**
   - Evidence: Disease prevalence derivable from training distribution; risk asymmetry from clinical guidelines
   - Consequence if violated: Cannot condition on clinical context; falls back to context-free calibration

4. **Focal calibration loss provides stable training**
   - Evidence: Mukhoti et al. 2020 shows stable convergence
   - Consequence if violated: Training instability; may need alternative calibration objectives

### 1.5 Scope & Boundaries

**Applies to:**
- Medical image classification (diagnosis, screening)
- Binary and multi-class classification problems
- Modalities: X-ray, CT, dermoscopy, fundus imaging

**Does NOT apply to:**
- Medical image segmentation (requires architectural modification)
- Object detection in medical images
- 3D volumetric analysis (without modification)

**Known Limitations:**
- Requires domain knowledge for clinical context category definition
- Hyperparameter sensitivity for loss balancing (λ_cal, λ_consistency)

### 1.6 Testable Predictions

**Primary Prediction:**

**P1 (ECE Improvement over Baselines):**
MetaCal-Net will achieve ECE < 0.05 on medical imaging benchmarks, representing >30% relative improvement over temperature scaling baseline.

*Measurement*: 15-bin ECE on held-out test set; Paired t-test, n ≥ 20 runs; p < 0.05

*Success Criteria*: ECE < 0.05 AND relative improvement > 30% over temperature scaling (p < 0.05)

*Falsification*: ECE > 0.10 OR no significant improvement over temperature scaling

**Secondary Predictions:**

**P2 (Clinical Context Contribution):**
MetaCal-Net WITH clinical context embeddings will achieve lower ECE than WITHOUT, specifically for rare disease classes (prevalence < 5%).

**P3 (Computational Efficiency):**
MetaCal-Net single-pass inference time will be within 1.1x of baseline encoder inference time (< 10% overhead).

**Falsification Criteria:**

The hypothesis will be **REJECTED** if any occur:
1. **Primary Failure**: ECE > 0.10
2. **Mechanism Failure**: Feature statistics show no correlation with calibration quality, OR clinical context ablation shows no difference
3. **Baseline Failure**: MetaCal-Net performs worse than temperature scaling

### 1.8 Statistical Verification Design

**Sample Size**: n ≥ 20 random seeds
**Statistical Test**: Paired t-test, α = 0.05, power = 0.8
**Effect Size**: Cohen's d > 0.8 (large effect)
**Report Format**: Mean ± Std Dev, 95% CI, Cohen's d, p-value

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Does the MetaCal module produce confidence estimates that are better calibrated than the raw softmax probabilities from the classification head?"
- Maps to: Primary prediction P1
- Verification type: Empirical comparison
- Critical: MUST PASS for hypothesis to proceed

**SH2 (Mechanism):**
"Is the proposed 4-step causal mechanism the actual cause of improved calibration?"

Will decompose into 4 sub-hypotheses in Phase 2B:
- **H-M1:** Feature statistics encode uncertainty information relevant to calibration
- **H-M2:** Combining features + logits produces better confidence than logits alone
- **H-M3:** Clinical context embeddings improve calibration for varying prevalence
- **H-M4:** Focal calibration loss outperforms cross-entropy for calibration training

**SH3 (Comparison):**
"Does MetaCal-Net outperform established baselines (temperature scaling, MC Dropout, ConfidNet) on medical imaging benchmarks?"
- Maps to: Secondary predictions P2, P3
- Verification type: Comparative empirical

**Total sub-hypotheses in Phase 2B:** 6 (1 + 4 + 1)

### Readiness Checklist

- [x] Hypothesis is in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID assigned: H-MetaCal-v1
- [x] Confidence level specified: 0.85
- [x] Alternative hypothesis (H0) defined
- [x] All variables have operationalization from evidence
- [x] Causal mechanism has evidence at each step (N=4 steps)
- [x] Causal chain length determined: N=4
- [x] Key tension identified and resolution proposed
- [x] Key assumptions list consequences if violated
- [x] At least 2 testable predictions exist (3 total)
- [x] Falsification criteria are defined
- [x] Baselines are identified for comparison
- [x] SH1, SH2, SH3 are clear starting points

### Open Questions

1. **Dataset Selection:** Which medical imaging benchmarks should be prioritized? (ChestX-ray14, ISIC, PathMNIST?)

2. **Clinical Context Categories:** How many prevalence levels and risk categories provide optimal granularity?

3. **Verification Order:** Should SH1 (existence) be verified before SH2 (mechanism)?

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow*
*2026-02-12*
