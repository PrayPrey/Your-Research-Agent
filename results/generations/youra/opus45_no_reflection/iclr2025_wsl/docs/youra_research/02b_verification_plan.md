# Verification Plan: Behavioral Fingerprinting via Weight-Space Neural Functionals

**Date:** 2026-08-19
**Hypothesis ID:** H-BehavioralFingerprint-v1
**Confidence:** 0.75
**Total Hypotheses:** 5

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement
Under the scope of CNN model zoos (Small CNN Zoo, CIFAR-10),
if we train a permutation-equivariant neural functional (NF-Layer) to predict class-wise accuracy profiles from weights,
then the learned behavioral embedding will (1) explain ≥5% more variance in class-wise accuracy than a stratified baseline AND (2) correlate with confusion matrix similarity (r ≥ 0.30) despite never being trained on confusion matrices,
because NF-Layers capture functionally salient weight directions (per Meynent et al.'s Jacobian-alignment analysis) that scalar predictions miss.

### 1.2 Alternative Hypothesis (H0)
Class-wise accuracy profiles are fully predictable from overall accuracy + class baseline difficulty.
NF-Layer behavioral embeddings add no additional explanatory power beyond this stratified baseline.

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | Small CNN Zoo (CIFAR-10 subset) (standard) | Contains ~3000 models with stored predictions, enabling confusion matrix computation without new evaluation |
| **Model** | NF-Layer Neural Functional | Designed for processing CNN weights equivariantly; proven characterization theorem ensures completeness |

**Dataset Details:**
- Source: github.com/HSG-AIML/model_zoos
- Path: model_zoos/CIFAR10_small_cnn/

**Model Details:**
- Type: permutation-equivariant neural functional
- Source: github.com/AllanYangZhou/nfn (MIT license)

### 1.4 Baseline Methods (for Phase 5 comparison)

| Method | Performance | Dataset |
|--------|-------------|---------|
| SANE embeddings + linear probe | R² > 0.9 for accuracy on MNIST/SVHN small CNNs | Small CNN Zoo |
| Weight statistics (Unterthiner et al. 2020) | R² ~0.97 for accuracy on small models | Small CNN Zoo |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | Class-wise accuracy profiles vary meaningfully across models in the zoo | Model zoos contain hyperparameter and seed variation; different models should fail on different classes | If all models fail/succeed on same classes, behavioral prediction collapses to accuracy prediction |
| A2 | NF-Layer architecture scales to Small CNN Zoo model sizes (~12k parameters) | Zhou et al. (2023) demonstrate NF-Layers on CNNs with similar parameter counts | Would need architecture modification; computational feasibility at risk |
| A3 | Confusion matrices are derivable from stored evaluation data in model zoos | Model zoos store per-model predictions; confusion matrices = predictions × ground truth | Would need to re-evaluate models, violating no-new-data constraint |
| A4 | 16-dim embedding is sufficient to capture behavioral structure | Herrmann et al. (2024) use 16-dim embeddings for RNN behavior encoding | May need larger embedding; hyperparameter search required |
| A5 | Behavioral transfer (accuracy → confusion) is meaningful measure of generalization | Confusion matrices capture error patterns not reducible to accuracy; correlation indicates shared structure | Alternative transfer metrics needed (CKA, sample agreement) |

### 1.6 Research Gap & Novelty

**Gap:** Prior work (SANE, Zhou et al. NF-Layers) predicts scalar properties from weights. No method predicts structured behavioral profiles with cross-metric transfer validation.

**Novelty:** First structured behavioral prediction from weights with cross-metric transfer validation. Shift from scalar property prediction (accuracy) to behavioral profile prediction (class-wise accuracy) with transfer to confusion matrices.

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| H-E1 | Existence | MUST_WORK | None | READY |
| H-M1 | Mechanism | MUST_WORK | H-E1 | NOT_STARTED |
| H-M2 | Mechanism | SHOULD_WORK | H-M1 | NOT_STARTED |
| H-M3 | Mechanism | SHOULD_WORK | H-M2 | NOT_STARTED |
| H-M4 | Mechanism | SHOULD_WORK | H-M3 | NOT_STARTED |

---

### 2.2 Hypothesis Specifications

---
**H-E1: Behavioral Information Exists Beyond Accuracy**

**Statement**: Under CNN model zoo scope, if we analyze class-wise accuracy profiles across models, then variance beyond overall accuracy will be observed, because different models encode different behavioral patterns in their weights.

**Rationale**: Establishes that the phenomenon to be predicted actually exists. Without meaningful variance in class-wise profiles, behavioral prediction reduces to accuracy prediction.

**Variables**:
- Independent: Model identity (different hyperparameters/seeds)
- Dependent: Class-wise accuracy profile variance
- Controlled: Architecture (fixed CNN), Dataset (CIFAR-10)

**Verification Protocol**:
1. Load Small CNN Zoo (~3000 models) stored predictions
2. Compute class-wise accuracy profiles for each model
3. Calculate variance explained by overall accuracy vs. residual per-class variance
4. Test: residual variance > 5% of total variance

**Success Criteria (PoC)**:
- Primary: Class-wise variance NOT fully explained by overall accuracy
- Secondary: Different models show different per-class error patterns

**Failure Response**:
- IF fails: STOP - behavioral prediction meaningless if no behavioral variance exists

**Dependencies**: None

**Source**: Phase 2A SH1, Prediction P1

---

**H-M1: Weight Matrices Encode Behavioral Information**

**Statement**: Under Small CNN Zoo scope, if we extract features from weight matrices, then these features will correlate with class-wise accuracy profiles, because weights encode functionally salient directions per Meynent et al.

**Rationale**: Tests first causal step: weights contain behavioral information extractable by any method, not just NF-Layers.

**Variables**:
- Independent: Weight feature extraction method
- Dependent: Correlation with class-wise accuracy
- Controlled: Model architecture, dataset

**Verification Protocol**:
1. Extract basic weight statistics (mean, std, norms per layer)
2. Train linear probe to predict class-wise accuracy from weight features
3. Compare R² against stratified baseline (overall accuracy + per-class difficulty)
4. Test: R² > stratified baseline R²

**Success Criteria (PoC)**:
- Primary: Weight features predict class-wise accuracy better than stratified baseline
- Secondary: Multiple weight statistics contribute to prediction

**Failure Response**:
- IF fails: PIVOT to alternative feature extraction

**Dependencies**: H-E1

**Source**: Phase 2A Causal Step 1

---

**H-M2: NF-Layer Cross-Layer Aggregation Captures Behavioral Structure**

**Statement**: Under Small CNN Zoo scope, if we use full NF-Layer (with cross-layer terms) vs pointwise NF-Layer, then full NF-Layer will predict class-wise accuracy better, because cross-layer correlations encode behavioral interactions.

**Rationale**: Tests whether NF-Layer's equivariant structure adds value over simpler approaches.

**Variables**:
- Independent: NF-Layer architecture (full vs pointwise ablation)
- Dependent: Class-wise accuracy R²
- Controlled: Embedding dimension (16), training procedure

**Verification Protocol**:
1. Train full NF-Layer (all terms in Zhou et al. Eq. 2) on class-wise accuracy
2. Train pointwise NF-Layer (d_i W_jk only) with same setup
3. Compare R² on held-out test set
4. Statistical test: paired t-test across 10-fold CV

**Success Criteria (PoC)**:
- Primary: Full NF-Layer R² > Pointwise NF-Layer R² (p < 0.05)
- Secondary: Cross-layer terms contribute significant coefficients

**Failure Response**:
- IF fails: Document limitation - pointwise sufficient

**Dependencies**: H-M1

**Source**: Phase 2A Causal Step 2

---

**H-M3: Embedding Bottleneck Forces Shared Behavioral Factors**

**Statement**: Under 16-dim embedding constraint, if the bottleneck forces compression, then embedding will capture shared factors transferable across metrics, because redundant behavioral information is compressed out.

**Rationale**: Tests whether dimensionality reduction produces generalizable representation.

**Variables**:
- Independent: Embedding dimension (8, 16, 32, 64)
- Dependent: Class-wise R² and transfer correlation
- Controlled: NF-Layer architecture, training procedure

**Verification Protocol**:
1. Train NF-Layer with varying embedding dimensions
2. Evaluate class-wise R² for each dimension
3. Compute confusion similarity correlation for each
4. Identify optimal dimension balancing both metrics

**Success Criteria (PoC)**:
- Primary: 16-dim achieves within 5% of best R²
- Secondary: Smaller dimensions show transfer (not just overfitting)

**Failure Response**:
- IF fails: Adjust embedding dimension based on results

**Dependencies**: H-M2

**Source**: Phase 2A Causal Step 3

---

**H-M4: Behavioral Factors Transfer to Unseen Metrics**

**Statement**: Under behavioral embedding scope, if embeddings capture general functional saliency, then embedding distance will correlate with confusion matrix similarity, because shared behavioral structure underlies both metrics.

**Rationale**: This is the key novelty test - transfer beyond training objective.

**Variables**:
- Independent: Embedding distance between model pairs
- Dependent: Confusion matrix cosine similarity
- Controlled: Models never trained on confusion similarity

**Verification Protocol**:
1. Train NF-Layer on class-wise accuracy (never sees confusion matrices)
2. Compute pairwise embedding distances for all models
3. Compute pairwise confusion matrix cosine similarities
4. Calculate Pearson correlation r between distances and similarities

**Success Criteria (PoC)**:
- Primary: r ≥ 0.30 with p < 0.01
- Secondary: Correlation remains significant in held-out hyperparameter configs

**Failure Response**:
- IF fails: Try alternative transfer metrics (CKA, sample agreement)

**Dependencies**: H-M3

**Source**: Phase 2A Causal Step 4, Prediction P2

---

## 3. Risk Analysis

### 3.1 Risk Identification

| Risk | Source | Description | Severity |
|------|--------|-------------|----------|
| R1 | A1 | No meaningful class-wise variance in model zoo | Critical |
| R2 | A2 | NF-Layer doesn't scale to Small CNN Zoo models | High |
| R3 | A3 | Cannot derive confusion matrices from stored data | High |
| R4 | A4 | 16-dim embedding insufficient | Medium |
| R5 | A5 | Confusion transfer not meaningful | Medium |

### 3.2 Risk-Hypothesis Mapping

| Risk | Affected Hypotheses | Impact |
|------|---------------------|--------|
| R1 | H-E1, All | Entire hypothesis invalid |
| R2 | H-M1, H-M2 | Cannot test NF-Layer mechanism |
| R3 | H-M4 | Cannot test transfer |
| R4 | H-M3 | Need dimension search |
| R5 | H-M4 | Need alternative transfer metrics |

### 3.3 Mitigation Strategies

**R1 (Critical): No class-wise variance**
- Prevention: Preliminary variance analysis before full experiment
- Detection: Check variance in first 100 models
- Response: STOP if variance < 5% - hypothesis fundamentally flawed

**R2 (High): Scaling issues**
- Prevention: Test NF-Layer on subset first
- Detection: Monitor memory/compute during training
- Response: PIVOT to smaller architecture or mixed-precision

**R3 (High): Cannot derive confusion matrices**
- Prevention: Verify stored prediction format early
- Detection: Attempt derivation on 10 models first
- Response: SCOPE to class-wise accuracy only (lose transfer validation)

**R4 (Medium): Embedding dimension**
- Prevention: Plan dimension sweep from start
- Detection: Compare 8/16/32/64 dimensions
- Response: Use optimal dimension, document sensitivity

**R5 (Medium): Transfer not meaningful**
- Prevention: Define multiple transfer metrics upfront
- Detection: Test CKA and sample agreement alongside confusion
- Response: Report all transfer metrics, discuss validity

### 3.4 Risk Summary

| ID | Risk | Severity | Likelihood | Mitigation |
|----|------|----------|------------|------------|
| R1 | No variance | Critical | Low | Early variance check |
| R2 | Scaling | High | Low | Subset test |
| R3 | No confusion | High | Low | Format verification |
| R4 | Dimension | Medium | Medium | Dimension sweep |
| R5 | Transfer validity | Medium | Medium | Multiple metrics |

**Critical Risks:** 1
**High Risks:** 2
**Medium Risks:** 2

---

## 4. Dependency Graph

### 4.1 DAG Visualization

```
═══════════════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) - 5 Hypotheses
═══════════════════════════════════════════════════════════════════

[Level 0 - Foundation]
    ┌─────────────────────────────────────┐
    │  H-E1: Behavioral Variance Exists   │
    │  Gate: MUST_WORK                    │
    └─────────────────────────────────────┘
                      │
                      ▼ [Gate 1]
[Level 1 - Mechanism Start]
    ┌─────────────────────────────────────┐
    │  H-M1: Weights Encode Behavior      │
    │  Gate: MUST_WORK                    │
    └─────────────────────────────────────┘
                      │
                      ▼
[Level 2 - Core Mechanism]
    ┌─────────────────────────────────────┐
    │  H-M2: Cross-Layer Aggregation      │
    │  Gate: SHOULD_WORK                  │
    └─────────────────────────────────────┘
                      │
                      ▼
[Level 3 - Compression]
    ┌─────────────────────────────────────┐
    │  H-M3: Embedding Bottleneck         │
    │  Gate: SHOULD_WORK                  │
    └─────────────────────────────────────┘
                      │
                      ▼
[Level 4 - Transfer]
    ┌─────────────────────────────────────┐
    │  H-M4: Cross-Metric Transfer        │
    │  Gate: SHOULD_WORK                  │
    └─────────────────────────────────────┘
                      │
                      ▼ [Gate 2]
                 [COMPLETE]

═══════════════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M2 → H-M3 → H-M4
═══════════════════════════════════════════════════════════════════
```

### 4.2 Dependency Hierarchy

| Level | Hypothesis | Prerequisites | Gate Type |
|-------|------------|---------------|-----------|
| 0 | H-E1 | None | MUST_WORK |
| 1 | H-M1 | H-E1 | MUST_WORK |
| 2 | H-M2 | H-M1 | SHOULD_WORK |
| 3 | H-M3 | H-M2 | SHOULD_WORK |
| 4 | H-M4 | H-M3 | SHOULD_WORK |

---

## 5. Timeline & Execution

### 5.1 Gantt Timeline

```
═══════════════════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE - 5 Hypotheses
═══════════════════════════════════════════════════════════════════════════════
Phase/Hypothesis      │ W1-2    │ W3-4    │ W5      │ W6      │ W7      │
──────────────────────┼─────────┼─────────┼─────────┼─────────┼─────────┤
PHASE 1: Foundation   │         │         │         │         │         │
  H-E1 (Existence)    │ ████████│         │         │         │         │
  [Gate 1]            │        ◆│         │         │         │         │
──────────────────────┼─────────┼─────────┼─────────┼─────────┼─────────┤
PHASE 2: Mechanisms   │         │         │         │         │         │
  H-M1 (Encoding)     │         │ ████████│         │         │         │
  H-M2 (Cross-Layer)  │         │         │ ████    │         │         │
  H-M3 (Bottleneck)   │         │         │         │ ████    │         │
  H-M4 (Transfer)     │         │         │         │         │ ████    │
  [Gate 2]            │         │         │         │         │    ◆    │
══════════════════════════════════════════════════════════════════════════════
Legend: ████ = Active work │ ◆ = Gate decision point
Total Duration: 7 weeks
═══════════════════════════════════════════════════════════════════════════════
```

### 5.2 Critical Path Analysis

**Critical Path:** H-E1 → H-M1 → H-M2 → H-M3 → H-M4

**Total Duration:** 7 weeks
- Formula: 2 (H-E1) + 2 (H-M1) + 1 (H-M2) + 1 (H-M3) + 1 (H-M4)

**Slack Available:** 0 weeks (all sequential)

### 5.3 Resource Summary

| Resource | Allocation |
|----------|------------|
| Total Hypotheses | 5 |
| Existence | 1 (H-E1) |
| Mechanism | 4 (H-M1 to H-M4) |
| Phases | 2 |
| Duration | 7 weeks |
| Execution Mode | Sequential chain |

### 5.4 Execution Order

1. **Week 1-2**: Execute H-E1 (Foundation)
2. **Week 2**: Evaluate Gate 1 → If pass, proceed
3. **Week 3-4**: Execute H-M1 (Weight encoding)
4. **Week 5**: Execute H-M2 (Cross-layer ablation)
5. **Week 6**: Execute H-M3 (Embedding dimension)
6. **Week 7**: Execute H-M4 (Transfer validation)
7. **Week 7**: Evaluate Gate 2 → Verification complete

---

## 6. Dialectical Analysis

### 6.1 Overview

The hypothesis undergoes thesis-antithesis-synthesis evaluation to ensure robust verification design.

### 6.2 Thesis

**Core Claim:** NF-Layer behavioral embeddings can predict structured behavioral profiles from weights with cross-metric transfer.

**Supporting Evidence:**
1. NF-Layers capture functionally salient weight directions via equivariant aggregation (Zhou et al. 2023)
2. Behavioral information beyond accuracy exists in weight matrices (Meynent et al. 2025)
3. Low-dimensional embedding bottleneck forces compression to shared behavioral factors
4. Cross-layer terms capture behaviorally relevant weight interactions

**Strengths:**
- Built on established NF-Layer theory
- Clear quantified success criteria (ΔR² > 0.05, r ≥ 0.30)
- Cross-metric transfer breaks circularity concern
- All data and code already available

**Expected Outcomes:**
- P1: ΔR² > 0.05 over stratified baseline (p < 0.05)
- P2: Confusion similarity correlation r ≥ 0.30 (p < 0.01)
- P3: Full NF-Layer > Pointwise NF-Layer (p < 0.05)

### 6.3 Antithesis

**Null Hypothesis (H0):** Class-wise accuracy profiles are fully predictable from overall accuracy + per-class baseline difficulty. NF-Layer behavioral embeddings add no additional explanatory power beyond this stratified baseline.

**Counter-Arguments:**
1. Per-class difficulty is stable across models (some classes are inherently harder)
2. Overall accuracy strongly correlates with per-class accuracy
3. Prior work achieves R² > 0.9 for scalar accuracy without behavioral structure
4. Behavioral structure may be epiphenomenal, not causally linked to weights

**Conditions Under Which H0 Would Be Supported:**
- If ΔR² ≤ 0.05 (no improvement over stratified baseline)
- If confusion correlation r < 0.30 (no transfer)
- If pointwise NF-Layer equals full NF-Layer (cross-layer terms useless)

### 6.4 Synthesis

**Balanced Assessment:**

The hypothesis H-BehavioralFingerprint-v1 presents a testable claim that NF-Layers can extract structured behavioral information from weights. However, the null hypothesis raises valid concerns regarding whether this structure is merely an artifact of overall accuracy correlations.

**Resolution Path:**

The verification plan resolves this dialectic through:
1. **Foundation verification (H-E1):** Establishes existence before mechanism
2. **Sequential mechanism testing (H-M1-4):** Tests causal chain step-by-step
3. **Gate conditions:** Allow early detection of H0 support

**Conditions for Thesis Support:**
- All MUST_WORK gates pass (H-E1, H-M1)
- P1 confirmed (ΔR² > 0.05)
- P2 confirmed (r ≥ 0.30)

**Conditions for Antithesis Support:**
- H-E1 fails (no behavioral variance)
- H-M1 fails (weights don't encode behavior)
- P1 and P2 both fail

**Nuanced Outcome Possibilities:**
1. **Full Support:** All hypotheses pass → Thesis validated
2. **Partial Support:** H-M4 fails → Behavioral encoding works but doesn't transfer
3. **No Support:** H-E1 or H-M1 fail → Antithesis supported

### 6.5 Robustness Assessment

| Aspect | Thesis Position | Antithesis Challenge | Resolution |
|--------|-----------------|----------------------|------------|
| Existence | Behavioral variance exists | May be artifact of accuracy | H-E1 test with residual variance |
| Mechanism | NF-Layer captures structure | Simpler methods sufficient | H-M2 ablation |
| Transfer | Embeddings generalize | Overfitting to accuracy | H-M4 confusion transfer |
| Performance | Outperforms baselines | Marginal improvement | Quantified criteria |

**Overall Robustness Score:** High

**Confidence in Verification Plan:** 0.75

---

## 7. Summary & Conclusions

### 7.1 Executive Summary

**Main Hypothesis:** Behavioral Fingerprinting via Weight-Space Neural Functionals
- ID: H-BehavioralFingerprint-v1, Confidence: 0.75

**Verification Structure:**
- Mode: Incremental (Phase 2A available)
- Sub-Hypotheses: 5 total (H-E: 1, H-M: 4)
- Phases: 2 phases over 7 weeks
- Critical Gates: 2 decision points

**Risk Assessment:** Medium
- Primary concerns: R1 (no variance), R2 (scaling)

**Immediate Action:** Begin Phase 1 with H-E1

### 7.2 Final Summary

**Key Achievements:**
- 5 hypotheses across 2 phases with clear verification protocols
- H0 addressed through stratified baseline comparison
- Scope reduction: 80% (BUILD_ON claims not re-verified)

### 7.3 Conclusions

**Verification Execution Order:**

**Phase 1: Foundation** (2 weeks)
- H-E1: Behavioral variance exists in class-wise profiles
- Gate 1: MUST PASS → Stop if fails

**Phase 2: Core Mechanisms** (5 weeks)
- H-M1: Weights encode behavioral information
- H-M2: Cross-layer aggregation adds value
- H-M3: Embedding bottleneck forces generalization
- H-M4: Transfer to confusion matrices
- Gate 2: H-M1 must pass; later failures narrow scope

**Critical Decision Points:**
1. Gate 1: H-E1 failure → STOP, reassess hypothesis
2. Gate 2: H-M1 failure → STOP; H-M2-4 failures → document limitations

**Open Questions:**
- Optimal embedding dimension (16 vs. 8/32/64)
- Whether confusion transfer metric is sufficient or CKA needed
- Computational cost of NF-Layer training on full zoo

**Recommendations:**
1. Start Phase 1 immediately with variance analysis
2. Set up NF-Layer training infrastructure in parallel
3. Prepare fallback transfer metrics (CKA, sample agreement)

### 7.4 Appendices

**A. Phase 2A Reference**
- Source: 03_refinement.yaml (H-BehavioralFingerprint-v1)
- Causal Chain: 4 steps
- Scope Reduction: 80%

**B. MCP Tool Usage**
- scientificmethod: 2 calls (H-E1, H-M integrated)
- structuredargumentation: 3 calls (thesis, antithesis, synthesis)

---

## 8. Finalization

### 8.1 Verification State

**Status:** verification_state.yaml generated with 5 sub-hypotheses

### 8.2 Pipeline Tasks

**Phase 2B:** Marked complete
**Phase 2C:** Ready to start

### 8.3 Hypothesis Tasks

Created 5 hypothesis tasks in Archon pipeline project:
- H-E1: Existence hypothesis
- H-M1: Mechanism step 1
- H-M2: Mechanism step 2
- H-M3: Mechanism step 3
- H-M4: Mechanism step 4 (Transfer)
