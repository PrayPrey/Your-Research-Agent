# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-12
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-MSD-v1
**Confidence Level:** 0.78

**Main Hypothesis:**
Under standard deep learning training conditions, if we monitor training dynamics (loss trajectory, Prediction Depth) combined with prediction consistency under semantic-preserving augmentations, then we can detect examples relying on spurious correlations without group labels, because spurious features are learned faster (simplicity bias) and produce inconsistent predictions under augmentations that preserve core semantic content.

**Alternative Hypothesis (H0):**
Training dynamics and prediction consistency patterns do not reliably distinguish spurious-reliant examples from core-feature examples; the behavioral signatures of fast learning and augmentation inconsistency are not specific to spurious correlation reliance.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| Training dynamics features | Independent | Per-example loss trajectory slope in first 10% of training, gradient norm, Prediction Depth (layer at which correct prediction stabilizes) | Loss slope: [-0.5, 0], PD: [1, L] where L=num_layers |
| Prediction consistency score | Independent | Variance of softmax outputs across K semantic-preserving augmentations (K=5-10) | Variance: [0, 0.25] for softmax outputs |
| Prediction Depth threshold | Independent | Percentile cutoff for identifying anchor set with high Prediction Depth | 10th-30th percentile (deeper = more core) |
| Spurious reliance detection AUC | Dependent | AUC-ROC of flagging spurious-reliant examples vs ground-truth group membership | Target: >0.75 AUC |
| Worst-group accuracy improvement | Dependent | Accuracy on minority group after mitigation minus ERM baseline | Target: >10% improvement |
| OOD generalization | Dependent | Accuracy on test set where spurious correlation is broken/reversed | Target: >5% improvement over ERM |

### 1.3 Causal Mechanism

**Causal Chain (N=3 steps):**

```
Step 1: Simplicity Bias → Fast Learning of Spurious Features
        ↓
Step 2: Spurious Feature Reliance → Augmentation Inconsistency
        ↓
Step 3: Combined Behavioral Signature → Accurate Spurious Detection
        ↓
      Outcome: Targeted Mitigation → Improved Worst-Group Accuracy
```

**Step 1 - Simplicity Bias Effect:**
DNNs preferentially learn simpler features first due to gradient descent dynamics. Spurious features (textures, backgrounds, artifacts) are often simpler than core semantic features, causing them to be learned in early training epochs and at shallower network layers.

**Step 2 - Augmentation Sensitivity:**
Examples relying on spurious features exhibit high prediction variance under semantic-preserving augmentations because these augmentations alter the spurious cues while preserving the core semantic content. Core-feature predictions remain stable.

**Step 3 - Joint Signal Specificity:**
The combination of (fast learning AND augmentation inconsistency) provides higher specificity than either signal alone. Fast learning alone could flag easy examples; inconsistency alone could flag ambiguous examples. The joint presence specifically indicates spurious reliance.

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step 1 → Step 2 | Murali et al. (2023) | "Harmful spurious features can be detected by observing learning dynamics of early layers. Easy features learned early can hurt generalization." Uses Prediction Depth to quantify. | Strong |
| Step 2 → Step 3 | Adebayo et al. (2022) | Post-hoc explanations fail for unknown spurious features, motivating behavioral (dynamics-based) approaches | Medium |
| Step 3 → Outcome | SCER (Park et al., 2025), ULE (Mitchell et al., 2025) | Recent methods achieve 29-44% worst-group improvement by targeting spurious features | Strong |

**Key Tension:**
Murali et al. (2023) shows Prediction Depth identifies spurious-reliant examples, but the anchor set identification assumes some examples learn via core features. If the entire dataset is spuriously correlated (no "clean" examples), the normal behavior manifold would be contaminated.

**Resolution:** Use Prediction Depth threshold to identify highest-depth examples as anchor set. Even in highly correlated datasets, some examples will have relatively higher depth. Phase 2B must test sensitivity to anchor set contamination levels.

### 1.4 Key Assumptions

1. **Simplicity Bias Assumption:** Spurious features are simpler and learned faster than core features
   - *Evidence:* Geirhos (2020), Murali (2023) empirically validated
   - *If violated:* Detection based on learning speed fails; must rely solely on consistency

2. **Augmentation Preservation Assumption:** Semantic-preserving augmentations do not remove or significantly alter core predictive features
   - *Evidence:* Standard practice in SSL (SimCLR, MoCo); domain-specific validation needed
   - *If violated:* Consistency metric becomes unreliable; false positives increase

3. **Prediction Depth Correlation Assumption:** Prediction Depth correlates with feature complexity - shallow predictions indicate simpler (potentially spurious) features
   - *Evidence:* Murali (2023) Prediction Depth methodology
   - *If violated:* Anchor set identification fails; entire pipeline becomes unreliable

4. **Foundation Model Transfer Assumption:** Fine-tuning dynamics on foundation models exhibit similar patterns to full training dynamics
   - *Evidence:* Probe-based dynamics shown effective in transfer learning literature
   - *If violated:* MSD limited to training-from-scratch scenarios

### 1.5 Scope & Boundaries

**Where Hypothesis Applies:**
- Supervised classification tasks (vision, language, multimodal)
- Fine-tuning pre-trained foundation models
- Any neural network architecture with layered representations
- Datasets with at least some examples that learn via core features

**Where Hypothesis Does NOT Apply:**
- Pure generative modeling without classification objective
- Extremely small datasets where dynamics are noisy (n < 1000)
- Settings where ALL augmentations remove core features (domain-specific)
- Real-time inference requirements (method requires training-time monitoring)

**Known Limitations:**
- Augmentation-invariant spurious features may be missed
- Threshold tuning required per domain (Prediction Depth percentile, consistency variance cutoff)
- Computational overhead of storing per-example dynamics and running augmentation ensembles

### 1.6 Testable Predictions

**Primary Prediction:**
**P1 (Detection Accuracy):**
MSD will achieve spurious detection AUC-ROC > 0.75 on standard benchmarks (Waterbirds, CelebA) without requiring group labels during training.

*Measurement:*
- AUC-ROC > 0.75 with p < 0.05
- Statistical test: Bootstrap confidence intervals, n ≥ 1000 test examples

*Basis:*
Recent methods (JTT, GEORGE) achieve ~0.65-0.70 AUC with single signals. Dual-signal approach should improve to >0.75.

*Success Criteria for Phase 2B:*
- Primary: AUC > 0.75 (p < 0.05)
- Falsification: AUC ≤ 0.60 triggers rejection

**Secondary Predictions:**

**P2 (Worst-Group Improvement):**
After applying targeted mitigation (loss upweighting) to MSD-flagged examples, worst-group accuracy will improve by >10% over ERM baseline.

*Measurement:* Worst-group accuracy improvement, n ≥ 3 random seeds

**P3 (Mechanism Validation):**
Examples flagged by MSD (fast learning + inconsistent) will have significantly lower Prediction Depth AND higher augmentation variance than non-flagged examples (p < 0.01).

*Measurement:* Two-sample t-test on Prediction Depth and variance distributions

**Falsification Criteria:**
The hypothesis will be **REJECTED** if any occur:

1. **Primary Failure:** Detection AUC ≤ 0.60 (no better than random + margin)
2. **Mechanism Failure:** Flagged examples do NOT show significantly different Prediction Depth or consistency scores
3. **Mitigation Failure:** Worst-group accuracy improvement < 5% despite correct detection

### 1.7 Statistical Verification Design

**Sample Size Calculation:**
- Effect size (Cohen's d): 0.5 (medium effect expected)
- Required runs: n ≥ 20 random seeds
- Statistical power: 0.8

**Test Specification:**
- Method: Bootstrap confidence intervals for AUC; paired t-test for accuracy comparisons
- Significance level: α = 0.05 (two-tailed for mechanism tests, one-tailed for improvement tests)
- Report format: Mean ± Std Dev, 95% CI, Cohen's d, p-value

**Datasets:**
- Primary: Waterbirds (known spurious: background)
- Secondary: CelebA (known spurious: hair color for gender)
- Ablation: CIFAR-10-S (controlled single-pixel spurious)

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Does the behavioral signature (fast learning + prediction inconsistency) exist as a distinguishing characteristic of spurious-reliant examples?"
- Maps to: Primary prediction (Detection AUC)
- Verification type: Empirical observation
- Critical: MUST PASS for hypothesis to proceed

**SH2 (Mechanism):**
"Is the proposed 3-step causal mechanism (simplicity bias → fast learning → inconsistency → detection) the actual cause of MSD's detection capability?"
- Maps to: Causal mechanism validation
- Phase 2B will decompose into 3 sub-hypotheses:
  - H-M1: Simplicity bias → fast learning (Prediction Depth correlation)
  - H-M2: Fast learning → augmentation sensitivity (behavioral linkage)
  - H-M3: Joint signal → improved specificity (dual vs single signal)
- Verification type: Causal ablation experiments

**SH3 (Comparison):**
"Does MSD outperform existing methods (JTT, ERM) in detecting and mitigating spurious correlations?"
- Maps to: Secondary predictions (worst-group accuracy)
- Verification type: Comparative empirical
- Critical: Determines practical value

**Total sub-hypotheses in Phase 2B:** 2 + 3 = 5 (SH1 + SH2[×3] + SH3)

### Readiness Checklist

- [x] Hypothesis is in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID assigned: H-MSD-v1
- [x] Confidence level specified: 0.78
- [x] Alternative hypothesis (H0) defined
- [x] All variables have operationalization from evidence
- [x] Causal mechanism has evidence at each step (N=3 steps, evidence table complete)
- [x] Causal chain length (N=3) determined and stored
- [x] Key tension identified and resolution proposed
- [x] Key assumptions list consequences if violated
- [x] At least 2 testable predictions exist (3 total, with P1 as primary)
- [x] Falsification criteria are defined (3 conditions)
- [x] Baselines identified for comparison (JTT, GroupDRO, ERM)
- [x] SH1, SH2, SH3 are clear starting points

### Open Questions

1. **Resource Requirements:** What computational overhead does per-example dynamics tracking add? Estimate: ~20% training time increase for storing loss/gradient histories.

2. **Augmentation Selection:** Which augmentation ensemble is optimal for different modalities (vision vs. language vs. multimodal)? Requires domain-specific tuning in Phase 2C.

3. **Threshold Sensitivity:** How sensitive is detection performance to Prediction Depth percentile threshold? Recommend ablation study in Phase 2B across 10th-30th percentile range.

4. **Priority Verification Order:** Recommend SH1 (existence) first, then SH2-M1 (simplicity bias link), then SH2-M2/M3, finally SH3 (comparison).

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow (Focused)*
*2026-02-12*
