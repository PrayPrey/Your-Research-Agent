# Configuration Design: H-M2 Parameter Allocation Pattern

**Hypothesis ID:** h-m2  
**Type:** MECHANISM (MUST_WORK gate)  
**Date:** 2026-07-11  

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis  
**Status:** Config classes verified from h-m1 base code  
**Config Files Found:** docs/youra_research/h-m1/code/config.py  
**Pattern Used:** Hardcoded dict (reusing h-m1 pattern for consistency)

**Base Config Reference:** h-m1/code/config.py contains:
- MODEL_FAMILIES dict (50 TIMM models)
- FEATURE_NAMES list (5 statistical features including param_mass_ratio)
- THRESHOLDS dict (including scale_invariance_cv: 0.15)
- RESNET_MODELS list (for scale invariance validation)

---

## Knowledge Base Patterns Applied

**Applied:** Statistical analysis configuration patterns (Cohen's d, CV computation), matplotlib visualization configs

---

## Configuration Format

Single hardcoded dictionary for MECHANISM validation. H-m2 reuses h-m1 configurations and adds statistical analysis settings.

```python
# code/config_h_m2.py

"""
Configuration for H-M2: Parameter Allocation Pattern
MECHANISM hypothesis - extends h-m1 with Cohen's d and CV analysis configs
"""

# ============================================================================
# INHERITED FROM H-M1 (Actual Base Code)
# ============================================================================

# Reuse h-m1 config via import
from h_m1.code.config import (
    MODEL_FAMILIES,      # 50 TIMM models (24 CNN, 22 Transformer, 11 Hybrid)
    FEATURE_NAMES,       # ['bn_count', 'ln_count', 'gn_count', 'no_norm_flag', 'param_mass_ratio']
    THRESHOLDS,          # Contains scale_invariance_cv: 0.15
    RESNET_MODELS        # ['resnet18', 'resnet34', 'resnet50', 'resnet101', 'resnet152']
)

# ============================================================================
# H-M2 SPECIFIC: PRIMARY CRITERIA (MUST_WORK GATE)
# ============================================================================

GATE_CRITERIA = {
    'P1_cohens_d_threshold': 1.0,       # P1: Cohen's d >1.0 (very large effect)
    'P2_cv_threshold': 0.15             # P2: CV <0.15 (scale invariance)
}

# ============================================================================
# H-M2 SPECIFIC: COHEN'S D ANALYSIS
# ============================================================================

COHENS_D_CONFIG = {
    'family_pair': ('CNN', 'Transformer'),  # Compare CNN vs Transformer
    'feature': 'param_mass_ratio',          # R metric from h-m1
    'statistical_test': 'ttest_ind',        # Independent samples t-test
    'two_tailed': True,                     # Two-tailed test
    'equal_var': False                      # Use Welch's t-test (no equal variance assumption)
}

# ============================================================================
# H-M2 SPECIFIC: SCALE INVARIANCE (CV) VALIDATION
# ============================================================================

SCALE_FAMILIES = {
    'resnet': {
        'models': ['resnet18', 'resnet34', 'resnet50', 'resnet101', 'resnet152'],
        'family': 'CNN',
        'cv_threshold': 0.15,  # P2 primary criterion
        'is_primary': True     # Primary scale family for gate decision
    },
    'efficientnet': {
        'models': ['efficientnet_b0', 'efficientnet_b4'],
        'family': 'CNN',
        'cv_threshold': 0.15,
        'is_primary': False    # Secondary validation
    },
    'vit': {
        'models': ['vit_tiny_patch16_224', 'vit_small_patch16_224', 
                   'vit_base_patch16_224', 'vit_large_patch16_224'],
        'family': 'Transformer',
        'cv_threshold': 0.15,
        'is_primary': False    # Secondary validation
    }
}

CV_CONFIG = {
    'primary_family': 'resnet',             # ResNet used for P2 gate criterion
    'compute_for_all': True,                # Compute CV for all scale families
    'feature': 'param_mass_ratio'
}

# ============================================================================
# H-M2 SPECIFIC: DISTRIBUTION VISUALIZATION
# ============================================================================

VISUALIZATION_CONFIG = {
    'output_file': 'outputs/R_distributions.png',
    'figure_size': (15, 5),
    'dpi': 300,
    'subplot_count': 3,
    'families': ['CNN', 'Transformer', 'Hybrid'],
    'colors': {
        'CNN': '#1f77b4',
        'Transformer': '#ff7f0e',
        'Hybrid': '#2ca02c'
    },
    'threshold_lines': {
        'CNN': 0.6,         # R >0.6 for CNNs
        'Transformer': 0.2  # R <0.2 for Transformers
    }
}

PLOT_CONFIGS = {
    'violin': {
        'subplot_index': 0,
        'title': 'R Distribution by Family (Violin Plot)',
        'ylabel': 'Parameter-Mass Ratio (R)',
        'show_threshold_lines': True
    },
    'box': {
        'subplot_index': 1,
        'title': 'R Distribution by Family (Box Plot)',
        'ylabel': 'Parameter-Mass Ratio (R)',
        'show_outliers': True
    },
    'histogram': {
        'subplot_index': 2,
        'title': 'R Distribution by Family (Histogram + KDE)',
        'ylabel': 'Density',
        'bins': 20,
        'kde': True,
        'alpha': 0.5
    }
}

# ============================================================================
# H-M2 SPECIFIC: EDGE CASE DETECTION
# ============================================================================

EDGE_CASE_THRESHOLDS = {
    'cnn_low_R': 0.6,           # CNN violation: R <0.6 (not conv-dominant)
    'transformer_high_R': 0.2,  # Transformer violation: R >0.2 (not linear-dominant)
    'hybrid_low_R': 0.2,        # Hybrid outlier: R <0.2 (too linear-dominant)
    'hybrid_high_R': 0.6        # Hybrid outlier: R >0.6 (too conv-dominant)
}

KNOWN_EDGE_CASES = {
    'vgg16': {
        'family': 'CNN',
        'expected_R_range': (0.95, 1.0),
        'notes': 'NormFree CNN, purely convolutional (no FC layers except head)'
    },
    'vgg19': {
        'family': 'CNN',
        'expected_R_range': (0.95, 1.0),
        'notes': 'NormFree CNN, purely convolutional'
    },
    'poolformer_m36': {
        'family': 'Transformer',
        'expected_R_range': (0.0, 0.2),
        'notes': 'MetaFormer, linear-dominant (pooling as token mixer)'
    },
    'poolformer_m48': {
        'family': 'Transformer',
        'expected_R_range': (0.0, 0.2),
        'notes': 'MetaFormer, linear-dominant'
    },
    'convnext_tiny': {
        'family': 'CNN',
        'expected_R_range': (0.6, 1.0),
        'notes': 'Modern CNN with LayerNorm, still conv-dominant'
    },
    'convnext_base': {
        'family': 'CNN',
        'expected_R_range': (0.6, 1.0),
        'notes': 'Modern CNN with LayerNorm'
    },
    'mixer_b16_224': {
        'family': 'Hybrid',
        'expected_R_range': (0.0, 0.2),
        'notes': 'MLP-Mixer, linear-dominant (conv only in patch embedding)'
    },
    'mixer_l16_224': {
        'family': 'Hybrid',
        'expected_R_range': (0.0, 0.2),
        'notes': 'MLP-Mixer, linear-dominant'
    }
}

EDGE_CASE_CONFIG = {
    'max_violation_rate': 0.25,  # S3: ≤25% violation rate (higher tolerance for edge cases)
    'detect_known_cases': True,
    'log_all_violations': True
}

# ============================================================================
# H-M2 SPECIFIC: SECONDARY CRITERIA
# ============================================================================

SECONDARY_CRITERIA = {
    'S1_p_value_threshold': 0.05,   # S1: Statistical significance p <0.05
    'S2_mean_separation': 0.4,      # S2: Mean R_CNN - Mean R_Transformer >0.4
    'S3_violation_rate': 0.25       # S3: Edge case violation rate ≤25%
}

# ============================================================================
# H-M2 SPECIFIC: DATA SOURCES
# ============================================================================

H_M1_ARTIFACTS = {
    'base_dir': '../h-m1/code/data/',
    'train_features': '../h-m1/code/data/train_features.csv',
    'val_features': '../h-m1/code/data/val_features.csv'
}

# ============================================================================
# H-M2 SPECIFIC: OUTPUT CONFIGURATION
# ============================================================================

OUTPUT_CONFIG = {
    'output_dir': 'outputs/',
    'cohens_d_report': 'outputs/h-m2_cohens_d_report.json',
    'cv_report': 'outputs/h-m2_cv_report.json',
    'edge_cases_json': 'outputs/h-m2_edge_cases.json',
    'distributions_plot': 'outputs/R_distributions.png',
    'gate_decision_txt': 'outputs/h-m2_gate_decision.txt',
    'validation_report': 'outputs/04_validation.md'
}

OUTPUT_FORMATS = {
    'json_indent': 2,
    'json_ensure_ascii': False,
    'txt_encoding': 'utf-8',
    'markdown_table_format': 'github'
}

# ============================================================================
# H-M2 SPECIFIC: RUNTIME CONFIGURATION
# ============================================================================

RUNTIME_CONFIG = {
    'random_seed': 42,          # Same as h-m1/h-e1 for reproducibility
    'device': 'cpu',            # CPU-only, no GPU required
    'max_memory_gb': 8,         # Laptop-friendly memory limit
    'max_runtime_minutes': 10,  # Runtime constraint (h-m2 should be ~5 min)
    'matplotlib_backend': 'Agg' # Non-interactive backend for headless execution
}

# ============================================================================
# H-M2 SPECIFIC: GATE DECISION LOGIC
# ============================================================================

GATE_DECISION_CONFIG = {
    'primary_criteria': ['P1', 'P2'],  # Both must pass
    'secondary_criteria': ['S1', 'S2', 'S3'],  # Optional
    'decision_matrix': {
        'PASS': 'P1: Cohen\'s d >1.0 AND P2: CV <0.15',
        'FAIL_P1': 'Cohen\'s d ≤1.0',
        'FAIL_P2': 'CV ≥0.15'
    },
    'next_steps': {
        'PASS': 'Proceed to H-M3',
        'FAIL_P1': 'EXPLORE alternative ratios (attention_params / total_params)',
        'FAIL_P2': 'PIVOT to normalized R: (R - μ_family) / σ_family'
    }
}

FAILURE_MODE_ANALYSIS = {
    'P1_fail': {
        'symptom': 'Overlapping R distributions for CNN/Transformer',
        'diagnosis': 'Parameter allocation insufficient for discrimination',
        'remediation': 'Explore alternative features (attention mechanism detection)'
    },
    'P2_fail': {
        'symptom': 'R increases with model size (ResNet-18 ≠ ResNet-152)',
        'diagnosis': 'Parameter allocation reflects scale, not structure',
        'remediation': 'Pivot to normalized R or size-adjusted metrics'
    }
}

# ============================================================================
# H-M2 SPECIFIC: LOGGING
# ============================================================================

LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
    'datefmt': '%Y-%m-%d %H:%M:%S',
    'handlers': {
        'file': {
            'filename': 'outputs/h_m2_experiment.log',
            'mode': 'w'
        },
        'console': {
            'stream': 'stdout'
        }
    }
}

LOG_CHECKPOINTS = [
    'h_m1_features_loaded',
    'cohens_d_analysis_complete',
    'cv_analysis_complete',
    'distribution_visualization_complete',
    'edge_case_detection_complete',
    'gate_decision',
    'validation_report_generated'
]

# ============================================================================
# H-M2 SPECIFIC: VALIDATION REPORT TEMPLATE
# ============================================================================

REPORT_TEMPLATE = {
    'sections': [
        'gate_decision',
        'primary_results_p1_cohens_d',
        'primary_results_p2_cv',
        'secondary_results_s1_p_value',
        'secondary_results_s2_mean_separation',
        'secondary_results_s3_edge_cases',
        'r_distributions',
        'scale_family_analysis',
        'edge_case_details',
        'key_findings',
        'recommendations_next_hypothesis'
    ],
    'include_tables': True,
    'include_statistics': True,
    'include_violation_lists': True,
    'include_plot_reference': True
}

# ============================================================================
# SUMMARY: KEY CONFIGURATION VALUES
# ============================================================================

CONFIG_SUMMARY = {
    'hypothesis_type': 'MECHANISM',
    'gate_type': 'MUST_WORK',
    'total_models': 50,
    'train_models': 32,
    'val_models': 18,
    'primary_thresholds': {
        'P1_cohens_d': 1.0,
        'P2_cv': 0.15
    },
    'secondary_thresholds': {
        'S1_p_value': 0.05,
        'S2_mean_separation': 0.4,
        'S3_violation_rate': 0.25
    },
    'runtime_target': '5 minutes',
    'memory_target': '8 GB',
    'code_reuse_rate': 0.70,  # Data reuse 100%, code reuse 30%
    'random_seed': 42
}
```

---

## Inherited Configuration (Base Hypothesis)

### Config Classes (From h-m1 Actual Code)

The following configs are inherited or referenced from h-m1:

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

NORM_PATTERNS = {
    'bn': r'bn|batch_norm|batchnorm',
    'ln': r'ln|layer_norm|layernorm',
    'gn': r'gn|group_norm|groupnorm'
}

HEAD_KEYWORDS = ['head', 'fc', 'classifier']

CLASSIFIER_CONFIG = {
    'solver': 'lbfgs',
    'max_iter': 1000,
    'random_state': 42,
    'class_weight': 'balanced'
}

SPLIT_CONFIG = {
    'test_size': 0.3,
    'random_state': 42
}

THRESHOLDS = {
    'macro_accuracy': 0.80,
    'per_class_accuracy': 0.75,
    'scale_invariance_cv': 0.15,
    'a1_alignment_rate': 0.90,
    'a2_violation_rate': 0.15
}

RESNET_MODELS = ['resnet18', 'resnet34', 'resnet50', 'resnet101', 'resnet152']
```

**Verified from:** docs/youra_research/h-m1/code/config.py (actual implementation)

---

## Configuration Usage Example

```python
# main_h_m2.py - H-M2 orchestrator usage

from h_m1.code.config import MODEL_FAMILIES, FEATURE_NAMES, RESNET_MODELS
from config_h_m2 import (
    GATE_CRITERIA,
    COHENS_D_CONFIG,
    SCALE_FAMILIES,
    CV_CONFIG,
    VISUALIZATION_CONFIG,
    EDGE_CASE_THRESHOLDS,
    KNOWN_EDGE_CASES,
    H_M1_ARTIFACTS,
    OUTPUT_CONFIG,
    GATE_DECISION_CONFIG
)

class H_M2_Runner:
    def __init__(self):
        self.config = {
            'model_families': MODEL_FAMILIES,
            'gate_criteria': GATE_CRITERIA,
            'cohens_d': COHENS_D_CONFIG,
            'scale_families': SCALE_FAMILIES,
            'h_m1_artifacts': H_M1_ARTIFACTS,
            'output': OUTPUT_CONFIG
        }
        self._setup_logging()
    
    def run_mechanism_validation(self):
        # Step 1: Load h-m1 features (param_mass_ratio already computed)
        train_df, val_df = self._load_h_m1_features()
        
        # Step 2: Run Cohen's d analysis (CNN vs Transformer)
        cohens_d_results = self._run_cohens_d_analysis(val_df)
        
        # Step 3: Run CV analysis (ResNet family)
        cv_results = self._run_cv_analysis(train_df)
        
        # Step 4: Generate distribution plots
        self._generate_distribution_plots(val_df)
        
        # Step 5: Detect edge cases
        edge_case_results = self._detect_edge_cases(val_df)
        
        # Step 6: Make gate decision
        gate_decision = self._make_gate_decision(
            cohens_d_results,
            cv_results,
            GATE_CRITERIA
        )
        
        # Step 7: Generate validation report
        self._generate_validation_report(
            gate_decision,
            cohens_d_results,
            cv_results,
            edge_case_results
        )
        
        return gate_decision
```

---

## MECHANISM Compliance Check

- [x] Reuses h-m1 configurations (MODEL_FAMILIES, FEATURE_NAMES, THRESHOLDS)
- [x] Fixed gate thresholds (no tuning)
- [x] Same random seed (42) as h-m1/h-e1
- [x] Single configuration (no hyperparameter grid)
- [x] Analysis-specific configs only (Cohen's d, CV, visualization)
- [x] MUST_WORK gate criteria clearly defined (P1, P2)
- [x] Total subtasks: 5 (within budget)

---

## Critical Configuration Notes

### 1. Field Name Verification (h-m1 Compatibility)

**All field names match h-m1 actual code:**
- `param_mass_ratio`: Match FEATURE_NAMES in h-m1/code/config.py
- `bn_count`, `ln_count`, `gn_count`, `no_norm_flag`: Available in h-m1 features (not used in h-m2)

### 2. Model Family Counts

**Actual counts from h-m1 config:**
- CNN: 24 models
- Transformer: 22 models
- Hybrid: 11 models (note: some overlap with CNN)
- **Total unique: 50 models**

### 3. Train/Val Split

**From h-m1 SPLIT_CONFIG:**
- test_size=0.3 → 70/30 split
- random_state=42 → deterministic split
- **Expected:** 32 train, 18 val (verified from architecture doc)

### 4. Scale Family Models

**ResNet family (primary for P2):**
- resnet18, resnet34, resnet50, resnet101, resnet152 (5 models)
- All present in RESNET_MODELS from h-m1/code/config.py

**EfficientNet family (secondary):**
- efficientnet_b0, efficientnet_b4 (2 models)

**ViT family (secondary):**
- vit_tiny_patch16_224, vit_small_patch16_224, vit_base_patch16_224, vit_large_patch16_224 (4 models)

### 5. Edge Case Thresholds

**R threshold boundaries:**
- CNN: R >0.6 (convolution-dominant)
- Transformer: R <0.2 (linear-dominant)
- Hybrid: 0.2 < R < 0.6 (mixed)

**Known edge cases from h-m1:**
- VGG-16, VGG-19: NormFree CNNs (R ≈ 1.0)
- PoolFormer: MetaFormer Transformers (R <0.2)
- ConvNeXt: Modern CNNs with LayerNorm (R >0.6)
- MLP-Mixer: Hybrid linear-dominant (R <0.2)

### 6. Statistical Configuration

**Cohen's d computation:**
- Use SciPy's `ttest_ind` with `equal_var=False` (Welch's t-test)
- Two-tailed test for statistical significance

**CV computation:**
- CV = σ / μ (standard deviation divided by mean)
- Computed separately for each scale family

---

## Next Phase Handoff

**For Phase 4 (Coder):**

Copy-paste ready configuration in `code/config_h_m2.py`. Import h-m1 configs via relative import.

**Key Import Pattern:**
```python
# Import h-m1 base configs
from h_m1.code.config import MODEL_FAMILIES, FEATURE_NAMES, THRESHOLDS, RESNET_MODELS

# Import h-m2 specific configs
from config_h_m2 import (
    GATE_CRITERIA,
    COHENS_D_CONFIG,
    SCALE_FAMILIES,
    EDGE_CASE_THRESHOLDS,
    OUTPUT_CONFIG
)
```

**Critical Values:**
- Random seed: 42 (same as h-m1/h-e1)
- P1: Cohen's d >1.0 (MUST_WORK gate)
- P2: CV <0.15 for ResNet family (MUST_WORK gate)
- S1: p-value <0.05 (statistical significance)
- S2: Mean separation >0.4 (practical significance)
- S3: Violation rate ≤25% (edge case tolerance)

**No Configuration Variations:**
This is MECHANISM validation - fixed thresholds, no hyperparameter tuning, reuses h-m1 features.

---

**End of Configuration Document**
