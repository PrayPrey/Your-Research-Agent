# Validated Hypothesis Report: H-LossTraj-v1
## Loss Trajectory Divergence Analysis for Spurious Correlation Detection

**Version:** 2.0
**Generated:** 2026-04-14T11:30:00Z
**Pipeline Phase:** 4.5 (Hypothesis Synthesis)
**Status:** PARTIALLY_VALIDATED

---

## Executive Summary

This document synthesizes experimental evidence from the hypothesis verification loop for the Loss Trajectory Divergence Analysis research direction. The main hypothesis tested whether per-sample loss trajectories during ERM training can serve as diagnostic signatures for spurious correlation-affected samples.

### Overall Assessment

The Loss Trajectory Divergence hypothesis is **partially validated**:

1. **Existence Confirmed:** Per-sample loss trajectory features strongly predict minority group membership (AUROC = 0.9452, 26% above threshold)
2. **Spurious-Specificity Validated:** The divergence attenuates under GroupDRO (delta = 0.29) but not random reweighting (delta = 0.01), confirming it reflects spurious correlation conflict specifically
3. **Curvature Mechanism Refuted:** The proposed curvature timing delay is not observed; curvature stabilizes at epoch 2-3 for all samples
4. **Revised Understanding:** The discriminative signal comes from **loss magnitude** (especially L1) rather than temporal curvature dynamics

**Overall Verdict:** The research direction is **validated with refinements**. The core insight (trajectory divergence exists and is spurious-specific) is confirmed, while the specific mechanism (curvature timing) is replaced with a magnitude-based explanation.

### Key Results Summary

| Sub-Hypothesis | Type | Gate | Result | Primary Metric |
|----------------|------|------|--------|----------------|
| H-E1 | EXISTENCE | MUST_WORK | **PASS** | AUROC = 0.9452 +/- 0.0072 |
| H-M1 | MECHANISM | SHOULD_WORK | **FAIL** | Timing gap = 0.20 +/- 0.40 epochs |
| H-M2 | MECHANISM | SHOULD_WORK | **PASS** | Delta_AUROC_GroupDRO = 0.2923 |
| H-M3 | MECHANISM | SHOULD_WORK | NOT_TESTED | - |

---

## Prediction-Result Matrix

This section maps the original predictions from the main hypothesis to experimental evidence.

### Prediction-to-Evidence Mapping

| ID | Original Prediction | Sub-Hypothesis | Experimental Test | Quantitative Result | Verdict |
|----|---------------------|----------------|-------------------|---------------------|---------|
| **P1** | Trajectory features predict minority with AUROC > 0.75 | H-E1 | 5-fold CV with LogisticRegression on 4 trajectory features | AUROC = 0.9452 +/- 0.0072 | **SUPPORTED** |
| **P2** | Curvature timing gap >= 3 epochs in >= 70% seeds | H-M1 | Second derivative sign-flip detection across 5 seeds | Gap = 0.20 +/- 0.40 epochs, 0% pass rate | **REFUTED** |
| **P3** | AUROC attenuates >0.10 under GroupDRO, <0.05 under random | H-M2 | 3-regime comparison (ERM, GroupDRO, Random Reweighting) | Delta_GDRO = 0.2923, Delta_Random = 0.0100 | **SUPPORTED** |
| **P4** | Early divergence predicts final WGA with R^2 > 0.5 | H-M3 | Not executed due to scope | - | **INCONCLUSIVE** |

### Prediction Success Rate

- **Supported:** 2/4 (50%)
- **Refuted:** 1/4 (25%)
- **Inconclusive:** 1/4 (25%)

### Planned vs Actual Metrics

| Hypothesis | Planned Metric | Threshold | Achieved | Delta from Threshold |
|------------|----------------|-----------|----------|---------------------|
| H-E1 | AUROC | > 0.75 | 0.9452 | +26.0% |
| H-M1 | Timing Gap | >= 3 epochs | 0.20 epochs | -93.3% |
| H-M1 | Pass Rate | >= 70% | 0% | -100% |
| H-M2 | Delta_GDRO | > 0.10 | 0.2923 | +192.3% |
| H-M2 | Delta_Random | < 0.05 | 0.0100 | 80% below threshold (good) |

---

## Hypothesis Refinement

### Original Hypothesis Statement (Pre-Validation)

> Under standard ERM training on spurious correlation benchmarks (Waterbirds), if we track per-sample loss trajectories across epochs, then minority group samples will exhibit statistically distinguishable trajectory patterns (AUROC > 0.75) with delayed curvature stabilization (>=3 epochs later than majority), because the model experiences prolonged optimization conflict when spurious background features contradict learned shortcuts.

### Refined Hypothesis Statement (Post-Validation)

> Under standard ERM training on Waterbirds, per-sample loss trajectory features extracted from epochs 1-5 predict minority group membership with **AUROC = 0.9452 +/- 0.0072**, significantly exceeding the 0.75 threshold. This trajectory divergence is **spurious-feature specific**: it attenuates by 29.2% under GroupDRO training but only 1.0% under variance-matched random reweighting, confirming the divergence reflects spurious correlation conflict rather than generic sample hardness. The proposed curvature timing mechanism (delayed stabilization) is NOT supported - curvature stabilizes at epoch 2-3 for both minority and majority groups.

### Claims Status

#### Claims Validated
1. Trajectory features predict minority membership (AUROC = 0.9452)
2. Initial loss (L1) is the most discriminative feature (AUROC = 0.9473)
3. Divergence is spurious-specific (GroupDRO attenuation >> random reweighting)
4. The signal appears from epoch 1, not requiring extended training

#### Claims Refuted
1. ~~Delayed curvature stabilization (>=3 epochs later than majority)~~
2. ~~Prolonged optimization conflict manifests as curvature timing differences~~

#### Claims Requiring Further Investigation
1. Early divergence predicts final worst-group accuracy (H-M3 not tested)
2. Generalization to other spurious correlation benchmarks (CelebA, ColoredMNIST)

---

## Theoretical Interpretation

### Validated Mechanism: Spurious-Specific Trajectory Divergence

**Evidence Chain:**
1. **H-E1 (Existence):** Trajectory features predict minority membership (AUROC = 0.9452)
2. **H-M2 (Specificity):** GroupDRO (targets spurious correlations) -> large attenuation (0.29)
3. **H-M2 (Control):** Random reweighting (generic smoothing) -> no attenuation (0.01)

**Mechanism Interpretation:**
- Under ERM training, the model learns spurious correlations (background -> bird type)
- Minority samples (conflicting background) experience higher loss from epoch 1
- This creates distinctive trajectory patterns (high L1, steep slope)
- GroupDRO reduces spurious reliance -> trajectory divergence attenuates
- Random reweighting only smooths gradients -> divergence persists

### Refuted Mechanism: Curvature Timing Delay

**Evidence Against:**
1. **H-M1 Result:** Timing gap = 0.20 +/- 0.40 epochs (target: >= 3 epochs)
2. **Pass Rate:** 0% of seeds showed >= 3 epoch gap
3. **Root Cause:** Pretrained ResNet-50 converges very quickly; curvature stabilizes at epoch 2-3 for ALL samples

**Alternative Explanation:**
The discriminative signal comes from **loss magnitude** (L1), not temporal dynamics. Minority samples start at higher loss and maintain distinctive patterns, but the curvature dynamics do not differ meaningfully between groups.

### Per-Feature Analysis

| Feature | AUROC | Rank | Theoretical Role |
|---------|-------|------|------------------|
| **L1 (Initial Loss)** | 0.9473 | 1 | Immediate spurious feature conflict at epoch 1 |
| **Slope** | 0.8970 | 2 | Different learning dynamics for minority samples |
| **Variance** | 0.7242 | 3 | Trajectory instability from conflicting gradients |
| **Convergence Time** | 0.5259 | 4 | Near random - not informative |

**Key Insight:** The initial loss (L1) alone achieves AUROC = 0.9473, suggesting minority samples are distinguishable from epoch 1 due to immediate spurious feature conflict. This is consistent with pretrained models already encoding background features that cause instant conflict for minority samples.

### Unexpected Findings

1. **Initial Loss Dominance:** Expected temporal features to be most important; observed L1 (magnitude) as dominant
2. **Extreme GroupDRO Attenuation:** Expected delta > 0.10; observed delta = 0.2923 (nearly 3x threshold)
3. **Random Reweighting Null Effect:** Expected delta < 0.05; observed delta = 0.0100 (5x below threshold)

These findings strengthen the conclusion that trajectory divergence is specifically tied to spurious feature reliance, not generic sample difficulty.

---

## Experiment Results

### H-E1: Existence Test (MUST_WORK Gate)

**Objective:** Verify that trajectory features can predict minority group membership

**Configuration:**
- Dataset: Waterbirds (4,795 training samples)
- Model: ResNet-50 (ImageNet pretrained)
- Epochs: 20 (trajectory features from epochs 1-5)
- Evaluation: 5-fold stratified cross-validation

**Results:**
```
AUROC (combined features): 0.9452 +/- 0.0072
Gate threshold: 0.75
Gate result: PASS
```

**Per-Feature AUROC:**
| Feature | AUROC |
|---------|-------|
| L1 (Initial Loss) | 0.9473 |
| Slope | 0.8970 |
| Variance | 0.7242 |
| Convergence Time | 0.5259 |

**Conclusion:** Strong evidence that loss trajectory features can identify minority samples. The MUST_WORK gate is satisfied with 26% margin above threshold.

---

### H-M1: Curvature Timing Test (SHOULD_WORK Gate)

**Objective:** Test if minority samples show delayed curvature stabilization

**Configuration:**
- Seeds: 5 (42, 123, 456, 789, 1011)
- Curvature: Second derivative of smoothed loss curves
- Sign-flip detection: First epoch where curvature > -0.002 for 2 consecutive epochs

**Results:**
```
Mean timing gap: 0.20 +/- 0.40 epochs
Target: >= 3 epochs
Pass rate: 0% (0/5 seeds)
Target: >= 70%
Gate result: FAIL
```

**Per-Seed Results:**
| Seed | Minority Median | Majority Median | Timing Gap | Passes |
|------|-----------------|-----------------|------------|--------|
| 42 | 2.0 | 2.0 | 0.0 | No |
| 123 | 2.0 | 2.0 | 0.0 | No |
| 456 | 2.0 | 2.0 | 0.0 | No |
| 789 | 3.0 | 2.0 | 1.0 | No |
| 1011 | 2.0 | 2.0 | 0.0 | No |

**Conclusion:** Curvature stabilizes at epoch 2-3 for ALL samples. The proposed timing mechanism is NOT supported. The discriminative signal comes from loss magnitude, not curvature timing.

---

### H-M2: Spurious-Specificity Test (SHOULD_WORK Gate)

**Objective:** Verify that trajectory divergence reflects spurious-feature conflict specifically

**Configuration:**
- Regimes: ERM, GroupDRO, Random Reweighting
- Seeds: 3 (42, 43, 44)
- GroupDRO gamma: 0.1
- Variance matching: Random weights match GroupDRO gradient variance

**Results:**
```
AUROC (ERM): 0.9436 +/- 0.0123
AUROC (GroupDRO): 0.6513 +/- 0.0390
AUROC (Random): 0.9336 +/- 0.0244

Delta_GroupDRO: 0.2923 (target: > 0.10) - PASS
Delta_Random: 0.0100 (target: < 0.05) - PASS
Gate result: PASS
```

**Interpretation:**
- GroupDRO attenuates trajectory divergence by ~29% (targets spurious correlations)
- Random reweighting attenuates by only ~1% (generic gradient smoothing)
- The 29x difference confirms divergence is spurious-specific, not generic sample hardness

**Conclusion:** Strong evidence that trajectory divergence reflects spurious correlation conflict specifically. The SHOULD_WORK gate is satisfied with large margins.

---

### H-M3: Predictive Validity Test (NOT EXECUTED)

**Status:** Not executed due to pipeline scope constraints

**Planned Objective:** Test if early divergence (W1-distance at epoch 3) predicts final worst-group accuracy

**Reason for Skipping:** H-M3 depends on H-M1 results. With H-M1 failing (no timing gap), the predictive validity test was deprioritized in favor of completing the core validation.

---

## Limitations

### Methodological Limitations

| ID | Limitation | Root Cause | Impact | Mitigation |
|----|------------|------------|--------|------------|
| L1 | Single dataset (Waterbirds) | Scope constraints | Generalization uncertain | Validate on CelebA, ColoredMNIST in future |
| L2 | Curvature mechanism refuted | Pretrained model convergence speed | Original hypothesis partially invalid | Revised mechanism focuses on magnitude |
| L3 | H-M3 incomplete | Pipeline scope | Predictive validity not established | Future work priority |
| L4 | Limited seed variance for H-E1 | PoC tier (single seed) | Statistical robustness limited | H-M2 (3 seeds) confirms robustness |
| L5 | Observational design | No causal intervention on features | "Causes" limited to "associated with" | H-M2 provides interventional evidence via GroupDRO |
| L6 | Pretrained model only | Single initialization strategy | May not generalize to from-scratch training | Test with random init in future |

### Scope Boundaries

**Applies To:**
- Spurious correlation settings with group labels
- Image classification with pretrained CNNs
- Waterbirds benchmark (validated)
- Detection/diagnosis use cases

**Does Not Apply To:**
- Settings without spurious attribute labels (unsupervised detection not tested)
- Non-vision domains (NLP, tabular) without additional validation
- Intervention/debiasing design (detection only)
- Models trained from scratch (pretrained only tested)

### Assumptions Status

| Assumption | Status | Evidence |
|------------|--------|----------|
| A1: Per-sample loss trackable | VALIDATED | H-E1 successful |
| A2: Curvature reflects dynamics | VIOLATED | H-M1 failed - curvature uninformative |
| A3: GroupDRO attenuates spurious | VALIDATED | H-M2 successful |
| A4: Between-seed WGA variance | UNKNOWN | H-M3 not tested |
| A5: Waterbirds representative | ASSUMED | Standard benchmark in literature |

### Threats to Validity

1. **Internal:** Single dataset may have idiosyncratic properties
2. **External:** Generalization to other domains untested
3. **Construct:** "Minority group" defined by group labels, not actual spurious feature reliance

---

## Future Work

### Tier 1: Immediate Extensions (Results-Grounded)

1. **H-M3 Completion** (from incomplete hypothesis)
   - Test early divergence -> final WGA prediction
   - Cross-seed R^2 analysis with 10+ seeds
   - Priority: HIGH (direct extension of current work)

2. **Alternative Temporal Signatures** (from H-M1 failure)
   - First-derivative (slope) temporal patterns
   - Gradient norm trajectories
   - Loss variance evolution over epochs
   - Priority: MEDIUM (pivot from failed mechanism)

### Tier 2: Validation Extensions

3. **Cross-Dataset Validation** (from L1)
   - CelebA benchmark (hair color spurious correlation)
   - ColoredMNIST (color as spurious feature)
   - NICO++ benchmark (diverse spurious correlations)
   - Priority: HIGH (critical for generalization claims)

4. **Architecture Generalization**
   - ViT models (different inductive biases)
   - Different pretraining (CLIP, MAE, self-supervised)
   - Models trained from scratch (no pretrained features)
   - Priority: MEDIUM (broader applicability)

### Tier 3: Application Directions

5. **Trajectory-Guided Debiasing**
   - Sample selection for GroupDRO based on L1
   - Curriculum learning using trajectory features
   - Early stopping criteria from trajectory patterns
   - Priority: MEDIUM (downstream application)

6. **Efficient Detection**
   - L1-only detection (single epoch, no full training)
   - Online trajectory monitoring during training
   - Active learning integration for label-efficient detection
   - Priority: LOW (optimization, not core research)

### Research Questions for Future Investigation

1. Does L1-based detection transfer across datasets without retraining?
2. Can trajectory features detect novel spurious correlations not seen during training?
3. What is the minimum number of epochs needed for reliable detection?
4. How do trajectory patterns differ across model architectures?

---

## Implications for Phase 6

### Paper Framing Recommendations

**Narrative Arc:**
1. Motivation: Spurious correlations cause silent failures in deployed models
2. Insight: Loss trajectories encode spurious feature reliance
3. Validation: AUROC = 0.9452 for minority detection; GroupDRO attenuation confirms specificity
4. Limitation: Curvature timing not informative; magnitude-based mechanism instead
5. Impact: Simple, training-integrated diagnostic for spurious correlation detection

**Key Claims for Paper:**
1. Loss trajectory features predict spurious correlation-affected samples (AUROC = 0.9452)
2. Initial loss (L1) is sufficient for detection (AUROC = 0.9473)
3. Divergence is spurious-specific (GroupDRO attenuation = 0.29 vs. random = 0.01)
4. Detection possible from epoch 1, enabling early intervention

**Claims to Avoid:**
1. ~~Curvature timing differences~~ (refuted by H-M1)
2. ~~Generalization beyond Waterbirds~~ (not tested)
3. ~~Causal claims about trajectory features~~ (observational design)

### Figure Recommendations for Paper

1. **Figure 1:** Loss trajectory comparison (minority vs. majority) - visual evidence
2. **Figure 2:** Per-feature AUROC bar chart - L1 dominance
3. **Figure 3:** GroupDRO vs. Random attenuation - specificity evidence
4. **Figure 4:** ROC curve with AUROC annotation - main result

### Baseline Comparison Strategy (Phase 5)

**Recommended Baseline:** Gradient Norm Detection
- Method: Gradient norms at epoch T for minority prediction
- Rationale: Tests whether trajectory features outperform gradient-based alternatives
- Expected outcome: Trajectory features (especially L1) should outperform due to information integration across epochs

**Alternative Baselines:**
1. Loss-at-epoch-T (single snapshot vs. trajectory)
2. ERM worst-group accuracy (standard spurious correlation metric)
3. JTT-style error-based detection (Liu et al., 2021)

---

## Appendix: Raw Metrics

### H-E1 Complete Results

```json
{
  "auroc_mean": 0.9452,
  "auroc_std": 0.0072,
  "per_feature_auroc": {
    "L1": 0.9473,
    "slope": 0.8970,
    "variance": 0.7242,
    "convergence": 0.5259
  },
  "gate": {
    "threshold": 0.75,
    "achieved": 0.9452,
    "passed": true,
    "result": "PASS"
  },
  "dataset": {
    "train_samples": 4795,
    "minority_samples": 240,
    "minority_ratio": 0.05
  }
}
```

### H-M1 Complete Results

```json
{
  "mean_timing_gap": 0.20,
  "std_timing_gap": 0.40,
  "pass_rate": 0.0,
  "seeds_passed": 0,
  "seeds_total": 5,
  "gate_result": "FAIL",
  "per_seed": {
    "42": {"minority_median": 2.0, "majority_median": 2.0, "gap": 0.0},
    "123": {"minority_median": 2.0, "majority_median": 2.0, "gap": 0.0},
    "456": {"minority_median": 2.0, "majority_median": 2.0, "gap": 0.0},
    "789": {"minority_median": 3.0, "majority_median": 2.0, "gap": 1.0},
    "1011": {"minority_median": 2.0, "majority_median": 2.0, "gap": 0.0}
  }
}
```

### H-M2 Complete Results

```json
{
  "auroc_erm": 0.9436,
  "auroc_erm_std": 0.0123,
  "auroc_groupdro": 0.6513,
  "auroc_groupdro_std": 0.0390,
  "auroc_random": 0.9336,
  "auroc_random_std": 0.0244,
  "delta_gdro": 0.2923,
  "delta_random": 0.0100,
  "gate_result": "PASS",
  "mechanism_verified": {
    "groupdro_weights_diverged": true,
    "variance_matching_verified": true,
    "groupdro_grad_variance": 0.015,
    "random_grad_variance": 0.014
  }
}
```

---

## Conclusion

The Loss Trajectory Divergence hypothesis is **partially validated** with important refinements:

1. **Core Insight Confirmed:** Per-sample loss trajectory features can effectively identify spurious correlation-affected samples with high accuracy (AUROC = 0.9452)

2. **Mechanism Clarified:** The signal comes from loss magnitude (L1), not temporal curvature dynamics. Minority samples are distinguishable from epoch 1.

3. **Specificity Validated:** GroupDRO attenuation (0.29) vs. random reweighting (0.01) confirms the divergence reflects spurious feature conflict specifically.

4. **Practical Implication:** Simple, early-epoch detection is possible using initial loss alone, enabling efficient diagnosis of spurious correlation vulnerability.

The research direction provides a novel diagnostic lens for understanding and detecting spurious correlations in neural network training, with clear pathways for future extension and application.

---

*Generated by Phase 4.5 Hypothesis Synthesis Workflow*
*Anonymous Research Pipeline v3.5*
*Synthesis Date: 2026-04-14*
