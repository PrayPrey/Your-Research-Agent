# Architecture Design: H-M1 Normalization Layer Fingerprinting

**Hypothesis ID:** h-m1  
**Type:** MECHANISM (MUST_WORK gate)  
**Date:** 2026-07-11  
**Applied Patterns:** sklearn pipeline + state_dict regex + violation detection  

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis  
**Status:** Reusing components from h-e1 validated codebase  
**Analyzed Path:** docs/youra_research/h-e1/code/  
**Findings:** 80%+ code reuse - FeatureExtractor, DataLoader, Classifier already implement normalization counting via regex

---

## Design Philosophy

MECHANISM architecture extending EXISTENCE (h-e1):
- Reuse h-e1's proven feature extraction pipeline (88.89% validation accuracy)
- Add 3 new analysis modules: ViolationRateAnalyzer, NormalizationDistributionAnalyzer, EdgeCaseDetector
- Validate normalization layer choice as architectural signature (MUST_WORK gate: ≤15% violation rate)
- CPU-only, runtime ≤20 min, memory ≤8 GB

---

## System Overview

### Component Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│ H-M1 Normalization Fingerprinting System                            │
├─────────────────────────────────────────────────────────────────────┤
│ [REUSED FROM H-E1] (80% Code Reuse)                                 │
│  ├─ StatisticalFeatureExtractor  (feature_extractor.py)             │
│  │   └─ extract_features() → {bn_count, ln_count, gn_count, ...}    │
│  ├─ TIMMDataLoader              (data_loader.py)                    │
│  │   └─ download_models() → 50 models, 70/30 split                  │
│  ├─ LogisticClassifierTrainer   (classifier_trainer.py)             │
│  │   └─ load_artifacts() → trained classifier from h-e1             │
│  └─ Config                      (config.py)                         │
│      └─ NORM_PATTERNS, MODEL_FAMILIES, FEATURE_NAMES                │
├─────────────────────────────────────────────────────────────────────┤
│ [NEW H-M1 COMPONENTS] (20% New Code)                                │
│  ├─ ViolationRateAnalyzer       (violation_analyzer.py)             │
│  │   └─ compute_violation_rates() → CNN/Trans violation ≤15%        │
│  ├─ NormalizationDistributionAnalyzer (distribution_analyzer.py)    │
│  │   └─ compute_distributions() → per-family statistics             │
│  ├─ EdgeCaseDetector            (edge_case_detector.py)             │
│  │   └─ detect_edge_cases() → NormFree, MetaFormer, ConvNeXt        │
│  └─ H_M1_Runner                 (main_h_m1.py)                      │
│      └─ run_mechanism_validation() → orchestrate all analyses       │
└─────────────────────────────────────────────────────────────────────┘
```

### Data Flow

```
Input: TIMM Model Zoo (50 models from h-e1)
  ↓
[1] TIMMDataLoader.download_models()
  → [(model_name, family, state_dict), ...]
  ↓
[2] StatisticalFeatureExtractor.extract_features()
  → {bn_count, ln_count, gn_count, no_norm_flag, param_mass_ratio}
  ↓
[3] Create features DataFrame
  → train_df (35 models), val_df (15 models)
  ↓
[4] ViolationRateAnalyzer.compute_violation_rates()
  → {cnn_violation_rate, transformer_violation_rate, violations_list}
  ↓
[5] NormalizationDistributionAnalyzer.compute_distributions()
  → {family: {bn_count: {mean, median, std}, dominant_norm}}
  ↓
[6] EdgeCaseDetector.detect_edge_cases()
  → {NormFree: [VGG-16], MetaFormer: [PoolFormer], ConvNeXt: [...]}
  ↓
[7] LogisticClassifierTrainer.load_artifacts() + extract feature importance
  → {feature: coefficient, rank}
  ↓
Output: CSV reports, JSON distributions, 04_validation.md
```

---

## Module Design

### 1. ViolationRateAnalyzer (`src/violation_analyzer.py`)

**Dependencies:** pandas, numpy

```python
class ViolationRateAnalyzer:
    def __init__(self, threshold: float = 0.15): ...
    
    def compute_violation_rates(self, features_df: pd.DataFrame) -> dict:
        """
        Compute per-class violation rates for normalization paradigms.
        
        Violation Definitions:
        - CNN violation: ln_count > bn_count (LayerNorm dominates)
        - Transformer violation: bn_count > ln_count (BatchNorm dominates)
        - Hybrid: No violation (mixed patterns expected)
        
        Args:
            features_df: DataFrame with columns [model_name, family, bn_count, ln_count, ...]
        
        Returns:
            {
                'cnn_violation_rate': float,
                'transformer_violation_rate': float,
                'cnn_violations': list[str],  # model names
                'transformer_violations': list[str],
                'cnn_passed': bool,  # ≤15% threshold
                'transformer_passed': bool,
                'gate_decision': str  # 'PASS' or 'FAIL'
            }
        """
        ...
    
    def _compute_family_violation_rate(self, family_df: pd.DataFrame, family: str) -> tuple:
        """Helper: compute violation rate for single family"""
        ...
    
    def save_violation_report(self, results: dict, output_path: str):
        """Save violation rates to CSV"""
        ...
```

**Interface:**
- Input: features_df (from h-e1 FeatureExtractor)
- Output: Violation rates + gate decision (PASS/FAIL)
- MUST_WORK Gate: Both CNN and Transformer violation rates ≤15%

---

### 2. NormalizationDistributionAnalyzer (`src/distribution_analyzer.py`)

**Dependencies:** pandas, numpy, json

```python
class NormalizationDistributionAnalyzer:
    def __init__(self): ...
    
    def compute_distributions(self, features_df: pd.DataFrame) -> dict:
        """
        Compute per-family normalization layer statistics.
        
        Args:
            features_df: DataFrame with [family, bn_count, ln_count, gn_count]
        
        Returns:
            {
                'CNN': {
                    'bn_count': {'mean': float, 'median': float, 'std': float},
                    'ln_count': {'mean': float, 'median': float, 'std': float},
                    'gn_count': {'mean': float, 'median': float, 'std': float},
                    'dominant_norm': str  # 'BatchNorm' | 'LayerNorm' | 'GroupNorm' | 'Mixed'
                },
                'Transformer': {...},
                'Hybrid': {...}
            }
        """
        ...
    
    def _compute_family_stats(self, family_df: pd.DataFrame) -> dict:
        """Helper: compute statistics for single family"""
        ...
    
    def _determine_dominant_norm(self, family_df: pd.DataFrame) -> str:
        """Helper: identify dominant normalization type (>50% models)"""
        ...
    
    def save_distributions(self, distributions: dict, output_path: str):
        """Save distributions to JSON"""
        ...
    
    def generate_distribution_table(self, distributions: dict) -> str:
        """Generate markdown table for validation report"""
        ...
```

**Interface:**
- Input: features_df (from h-e1)
- Output: Per-family statistics + dominant normalization type
- Expected: CNN → BatchNorm, Transformer → LayerNorm, Hybrid → Mixed

---

### 3. EdgeCaseDetector (`src/edge_case_detector.py`)

**Dependencies:** pandas, json

```python
class EdgeCaseDetector:
    def __init__(self): ...
    
    def detect_edge_cases(self, features_df: pd.DataFrame) -> dict:
        """
        Identify and categorize edge case models.
        
        Categories:
        1. NormFree: no_norm_flag == 1 (e.g., VGG-16)
        2. MetaFormer: 'poolformer' in model_name (non-standard LayerNorm)
        3. ConvNeXt: 'convnext' in model_name (modern CNN with LayerNorm)
        
        Args:
            features_df: DataFrame with [model_name, family, bn_count, ln_count, no_norm_flag]
        
        Returns:
            {
                'NormFree': [
                    {'model': str, 'family': str, 'bn_count': int, 'ln_count': int, 'notes': str}
                ],
                'MetaFormer': [...],
                'ConvNeXt': [...],
                'total_edge_cases': int,
                'edge_case_rate': float  # edge_cases / total_models
            }
        """
        ...
    
    def _detect_normfree(self, features_df: pd.DataFrame) -> list:
        """Detect models with no normalization layers"""
        ...
    
    def _detect_metaformer(self, features_df: pd.DataFrame) -> list:
        """Detect PoolFormer and similar MetaFormer architectures"""
        ...
    
    def _detect_convnext(self, features_df: pd.DataFrame) -> list:
        """Detect modern CNNs using LayerNorm"""
        ...
    
    def save_edge_cases(self, edge_cases: dict, output_path: str):
        """Save edge cases to JSON"""
        ...
    
    def generate_edge_case_table(self, edge_cases: dict) -> str:
        """Generate markdown table for validation report"""
        ...
```

**Interface:**
- Input: features_df (from h-e1)
- Output: Categorized edge cases (NormFree, MetaFormer, ConvNeXt)
- Acceptance: 100% detection for known edge cases (VGG-16, PoolFormer)

---

### 4. FeatureImportanceExtractor (`src/feature_importance.py`)

**Dependencies:** sklearn, pandas, numpy

```python
class FeatureImportanceExtractor:
    def __init__(self, feature_names: list[str]): ...
    
    def extract_importance(self, classifier, feature_names: list[str]) -> pd.DataFrame:
        """
        Extract and rank feature importance from LogisticRegression coefficients.
        
        Method: Average absolute coefficient across 3 classes (CNN, Transformer, Hybrid)
        
        Args:
            classifier: Trained sklearn LogisticRegression
            feature_names: ['bn_count', 'ln_count', 'gn_count', 'no_norm_flag', 'param_mass_ratio']
        
        Returns:
            DataFrame with columns [feature, coefficient, rank, interpretation]
            Sorted descending by absolute coefficient
        """
        ...
    
    def _compute_average_coefficient(self, classifier, feature_idx: int) -> float:
        """Helper: average |coef| across classes"""
        ...
    
    def _interpret_coefficient(self, feature: str, coef: float) -> str:
        """Helper: generate human-readable interpretation"""
        ...
    
    def save_feature_importance(self, importance_df: pd.DataFrame, output_path: str):
        """Save feature importance to CSV"""
        ...
    
    def check_normalization_feature_importance(self, importance_df: pd.DataFrame) -> dict:
        """
        Validate S1 criterion: bn_count, ln_count coefficients > 0.1
        
        Returns:
            {
                'bn_count_coef': float,
                'ln_count_coef': float,
                'bn_passed': bool,  # > 0.1
                'ln_passed': bool,  # > 0.1
                's1_criterion_passed': bool  # both > 0.1
            }
        """
        ...
```

**Interface:**
- Input: Trained classifier (loaded from h-e1), feature_names
- Output: Feature importance ranking + S1 criterion validation
- Expected: bn_count > ln_count > gn_count (within norm features)

---

### 5. H_M1_Runner (`main_h_m1.py`)

**Dependencies:** All h-m1 modules + h-e1 modules

```python
class H_M1_Runner:
    def __init__(self, base_hypothesis_dir: str, output_dir: str): ...
    
    def run_mechanism_validation(self) -> dict:
        """
        Main orchestration function for H-M1 validation.
        
        Steps:
        1. Load h-e1 features (train_features.csv, val_features.csv)
        2. Load h-e1 trained classifier
        3. Run ViolationRateAnalyzer → P1, P2 gate criteria
        4. Run NormalizationDistributionAnalyzer → per-family statistics
        5. Run EdgeCaseDetector → NormFree, MetaFormer, ConvNeXt
        6. Run FeatureImportanceExtractor → S1 criterion
        7. Generate 04_validation.md report
        
        Returns:
            {
                'violation_results': dict,
                'distribution_results': dict,
                'edge_case_results': dict,
                'feature_importance_results': dict,
                'gate_decision': str,  # 'PASS' or 'FAIL'
                'runtime_seconds': float
            }
        """
        ...
    
    def _load_h_e1_artifacts(self) -> tuple:
        """Load features and classifier from h-e1"""
        ...
    
    def _run_analyses(self, features_df: pd.DataFrame, classifier) -> dict:
        """Run all 4 analysis modules"""
        ...
    
    def _generate_validation_report(self, results: dict, output_path: str):
        """Generate 04_validation.md with all results"""
        ...
    
    def _save_all_outputs(self, results: dict):
        """Save CSV/JSON outputs"""
        ...
```

**Interface:**
- Input: h-e1 artifacts (features, classifier)
- Output: 04_validation.md + CSV/JSON reports
- Orchestration: Sequential pipeline (no parallelization)

---

## External Dependencies (Base Hypothesis)

### Module Paths (From h-e1 Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| StatisticalFeatureExtractor | `from h_e1.src.feature_extractor import StatisticalFeatureExtractor` | `h-e1/code/src/feature_extractor.py` |
| TIMMDataLoader | `from h_e1.src.data_loader import TIMMDataLoader` | `h-e1/code/src/data_loader.py` |
| LogisticClassifierTrainer | `from h_e1.src.classifier_trainer import LogisticClassifierTrainer` | `h-e1/code/src/classifier_trainer.py` |
| Config (NORM_PATTERNS, MODEL_FAMILIES, FEATURE_NAMES) | `from h_e1.config import *` | `h-e1/code/config.py` |

**Verified from:** `docs/youra_research/h-e1/code/` (actual implementation)

**Note:** h-m1 will reference h-e1 modules via relative import or absolute path, NOT copy-paste code. This ensures single source of truth for feature extraction logic.

---

## Data Schemas

### Input Schema (from h-e1)

**train_features.csv / val_features.csv:**
```
model_name,family,bn_count,ln_count,gn_count,no_norm_flag,param_mass_ratio
resnet18,CNN,20,0,0,0,0.997
vit_tiny_patch16_224,Transformer,0,24,0,0,0.015
mixer_b16_224,Hybrid,0,12,0,0,0.000
vgg16,CNN,0,0,0,1,0.995
```

**classifier.pkl / scaler.pkl:**
- Trained LogisticRegression (3 classes: CNN, Transformer, Hybrid)
- StandardScaler fitted on training data

### Output Schemas

**h-m1_violation_rates.csv:**
```
family,total_models,violations,violation_rate,threshold,status
CNN,24,2,0.083,0.15,PASS
Transformer,15,1,0.067,0.15,PASS
```

**h-m1_feature_importance.csv:**
```
feature,coefficient,rank,interpretation
param_mass_ratio,2.456,1,Strong discriminator (conv vs linear mass)
bn_count,0.823,2,Moderate discriminator (CNN signature)
ln_count,0.567,3,Moderate discriminator (Transformer signature)
no_norm_flag,0.234,4,Weak discriminator (NormFree detection)
gn_count,0.012,5,Negligible (GroupNorm rare)
```

**h-m1_norm_distributions.json:**
```json
{
  "CNN": {
    "bn_count": {"mean": 18.5, "median": 20.0, "std": 4.2},
    "ln_count": {"mean": 0.3, "median": 0.0, "std": 1.1},
    "gn_count": {"mean": 0.0, "median": 0.0, "std": 0.0},
    "dominant_norm": "BatchNorm"
  },
  "Transformer": {
    "bn_count": {"mean": 0.8, "median": 0.0, "std": 2.1},
    "ln_count": {"mean": 22.3, "median": 24.0, "std": 5.6},
    "gn_count": {"mean": 0.0, "median": 0.0, "std": 0.0},
    "dominant_norm": "LayerNorm"
  },
  "Hybrid": {...}
}
```

**h-m1_edge_cases.json:**
```json
{
  "NormFree": [
    {"model": "vgg16", "family": "CNN", "bn_count": 0, "ln_count": 0, "notes": "No normalization layers"}
  ],
  "MetaFormer": [
    {"model": "poolformer_m36", "family": "Transformer", "bn_count": 0, "ln_count": 12, "notes": "Token mixer architecture"}
  ],
  "ConvNeXt": [
    {"model": "convnext_tiny", "family": "CNN", "bn_count": 2, "ln_count": 9, "notes": "Modern CNN with LayerNorm"}
  ],
  "total_edge_cases": 5,
  "edge_case_rate": 0.10
}
```

---

## Integration Points

### H-M1 ↔ H-E1 Integration

```
H-E1 Outputs (Prerequisites)
  ├─ train_features.csv      → ViolationRateAnalyzer, DistributionAnalyzer, EdgeCaseDetector
  ├─ val_features.csv        → Same as above (validation set)
  ├─ classifier.pkl          → FeatureImportanceExtractor
  └─ scaler.pkl              → Not needed for h-m1 (no prediction, only analysis)

H-M1 Modules (New Components)
  ├─ ViolationRateAnalyzer   → Reads features, computes violation rates
  ├─ DistributionAnalyzer    → Reads features, computes statistics
  ├─ EdgeCaseDetector        → Reads features, detects edge cases
  └─ FeatureImportanceExtractor → Reads classifier, extracts coefficients

H-M1 Outputs (For H-M2)
  ├─ h-m1_violation_rates.csv    → Primary gate decision (P1, P2)
  ├─ h-m1_feature_importance.csv → Secondary criterion (S1)
  ├─ h-m1_norm_distributions.json → Distribution evidence
  ├─ h-m1_edge_cases.json        → Edge case documentation
  └─ 04_validation.md            → Human-readable report + gate decision
```

### Data Flow Sequence

```
[1] H_M1_Runner.run_mechanism_validation() starts
      ↓
[2] Load h-e1/outputs/train_features.csv
      ↓
[3] ViolationRateAnalyzer.compute_violation_rates(features_df)
      → Compute CNN violation rate (ln_count > bn_count)
      → Compute Transformer violation rate (bn_count > ln_count)
      → Check P1: CNN ≤15%, P2: Transformer ≤15%
      ↓
[4] NormalizationDistributionAnalyzer.compute_distributions(features_df)
      → Compute mean/median/std for bn_count, ln_count, gn_count per family
      → Determine dominant_norm per family (expected: CNN→BN, Trans→LN)
      ↓
[5] EdgeCaseDetector.detect_edge_cases(features_df)
      → Detect NormFree (no_norm_flag == 1)
      → Detect MetaFormer ('poolformer' in model_name)
      → Detect ConvNeXt ('convnext' in model_name)
      ↓
[6] Load h-e1/outputs/classifier.pkl
      ↓
[7] FeatureImportanceExtractor.extract_importance(classifier)
      → Compute average |coefficient| across 3 classes
      → Rank features descending
      → Check S1: bn_count > 0.1, ln_count > 0.1
      ↓
[8] Generate 04_validation.md
      → Primary Criteria: P1, P2 (MUST_WORK gate)
      → Secondary Criteria: S1, S2, S3
      → Gate Decision: PASS/FAIL
      ↓
[9] Save outputs to h-m1/outputs/
      ↓
[10] Return gate_decision + results summary
```

---

## Error Handling

### Edge Case Handling

| Edge Case | Detection | Handling | Impact on Gate |
|-----------|-----------|----------|----------------|
| **NormFree (VGG-16)** | `no_norm_flag == 1` | Flag as edge case, exclude from violation rate if needed | May increase CNN violation rate → documented risk |
| **MetaFormer (PoolFormer)** | `'poolformer' in model_name` | Flag as Transformer edge case (non-standard LN) | May increase Transformer violation rate → acceptable if ≤15% |
| **ConvNeXt (Modern CNN)** | `'convnext' in model_name` | Flag as CNN edge case (uses LayerNorm) | Expected to violate CNN paradigm → documented in 04_validation.md |
| **DeiT Stem BatchNorm** | `bn_count > 0` in Transformer | Not an edge case (h-e1 showed 13.33% BN in Transformers) | Acceptable if ≤15% |
| **GroupNorm Presence** | `gn_count > 0` | Log occurrence, no special handling | Not expected (h-e1 showed gn_count=0 for all models) |

### Violation Rate Edge Cases

**Scenario 1: CNN violation rate 16% (marginal fail)**
- **Root Cause:** ConvNeXt models (modern CNNs with LayerNorm)
- **Mitigation:** Document as "modern CNN" category, propose temporal feature (release year)
- **Gate Decision:** FAIL → PIVOT to alternative features or refined taxonomy

**Scenario 2: Transformer violation rate 14% (marginal pass)**
- **Root Cause:** DeiT stem BatchNorm (known from h-e1)
- **Mitigation:** Acceptable (within ≤15% threshold)
- **Gate Decision:** PASS

**Scenario 3: Hybrid family shows violations**
- **Root Cause:** No violation definition for Hybrid (mixed patterns expected)
- **Mitigation:** Skip violation check for Hybrid, only report CNN/Transformer
- **Gate Decision:** No impact

### Feature Importance Edge Cases

**Scenario 1: gn_count coefficient > 0.1 (unexpected)**
- **Root Cause:** GroupNorm models added to TIMM since h-e1
- **Mitigation:** Log finding, update hypothesis for future work
- **Gate Decision:** No impact (S1 only checks bn_count, ln_count)

**Scenario 2: no_norm_flag coefficient < 0.1 (expected)**
- **Root Cause:** NormFree models rare (only VGG-16 in dataset)
- **Mitigation:** Expected behavior, document as low-importance feature
- **Gate Decision:** No impact

---

## Testing Strategy

### Unit Tests

**test_violation_analyzer.py:**
```python
def test_cnn_violation_detection():
    # Test: ln_count > bn_count triggers CNN violation
    ...

def test_transformer_violation_detection():
    # Test: bn_count > ln_count triggers Transformer violation
    ...

def test_hybrid_no_violation():
    # Test: Hybrid family skips violation check
    ...

def test_violation_rate_calculation():
    # Test: violations / total_models = violation_rate
    ...

def test_gate_decision_pass():
    # Test: Both ≤15% → PASS
    ...

def test_gate_decision_fail():
    # Test: Either >15% → FAIL
    ...
```

**test_distribution_analyzer.py:**
```python
def test_compute_family_stats():
    # Test: mean, median, std calculation for single family
    ...

def test_dominant_norm_batchnorm():
    # Test: CNN → 'BatchNorm' when >50% models have bn_count > ln_count
    ...

def test_dominant_norm_layernorm():
    # Test: Transformer → 'LayerNorm' when >50% models have ln_count > bn_count
    ...

def test_dominant_norm_mixed():
    # Test: Hybrid → 'Mixed' when no clear majority
    ...
```

**test_edge_case_detector.py:**
```python
def test_detect_normfree():
    # Test: no_norm_flag == 1 detected as NormFree
    ...

def test_detect_metaformer():
    # Test: 'poolformer' in model_name detected
    ...

def test_detect_convnext():
    # Test: 'convnext' in model_name detected
    ...

def test_edge_case_rate_calculation():
    # Test: edge_cases / total_models
    ...
```

**test_feature_importance.py:**
```python
def test_extract_importance():
    # Test: average |coef| across classes
    ...

def test_s1_criterion_pass():
    # Test: bn_count > 0.1 AND ln_count > 0.1
    ...

def test_s1_criterion_fail():
    # Test: Either ≤0.1 → S1 fails
    ...
```

### Integration Tests

**test_h_m1_runner.py:**
```python
def test_run_mechanism_validation():
    # Test: End-to-end pipeline from h-e1 artifacts to 04_validation.md
    ...

def test_load_h_e1_artifacts():
    # Test: Load train_features.csv, classifier.pkl from h-e1/outputs/
    ...

def test_generate_validation_report():
    # Test: 04_validation.md contains all 5 sections (P1, P2, S1, S2, S3)
    ...

def test_save_all_outputs():
    # Test: CSV/JSON files written to h-m1/outputs/
    ...
```

### Manual Validation (10 Sample Models)

**Manual regex accuracy check (S2 criterion):**
```python
# Sample 10 models randomly
# For each model:
#   1. Print state_dict.keys()
#   2. Manually count BN/LN/GN keys
#   3. Compare with FeatureExtractor output
#   4. Accuracy = matches / 10 ≥ 0.95 (9/10 correct)
```

**Sample models for manual check:**
- resnet18 (CNN, expect high bn_count)
- vit_tiny_patch16_224 (Transformer, expect high ln_count)
- mixer_b16_224 (Hybrid, expect mixed)
- vgg16 (NormFree, expect no_norm_flag=1)
- poolformer_m36 (MetaFormer, expect ln_count)
- convnext_tiny (ConvNeXt, expect ln_count in CNN)
- deit_tiny_patch16_224 (DeiT, expect ln_count + potential bn_count in stem)
- efficientnet_b0 (CNN, expect bn_count)
- swin_tiny_patch4_window7_224 (Transformer, expect ln_count)
- pit_b_224 (Hybrid, expect mixed)

---

## Epic Tasks

### Task Breakdown with Complexity Scores

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| **A-1** | **Project Setup** | Create h-m1/code directory, copy h-e1 modules, setup imports | **6** | Module structure (1) + imports (1) + config (2) + validation (2) |
| **A-2** | **ViolationRateAnalyzer** | Implement violation detection logic (CNN/Transformer) | **14** | Algorithm (4) + edge cases (3) + gate logic (3) + testing (4) |
| **A-3** | **NormalizationDistributionAnalyzer** | Implement per-family statistics (mean, median, std, dominant_norm) | **12** | Statistics (3) + dominant_norm logic (2) + families (3) + testing (4) |
| **A-4** | **EdgeCaseDetector** | Implement NormFree, MetaFormer, ConvNeXt detection | **10** | Detection rules (3) + categories (2) + testing (3) + integration (2) |
| **A-5** | **FeatureImportanceExtractor** | Extract coefficients from h-e1 classifier, rank features | **11** | Coefficient extraction (3) + ranking (2) + S1 validation (2) + testing (4) |
| **A-6** | **H_M1_Runner** | Orchestrate all analyses, generate 04_validation.md | **15** | Pipeline logic (4) + report generation (4) + integration (3) + testing (4) |
| **A-7** | **Manual Validation** | Regex accuracy check (10 models), edge case verification | **8** | Manual counting (3) + comparison (2) + documentation (3) |
| **A-8** | **Output Generation** | Write CSV/JSON files, generate markdown tables | **9** | CSV writer (2) + JSON writer (2) + markdown formatter (3) + validation (2) |
| **A-9** | **Gate Decision Logic** | Implement PASS/FAIL decision + pivot recommendations | **7** | Gate logic (2) + decision tree (2) + recommendations (2) + testing (1) |
| **A-10** | **Integration Testing** | End-to-end test from h-e1 artifacts to final report | **10** | Test setup (2) + execution (3) + validation (3) + debugging (2) |
| **A-11** | **Documentation** | Update 03_architecture.md, code comments, docstrings | **4** | Architecture doc (1) + code comments (1) + docstrings (2) |
| **A-12** | **Runtime Optimization** | Profile runtime, optimize if >20 min | **6** | Profiling (2) + bottleneck identification (2) + optimization (2) |

**Total Complexity:** 112  
**Distribution:** VeryHigh (18-20): [], High (14-17): [A-2, A-6], Medium (9-13): [A-3, A-4, A-5, A-8, A-10], Low (4-8): [A-1, A-7, A-9, A-11, A-12]

**Complexity Legend:**
- **Module Size (1-5):** Lines of code, number of methods
- **Dependencies (1-5):** External modules, integration complexity
- **Algorithm (1-5):** Logic complexity, edge case handling
- **Integration (1-5):** Testing, validation, debugging effort

---

## Non-Functional Requirements

### NFR1: Code Reuse from H-E1 (≥80%)

**Reused Components (from h-e1/code/):**
1. `StatisticalFeatureExtractor.extract_features()` - Normalization counting (NORM_PATTERNS regex)
2. `TIMMDataLoader.download_models()` - 50 models, 70/30 split
3. `LogisticClassifierTrainer` - Trained classifier, feature importance
4. `config.py` - MODEL_FAMILIES, NORM_PATTERNS, FEATURE_NAMES

**New Components (h-m1 only):**
1. `ViolationRateAnalyzer` - New logic
2. `NormalizationDistributionAnalyzer` - New logic
3. `EdgeCaseDetector` - New logic
4. `FeatureImportanceExtractor` - New logic
5. `H_M1_Runner` - New orchestration

**Code Reuse Calculation:**
- Reused: 4 modules (~400 LOC from h-e1)
- New: 5 modules (~100 LOC for h-m1)
- Reuse rate: 400 / (400 + 100) = 80% ✓

---

### NFR2: Runtime Performance (≤20 minutes)

**Runtime Breakdown:**
- Model loading: 0 min (reuse h-e1 features, no re-download)
- Feature extraction: 0 min (reuse h-e1 features)
- ViolationRateAnalyzer: <1 min (50 models × regex check)
- DistributionAnalyzer: <1 min (pandas groupby + statistics)
- EdgeCaseDetector: <1 min (string matching)
- FeatureImportanceExtractor: <1 min (sklearn coefficient extraction)
- Report generation: <1 min (markdown writing)
- **Total: ~5 minutes** (well below 20 min threshold)

**Optimization Strategy:**
- Sequential processing (no parallelization needed)
- Reuse h-e1 features (avoid 10-min model download)
- In-memory pandas operations (no disk I/O during analysis)

---

### NFR3: Reproducibility

**Determinism Guarantees:**
- Reuse h-e1 features (same 70/30 split, random_state=42)
- No randomness in h-m1 modules (deterministic regex, statistics)
- Fixed TIMM version: 1.0.9 (same as h-e1)
- Fixed sklearn version: 1.3.0 (same as h-e1)

**Verification:**
- Run h-m1 twice, compare outputs byte-by-byte
- Expected: Identical CSV/JSON files, identical 04_validation.md

---

### NFR4: Memory Efficiency (≤8 GB)

**Memory Profile:**
- h-e1 features: 50 models × 5 features × 8 bytes = 2 KB (negligible)
- h-e1 classifier: ~10 KB (sklearn LogisticRegression)
- Analysis results: ~50 KB (violation rates, distributions, edge cases)
- **Peak RAM: <100 MB** (well below 8 GB threshold)

**Memory Optimization:**
- No model loading in h-m1 (reuse h-e1 features)
- Sequential processing (no batching needed)
- Release intermediate DataFrames after analysis

---

## File Organization

```
docs/youra_research/h-m1/
├── code/
│   ├── src/
│   │   ├── violation_analyzer.py       (NEW)
│   │   ├── distribution_analyzer.py    (NEW)
│   │   ├── edge_case_detector.py       (NEW)
│   │   ├── feature_importance.py       (NEW)
│   │   └── __init__.py
│   ├── tests/
│   │   ├── test_violation_analyzer.py  (NEW)
│   │   ├── test_distribution_analyzer.py (NEW)
│   │   ├── test_edge_case_detector.py  (NEW)
│   │   ├── test_feature_importance.py  (NEW)
│   │   └── test_h_m1_runner.py         (NEW)
│   ├── main_h_m1.py                    (NEW)
│   ├── config_h_m1.py                  (NEW - h-m1 specific config)
│   └── requirements.txt                (Reuse h-e1)
├── outputs/
│   ├── h-m1_violation_rates.csv        (Output)
│   ├── h-m1_feature_importance.csv     (Output)
│   ├── h-m1_norm_distributions.json    (Output)
│   ├── h-m1_edge_cases.json            (Output)
│   └── 04_validation.md                (Output)
├── 01_research_summary.md              (Existing)
├── 02a_hypothesis_formulation.md       (Existing)
├── 02b_verification_plan.md            (Existing)
├── 02c_experiment_brief.md             (Existing)
├── 03_prd.md                           (Existing)
└── 03_architecture.md                  (This document)

Reference to h-e1 artifacts:
docs/youra_research/h-e1/
└── outputs/
    ├── train_features.csv              (Input to h-m1)
    ├── val_features.csv                (Input to h-m1)
    ├── classifier.pkl                  (Input to h-m1)
    └── scaler.pkl                      (Not used in h-m1)
```

---

## Validation Report Template (04_validation.md)

```markdown
# Validation Report: H-M1 Normalization Layer Fingerprinting

**Date:** 2026-07-11  
**Runtime:** X.X minutes  

---

## Gate Decision: [PASS | FAIL]

**Primary Criteria (MUST_WORK):**
- P1: CNN Violation Rate ≤15% → [PASS | FAIL] (actual: X.X%)
- P2: Transformer Violation Rate ≤15% → [PASS | FAIL] (actual: X.X%)

**Decision:** [PASS both → Proceed to H-M2 | FAIL either → PIVOT]

---

## Primary Results

### P1: CNN Violation Rate

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| Total CNN models | 24 | - | - |
| CNN violations | X | - | - |
| Violation rate | X.X% | ≤15% | [PASS|FAIL] |

**Violations:** [model1, model2, ...]

### P2: Transformer Violation Rate

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| Total Transformer models | 15 | - | - |
| Transformer violations | X | - | - |
| Violation rate | X.X% | ≤15% | [PASS|FAIL] |

**Violations:** [model1, model2, ...]

---

## Secondary Results

### S1: Feature Importance

| Feature | Coefficient | Rank | Threshold | Status |
|---------|-------------|------|-----------|--------|
| bn_count | X.XXX | 2 | >0.1 | [PASS|FAIL] |
| ln_count | X.XXX | 3 | >0.1 | [PASS|FAIL] |

### S2: Regex Accuracy (Manual Validation)

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| Manual matches | 9/10 | ≥9.5/10 | [PASS|FAIL] |

### S3: Edge Case Handling

| Category | Detected | Expected | Status |
|----------|----------|----------|--------|
| NormFree | [VGG-16] | [VGG-16] | PASS |
| MetaFormer | [PoolFormer] | [PoolFormer] | PASS |
| ConvNeXt | [...] | [...] | PASS |

---

## Key Findings

1. **Normalization Layer Distributions:**
   - CNN: Dominant BatchNorm (X.X% of models)
   - Transformer: Dominant LayerNorm (X.X% of models)
   - Hybrid: Mixed patterns (X.X% BN, X.X% LN)

2. **Edge Cases:**
   - NormFree: X models (X.X% of dataset)
   - MetaFormer: X models (X.X% of dataset)
   - ConvNeXt: X models (X.X% of CNN family)

3. **Feature Importance:**
   - param_mass_ratio remains strongest discriminator (coef=X.XXX)
   - Normalization counts show moderate importance (bn_count=X.XXX, ln_count=X.XXX)

---

## Recommendations for H-M2

[If PASS:]
- Proceed to H-M2: Parameter Mass Ratio Verification
- Investigate edge cases (ConvNeXt, MetaFormer) for refined taxonomy
- Consider temporal feature (model release year) for future work

[If FAIL:]
- Pivot to alternative features (attention mechanism detection, model depth)
- Refine architecture taxonomy (Legacy CNN vs Modern CNN)
- Add temporal feature to account for architectural evolution
```

---

## Risk Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| ConvNeXt increases CNN violation rate | High | Critical | Document as "modern CNN" edge case, propose temporal feature |
| DeiT stem BatchNorm increases Transformer violation | Medium | Moderate | Acceptable if ≤15% (h-e1 showed 13.33%) |
| Regex false negatives | Low | Moderate | Manual validation (S2 criterion) catches errors |
| GroupNorm models added to TIMM | Low | Low | Log occurrence, update hypothesis for future work |
| Runtime >20 min | Low | Low | Profiling + optimization (h-m1 reuses h-e1 features, no model download) |
| Memory >8 GB | Very Low | Low | Sequential processing, no model loading in h-m1 |

---

## Acceptance Criteria Summary

**Primary (MUST_WORK Gate):**
- ✓ CNN violation rate ≤15%
- ✓ Transformer violation rate ≤15%

**Secondary:**
- ✓ Feature importance: bn_count > 0.1, ln_count > 0.1
- ✓ Regex accuracy ≥95% (manual validation)
- ✓ Edge case detection 100% (NormFree, MetaFormer, ConvNeXt)

**Non-Functional:**
- ✓ Code reuse ≥80% from h-e1
- ✓ Runtime ≤20 minutes
- ✓ Memory ≤8 GB
- ✓ Reproducibility (fixed seed=42, same split)

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| CNN violation rate | ≤15% | violations / total_cnn_models |
| Transformer violation rate | ≤15% | violations / total_transformer_models |
| Feature importance (bn_count) | >0.1 | avg(\|coef\|) across classes |
| Feature importance (ln_count) | >0.1 | avg(\|coef\|) across classes |
| Regex accuracy | ≥95% | manual_matches / 10 |
| Edge case detection | 100% | detected / known_edge_cases |
| Code reuse | ≥80% | reused_loc / total_loc |
| Runtime | ≤20 min | time.time() end - start |
| Memory | ≤8 GB | memory_profiler peak |

---

## Appendix: Technical Decisions

### Why Reuse h-e1 Features Instead of Re-Extract?

**Rationale:**
- h-e1 already validated feature extraction (88.89% accuracy)
- Avoids 10-minute model download
- Ensures identical features for comparison
- Reduces runtime to ~5 minutes

**Trade-off:**
- Dependent on h-e1 artifacts (must exist)
- Cannot modify feature extraction logic without re-running h-e1

**Decision:** Reuse h-e1 features (benefits outweigh costs)

---

### Why Sequential Pipeline (No Parallelization)?

**Rationale:**
- Analysis modules independent (no data dependencies)
- Runtime already <5 min (parallelization overhead not justified)
- Simpler code, easier debugging

**Trade-off:**
- Could parallelize if runtime >20 min
- Minimal speedup for I/O-bound tasks

**Decision:** Sequential pipeline (KISS principle)

---

### Why Average Absolute Coefficient for Feature Importance?

**Rationale:**
- LogisticRegression is one-vs-rest (3 classes → 3 coefficient vectors)
- Different classes may have opposite signs (CNN: +bn_count, Transformer: -bn_count)
- Absolute value captures discriminative power regardless of direction
- Average across classes provides global importance ranking

**Alternative Considered:**
- Use only CNN class coefficients → biased toward CNN features
- Use L2 norm of coefficient vector → similar results, less interpretable

**Decision:** Average absolute coefficient (standard practice)

---

## Document Metadata

**Version:** 1.0  
**Last Updated:** 2026-07-11  
**Status:** APPROVED for Phase 4 Implementation  
**Estimated Implementation Time:** 5 hours  
**Estimated Runtime:** 5 minutes  
**Code Reuse:** 80% from h-e1  
**New Code:** 5 modules, ~100 LOC
