# Configuration: H-C1 Edge Case Robustness Validation

**Hypothesis:** h-c1 (CONDITION - SHOULD_WORK)  
**Date:** 2026-07-11  
**Prerequisites:** h-m3 (extractor), h-e1 (classifier)

---

## Codebase Analysis (Serena)

**Project Type:** Existing codebase with base hypothesis  
**Status:** Config patterns verified from h-m3 and h-e1  
**Config Files Found:**
- `docs/youra_research/h-m3/code/config_h_m3.py`
- `docs/youra_research/h-e1/code/config.py`
- `docs/youra_research/h-e1/code/models/classifier.pkl` (verified)

**Pattern Used:** Python hardcoded dict (per PRD requirements for external parameter modification)

**Applied:** Standard PyTorch ML experiment config pattern with hardcoded dictionaries.

---

## Configuration

```python
"""
Configuration for H-C1: Edge Case Robustness Validation
CONDITION hypothesis - tests edge case architectures with fallback heuristics
"""

import os

# ============================================================================
# EDGE CASE MODEL FAMILIES (20 models across 4 families)
# ============================================================================

EDGE_CASE_MODELS = {
    'NormFree': [
        'nfnet_f0',
        'nfnet_f1',
        'dm_nfnet_f0',
        'nfnet_f2',
        'nfnet_f3'
    ],
    'SENet': [
        'seresnet50',
        'senet154',
        'legacy_seresnet50',
        'seresnet101',
        'seresnet152'
    ],
    'RegNet': [
        'regnetx_032',
        'regnety_032',
        'regnetx_160',
        'regnety_160',
        'regnetx_320'
    ],
    'ViT-Extreme': [
        'vit_giant_patch14_224',
        'vit_huge_patch14_224',
        'vit_large_patch32_224',
        'deit_huge_patch14_224',
        'beit_large_patch16_224'
    ]
}

# Fallback models if primary models unavailable
FALLBACK_MODELS = {
    'NormFree': ['eca_nfnet_l0', 'nf_regnet_b0', 'nf_resnet50'],
    'SENet': ['seresnext50_32x4d', 'seresnext101_32x4d'],
    'RegNet': ['regnety_040', 'regnetx_040'],
    'ViT-Extreme': ['vit_base_patch16_384', 'deit_base_patch16_384']
}

# Minimum viable sample size (if primary models fail)
MIN_MODELS_PER_FAMILY = 3

# ============================================================================
# INHERITED FROM H-M3/H-E1 (Actual Base Code)
# ============================================================================

FEATURE_NAMES = ['bn_count', 'ln_count', 'gn_count', 'no_norm_flag', 'param_mass_ratio']

NORM_PATTERNS = {
    'bn': r'bn|batch_norm|batchnorm',
    'ln': r'ln|layer_norm|layernorm',
    'gn': r'gn|group_norm|groupnorm'
}

HEAD_KEYWORDS = ['head', 'fc', 'classifier']

# ============================================================================
# GATE CRITERIA (SHOULD_WORK)
# ============================================================================

GATE_CRITERIA = {
    'P1_overall_accuracy_min': 0.70,        # P1: Overall edge case accuracy ≥70%
    'P2_passing_families_min': 3,           # P2: At least 3/4 families pass 70%
    'degradation_max': 0.15                 # Acceptable: ≤15% degradation from baseline
}

# ============================================================================
# ACCURACY THRESHOLDS
# ============================================================================

ACCURACY_THRESHOLDS = {
    'per_family_min': 0.70,                 # Per-family accuracy threshold
    'baseline_expected': 0.85,              # h-e1 baseline accuracy (standard models)
    'edge_case_target': 0.70,               # Edge case target (15% degradation)
    'ci_method': 'wilson',                  # Wilson score for exact binomial CI
    'confidence_level': 0.95,               # 95% confidence intervals
    'ci_width_max': 0.10                    # Flag if CI width >±10%
}

# ============================================================================
# EVALUATION PARAMETERS
# ============================================================================

EVALUATION_CONFIG = {
    'confidence_interval_method': 'wilson',     # Wilson score method (exact binomial)
    'confidence_level': 0.95,                   # 95% confidence level
    'metrics': [
        'overall_accuracy',
        'per_family_accuracy',
        'degradation',
        'confusion_matrix',
        'feature_importance'
    ],
    'per_family_breakdown': True,
    'log_misclassifications': True
}

# Statistical power validation
STATISTICAL_CONFIG = {
    'min_sample_size': 12,                  # Minimum viable (3 per family)
    'target_sample_size': 20,               # Target (5 per family)
    'expanded_sample_size': 28,             # Fallback if CI too wide (7 per family)
    'max_ci_width': 0.10,                   # Maximum acceptable CI width (±10%)
    'report_ci': True
}

# ============================================================================
# FILE PATHS
# ============================================================================

PATHS = {
    # Input: h-m3 extractor (code reuse)
    'h_m3_extractor_dir': '../h-m3/code/src',
    'h_m3_config': '../h-m3/code/config_h_m3.py',
    
    # Input: h-e1 trained classifier
    'h_e1_classifier': '../h-e1/code/models/classifier.pkl',
    'h_e1_scaler': '../h-e1/code/models/scaler.pkl',
    'h_e1_features': '../h-e1/code/data/train_features.csv',
    
    # Checkpoint cache (reuse h-m3 infrastructure)
    'cache_dir': '.cache/checkpoints',
    
    # Output directories
    'output_dir': 'results/',
    'plots_dir': 'results/plots/',
    'logs_dir': 'results/logs/'
}

# ============================================================================
# CHECKPOINT LOADING (Reuse h-m3 config)
# ============================================================================

CHECKPOINT_CONFIG = {
    'weights_only': True,
    'map_location': 'cpu',
    'cache_dir': '.cache/checkpoints',
    'download_retry': 3,
    'download_timeout': 300,
    'skip_failed_models': True,
    'max_failed_rate': 0.20                 # Allow 20% failure for edge cases
}

# ============================================================================
# VISUALIZATION SETTINGS
# ============================================================================

VISUALIZATION_CONFIG = {
    # Confusion matrix
    'confusion_matrix': {
        'figsize': (10, 8),
        'dpi': 300,
        'cmap': 'Blues',
        'annot': True,
        'fmt': 'd',
        'title': 'Edge Case Confusion Matrix',
        'save_format': 'png'
    },
    
    # Feature distributions
    'feature_distributions': {
        'figsize': (14, 10),
        'dpi': 300,
        'plot_type': 'violin',              # Violin plot for distributions
        'colors': {
            'edge_case': '#ff7f0e',         # Orange
            'baseline': '#1f77b4'           # Blue
        },
        'title': 'Feature Distributions: Edge Cases vs Baseline',
        'save_format': 'png'
    },
    
    # Per-family accuracy bar chart
    'accuracy_breakdown': {
        'figsize': (12, 6),
        'dpi': 300,
        'bar_width': 0.6,
        'threshold_line': 0.70,             # Show 70% threshold line
        'colors': {
            'pass': '#2ca02c',              # Green
            'fail': '#d62728'               # Red
        },
        'title': 'Per-Family Accuracy: Edge Cases',
        'save_format': 'png'
    }
}

# ============================================================================
# FALLBACK CONFIGURATIONS
# ============================================================================

FALLBACK_CONFIG = {
    # Model availability fallback
    'pre_validate_availability': True,
    'min_models_per_family': 3,
    'substitute_similar_models': True,
    'log_substitutions': True,
    
    # Classifier fallback (if h-e1 file missing)
    'train_fallback_classifier': True,
    'fallback_classifier_config': {
        'solver': 'lbfgs',
        'max_iter': 1000,
        'random_state': 42,
        'class_weight': 'balanced'
    },
    
    # Statistical power fallback
    'expand_sample_if_needed': True,
    'target_ci_width': 0.10
}

# ============================================================================
# OUTPUT FILES
# ============================================================================

OUTPUT_FILES = {
    # Feature extraction
    'edge_features_csv': 'results/edge_case_features.csv',
    
    # Predictions
    'predictions_csv': 'results/edge_case_predictions.csv',
    
    # Accuracy metrics
    'accuracy_by_family_json': 'results/accuracy_by_family.json',
    'gate_evaluation_json': 'results/gate_evaluation.json',
    
    # Visualizations
    'confusion_matrix_png': 'results/plots/confusion_matrix.png',
    'feature_distributions_png': 'results/plots/feature_distributions.png',
    'accuracy_breakdown_png': 'results/plots/accuracy_breakdown.png',
    
    # Analysis
    'failure_analysis_md': 'results/failure_analysis.md',
    'feature_importance_json': 'results/feature_importance.json',
    
    # Validation report
    'validation_report_md': 'results/04_validation.md',
    
    # Logs
    'experiment_log': 'results/logs/h_c1_experiment.log',
    'model_availability_log': 'results/logs/model_availability.log'
}

# ============================================================================
# RUNTIME CONFIGURATION
# ============================================================================

RUNTIME_CONFIG = {
    'device': 'cpu',                        # CPU-only (h-m3 validated)
    'max_memory_gb': 4,                     # 4GB RAM limit (checkpoint-only)
    'max_runtime_minutes': 10,              # Target: <5 min, allow 10 min buffer
    'matplotlib_backend': 'Agg',            # Non-interactive backend
    'random_seed': 42                       # Same as h-m2/h-e1
}

# ============================================================================
# LOGGING
# ============================================================================

LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
    'datefmt': '%Y-%m-%d %H:%M:%S',
    'handlers': {
        'file': {
            'filename': 'results/logs/h_c1_experiment.log',
            'mode': 'w'
        },
        'console': {
            'stream': 'stdout'
        }
    }
}

# ============================================================================
# FAILURE MODE ANALYSIS
# ============================================================================

FAILURE_ANALYSIS_CONFIG = {
    'per_family_analysis': True,
    'feature_distributions': True,
    'systematic_patterns': True,
    'proposed_extensions': True,
    
    # Analysis dimensions (from PRD Section 4.5)
    'analysis_dimensions': {
        'NormFree': 'Check no_norm_flag correlation with misclassification',
        'SENet': 'Measure R variance (SE blocks add extra linear layers)',
        'RegNet': 'Validate CV <0.15 holds for extreme depth',
        'ViT-Extreme': 'Check if scale-invariance breaks for billion-param models'
    },
    
    # Feature importance shift
    'compute_coefficient_shift': True,
    'cohens_d_threshold': 0.5,              # Medium effect size for R discriminative power
    
    # Visualization
    'plot_failure_patterns': True,
    'save_per_model_analysis': True
}

# ============================================================================
# VALIDATION CHECKLIST
# ============================================================================

VALIDATION_CHECKLIST = {
    'before_execution': [
        'edge_case_model_availability',
        'h_e1_classifier_exists',
        'h_m3_extractor_verified'
    ],
    'during_execution': [
        'no_nan_features',
        'no_norm_flag_verified_for_normfree',
        'extraction_time_check'
    ],
    'after_execution': [
        'overall_accuracy_with_ci',
        'per_family_breakdown',
        'confusion_matrix_generated',
        'failure_analysis_documented',
        'gate_decision_recorded'
    ]
}

# ============================================================================
# SUMMARY
# ============================================================================

CONFIG_SUMMARY = {
    'hypothesis_type': 'CONDITION',
    'gate_type': 'SHOULD_WORK',
    'edge_case_families': 4,
    'total_edge_models': 20,
    'min_viable_models': 12,
    'primary_thresholds': {
        'P1_overall_accuracy': 0.70,
        'P2_passing_families': 3
    },
    'acceptable_degradation': 0.15,
    'confidence_interval': 0.95,
    'runtime_target': '<5 minutes',
    'memory_target': '<4 GB',
    'cpu_only': True,
    'code_reuse_rate': 0.90            # Reuse h-m3 extractor + h-e1 classifier
}
```

---

## Task Configuration

No subtask decomposition needed. This is an EXISTENCE-level proof of concept with single fixed configuration.

**Total Configuration Lines:** ~350 (within target)

---

## Notes

1. **Format Choice:** Hardcoded dict (per PRD requirement for externalized parameters)
2. **Base Code Verification:** Field names match h-m3 and h-e1 actual implementations
3. **Edge Case Models:** Subject to TIMM availability validation in Phase 4
4. **Classifier Path:** Verified `classifier.pkl` exists at `../h-e1/code/models/classifier.pkl`
5. **Fallback Strategy:** 3 levels (primary models → fallback models → minimum viable 12 models)
