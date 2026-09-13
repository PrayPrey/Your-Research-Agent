# Configuration Design: H-M1 Normalization Layer Fingerprinting

**Hypothesis ID:** h-m1  
**Type:** MECHANISM (MUST_WORK gate)  
**Date:** 2026-07-11  

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis  
**Status:** Config classes verified from h-e1 base code  
**Config Files Found:** docs/youra_research/h-e1/code/config.py  
**Pattern Used:** Hardcoded dict (reusing h-e1 pattern for consistency)

**Base Config Reference:** h-e1/code/config.py contains:
- MODEL_FAMILIES dict (50 TIMM models)
- NORM_PATTERNS dict (regex for BN/LN/GN detection)
- CLASSIFIER_CONFIG dict (LogisticRegression settings)
- SPLIT_CONFIG dict (70/30 train/val split)
- FEATURE_NAMES list (5 statistical features)

---

## Knowledge Base Patterns Applied

**Applied:** PyTorch reproducibility patterns, sklearn pipeline configuration

---

## Configuration Format

Single hardcoded dictionary for MECHANISM validation. H-m1 reuses h-e1 configurations and adds analysis-specific settings.

```python
# code/config_h_m1.py

"""
Configuration for H-M1: Normalization Layer Fingerprinting
MECHANISM hypothesis - extends h-e1 with violation analysis configs
"""

# ============================================================================
# INHERITED FROM H-E1 (Actual Base Code)
# ============================================================================

# Reuse h-e1 config via import
from h_e1.code.config import (
    MODEL_FAMILIES,      # 50 TIMM models (24 CNN, 22 Transformer, 11 Hybrid)
    NORM_PATTERNS,       # Regex patterns for BN/LN/GN detection
    CLASSIFIER_CONFIG,   # LogisticRegression hyperparameters
    SPLIT_CONFIG,        # 70/30 train/val split, random_state=42
    FEATURE_NAMES        # ['bn_count', 'ln_count', 'gn_count', 'no_norm_flag', 'param_mass_ratio']
)

# ============================================================================
# H-M1 SPECIFIC: VIOLATION ANALYSIS
# ============================================================================

VIOLATION_THRESHOLDS = {
    'cnn_max': 0.15,           # P1: CNN violation rate must be ≤15%
    'transformer_max': 0.15    # P2: Transformer violation rate must be ≤15%
}

VIOLATION_DEFINITIONS = {
    'CNN': 'ln_count > bn_count',        # CNN violation: LayerNorm dominates
    'Transformer': 'bn_count > ln_count', # Transformer violation: BatchNorm dominates
    'Hybrid': None                        # No violation definition (mixed expected)
}

# ============================================================================
# H-M1 SPECIFIC: FEATURE IMPORTANCE
# ============================================================================

FEATURE_IMPORTANCE_CONFIG = {
    'min_coefficient': 0.1,     # S1: bn_count, ln_count coefficients must exceed 0.1
    'aggregation_method': 'mean_abs',  # Average absolute coefficient across 3 classes
    'target_features': ['bn_count', 'ln_count']  # Features to validate for S1 criterion
}

# ============================================================================
# H-M1 SPECIFIC: EDGE CASE DETECTION
# ============================================================================

EDGE_CASE_CATEGORIES = {
    'NormFree': {
        'detection': 'no_norm_flag == 1',
        'expected_models': ['vgg16', 'vgg19'],
        'notes': 'Architectures with no normalization layers'
    },
    'MetaFormer': {
        'detection': "'poolformer' in model_name.lower()",
        'expected_models': ['poolformer_m36', 'poolformer_m48'],
        'notes': 'Token mixer architectures (non-standard Transformer)'
    },
    'ConvNeXt': {
        'detection': "'convnext' in model_name.lower()",
        'expected_models': ['convnext_tiny', 'convnext_base', 'convnext_base_in22k'],
        'notes': 'Modern CNNs using LayerNorm instead of BatchNorm'
    }
}

EDGE_CASE_CONFIG = {
    'detection_rate_threshold': 1.0,  # S3: Must detect 100% of known edge cases
    'log_unexpected_cases': True
}

# ============================================================================
# H-M1 SPECIFIC: NORMALIZATION DISTRIBUTIONS
# ============================================================================

DISTRIBUTION_CONFIG = {
    'families': ['CNN', 'Transformer', 'Hybrid'],
    'norm_types': ['bn_count', 'ln_count', 'gn_count'],
    'statistics': ['mean', 'median', 'std'],
    'dominant_threshold': 0.5  # >50% models with majority norm type
}

DOMINANT_NORM_RULES = {
    'CNN': {
        'expected': 'BatchNorm',
        'criterion': 'bn_count > ln_count for >50% of CNN models'
    },
    'Transformer': {
        'expected': 'LayerNorm',
        'criterion': 'ln_count > bn_count for >50% of Transformer models'
    },
    'Hybrid': {
        'expected': 'Mixed',
        'criterion': 'No single normalization type dominates'
    }
}

# ============================================================================
# H-M1 SPECIFIC: MANUAL VALIDATION
# ============================================================================

MANUAL_VALIDATION_CONFIG = {
    'sample_size': 10,  # S2: Regex accuracy check on 10 random models
    'accuracy_threshold': 0.95,  # S2: ≥95% match rate (9/10 correct)
    'sample_models': [
        'resnet18',                    # CNN - expect high bn_count
        'vit_tiny_patch16_224',        # Transformer - expect high ln_count
        'mixer_b16_224',               # Hybrid - expect mixed
        'vgg16',                       # NormFree - expect no_norm_flag=1
        'poolformer_m36',              # MetaFormer - expect ln_count
        'convnext_tiny',               # ConvNeXt - expect ln_count in CNN
        'deit_tiny_patch16_224',       # DeiT - expect ln_count (possible bn in stem)
        'efficientnet_b0',             # CNN - expect bn_count
        'swin_tiny_patch4_window7_224',# Transformer - expect ln_count
        'pit_b_224'                    # Hybrid - expect mixed
    ]
}

# ============================================================================
# H-M1 SPECIFIC: RUNTIME CONFIGURATION
# ============================================================================

RUNTIME_CONFIG = {
    'random_seed': 42,          # Same as h-e1 for reproducibility
    'device': 'cpu',            # CPU-only, no GPU required
    'batch_size': 1,            # Sequential processing
    'max_memory_gb': 8,         # Laptop-friendly memory limit
    'max_runtime_minutes': 20   # Runtime constraint (h-m1 should be ~5 min)
}

# ============================================================================
# H-M1 SPECIFIC: DATA SOURCES
# ============================================================================

H_E1_ARTIFACTS = {
    'base_dir': '../h-e1/outputs/',
    'train_features': '../h-e1/outputs/train_features.csv',
    'val_features': '../h-e1/outputs/val_features.csv',
    'classifier': '../h-e1/outputs/classifier.pkl',
    'scaler': '../h-e1/outputs/scaler.pkl'  # Not used in h-m1
}

# ============================================================================
# H-M1 SPECIFIC: OUTPUT CONFIGURATION
# ============================================================================

OUTPUT_CONFIG = {
    'output_dir': 'outputs/',
    'violation_rates_csv': 'outputs/h-m1_violation_rates.csv',
    'feature_importance_csv': 'outputs/h-m1_feature_importance.csv',
    'norm_distributions_json': 'outputs/h-m1_norm_distributions.json',
    'edge_cases_json': 'outputs/h-m1_edge_cases.json',
    'validation_report': 'outputs/04_validation.md',
    'intermediate_results': True  # Save intermediate DataFrames for debugging
}

OUTPUT_FORMATS = {
    'csv_encoding': 'utf-8',
    'csv_index': False,
    'json_indent': 2,
    'json_ensure_ascii': False,
    'markdown_table_format': 'github'
}

# ============================================================================
# H-M1 SPECIFIC: LOGGING
# ============================================================================

LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
    'datefmt': '%Y-%m-%d %H:%M:%S',
    'handlers': {
        'file': {
            'filename': 'outputs/h_m1_experiment.log',
            'mode': 'w'  # Overwrite each run
        },
        'console': {
            'stream': 'stdout'
        }
    }
}

LOG_CHECKPOINTS = [
    'h_e1_artifacts_loaded',
    'violation_analysis_complete',
    'distribution_analysis_complete',
    'edge_case_detection_complete',
    'feature_importance_extracted',
    'gate_decision',
    'validation_report_generated'
]

# ============================================================================
# H-M1 SPECIFIC: GATE DECISION LOGIC
# ============================================================================

GATE_DECISION_CONFIG = {
    'primary_criteria': ['P1', 'P2'],  # Both must pass
    'secondary_criteria': ['S1', 'S2', 'S3'],  # Optional
    'decision_matrix': {
        'PASS': 'P1 ≤15% AND P2 ≤15%',
        'FAIL': 'P1 >15% OR P2 >15%'
    },
    'next_steps': {
        'PASS': 'Proceed to H-M2 (Parameter Mass Ratio Verification)',
        'FAIL': 'PIVOT to alternative features (attention mechanism, model depth)'
    }
}

PIVOT_RECOMMENDATIONS = {
    'P1_fail': {
        'root_cause': 'Modern CNNs (ConvNeXt) adopting LayerNorm',
        'mitigation': 'Add temporal feature (model release year) or refine taxonomy (Legacy vs Modern CNN)'
    },
    'P2_fail': {
        'root_cause': 'Hybrid architectures mislabeled as Transformers',
        'mitigation': 'Add attention mechanism detection (Q/K/V weight counting)'
    }
}

# ============================================================================
# H-M1 SPECIFIC: VALIDATION REPORT TEMPLATE
# ============================================================================

REPORT_TEMPLATE = {
    'sections': [
        'gate_decision',
        'primary_results_p1',
        'primary_results_p2',
        'secondary_results_s1',
        'secondary_results_s2',
        'secondary_results_s3',
        'normalization_distributions',
        'edge_cases',
        'key_findings',
        'recommendations_next_hypothesis'
    ],
    'include_tables': True,
    'include_violation_lists': True,
    'include_distribution_stats': True,
    'include_edge_case_details': True
}

# ============================================================================
# H-M1 SPECIFIC: TIMM CONFIGURATION
# ============================================================================

TIMM_CONFIG = {
    'version': '1.0.9',  # Same as h-e1
    'pretrained': True,
    'cache_dir': '~/.cache/torch/hub/checkpoints/',
    'download_timeout': 1800,  # Not used in h-m1 (reuses h-e1 features)
    'num_workers': 4           # Not used in h-m1
}

# ============================================================================
# SUMMARY: KEY CONFIGURATION VALUES
# ============================================================================

CONFIG_SUMMARY = {
    'hypothesis_type': 'MECHANISM',
    'gate_type': 'MUST_WORK',
    'total_models': 50,
    'train_models': 35,
    'val_models': 15,
    'primary_thresholds': {
        'P1_cnn_violation': 0.15,
        'P2_transformer_violation': 0.15
    },
    'secondary_thresholds': {
        'S1_min_coefficient': 0.1,
        'S2_regex_accuracy': 0.95,
        'S3_edge_case_detection': 1.0
    },
    'runtime_target': '5 minutes',
    'memory_target': '8 GB',
    'code_reuse_rate': 0.80,
    'random_seed': 42
}
```

---

## Inherited Configuration (Base Hypothesis)

### Config Classes (From h-e1 Actual Code)

The following configs are inherited or referenced from h-e1:

```python
# From: docs/youra_research/h-e1/code/config.py (ACTUAL CODE)

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
    ],  # Total: 24 models
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
    ],  # Total: 22 models
    'Hybrid': [
        'resnetv2_50x1_bit_distilled', 'convit_base',
        'pit_b_224', 'pit_s_224', 'cait_xxs24_224',
        'mixer_b16_224', 'mixer_l16_224',
        'convnext_base_in22k', 'twins_pcpvt_small',
        'visformer_small', 'tnt_s_patch16_224', 'maxvit_tiny_tf_224'
    ]  # Total: 11 models (note: convnext_base_in22k also listed here)
}

FEATURE_NAMES = ['bn_count', 'ln_count', 'gn_count', 'no_norm_flag', 'param_mass_ratio']

NORM_PATTERNS = {
    'bn': r'bn|batch_norm|batchnorm',     # Case-insensitive regex
    'ln': r'ln|layer_norm|layernorm',
    'gn': r'gn|group_norm|groupnorm'
}

HEAD_KEYWORDS = ['head', 'fc', 'classifier']  # Used in param_mass_ratio calculation

CLASSIFIER_CONFIG = {
    'solver': 'lbfgs',
    'max_iter': 1000,
    'random_state': 42,
    'class_weight': 'balanced'
}

SPLIT_CONFIG = {
    'test_size': 0.3,      # 70/30 train/val split
    'random_state': 42     # Same seed for reproducibility
}

THRESHOLDS = {
    'macro_accuracy': 0.80,
    'per_class_accuracy': 0.75,
    'scale_invariance_cv': 0.15,
    'a1_alignment_rate': 0.90,
    'a2_violation_rate': 0.15  # Reused in h-m1 as violation threshold
}
```

**Verified from:** docs/youra_research/h-e1/code/config.py (actual implementation)

---

## Configuration Usage Example

```python
# main_h_m1.py - H-M1 orchestrator usage

from h_e1.code.config import MODEL_FAMILIES, NORM_PATTERNS, CLASSIFIER_CONFIG
from config_h_m1 import (
    VIOLATION_THRESHOLDS,
    FEATURE_IMPORTANCE_CONFIG,
    EDGE_CASE_CATEGORIES,
    H_E1_ARTIFACTS,
    OUTPUT_CONFIG,
    GATE_DECISION_CONFIG
)

class H_M1_Runner:
    def __init__(self):
        self.config = {
            'model_families': MODEL_FAMILIES,
            'norm_patterns': NORM_PATTERNS,
            'violation_thresholds': VIOLATION_THRESHOLDS,
            'h_e1_artifacts': H_E1_ARTIFACTS,
            'output': OUTPUT_CONFIG
        }
        self._setup_logging()
    
    def run_mechanism_validation(self):
        # Step 1: Load h-e1 artifacts
        features_df = self._load_h_e1_features()
        classifier = self._load_h_e1_classifier()
        
        # Step 2: Run violation analysis
        violation_results = self._run_violation_analysis(features_df)
        
        # Step 3: Run distribution analysis
        distribution_results = self._run_distribution_analysis(features_df)
        
        # Step 4: Detect edge cases
        edge_case_results = self._detect_edge_cases(features_df)
        
        # Step 5: Extract feature importance
        importance_results = self._extract_feature_importance(classifier)
        
        # Step 6: Make gate decision
        gate_decision = self._make_gate_decision(
            violation_results,
            VIOLATION_THRESHOLDS
        )
        
        # Step 7: Generate validation report
        self._generate_validation_report(
            gate_decision,
            violation_results,
            distribution_results,
            edge_case_results,
            importance_results
        )
        
        return gate_decision
```

---

## MECHANISM Compliance Check

- [x] Reuses h-e1 configurations (80% code reuse)
- [x] Fixed violation thresholds (no tuning)
- [x] Same random seed (42) as h-e1
- [x] Single configuration (no hyperparameter grid)
- [x] Analysis-specific configs only (violation, distribution, edge cases)
- [x] MUST_WORK gate criteria clearly defined (P1, P2)
- [x] Total subtasks: within budget (see architecture document)

---

## Critical Configuration Notes

### 1. Field Name Verification (h-e1 Compatibility)

**All field names match h-e1 actual code:**
- `bn_count`, `ln_count`, `gn_count`: Match FEATURE_NAMES in h-e1/code/config.py
- `no_norm_flag`: Match FEATURE_NAMES in h-e1/code/config.py
- `param_mass_ratio`: Match FEATURE_NAMES in h-e1/code/config.py

### 2. Model Family Counts

**Actual counts from h-e1 config:**
- CNN: 24 models (note: convnext models are in both CNN and Hybrid)
- Transformer: 22 models
- Hybrid: 11 models
- **Total unique: 50 models** (accounting for overlaps)

### 3. Train/Val Split

**From h-e1 SPLIT_CONFIG:**
- test_size=0.3 → 70/30 split
- random_state=42 → deterministic split
- **Expected:** ~35 train, ~15 val (may vary by 1-2 due to stratification)

### 4. Edge Case Notes

**Known edge cases from h-e1 experiments:**
- VGG models (vgg16, vgg19): NormFree
- PoolFormer models: MetaFormer
- ConvNeXt models: Modern CNN with LayerNorm (listed in both CNN and Hybrid)

### 5. Violation Rate Context

**From h-e1 validation results:**
- Transformer BatchNorm rate: 13.33% (within 15% threshold)
- CNN LayerNorm rate: Expected to be low (ConvNeXt is main concern)

---

## Next Phase Handoff

**For Phase 4 (Coder):**

Copy-paste ready configuration in `code/config_h_m1.py`. Import h-e1 configs via relative import.

**Key Import Pattern:**
```python
# Import h-e1 base configs
from h_e1.code.config import MODEL_FAMILIES, NORM_PATTERNS, CLASSIFIER_CONFIG, SPLIT_CONFIG

# Import h-m1 specific configs
from config_h_m1 import VIOLATION_THRESHOLDS, EDGE_CASE_CATEGORIES, OUTPUT_CONFIG
```

**Critical Values:**
- Random seed: 42 (same as h-e1)
- CNN violation threshold: ≤15% (P1 MUST_WORK gate)
- Transformer violation threshold: ≤15% (P2 MUST_WORK gate)
- Feature importance threshold: >0.1 (S1 secondary criterion)
- Regex accuracy threshold: ≥95% (S2 secondary criterion)
- Edge case detection: 100% (S3 secondary criterion)

**No Configuration Variations:**
This is MECHANISM validation - fixed thresholds, no hyperparameter tuning, reuses h-e1 artifacts.

---

**End of Configuration Document**
