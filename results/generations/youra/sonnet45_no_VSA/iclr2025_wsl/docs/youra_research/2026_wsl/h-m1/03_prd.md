# Product Requirements Document: H-M1 Normalization Layer Fingerprinting

**Hypothesis ID:** h-m1  
**Type:** MECHANISM  
**Gate:** MUST_WORK  
**Date:** 2026-07-11  
**Author:** YouRA Pipeline Phase 3  

---

## 1. Executive Summary

### 1.1 Product Vision
Build a normalization layer fingerprinting system that validates the hypothesis: CNNs show predominantly BatchNorm (>80%), Transformers show predominantly LayerNorm (>80%), and Hybrids show mixed patterns via state_dict key regex matching.

### 1.2 Business Context
**Prerequisite:** H-E1 validated statistical feature classification with 88.89% accuracy  
**Strategic Goal:** Validate the first step of the causal mechanism—normalization layer choice as architectural signature  
**Success Impact:** Confirms Chun 2026's theoretical finding manifests empirically as a discriminative feature

### 1.3 Key Metrics
- **Primary:** CNN violation rate ≤15%, Transformer violation rate ≤15% (MUST_WORK gate)
- **Secondary:** Feature importance (bn_count, ln_count > 0.1), regex accuracy ≥95%, edge case detection 100%

---

## 2. Problem Statement

### 2.1 Research Questions
**RQ1 (Primary):** Do normalization layer counts (BN, LN, GN) reliably fingerprint architecture families (CNN/Transformer/Hybrid) with violation rates ≤15% per class?

**RQ2-RQ4 (Secondary):**
- RQ2: What is the feature importance ranking of normalization counts in the logistic regression classifier?
- RQ3: How do edge case architectures (NormFree, MetaFormer) affect normalization fingerprinting accuracy?
- RQ4: Does adding fallback heuristics (`no_norm_flag`) mitigate edge case failures?

### 2.2 Current State (from H-E1)
- ✅ 88.89% validation accuracy achieved
- ✅ Feature importance: bn_count (0.353), ln_count (0.171) contribute to classification
- ✅ Assumption A2 validated: CNN LayerNorm 0%, Transformer BatchNorm 13.33%
- ⚠️ Edge cases: VGG-16 (NormFree), PoolFormer (MetaFormer)

### 2.3 User Needs
**Primary User:** YouRA pipeline (automated hypothesis validation)  
**Need:** Mechanistic evidence that normalization layer choice is a reliable architectural signature

---

## 3. Product Requirements

### 3.1 Functional Requirements

#### FR1: Normalization Layer Extraction
- **ID:** FR1
- **Description:** Extract BatchNorm, LayerNorm, GroupNorm counts from TIMM model checkpoints
- **Input:** PyTorch state_dict (OrderedDict)
- **Output:** `{bn_count: int, ln_count: int, gn_count: int, no_norm_flag: int}`
- **Method:** Regex pattern matching on state_dict keys
- **Patterns:**
  - BatchNorm: `r'bn|batch_norm|batchnorm'` (case-insensitive)
  - LayerNorm: `r'ln|layer_norm|layernorm'` (case-insensitive)
  - GroupNorm: `r'gn|group_norm|groupnorm'` (case-insensitive)
- **Fallback:** `no_norm_flag = 1` if total_norm == 0 (NormFree detection)
- **Acceptance Criteria:**
  - Regex accuracy ≥95% vs manual counting (10 sample validation)
  - Handles edge cases: VGG-16 (NormFree), ConvNeXt (LayerNorm CNN)

#### FR2: Violation Rate Analysis
- **ID:** FR2
- **Description:** Compute per-class violation rates for normalization layer paradigms
- **Input:** Features dataframe + family labels
- **Output:** `{cnn_violation_rate: float, transformer_violation_rate: float, violations: list}`
- **Violation Definitions:**
  - CNN violation: `ln_count > bn_count` (LayerNorm dominates)
  - Transformer violation: `bn_count > ln_count` (BatchNorm dominates)
  - Hybrid: No violation (expected mixed patterns)
- **Acceptance Criteria:**
  - CNN violation rate ≤15% (P1 MUST_WORK gate)
  - Transformer violation rate ≤15% (P2 MUST_WORK gate)
  - Per-model violation tracking (identify violators: VGG-16, PoolFormer)

#### FR3: Feature Importance Extraction
- **ID:** FR3
- **Description:** Rank normalization counts by discriminative power in logistic regression
- **Input:** Trained classifier (reuse from h-e1), feature names
- **Output:** `{feature: coefficient, rank: int}` (sorted descending)
- **Method:** Average absolute coefficient across 3 classes (CNN, Transformer, Hybrid)
- **Expected Ranking (within norm features):** bn_count > ln_count > gn_count
- **Acceptance Criteria:**
  - bn_count coefficient > 0.1 (S1 secondary criterion)
  - ln_count coefficient > 0.1 (S1 secondary criterion)
  - Comparison with h-e1 baseline (param_mass_ratio still dominant)

#### FR4: Normalization Distribution Analysis
- **ID:** FR4
- **Description:** Compute per-family normalization layer statistics (mean, median, std, dominant type)
- **Input:** Features dataframe + family labels
- **Output:** `{family: {bn_count: {mean, median, std}, ..., dominant_norm: str}}`
- **Families:** CNN, Transformer, Hybrid
- **Acceptance Criteria:**
  - CNN dominant_norm == 'BatchNorm' (expected)
  - Transformer dominant_norm == 'LayerNorm' (expected)
  - Hybrid dominant_norm == 'Mixed' (expected)

#### FR5: Edge Case Detection
- **ID:** FR5
- **Description:** Identify and categorize edge case models (NormFree, MetaFormer, ConvNeXt)
- **Input:** Features dataframe + model names
- **Output:** `{category: [model_name, features, notes]}`
- **Categories:**
  - NormFree: `no_norm_flag == 1` (e.g., VGG-16)
  - MetaFormer: `'poolformer' in model_name` (non-standard LayerNorm)
  - ConvNeXt: `'convnext' in model_name` (modern CNN with LayerNorm)
- **Acceptance Criteria:**
  - NormFree detection rate 100% (S3 secondary criterion)
  - Edge case models flagged for review

### 3.2 Non-Functional Requirements

#### NFR1: Code Reuse from H-E1
- **Requirement:** Reuse h-e1 components to minimize implementation time
- **Components:**
  1. `StatisticalFeatureExtractor.extract_features()` → normalization counting already implemented
  2. `TIMMModelLoader.load_models()` → 50 models, 70/30 split
  3. `LogisticRegression` classifier → trained in h-e1
  4. `NORM_PATTERNS` regex → defined in h-e1/code/config.py
- **Acceptance Criteria:** ≥80% code reuse (5 new classes vs 20+ existing)

#### NFR2: Runtime Performance
- **Requirement:** Total runtime ≤20 minutes (CPU-only, no GPU)
- **Breakdown:**
  - Model loading: 10 min (50 models × 12 sec)
  - Feature extraction: 2 min (regex matching)
  - Violation analysis: 1 min
  - Distribution analysis: 1 min
  - Report generation: 2 min
- **Acceptance Criteria:** End-to-end runtime ≤20 min on standard CPU

#### NFR3: Reproducibility
- **Requirement:** Deterministic results for same TIMM model zoo
- **Constraints:**
  - Fixed random seed: 42 (same as h-e1)
  - Fixed TIMM version: 1.0.9
  - Fixed train/val split (same 32/18 models as h-e1)
- **Acceptance Criteria:** Bit-identical results across runs

#### NFR4: Memory Efficiency
- **Requirement:** Peak RAM ≤8 GB (laptop-friendly)
- **Constraints:**
  - Load models sequentially (not all 50 in memory)
  - Release state_dict after feature extraction
- **Acceptance Criteria:** Memory profiling shows peak ≤8 GB

---

## 4. System Architecture

### 4.1 High-Level Architecture
```
[TIMM Model Zoo] → [Feature Extractor (h-e1 reuse)] → [Violation Analyzer (new)]
                                                     ↓
                                      [Distribution Analyzer (new)] → [Report Generator]
                                                     ↓
                                         [Edge Case Detector (new)]
```

### 4.2 Data Flow
1. **Input:** TIMM model names (50 models from h-e1 config)
2. **Load:** `timm.create_model(pretrained=True)` → state_dict
3. **Extract:** Regex count `bn_count`, `ln_count`, `gn_count`, `no_norm_flag`, `param_mass_ratio`
4. **Analyze:** Violation rates, distributions, edge cases
5. **Output:** CSV reports, JSON distributions, validation markdown

### 4.3 Component Diagram
```
┌─────────────────────────────────────────────────────────────┐
│ H-M1 Normalization Fingerprinting System                    │
├─────────────────────────────────────────────────────────────┤
│ [Reused from H-E1]                                          │
│ - StatisticalFeatureExtractor (feature_extractor.py)       │
│ - TIMMModelLoader (data_loader.py)                          │
│ - LogisticRegression (classifier_trainer.py)                │
│ - NORM_PATTERNS (config.py)                                 │
├─────────────────────────────────────────────────────────────┤
│ [New H-M1 Components]                                       │
│ - ViolationRateAnalyzer (violation_analyzer.py)            │
│ - NormalizationDistributionAnalyzer (distribution_analyzer.py) │
│ - EdgeCaseDetector (edge_case_detector.py)                 │
│ - H_M1_Runner (main_h_m1.py)                                │
├─────────────────────────────────────────────────────────────┤
│ [Output Artifacts]                                          │
│ - h-m1_violation_rates.csv                                  │
│ - h-m1_feature_importance.csv                               │
│ - h-m1_norm_distributions.json                              │
│ - h-m1_edge_cases.json                                      │
│ - 04_validation.md                                          │
└─────────────────────────────────────────────────────────────┘
```

---

## 5. Success Criteria

### 5.1 Primary Success Criteria (MUST_WORK Gate)
| ID | Criterion | Metric | Threshold | Status |
|----|-----------|--------|-----------|--------|
| P1 | CNN Violation Rate | `cnn_violation_rate` | ≤15% | TBD |
| P2 | Transformer Violation Rate | `transformer_violation_rate` | ≤15% | TBD |

**Gate Decision:**
- **PASS:** Both P1 AND P2 meet thresholds → Proceed to H-M2
- **FAIL:** Either P1 OR P2 exceeds threshold → PIVOT to alternative features

### 5.2 Secondary Success Criteria
| ID | Criterion | Metric | Threshold | Status |
|----|-----------|--------|-----------|--------|
| S1 | Feature Importance | bn_count + ln_count coefficients | Both > 0.1 | TBD |
| S2 | Regex Accuracy | Manual validation match rate | ≥95% | TBD |
| S3 | Edge Case Handling | no_norm_flag detection for NormFree | 100% | TBD |

### 5.3 Pivot Actions (if Gate Fails)
**If P1 Fails (CNN violation >15%):**
- **Root Cause:** Modern CNNs adopting LayerNorm (e.g., ConvNeXt)
- **Pivot:** Add temporal feature (model release year) or refine taxonomy (Legacy vs Modern CNN)

**If P2 Fails (Transformer violation >15%):**
- **Root Cause:** Hybrid architectures mislabeled as Transformers
- **Pivot:** Add attention mechanism detection (Q/K/V weight counting)

---

## 6. Implementation Plan

### 6.1 Development Phases

#### Phase 1: Setup (Budget: 2 tasks)
- **Task 1.1:** Environment setup (venv, requirements.txt)
- **Task 1.2:** Copy h-e1 codebase to h-m1/code

#### Phase 2: Core Analysis (Budget: 7 tasks)
- **Task 2.1:** Implement ViolationRateAnalyzer
- **Task 2.2:** Implement NormalizationDistributionAnalyzer
- **Task 2.3:** Implement EdgeCaseDetector
- **Task 2.4:** Integrate with h-e1 FeatureExtractor
- **Task 2.5:** Load h-e1 trained classifier
- **Task 2.6:** Extract feature importance
- **Task 2.7:** Run violation rate analysis

#### Phase 3: Validation (Budget: 3 tasks)
- **Task 3.1:** Manual validation (10 models, S2 criterion)
- **Task 3.2:** Edge case verification (NormFree, MetaFormer, ConvNeXt)
- **Task 3.3:** Generate validation report (04_validation.md)

#### Phase 4: Output (Budget: 3 tasks)
- **Task 4.1:** Write violation_rates.csv
- **Task 4.2:** Write norm_distributions.json
- **Task 4.3:** Write edge_cases.json

**Total Budget:** 15 tasks (2 setup + 7 core + 3 validation + 3 output)

### 6.2 Dependencies
- **External:** h-e1 codebase (feature_extractor.py, data_loader.py, config.py)
- **Internal:** TIMM 1.0.9, PyTorch 2.1.0, scikit-learn 1.3.0

### 6.3 Risks and Mitigations
| Risk | Impact | Mitigation |
|------|--------|------------|
| ConvNeXt false positives | P1 gate failure | Document as "modern CNN" edge case, add temporal feature |
| DeiT stem BatchNorm | P2 gate marginal | Acceptable if ≤15% (h-e1 showed 13.33%) |
| Regex false negatives | S2 failure | Manual validation catches, expand regex if needed |
| GroupNorm irrelevance | S1 partial failure | Acceptable (gn_count = 0 confirmed in h-e1) |

---

## 7. Output Artifacts

### 7.1 Data Outputs
1. **h-m1_violation_rates.csv**
   - Columns: `family, total_models, violations, violation_rate, threshold, status`
   - Rows: CNN, Transformer (Hybrid has no violation definition)

2. **h-m1_feature_importance.csv**
   - Columns: `feature, coefficient, rank, interpretation`
   - Rows: bn_count, ln_count, gn_count, no_norm_flag, param_mass_ratio

3. **h-m1_norm_distributions.json**
   - Per-family statistics: mean, median, std for bn_count, ln_count, gn_count
   - Dominant normalization type per family

4. **h-m1_edge_cases.json**
   - NormFree models (VGG-16)
   - MetaFormer models (PoolFormer)
   - ConvNeXt models (modern CNN with LayerNorm)

### 7.2 Documentation Outputs
5. **04_validation.md**
   - Gate decision (PASS/FAIL)
   - Primary criteria results (P1, P2)
   - Secondary criteria results (S1, S2, S3)
   - Key findings and recommendations for H-M2

---

## 8. Timeline and Resources

### 8.1 Estimated Timeline
- **Setup:** 30 minutes
- **Implementation:** 3 hours (7 core tasks)
- **Validation:** 1 hour (manual checks)
- **Output generation:** 30 minutes
- **Total:** ~5 hours development time

### 8.2 Computational Resources
- **CPU:** Standard laptop (no GPU required)
- **RAM:** 8 GB peak
- **Storage:** 10 GB (TIMM checkpoint cache)
- **Runtime:** 15-20 minutes per execution

### 8.3 Human Resources
- **Developer:** 1 (Python ML engineer)
- **Reviewer:** 1 (YouRA pipeline validator)

---

## 9. Appendix

### 9.1 Related Documents
- **Phase 2C:** `docs/youra_research/h-m1/02c_experiment_brief.md` (experiment design)
- **H-E1 Validation:** `docs/youra_research/h-e1/04_validation.md` (prerequisite results)
- **Verification Plan:** `docs/youra_research/02b_verification_plan.md` (h-m1 specification)

### 9.2 Glossary
- **MUST_WORK Gate:** Hypothesis must pass primary criteria (P1, P2) or PIVOT
- **Violation:** CNN with dominant LayerNorm OR Transformer with dominant BatchNorm
- **NormFree:** Architecture with no normalization layers (no_norm_flag=1)
- **MetaFormer:** Token mixer architectures (PoolFormer, not pure Transformer)

### 9.3 References
- Chun et al. 2026: "LayerNorm reduces LLC by m/2 vs BatchNorm"
- Fang et al. 2024: "Heterogeneous structures have diverged importance distributions"
- H-E1 Results: 88.89% validation accuracy, feature importance validation

---

**Document Version:** 1.0  
**Last Updated:** 2026-07-11  
**Status:** APPROVED for Phase 3 Implementation
