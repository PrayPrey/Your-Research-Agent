# Logic Specification: H-M2 Parameter Allocation Pattern

**Hypothesis ID:** h-m2  
**Type:** MECHANISM (MUST_WORK gate)  
**Date:** 2026-07-11  
**Status:** Ready for Phase 4 Implementation  

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis  
**Status:** Extending h-m1 validated codebase (0% CNN violation, 14.29% Transformer violation)  
**Analyzed Path:** `docs/youra_research/h-m1/code/`  
**Relevant Symbols:** StatisticalFeatureExtractor, TIMMDataLoader, MODEL_FAMILIES, FEATURE_NAMES  
**Code Reuse:** 70% data reuse (features pre-extracted), 30% code reuse (config, utilities)

---

## Knowledge Base Patterns Applied

**Applied:** SciPy statistical tests (t-test, Cohen's d), Pandas groupby CV computation, Matplotlib multi-subplot visualization

---

## A-1: CohensDAnalyzer [Complexity: 14, Budget: 14/14]

**Applied:** SciPy independent samples t-test with pooled standard deviation

### API Signatures

```python
class CohensDAnalyzer:
    def __init__(self):
        """Initialize Cohen's d analyzer."""
        ...
    
    def compute_cohens_d(self, features_df: pd.DataFrame) -> dict:
        """
        Compute Cohen's d effect size between CNN and Transformer R distributions.
        
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
    
    def _compute_pooled_std(self, group1: np.ndarray, group2: np.ndarray) -> float:
        """Compute pooled standard deviation."""
        ...
    
    def save_results(self, results: dict, output_path: str):
        """Save results to JSON."""
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| cnn_R | (N_cnn,) | CNN param_mass_ratio values |
| transformer_R | (N_transformer,) | Transformer param_mass_ratio values |
| cohens_d | scalar | Effect size |

### Pseudo-code

```
1. Split features_df by family:
   cnn_R = features_df[features_df.family == 'CNN'].param_mass_ratio.values
   transformer_R = features_df[features_df.family == 'Transformer'].param_mass_ratio.values

2. Compute statistics:
   mean_cnn = np.mean(cnn_R)
   mean_transformer = np.mean(transformer_R)
   std_cnn = np.std(cnn_R, ddof=1)
   std_transformer = np.std(transformer_R, ddof=1)

3. Compute pooled standard deviation:
   n_cnn = len(cnn_R)
   n_transformer = len(transformer_R)
   pooled_std = sqrt(((n_cnn - 1) * std_cnn^2 + (n_transformer - 1) * std_transformer^2) / (n_cnn + n_transformer - 2))

4. Compute Cohen's d:
   cohens_d = (mean_cnn - mean_transformer) / pooled_std

5. Statistical significance test:
   t_stat, p_value = scipy.stats.ttest_ind(cnn_R, transformer_R)

6. Check P1 criterion:
   passed = (cohens_d > 1.0)

7. Return results dictionary
```

### Subtasks [14/14 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | Data filtering | Split by CNN/Transformer families |
| L-1-2 | Statistics | Compute mean/std for both groups |
| L-1-3 | Pooled std | Implement pooled variance formula |
| L-1-4 | Effect size | Compute Cohen's d |
| L-1-5 | Statistical test | Run t-test for significance |
| L-1-6 | P1 validation | Check d > 1.0 threshold |
| L-1-7 | JSON export | Save results to file |

---

## A-2: ScaleInvarianceValidator [Complexity: 12, Budget: 12/12]

**Applied:** Pandas groupby with coefficient of variation computation

### API Signatures

```python
class ScaleInvarianceValidator:
    def __init__(self, threshold: float = 0.15):
        """Initialize validator with CV threshold."""
        self.threshold = threshold
    
    def validate_scale_invariance(self, features_df: pd.DataFrame) -> dict:
        """
        Validate scale invariance via CV across model families.
        
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
    
    def _compute_cv(self, family_df: pd.DataFrame, scale_models: list[str]) -> dict:
        """Compute CV for single scale family."""
        ...
    
    def save_results(self, results: dict, output_path: str):
        """Save results to JSON."""
        ...
```

### Pseudo-code

```
1. Define scale families (from architecture):
   SCALE_FAMILIES = {
       'resnet_family': ['resnet18', 'resnet34', 'resnet50', 'resnet101', 'resnet152'],
       'efficientnet_family': ['efficientnet_b0', 'efficientnet_b4'],
       'vit_family': ['vit_tiny_patch16_224', 'vit_small_patch16_224', 'vit_base_patch16_224', 'vit_large_patch16_224']
   }

2. For each scale family:
   family_df = features_df[features_df.model_name.isin(scale_models)]
   R_values = family_df.param_mass_ratio.values

3. Compute CV:
   mean_R = np.mean(R_values)
   std_R = np.std(R_values, ddof=1)
   cv = std_R / mean_R

4. Check P2 criterion:
   passed = (cv < 0.15)

5. Primary gate uses ResNet family:
   overall_passed = results['resnet_family']['passed']

6. Return results with all scale families
```

### Subtasks [12/12 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | Config | Define SCALE_FAMILIES dictionary |
| L-2-2 | Filtering | Filter models by scale family membership |
| L-2-3 | CV computation | Compute mean, std, CV |
| L-2-4 | Multi-family | Loop over 3 scale families |
| L-2-5 | P2 validation | Check ResNet CV < 0.15 |
| L-2-6 | JSON export | Save results to file |

---

## A-3: DistributionVisualizer [Complexity: 11, Budget: 11/11]

**Applied:** Matplotlib subplots with seaborn styling

### API Signatures

```python
class DistributionVisualizer:
    def __init__(self):
        """Initialize visualizer."""
        ...
    
    def plot_R_distributions(self, features_df: pd.DataFrame, output_path: str):
        """
        Generate 3-subplot R distribution visualization.
        
        Args:
            features_df: DataFrame with ['family', 'param_mass_ratio']
            output_path: Path to save PNG file
        """
        ...
    
    def _plot_violin(self, features_df: pd.DataFrame, ax):
        """Violin plot with threshold lines."""
        ...
    
    def _plot_box(self, features_df: pd.DataFrame, ax):
        """Box plot for outlier detection."""
        ...
    
    def _plot_histogram_kde(self, features_df: pd.DataFrame, ax):
        """Histogram + KDE with family means."""
        ...
```

### Pseudo-code

```
1. Create figure with 3 subplots:
   fig, axes = plt.subplots(1, 3, figsize=(18, 5))

2. Subplot 1 - Violin plot:
   sns.violinplot(data=features_df, x='family', y='param_mass_ratio', ax=axes[0])
   axes[0].axhline(0.6, color='red', linestyle='--', label='CNN threshold')
   axes[0].axhline(0.2, color='blue', linestyle='--', label='Transformer threshold')

3. Subplot 2 - Box plot:
   sns.boxplot(data=features_df, x='family', y='param_mass_ratio', ax=axes[1])

4. Subplot 3 - Histogram + KDE:
   For family in ['CNN', 'Transformer', 'Hybrid']:
       family_R = features_df[features_df.family == family].param_mass_ratio
       axes[2].hist(family_R, alpha=0.5, label=family)
       sns.kdeplot(family_R, ax=axes[2])
       axes[2].axvline(family_R.mean(), linestyle='--')

5. Save figure:
   plt.tight_layout()
   plt.savefig(output_path, dpi=300)
```

### Subtasks [11/11 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | Subplot setup | Create 1×3 subplot grid |
| L-3-2 | Violin plot | Implement with threshold lines |
| L-3-3 | Box plot | Implement outlier detection |
| L-3-4 | Histogram | Multi-family histogram with KDE |
| L-3-5 | Styling | Apply seaborn theme, labels |
| L-3-6 | PNG export | Save high-res figure |

---

## A-4: EdgeCaseAnalyzer [Complexity: 10, Budget: 10/10]

**Applied:** Threshold-based violation detection

### API Signatures

```python
class EdgeCaseAnalyzer:
    def __init__(self, cnn_threshold: float = 0.6, transformer_threshold: float = 0.2):
        """Initialize with R thresholds."""
        self.cnn_threshold = cnn_threshold
        self.transformer_threshold = transformer_threshold
    
    def detect_edge_cases(self, features_df: pd.DataFrame) -> dict:
        """
        Detect models violating expected R thresholds.
        
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
    
    def _detect_known_edge_cases(self, features_df: pd.DataFrame) -> dict:
        """Identify known edge case models."""
        ...
    
    def save_results(self, results: dict, output_path: str):
        """Save results to JSON."""
        ...
```

### Pseudo-code

```
1. Detect CNN violations (R < 0.6):
   cnn_df = features_df[features_df.family == 'CNN']
   cnn_low_R = cnn_df[cnn_df.param_mass_ratio < 0.6].model_name.tolist()
   cnn_violation_rate = len(cnn_low_R) / len(cnn_df)

2. Detect Transformer violations (R > 0.2):
   transformer_df = features_df[features_df.family == 'Transformer']
   transformer_high_R = transformer_df[transformer_df.param_mass_ratio > 0.2].model_name.tolist()
   transformer_violation_rate = len(transformer_high_R) / len(transformer_df)

3. Detect Hybrid outliers (R < 0.2 or R > 0.6):
   hybrid_df = features_df[features_df.family == 'Hybrid']
   hybrid_outliers = hybrid_df[(hybrid_df.param_mass_ratio < 0.2) | (hybrid_df.param_mass_ratio > 0.6)].model_name.tolist()
   hybrid_outlier_rate = len(hybrid_outliers) / len(hybrid_df)

4. Identify known edge cases:
   KNOWN_EDGE_CASES = ['vgg16', 'poolformer_m36', 'convnext_tiny', 'mixer_b16_224']
   known_edge_cases = {}
   for model in KNOWN_EDGE_CASES:
       if model in features_df.model_name.values:
           row = features_df[features_df.model_name == model].iloc[0]
           known_edge_cases[model] = {'R': row.param_mass_ratio, 'family': row.family}

5. Return results dictionary
```

### Subtasks [10/10 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | CNN violations | Detect R < 0.6 |
| L-4-2 | Transformer violations | Detect R > 0.2 |
| L-4-3 | Hybrid outliers | Detect boundary cases |
| L-4-4 | Known cases | Identify VGG, PoolFormer, ConvNeXt, MLP-Mixer |
| L-4-5 | Violation rates | Compute percentages |
| L-4-6 | JSON export | Save results to file |

---

## A-5: GateDecisionMaker [Complexity: 9, Budget: 9/9]

**Applied:** Decision tree logic for MUST_WORK gate

### API Signatures

```python
class GateDecisionMaker:
    def __init__(self):
        """Initialize gate decision maker."""
        ...
    
    def evaluate_gate(self, cohens_d_results: dict, cv_results: dict) -> dict:
        """
        Evaluate MUST_WORK gate decision.
        
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
    
    def save_decision(self, decision: dict, output_path: str):
        """Save decision to text file."""
        ...
```

### Pseudo-code

```
1. Extract primary criteria results:
   p1_passed = cohens_d_results['passed']  # d > 1.0
   p2_passed = cv_results['resnet_family']['passed']  # CV < 0.15

2. Gate decision logic:
   IF p1_passed AND p2_passed:
       gate_decision = 'PASS'
       reasoning = 'Both P1 (Cohen's d > 1.0) and P2 (CV < 0.15) criteria met'
       failure_mode = None
       recommendation = 'Proceed to H-M3'
   
   ELIF NOT p1_passed:
       gate_decision = 'FAIL'
       reasoning = f'Cohen's d = {cohens_d_results["cohens_d"]:.3f} ≤ 1.0'
       failure_mode = 'Weak inter-family separation'
       recommendation = 'EXPLORE alternative ratios: attention_params / total_params'
   
   ELIF NOT p2_passed:
       gate_decision = 'FAIL'
       reasoning = f'ResNet CV = {cv_results["resnet_family"]["cv"]:.3f} ≥ 0.15'
       failure_mode = 'Scale confounding'
       recommendation = 'PIVOT to normalized R: (R - μ_family) / σ_family'

3. Return decision dictionary
```

### Subtasks [9/9 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | Criteria extraction | Get p1_passed, p2_passed |
| L-5-2 | Decision tree | Implement PASS/FAIL logic |
| L-5-3 | Failure modes | Generate failure_mode strings |
| L-5-4 | Recommendations | Generate next-step recommendations |
| L-5-5 | TXT export | Save decision to file |

---

## A-6: H_M2_Runner [Complexity: 15, Budget: 15/15]

**Applied:** Pipeline orchestration pattern

### API Signatures

```python
class H_M2_Runner:
    def __init__(self, base_dir: str = None):
        """Initialize runner with base directory."""
        self.base_dir = base_dir or 'docs/youra_research/h-m2'
        self.h_m1_dir = 'docs/youra_research/h-m1'
    
    def run_mechanism_validation(self) -> dict:
        """
        Orchestrate all h-m2 analyses.
        
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
    
    def _load_h_m1_features(self) -> pd.DataFrame:
        """Load pre-extracted features from h-m1."""
        ...
    
    def _run_analyses(self, features_df: pd.DataFrame) -> dict:
        """Run all statistical analyses."""
        ...
    
    def _generate_validation_report(self, results: dict, output_path: str):
        """Generate 04_validation.md."""
        ...
    
    def _save_all_outputs(self, results: dict):
        """Save all output files (JSON, PNG, TXT)."""
        ...
```

### Pseudo-code

```
1. Start timer:
   start_time = time.time()

2. Load h-m1 features:
   train_features = pd.read_csv(f"{self.h_m1_dir}/code/data/train_features.csv")
   val_features = pd.read_csv(f"{self.h_m1_dir}/code/data/val_features.csv")
   features_df = pd.concat([train_features, val_features])

3. Run CohensDAnalyzer (validation set only):
   cohens_d_analyzer = CohensDAnalyzer()
   cohens_d_results = cohens_d_analyzer.compute_cohens_d(val_features)

4. Run ScaleInvarianceValidator (training set):
   cv_validator = ScaleInvarianceValidator(threshold=0.15)
   cv_results = cv_validator.validate_scale_invariance(train_features)

5. Run DistributionVisualizer:
   visualizer = DistributionVisualizer()
   visualizer.plot_R_distributions(features_df, f"{self.base_dir}/outputs/R_distributions.png")

6. Run EdgeCaseAnalyzer:
   edge_analyzer = EdgeCaseAnalyzer()
   edge_results = edge_analyzer.detect_edge_cases(features_df)

7. Run GateDecisionMaker:
   gate_maker = GateDecisionMaker()
   gate_decision = gate_maker.evaluate_gate(cohens_d_results, cv_results)

8. Save all outputs:
   cohens_d_analyzer.save_results(cohens_d_results, f"{self.base_dir}/outputs/h-m2_cohens_d_report.json")
   cv_validator.save_results(cv_results, f"{self.base_dir}/outputs/h-m2_cv_report.json")
   edge_analyzer.save_results(edge_results, f"{self.base_dir}/outputs/h-m2_edge_cases.json")
   gate_maker.save_decision(gate_decision, f"{self.base_dir}/outputs/h-m2_gate_decision.txt")

9. Generate 04_validation.md:
   self._generate_validation_report(results, f"{self.base_dir}/04_validation.md")

10. End timer:
    runtime_seconds = time.time() - start_time

11. Return results
```

### Subtasks [15/15 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-6-1 | Data loading | Load h-m1 CSV features |
| L-6-2 | Cohen's d analysis | Run CohensDAnalyzer |
| L-6-3 | CV validation | Run ScaleInvarianceValidator |
| L-6-4 | Visualization | Run DistributionVisualizer |
| L-6-5 | Edge case detection | Run EdgeCaseAnalyzer |
| L-6-6 | Gate decision | Run GateDecisionMaker |
| L-6-7 | Output saving | Save 4 JSON/TXT/PNG files |
| L-6-8 | Report generation | Generate 04_validation.md |
| L-6-9 | Runtime tracking | Time entire pipeline |

---

## External Dependencies API (From h-m1)

### Verified from Actual Code

The following data and config are reused from h-m1 validated codebase:

```python
# From: docs/youra_research/h-m1/code/config.py (ACTUAL CODE)
MODEL_FAMILIES = {
    'CNN': [
        'resnet18', 'resnet34', 'resnet50', 'resnet101', 'resnet152',
        'mobilenetv3_large_100', 'efficientnet_b0', 'efficientnet_b4',
        'densenet121', 'densenet201', 'vgg16', 'vgg19',
        'convnext_tiny', 'convnext_base',
        'resnext50_32x4d', 'wide_resnet50_2',
        'regnetx_032', 'regnety_032',
        'seresnet50', 'senet154',
        'inception_v3', 'inception_v4',
        'dpn68', 'dpn131'
    ],
    'Transformer': [
        'vit_tiny_patch16_224', 'vit_small_patch16_224',
        'vit_base_patch16_224', 'vit_large_patch16_224',
        'deit_tiny_patch16_224', 'deit_small_patch16_224',
        'deit_base_patch16_224', 'deit_base_distilled_patch16_224',
        'swin_tiny_patch4_window7_224', 'swin_small_patch4_window7_224',
        'swin_base_patch4_window7_224', 'beit_base_patch16_224',
        'twins_pcpvt_base', 'twins_svt_base', 'cait_s24_224',
        'coat_lite_medium', 'levit_256', 'levit_384',
        'poolformer_m36', 'poolformer_m48',
        'xcit_small_12_p16_224', 'crossvit_base_240'
    ],
    'Hybrid': [
        'resnetv2_50x1_bit_distilled', 'convit_base',
        'pit_b_224', 'pit_s_224', 'cait_xxs24_224',
        'mixer_b16_224', 'mixer_l16_224',
        'convnext_base_in22k', 'twins_pcpvt_small',
        'visformer_small', 'tnt_s_patch16_224', 'maxvit_tiny_tf_224'
    ]
}

FEATURE_NAMES = ['bn_count', 'ln_count', 'gn_count', 'no_norm_flag', 'param_mass_ratio']


# From: docs/youra_research/h-m1/code/src/feature_extractor.py (ACTUAL CODE)
class StatisticalFeatureExtractor:
    def extract_features(self, state_dict: dict) -> dict:
        """
        Extract normalization counts and parameter-mass ratio.
        
        Returns:
            {
                'bn_count': int,
                'ln_count': int,
                'gn_count': int,
                'no_norm_flag': int,
                'param_mass_ratio': float
            }
        """
        ...
    
    def _compute_param_mass_ratio(self, state_dict: dict) -> float:
        """
        Compute R = conv_params / (conv_params + linear_params).
        
        Logic:
            - 4D tensors → conv weights
            - 2D tensors → linear weights
            - Exclude classification head keys
        """
        ...
```

**Verified from:** `docs/youra_research/h-m1/code/` (actual implementation)

**Note:** h-m2 DOES NOT re-extract features. Features are loaded from:
- `docs/youra_research/h-m1/code/data/train_features.csv`
- `docs/youra_research/h-m1/code/data/val_features.csv`

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
  "efficientnet_family": {
    "cv": 0.112,
    "mean_R": 0.845,
    "std_R": 0.095,
    "models": ["efficientnet_b0", "efficientnet_b4"],
    "passed": true
  },
  "vit_family": {
    "cv": 0.087,
    "mean_R": 0.034,
    "std_R": 0.003,
    "models": ["vit_tiny_patch16_224", "vit_small_patch16_224", "vit_base_patch16_224", "vit_large_patch16_224"],
    "passed": true
  },
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
  "hybrid_outlier_rate": 0.0,
  "known_edge_cases": {
    "vgg16": {"R": 0.995, "family": "CNN", "notes": "NormFree CNN"},
    "poolformer_m36": {"R": 0.012, "family": "Transformer", "notes": "MetaFormer"},
    "convnext_tiny": {"R": 0.678, "family": "CNN", "notes": "Modern CNN with LayerNorm"},
    "mixer_b16_224": {"R": 0.000, "family": "Hybrid", "notes": "MLP-Mixer"}
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

## Gate Conditions (MUST_WORK Logic)

### Primary Criteria

**P1: Cohen's d >1.0**
```python
cohens_d = (mean_cnn - mean_transformer) / pooled_std
P1_passed = (cohens_d > 1.0)
```

**P2: CV <0.15 (ResNet family)**
```python
cv = std_R / mean_R
P2_passed = (cv < 0.15)
```

### Gate Decision Tree

```
IF P1_passed AND P2_passed:
    gate_decision = 'PASS'
    recommendation = 'Proceed to H-M3'
ELSE:
    gate_decision = 'FAIL'
    IF NOT P1_passed:
        recommendation = 'EXPLORE alternative ratios (attention_params / total_params)'
    ELIF NOT P2_passed:
        recommendation = 'PIVOT to normalized R: (R - μ_family) / σ_family'
```

---

## Edge Case Handling

### Known Edge Cases

**VGG-16 (NormFree):**
- Expected: R ≈ 1.0 (purely convolutional, no normalization)
- Handling: Document in edge_cases.json, acceptable for CNN family

**PoolFormer (MetaFormer):**
- Expected: R < 0.2 (linear-dominant despite Transformer label)
- Handling: Expected behavior, validates hypothesis

**ConvNeXt (Modern CNN):**
- Expected: R > 0.6 (conv-dominant despite LayerNorm)
- Handling: Expected behavior, validates CNN allocation pattern

**MLP-Mixer (Hybrid):**
- Expected: R ≈ 0.0 (no conv layers except tokenization)
- Handling: Boundary case, acceptable for Hybrid family

---

## Error Handling

### ZeroDivisionError

```python
# In CohensDAnalyzer
if total_params == 0:
    pooled_std = 0.001  # Avoid division by zero

# In ScaleInvarianceValidator
if mean_R == 0:
    cv = float('inf')  # Flag as invalid
```

### KeyError

```python
# In H_M2_Runner
required_columns = ['model_name', 'family', 'param_mass_ratio']
missing = [col for col in required_columns if col not in features_df.columns]
if missing:
    raise KeyError(f"Missing required columns: {missing}")
```

### FileNotFoundError

```python
# In H_M2_Runner._load_h_m1_features
if not os.path.exists(f"{self.h_m1_dir}/code/data/train_features.csv"):
    raise FileNotFoundError("h-m1 features not found. Run h-m1 first.")
```

---

## Performance Requirements

### Runtime Budget

**Target:** ≤10 minutes (CPU-only)

**Breakdown:**
- Feature loading: <1 min (CSV read)
- Cohen's d computation: <1 min (NumPy operations)
- CV validation: <1 min (Pandas groupby)
- Distribution visualization: <2 min (Matplotlib rendering)
- Edge case detection: <1 min (threshold filtering)
- Report generation: <1 min (Markdown writing)
- **Total: ~5 minutes** (well below 10 min threshold)

### Memory Budget

**Target:** ≤8 GB peak RAM

**Profile:**
- h-m1 features: 50 models × 7 features × 8 bytes = 2.8 KB
- Statistical results: ~10 KB
- Matplotlib figures: ~5 MB
- **Peak RAM: <50 MB** (well below 8 GB threshold)

---

## Success Metrics

### Primary Success Criteria (MUST_WORK Gate)

| ID | Criterion | Metric | Threshold | Measurement |
|----|-----------|--------|-----------|-------------|
| P1 | Inter-Family Separation | Cohen's d | >1.0 | (μ_CNN - μ_Transformer) / σ_pooled |
| P2 | Scale Invariance | CV (ResNet) | <0.15 | σ / μ |

**Gate Decision:**
- **PASS:** P1 AND P2 meet thresholds → Proceed to H-M3
- **FAIL:** P1 OR P2 fails → Remediation

---

### Secondary Success Criteria

| ID | Criterion | Metric | Threshold | Measurement |
|----|-----------|--------|-----------|-------------|
| S1 | Statistical Significance | p-value | <0.05 | scipy.stats.ttest_ind |
| S2 | Distribution Separation | Mean separation | >0.4 | μ_CNN - μ_Transformer |
| S3 | Edge Case Robustness | Violation rate | ≤25% | violations / edge_case_models |

---

## Type Annotations

### Core Types

```python
from typing import Dict, List, Tuple, Optional
import pandas as pd
import numpy as np

# Cohen's d results
CohensDResults = Dict[str, Union[float, int, bool]]
# {
#     'cohens_d': float,
#     'p_value': float,
#     't_statistic': float,
#     'mean_cnn': float,
#     'mean_transformer': float,
#     'std_cnn': float,
#     'std_transformer': float,
#     'n_cnn': int,
#     'n_transformer': int,
#     'passed': bool
# }

# Scale invariance results
ScaleFamilyResults = Dict[str, Union[float, List[str], bool]]
# {
#     'cv': float,
#     'mean_R': float,
#     'std_R': float,
#     'models': List[str],
#     'passed': bool
# }

ScaleInvarianceResults = Dict[str, Union[ScaleFamilyResults, bool]]
# {
#     'resnet_family': ScaleFamilyResults,
#     'efficientnet_family': ScaleFamilyResults,
#     'vit_family': ScaleFamilyResults,
#     'overall_passed': bool
# }

# Edge case results
EdgeCaseResults = Dict[str, Union[List[str], float, Dict]]
# {
#     'cnn_low_R': List[str],
#     'transformer_high_R': List[str],
#     'hybrid_outliers': List[str],
#     'cnn_violation_rate': float,
#     'transformer_violation_rate': float,
#     'hybrid_outlier_rate': float,
#     'known_edge_cases': Dict[str, Dict[str, Union[float, str]]]
# }

# Gate decision
GateDecision = Dict[str, Union[str, bool]]
# {
#     'gate_decision': str,
#     'reasoning': str,
#     'failure_mode': Optional[str],
#     'p1_passed': bool,
#     'p2_passed': bool,
#     'recommendation': str
# }
```

---

## Document Metadata

**Version:** 1.0  
**Last Updated:** 2026-07-11  
**Status:** APPROVED for Phase 4 Implementation  
**Estimated Implementation Time:** 6 hours  
**Estimated Runtime:** 5 minutes  
**Code Reuse:** 70% data reuse (features), 30% code reuse (config)  
**New Code:** 6 modules, ~400 LOC  
**Total Complexity:** 71 (14 + 12 + 11 + 10 + 9 + 15)  
**Budget Used:** 71/11 subtasks (11 total budget from allocation)
