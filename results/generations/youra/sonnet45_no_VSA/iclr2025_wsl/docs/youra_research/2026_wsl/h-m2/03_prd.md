# Product Requirements Document: H-M2 Parameter Allocation Pattern

**Hypothesis ID:** h-m2  
**Type:** MECHANISM  
**Gate:** MUST_WORK  
**Date:** 2026-07-11  
**Author:** YouRA Pipeline Phase 3  

---

## 1. Executive Summary

### 1.1 Product Vision
Build a parameter allocation pattern analysis system that validates the hypothesis: CNNs show high parameter-mass ratio R (>0.6), Transformers show low R (<0.2), with inter-family Cohen's d >1.0 and intra-family CV <0.15, demonstrating that parameter allocation patterns reflect architectural computation style.

### 1.2 Business Context
**Prerequisite:** H-M1 validated normalization fingerprinting (0% CNN violation, 14.29% Transformer violation)  
**Strategic Goal:** Validate the second step of the causal mechanism—parameter allocation patterns as architectural signature  
**Success Impact:** Confirms that parameter-mass ratio provides strong inter-family separation while maintaining scale invariance

### 1.3 Key Metrics
- **Primary:** Cohen's d (CNN vs Transformer) >1.0, CV (ResNet family) <0.15 (MUST_WORK gate)
- **Secondary:** Statistical significance p <0.05, mean separation >0.4, edge case violation rate ≤25%

---

## 2. Problem Statement

### 2.1 Research Questions
**RQ1 (Primary):** Does the parameter-mass ratio R show strong inter-family separation (Cohen's d >1.0) between CNNs and Transformers while maintaining scale invariance (intra-family CV <0.15)?

**RQ2-RQ4 (Secondary):**
- RQ2: What are the empirical R distributions for CNN, Transformer, and Hybrid families?
- RQ3: Does the parameter-mass ratio remain stable across model scales (ResNet-18 to ResNet-152)?
- RQ4: How do edge case architectures (NormFree, ConvNeXt, MLP-Mixer) affect R distributions?

### 2.2 Current State (from H-E1/H-M1)
- ✅ H-E1: 88.89% validation accuracy, param_mass_ratio feature importance 0.777 (dominant feature)
- ✅ H-M1: Normalization fingerprinting validated (0% CNN violation, 14.29% Transformer violation)
- ✅ Dataset: 50 TIMM models (32 train, 18 val), features already extracted
- ⚠️ Edge cases: VGG-16 (NormFree), PoolFormer (MetaFormer), ConvNeXt, MLP-Mixer

### 2.3 User Needs
**Primary User:** YouRA pipeline (automated hypothesis validation)  
**Need:** Mechanistic evidence that parameter allocation patterns provide strong inter-family separation with scale invariance

---

## 3. Product Requirements

### 3.1 Functional Requirements

#### FR1: Parameter-Mass Ratio Computation (Reuse from H-E1)
- **ID:** FR1
- **Description:** Compute R = conv_params / (conv_params + linear_params_no_head) from TIMM checkpoints
- **Input:** PyTorch state_dict (OrderedDict)
- **Output:** `{param_mass_ratio: float}`
- **Method:** 
  - Count parameters in 4D tensors (convolution weights)
  - Count parameters in 2D tensors (linear weights), excluding classification head
  - R = conv_params / (conv_params + linear_params_no_head)
- **Head Exclusion:** Skip keys containing 'head', 'fc', 'classifier'
- **Acceptance Criteria:**
  - Reuse `_compute_param_mass_ratio()` from h-e1/code/src/feature_extractor.py
  - Manual validation: 95% accuracy on 5 sample models (compare with manual counting)
  - Handles edge cases: VGG-16 (R ≈ 1.0), MLP-Mixer (ambiguous R)

#### FR2: Inter-Family Separation Analysis (Cohen's d)
- **ID:** FR2
- **Description:** Compute Cohen's d effect size between CNN and Transformer R distributions
- **Input:** Features dataframe with columns ['family', 'param_mass_ratio']
- **Output:** `{cohens_d: float, p_value: float, t_statistic: float, mean_cnn: float, mean_transformer: float, std_cnn: float, std_transformer: float}`
- **Method:**
  ```python
  cohens_d = (μ_CNN - μ_Transformer) / σ_pooled
  σ_pooled = sqrt(((n_CNN - 1) * σ²_CNN + (n_Transformer - 1) * σ²_Transformer) / (n_CNN + n_Transformer - 2))
  ```
- **Statistical Test:** Independent samples t-test (two-tailed)
- **Acceptance Criteria:**
  - Cohen's d >1.0 (P1 MUST_WORK gate - very large effect)
  - p-value <0.05 (S1 secondary criterion - statistical significance)
  - Mean separation >0.4 (S2 secondary criterion - practical separation)

#### FR3: Intra-Family Scale Invariance (Coefficient of Variation)
- **ID:** FR3
- **Description:** Validate scale invariance by computing CV = σ / μ across model scales
- **Input:** Features dataframe with scale families (ResNet, EfficientNet, ViT)
- **Output:** `{family_name: {cv: float, mean_R: float, std_R: float, models: list, passed: bool}}`
- **Primary Test:** ResNet family (resnet18, resnet34, resnet50, resnet101, resnet152)
- **Secondary Tests:** EfficientNet-B{0,4}, ViT-{tiny,small,base,large}
- **Acceptance Criteria:**
  - CV <0.15 for ResNet family (P2 MUST_WORK gate)
  - CV <0.15 for at least 1 Transformer scale family (secondary)
  - Individual model R values tracked for scale progression analysis

#### FR4: R Distribution Visualization
- **ID:** FR4
- **Description:** Generate distribution plots for R values per family
- **Input:** Features dataframe with columns ['family', 'param_mass_ratio']
- **Output:** PNG file with 3 subplots (violin plot, box plot, histogram with KDE)
- **Visualizations:**
  1. Violin plot: R distributions for CNN/Transformer/Hybrid with threshold lines (0.6, 0.2)
  2. Box plot: Outlier detection per family
  3. Histogram: KDE with family means marked
- **Acceptance Criteria:**
  - All 3 visualizations generated successfully
  - Threshold lines visible (CNN >0.6, Transformer <0.2)
  - Outliers flagged for edge case analysis
  - Saved to `outputs/R_distributions.png`

#### FR5: Edge Case Detection and Analysis
- **ID:** FR5
- **Description:** Identify models violating expected R thresholds
- **Input:** Features dataframe with columns ['model_name', 'family', 'param_mass_ratio']
- **Output:** `{cnn_low_R: list, transformer_high_R: list, hybrid_outliers: list, cnn_violation_rate: float, transformer_violation_rate: float}`
- **Violation Definitions:**
  - CNN violation: R <0.6 (not convolution-dominant)
  - Transformer violation: R >0.2 (not linear-dominant)
  - Hybrid outlier: R <0.2 or R >0.6 (not in mixed range)
- **Known Edge Cases:**
  - VGG-16 (NormFree): Expected R ≈ 1.0 (purely convolutional)
  - ConvNeXt: Expected R >0.6 (still conv-dominant despite LayerNorm)
  - PoolFormer (MetaFormer): Expected R <0.2 (linear-dominant)
  - MLP-Mixer: Expected 0.2 < R < 0.6 (balanced)
- **Acceptance Criteria:**
  - Edge case violation rate ≤25% (S3 secondary criterion - higher tolerance for boundary architectures)
  - All violators documented in `outputs/edge_cases.json`
  - Manual validation of known edge cases (VGG-16, PoolFormer, ConvNeXt, MLP-Mixer)

#### FR6: Gate Decision Report
- **ID:** FR6
- **Description:** Generate gate decision based on primary criteria evaluation
- **Input:** Cohen's d results, CV results
- **Output:** `{gate_decision: 'PASS' | 'FAIL', reasoning: str, failure_mode: str | null}`
- **Decision Logic:**
  ```python
  if cohens_d > 1.0 and cv < 0.15:
      gate_decision = 'PASS'
  elif cohens_d <= 1.0:
      gate_decision = 'FAIL'
      failure_mode = 'Weak inter-family separation (Cohen's d ≤1.0) → EXPLORE alternative ratios'
  elif cv >= 0.15:
      gate_decision = 'FAIL'
      failure_mode = 'Scale confounding (CV ≥0.15) → PIVOT to normalized R'
  ```
- **Acceptance Criteria:**
  - Gate decision documented in `outputs/gate_decision.txt`
  - Failure mode analysis completed if FAIL
  - Recommendation provided for next steps (PASS → H-M3, FAIL → remediation path)

### 3.2 Data Requirements

#### DR1: Dataset Reuse from H-E1
- **Source:** TIMM Model Zoo (50 models)
- **Split:** 32 train, 18 validation (same split as h-e1)
- **Families:** CNN (16 train, 7 val), Transformer (15 train, 7 val), Hybrid (5 train, 4 val)
- **Features:** Reuse h-e1 extracted features (param_mass_ratio already computed)
- **Access:**
  ```python
  train_features = pd.read_csv('h-e1/code/data/train_features.csv')
  val_features = pd.read_csv('h-e1/code/data/val_features.csv')
  ```
- **Acceptance Criteria:**
  - Features loaded successfully from h-e1 cache
  - param_mass_ratio column present in both train and val
  - 50 total models (32 + 18)

#### DR2: Scale Family Membership
- **ResNet Family:** resnet18, resnet34, resnet50, resnet101, resnet152
- **EfficientNet Family:** efficientnet_b0, efficientnet_b4
- **ViT Family:** vit_tiny_patch16_224, vit_small_patch16_224, vit_base_patch16_224, vit_large_patch16_224
- **Purpose:** Scale invariance validation (CV <0.15)
- **Acceptance Criteria:**
  - At least ResNet-{18,34,50,101,152} present in dataset
  - Scale family membership documented in config.py

### 3.3 Non-Functional Requirements

#### NFR1: Code Reuse from H-E1/H-M1
- **Requirement:** Maximize code reuse from validated components
- **Reusable Components:**
  1. `h-e1/code/src/feature_extractor.py` → `_compute_param_mass_ratio()`
  2. `h-e1/code/src/data_loader.py` → TIMM model loading
  3. `h-e1/code/config.py` → Model families, thresholds
  4. `h-m1/code/src/violation_analyzer.py` → Violation rate computation pattern
- **New Modules:**
  1. `src/cohens_d_analyzer.py` → Inter-family effect size
  2. `src/scale_invariance_validator.py` → Intra-family CV
  3. `src/distribution_visualizer.py` → R distribution plots
  4. `src/edge_case_analyzer.py` → Threshold violation detection
- **Acceptance Criteria:** ≥70% code reuse (4 new modules vs 10+ reused)

#### NFR2: Runtime Performance
- **Requirement:** Total runtime ≤10 minutes (CPU-only)
- **Breakdown:**
  - Feature loading: <1 min (reuse h-e1 cached features)
  - Cohen's d analysis: <2 min (statistical computation)
  - CV validation: <1 min (per scale family)
  - Distribution visualization: <2 min (matplotlib/seaborn)
  - Edge case detection: <1 min (threshold filtering)
  - Report generation: <2 min (JSON + text outputs)
- **Acceptance Criteria:** End-to-end runtime ≤10 min on standard CPU

#### NFR3: Reproducibility
- **Requirement:** Deterministic results for same TIMM model zoo
- **Constraints:**
  - Fixed random seed: 42 (same as h-e1/h-m1)
  - Fixed TIMM version: 1.0.9
  - Fixed train/val split (same 32/18 models)
  - Fixed statistical methods (SciPy implementations)
- **Acceptance Criteria:** Bit-identical results across runs

#### NFR4: Memory Efficiency
- **Requirement:** Peak RAM ≤8 GB (laptop-friendly)
- **Constraints:**
  - Features loaded once (not per analysis)
  - Models NOT loaded (features already extracted in h-e1)
  - Visualizations generated sequentially (not all in memory)
- **Acceptance Criteria:** Peak RAM ≤8 GB measured via memory profiler

#### NFR5: Output Completeness
- **Requirement:** Generate all required outputs for 04_validation.md
- **Outputs:**
  1. `outputs/cohens_d_report.json` → Effect size, p-value, confidence intervals
  2. `outputs/cv_report.json` → CV values per family, scale invariance results
  3. `outputs/R_distributions.png` → Violin/box/histogram plots
  4. `outputs/edge_cases.json` → Models violating R thresholds
  5. `outputs/gate_decision.txt` → PASS/FAIL status with reasoning
- **Acceptance Criteria:** All 5 outputs generated successfully

---

## 4. Success Criteria

### 4.1 Primary Criteria (MUST_WORK Gate)

| Criterion | Metric | Threshold | Rationale |
|-----------|--------|-----------|-----------|
| **P1: Inter-Family Separation** | Cohen's d (CNN vs Transformer) | >1.0 | Strong effect size validates allocation pattern hypothesis |
| **P2: Intra-Family Scale Invariance** | CV across ResNet-{18,34,50,101,152} | <0.15 | R must be scale-stable, not size-dependent |

**Gate Decision:**
- **PASS:** Both P1 AND P2 meet thresholds → Proceed to next hypothesis
- **FAIL (P1):** Cohen's d ≤1.0 → **EXPLORE** alternative ratios (attention_params / total_params)
- **FAIL (P2):** CV ≥0.15 → **PIVOT** to normalized ratio (R_rank or size-adjusted R)

### 4.2 Secondary Criteria

| Criterion | Metric | Threshold | Purpose |
|-----------|--------|-----------|---------|
| **S1: Statistical Significance** | t-test p-value (CNN vs Transformer) | <0.05 | Confirm separation is not random |
| **S2: Distribution Separation** | Mean R_CNN - Mean R_Transformer | >0.4 | Practical separation (0.6 - 0.2 = 0.4) |
| **S3: Edge Case Robustness** | Violation rate on edge cases | ≤25% | Higher tolerance for boundary architectures |

### 4.3 Failure Mode Analysis

**Potential Failure Scenarios:**

1. **Failure Mode 1: Scale Confounding (CV ≥0.15)**
   - **Symptom:** R increases with model size (ResNet-18 ≠ ResNet-152)
   - **Diagnosis:** Parameter allocation reflects scale, not structure
   - **Response:** PIVOT to normalized R = (R - μ_family) / σ_family

2. **Failure Mode 2: Weak Separation (Cohen's d ≤1.0)**
   - **Symptom:** Overlapping R distributions for CNN and Transformer
   - **Diagnosis:** Parameter-mass ratio insufficient for discrimination
   - **Response:** EXPLORE alternative features (attention_params, embedding_dim)

3. **Failure Mode 3: Hybrid Misalignment**
   - **Symptom:** Hybrid R values cluster with CNNs or Transformers (not intermediate)
   - **Diagnosis:** Hybrid architectures not structurally balanced
   - **Response:** DOCUMENT as boundary case (acceptable for SHOULD_WORK hypotheses)

---

## 5. Dependencies & Risks

### 5.1 Prerequisites
- ✅ H-E1 completed (features extracted, 88.89% accuracy)
- ✅ H-M1 validated (normalization fingerprinting, MUST_WORK gate PASSED)
- ✅ TIMM model zoo accessible (50 models, 70/30 split)

### 5.2 High-Risk Assumptions

| Risk ID | Assumption | Mitigation |
|---------|------------|------------|
| **R1** | R is scale-invariant (CV <0.15) | Pre-validate on ResNet family before full experiment |
| **R2** | CNN/Transformer separation is strong (d >1.0) | Fallback to normalized R if raw R shows weak separation |
| **R3** | Head exclusion is correct | Manual validation on 5 models (compare with/without head) |

### 5.3 External Dependencies
- Python 3.8+
- PyTorch 2.1+ (for checkpoint loading if needed, though features are pre-extracted)
- NumPy, Pandas, Scikit-learn, SciPy, Matplotlib, Seaborn
- TIMM 1.0.9 (model zoo)
- Hardware: CPU-only, 8GB RAM, <100MB storage

---

## 6. Timeline & Milestones

### 6.1 Implementation Breakdown (FULL tier, 30 task budget)

**Note:** Specific task allocation determined in Phase 3 Step 4 (Budget Allocation) and Step 9 (Task Generation)

**Estimated Complexity:** MEDIUM (reuses h-e1 features, adds statistical analysis)

**Key Implementation Areas:**
1. Dataset preparation (reuse h-e1 features)
2. Cohen's d analysis module
3. Scale invariance validation module
4. Distribution visualization module
5. Edge case detection module
6. Report generation and gate decision logic

### 6.2 Compute Requirements
- **Environment:** Python 3.8+, PyTorch 2.1+
- **Hardware:** CPU-only, 8GB RAM
- **Storage:** <100MB (reusing h-e1 cached features)
- **Execution Time:** <10 minutes total

---

## 7. Validation Checklist

**Pre-Experiment Validation:**
- [ ] h-e1 features available at `h-e1/code/data/{train,val}_features.csv`
- [ ] h-m1 completed with PASS gate decision
- [ ] Manual validation: R computation matches manual counting (5 models, 95% accuracy)
- [ ] ResNet family present in dataset (18, 34, 50, 101, 152)

**Experiment Execution:**
- [ ] Cohen's d computed for CNN vs Transformer (validation set)
- [ ] CV computed for ResNet family (training set)
- [ ] Statistical significance tested (t-test, p-value)
- [ ] Distribution plots generated (violin, box, histogram)
- [ ] Edge cases identified and documented

**Post-Experiment Validation:**
- [ ] Primary criteria (P1: d >1.0, P2: CV <0.15) evaluated
- [ ] Secondary criteria (S1-S3) evaluated
- [ ] Gate decision documented (PASS/FAIL + reasoning)
- [ ] Failure mode analysis completed (if FAIL)
- [ ] Results exported to 04_validation.md

---

## 8. References

### 8.1 Theoretical Foundation
- **Fang et al. 2024:** Heterogeneous structures show diverged importance distributions
- **Chun et al. 2026:** LayerNorm reduces Last Layer Complexity vs BatchNorm
- **H-M1 (prerequisite):** Normalization layer choice as architectural signature (VALIDATED)

### 8.2 Baseline Comparison
- **H-E1:** param_mass_ratio feature importance 0.777 (dominant feature)
- **Kofinas et al. 2024 GNN:** Complex graph construction (50+ hours) vs simple R metric
- **Zhang & Abdulla 2023:** Runtime statistics (expensive) vs checkpoint-only counting

---

**END OF PRD**

**Next Steps:**
1. Proceed to Step 3: Architecture Agent generation
2. Define Epic tasks with complexity scores
3. Generate Logic, Config documents via parallel agents
4. Create 03_tasks.yaml implementation plan
