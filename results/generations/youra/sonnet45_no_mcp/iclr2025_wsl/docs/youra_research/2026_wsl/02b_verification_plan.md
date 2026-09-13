# Verification Plan: Weight-Based Binary Classification of CNN Architectural Depth

**Date:** 2026-04-21
**Hypothesis ID:** H-WeightDepthClassifier-v1
**Confidence:** 0.75
**Total Hypotheses:** 4

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement
Under the scope of pretrained ImageNet CNNs (ResNet, VGG, DenseNet families), if we extract layer-wise weight norm statistics (mean, std, min, max of Frobenius norms) and train a logistic regression classifier on 16 models (8 shallow ≤34 layers, 8 deep ≥50 layers), then test accuracy on 4 held-out models will exceed 70%, because deeper networks develop distinctive weight distribution patterns due to accumulated gradient transformations and architectural constraints (residual connections, batch normalization).

### 1.2 Alternative Hypothesis (H0)
There is no significant difference in weight distribution statistics between shallow (≤34 layers) and deep (≥50 layers) pretrained CNNs sufficient for >70% binary classification accuracy.

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | PyTorch Torchvision Pretrained Models (standard) | Provides 20+ pretrained ImageNet CNNs with standardized training, covering shallow and deep architectures across multiple families |
| **Model** | sklearn LogisticRegression | Simple linear classifier appropriate for EXISTENCE-tier validation, interpretable coefficients, no custom algorithms required |

**Dataset Details:**
- Source: torchvision.models (PyTorch official)
- Path: torchvision.models API (no file downloads)

**Model Details:**
- Type: Binary classifier
- Source: scikit-learn (built-in)

### 1.4 Baseline Methods (for Phase 5 comparison)

| Method | Performance | Dataset | Why Insufficient |
|--------|-------------|---------|------------------|
| Run 3 Weight Norm Correlation | \|ρ\| = 0.859, p = 0.067 (failed significance) | 5 ResNet models | Small sample size (n=5), rigorous threshold (ρ ≥ 0.90), continuous correlation instead of classification |
| Random Classifier | 50% accuracy (random guessing) | N/A | Baseline for statistical significance |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | Pretrained models retain architectural signatures from training process | Weight statistics reflect training history - gradient flow patterns persist in final weights | If weights are re-initialized or heavily fine-tuned post-pretraining, architectural signatures may be erased, causing classification failure |
| A2 | Depth signal is stronger than confounding variables (width, training recipe, architecture family) | Run 3 showed correlation \|ρ\| = 0.859, suggesting depth signal exists despite confounds | Classifier may learn width/training patterns instead of depth, leading to spurious accuracy |
| A3 | Simple aggregated features (mean/std/min/max) capture sufficient information for classification | Statistical theory - distribution moments encode shape information | May require complex features (SVD spectra, cross-layer correlations) to achieve 70% threshold, weakening contribution |
| A4 | 20 models provide adequate sample size for robust accuracy estimation | Sample size increased from Run 3 (n=5) to Run 4 (n=20) for statistical power | Accuracy estimate may have high variance, limiting generalization confidence |
| A5 | PyTorch torchvision models have standardized training recipes (ImageNet, similar preprocessing) | Common source reduces training recipe variance | Training hyperparameter variance could dominate depth signal, causing spurious classification |

### 1.6 Research Gap & Novelty

**Gap:** While weight-based model compression and transfer learning are established fields, no prior work has demonstrated that architectural depth—a fundamental network property—can be inferred from weight statistics alone without forward passes, activation analysis, or metadata parsing.

**Novelty:**
- **Key Innovation:** First demonstration of weight-statistics-only architectural depth classification, extending weight analysis beyond compression/transfer learning to property inference
- **Methodological Pivot:** From Run 3 correlation analysis (|ρ| = 0.859) to binary classification for larger effect size and clearer validation
- **Practical Impact:** Enables model zoo navigation (1M+ Hugging Face models), mislabel detection, and opens new research direction (what other properties can be weight-fingerprinted?)

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| H-E1 | Existence | MUST_WORK | None | READY |
| H-M1 | Mechanism | MUST_WORK | H-E1 | READY |
| H-M2 | Mechanism | MUST_WORK | H-M1 | READY |
| H-M3 | Mechanism | MUST_WORK | H-M2 | READY |

---

### 2.2 Hypothesis Specifications

---
**H-E1: Weight Distribution Signatures Enable Depth Classification**

**Statement**: Under the scope of pretrained ImageNet CNNs, if we extract layer-wise weight norm statistics (mean, std, min, max of Frobenius norms) and train a binary classifier on 16 models, then test accuracy on 4 held-out models will exceed 70%, because weight distributions encode architectural depth through training history.

**Rationale**: This existence hypothesis validates that weight statistics alone contain sufficient discriminative information for binary depth classification. Success demonstrates that architectural depth leaves measurable fingerprints in weight space, establishing the foundation for all subsequent mechanism tests.

**Variables**:
- Independent: Network Depth Category (binary: shallow ≤34 vs deep ≥50 layers)
- Dependent: Classification Accuracy (test set %, primary metric)
- Controlled: Training Dataset (ImageNet 1K), Feature Extraction (Frobenius norms)

**Verification Protocol**:
1. Load 20 pretrained models from PyTorch torchvision (10 shallow, 10 deep)
2. Extract layer-wise Frobenius norms and compute mean/std/min/max features
3. Split 80/20 (16 train, 4 test) and train sklearn LogisticRegression
4. Evaluate on held-out test set and measure accuracy
5. Compare against 50% random baseline and 70% success threshold

**Success Criteria**:
- Primary: Test accuracy ≥ 70%
- Secondary: P2 within-family accuracy ≥ 65%, P3 random labels ≤ 55%

**Failure Response**:
- IF fails: Accept negative result, document "simple weight norms insufficient," publish or route to Phase 0

**Dependencies**: None (foundation hypothesis)

**Source**: Phase 2A Section 1.6 (P1 Primary Prediction)

---
**H-M1: Gradient Accumulation Creates Depth-Specific Patterns**

**Statement**: Under pretrained CNN training, if gradient transformations accumulate across 50+ layers (deep) versus <34 layers (shallow), then weight magnitude patterns will differ measurably, because backpropagation through more layers creates characteristic gradient flow signatures.

**Rationale**: Tests whether gradient accumulation—the first proposed mechanism—contributes to classification success. Validates theoretical link between depth and weight update histories.

**Variables**:
- Independent: Layer count during training (depth proxy)
- Dependent: Weight magnitude distribution patterns
- Controlled: Architecture family, training dataset

**Verification Protocol**:
1. Analyze layer-wise weight norm progression from input to output layers
2. Compare gradient flow depth (shallow vs deep) using layer-wise statistics
3. Test if randomly initialized models (no training) show same patterns
4. Measure classification accuracy on gradient-related features only

**Success Criteria**:
- Primary: Gradient-based features contribute to classification (accuracy > baseline)
- Secondary: Randomly initialized models fail to classify (accuracy ≤ 55%)

**Failure Response**:
- IF fails: Gradient accumulation not the mechanism, focus on H-M2/H-M3

**Dependencies**: H-E1 must pass

**Source**: Phase 2A Causal Mechanism Step 1

---
**H-M2: Architectural Constraints Create Depth-Specific Structures**

**Statement**: Under pretrained CNN architectures, if residual connections (ResNet), dense connections (DenseNet), and bottleneck layers exist in deep models but not shallow models, then weight structures will exhibit depth-specific patterns, because architectural constraints shape weight organization.

**Rationale**: Tests whether architectural differences (residual/dense connections) contribute to classification. Validates structural hypothesis independent of gradient flow.

**Variables**:
- Independent: Architecture type (ResNet/DenseNet with residual/dense vs VGG without)
- Dependent: Weight structure patterns
- Controlled: Depth category, training dataset

**Verification Protocol**:
1. Compare within-family accuracy (ResNet-only, VGG-only, DenseNet-only)
2. Test if VGG models (no residual connections) still classify correctly
3. Analyze weight norm patterns specific to residual/dense connections
4. Measure architecture-specific feature contributions

**Success Criteria**:
- Primary: Architecture features contribute to classification (within-family ≥ 65%)
- Secondary: VGG classification success validates depth signal over architecture type

**Failure Response**:
- IF fails: Architecture dominates depth signal, scope violation

**Dependencies**: H-M1 (sequential mechanism chain)

**Source**: Phase 2A Causal Mechanism Step 2

---
**H-M3: Normalization Effects Accumulate Differently by Depth**

**Statement**: Under pretrained CNN training with batch normalization, if normalization statistics accumulate across 50+ layers versus <34 layers, then batch norm layer weight distributions will differ, because cumulative normalization effects scale with depth.

**Rationale**: Tests whether batch normalization—the third proposed mechanism—contributes to depth fingerprinting. Completes causal chain validation.

**Variables**:
- Independent: Number of batch norm layers (depth-correlated)
- Dependent: Batch norm weight statistics
- Controlled: Architecture family, training protocol

**Verification Protocol**:
1. Extract statistics from batch normalization layers only
2. Compare batch norm weight distributions (shallow vs deep)
3. Test if models without batch norm (e.g., AlexNet) show different accuracy
4. Measure batch-norm-specific feature contributions

**Success Criteria**:
- Primary: Batch norm features contribute to classification (accuracy improvement)
- Secondary: Models without batch norm provide comparison baseline

**Failure Response**:
- IF fails: Normalization not key mechanism, gradient/architecture dominate

**Dependencies**: H-M2 (sequential mechanism chain)

**Source**: Phase 2A Causal Mechanism Step 3

<!--
Each hypothesis follows this format:

#### {H-ID}: {Title}

**Type:** {EXISTENCE|MECHANISM|CONDITION|COMPARISON}
**Statement:** {Full Under-If-Then-Because statement}

**Variables:**
- IV: {independent variable}
- DV: {dependent variable}
- CV: {controlled variables}

**Success Criteria:**
- {quantitative threshold 1}
- {quantitative threshold 2}

**Gate:**
- Type: {MUST_WORK|SHOULD_WORK|DETERMINES_SUCCESS}
- If Fail: {consequence}

**Prerequisites:** {list or "None"}

**Verification Protocol:** (100-150 words)
{step-by-step protocol}

---
-->

---

## 2.3 Risk Analysis

### Risk-Hypothesis Mapping

| Risk | Source | Affected Hypotheses | Severity | Likelihood |
|------|--------|---------------------|----------|------------|
| R1: Architectural signatures erased | A1 | H-E1, H-M1, H-M2, H-M3 | High | Low |
| R2: Confound dominance (width/training) | A2 | H-E1, H-M1 | High | Medium |
| R3: Simple features insufficient | A3 | H-E1 | Medium | Medium |
| R4: Sample size inadequate | A4 | H-E1 | Medium | Low |
| R5: Training recipe variance | A5 | H-E1, H-M1, H-M2, H-M3 | Medium | Low |

### Mitigation Strategies

**Risk R1: Pretrained Signatures Erased**
- **Prevention**: Use only official PyTorch torchvision models (standardized pretraining, no post-training modifications)
- **Detection**: Check model metadata for fine-tuning history; test on models with known training provenance
- **Response**: If detected, exclude affected models from dataset; document as scope limitation

**Risk R2: Confound Dominance**
- **Prevention**: Multi-family sampling (ResNet, VGG, DenseNet) tests depth signal across varied widths
- **Detection**: P2 within-family validation (if accuracy drops <60%, confound dominates)
- **Response**: PIVOT to confound-aware features or explicitly model width as covariate

**Risk R3: Simple Features Insufficient**
- **Prevention**: Start with simple features (mean/std/min/max) for stronger contribution claim
- **Detection**: Monitor P1 accuracy; if 60-70%, features are marginal
- **Response**: EXPLORE complex features (SVD spectra) but document as weaker contribution

**Risk R4: Sample Size Inadequate**
- **Prevention**: n=20 provides 4:1 train-test ratio with stratification
- **Detection**: High test variance across random splits
- **Response**: Use cross-validation; acknowledge limitation; defer robust claims to future work

**Risk R5: Training Recipe Variance**
- **Prevention**: All models from torchvision (standardized ImageNet training)
- **Detection**: P3 random label control (accuracy >60% suggests spurious patterns)
- **Response**: Document variance source; SCOPE to torchvision-only models

### Risk Summary

| Severity | Count | Risks |
|----------|-------|-------|
| Critical | 0 | None |
| High | 2 | R1 (Low likelihood), R2 (Medium likelihood) |
| Medium | 3 | R3, R4, R5 (All Low-Medium likelihood) |
| Low | 0 | None |

**Overall Risk Profile**: Moderate. Two high-severity risks have low-medium likelihood and clear mitigation paths. All risks have detection mechanisms and response protocols.

---

## 3. Execution

### 3.1 Dependency Chain

```
═══════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) - 4 Hypotheses
═══════════════════════════════════════════════════════════

[Level 0 - Foundation]
    H-E1: Weight Distribution Signatures Enable Depth Classification
         │
         ▼
[Level 1 - Mechanism 1]
    H-M1: Gradient Accumulation Creates Depth-Specific Patterns
         │  (depends on H-E1)
         ▼
[Level 2 - Mechanism 2]
    H-M2: Architectural Constraints Create Depth-Specific Structures
         │  (depends on H-M1)
         ▼
[Level 3 - Mechanism 3]
    H-M3: Normalization Effects Accumulate Differently by Depth
         │  (depends on H-M2)
         ▼
    [Terminal]

═══════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M2 → H-M3 (All sequential)
Parallelization: None (sequential causal chain)
Total Depth: 4 levels
═══════════════════════════════════════════════════════════
```

### 3.1.1 Verification Phases

**Phase 1 - Foundation (H-E1)**
- **Test**: Binary classification achieves ≥70% test accuracy
- **Gate**: MUST_WORK - If fails, entire hypothesis is invalid
- **Pass → Phase 2** | **Fail → STOP, document negative result**

**Phase 2 - Core Mechanisms (H-M1, H-M2, H-M3)**
- **H-M1 Gate**: MUST_WORK - Gradient accumulation must contribute
- **H-M2 Gate**: SHOULD_WORK - Architecture constraints provide evidence
- **H-M3 Gate**: SHOULD_WORK - Normalization completes causal story
- **Pass → Phase 5** | **H-M1 Fail → Investigate alternative mechanisms**

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | Test accuracy ≥ 70% | STOP - Document negative result, publish or route to Phase 0 |
| H-M1 | MUST_WORK | Gradient features contribute (accuracy > baseline) | Investigate alternative mechanisms (architecture/normalization) |
| H-M2 | SHOULD_WORK | Within-family accuracy ≥ 65% | Document as limitation, focus on H-M1/H-M3 |
| H-M3 | SHOULD_WORK | Batch norm features contribute | Document as limitation, gradient/architecture dominate |

### 3.3 Timeline

```
═══════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE - 4 Hypotheses
═══════════════════════════════════════════════════════════════════
Phase/Hypothesis │ W1-2    │ W3      │ W4      │ W5      │
─────────────────┼─────────┼─────────┼─────────┼─────────┤
PHASE 1: Foundation
  H-E1           │ ████████│         │         │         │
  [Gate 1]       │        ◆│         │         │         │
─────────────────┼─────────┼─────────┼─────────┼─────────┤
PHASE 2: Mechanisms
  H-M1           │         │ ████    │         │         │
  H-M2           │         │         │ ████    │         │
  H-M3           │         │         │         │ ████    │
  [Gate 2]       │         │         │         │        ◆│
─────────────────┼─────────┼─────────┼─────────┼─────────┤
═══════════════════════════════════════════════════════════════════
Legend: ████ = Active work | ◆ = Gate decision point
Total Duration: 5 weeks
═══════════════════════════════════════════════════════════════════
```

**Critical Path Analysis:**
- Path: H-E1 → H-M1 → H-M2 → H-M3
- Duration: 2 (H-E1) + 3 (H-M1-3) = 5 weeks
- Slack: 0 weeks (all sequential)

**Execution Order:**
1. Week 1-2: Execute H-E1 (Foundation) → Gate 1
2. Week 3: Execute H-M1 (Gradient accumulation)
3. Week 4: Execute H-M2 (Architectural constraints)
4. Week 5: Execute H-M3 (Normalization effects) → Gate 2
5. Complete: Verification done, ready for Phase 5

**Total Duration:** 5 weeks

---

## 4. Dialectical Analysis

### 4.1 Thesis

**Core Claim:** Weight distribution signatures in pretrained CNNs enable binary depth classification with >70% accuracy.

**Supporting Evidence:**
1. Run 3 demonstrated correlation (|ρ| = 0.859) between weight norms and depth
2. Binary classification amplifies signal through extreme group comparison
3. Three-step causal mechanism: gradient accumulation, architectural constraints, normalization effects

**Strengths:**
- Built on empirical correlation finding from prior experiment
- Clear testable predictions with quantitative thresholds
- Multi-family sampling addresses confound concerns

**Expected Outcomes:**
- Primary: Test accuracy ≥ 70% (P1)
- Secondary: Within-family accuracy ≥ 65% (P2)
- Tertiary: Random labels ≤ 55% (P3)

### 4.2 Antithesis (H0)

**Null Hypothesis:** There is no significant difference in weight distribution statistics between shallow and deep pretrained CNNs sufficient for >70% binary classification accuracy.

**Counter-Arguments:**
1. Simple weight statistics may be insufficient (only mean/std/min/max)
2. Depth signal may be confounded with width, training recipe, architecture family
3. Sample size (n=20) may be inadequate for robust generalization

**Potential Failure Points:**
- R1: Architectural signatures erased by training variance
- R2: Confound dominance (width/training patterns override depth)
- R3: Simple features insufficient, requiring complex features (weakens contribution)

**Conditions Supporting H0:**
- Test accuracy ≤ 60% (below meaningful threshold)
- Random label control shows >60% accuracy (spurious patterns)
- Within-family validation fails (<60%, confound dominance)

### 4.3 Synthesis

**Balanced Assessment:**

The hypothesis H-WeightDepthClassifier-v1 presents a testable claim that weight statistics encode architectural depth through training-induced patterns. However, the null hypothesis raises valid concerns regarding confound correlation and feature sufficiency.

**Resolution Path:**

The verification plan addresses this dialectic through:
1. **Foundation verification (H-E1):** Establishes existence before mechanism investigation
2. **Sequential mechanism testing (H-M1-3):** Tests each causal step independently
3. **Robustness controls:** P2 within-family validation, P3 random label control
4. **Gate conditions:** Allow early detection of H0 support and graceful failure

**Conditions for Thesis Support:**
- H-E1 passes (≥70% accuracy)
- P2 confirms depth signal across families (≥65%)
- P3 validates real signal over artifacts (≤55%)

**Conditions for Antithesis Support:**
- H-E1 fails (≤60% accuracy)
- P3 fails (random labels >60%, spurious patterns)
- P2 fails (<60%, confound dominance)

**Nuanced Outcome Possibilities:**
1. **Full Support:** All gates pass → Weight statistics strongly fingerprint depth
2. **Partial Support:** H-E1 passes, some H-M fail → Depth signal exists but mechanism incomplete
3. **No Support:** H-E1 fails → Accept H0, simple weight norms insufficient

**Overall Robustness:** Medium-High. Hypothesis has clear falsification criteria, controls for confounds, and commits to publishing negative results.

---

## 5. Executive Summary

**Main Hypothesis:** Weight-based binary classification of CNN architectural depth
- ID: H-WeightDepthClassifier-v1, Confidence: 0.75

**Verification Structure:**
- Mode: Incremental (building on Phase 2A)
- Sub-Hypotheses: 4 total (H-E1, H-M1-3)
- Phases: 2 phases over 5 weeks
- Critical Gates: 2 decision points (Foundation, Mechanisms)

**Risk Assessment:** Moderate
- High-severity risks: R1 (signatures erased - low likelihood), R2 (confounds - medium likelihood)
- All risks have clear detection and mitigation strategies

**Key Decision Points:**
1. Gate 1 (Week 2): H-E1 must pass → If fail, STOP
2. Gate 2 (Week 5): H-M1 must pass → If fail, investigate alternatives

**Immediate Action:** Begin Phase 1 (H-E1) - extract features from 20 models, train classifier, evaluate on held-out test set

---

## Appendices

### A. Phase 2A Reference
- Source: `03_refinement.yaml` (H-WeightDepthClassifier-v1)
- Generated: 2026-04-21T05:12:44
- Convergence: All 6 criteria met (SPECIFIC, MECHANISM, PREDICTIONS, NOVELTY, FEASIBILITY, OBJECTIONS)

### B. Hypothesis Execution Summary
- Total: 4 hypotheses (1 existence, 3 mechanism)
- Duration: 5 weeks critical path
- Sequential verification (no parallelization)

---

*Generated by YouRA Phase 2B (Compact v1.0) | 2026-04-21*
