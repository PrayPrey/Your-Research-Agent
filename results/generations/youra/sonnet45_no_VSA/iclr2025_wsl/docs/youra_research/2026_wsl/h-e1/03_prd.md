# Product Requirements Document (PRD)

**Hypothesis:** h-e1  
**Title:** Statistical Features Sufficiency for Architecture Family Classification  
**Date:** 2026-07-11  
**Phase:** 3 - Implementation Planning  
**Status:** DRAFT  

---

## Executive Summary

### Problem Statement
Validate that simple statistical features extracted from model checkpoints (normalization layer counts + parameter-mass ratio) can achieve >80% accuracy for classifying neural network architectures into families (CNN/Transformer/Hybrid), establishing a foundation for lightweight architecture analysis without complex graph representations.

### Solution Overview
Implement a proof-of-concept (PoC) system that:
1. Downloads 60 pretrained models from TIMM Model Zoo (24 CNN, 24 Transformer, 12 Hybrid)
2. Extracts 5 statistical features from each model's state_dict (BatchNorm count, LayerNorm count, GroupNorm count, no-norm flag, parameter-mass ratio)
3. Trains a LogisticRegression classifier on stratified 70/30 train/validation split
4. Achieves >80% macro-averaged validation accuracy (MUST_WORK gate)

### Success Criteria
- **Primary:** Validation macro-accuracy > 80%
- **Secondary:** Per-class accuracy ≥ 75% for all families (CNN, Transformer, Hybrid)
- **Tertiary:** Scale invariance validated (intra-family CV < 0.15 for ResNet variants)

---

## Product Context

### Target Users
- Deep learning researchers investigating architecture classification methods
- ML practitioners exploring lightweight model analysis techniques
- AutoML pipeline developers needing fast architecture detection

### Use Cases
1. **Architecture Family Detection:** Classify unknown model checkpoints without architecture source code
2. **Baseline Validation:** Establish simple feature performance before exploring complex methods (GNN, MLP)
3. **Mechanism Hypothesis Foundation:** Provide empirical foundation for H-M1, H-M2, H-M3 (normalization fingerprinting, parameter-mass separation)

### Dependencies
- **Prerequisites:** None (foundation hypothesis)
- **Follows:** Phase 2C experiment design completion
- **Enables:** H-M1 (normalization fingerprinting), H-M2 (parameter-mass separation), H-M3 (hybrid identification)

---

## Functional Requirements

### FR1: Dataset Preparation
**Priority:** P0 (Critical)  
**Description:** Download and prepare 60-model TIMM dataset with stratified split

**Acceptance Criteria:**
- Download 60 pretrained models via `timm.create_model(name, pretrained=True)`
  - 24 CNN models (ResNet variants, MobileNet, EfficientNet, DenseNet, VGG, ConvNeXt, etc.)
  - 24 Transformer models (ViT, DeiT, Swin, BEiT, Twins, CaiT, etc.)
  - 12 Hybrid models (PiT, Mixer, ConViT, MaxViT, etc.)
- Create stratified 70/30 train/validation split
  - Train: 42 models (17 CNN, 17 Transformer, 8 Hybrid)
  - Validation: 18 models (7 CNN, 7 Transformer, 4 Hybrid)
- Save to CSV files: `train_features.csv`, `val_features.csv`
- Total checkpoint size: ~15 GB (cached in `~/.cache/torch/hub/checkpoints/`)

**Implementation Notes:**
- Use `timm.list_models(pretrained=True)` for model discovery
- Apply regex patterns for family classification:
  - CNN: `r'^(resnet|mobilenet|efficientnet|densenet|vgg|convnext|resnext|wide_resnet|regnet|seresnet|senet|inception|dpn)'`
  - Transformer: `r'^(vit|deit|swin|beit|twins|cait|coat|levit|poolformer|xcit|crossvit)'`
  - Hybrid: `r'^(resnetv2.*bit|convit|pit|mixer|visformer|tnt|maxvit)'`
- Random seed: 42 (for reproducibility)

### FR2: Feature Extraction
**Priority:** P0 (Critical)  
**Description:** Extract 5 statistical features from each model's state_dict

**Acceptance Criteria:**
- For each model checkpoint, compute:
  1. **bn_count:** BatchNorm layer count (regex match: `bn|batch_norm|batchnorm`)
  2. **ln_count:** LayerNorm layer count (regex match: `ln|layer_norm|layernorm`)
  3. **gn_count:** GroupNorm layer count (regex match: `gn|group_norm|groupnorm`)
  4. **no_norm_flag:** Binary flag (1 if all norm counts = 0, else 0)
  5. **param_mass_ratio:** R = conv_params / (conv_params + linear_params_no_head)
- Feature vector shape: [N=60, D=5]
- All features stored as numerical values (int for counts, float for ratio)

**Implementation Notes:**
- State dict key matching via case-insensitive regex
- Parameter counting logic:
  - 4D tensors → conv_params (shape: [out_ch, in_ch, kH, kW])
  - 2D tensors → linear_params (shape: [out_feat, in_feat])
  - Exclude classification head keys: `head`, `fc`, `classifier`
- Handle edge cases:
  - NormFree networks (no normalization layers) → no_norm_flag = 1
  - Models with only conv or only linear → ratio = 0.0 or 1.0

### FR3: Data Validation (Assumption Tests)
**Priority:** P1 (High)  
**Description:** Validate Phase 2A assumptions A1, A2, A3 before training

**Acceptance Criteria:**
- **A1 Test (TIMM Naming Alignment):** 
  - Sample 10 models, manually verify structural alignment
  - Expected: >90% alignment rate
  - Action if failed: Flag for manual verification
  
- **A2 Test (Normalization Convention):**
  - Compute violation rates on training set
  - CNN with LayerNorm: ≤15%
  - Transformer with BatchNorm: ≤15%
  - Action if failed: Add GroupNorm features or pivot to alternative features
  
- **A3 Test (Scale Invariance):**
  - Compute CV for ResNet family (resnet18, 34, 50, 101, 152)
  - CV = std(R) / mean(R) < 0.15
  - Action if failed: Use R-rank or normalized ratio
  
- Save validation results to `data/assumption_validation.json`

**Implementation Notes:**
- Run validation before training (early failure detection)
- Log failures with specific violation details
- Generate diagnostic plots if any test fails

### FR4: Classifier Training
**Priority:** P0 (Critical)  
**Description:** Train LogisticRegression classifier on scaled features

**Acceptance Criteria:**
- Use scikit-learn LogisticRegression with:
  - multi_class='multinomial' (3-way classification)
  - solver='lbfgs' (handles multinomial well)
  - max_iter=1000 (ensure convergence)
  - random_state=42 (reproducibility)
  - class_weight='balanced' (handle 20% hybrid imbalance)
- Apply StandardScaler preprocessing (mean=0, std=1)
- Save trained artifacts:
  - `models/classifier.pkl` (trained LogisticRegression)
  - `models/scaler.pkl` (fitted StandardScaler)
- Training time: <1 minute

**Implementation Notes:**
- No hyperparameter tuning (default C=1.0)
- No cross-validation (single split for PoC)
- Feature scaling critical for convergence

### FR5: Validation Evaluation
**Priority:** P0 (Critical)  
**Description:** Evaluate classifier on held-out validation set

**Acceptance Criteria:**
- Compute primary metric:
  - **Macro-averaged accuracy:** >80% (MUST_WORK threshold)
- Compute secondary metrics:
  - Per-class accuracy (precision from classification_report): ≥75% for CNN, Transformer, Hybrid
  - Confusion matrix (3x3 for CNN/Transformer/Hybrid)
  - Feature importance (average absolute coefficients across classes)
- Generate visualizations:
  - `results/confusion_matrix.png`
  - `results/feature_importance.png`
  - `results/r_distribution.png` (histogram of R per family)
- Save results to `results/h_e1_results.md`

**Implementation Notes:**
- Use sklearn metrics: `accuracy_score`, `classification_report`, `confusion_matrix`
- Report decimal format (e.g., 0.85 for 85% accuracy)
- Document all misclassified models by name

### FR6: Failure Diagnostic Analysis (Conditional)
**Priority:** P2 (Medium)  
**Description:** If validation accuracy ≤80%, run diagnostic analysis

**Acceptance Criteria:**
- Generate diagnostic outputs:
  1. Confusion matrix asymmetry analysis (which families confused)
  2. Feature distribution scatter plots (BN vs LN, R histograms)
  3. Failure case inspection (list misclassified models with reasoning)
  4. Alternative feature exploration (GroupNorm importance, activation patterns)
- Decision tree:
  - If accuracy <50%: ABANDON (features fundamentally insufficient)
  - If accuracy 50-80%: PIVOT (refine features or test polynomial features)
- Save diagnostic report to `results/h_e1_failure_analysis.md`

**Implementation Notes:**
- Only execute if primary metric fails
- Provide actionable recommendations for pivot
- Document root cause hypothesis (A1/A2/A3/A4 violation)

### FR7: Reporting and Documentation
**Priority:** P1 (High)  
**Description:** Generate comprehensive results report

**Acceptance Criteria:**
- Create `results/h_e1_results.md` with:
  - Executive summary (PASSED/FAILED decision)
  - Primary and secondary metrics
  - Confusion matrix table and visualization
  - Feature importance ranking
  - Failure cases (if any)
  - Assumption validation results
  - Next steps recommendation
- Update `verification_state.yaml`:
  - Set `hypotheses.h-e1.validation.status` to COMPLETED (if passed)
  - Set `hypotheses.h-e1.gate.satisfied` to true/false
  - Record validation metrics

**Implementation Notes:**
- Use markdown tables for readability
- Include timestamps and hypothesis ID in all outputs
- Link to generated visualizations

---

## Non-Functional Requirements

### NFR1: Performance
- Dataset preparation: ≤3 hours (checkpoint download time)
- Feature extraction: ≤30 minutes (CPU-only, sequential processing)
- Training: ≤1 minute (42 samples, 5 features)
- Evaluation: ≤5 minutes (metrics + visualization generation)
- **Total end-to-end runtime:** ≤4 hours

### NFR2: Resource Constraints
- **CPU:** 4+ cores (checkpoint download parallelization)
- **RAM:** 8 GB minimum (load multiple models)
- **Storage:** 20 GB (15 GB checkpoints + 5 GB workspace)
- **GPU:** NOT REQUIRED (checkpoint-only extraction)
- **Network:** Internet required for initial download, cached afterward

### NFR3: Reproducibility
- Fixed random seeds: `random_state=42` (sklearn), `seed=42` (numpy)
- Dependency version pinning:
  - Python 3.9+
  - PyTorch 2.1+
  - TIMM 1.0.9
  - scikit-learn 1.3+
  - pandas, numpy, matplotlib
- Deterministic train/val split via stratified sampling

### NFR4: Maintainability
- Modular script structure (5 independent scripts):
  - `01_prepare_data.py` (dataset creation)
  - `02_validate_assumptions.py` (A1/A2/A3 tests)
  - `03_train_classifier.py` (model training)
  - `04_evaluate.py` (validation metrics)
  - `05_analyze_failures.py` (diagnostic analysis)
- Clear file organization:
  - `data/` (CSV features)
  - `models/` (trained artifacts)
  - `results/` (metrics, plots, reports)
  - `scripts/` (Python executables)
- Execution log: `experiment_log.txt` with timestamps

### NFR5: Extensibility
- Feature vector design supports adding new features (e.g., activation counts, embedding dimensions)
- Dataset expansion supported (current 60 → future 100+ models)
- Classifier swap supported (LogisticRegression → SVM/MLP if needed)

---

## Data Specifications

### Input Data
- **Source:** TIMM Model Zoo (PyTorch Image Models library v1.0.9+)
- **Access Method:** Programmatic API via `timm.create_model()`
- **Sample Size:** 60 pretrained models
- **Format:** PyTorch state_dict (`.pth` or `.bin` checkpoint files)
- **Storage Location:** `~/.cache/torch/hub/checkpoints/` (auto-managed by TIMM)

### Feature Schema
```python
{
    'model_name': str,           # e.g., 'resnet50'
    'family': str,               # 'CNN' | 'Transformer' | 'Hybrid'
    'bn_count': int,             # BatchNorm layer count
    'ln_count': int,             # LayerNorm layer count
    'gn_count': int,             # GroupNorm layer count
    'no_norm_flag': int,         # 0 or 1
    'param_mass_ratio': float    # [0.0, 1.0]
}
```

### Output Data
- **Train CSV:** `data/train_features.csv` (42 rows × 7 columns)
- **Validation CSV:** `data/val_features.csv` (18 rows × 7 columns)
- **Model Artifacts:** `models/classifier.pkl`, `models/scaler.pkl`
- **Results Report:** `results/h_e1_results.md` (markdown document)
- **Visualizations:** PNG images (confusion matrix, feature importance, R distribution)

---

## Success Metrics

### Primary Metric
| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| Validation Macro-Accuracy | >80% | `sklearn.metrics.accuracy_score()` on held-out validation set |

### Secondary Metrics
| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| CNN Per-Class Accuracy | ≥75% | Precision from `classification_report()` |
| Transformer Per-Class Accuracy | ≥75% | Precision from `classification_report()` |
| Hybrid Per-Class Accuracy | ≥75% | Precision from `classification_report()` |
| ResNet Family CV | <0.15 | Coefficient of variation: std(R) / mean(R) |

### Tertiary Metrics (Diagnostic)
| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| Feature Importance Rank | param_mass_ratio or ln_count in top 2 | Absolute coefficient magnitude |
| Confusion Matrix Symmetry | No single-direction collapse | Visual inspection of off-diagonal elements |
| Failure Case Count | ≤3 misclassified models (out of 18) | Count where y_val ≠ y_pred |

---

## Decision Gates

### MUST_WORK Gate (Primary)
**Condition:** Validation macro-accuracy > 80%

**If PASSED:**
- Action: Proceed to H-M1, H-M2, H-M3 (mechanism hypotheses)
- Update: `verification_state.yaml` → `hypotheses.h-e1.gate.satisfied = true`
- Document: Results in `results/h_e1_results.md`

**If FAILED (accuracy ≤80%):**
- Action paths:
  1. If accuracy <50%: **ABANDON** hypothesis → Shift to complex representations (GNN approach)
  2. If accuracy 50-80%: **PIVOT** → Test alternative features (GroupNorm patterns, activation functions)
- Update: `verification_state.yaml` → `hypotheses.h-e1.gate.satisfied = false`
- Document: Failure analysis in `results/h_e1_failure_analysis.md`

### Secondary Gate (Per-Class Collapse Check)
**Condition:** All class accuracies ≥75%

**If ANY class <75%:**
- Action: Analyze confusion matrix for collapse pattern
- Example: Hybrid → CNN confusion suggests parameter-mass ratio overlap
- Recommendation: Add hybrid-specific features or refine classification boundary

---

## Risk Mitigation

### R1: TIMM Naming Misalignment (>10%)
- **Detection:** Pre-validate 10-model sample via structural inspection
- **Mitigation:** Add structural validation layer using state_dict key patterns
- **Contingency:** Reduce dataset to high-confidence subset (40-50 models)

### R2: Normalization Convention Violation (>15%)
- **Detection:** Monitor violation rates during data preparation
- **Mitigation:** Add GroupNorm counts, test activation function patterns
- **Contingency:** Explore alternative features (attention layers, embedding dimensions)

### R3: Scale Invariance Failure (CV ≥0.15)
- **Detection:** Pre-validate ResNet family before full experiment
- **Mitigation:** Use R-rank or normalize by model size: `R_norm = R / log(total_params)`
- **Contingency:** Document limitation: "Approach works within single scale, not across scales"

### R4: Checkpoint Download Timeout
- **Detection:** Monitor download progress, timeout after 30 min per model
- **Mitigation:** Use TIMM's caching, parallelize downloads
- **Contingency:** Substitute unavailable models with similar architectures

### R5: Memory Overflow (>8 GB RAM)
- **Detection:** Monitor RAM usage during feature extraction
- **Mitigation:** Extract features sequentially, delete models after processing
- **Contingency:** Run extraction in batches (10 models at a time)

---

## Implementation Roadmap

### Phase 1: Setup (Est. 30 min)
- Install dependencies: `pip install timm==1.0.9 torch sklearn pandas matplotlib`
- Create directory structure: `data/`, `models/`, `results/`, `scripts/`
- Initialize logging: `experiment_log.txt`

### Phase 2: Data Preparation (Est. 2-3 hours)
- Download 60 model checkpoints via TIMM
- Extract 5 features from each model
- Create train/val DataFrames with stratified split
- Save to CSV files
- **Validation checkpoint:** Run A1, A2, A3 assumption tests

### Phase 3: Training (Est. 5 min)
- Load train features, apply StandardScaler
- Fit LogisticRegression classifier
- Save model artifacts

### Phase 4: Evaluation (Est. 5 min)
- Predict on validation set
- Compute metrics (macro-accuracy, per-class, confusion matrix)
- Generate visualizations
- **Success checkpoint:** Verify macro_accuracy > 0.80

### Phase 5: Reporting (Est. 30 min)
- Generate plots and results document
- Update verification_state.yaml
- Document next steps

**Total Estimated Timeline:** 3-4 hours

---

## Acceptance Criteria Summary

### Definition of Done
- [ ] 60 models downloaded and features extracted
- [ ] Train/validation CSV files created with correct stratification
- [ ] Assumption validation tests (A1, A2, A3) executed and passed
- [ ] LogisticRegression classifier trained and saved
- [ ] Validation accuracy computed: >80% (MUST_WORK)
- [ ] Per-class accuracies computed: all ≥75%
- [ ] Confusion matrix, feature importance, R distribution plots generated
- [ ] Results document (`h_e1_results.md`) created
- [ ] verification_state.yaml updated with validation status

### Verification Methods
- **Unit Tests:** Feature extraction function tests (normalization count accuracy, parameter ratio computation)
- **Integration Tests:** End-to-end pipeline test (mock 5-model dataset)
- **Manual Inspection:** Verify ResNet-50 has BatchNorm, ViT-Base has LayerNorm
- **Statistical Validation:** A1/A2/A3 assumption tests

---

## Appendix

### A. Model Selection Details

**CNN Family (24 models):**
```
resnet18, resnet34, resnet50, resnet101, resnet152,
mobilenetv3_large_100, efficientnet_b0, efficientnet_b4,
densenet121, densenet201, vgg16, vgg19,
convnext_tiny, convnext_base,
resnext50_32x4d, wide_resnet50_2,
regnetx_032, regnety_032,
seresnet50, senet154,
inception_v3, inception_v4,
dpn68, dpn131
```

**Transformer Family (24 models):**
```
vit_tiny_patch16_224, vit_small_patch16_224, vit_base_patch16_224, vit_large_patch16_224,
deit_tiny_patch16_224, deit_small_patch16_224, deit_base_patch16_224, deit_base_distilled_patch16_224,
swin_tiny_patch4_window7_224, swin_small_patch4_window7_224, swin_base_patch4_window7_224,
beit_base_patch16_224,
twins_pcpvt_base, twins_svt_base,
cait_s24_224,
coat_lite_medium,
levit_256, levit_384,
poolformer_m36, poolformer_m48,
xcit_small_12_p16_224,
crossvit_base_240
```

**Hybrid Family (12 models):**
```
resnetv2_50x1_bit_distilled, convit_base,
pit_b_224, pit_s_224,
cait_xxs24_224,
mixer_b16_224, mixer_l16_224,
convnext_base_in22k,
twins_pcpvt_small,
visformer_small,
tnt_s_patch16_224,
maxvit_tiny_tf_224
```

### B. Related Work

**Chun et al. 2026:** LayerNorm reduces loss landscape curvature → Validates assumption A2 (normalization reflects paradigm)

**Fang et al. 2024:** Heterogeneous structures have diverged importance → Validates parameter-mass ratio as discriminative feature

**Kofinas et al. 2024:** GNN-based classification (high complexity, 50+ hours) → Baseline comparison for simple features approach

---

**End of PRD**
