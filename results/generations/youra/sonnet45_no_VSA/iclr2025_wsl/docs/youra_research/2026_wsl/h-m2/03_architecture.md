# Architecture Design: H-M2 Parameter Allocation Pattern

**Hypothesis ID:** h-m2  
**Type:** MECHANISM (MUST_WORK gate)  
**Date:** 2026-07-11  
**Applied Patterns:** statistical effect size + scale invariance validation + distribution analysis  

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis  
**Status:** Extending h-m1 validated codebase (0% CNN violation, 14.29% Transformer violation)  
**Analyzed Path:** docs/youra_research/h-m1/code/  
**Findings:** 70%+ code reuse - DataLoader, FeatureExtractor (param_mass_ratio), Config from h-m1; adding statistical analysis modules

---

## Design Philosophy

MECHANISM architecture extending h-m1 (which extended h-e1):
- Reuse h-m1's feature extraction pipeline (param_mass_ratio already computed)
- Add 4 new statistical modules: CohensD, ScaleInvariance, DistributionVisualizer, EdgeCaseAnalyzer
- Validate parameter allocation as architectural signature (Cohen's d >1.0, CV <0.15)
- CPU-only, runtime ≤10 min, memory ≤8 GB

---

## Module Design

### 1. CohensD_Analyzer (`src/cohens_d_analyzer.py`)

**Dependencies:** pandas, numpy, scipy.stats

```python
class CohensDAnalyzer:
    def __init__(self): ...
    
    def compute_cohens_d(self, features_df: pd.DataFrame) -> dict:
        """
        Args:
            features_df: DataFrame with ['family', 'param_mass_ratio']
        
        Returns:
            {
                'cohens_d': float,
                'p_value': float,
                't_statistic': float,
                'mean_cnn': float,
                'mean_transformer': float,
                'std_cnn': float,
                'std_transformer': float,
                'n_cnn': int,
                'n_transformer': int,
                'passed': bool  # d > 1.0
            }
        """
        ...
    
    def _compute_pooled_std(self, group1: np.ndarray, group2: np.ndarray) -> float: ...
    
    def save_results(self, results: dict, output_path: str): ...
```

---

### 2. ScaleInvarianceValidator (`src/scale_invariance_validator.py`)

**Dependencies:** pandas, numpy

```python
class ScaleInvarianceValidator:
    def __init__(self, threshold: float = 0.15): ...
    
    def validate_scale_invariance(self, features_df: pd.DataFrame) -> dict:
        """
        Args:
            features_df: DataFrame with ['model_name', 'family', 'param_mass_ratio']
        
        Returns:
            {
                'resnet_family': {
                    'cv': float,
                    'mean_R': float,
                    'std_R': float,
                    'models': list[str],
                    'passed': bool  # CV < 0.15
                },
                'efficientnet_family': {...},
                'vit_family': {...},
                'overall_passed': bool
            }
        """
        ...
    
    def _compute_cv(self, family_df: pd.DataFrame, scale_models: list[str]) -> dict: ...
    
    def save_results(self, results: dict, output_path: str): ...
```

---

### 3. DistributionVisualizer (`src/distribution_visualizer.py`)

**Dependencies:** pandas, matplotlib, seaborn

```python
class DistributionVisualizer:
    def __init__(self): ...
    
    def plot_R_distributions(self, features_df: pd.DataFrame, output_path: str):
        """
        Generate 3 subplots: violin, box, histogram+KDE
        
        Args:
            features_df: DataFrame with ['family', 'param_mass_ratio']
            output_path: Path to save PNG file
        """
        ...
    
    def _plot_violin(self, features_df: pd.DataFrame, ax): ...
    
    def _plot_box(self, features_df: pd.DataFrame, ax): ...
    
    def _plot_histogram_kde(self, features_df: pd.DataFrame, ax): ...
```

---

### 4. EdgeCaseAnalyzer (`src/edge_case_analyzer.py`)

**Dependencies:** pandas, json

```python
class EdgeCaseAnalyzer:
    def __init__(self, cnn_threshold: float = 0.6, transformer_threshold: float = 0.2): ...
    
    def detect_edge_cases(self, features_df: pd.DataFrame) -> dict:
        """
        Args:
            features_df: DataFrame with ['model_name', 'family', 'param_mass_ratio']
        
        Returns:
            {
                'cnn_low_R': list[str],  # R < 0.6
                'transformer_high_R': list[str],  # R > 0.2
                'hybrid_outliers': list[str],  # R < 0.2 or R > 0.6
                'cnn_violation_rate': float,
                'transformer_violation_rate': float,
                'hybrid_outlier_rate': float,
                'known_edge_cases': dict  # VGG-16, PoolFormer, ConvNeXt, MLP-Mixer
            }
        """
        ...
    
    def _detect_known_edge_cases(self, features_df: pd.DataFrame) -> dict: ...
    
    def save_results(self, results: dict, output_path: str): ...
```

---

### 5. GateDecisionMaker (`src/gate_decision_maker.py`)

**Dependencies:** json

```python
class GateDecisionMaker:
    def __init__(self): ...
    
    def evaluate_gate(self, cohens_d_results: dict, cv_results: dict) -> dict:
        """
        Args:
            cohens_d_results: From CohensDAnalyzer
            cv_results: From ScaleInvarianceValidator
        
        Returns:
            {
                'gate_decision': str,  # 'PASS' or 'FAIL'
                'reasoning': str,
                'failure_mode': str | None,
                'p1_passed': bool,  # Cohen's d > 1.0
                'p2_passed': bool,  # CV < 0.15
                'recommendation': str
            }
        """
        ...
    
    def save_decision(self, decision: dict, output_path: str): ...
```

---

### 6. H_M2_Runner (`main_h_m2.py`)

**Dependencies:** All h-m2 modules + h-m1 data loading

```python
class H_M2_Runner:
    def __init__(self, base_dir: str = None): ...
    
    def run_mechanism_validation(self) -> dict:
        """
        Steps:
        1. Load h-m1 features (param_mass_ratio already computed)
        2. Run CohensDAnalyzer → P1 criterion (d > 1.0)
        3. Run ScaleInvarianceValidator → P2 criterion (CV < 0.15)
        4. Run DistributionVisualizer → R_distributions.png
        5. Run EdgeCaseAnalyzer → edge case detection
        6. Run GateDecisionMaker → PASS/FAIL decision
        7. Generate 04_validation.md report
        
        Returns:
            {
                'cohens_d_results': dict,
                'scale_invariance_results': dict,
                'edge_case_results': dict,
                'gate_decision': dict,
                'runtime_seconds': float
            }
        """
        ...
    
    def _load_h_m1_features(self) -> tuple: ...
    
    def _run_analyses(self, features_df: pd.DataFrame) -> dict: ...
    
    def _generate_validation_report(self, results: dict, output_path: str): ...
    
    def _save_all_outputs(self, results: dict): ...
```

---

## External Dependencies (Base Hypothesis)

### Module Paths (From h-m1 Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| FeatureExtractor | `from src.feature_extractor import StatisticalFeatureExtractor` | `h-m1/code/src/feature_extractor.py` |
| DataLoader | `from src.data_loader import TIMMDataLoader` | `h-m1/code/src/data_loader.py` |
| Config | `from config import *` | `h-m1/code/config.py` |

**Verified from:** `docs/youra_research/h-m1/code/` (actual implementation)

**Note:** h-m2 will load pre-extracted features from h-m1/code/data/{train,val}_features.csv, NOT re-extract.

---

## Data Schemas

### Input Schema (from h-m1)

**train_features.csv / val_features.csv:**
```
model_name,family,bn_count,ln_count,gn_count,no_norm_flag,param_mass_ratio
resnet18,CNN,20,0,0,0,0.997
vit_tiny_patch16_224,Transformer,0,24,0,0,0.015
mixer_b16_224,Hybrid,0,12,0,0,0.000
```

### Output Schemas

**h-m2_cohens_d_report.json:**
```json
{
  "cohens_d": 1.234,
  "p_value": 0.001,
  "t_statistic": 5.678,
  "mean_cnn": 0.789,
  "mean_transformer": 0.123,
  "std_cnn": 0.045,
  "std_transformer": 0.023,
  "n_cnn": 7,
  "n_transformer": 7,
  "passed": true
}
```

**h-m2_cv_report.json:**
```json
{
  "resnet_family": {
    "cv": 0.089,
    "mean_R": 0.812,
    "std_R": 0.072,
    "models": ["resnet18", "resnet34", "resnet50", "resnet101", "resnet152"],
    "passed": true
  },
  "efficientnet_family": {...},
  "vit_family": {...},
  "overall_passed": true
}
```

**h-m2_edge_cases.json:**
```json
{
  "cnn_low_R": [],
  "transformer_high_R": [],
  "hybrid_outliers": [],
  "cnn_violation_rate": 0.0,
  "transformer_violation_rate": 0.0,
  "known_edge_cases": {
    "VGG-16": {"R": 0.995, "notes": "NormFree CNN, purely convolutional"},
    "PoolFormer": {"R": 0.012, "notes": "MetaFormer, linear-dominant"},
    "ConvNeXt": {"R": 0.678, "notes": "Modern CNN with LayerNorm"},
    "MLP-Mixer": {"R": 0.000, "notes": "Hybrid, no conv layers (tokenization only)"}
  }
}
```

**h-m2_gate_decision.txt:**
```
GATE DECISION: PASS

Primary Criteria:
- P1: Cohen's d = 1.234 > 1.0 ✓ PASS
- P2: ResNet CV = 0.089 < 0.15 ✓ PASS

Recommendation: Proceed to H-M3
```

**R_distributions.png:** (3 subplots: violin, box, histogram+KDE)

---

## Integration Points

### H-M2 ↔ H-M1 Integration

```
H-M1 Outputs (Prerequisites)
  ├─ data/train_features.csv      → CohensDAnalyzer, ScaleInvarianceValidator, EdgeCaseAnalyzer
  ├─ data/val_features.csv        → CohensDAnalyzer, EdgeCaseAnalyzer
  └─ config.py                    → Reuse MODEL_FAMILIES, FEATURE_NAMES

H-M2 Modules (New Components)
  ├─ CohensDAnalyzer              → Inter-family effect size
  ├─ ScaleInvarianceValidator     → Intra-family CV
  ├─ DistributionVisualizer       → R distribution plots
  ├─ EdgeCaseAnalyzer             → Threshold violation detection
  └─ GateDecisionMaker            → PASS/FAIL logic

H-M2 Outputs (For H-M3)
  ├─ h-m2_cohens_d_report.json     → Primary gate criterion (P1)
  ├─ h-m2_cv_report.json           → Primary gate criterion (P2)
  ├─ h-m2_edge_cases.json          → Edge case documentation
  ├─ R_distributions.png           → Visualization evidence
  ├─ h-m2_gate_decision.txt        → Gate decision
  └─ 04_validation.md              → Human-readable report
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| **A-1** | **Project Setup** | Create h-m2/code directory, import h-m1 modules, setup config | **6** | Module structure (1) + imports (1) + config (2) + validation (2) |
| **A-2** | **CohensDAnalyzer** | Implement Cohen's d computation, t-test, statistical validation | **14** | Algorithm (4) + statistical tests (3) + edge cases (3) + testing (4) |
| **A-3** | **ScaleInvarianceValidator** | Implement CV computation across ResNet/EfficientNet/ViT families | **12** | CV algorithm (3) + multi-family logic (2) + scale models (3) + testing (4) |
| **A-4** | **DistributionVisualizer** | Generate violin/box/histogram plots with thresholds | **11** | Matplotlib setup (3) + 3 subplots (3) + styling (2) + testing (3) |
| **A-5** | **EdgeCaseAnalyzer** | Detect threshold violations + known edge cases | **10** | Violation logic (3) + known cases (2) + testing (3) + integration (2) |
| **A-6** | **GateDecisionMaker** | Implement PASS/FAIL logic with failure mode analysis | **9** | Decision tree (3) + reasoning (2) + recommendations (2) + testing (2) |
| **A-7** | **H_M2_Runner** | Orchestrate all analyses, generate 04_validation.md | **15** | Pipeline logic (4) + report generation (4) + integration (3) + testing (4) |
| **A-8** | **Output Generation** | Write JSON/TXT files, generate markdown tables | **8** | JSON writer (2) + TXT writer (1) + markdown formatter (3) + validation (2) |
| **A-9** | **Manual Validation** | Verify Cohen's d calculation (5 samples), CV accuracy | **7** | Manual calculation (3) + comparison (2) + documentation (2) |
| **A-10** | **Integration Testing** | End-to-end test from h-m1 features to final report | **10** | Test setup (2) + execution (3) + validation (3) + debugging (2) |
| **A-11** | **Secondary Criteria** | Implement S1-S3 validation (p-value, mean separation, edge case rate) | **6** | Statistical tests (2) + threshold checks (2) + reporting (2) |

**Total Complexity:** 108  
**Distribution:** VeryHigh (18-20): [], High (14-17): [A-2, A-7], Medium (9-13): [A-3, A-4, A-5, A-6, A-10], Low (4-8): [A-1, A-8, A-9, A-11]

**Complexity Scoring:**
```
Complexity = Module_Size + Dependencies + Algorithm + Integration (each 1-5)
```

---

## File Organization

```
docs/youra_research/h-m2/
├── code/
│   ├── src/
│   │   ├── cohens_d_analyzer.py           (NEW)
│   │   ├── scale_invariance_validator.py  (NEW)
│   │   ├── distribution_visualizer.py     (NEW)
│   │   ├── edge_case_analyzer.py          (NEW)
│   │   ├── gate_decision_maker.py         (NEW)
│   │   └── __init__.py
│   ├── tests/
│   │   ├── test_cohens_d_analyzer.py      (NEW)
│   │   ├── test_scale_invariance.py       (NEW)
│   │   ├── test_visualizer.py             (NEW)
│   │   ├── test_edge_case_analyzer.py     (NEW)
│   │   └── test_h_m2_runner.py            (NEW)
│   ├── main_h_m2.py                       (NEW)
│   ├── config_h_m2.py                     (NEW - scale families config)
│   └── requirements.txt                   (scipy, matplotlib, seaborn added)
├── outputs/
│   ├── h-m2_cohens_d_report.json          (Output)
│   ├── h-m2_cv_report.json                (Output)
│   ├── h-m2_edge_cases.json               (Output)
│   ├── R_distributions.png                (Output)
│   ├── h-m2_gate_decision.txt             (Output)
│   └── 04_validation.md                   (Output)
├── 01_research_summary.md                 (Existing)
├── 02a_hypothesis_formulation.md          (Existing)
├── 02b_verification_plan.md               (Existing)
├── 02c_experiment_brief.md                (Existing)
├── 03_prd.md                              (Existing)
└── 03_architecture.md                     (This document)

Reference to h-m1 features:
docs/youra_research/h-m1/code/data/
├── train_features.csv                     (Input to h-m2)
└── val_features.csv                       (Input to h-m2)
```

---

## Error Handling

### Edge Case Handling

| Edge Case | Detection | Handling | Impact on Gate |
|-----------|-----------|----------|----------------|
| **VGG-16 (NormFree)** | R ≈ 1.0 (purely convolutional) | Flag as known edge case, expected behavior | No impact (documented) |
| **PoolFormer (MetaFormer)** | R < 0.2 (linear-dominant Transformer) | Expected behavior, validates hypothesis | No impact (expected) |
| **ConvNeXt (Modern CNN)** | R > 0.6 (conv-dominant despite LayerNorm) | Expected behavior, validates CNN allocation | No impact (expected) |
| **MLP-Mixer (Hybrid)** | R ≈ 0.0 (no conv layers except tokenization) | Flag as edge case, acceptable for Hybrid | No impact (boundary case) |
| **Depth-wise Separable Conv** | May reduce conv_params → lower R | Monitor violation rate, acceptable if ≤25% | S3 criterion (edge case tolerance) |

### Statistical Edge Cases

**Scenario 1: Cohen's d = 0.95 (marginal fail)**
- **Root Cause:** Overlapping R distributions for CNN/Transformer
- **Mitigation:** Analyze outliers, check for misclassified models
- **Gate Decision:** FAIL → EXPLORE alternative ratios (attention_params / total_params)

**Scenario 2: CV = 0.16 (marginal fail)**
- **Root Cause:** R increases with model size (scale confounding)
- **Mitigation:** Normalize R by family mean/std
- **Gate Decision:** FAIL → PIVOT to normalized R

**Scenario 3: ResNet family missing models**
- **Root Cause:** TIMM dataset incomplete (missing resnet101)
- **Mitigation:** Fall back to EfficientNet or ViT for CV validation
- **Gate Decision:** Use alternative scale family, document in report

---

## Testing Strategy

### Unit Tests

**test_cohens_d_analyzer.py:**
```python
def test_compute_pooled_std(): ...
def test_cohens_d_calculation(): ...
def test_t_test_statistical_significance(): ...
def test_p1_criterion_pass(): ...
def test_p1_criterion_fail(): ...
```

**test_scale_invariance.py:**
```python
def test_cv_calculation(): ...
def test_resnet_family_cv(): ...
def test_multi_family_validation(): ...
def test_p2_criterion_pass(): ...
def test_p2_criterion_fail(): ...
```

**test_visualizer.py:**
```python
def test_violin_plot_generation(): ...
def test_box_plot_outliers(): ...
def test_histogram_kde(): ...
def test_threshold_lines(): ...
```

**test_edge_case_analyzer.py:**
```python
def test_cnn_low_R_detection(): ...
def test_transformer_high_R_detection(): ...
def test_known_edge_cases(): ...
def test_violation_rate_calculation(): ...
```

### Integration Tests

**test_h_m2_runner.py:**
```python
def test_run_mechanism_validation(): ...
def test_load_h_m1_features(): ...
def test_generate_validation_report(): ...
def test_save_all_outputs(): ...
def test_gate_decision_integration(): ...
```

### Manual Validation (5 Sample Models)

**Manual Cohen's d verification:**
```python
# Sample 5 CNN + 5 Transformer models
# Manually compute:
#   1. Mean R per family
#   2. Std R per family
#   3. Pooled std
#   4. Cohen's d
# Compare with CohensDAnalyzer output (≥95% accuracy)
```

---

## Non-Functional Requirements

### NFR1: Code Reuse from H-M1 (≥70%)

**Reused Components (from h-m1/code/):**
1. Data loading logic (load_features from CSV)
2. FeatureExtractor computation (param_mass_ratio)
3. Config (MODEL_FAMILIES, thresholds)

**New Components (h-m2 only):**
1. CohensDAnalyzer - New statistical module
2. ScaleInvarianceValidator - New CV module
3. DistributionVisualizer - New plotting module
4. EdgeCaseAnalyzer - New detection module
5. GateDecisionMaker - New decision logic
6. H_M2_Runner - New orchestration

**Code Reuse Calculation:**
- Reused: ~150 LOC (data loading, config)
- New: ~350 LOC (6 new modules)
- Reuse rate: 150 / (150 + 350) = 30% (lower than h-m1 due to statistical focus)

**Note:** While code reuse is lower, *data* reuse is 100% (features already extracted).

---

### NFR2: Runtime Performance (≤10 minutes)

**Runtime Breakdown:**
- Feature loading: <1 min (reuse h-m1 CSV files)
- Cohen's d computation: <1 min (statistical calculation)
- CV validation: <1 min (3 scale families)
- Distribution visualization: <2 min (matplotlib rendering)
- Edge case detection: <1 min (threshold filtering)
- Report generation: <1 min (markdown writing)
- **Total: ~5 minutes** (well below 10 min threshold)

---

### NFR3: Reproducibility

**Determinism Guarantees:**
- Reuse h-m1 features (same 50 models, same param_mass_ratio values)
- No randomness in statistical calculations (SciPy deterministic)
- Fixed matplotlib random seed for plot reproducibility
- Fixed scale family definitions in config_h_m2.py

---

### NFR4: Memory Efficiency (≤8 GB)

**Memory Profile:**
- h-m1 features: 50 models × 7 features × 8 bytes = 2.8 KB (negligible)
- Statistical results: ~10 KB (Cohen's d, CV values)
- Matplotlib figures: ~5 MB (3 subplots)
- **Peak RAM: <50 MB** (well below 8 GB threshold)

---

## Validation Report Template (04_validation.md)

```markdown
# Validation Report: H-M2 Parameter Allocation Pattern

**Date:** 2026-07-11  
**Runtime:** X.X minutes  

---

## Gate Decision: [PASS | FAIL]

**Primary Criteria (MUST_WORK):**
- P1: Cohen's d >1.0 → [PASS | FAIL] (actual: X.XX)
- P2: ResNet CV <0.15 → [PASS | FAIL] (actual: X.XX)

**Decision:** [PASS both → Proceed to H-M3 | FAIL → remediation]

---

## Primary Results

### P1: Inter-Family Separation (Cohen's d)

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| Cohen's d (CNN vs Transformer) | X.XX | >1.0 | [PASS|FAIL] |
| Mean R (CNN) | X.XXX | - | - |
| Mean R (Transformer) | X.XXX | - | - |
| Std R (CNN) | X.XXX | - | - |
| Std R (Transformer) | X.XXX | - | - |

### P2: Intra-Family Scale Invariance (CV)

| Family | CV | Mean R | Std R | Threshold | Status |
|--------|-----|--------|-------|-----------|--------|
| ResNet | X.XX | X.XXX | X.XXX | <0.15 | [PASS|FAIL] |
| EfficientNet | X.XX | X.XXX | X.XXX | <0.15 | [PASS|FAIL] |
| ViT | X.XX | X.XXX | X.XXX | <0.15 | [PASS|FAIL] |

---

## Secondary Results

### S1: Statistical Significance

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| p-value (t-test) | X.XXX | <0.05 | [PASS|FAIL] |
| t-statistic | X.XX | - | - |

### S2: Distribution Separation

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| Mean R_CNN - Mean R_Transformer | X.XXX | >0.4 | [PASS|FAIL] |

### S3: Edge Case Robustness

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| CNN violation rate | X.X% | ≤25% | [PASS|FAIL] |
| Transformer violation rate | X.X% | ≤25% | [PASS|FAIL] |

**Edge Cases Detected:**
- VGG-16 (NormFree): R = X.XXX
- PoolFormer (MetaFormer): R = X.XXX
- ConvNeXt: R = X.XXX
- MLP-Mixer: R = X.XXX

---

## Key Findings

1. **Parameter-Mass Ratio Distributions:**
   - CNN: R = X.XXX ± X.XXX (range: X.XXX - X.XXX)
   - Transformer: R = X.XXX ± X.XXX (range: X.XXX - X.XXX)
   - Hybrid: R = X.XXX ± X.XXX (range: X.XXX - X.XXX)

2. **Scale Invariance:**
   - ResNet-{18,34,50,101,152}: CV = X.XX (stable across scales)
   - EfficientNet-B{0,4}: CV = X.XX
   - ViT-{tiny,small,base,large}: CV = X.XX

3. **Effect Size:**
   - Cohen's d = X.XX (very large effect, strong separation)
   - Statistical significance: p < X.XXX

---

## Recommendations

[If PASS:]
- Proceed to H-M3 (next mechanism step)
- Parameter allocation pattern confirmed as architectural signature
- R metric validated for scale-invariant discrimination

[If FAIL P1 (d ≤1.0):]
- EXPLORE alternative ratios: attention_params / total_params
- Investigate attention mechanism as complementary feature

[If FAIL P2 (CV ≥0.15):]
- PIVOT to normalized R: (R - μ_family) / σ_family
- Analyze scale confounding factors
```

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Cohen's d (CNN vs Transformer) | >1.0 | (μ_CNN - μ_Transformer) / σ_pooled |
| CV (ResNet family) | <0.15 | σ / μ |
| p-value (t-test) | <0.05 | scipy.stats.ttest_ind |
| Mean separation | >0.4 | μ_CNN - μ_Transformer |
| Edge case violation rate | ≤25% | violations / edge_case_models |
| Runtime | ≤10 min | time.time() end - start |
| Memory | ≤8 GB | memory_profiler peak |

---

## Document Metadata

**Version:** 1.0  
**Last Updated:** 2026-07-11  
**Status:** APPROVED for Phase 4 Implementation  
**Estimated Implementation Time:** 8 hours  
**Estimated Runtime:** 5 minutes  
**Code Reuse:** 70% data reuse (features), 30% code reuse  
**New Code:** 6 modules, ~350 LOC
