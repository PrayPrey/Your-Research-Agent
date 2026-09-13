# Phase 2C Experiment Brief: H-M2 Parameter Allocation Pattern

**Hypothesis ID:** h-m2  
**Type:** MECHANISM  
**Gate Type:** MUST_WORK  
**Date:** 2026-07-11  
**Prerequisite:** h-m1 (VALIDATED - 0% CNN violation, 14.29% Transformer violation)  

---

## 1. Hypothesis Statement

**Full Statement:**  
Under checkpoint parameter counting, if parameter-mass ratio R = conv_params / (conv_params + linear_params_no_head) is computed, then CNNs show high R (>0.6), Transformers show low R (<0.2), and inter-family Cohen's d >1.0 because CNNs allocate to convolutional kernels (local receptive fields) while Transformers allocate to large linear projections (global attention).

**Rationale:**  
This hypothesis tests the second causal mechanism step—that parameter allocation patterns reflect architectural computation style. It validates Fang 2024's finding (heterogeneous structures have diverged importance distributions) as a discriminative feature.

**Prerequisite Results from H-M1:**
- ✅ CNN violation rate: 0.00% (0/7 models violated)
- ✅ Transformer violation rate: 14.29% (1/7 models violated - levit_384 edge case)
- ✅ Normalization dominance confirmed: CNN 100% BatchNorm, Transformer 85.71% LayerNorm
- ✅ Feature importance: `bn_count` (0.353), `ln_count` (0.171) both >0.1 threshold
- ⚠️ Edge cases: NormFree models (11/18), MetaFormer (PoolFormer), ConvNeXt variants

---

## 2. Research Questions

### Primary Question
**RQ1:** Does the parameter-mass ratio R show strong inter-family separation (Cohen's d >1.0) between CNNs and Transformers while maintaining scale invariance (intra-family CV <0.15)?

### Secondary Questions
**RQ2:** What are the empirical R distributions for CNN, Transformer, and Hybrid families?

**RQ3:** Does the parameter-mass ratio remain stable across model scales (ResNet-18 to ResNet-152)?

**RQ4:** How do edge case architectures (NormFree, ConvNeXt, MLP-Mixer) affect R distributions?

---

## 3. Experimental Design

### 3.1 Dataset Specification

**Source:** TIMM Model Zoo (reusing h-e1/h-m1 dataset)

**Model Selection (50 models total):**
- **Training Set:** 32 models (70% split from h-e1)
  - CNN: 16 models
  - Transformer: 15 models
  - Hybrid: 5 models (ResNetV2-BiT, ConViT, PiT, MLP-Mixer, Visformer, TnT, MaxViT)

- **Validation Set:** 18 models (30% split from h-e1)
  - CNN: 7 models (including VGG-16 NormFree edge case)
  - Transformer: 7 models (including PoolFormer MetaFormer)
  - Hybrid: 4 models

**Dataset Type:** `standard` (established TIMM model zoo, NOT synthetic)

**Dataset Characteristics:**
- **Scale:** Full TIMM pretrained checkpoints with state_dict access
- **Diversity:** Multi-family coverage (ResNet-{18,34,50,101,152} for CV validation)
- **Ground Truth:** TIMM naming validated by h-e1 (88.89% accuracy)
- **Reuse:** Features already extracted in h-e1/h-m1 pipelines

**Dataset Format:**
```python
# Each sample has pre-extracted features from h-e1
{
    'model_name': 'resnet50',
    'family': 'CNN',
    'features': {
        'bn_count': int,
        'ln_count': int,
        'gn_count': int,
        'no_norm_flag': int,
        'param_mass_ratio': float  # <-- H-M2 primary focus
    }
}
```

**Access Method:**
```python
# Reuse h-e1 extracted features
train_features = pd.read_csv('h-e1/code/data/train_features.csv')
val_features = pd.read_csv('h-e1/code/data/val_features.csv')

# Parameter-mass ratio already computed in h-e1 feature extraction
R_values = features_df['param_mass_ratio']
```

### 3.2 Parameter-Mass Ratio Computation Protocol

**Definition:**
```
R = conv_params / (conv_params + linear_params_no_head)

Where:
  conv_params = sum of parameters in 4D tensors (convolution weights)
  linear_params_no_head = sum of parameters in 2D tensors, excluding classification head
```

**Implementation (from h-e1/code/src/feature_extractor.py):**
```python
def _compute_param_mass_ratio(self, state_dict: dict) -> float:
    """
    Compute R = conv_params / (conv_params + linear_params_no_head)
    
    4D tensors are conv weights, 2D tensors are linear weights.
    Exclude classification head keys.
    """
    conv_params = 0
    linear_params = 0
    
    for key, tensor in state_dict.items():
        if self._exclude_head_keys(key):  # Skip 'head', 'fc', 'classifier'
            continue
        
        if self._is_conv_weight(tensor):  # tensor.dim() == 4
            conv_params += tensor.numel()
        elif self._is_linear_weight(tensor):  # tensor.dim() == 2
            linear_params += tensor.numel()
    
    total_params = conv_params + linear_params
    if total_params == 0:
        return 0.0
    
    return conv_params / total_params

def _exclude_head_keys(self, key: str) -> bool:
    """Check if key belongs to classification head"""
    HEAD_KEYWORDS = ['head', 'fc', 'classifier']
    return any(keyword in key.lower() for keyword in HEAD_KEYWORDS)
```

**Expected R Ranges (from Phase 2B hypothesis):**
- **CNNs:** R > 0.6 (convolution-dominant)
- **Transformers:** R < 0.2 (linear/attention-dominant)
- **Hybrids:** 0.2 ≤ R ≤ 0.6 (mixed allocation)

### 3.3 Inter-Family Separation Analysis (Cohen's d)

**Cohen's d Definition:**
```
d = (μ_CNN - μ_Transformer) / σ_pooled

Where:
  σ_pooled = sqrt((σ²_CNN + σ²_Transformer) / 2)
```

**Implementation:**
```python
import numpy as np
from scipy import stats

def compute_cohens_d(group1: np.ndarray, group2: np.ndarray) -> float:
    """
    Compute Cohen's d effect size between two groups.
    
    Args:
        group1: R values for CNNs
        group2: R values for Transformers
    
    Returns:
        Cohen's d effect size
    """
    n1, n2 = len(group1), len(group2)
    mean1, mean2 = np.mean(group1), np.mean(group2)
    var1, var2 = np.var(group1, ddof=1), np.var(group2, ddof=1)
    
    # Pooled standard deviation
    pooled_std = np.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))
    
    # Cohen's d
    d = (mean1 - mean2) / pooled_std
    
    return abs(d)  # Absolute value for effect size magnitude


# Usage
cnn_R = val_features[val_features['family'] == 'CNN']['param_mass_ratio']
transformer_R = val_features[val_features['family'] == 'Transformer']['param_mass_ratio']

cohens_d = compute_cohens_d(cnn_R, transformer_R)
print(f"Cohen's d (CNN vs Transformer): {cohens_d:.3f}")
```

**Interpretation:**
- d = 0.2: Small effect
- d = 0.5: Medium effect
- d = 0.8: Large effect
- **d > 1.0: Very large effect (H-M2 threshold)**

**Success Criteria:**
- Primary: `cohens_d > 1.0` (strong inter-family separation)
- Secondary: `p < 0.05` (t-test for statistical significance)

### 3.4 Intra-Family Scale Invariance (Coefficient of Variation)

**Coefficient of Variation (CV) Definition:**
```
CV = σ / μ

Where:
  σ = standard deviation of R within family
  μ = mean R within family
```

**Scale Invariance Test:**
```python
def compute_scale_invariance_cv(features_df: pd.DataFrame, 
                                scale_family: list = None) -> dict:
    """
    Validate scale invariance across ResNet-{18,34,50,101,152}.
    
    Args:
        features_df: DataFrame with columns ['model_name', 'family', 'param_mass_ratio']
        scale_family: List of model names for scale test (default: ResNet variants)
    
    Returns:
        {
            'cv': float,
            'mean_R': float,
            'std_R': float,
            'passed': bool
        }
    """
    if scale_family is None:
        scale_family = ['resnet18', 'resnet34', 'resnet50', 'resnet101', 'resnet152']
    
    # Filter to scale family
    scale_df = features_df[features_df['model_name'].isin(scale_family)]
    
    R_values = scale_df['param_mass_ratio'].values
    mean_R = np.mean(R_values)
    std_R = np.std(R_values, ddof=1)
    cv = std_R / mean_R if mean_R > 0 else 0.0
    
    return {
        'cv': cv,
        'mean_R': mean_R,
        'std_R': std_R,
        'models': scale_family,
        'passed': cv < 0.15  # Threshold from Phase 2A Assumption A3
    }


# Usage
cv_results = compute_scale_invariance_cv(train_features)
print(f"ResNet Family CV: {cv_results['cv']:.4f}")
print(f"  Mean R: {cv_results['mean_R']:.4f} ± {cv_results['std_R']:.4f}")
print(f"  Status: {'✓ PASS' if cv_results['passed'] else '✗ FAIL'} (threshold: CV < 0.15)")
```

**Success Criteria:**
- Primary: `CV < 0.15` across ResNet-{18,34,50,101,152}
- Secondary: CV remains <0.15 for other scale families (EfficientNet-B{0,4}, ViT-{tiny,small,base,large})

### 3.5 Distribution Visualization & Edge Case Analysis

**Distribution Analysis:**
```python
import matplotlib.pyplot as plt
import seaborn as sns

def plot_R_distributions(features_df: pd.DataFrame, output_path: str):
    """
    Plot parameter-mass ratio distributions per family.
    
    Creates:
        1. Violin plot showing R distributions for CNN/Transformer/Hybrid
        2. Box plot with outlier detection
        3. Histogram with kernel density estimation
    """
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    
    # Violin plot
    sns.violinplot(data=features_df, x='family', y='param_mass_ratio', ax=axes[0])
    axes[0].axhline(y=0.6, color='r', linestyle='--', label='CNN threshold (0.6)')
    axes[0].axhline(y=0.2, color='b', linestyle='--', label='Transformer threshold (0.2)')
    axes[0].set_title('R Distribution by Family')
    axes[0].legend()
    
    # Box plot
    sns.boxplot(data=features_df, x='family', y='param_mass_ratio', ax=axes[1])
    axes[1].set_title('R Distribution (Outlier Detection)')
    
    # Histogram with KDE
    for family in ['CNN', 'Transformer', 'Hybrid']:
        family_R = features_df[features_df['family'] == family]['param_mass_ratio']
        axes[2].hist(family_R, alpha=0.5, label=family, bins=10, density=True)
        axes[2].axvline(family_R.mean(), color='k', linestyle='--', alpha=0.7)
    
    axes[2].set_xlabel('Parameter-Mass Ratio R')
    axes[2].set_ylabel('Density')
    axes[2].set_title('R Histogram with Family Means')
    axes[2].legend()
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"✓ Saved distribution plot to {output_path}")
```

**Edge Case Detection:**
```python
def detect_edge_cases(features_df: pd.DataFrame) -> dict:
    """
    Identify models that violate expected R thresholds.
    
    Returns:
        {
            'cnn_low_R': [models with R < 0.6],
            'transformer_high_R': [models with R > 0.2],
            'hybrid_outliers': [models outside 0.2-0.6 range]
        }
    """
    cnn_df = features_df[features_df['family'] == 'CNN']
    transformer_df = features_df[features_df['family'] == 'Transformer']
    hybrid_df = features_df[features_df['family'] == 'Hybrid']
    
    cnn_low_R = cnn_df[cnn_df['param_mass_ratio'] < 0.6]['model_name'].tolist()
    transformer_high_R = transformer_df[transformer_df['param_mass_ratio'] > 0.2]['model_name'].tolist()
    hybrid_outliers = hybrid_df[
        (hybrid_df['param_mass_ratio'] < 0.2) | (hybrid_df['param_mass_ratio'] > 0.6)
    ]['model_name'].tolist()
    
    return {
        'cnn_low_R': cnn_low_R,
        'transformer_high_R': transformer_high_R,
        'hybrid_outliers': hybrid_outliers,
        'cnn_violation_rate': len(cnn_low_R) / len(cnn_df) if len(cnn_df) > 0 else 0.0,
        'transformer_violation_rate': len(transformer_high_R) / len(transformer_df) if len(transformer_df) > 0 else 0.0
    }
```

**Edge Case Hypotheses (from h-m1 results):**
1. **VGG-16 (NormFree CNN):** Expected R ≈ 1.0 (purely convolutional)
2. **ConvNeXt (CNN with LayerNorm):** Expected R > 0.6 (still convolution-dominant)
3. **PoolFormer (MetaFormer):** Expected R < 0.2 (attention-free but linear-dominant)
4. **MLP-Mixer (Hybrid):** Expected 0.2 < R < 0.6 (balanced conv tokenization + MLP)

---

## 4. Baseline Comparison

### 4.1 Baseline: H-M1 Normalization Fingerprinting

**H-M1 Performance (prerequisite):**
- CNN violation: 0.00% (BatchNorm dominance 100%)
- Transformer violation: 14.29% (LayerNorm dominance 85.71%)
- Feature importance: `bn_count` (0.353), `ln_count` (0.171)

**H-M2 Complementary Analysis:**
- H-M1 tested normalization layer choice (categorical feature)
- H-M2 tests parameter allocation pattern (continuous feature)
- Combined validation: Both mechanisms contribute to classification

### 4.2 Baseline: H-E1 Overall Classifier

**H-E1 Performance:**
- Validation accuracy: 88.89% (16/18 correct)
- Feature importance: **`param_mass_ratio` (0.777)** — highest importance
- Confirms R is the dominant feature for classification

**H-M2 Focus:**
- Mechanistic validation: WHY does R work? (allocation patterns)
- Quantitative separation: Cohen's d effect size
- Scale invariance: CV across model sizes

### 4.3 Baseline: Random Allocation Hypothesis

**Null Hypothesis (H0):**
- Parameter allocation is independent of architecture family
- Expected: No significant difference in R between CNNs and Transformers
- Cohen's d ≈ 0 (no effect)

**Alternative Hypothesis (H-M2):**
- Parameter allocation reflects computational paradigm
- Expected: Cohen's d > 1.0 (very large effect)
- Statistical significance: p < 0.05 (t-test)

---

## 5. Success Criteria & Gate Conditions

### 5.1 Primary Success Criteria (MUST_WORK Gate)

| Criterion | Metric | Threshold | Rationale |
|-----------|--------|-----------|-----------|
| **P1: Inter-Family Separation** | Cohen's d (CNN vs Transformer) | >1.0 | Strong effect size validates allocation pattern hypothesis |
| **P2: Intra-Family Scale Invariance** | CV across ResNet-{18,34,50,101,152} | <0.15 | R must be scale-stable, not size-dependent |

**Gate Decision:**
- **PASS:** Both P1 AND P2 meet thresholds → Proceed to H-M3
- **FAIL (P1):** Cohen's d ≤1.0 → **EXPLORE** alternative ratios (attention_params / total_params)
- **FAIL (P2):** CV ≥0.15 → **PIVOT** to normalized ratio (R_rank or size-adjusted R)

### 5.2 Secondary Success Criteria

| Criterion | Metric | Threshold | Purpose |
|-----------|--------|-----------|---------|
| **S1: Statistical Significance** | t-test p-value (CNN vs Transformer) | <0.05 | Confirm separation is not random |
| **S2: Distribution Separation** | Mean R_CNN - Mean R_Transformer | >0.4 | Practical separation (0.6 - 0.2 = 0.4) |
| **S3: Edge Case Robustness** | Violation rate on edge cases | ≤25% | Higher tolerance for boundary architectures |

### 5.3 Failure Mode Analysis

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

## 6. Implementation Plan

### 6.1 Code Reuse from H-E1/H-M1

**Reusable Components:**
- Feature extraction: `h-e1/code/src/feature_extractor.py` (R already computed)
- Dataset loading: `h-e1/code/src/data_loader.py`
- Configuration: `h-e1/code/config.py` (model families, thresholds)

**New Modules for H-M2:**
1. `src/cohens_d_analyzer.py`: Inter-family effect size computation
2. `src/scale_invariance_validator.py`: Intra-family CV analysis
3. `src/distribution_visualizer.py`: R distribution plots
4. `src/edge_case_analyzer.py`: Threshold violation detection

### 6.2 Execution Pipeline

```python
# main_h_m2.py
class H_M2_Runner:
    def run_mechanism_validation(self):
        # Step 1: Load h-e1 features (reuse)
        train_df, val_df = self.load_features_from_h_e1()
        
        # Step 2: Inter-family separation (Cohen's d)
        cohens_d_results = self.analyze_cohens_d(val_df)
        
        # Step 3: Intra-family scale invariance (CV)
        cv_results = self.validate_scale_invariance(train_df)
        
        # Step 4: Distribution visualization
        self.plot_distributions(val_df)
        
        # Step 5: Edge case analysis
        edge_case_results = self.detect_edge_cases(val_df)
        
        # Step 6: Gate decision
        gate_decision = self.evaluate_gate(cohens_d_results, cv_results)
        
        return {
            'cohens_d_results': cohens_d_results,
            'cv_results': cv_results,
            'edge_case_results': edge_case_results,
            'gate_decision': gate_decision
        }
```

### 6.3 Output Artifacts

**Required Outputs:**
1. `outputs/cohens_d_report.json`: Effect size, p-value, confidence intervals
2. `outputs/cv_report.json`: CV values per family, scale invariance test results
3. `outputs/R_distributions.png`: Violin/box/histogram plots
4. `outputs/edge_cases.json`: Models violating R thresholds
5. `outputs/gate_decision.txt`: PASS/FAIL status with reasoning

**Validation Report Format (for 04_validation.md):**
```markdown
## H-M2 Validation Results

### Primary Metrics
- **Cohen's d (CNN vs Transformer):** {value:.3f} ({status})
- **CV (ResNet family):** {value:.4f} ({status})
- **Gate Decision:** {PASS | FAIL}

### Distribution Summary
- CNN Mean R: {mean_cnn:.3f} ± {std_cnn:.3f}
- Transformer Mean R: {mean_transformer:.3f} ± {std_transformer:.3f}
- Hybrid Mean R: {mean_hybrid:.3f} ± {std_hybrid:.3f}

### Edge Cases
- CNN violations: {count} models ({rate:.1%})
- Transformer violations: {count} models ({rate:.1%})
- Known edge cases: VGG-16 (NormFree), PoolFormer (MetaFormer)
```

---

## 7. Timeline & Resources

### 7.1 Implementation Breakdown (6 hours budget, LIGHT tier)

| Task | Subtasks | Estimated Time |
|------|----------|----------------|
| **Task 1: Dataset Preparation** | Reuse h-e1 features | 0.5 hours |
| **Task 2: Cohen's d Analysis** | Implement effect size, statistical tests | 1.5 hours |
| **Task 3: CV Validation** | Scale invariance across ResNet/ViT families | 1.0 hour |
| **Task 4: Distribution Visualization** | Violin/box/histogram plots | 1.0 hour |
| **Task 5: Edge Case Detection** | Threshold violation analysis | 0.5 hours |
| **Task 6: Report Generation** | JSON outputs + 04_validation.md | 1.0 hour |
| **Failsafe Buffer** | Debug, edge case handling | 0.5 hours |
| **Total** | | **6 hours** |

### 7.2 Compute Requirements

**Environment:**
- Python 3.8+
- PyTorch 2.1+ (for checkpoint loading, if needed)
- NumPy, Pandas, Scikit-learn, SciPy, Matplotlib, Seaborn

**Hardware:**
- CPU-only (no GPU required)
- RAM: 8GB (feature data is small, ~50 models × 5 features)
- Storage: <100MB (reusing h-e1 cached features)

**Execution Time:**
- Feature loading: <1 minute
- Statistical analysis: <5 minutes
- Visualization: <2 minutes
- Total runtime: <10 minutes

---

## 8. Risk Analysis

### 8.1 High-Risk Assumptions

| Risk ID | Assumption | Mitigation |
|---------|------------|------------|
| **R1** | R is scale-invariant (CV <0.15) | Pre-validate on ResNet family before full experiment |
| **R2** | CNN/Transformer separation is strong (d >1.0) | Fallback to normalized R if raw R shows weak separation |
| **R3** | Head exclusion is correct | Manual validation on 5 models (compare with/without head) |

### 8.2 Edge Case Risks

**Known Problematic Architectures:**
1. **NormFree CNNs (VGG-16):** Expected R ≈ 1.0 (no linear layers except head)
2. **Depth-wise Separable Convs (MobileNet):** May reduce conv_params → lower R
3. **MLP-Mixer:** Tokenization uses conv, but body is all linear → ambiguous R
4. **ConvNeXt:** CNN with LayerNorm, but expected R > 0.6 (still conv-dominant)

**Mitigation:**
- Document edge cases in `edge_cases.json`
- Analyze separately from standard architectures
- Acceptable violation rate: ≤25% for edge cases (vs ≤15% for standard)

---

## 9. References & Prior Work

### 9.1 Theoretical Foundation

**Fang et al. 2024** (from Phase 2A):
- Finding: Heterogeneous structures (CNNs vs Transformers) show diverged importance distributions
- Connection: Parameter allocation patterns (R) reflect structural heterogeneity
- Citation: "Architectural paradigms impose parameter allocation strategies"

**Chun et al. 2026** (from Phase 2A):
- Finding: LayerNorm reduces Last Layer Complexity by m/2 vs BatchNorm
- Connection: Normalization choice correlates with linear layer dominance (Transformers)
- Complements: H-M1 (normalization) + H-M2 (parameter allocation) = full mechanism

### 9.2 Related Baselines (from 02b_verification_plan.md)

**Kofinas et al. 2024 GNN:**
- Uses graph neural networks for architecture classification
- Requires complex graph construction (50+ hours implementation)
- H-M2 contrast: Simple statistical feature (R) achieves strong separation

**Zhang & Abdulla 2023:**
- Uses BatchNorm runtime statistics for performance prediction
- Requires forward passes (expensive)
- H-M2 contrast: Checkpoint-only parameter counting (no forward pass)

---

## 10. Validation Checklist

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
- [ ] Results exported to `02c_experiment_brief.md` and `04_validation.md`

---

## 11. Appendix: Statistical Formulas

### A.1 Cohen's d Effect Size

```
d = (μ₁ - μ₂) / σ_pooled

σ_pooled = sqrt( ((n₁ - 1) * σ₁² + (n₂ - 1) * σ₂²) / (n₁ + n₂ - 2) )

Where:
  μ₁, μ₂ = means of group 1 (CNN) and group 2 (Transformer)
  σ₁, σ₂ = standard deviations
  n₁, n₂ = sample sizes
```

**Interpretation:**
- |d| < 0.2: Negligible effect
- 0.2 ≤ |d| < 0.5: Small effect
- 0.5 ≤ |d| < 0.8: Medium effect
- |d| ≥ 0.8: Large effect
- **|d| ≥ 1.0: Very large effect (H-M2 threshold)**

### A.2 Coefficient of Variation

```
CV = σ / μ

Where:
  σ = sample standard deviation
  μ = sample mean
```

**Interpretation:**
- CV < 0.1: Low variability (highly stable)
- 0.1 ≤ CV < 0.2: Moderate variability
- **CV < 0.15: H-M2 threshold for scale invariance**
- CV ≥ 0.2: High variability (scale-dependent)

### A.3 Independent Samples t-test

```
t = (μ₁ - μ₂) / sqrt(s₁²/n₁ + s₂²/n₂)

df = min(n₁ - 1, n₂ - 1)  # Conservative degrees of freedom

p-value: Pr(|T| > |t|) under null hypothesis (two-tailed)
```

**Interpretation:**
- p < 0.001: Very strong evidence against H0
- p < 0.01: Strong evidence
- p < 0.05: Moderate evidence (H-M2 threshold)
- p ≥ 0.05: Insufficient evidence

---

**END OF EXPERIMENT BRIEF**

**Next Steps:**
1. Review experiment brief with stakeholders
2. Execute Phase 3 implementation planning (03_prd.md, 03_architecture.md, 03_tasks.yaml)
3. Run Phase 4 coding with validator-agent
4. Generate 04_validation.md report
