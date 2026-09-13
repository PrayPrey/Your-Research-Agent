# Verification Plan: Cross-Architecture Weight Feature Prediction

**Date:** 2026-08-29
**Hypothesis ID:** H-CrossArchWeightFeatures-v1
**Confidence:** 0.70
**Total Hypotheses:** 4

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement
Under collections of pretrained vision models on Hugging Face Model Hub (ResNet, ViT, ConvNeXt families), if we extract architecture-agnostic weight statistics (heavy-tailed exponent α, mean spectral norm ratio, normalized Frobenius norm) and train a single regression model, then this unified predictor achieves R² at least 0.15 higher than a parameter-count baseline when predicting ImageNet validation accuracy across architecture families, because well-trained models exhibit similar implicit self-regularization signatures (per Martin & Mahoney) regardless of architecture, and these signatures encode generalization quality.

### 1.2 Alternative Hypothesis (H0)
Weight statistics do not improve ImageNet accuracy prediction over a log(parameter_count) regression baseline. The unified regressor trained on weight features achieves R² ≤ baseline R² + 0.15 on held-out architecture families.

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | Hugging Face Model Hub (Vision) (standard) | Provides diverse pretrained models with reported ImageNet accuracy; enables cross-architecture analysis |
| **Model** | MLP Regressor | Simple regressor to isolate effect of weight features; matches Unterthiner et al. approach |

**Dataset Details:**
- Source: https://huggingface.co/models?pipeline_tag=image-classification
- Path: huggingface/hub

**Model Details:**
- Type: regression
- Source: scikit-learn / PyTorch

### 1.4 Baseline Methods (for H-CP* comparison)

| Method | Performance | Dataset |
|--------|-------------|---------|
| Parameter Count Baseline | R² ~ 0.3-0.4 (estimated) | ImageNet models |
| FLOPs Baseline | R² ~ 0.3-0.4 (estimated) | ImageNet models |
| Unterthiner et al. weight predictor | R² ~ 0.6-0.7 within CNN family | CNN model zoo |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | Heavy-tailed weight distributions are universal property of well-trained NNs | Martin & Mahoney's theory is about SGD dynamics | Must use architecture-specific features |
| A2 | HuggingFace ImageNet accuracy is accurate and comparable | Standard benchmark protocol | Need to re-evaluate models ourselves |
| A3 | Weight statistics reflect training quality, not post-hoc modifications | Most HF models are direct training outputs | Quantized/pruned models may confound |
| A4 | Sufficient model diversity exists (100+ per architecture) | HF hosts thousands of vision models | Reduced statistical power |
| A5 | Training procedure variation is not dominant factor | Heavy-tailed theory focuses on final state | Must include training recipe as covariate |

### 1.6 Research Gap & Novelty

**Gap:** Cross-architecture transfer of weight feature predictors has not been validated. Prior work (Unterthiner et al., Martin & Mahoney) focused on CNNs only.

**Novelty:** First systematic evaluation of weight-feature prediction across architecture families (CNN vs Transformer). Demonstrates architecture-invariant weight statistics that predict generalization quality.

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
**H-E1: Heavy-Tailed Exponent Computability for ViT**

**Statement**: Under ViT attention weight matrices, if we apply the Hill estimator to absolute weight values, then heavy-tailed exponents α can be computed with bounded variance (σ < 0.5), because attention weights follow similar statistical distributions as convolutional weights.

**Rationale**: This validates that heavy-tailed theory (developed on CNNs) applies to attention-based architectures. If α cannot be reliably computed for ViTs, the entire cross-architecture prediction approach fails.

**Variables**:
- Independent: Weight matrix type (attention Q/K/V, projection)
- Dependent: Heavy-tailed exponent α, computation variance
- Controlled: Model family (ViT only), ImageNet-trained models

**Verification Protocol**:
1. Download 50+ ViT models from HuggingFace Model Hub
2. Extract attention weight matrices (Q, K, V, projection layers)
3. Compute α via Hill estimator on absolute weight values
4. Calculate variance of α across well-trained models
5. Verify σ(α) < 0.5 threshold

**Success Criteria**:
- Primary: σ(α) < 0.5 across 50+ ViT models
- Secondary: α values fall in expected range [1.5, 4.0]

**Failure Response**:
- IF fails: PIVOT to architecture-specific features

**Dependencies**: None (foundation hypothesis)

**Source**: Phase 2A Prediction P1, SH1

---
**H-M1: Heavy-Tailed Distributions in ViT Training**

**Statement**: Under well-trained ViT models on ImageNet, if training converges successfully, then attention weights develop heavy-tailed distributions, because SGD dynamics produce implicit self-regularization regardless of architecture.

**Rationale**: Tests whether Martin & Mahoney's theoretical framework (developed on CNNs) holds for transformer architectures. This is the first link in the cross-architecture transfer chain.

**Variables**:
- Independent: Training convergence (accuracy > 70%)
- Dependent: Weight distribution tail behavior (α exponent)
- Controlled: ImageNet dataset, standard training protocols

**Verification Protocol**:
1. Filter ViT models by accuracy threshold (>70% ImageNet)
2. Compute heavy-tailed exponents for filtered models
3. Compare α distribution to known CNN ranges
4. Verify distribution match via statistical test

**Success Criteria**:
- Primary: ViT α values overlap with CNN α distribution
- Secondary: Higher accuracy correlates with expected α range

**Failure Response**:
- IF fails: EXPLORE ViT-specific regularization patterns

**Dependencies**: H-E1 (computability verified)

**Source**: Phase 2A Causal Step 1

---
**H-M2: Architecture-Invariant Generalization Signatures**

**Statement**: Under pretrained vision models (ResNet, ViT, ConvNeXt), if we extract weight statistics (α, spectral norm ratio, Frobenius norm), then these features encode generalization quality regardless of architectural substrate, because self-regularization signatures are properties of learning dynamics, not architecture.

**Rationale**: Tests whether weight features are truly architecture-agnostic or architecture-specific. This is the key mechanism enabling cross-architecture transfer.

**Variables**:
- Independent: Weight feature vector (α, spectral ratio, Frobenius norm)
- Dependent: ImageNet validation accuracy correlation
- Controlled: Feature extraction methodology, normalization

**Verification Protocol**:
1. Extract weight features from ResNet, ViT, ConvNeXt models
2. Compute feature-accuracy correlation within each family
3. Compare correlation patterns across families
4. Verify feature importance ranks are consistent

**Success Criteria**:
- Primary: Feature-accuracy correlations similar across architectures
- Secondary: Same features dominate (e.g., α most predictive)

**Failure Response**:
- IF fails: PIVOT to architecture-specific regressors

**Dependencies**: H-M1 (heavy-tailed theory applies to ViT)

**Source**: Phase 2A Causal Step 2

---
**H-M3: Cross-Architecture Regressor Transfer**

**Statement**: Under a regressor trained on ResNet+ConvNeXt weight features, if we apply it to held-out ViT models, then R² improves by at least 0.15 over parameter-count baseline, because the unified feature space captures architecture-invariant generalization information.

**Rationale**: This is the primary experimental test of the core hypothesis. Demonstrates practical value of architecture-invariant weight features for model selection.

**Variables**:
- Independent: Training architecture families (ResNet, ConvNeXt)
- Dependent: Test R² on held-out ViT family
- Controlled: Regressor architecture (MLP), feature set

**Verification Protocol**:
1. Train MLP regressor on ResNet+ConvNeXt features → accuracy
2. Evaluate on held-out ViT models
3. Compare R² to log(param_count) baseline on same test set
4. Compute R² difference and confidence interval

**Success Criteria**:
- Primary: R²(weight_features) - R²(param_count) ≥ 0.15
- Secondary: Top-20% accuracy overlap > 80%

**Failure Response**:
- IF fails: EXPLORE partial transfer or ensemble approaches

**Dependencies**: H-M2 (architecture-invariant features exist)

**Source**: Phase 2A Causal Step 3, Prediction P2

---

## 2.3 Risk Analysis

### Risk-Hypothesis Mapping

| Risk | Source | Description | Severity | Affected Hypotheses |
|------|--------|-------------|----------|---------------------|
| R1 | A1 | Heavy-tailed theory may not apply to attention weights | High | H-E1, H-M1 |
| R2 | A2 | HuggingFace accuracy metadata inconsistent | Medium | H-M3 |
| R3 | A3 | Quantized/pruned models confound weight statistics | Medium | H-M1, H-M2 |
| R4 | A4 | Insufficient model diversity (<100 per family) | Medium | H-M2, H-M3 |
| R5 | A5 | Training procedure variation dominates features | High | All |

### Mitigation Strategies

**R1 (High): Heavy-tailed theory inapplicable to attention**
- Prevention: Validate on small ViT sample first
- Detection: α variance > 0.5 or computation failures > 20%
- Response: PIVOT to architecture-specific features; document as negative result

**R2 (Medium): Accuracy metadata inconsistency**
- Prevention: Cross-check reported accuracy with model card details
- Detection: Large outliers in accuracy-feature correlation
- Response: Filter models without verified evaluation; reduce sample if needed

**R3 (Medium): Confounded weight statistics**
- Prevention: Filter quantized/pruned/distilled models via model card tags
- Detection: Bimodal distributions in weight features
- Response: Exclude confounded models; note reduced sample size

**R4 (Medium): Insufficient model diversity**
- Prevention: Survey HuggingFace before committing; set minimum threshold
- Detection: <50 models per architecture family
- Response: SCOPE to well-represented families; add DeiT/Swin as alternatives

**R5 (High): Training procedure dominates**
- Prevention: Include training recipe metadata as covariate where available
- Detection: Training recipe explains more variance than weight features
- Response: EXPLORE training-aware features; document confound

---

## 3. Execution

### 3.1 Dependency Graph (DAG)

```
═══════════════════════════════════════════════════════════
DEPENDENCY GRAPH - 4 Hypotheses (Sequential)
═══════════════════════════════════════════════════════════

[Level 0 - Foundation]
    ┌─────────────────────────────────┐
    │  H-E1: ViT α Computability      │
    │  Gate: MUST_WORK                │
    └───────────────┬─────────────────┘
                    │
                    ▼
[Level 1 - Mechanism Step 1]
    ┌─────────────────────────────────┐
    │  H-M1: Heavy-Tailed in ViT      │
    │  Gate: MUST_WORK                │
    └───────────────┬─────────────────┘
                    │
                    ▼
[Level 2 - Mechanism Step 2]
    ┌─────────────────────────────────┐
    │  H-M2: Arch-Invariant Features  │
    │  Gate: MUST_WORK                │
    └───────────────┬─────────────────┘
                    │
                    ▼
[Level 3 - Mechanism Step 3]
    ┌─────────────────────────────────┐
    │  H-M3: Cross-Arch Transfer      │
    │  Gate: MUST_WORK                │
    └─────────────────────────────────┘

═══════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M2 → H-M3
Path Length: 4 hypotheses (all sequential, no parallelization)
═══════════════════════════════════════════════════════════
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | σ(α) < 0.5 for 50+ ViT models | STOP: Cannot proceed without computable features |
| H-M1 | MUST_WORK | ViT α overlaps with CNN α distribution | PIVOT: Use architecture-specific features |
| H-M2 | MUST_WORK | Correlations similar across architectures | PIVOT: Architecture-specific regressors |
| H-M3 | MUST_WORK | R² improvement ≥ 0.15 over baseline | Document as negative result; explore partial transfer |

### 3.3 Dependency Hierarchy

| Level | Hypothesis | Prerequisites | Phase |
|-------|-----------|---------------|-------|
| 0 | H-E1 | None | Foundation |
| 1 | H-M1 | H-E1 | Mechanism |
| 2 | H-M2 | H-M1 | Mechanism |
| 3 | H-M3 | H-M2 | Mechanism |

### 3.4 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 1: Foundation | H-E1 | 1-2 days |
| Phase 2: Mechanism | H-M1, H-M2, H-M3 | 3-5 days |

**Total Duration:** 4-7 days (PoC verification)

### 3.5 Gantt Timeline

```
═══════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE - 4 Hypotheses
═══════════════════════════════════════════════════════════════════
Phase/Hypothesis      │ Day 1-2  │ Day 3-4  │ Day 5-6  │ Day 7   │
──────────────────────┼──────────┼──────────┼──────────┼─────────┤
PHASE 1: Foundation   │          │          │          │         │
  H-E1 (Existence)    │ ████████ │          │          │         │
  [Gate 1]            │        ◆ │          │          │         │
──────────────────────┼──────────┼──────────┼──────────┼─────────┤
PHASE 2: Mechanism    │          │          │          │         │
  H-M1 (ViT Theory)   │          │ ████████ │          │         │
  H-M2 (Invariance)   │          │          │ ████     │         │
  H-M3 (Transfer)     │          │          │     ████ │ ██      │
  [Gate 2]            │          │          │          │   ◆     │
═══════════════════════════════════════════════════════════════════
Legend: ████ = Active work  |  ◆ = Gate decision point
Critical Path: H-E1 → H-M1 → H-M2 → H-M3 (no parallelization)
═══════════════════════════════════════════════════════════════════
```

### 3.6 Execution Order

1. **Day 1-2**: Execute H-E1 (compute α for 50+ ViT models)
2. **Gate 1**: If σ(α) < 0.5, proceed; else STOP
3. **Day 3-4**: Execute H-M1 (compare ViT α to CNN distribution)
4. **Day 5-6**: Execute H-M2 (test feature-accuracy correlation across families)
5. **Day 6-7**: Execute H-M3 (train regressor, test cross-architecture transfer)
6. **Gate 2**: If R² improvement ≥ 0.15, SUCCESS; else document negative result

---

## 4. Dialectical Analysis

### 4.1 Thesis

**Core Claim:** Architecture-agnostic weight statistics (heavy-tailed exponent, spectral norm ratio, Frobenius norm) encode generalization quality and enable cross-architecture accuracy prediction.

**Supporting Evidence:**
1. Martin & Mahoney (2021) established theoretical framework for heavy-tailed weight distributions in CNNs
2. Unterthiner et al. (2020) demonstrated weight statistics predict accuracy within CNN family (R² ~ 0.6-0.7)
3. SGD dynamics theory is architecture-agnostic (learning dynamics, not architecture-specific)

**Strengths:**
- Grounded in established statistical physics theory
- Clear causal mechanism from training dynamics to weight statistics
- Testable predictions with quantitative thresholds

### 4.2 Antithesis

**Null Hypothesis (H0):** Weight statistics do not improve ImageNet accuracy prediction over a log(parameter_count) regression baseline. The unified regressor achieves R² ≤ baseline R² + 0.15 on held-out architecture families.

**Counter-Arguments:**
1. Attention mechanisms may have fundamentally different weight dynamics than convolutions
2. Heavy-tailed theory was validated only on older CNN architectures, not modern transformers
3. Cross-architecture feature spaces may be incomparable despite similar statistics

**Conditions Under Which H0 Would Be Supported:**
- Heavy-tailed exponents cannot be computed reliably for ViT (H-E1 fails)
- ViT weight distributions differ substantially from CNNs (H-M1 fails)
- Feature-accuracy correlations are architecture-specific (H-M2 fails)
- Cross-architecture R² improvement < 0.15 (H-M3 fails)

### 4.3 Synthesis

The hypothesis presents a testable claim about architecture-invariant weight features. The null hypothesis raises valid concerns about transformer-CNN comparability.

**Resolution Path:**
1. H-E1 tests computability: If α cannot be computed for ViTs, thesis fails at foundation
2. H-M1 tests theory validity: If ViTs don't exhibit heavy-tailed distributions, mechanism fails
3. H-M2 tests invariance: If correlations differ across architectures, unified features invalid
4. H-M3 tests transfer: Direct test of core claim with quantitative threshold

**Nuanced Outcome Possibilities:**
- **Full Support:** All gates pass → Cross-architecture prediction validated
- **Partial Support:** H-M3 shows smaller improvement (0.05-0.15) → Limited transfer, architecture-aware features may help
- **No Support:** H-E1 or H-M1 fails → Fundamental difference between architectures; document as negative result

### 4.4 Robustness Assessment

| Aspect | Thesis Position | Antithesis Challenge | Resolution |
|--------|-----------------|----------------------|------------|
| Existence | Heavy-tailed exponents computable for ViT | May fail for attention weights | H-E1: σ(α) < 0.5 test |
| Mechanism | SGD produces similar signatures across archs | Attention dynamics differ | H-M1: Distribution comparison |
| Invariance | Weight features are architecture-agnostic | Architecture-specific confounds | H-M2: Correlation consistency |
| Transfer | Unified regressor transfers | No cross-architecture benefit | H-M3: R² ≥ 0.15 threshold |

**Overall Robustness Score:** Medium (strong theory, but ViT validation is novel)

**Confidence in Verification Plan:** 0.70

---

## 5. Executive Summary

**Main Hypothesis:** Cross-architecture weight features predict ImageNet accuracy
- ID: H-CrossArchWeightFeatures-v1, Confidence: 0.70

**Verification Structure:**
- Mode: Incremental (Phase 2A available)
- Sub-Hypotheses: 4 total (H-E: 1, H-M: 3)
- Phases: 2 phases over 4-7 days
- Critical Gates: 2 decision points

**Risk Assessment:** Medium
- Primary concerns: Heavy-tailed theory may not apply to attention (R1), training procedure confounds (R5)

**Immediate Action:** Begin Phase 1 with H-E1 (ViT α computability)

---

## 6. Conclusions

### 6.1 Key Achievements
- 4 hypotheses across 2 phases testing cross-architecture weight feature prediction
- H0 directly addressed: "R² improvement ≥ 0.15" is falsifiable threshold

### 6.2 Verification Execution Order

**Phase 1: Foundation** (1-2 days)
- H-E1: Validate heavy-tailed exponent computability for ViT
- Gate 1: σ(α) < 0.5 MUST PASS

**Phase 2: Core Mechanisms** (3-5 days)
- H-M1: ViT weights exhibit heavy-tailed distributions
- H-M2: Weight features are architecture-invariant
- H-M3: Cross-architecture regressor achieves R² ≥ baseline + 0.15
- Gate 2: H-M3 determines success

### 6.3 Critical Decision Points

1. **Gate 1 (Foundation):** H-E1 must pass
   - FAIL → STOP: Cannot compute features for ViT
   - PASS → Proceed to Phase 2

2. **Gate 2 (Transfer):** H-M3 determines success
   - R² ≥ 0.15 → SUCCESS: Cross-architecture prediction validated
   - R² < 0.15 → Document as negative result; explore partial transfer

### 6.4 Open Questions
- What is the actual R² of the unified predictor?
- Do specific weight features dominate (heavy-tailed vs spectral vs Frobenius)?
- Does training procedure variation confound results?

### 6.5 Recommendations

1. **Immediate Actions:**
   - Survey HuggingFace for model counts per architecture family
   - Set up weight feature extraction pipeline

2. **Resource Allocation:**
   - Allocate 4-7 days for critical path
   - Reserve 2 additional days for failure analysis

3. **Failure Management:**
   - H-E1 fail: PIVOT to architecture-specific features
   - H-M3 partial: Explore ensemble or hybrid approaches

---

## Appendices

### A. Phase 2A Reference
- **Source:** 03_refinement.yaml (ID: H-CrossArchWeightFeatures-v1)
- **Schema:** v10.0.0 (Free-parse, Phase 2B-compatible)

### B. Scope Reduction
- BUILD_ON claims (50%): CNN prediction, heavy-tailed theory
- PROVE_NEW claims (50%): Cross-architecture transfer, ViT validation

---
