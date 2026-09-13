# Experiment Brief: H-C1 Edge Case Robustness

**Hypothesis ID:** h-c1  
**Type:** CONDITION  
**Gate:** SHOULD_WORK  
**Date:** 2026-07-11  
**Prerequisites:** h-m3 (Checkpoint extraction validated)

---

## 1. Hypothesis Statement

**Full Statement:**  
Under edge case architecture evaluation (NormFree networks, non-standard attention, extreme scaling), if fallback heuristics (No_norm_flag binary feature) are added, then accuracy degradation is ≤15% vs standard architectures because edge cases violate normalization assumptions but retain parameter allocation patterns.

**Rationale:**  
This hypothesis tests boundary conditions where standard assumptions (A2: normalization reflects paradigm) break down. It validates scope limits and identifies where the approach needs extension. Success proves robustness with fallback heuristics; acceptable failure documents scope boundaries for future work.

---

## 2. Research Context

### 2.1 Archon KB Insights

**Edge Case Patterns (from KB search):**
- NFNet/NormFree architectures replace BatchNorm with scaled weight standardization
- GroupNorm provides alternative to BatchNorm/LayerNorm for non-standard architectures
- Attention mechanisms (squeeze-excitation, non-local) add complexity beyond standard conv/linear patterns

**Key Finding:** Fallback heuristics (binary flags for missing features) are common in robust classifiers when feature extraction fails on edge cases.

### 2.2 Codebase Analysis

**Existing Infrastructure (from h-m3):**
- `StatisticalFeatureExtractor` already implements `no_norm_flag` binary feature (line 34)
- `no_norm_flag = 1` when `total_norm == 0` (no BN/LN/GN detected)
- Parameter-mass ratio R is normalization-agnostic (only depends on tensor shapes)

**Code Reuse Opportunity:**
- h-m3's checkpoint extractor handles arbitrary TIMM models
- Feature extraction logic requires NO modification for edge cases
- Only need to curate edge case model list and validate degradation

---

## 3. Experiment Design

### 3.1 Dataset Specification

**Type:** `standard` (TIMM Model Zoo)  
**Name:** TIMM Edge Case Evaluation Set  
**Source:** `timm.create_model()` API with edge case model families

**Edge Case Families:**

| Family | Representative Models | Edge Case Type | Expected Behavior |
|--------|----------------------|----------------|-------------------|
| **NormFree (NFNet)** | `nfnet_f0`, `nfnet_f1`, `dm_nfnet_f0` | No BatchNorm/LayerNorm | `no_norm_flag=1`, rely on R feature |
| **SENet** | `seresnet50`, `senet154`, `legacy_seresnet50` | Squeeze-Excitation attention | Non-standard linear layers → R variance |
| **RegNet** | `regnetx_032`, `regnety_032`, `regnetx_160` | Extreme depth scaling | High layer count → norm count inflation |
| **ViT Variants** | `vit_giant_patch14_224`, `vit_huge_patch14_224` | Extreme parameter scale | Test scale-invariance of R |

**Sample Size:** 20 edge case models (5 per family) + 15 standard models (5 per family: CNN/Transformer/Hybrid) for baseline comparison  
**Total:** 35 models (statistically meaningful for 15% degradation threshold)

**Split Strategy:**
- **Baseline Set (15 models):** Trained classifier from h-e1 (70% of 50 models = 35 train models)
- **Edge Case Test Set (20 models):** Hold-out edge case families (NOT in h-e1 training set)

**Cache Path:** `.cache/checkpoints` (reuse h-m3 infrastructure)

### 3.2 Baseline Method

**Baseline Performance (from h-e1 validation):**
- Standard architecture accuracy: **>80%** (h-e1 primary success criterion)
- Target edge case accuracy: **>70%** (15% degradation threshold)

**Method:** Logistic Regression classifier from h-e1  
**Features:** 5-dimensional vector `[bn_count, ln_count, gn_count, no_norm_flag, param_mass_ratio]`  
**Source:** `sklearn.linear_model.LogisticRegression`

---

## 4. Implementation Plan

### 4.1 Data Preparation (Tier 1: No new data)

**Reuse h-m3 Infrastructure:**
- Checkpoint extraction: `CheckpointOnlyExtractor` (h-m3)
- Feature extraction: `StatisticalFeatureExtractor` (h-m3)
- No new dataset download required

**New Task:**
1. **Curate edge case model list** (20 models across 4 edge case families)
2. **Extract features** using existing h-m3 code
3. **Load h-e1 trained classifier** from cached model file

### 4.2 Experiment Workflow

```python
# Step 1: Load trained classifier from h-e1
classifier = load_classifier('h-e1/code/results/logistic_classifier.pkl')

# Step 2: Extract edge case features (reuse h-m3 code)
edge_case_models = [
    'nfnet_f0', 'nfnet_f1', 'dm_nfnet_f0', 'nfnet_f2', 'nfnet_f3',  # NormFree
    'seresnet50', 'senet154', 'legacy_seresnet50', 'seresnet101', 'seresnet152',  # SENet
    'regnetx_032', 'regnety_032', 'regnetx_160', 'regnety_160', 'regnetx_320',  # RegNet
    'vit_giant_patch14_224', 'vit_huge_patch14_224', 'vit_large_patch32_224', 
    'deit_huge_patch14_224', 'beit_large_patch16_224'  # ViT extreme scale
]

extractor = CheckpointOnlyExtractor()
edge_features_df = extractor.extract_batch(edge_case_models)

# Step 3: Predict and evaluate
predictions = classifier.predict(edge_features_df[['bn_count', 'ln_count', 'gn_count', 'no_norm_flag', 'param_mass_ratio']])
accuracy = accuracy_score(ground_truth, predictions)

# Step 4: Per-family breakdown
for family in ['NormFree', 'SENet', 'RegNet', 'ViT-Extreme']:
    family_accuracy = compute_family_accuracy(family)
    degradation = baseline_accuracy - family_accuracy
    print(f"{family}: {family_accuracy:.1%} (degradation: {degradation:.1%})")

# Step 5: Failure mode analysis
misclassified = edge_features_df[predictions != ground_truth]
analyze_failure_patterns(misclassified)
```

### 4.3 Success Criteria

**Primary (Gate: SHOULD_WORK):**
- **P1:** Edge case accuracy ≥70% (15% degradation from 85% baseline)
- **P2:** At least 3/4 edge case families pass 70% threshold

**Secondary:**
- **S1:** Failure mode documentation identifies extension needs
- **S2:** `no_norm_flag` feature has non-zero importance for edge cases
- **S3:** Parameter-mass ratio R remains discriminative (Cohen's d >0.5) for edge families

**If Gate Fails (DOCUMENT outcome):**
- Characterize which edge case families fail and why
- Propose feature extensions (e.g., GroupNorm count, attention layer count)
- Scope boundary documentation for future work

---

## 5. Validation Protocol

### 5.1 Metrics

| Metric | Computation | Threshold |
|--------|-------------|-----------|
| **Edge Case Accuracy** | `accuracy_score(y_true, y_pred)` for 20 edge models | ≥70% |
| **Per-Family Accuracy** | Macro-average per edge family (4 families) | ≥70% for 3/4 families |
| **Degradation** | `baseline_acc - edge_acc` | ≤15% |
| **Feature Importance Shift** | Logistic regression coefficient change | Document top-2 features |
| **Confusion Matrix** | Per-family confusion patterns | Identify systematic errors |

### 5.2 Failure Mode Analysis

**Hypothesis-Driven Analysis:**

1. **NormFree (NFNet) failures:**
   - **Expected:** `no_norm_flag=1` triggers fallback to R-only classification
   - **If fails:** R is insufficient alone → need additional features (e.g., activation function counts)

2. **SENet failures:**
   - **Expected:** Squeeze-excitation layers appear as extra linear layers → R variance
   - **If fails:** SE blocks confound parameter-mass ratio → need to exclude SE-specific keys

3. **RegNet failures:**
   - **Expected:** Extreme depth inflates norm layer counts but preserves family patterns
   - **If fails:** Scale-invariance violated (CV ≥0.15) → normalize by depth

4. **ViT-Extreme failures:**
   - **Expected:** Scale-invariance holds (h-m2 validated CV <0.15 across ResNet-{18,152})
   - **If fails:** Extreme scale (billion-parameter) breaks assumptions → need size normalization

### 5.3 Validation Steps

1. **Extract edge case features** (20 models, ~2 min using h-m3 code)
2. **Load h-e1 classifier** and predict on edge cases
3. **Compute accuracy metrics** (overall + per-family breakdown)
4. **Analyze failures:**
   - Plot feature distributions (edge vs standard families)
   - Compute feature importance shift (logistic regression coefficients)
   - Document confusion matrix patterns
5. **Generate failure report:**
   - List misclassified models with features
   - Identify systematic patterns (e.g., all NormFree misclassified as CNN)
   - Propose feature extensions for future work

---

## 6. Expected Outcomes

### 6.1 Scenario 1: PASS (≥70% accuracy)

**Interpretation:**
- Fallback heuristics (`no_norm_flag`) successfully handle edge cases
- Parameter-mass ratio R is robust across non-standard architectures
- Approach generalizes beyond standard CNN/Transformer/Hybrid families

**Next Steps:**
- Document edge case support in scope
- No further action required (SHOULD_WORK gate allows acceptable failures)

### 6.2 Scenario 2: PARTIAL PASS (60-70% accuracy, 3/4 families pass)

**Interpretation:**
- Most edge cases handled, but one family shows systematic failure
- Indicates specific scope boundary (e.g., NormFree requires additional features)

**Next Steps:**
- Document failing family as out-of-scope
- Propose targeted feature extension (e.g., weight standardization detection for NFNet)

### 6.3 Scenario 3: FAIL (<60% accuracy, <3/4 families pass)

**Interpretation:**
- Edge cases break core assumptions more severely than expected
- Fallback heuristics insufficient for robustness

**Next Steps (DOCUMENT outcome):**
- Characterize failure modes in detail
- Propose comprehensive feature engineering (GroupNorm, activation functions, attention patterns)
- Update scope to "standard architectures only" for current approach

---

## 7. Resource Requirements

### 7.1 Computational Budget

| Resource | Estimate | Justification |
|----------|----------|---------------|
| **Extraction Time** | ~2 minutes | 20 models × 1.05s/model (h-m3 median) |
| **Inference Time** | <1 second | Logistic regression on 20 samples |
| **Total Runtime** | ~3 minutes | Extraction + prediction + analysis |
| **Memory** | <4 GB | Checkpoint-only (no model instantiation) |
| **GPU** | Not required | CPU-only (h-m3 validated) |

### 7.2 Code Reuse

| Component | Source | Reuse Rate |
|-----------|--------|------------|
| **Checkpoint Extractor** | h-m3 | 100% |
| **Feature Extractor** | h-m3 | 100% |
| **Classifier** | h-e1 | 100% (pre-trained) |
| **Evaluation Metrics** | h-e1 | 80% (add per-family breakdown) |
| **New Code** | Edge case analysis | ~100 lines |

**Total Code Budget:** ~100 new lines (mostly analysis/visualization)

### 7.3 Task Breakdown

**Epic Tasks (3 total):**
1. **Data Preparation:** Curate edge case model list (5 models × 4 families)
2. **Feature Extraction:** Run h-m3 extractor on edge case models
3. **Evaluation & Analysis:** Predict, compute metrics, analyze failures

**Estimated Effort:** 2-3 hours (minimal implementation, mostly configuration)

---

## 8. Risks & Mitigations

### 8.1 Risk 1: Edge Case Model Availability

**Risk:** Some edge case models (e.g., `nfnet_f3`, `vit_giant_patch14_224`) may not have pretrained checkpoints in TIMM.

**Mitigation:**
- Pre-validate availability via `timm.list_models('nfnet*')` before experiment
- Fallback: Use smaller variants (e.g., `nfnet_f0` instead of `nfnet_f3`)
- Minimum viable: 3 models per family (12 edge cases) for meaningful evaluation

**Likelihood:** Medium (TIMM coverage varies)  
**Impact:** Low (can substitute similar edge cases)

### 8.2 Risk 2: TIMM Naming Ambiguity for Edge Cases

**Risk:** Edge case models may be labeled as standard families in TIMM (e.g., `seresnet50` as 'CNN').

**Mitigation:**
- Manual ground truth labeling for edge case families
- Validate assumptions: SENet should show mixed norm patterns, NFNet should have `no_norm_flag=1`
- Document labeling decisions in code comments

**Likelihood:** High (TIMM naming is not always structurally consistent)  
**Impact:** Medium (affects ground truth accuracy)

### 8.3 Risk 3: Insufficient Degradation Sensitivity

**Risk:** 20-model sample may have high variance (±10%) → cannot reliably detect 15% degradation.

**Mitigation:**
- Use exact binomial confidence intervals (Wilson score)
- Report degradation with 95% confidence interval
- If variance is high (CI >±10%), increase edge case sample to 30 models

**Likelihood:** Medium (small sample size)  
**Impact:** Medium (may need to expand dataset)

---

## 9. Deliverables

### 9.1 Code Artifacts

1. **`config_h_c1.py`:** Edge case model list, evaluation thresholds
2. **`main_h_c1.py`:** Experiment runner (extract → predict → analyze)
3. **`edge_case_analyzer.py`:** Failure mode analysis module
4. **`requirements.txt`:** Dependencies (reuse h-m3: torch, timm, sklearn, pandas)

### 9.2 Results

1. **`results/edge_case_predictions.csv`:** Model-level predictions with features
2. **`results/accuracy_by_family.json`:** Per-family accuracy breakdown
3. **`results/confusion_matrix.png`:** Edge case confusion matrix
4. **`results/feature_importance_shift.png`:** Coefficient changes vs h-e1
5. **`results/failure_analysis.md`:** Detailed failure mode documentation

### 9.3 Validation Report

**File:** `docs/youra_research/h-c1/04_validation.md`

**Structure:**
```markdown
# H-C1 Validation Report

## 1. Executive Summary
- Edge case accuracy: XX%
- Degradation: XX% (threshold: ≤15%)
- Gate status: PASS/FAIL

## 2. Results
- Overall accuracy table
- Per-family breakdown
- Degradation analysis

## 3. Failure Mode Analysis
- NormFree patterns
- SENet patterns
- RegNet patterns
- ViT-Extreme patterns

## 4. Feature Importance Shift
- Coefficient comparison (h-e1 vs h-c1)
- Top-2 features for edge cases

## 5. Scope Boundaries
- Supported edge cases
- Unsupported edge cases
- Proposed extensions

## 6. Conclusion
- Gate decision: PASS/FAIL/DOCUMENT
- Recommendations
```

---

## 10. Success Checklist

**Before Execution:**
- [ ] Validate edge case model availability in TIMM
- [ ] Confirm h-e1 classifier file exists (`.pkl` or `.joblib`)
- [ ] Verify h-m3 extractor runs on sample edge case model

**During Execution:**
- [ ] Log extraction times per edge case model
- [ ] Validate `no_norm_flag=1` for NormFree models
- [ ] Check for missing features (NaN values)

**After Execution:**
- [ ] Compute accuracy with 95% confidence intervals
- [ ] Generate confusion matrix and failure analysis
- [ ] Document scope boundaries in validation report
- [ ] Update verification_state.yaml with gate decision

---

## 11. References

**Codebase:**
- h-m3 checkpoint extractor: `docs/youra_research/h-m3/code/src/checkpoint_only_extractor.py`
- h-m3 feature extractor: `docs/youra_research/h-m3/code/src/feature_extractor.py`
- h-e1 classifier (assumed): `docs/youra_research/h-e1/code/results/logistic_classifier.pkl`

**Archon KB Insights:**
- GroupNorm as BatchNorm/LayerNorm alternative (diffusers attention.py)
- Binary fallback flags for missing features (common pattern in robust classifiers)

**Hypothesis Context:**
- Verification plan: `docs/youra_research/02b_verification_plan.md` (Section 2.2, H-C1)
- Prerequisites: h-m3 validation report (checkpoint extraction feasibility confirmed)

---

**Document Version:** 1.0  
**Last Updated:** 2026-07-11  
**Status:** Ready for Phase 3 (Implementation Planning)
