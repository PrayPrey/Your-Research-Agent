# Configuration Design: H-E1 Statistical Features Sufficiency

**Hypothesis ID:** h-e1  
**Type:** EXISTENCE (PoC)  
**Date:** 2026-07-11  

---

## Codebase Analysis (Serena)

**Project Type:** green-field  
**Status:** New implementation - no existing code to analyze  
**Config Files Found:** None - new config design  
**Pattern Used:** Hardcoded dict (EXISTENCE PoC - minimal configuration)

---

## Knowledge Base Patterns Applied

**Applied:** Standard sklearn configuration patterns, TIMM model loading defaults

---

## Configuration Format

Single hardcoded dictionary for EXISTENCE proof-of-concept. No hyperparameter variations needed.

```python
# code/config.py

"""
Configuration for H-E1: Statistical Features Sufficiency
EXISTENCE hypothesis - fixed parameters, no tuning
"""

# ============================================================================
# MODEL SELECTION
# ============================================================================

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

# ============================================================================
# FEATURE EXTRACTION
# ============================================================================

FEATURE_NAMES = [
    'bn_count',          # BatchNorm layer count
    'ln_count',          # LayerNorm layer count
    'gn_count',          # GroupNorm layer count
    'no_norm_flag',      # Binary: 1 if no normalization, else 0
    'param_mass_ratio'   # R = conv_params / (conv_params + linear_params_no_head)
]

NORM_PATTERNS = {
    'bn': r'bn|batch_norm|batchnorm',
    'ln': r'ln|layer_norm|layernorm',
    'gn': r'gn|group_norm|groupnorm'
}

HEAD_KEYWORDS = ['head', 'fc', 'classifier']

# ============================================================================
# DATA SPLIT
# ============================================================================

SPLIT_CONFIG = {
    'test_size': 0.3,
    'random_state': 42,
    'stratify': True  # Stratify by family
}

# ============================================================================
# CLASSIFIER TRAINING
# ============================================================================

CLASSIFIER_CONFIG = {
    'multi_class': 'multinomial',
    'solver': 'lbfgs',
    'max_iter': 1000,
    'random_state': 42,
    'class_weight': 'balanced'  # Handle 20% hybrid imbalance
}

SCALER_CONFIG = {
    'with_mean': True,
    'with_std': True
}

# ============================================================================
# VALIDATION THRESHOLDS
# ============================================================================

VALIDATION_THRESHOLDS = {
    # Primary metric (MUST_WORK gate)
    'macro_accuracy': 0.80,
    
    # Secondary metrics
    'per_class_accuracy': 0.75,
    
    # Assumption validation
    'a1_alignment_rate': 0.90,      # A1: TIMM naming alignment
    'a2_cnn_ln_violation': 0.15,    # A2: CNN with LayerNorm rate
    'a2_trans_bn_violation': 0.15,  # A2: Transformer with BatchNorm rate
    'a3_scale_invariance_cv': 0.15  # A3: ResNet family CV threshold
}

ASSUMPTION_VALIDATION = {
    'a1_sample_size': 10,           # Manual verification sample
    'a3_family_models': [           # ResNet variants for scale invariance test
        'resnet18', 'resnet34', 'resnet50', 'resnet101', 'resnet152'
    ]
}

# ============================================================================
# FILE PATHS
# ============================================================================

PATHS = {
    'data_dir': 'data/',
    'models_dir': 'models/',
    'results_dir': 'results/',
    'logs_dir': 'logs/',
    
    # Data files
    'model_list': 'data/model_list.json',
    'train_features': 'data/train_features.csv',
    'val_features': 'data/val_features.csv',
    'assumption_validation': 'data/assumption_validation.json',
    
    # Model artifacts
    'classifier': 'models/classifier.pkl',
    'scaler': 'models/scaler.pkl',
    
    # Results
    'results_report': 'results/h_e1_results.md',
    'confusion_matrix_plot': 'results/confusion_matrix.png',
    'feature_importance_plot': 'results/feature_importance.png',
    'r_distribution_plot': 'results/r_distribution.png',
    'failure_analysis': 'results/h_e1_failure_analysis.md',
    
    # Logs
    'experiment_log': 'logs/experiment_log.txt'
}

# ============================================================================
# LOGGING
# ============================================================================

LOGGING_CONFIG = {
    'format': '[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
    'datefmt': '%Y-%m-%d %H:%M:%S',
    'level': 'INFO',
    'handlers': {
        'file': {
            'filename': 'logs/experiment_log.txt',
            'mode': 'a'
        },
        'console': {
            'stream': 'stdout'
        }
    }
}

LOG_CHECKPOINTS = [
    'data_download_progress',     # Every 10 models
    'assumption_validation',       # A1/A2/A3 pass/fail
    'training_completion',         # Convergence status
    'validation_accuracy',         # Primary metric
    'decision_gate'                # PASS/FAIL verdict
]

# ============================================================================
# EXPERIMENT SETTINGS
# ============================================================================

EXPERIMENT_CONFIG = {
    'random_seed': 42,
    'timm_cache_dir': '~/.cache/torch/hub/checkpoints/',
    'checkpoint_download_timeout': 1800,  # 30 minutes per model
    'num_workers': 4,                      # Parallel downloads
    'memory_limit_gb': 8
}

# ============================================================================
# REPORTING
# ============================================================================

REPORT_CONFIG = {
    'output_format': 'markdown',
    'include_plots': True,
    'plot_dpi': 150,
    'plot_style': 'seaborn-v0_8-darkgrid',
    'confusion_matrix_cmap': 'Blues',
    'feature_importance_color': 'steelblue',
    'r_distribution_bins': 20
}

REPORT_SECTIONS = [
    'executive_summary',
    'metrics',
    'confusion_matrix',
    'feature_importance',
    'failure_cases',
    'assumption_validation',
    'next_steps'
]

# ============================================================================
# ERROR HANDLING
# ============================================================================

ERROR_HANDLING = {
    'checkpoint_download_timeout': {
        'action': 'retry_once_then_skip',
        'log_level': 'WARNING'
    },
    'missing_model': {
        'action': 'substitute_similar',
        'log_level': 'WARNING'
    },
    'state_dict_parse_error': {
        'action': 'skip_model',
        'log_level': 'ERROR'
    },
    'empty_state_dict': {
        'action': 'raise_error',
        'log_level': 'ERROR'
    },
    'zero_total_params': {
        'action': 'set_ratio_zero',
        'log_level': 'WARNING'
    },
    'training_non_convergence': {
        'action': 'proceed_with_warning',
        'log_level': 'WARNING'
    },
    'singular_matrix': {
        'action': 'check_feature_variance',
        'log_level': 'ERROR'
    },
    'plot_generation_failure': {
        'action': 'continue_without_plot',
        'log_level': 'WARNING'
    }
}
```

---

## Task-Specific Configuration Breakdowns

### E1-3: Validation (Complexity 8, Budget: 1 subtask)

**Subtasks [1/1 used]:**

| ID | Subtask | Description |
|----|---------|-------------|
| C-3-1 | Assumption Test Implementation | Implement A1/A2/A3 validators with threshold checks |

**Configuration:**
```python
# Assumption validation settings (from config.py)
VALIDATION_THRESHOLDS = {
    'a1_alignment_rate': 0.90,
    'a2_cnn_ln_violation': 0.15,
    'a2_trans_bn_violation': 0.15,
    'a3_scale_invariance_cv': 0.15
}

ASSUMPTION_VALIDATION = {
    'a1_sample_size': 10,
    'a3_family_models': ['resnet18', 'resnet34', 'resnet50', 'resnet101', 'resnet152']
}
```

---

### E1-7: Pipeline Integration (Complexity 7, Budget: 1 subtask)

**Subtasks [1/1 used]:**

| ID | Subtask | Description |
|----|---------|-------------|
| C-7-1 | Orchestrator Wiring | Wire modules with logging, error handling, and checkpoint saving |

**Configuration:**
```python
# Logging configuration (from config.py)
LOGGING_CONFIG = {
    'format': '[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
    'datefmt': '%Y-%m-%d %H:%M:%S',
    'level': 'INFO',
    'handlers': {
        'file': {'filename': 'logs/experiment_log.txt', 'mode': 'a'},
        'console': {'stream': 'stdout'}
    }
}

# Error handling actions (from config.py)
ERROR_HANDLING = {
    'checkpoint_download_timeout': {'action': 'retry_once_then_skip'},
    'missing_model': {'action': 'substitute_similar'},
    'state_dict_parse_error': {'action': 'skip_model'}
}
```

---

### E1-4: Training (Complexity 6, Budget: 1 subtask)

**Subtasks [1/1 used]:**

| ID | Subtask | Description |
|----|---------|-------------|
| C-4-1 | Classifier Training | StandardScaler + LogisticRegression training and serialization |

**Configuration:**
```python
# Classifier hyperparameters (from config.py)
CLASSIFIER_CONFIG = {
    'multi_class': 'multinomial',
    'solver': 'lbfgs',
    'max_iter': 1000,
    'random_state': 42,
    'class_weight': 'balanced'
}

SCALER_CONFIG = {
    'with_mean': True,
    'with_std': True
}
```

---

### E1-6: Reporting (Complexity 5, Budget: 1 subtask)

**Subtasks [1/1 used]:**

| ID | Subtask | Description |
|----|---------|-------------|
| C-6-1 | Report Generation | Markdown report with metrics, plots, and failure analysis |

**Configuration:**
```python
# Report styling (from config.py)
REPORT_CONFIG = {
    'output_format': 'markdown',
    'include_plots': True,
    'plot_dpi': 150,
    'plot_style': 'seaborn-v0_8-darkgrid',
    'confusion_matrix_cmap': 'Blues',
    'feature_importance_color': 'steelblue',
    'r_distribution_bins': 20
}

REPORT_SECTIONS = [
    'executive_summary',
    'metrics',
    'confusion_matrix',
    'feature_importance',
    'failure_cases',
    'assumption_validation',
    'next_steps'
]
```

---

## Configuration Usage Example

```python
# main.py - Orchestrator usage
from config import (
    MODEL_FAMILIES,
    CLASSIFIER_CONFIG,
    VALIDATION_THRESHOLDS,
    PATHS,
    LOGGING_CONFIG
)

class ExperimentPipeline:
    def __init__(self):
        self.config = {
            'model_families': MODEL_FAMILIES,
            'classifier': CLASSIFIER_CONFIG,
            'thresholds': VALIDATION_THRESHOLDS,
            'paths': PATHS
        }
        self._setup_logging()
    
    def _setup_logging(self):
        import logging
        logging.basicConfig(**LOGGING_CONFIG)
        self.logger = logging.getLogger(__name__)
    
    def execute_full_pipeline(self):
        self.run_data_preparation()
        self.run_assumption_validation()
        self.run_training()
        self.run_evaluation()
        self.run_reporting()
```

---

## EXISTENCE Compliance Check

- [x] Single fixed configuration (no hyperparameter grid)
- [x] Default values from sklearn documentation
- [x] One random seed (42)
- [x] Minimal epochs/iterations (1000 max_iter)
- [x] No ablation configs
- [x] Hardcoded dict format (copy-paste ready)
- [x] Total subtasks: 4/4 used (within budget)

---

## Next Phase Handoff

**For Phase 4 (Coder):**

Copy-paste ready configuration in `code/config.py`. All modules import directly from this file.

**Key Import Pattern:**
```python
from config import MODEL_FAMILIES, CLASSIFIER_CONFIG, VALIDATION_THRESHOLDS, PATHS
```

**Critical Values:**
- Random seed: 42 (all components)
- Train/val split: 70/30 (test_size=0.3)
- Primary threshold: macro_accuracy > 0.80
- Max iterations: 1000 (lbfgs solver)

**No Configuration Variations:**
This is EXISTENCE PoC - no hyperparameter tuning, no ablation studies, no grid search.

---

**End of Configuration Document**
