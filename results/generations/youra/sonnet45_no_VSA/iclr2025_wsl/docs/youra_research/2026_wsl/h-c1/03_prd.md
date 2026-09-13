# Product Requirements Document: H-C1 Edge Case Robustness Validation

**Hypothesis ID:** h-c1  
**Type:** CONDITION (SHOULD_WORK gate)  
**Date:** 2026-07-11  
**Version:** 1.0  
**Prerequisites:** h-m3 (Checkpoint-only extraction validated)

---

## 1. Executive Summary

### 1.1 Problem Statement

The statistical feature extraction approach (h-m3) validates successfully on standard architectures (CNN, Transformer, Hybrid). However, edge case architectures (NormFree networks, extreme scaling, non-standard attention) may violate core assumptions:
- **A2 Violation:** NormFree architectures (NFNet) replace BatchNorm with weight standardization → `bn_count = 0`
- **Extreme Scale:** ViT-Giant/Huge models test scale-invariance of parameter-mass ratio R
- **Non-standard Patterns:** Squeeze-Excitation (SENet) adds extra linear layers → R variance
- **Depth Scaling:** RegNet extreme depth inflates norm layer counts

**Critical Question:** Does the approach gracefully degrade on edge cases, or catastrophically fail?

### 1.2 Success Criteria (SHOULD_WORK Gate)

**Primary (Gate Decision):**
- **P1:** Edge case overall accuracy ≥70% (15% degradation from 85% h-e1 baseline)
- **P2:** At least 3/4 edge case families pass 70% threshold

**Secondary (Characterization):**
- **S1:** Failure mode documentation identifies which edge cases fail and why
- **S2:** `no_norm_flag` binary fallback feature shows non-zero importance for edge cases
- **S3:** Parameter-mass ratio R remains discriminative (Cohen's d >0.5) across edge families

**Acceptable Outcomes (SHOULD_WORK allows failures):**
- **PASS:** ≥70% accuracy → edge case support confirmed
- **DOCUMENT:** <70% accuracy → characterize failures, document scope boundaries

---

## 2. User Stories & Scope

### 2.1 Primary Use Case

**As a** robustness validator,  
**I want to** evaluate the approach on edge case architectures,  
**So that** I can document scope boundaries and identify where fallback heuristics are sufficient.

**Acceptance Criteria:**
1. Extract features from 20 edge case models (4 families × 5 models)
2. Apply h-e1 trained classifier without retraining
3. Compute accuracy per family and overall degradation
4. Generate failure mode analysis for misclassified models

### 2.2 Edge Case Families

| Family | Representative Models | Edge Case Type | Expected Behavior |
|--------|----------------------|----------------|-------------------|
| **NormFree (NFNet)** | `nfnet_f0`, `nfnet_f1`, `dm_nfnet_f0`, `nfnet_f2`, `nfnet_f3` | No BatchNorm/LayerNorm | `no_norm_flag=1`, rely on R feature |
| **SENet** | `seresnet50`, `senet154`, `legacy_seresnet50`, `seresnet101`, `seresnet152` | Squeeze-Excitation attention | Extra linear layers → R variance |
| **RegNet** | `regnetx_032`, `regnety_032`, `regnetx_160`, `regnety_160`, `regnetx_320` | Extreme depth scaling | High norm count, test CV <0.15 |
| **ViT-Extreme** | `vit_giant_patch14_224`, `vit_huge_patch14_224`, `vit_large_patch32_224`, `deit_huge_patch14_224`, `beit_large_patch16_224` | Extreme parameter scale | Test R scale-invariance |

**Total:** 20 edge case models (statistically meaningful for 15% degradation detection)

### 2.3 Out-of-Scope

- **No Retraining:** Use existing h-e1 classifier (pre-trained)
- **No New Features:** Rely on existing 5D feature vector from h-m3
- **No Architecture Modifications:** Test edge cases as-is (no GroupNorm extraction, activation counting)

---

## 3. Technical Requirements

### 3.1 Data Requirements

**Input:**
- **Source:** TIMM Model Zoo (`timm.create_model()` API)
- **Edge Case Models:** 20 models across 4 families (Section 2.2)
- **Baseline Comparison:** 15 standard models (5 CNN + 5 Transformer + 5 Hybrid) from h-e1 training set
- **Total Dataset:** 35 models (20 edge + 15 baseline)

**Output:**
- **Features:** 5D feature vector `[bn_count, ln_count, gn_count, no_norm_flag, param_mass_ratio]`
- **Ground Truth:** Manual family labels (NormFree, SENet, RegNet, ViT-Extreme) based on TIMM naming

**Cache Path:** `.cache/checkpoints` (reuse h-m3 infrastructure)

### 3.2 Feature Extraction

**Reuse h-m3 Components (100% code reuse):**
- `CheckpointOnlyExtractor`: CPU-only checkpoint extraction (<1.05s per model median)
- `StatisticalFeatureExtractor`: Existing 5D feature computation
  - `no_norm_flag = 1` when `total_norm == 0` (NormFree detection)
  - Parameter-mass ratio R (normalization-agnostic)

**No Modifications Required:**
- Edge cases use identical feature extraction logic
- Fallback heuristics already implemented (`no_norm_flag`)

### 3.3 Classification

**Classifier:** Logistic Regression from h-e1 (pre-trained)  
**Source File:** `docs/youra_research/h-e1/code/results/logistic_classifier.pkl` (assumed)  
**Input Features:** 5D vector (same as h-e1 training)  
**Output:** Family prediction (CNN/Transformer/Hybrid)

**No Retraining:** Apply existing classifier to edge case features

### 3.4 Evaluation Metrics

| Metric | Computation | Threshold | Priority |
|--------|-------------|-----------|----------|
| **Overall Accuracy** | `accuracy_score(y_true, y_pred)` | ≥70% | P1 (Gate) |
| **Per-Family Accuracy** | Macro-average per edge family | ≥70% for 3/4 | P2 (Gate) |
| **Degradation** | `baseline_acc - edge_acc` | ≤15% | P1 (Gate) |
| **Confusion Matrix** | Per-family classification patterns | Document systematic errors | S1 |
| **Feature Importance** | Logistic regression coefficient shift | Document top-2 features | S2 |
| **Cohen's d (R)** | Effect size for R across families | >0.5 | S3 |

---

## 4. Functional Requirements

### 4.1 FR-1: Edge Case Model Curation

**Description:** Select 20 edge case models across 4 families with verified TIMM availability.

**Inputs:**
- TIMM model registry (`timm.list_models()`)
- Edge case family definitions (Section 2.2)

**Outputs:**
- `config_h_c1.py`: Edge case model list (Python list)
- Availability validation log (which models are missing pretrained weights)

**Acceptance Criteria:**
- At least 3 models per family (minimum 12 edge cases)
- All models have pretrained TIMM checkpoints
- Model names documented with family labels

**Fallback:** If <3 models available per family, substitute similar edge cases (e.g., `nfnet_f0` variants)

### 4.2 FR-2: Feature Extraction

**Description:** Extract 5D feature vectors from edge case models using h-m3 extractor.

**Inputs:**
- Edge case model list (FR-1 output)
- `CheckpointOnlyExtractor` (h-m3 code)

**Outputs:**
- `results/edge_case_features.csv`: Features with columns `[model_name, bn_count, ln_count, gn_count, no_norm_flag, param_mass_ratio, family_label]`
- Extraction time log (per-model timing)

**Acceptance Criteria:**
- All 20 edge case models extracted successfully
- No NaN values in features
- `no_norm_flag=1` for all NormFree models (validation check)
- Extraction time <2 minutes total (20 models × 1.05s median)

**Error Handling:**
- If model fails to load: Log error, skip model, continue with remaining
- If feature is NaN: Flag for manual inspection (may indicate TIMM API change)

### 4.3 FR-3: Classifier Application

**Description:** Apply h-e1 trained classifier to edge case features without retraining.

**Inputs:**
- Edge case features (FR-2 output)
- h-e1 trained classifier (`.pkl` file)

**Outputs:**
- `results/edge_case_predictions.csv`: Predictions with columns `[model_name, predicted_family, ground_truth, correct]`

**Acceptance Criteria:**
- Classifier loads successfully from h-e1 checkpoint
- Predictions generated for all 20 edge cases
- Output includes both predicted and ground truth labels

**Error Handling:**
- If classifier file missing: Fail with clear error (h-e1 prerequisite not satisfied)
- If feature dimension mismatch: Fail with diagnostic (feature extraction API changed)

### 4.4 FR-4: Accuracy Evaluation

**Description:** Compute overall, per-family accuracy and degradation metrics.

**Inputs:**
- Edge case predictions (FR-3 output)
- Baseline predictions (15 standard models from h-e1)

**Outputs:**
- `results/accuracy_by_family.json`: Per-family accuracy breakdown
  ```json
  {
    "NormFree": {"accuracy": 0.XX, "count": 5, "correct": X},
    "SENet": {"accuracy": 0.XX, "count": 5, "correct": X},
    "RegNet": {"accuracy": 0.XX, "count": 5, "correct": X},
    "ViT-Extreme": {"accuracy": 0.XX, "count": 5, "correct": X},
    "overall_edge": {"accuracy": 0.XX, "count": 20, "correct": X},
    "overall_baseline": {"accuracy": 0.XX, "count": 15, "correct": X},
    "degradation": 0.XX
  }
  ```

**Acceptance Criteria:**
- Overall accuracy computed with 95% Wilson confidence intervals
- Per-family accuracy for all 4 edge families
- Degradation = baseline_acc - edge_acc
- Gate decision documented (PASS if ≥70%, DOCUMENT if <70%)

### 4.5 FR-5: Failure Mode Analysis

**Description:** Analyze misclassified edge cases to identify systematic patterns.

**Inputs:**
- Misclassified models (predictions ≠ ground truth)
- Feature distributions (edge vs baseline)

**Outputs:**
- `results/failure_analysis.md`: Detailed failure characterization
  - Confusion matrix (predicted vs ground truth)
  - Feature distribution plots (edge vs baseline per family)
  - Systematic error patterns (e.g., "All NormFree misclassified as CNN")
  - Feature importance shift (h-e1 vs h-c1 coefficients)

**Acceptance Criteria:**
- Confusion matrix generated for all 4 edge families
- Feature distribution comparison (box plots or violin plots)
- Failure patterns documented with hypotheses (e.g., "NormFree fails because R alone is insufficient")
- Proposed extensions listed (e.g., "Add GroupNorm count", "Detect weight standardization")

**Analysis Dimensions:**
1. **NormFree failures:** Check if `no_norm_flag=1` correlates with misclassification
2. **SENet failures:** Measure R variance (SE blocks add extra linear layers)
3. **RegNet failures:** Validate CV <0.15 holds for extreme depth
4. **ViT-Extreme failures:** Check if scale-invariance breaks for billion-parameter models

---

## 5. Non-Functional Requirements

### 5.1 Performance

| Metric | Target | Justification |
|--------|--------|---------------|
| **Total Runtime** | <5 minutes | 2 min extraction + 1 sec inference + 2 min analysis |
| **Memory Usage** | <4 GB | Checkpoint-only (no model instantiation) |
| **GPU Requirement** | None (CPU-only) | h-m3 validated 0.00 MB GPU usage |

### 5.2 Code Reuse

**h-m3 Reuse (100%):**
- `CheckpointOnlyExtractor`
- `StatisticalFeatureExtractor`
- Checkpoint cache infrastructure

**h-e1 Reuse (100%):**
- Trained Logistic Regression classifier
- Evaluation metrics (accuracy_score, confusion_matrix)

**New Code (~150 lines):**
- Edge case model curation script
- Per-family accuracy breakdown
- Failure mode analysis (feature distributions, systematic patterns)

### 5.3 Robustness

**Model Availability:**
- Pre-validate TIMM availability before experiment (`timm.list_models()`)
- Fallback to smaller variants if models missing (e.g., `nfnet_f0` instead of `nfnet_f3`)
- Minimum viable: 12 edge cases (3 per family)

**Ground Truth Labeling:**
- Manual verification for ambiguous cases (e.g., is `seresnet50` SENet or standard CNN?)
- Document labeling decisions in code comments
- Cross-check with TIMM model card metadata

**Statistical Power:**
- Report 95% confidence intervals for accuracy (Wilson score method)
- If CI width >±10%, flag insufficient sample size
- Fallback: Expand edge case set to 30 models (5 per family → 7-8 per family)

---

## 6. Dependencies

### 6.1 Prerequisites

| Dependency | Source | Status | Risk |
|------------|--------|--------|------|
| **h-m3 Extractor** | `docs/youra_research/h-m3/code/` | VALIDATED | None (h-m3 completed) |
| **h-e1 Classifier** | `docs/youra_research/h-e1/code/results/` | ASSUMED | Medium (file may not exist) |
| **TIMM Edge Models** | `timm.create_model()` | UNKNOWN | Medium (availability varies) |

**Mitigation for h-e1:**
- If classifier file missing, train minimal logistic regression on h-e1 features (30 sec)
- Use same training set as h-e1 (35 standard models)

**Mitigation for TIMM:**
- Pre-validate availability before experiment start
- Fallback to similar edge cases if models missing

### 6.2 External Libraries

```python
# requirements.txt (reuse h-m3)
torch>=2.0.0
timm>=0.9.0
scikit-learn>=1.3.0
pandas>=2.0.0
numpy>=1.24.0
matplotlib>=3.7.0  # For failure analysis plots
seaborn>=0.12.0    # For distribution plots
```

**No New Dependencies:** All libraries already in h-m3 environment

---

## 7. Deliverables

### 7.1 Code Artifacts

| File | Purpose | Lines | Priority |
|------|---------|-------|----------|
| `config_h_c1.py` | Edge case model list, thresholds | ~50 | P1 |
| `main_h_c1.py` | Experiment runner (extract → predict → analyze) | ~100 | P1 |
| `edge_case_analyzer.py` | Failure mode analysis module | ~150 | P2 |
| `requirements.txt` | Dependencies (reuse h-m3) | ~10 | P1 |

### 7.2 Results

| File | Content | Format |
|------|---------|--------|
| `results/edge_case_features.csv` | Extracted features for 20 edge cases | CSV |
| `results/edge_case_predictions.csv` | Predictions with ground truth | CSV |
| `results/accuracy_by_family.json` | Per-family accuracy breakdown | JSON |
| `results/confusion_matrix.png` | Edge case confusion matrix | PNG |
| `results/feature_distributions.png` | Edge vs baseline distributions | PNG |
| `results/failure_analysis.md` | Detailed failure characterization | Markdown |

### 7.3 Validation Report

**File:** `docs/youra_research/h-c1/04_validation.md`

**Structure:**
1. **Executive Summary:** Gate decision (PASS/DOCUMENT), overall accuracy, degradation
2. **Results:** Overall accuracy, per-family breakdown, degradation analysis
3. **Failure Mode Analysis:** Per-family patterns, feature importance shift
4. **Scope Boundaries:** Supported vs unsupported edge cases
5. **Recommendations:** Proposed extensions for failing families
6. **Conclusion:** Gate decision rationale

---

## 8. Risk Analysis

### 8.1 Risk 1: Edge Case Model Unavailability

**Risk:** Some edge case models may not have pretrained checkpoints in TIMM.

**Likelihood:** Medium (TIMM coverage varies for exotic models)  
**Impact:** Low (can substitute similar edge cases)

**Mitigation:**
- Pre-validate availability via `timm.list_models('nfnet*')` before experiment
- Fallback to smaller variants (e.g., `nfnet_f0` instead of `nfnet_f3`)
- Minimum viable: 3 models per family (12 total)

**Contingency:**
- If <3 models per family, expand search to similar architectures (e.g., EfficientNet-V2 for NormFree)
- Document substitutions in `config_h_c1.py`

### 8.2 Risk 2: h-e1 Classifier File Missing

**Risk:** h-e1 may not have generated a saved classifier file.

**Likelihood:** Medium (h-e1 implementation details unknown)  
**Impact:** Medium (blocks experiment start)

**Mitigation:**
- Check for classifier file in Phase 3 Step 06 (verification)
- If missing, train minimal logistic regression on h-e1 features (30 sec)
- Use same 35-model training set as h-e1

**Contingency:**
- Quick-train classifier: `LogisticRegression().fit(X_h_e1, y_h_e1)`
- Verify accuracy matches h-e1 baseline (>80%) before proceeding

### 8.3 Risk 3: Insufficient Statistical Power

**Risk:** 20-model sample may have high variance (±10%) → cannot reliably detect 15% degradation.

**Likelihood:** Medium (small sample size)  
**Impact:** Medium (may need to expand dataset)

**Mitigation:**
- Use Wilson score confidence intervals (exact binomial)
- Report degradation with 95% CI width
- If CI >±10%, increase edge case sample to 30 models

**Contingency:**
- Expand each family from 5 → 7-8 models (28 total edge cases)
- Re-run extraction (additional ~1 min runtime)

### 8.4 Risk 4: TIMM Naming Ambiguity

**Risk:** Edge case models may be labeled as standard families in TIMM (e.g., `seresnet50` as 'CNN').

**Likelihood:** High (TIMM naming is not structurally consistent)  
**Impact:** Medium (affects ground truth accuracy)

**Mitigation:**
- Manual ground truth labeling based on architecture papers
- Validate assumptions (SENet should show mixed norm patterns, NFNet should have `no_norm_flag=1`)
- Document labeling decisions in code comments

**Contingency:**
- Cross-reference TIMM model cards and architecture papers
- For ambiguous cases, inspect checkpoint keys (e.g., presence of `se_module` keys)

---

## 9. Success Metrics (Detailed)

### 9.1 Primary Gate Metrics (SHOULD_WORK)

**P1: Overall Edge Case Accuracy ≥70%**
- **Computation:** `accuracy_score(y_true_edge, y_pred_edge)`
- **Sample:** 20 edge case models
- **Confidence Interval:** Wilson score 95% CI (exact binomial)
- **Decision Rule:** 
  - If accuracy ≥70% and lower CI bound ≥65% → PASS
  - If accuracy <70% → DOCUMENT (acceptable for SHOULD_WORK)

**P2: At Least 3/4 Families Pass 70% Threshold**
- **Computation:** Count families with accuracy ≥70%
- **Families:** NormFree, SENet, RegNet, ViT-Extreme
- **Decision Rule:**
  - If ≥3 families pass → PASS (one failing family is acceptable)
  - If <3 families pass → DOCUMENT (characterize multi-family failures)

### 9.2 Secondary Characterization Metrics

**S1: Failure Mode Documentation**
- **Requirement:** For each misclassified model, identify pattern (e.g., "All NormFree misclassified as CNN")
- **Output:** `results/failure_analysis.md` with systematic error characterization
- **Success:** Documented failure patterns enable future feature extensions

**S2: `no_norm_flag` Importance for Edge Cases**
- **Computation:** Logistic regression coefficient for `no_norm_flag` on edge cases
- **Baseline:** h-e1 coefficient (standard architectures)
- **Success:** Coefficient increases for edge cases (validates fallback heuristic design)

**S3: Parameter-Mass Ratio R Discriminative Power**
- **Computation:** Cohen's d for R across edge families (NormFree vs SENet vs RegNet vs ViT)
- **Threshold:** d >0.5 (medium effect size)
- **Success:** R remains discriminative despite edge case violations

---

## 10. Acceptance Criteria Checklist

**Before Implementation (Phase 3 Complete):**
- [ ] PRD reviewed and approved (this document)
- [ ] Architecture design specifies module structure
- [ ] Logic design defines experiment workflow
- [ ] Configuration design lists all hyperparameters

**Before Execution (Phase 4 Start):**
- [ ] Edge case model availability validated (`timm.list_models()`)
- [ ] h-e1 classifier file exists or fallback trained
- [ ] h-m3 extractor verified on sample edge case model

**During Execution:**
- [ ] All 20 edge cases extracted without NaN features
- [ ] `no_norm_flag=1` verified for NormFree models
- [ ] Extraction time <2 minutes (sanity check)

**After Execution (Validation):**
- [ ] Overall accuracy computed with 95% CI
- [ ] Per-family accuracy breakdown generated
- [ ] Confusion matrix and feature distributions plotted
- [ ] Failure analysis documented with proposed extensions
- [ ] Gate decision documented (PASS/DOCUMENT)
- [ ] `verification_state.yaml` updated with result

---

## 11. Appendices

### 11.1 Appendix A: Edge Case Model List (Proposed)

**NormFree (NFNet):**
1. `nfnet_f0` (71M params, ImageNet-1k)
2. `nfnet_f1` (133M params)
3. `dm_nfnet_f0` (DeepMind variant, 72M params)
4. `nfnet_f2` (194M params)
5. `nfnet_f3` (255M params)

**SENet:**
1. `seresnet50` (28M params, Squeeze-Excitation ResNet-50)
2. `senet154` (116M params, ImageNet-21k)
3. `legacy_seresnet50` (TIMM legacy variant)
4. `seresnet101` (49M params)
5. `seresnet152` (67M params)

**RegNet:**
1. `regnetx_032` (15M params, 0.32 GFLOPs)
2. `regnety_032` (20M params)
3. `regnetx_160` (54M params, 1.6 GFLOPs)
4. `regnety_160` (84M params)
5. `regnetx_320` (107M params, 3.2 GFLOPs)

**ViT-Extreme:**
1. `vit_giant_patch14_224` (1.8B params, extreme scale)
2. `vit_huge_patch14_224` (632M params)
3. `vit_large_patch32_224` (307M params, coarse patches)
4. `deit_huge_patch14_224` (632M params, DeiT variant)
5. `beit_large_patch16_224` (305M params, BEiT variant)

**Total:** 20 models (subject to TIMM availability validation)

### 11.2 Appendix B: Ground Truth Labeling Strategy

**Family Assignment:**
- **NormFree:** Models with `nfnet` or `dm_nfnet` in name
- **SENet:** Models with `se` prefix (Squeeze-Excitation)
- **RegNet:** Models with `regnet` in name (extreme depth scaling)
- **ViT-Extreme:** Models with `vit_giant`, `vit_huge`, `deit_huge`, `beit_large` (extreme parameter scale)

**Ambiguity Resolution:**
- If model name matches multiple families (e.g., `se_regnety`), prioritize first defining characteristic (SENet over RegNet)
- Cross-check TIMM model card metadata for architecture family
- Inspect checkpoint keys for architectural markers (e.g., `se_module` keys)

**Validation:**
- For NormFree: Verify `no_norm_flag=1` after feature extraction
- For SENet: Verify presence of extra linear layers in R computation
- For RegNet: Verify high layer count (>50 blocks)
- For ViT-Extreme: Verify parameter count >300M

### 11.3 Appendix C: Failure Mode Analysis Template

**For Each Misclassified Model:**

```markdown
### Model: {model_name}
**Ground Truth:** {true_family}  
**Predicted:** {predicted_family}  
**Features:** [bn={bn}, ln={ln}, gn={gn}, no_norm={no_norm}, R={R:.3f}]

**Failure Hypothesis:**
{Why was this model misclassified? Which feature(s) failed?}

**Proposed Extension:**
{What additional feature would fix this? e.g., "Add GroupNorm count", "Detect weight standardization"}
```

**Systematic Pattern Example:**

```markdown
### Pattern: All NormFree Models Misclassified as CNN
**Observation:** 5/5 NormFree models predicted as CNN despite `no_norm_flag=1`  
**Root Cause:** Logistic regression coefficient for `no_norm_flag` is near-zero (trained on standard architectures where norm layers are always present)  
**Proposed Fix:** Retrain classifier with balanced edge case representation OR add interaction term `no_norm * R`
```

---

**Document Status:** Ready for Phase 3 Architecture/Logic/Config Design  
**Next Step:** Launch architecture-agent, logic-agent, configuration-agent (Phase 3 Steps 05-07)
