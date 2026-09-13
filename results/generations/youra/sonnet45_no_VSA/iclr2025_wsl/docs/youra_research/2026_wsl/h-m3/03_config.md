# Configuration Design: H-M3 Checkpoint Extraction Feasibility

**Hypothesis ID:** h-m3  
**Type:** MECHANISM (MUST_WORK gate)  
**Date:** 2026-07-11  

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis  
**Status:** Config classes verified from h-m2 base code  
**Config Files Found:** docs/youra_research/h-m2/code/config.py, docs/youra_research/h-m2/code/src/feature_extractor.py  
**Pattern Used:** Hardcoded dict (reusing h-m2 pattern for consistency)

**Base Config Reference:** h-m2/code/config.py contains:
- MODEL_FAMILIES dict (50 TIMM models)
- FEATURE_NAMES list (5 statistical features)
- NORM_PATTERNS dict (normalization layer regex)
- HEAD_KEYWORDS list (classification head detection)

---

## Knowledge Base Patterns Applied

**Applied:** PyTorch timing benchmarks (perf_counter), GPU memory monitoring patterns, statistical validation configurations

---

## Configuration Format

Single hardcoded dictionary for MECHANISM validation. H-m3 reuses h-m2 configurations and adds timing/monitoring settings.

```python
# code/config_h_m3.py

"""
Configuration for H-M3: Checkpoint Extraction Feasibility
MECHANISM hypothesis - extends h-m2 with timing benchmark and GPU monitoring configs
"""

import os

# ============================================================================
# INHERITED FROM H-M2 (Actual Base Code)
# ============================================================================

# Reuse h-m2 config via import or direct copy
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

# ============================================================================
# H-M3 SPECIFIC: PRIMARY CRITERIA (MUST_WORK GATE)
# ============================================================================

GATE_CRITERIA = {
    'P1_total_time_max_seconds': 600,       # P1: Total extraction time <10 minutes
    'P2_gpu_memory_max_mb': 0               # P2: GPU memory usage = 0 MB (CPU-only)
}

# ============================================================================
# H-M3 SPECIFIC: SECONDARY CRITERIA
# ============================================================================

SECONDARY_CRITERIA = {
    'S1_feature_equivalence_min': 1.0,      # S1: 100% exact match with h-e1 cached features
    'S2_speedup_min_factor': 3.0            # S2: >3x faster than forward-pass baseline
}

# ============================================================================
# H-M3 SPECIFIC: TIMING BENCHMARK CONFIGURATION
# ============================================================================

TIMING_CONFIG = {
    'warmup_runs': 1,                       # Warmup: extract 1 model before timing
    'timer_function': 'perf_counter',       # time.perf_counter() for nanosecond precision
    'exclude_download_time': True,          # Report cached-run timing separately
    'per_model_logging': True,              # Log individual model extraction times
    'percentiles': [50, 90, 95],            # Compute median, 90th, 95th percentile
    'primary_metric': 'total_time',         # Primary gate criterion: total extraction time
    'secondary_metrics': ['avg_time', 'median_time', 'p90_time']
}

WARMUP_CONFIG = {
    'warmup_model': 'resnet18',             # Small model for warmup
    'exclude_from_results': True            # Don't count warmup in timing stats
}

# ============================================================================
# H-M3 SPECIFIC: GPU MONITORING CONFIGURATION
# ============================================================================

GPU_MONITOR_CONFIG = {
    'poll_interval': 0.1,                   # Poll GPU memory every 0.1 seconds
    'monitoring_method': 'torch.cuda.memory_allocated',
    'background_thread': True,              # Run monitoring in background thread
    'verify_cpu_only': True,                # Assert max GPU usage = 0 MB
    'fallback_method': 'nvidia-smi',        # Secondary verification via nvidia-smi
    'log_to_csv': True                      # Save memory log to CSV
}

# ============================================================================
# H-M3 SPECIFIC: CHECKPOINT LOADING CONFIGURATION
# ============================================================================

CHECKPOINT_CONFIG = {
    'weights_only': True,                   # PyTorch 2.0+ security: weights_only=True
    'map_location': 'cpu',                  # Force CPU device mapping
    'cache_dir': '.cache/checkpoints',      # Local checkpoint cache directory
    'download_retry': 3,                    # Retry download 3 times on failure
    'download_timeout': 300,                # 5-minute timeout per checkpoint download
    'skip_failed_models': True,             # Skip models with download/loading errors
    'max_failed_rate': 0.05                 # Allow up to 5% models to fail
}

# ============================================================================
# H-M3 SPECIFIC: FORWARD-PASS BASELINE CONFIGURATION
# ============================================================================

BASELINE_SUBSET = [
    'resnet50',                             # CNN representative
    'vit_base_patch16_224',                 # Transformer representative
    'efficientnet_b0',                      # Efficient CNN
    'deit_small_patch16_224',               # Small Transformer
    'swin_tiny_patch4_window7_224'          # Hierarchical Transformer
]

FORWARD_PASS_CONFIG = {
    'device': 'cpu',                        # CPU-only for fair comparison
    'input_shape': (1, 3, 224, 224),        # Single dummy input
    'num_forward_passes': 1,                # 1 forward pass per model
    'clear_cache_after': True,              # torch.cuda.empty_cache() after each model
    'pretrained': True                      # Load pretrained weights via TIMM
}

# ============================================================================
# H-M3 SPECIFIC: FEATURE VALIDATION CONFIGURATION
# ============================================================================

FEATURE_VALIDATION_CONFIG = {
    'cached_features_path': '../h-e1/code/data/train_features.csv',
    'similarity_metric': 'cosine',          # Cosine similarity for feature vectors
    'exact_match_threshold': 1.0,           # Require perfect match
    'log_mismatches': True,                 # Log models with feature mismatches
    'per_model_validation': True            # Validate each model individually
}

# ============================================================================
# H-M3 SPECIFIC: SCALABILITY ANALYSIS CONFIGURATION
# ============================================================================

SCALABILITY_CONFIG = {
    'target_sizes': [100, 200, 500],        # Extrapolate to 100, 200, 500 models
    'time_complexity': 'linear',            # Expected O(n) linear scaling
    'extrapolation_method': 'linear_fit',   # Use linear regression for extrapolation
    'bottleneck_detection': True,           # Identify slowest models/families
    'phase_breakdown': ['load', 'parse', 'extract']  # Time each extraction phase
}

BOTTLENECK_CONFIG = {
    'top_slowest_count': 5,                 # Report top 5 slowest models
    'top_fastest_count': 5,                 # Report top 5 fastest models
    'family_aggregation': True              # Compute avg time per family
}

# ============================================================================
# H-M3 SPECIFIC: OUTPUT CONFIGURATION
# ============================================================================

OUTPUT_CONFIG = {
    'output_dir': 'results/',
    'checkpoint_timings_json': 'results/checkpoint_only_timings.json',
    'forward_timings_json': 'results/forward_pass_timings.json',
    'speedup_analysis_json': 'results/speedup_analysis.json',
    'gpu_memory_log_csv': 'results/gpu_memory_log.csv',
    'gpu_memory_max_txt': 'results/gpu_memory_max.txt',
    'feature_validation_json': 'results/feature_validation.json',
    'scalability_analysis_json': 'results/scalability_analysis.json',
    'gate_evaluation_json': 'results/gate_evaluation.json',
    'timing_comparison_png': 'results/timing_comparison.png',
    'timing_report_md': 'results/timing_report.md',
    'validation_report_md': 'results/04_validation.md'
}

OUTPUT_FORMATS = {
    'json_indent': 2,
    'json_ensure_ascii': False,
    'csv_delimiter': ',',
    'plot_dpi': 300,
    'plot_format': 'png'
}

# ============================================================================
# H-M3 SPECIFIC: VISUALIZATION CONFIGURATION
# ============================================================================

VISUALIZATION_CONFIG = {
    'figure_size': (12, 6),
    'dpi': 300,
    'bar_width': 0.35,
    'colors': {
        'checkpoint_only': '#2ca02c',       # Green
        'forward_pass': '#d62728'           # Red
    },
    'title': 'Extraction Time Comparison: Checkpoint-Only vs Forward-Pass',
    'xlabel': 'Model',
    'ylabel': 'Extraction Time (seconds)',
    'legend': True,
    'grid': True,
    'save_format': 'png'
}

# ============================================================================
# H-M3 SPECIFIC: RUNTIME CONFIGURATION
# ============================================================================

RUNTIME_CONFIG = {
    'device': 'cpu',                        # CPU-only execution
    'max_memory_gb': 16,                    # 16GB RAM limit
    'max_runtime_minutes': 15,              # Allow 15 min (target <10 min)
    'matplotlib_backend': 'Agg',            # Non-interactive backend
    'num_workers': 1,                       # Sequential processing (no parallelization)
    'random_seed': 42                       # Same as h-m2/h-e1 for reproducibility
}

# ============================================================================
# H-M3 SPECIFIC: GATE DECISION LOGIC
# ============================================================================

GATE_DECISION_CONFIG = {
    'primary_criteria': ['P1', 'P2'],       # Both must pass
    'secondary_criteria': ['S1', 'S2'],     # Optional
    'decision_matrix': {
        'PASS': 'P1: total_time <600s AND P2: gpu_memory = 0 MB',
        'FAIL_P1': 'Total extraction time ≥10 minutes',
        'FAIL_P2': 'GPU memory usage >0 MB (not CPU-only)'
    },
    'next_steps': {
        'PASS': 'Proceed to H-C1 (Edge Case Robustness)',
        'FAIL_P1': 'EXPLORE parallel extraction OR PIVOT to relaxed threshold (15 min)',
        'FAIL_P2': 'ABANDON (method not CPU-only, requires GPU infrastructure)'
    }
}

FAILURE_MODE_ANALYSIS = {
    'P1_fail': {
        'symptom': 'Total extraction time >10 minutes',
        'diagnosis': 'Checkpoint download or state_dict parsing bottleneck',
        'remediation': 'Profile phase breakdown, implement parallel loading, or relax threshold'
    },
    'P2_fail': {
        'symptom': 'GPU memory usage detected during extraction',
        'diagnosis': 'torch.load() allocates GPU buffer despite map_location=cpu',
        'remediation': 'CRITICAL FAILURE - violates CPU-only claim, method abandoned'
    },
    'S1_fail': {
        'symptom': 'Feature mismatch with h-e1 cached features',
        'diagnosis': 'Extraction bug in weights_only=True loading',
        'remediation': 'Debug extraction logic, verify state_dict integrity'
    },
    'S2_fail': {
        'symptom': 'Speedup <3x vs forward-pass baseline',
        'diagnosis': 'Checkpoint-only extraction not significantly faster',
        'remediation': 'Document limitation, proceed if speedup still positive'
    }
}

# ============================================================================
# H-M3 SPECIFIC: LOGGING
# ============================================================================

LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
    'datefmt': '%Y-%m-%d %H:%M:%S',
    'handlers': {
        'file': {
            'filename': 'results/h_m3_experiment.log',
            'mode': 'w'
        },
        'console': {
            'stream': 'stdout'
        }
    }
}

LOG_CHECKPOINTS = [
    'warmup_complete',
    'checkpoint_only_extraction_start',
    'checkpoint_only_extraction_complete',
    'gpu_monitoring_complete',
    'forward_baseline_extraction_complete',
    'feature_validation_complete',
    'scalability_analysis_complete',
    'gate_decision',
    'validation_report_generated'
]

# ============================================================================
# H-M3 SPECIFIC: ERROR HANDLING
# ============================================================================

ERROR_HANDLING_CONFIG = {
    'retry_on_network_error': True,
    'max_retries': 3,
    'retry_delay_seconds': 5,
    'skip_corrupted_checkpoints': True,
    'log_failed_models': True,
    'raise_on_critical_failure': True,      # Raise exception for P2 failure (GPU usage >0)
    'graceful_degradation': True            # Allow P1 failure with remediation
}

# ============================================================================
# H-M3 SPECIFIC: VALIDATION REPORT TEMPLATE
# ============================================================================

REPORT_TEMPLATE = {
    'sections': [
        'gate_decision',
        'primary_results_p1_timing',
        'primary_results_p2_gpu',
        'secondary_results_s1_equivalence',
        'secondary_results_s2_speedup',
        'scalability_analysis',
        'bottleneck_analysis',
        'key_findings',
        'recommendations_next_hypothesis'
    ],
    'include_tables': True,
    'include_timing_plot': True,
    'include_gpu_log_reference': True,
    'include_per_model_breakdown': True
}

# ============================================================================
# SUMMARY: KEY CONFIGURATION VALUES
# ============================================================================

CONFIG_SUMMARY = {
    'hypothesis_type': 'MECHANISM',
    'gate_type': 'MUST_WORK',
    'total_models': 50,
    'baseline_subset_size': 5,
    'primary_thresholds': {
        'P1_total_time_seconds': 600,
        'P2_gpu_memory_mb': 0
    },
    'secondary_thresholds': {
        'S1_feature_equivalence': 1.0,
        'S2_speedup_factor': 3.0
    },
    'runtime_target': '8-9 minutes',
    'memory_target': '16 GB',
    'code_reuse_rate': 0.28,                # Reuse feature extraction, add timing modules
    'random_seed': 42,
    'cpu_only': True,
    'weights_only_flag': True
}
```

---

## Inherited Configuration (Base Hypothesis)

### Config Classes (From h-m2 Actual Code)

The following configs are inherited or referenced from h-m2:

```python
# From: docs/youra_research/h-m2/code/config.py (ACTUAL CODE)

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
```

### Feature Extraction (From h-m2 Actual Code)

```python
# From: docs/youra_research/h-m2/code/src/feature_extractor.py

class StatisticalFeatureExtractor:
    """Extract statistical features from PyTorch state_dict"""

    def extract_features(self, state_dict: dict) -> dict:
        """
        Returns:
            Dictionary with 5 features: bn_count, ln_count, gn_count, no_norm_flag, param_mass_ratio
        """
        # H-M3 reuses this extraction logic with timing measurement wrapper
```

**Verified from:** docs/youra_research/h-m2/code/ (actual implementation)

---

## Task Configuration Breakdown

### A-1: Project Setup [Complexity: 6]

```python
PROJECT_SETUP = {
    'directory_structure': {
        'code/': ['main_h_m3.py', 'config_h_m3.py'],
        'code/src/': ['checkpoint_only_extractor.py', 'forward_pass_extractor.py', 
                      'timing_benchmark.py', 'gpu_monitor.py', 'feature_validator.py',
                      'gate_evaluator.py', 'scalability_analyzer.py'],
        'code/tests/': ['test_checkpoint_extractor.py', 'test_timing_benchmark.py',
                       'test_gpu_monitor.py', 'test_feature_validator.py', 'test_h_m3_runner.py'],
        'results/': []
    },
    'dependencies': ['torch>=2.0', 'timm', 'pandas', 'matplotlib', 'numpy']
}
```

### A-2: CheckpointOnlyExtractor [Complexity: 14]

```python
CHECKPOINT_EXTRACTOR_CONFIG = {
    'weights_only': True,                   # Security: prevent code execution
    'map_location': 'cpu',
    'cache_dir': '.cache/checkpoints',
    'download_retry': 3,
    'download_timeout': 300,
    'skip_failed_models': True,
    'max_failed_rate': 0.05
}
```

### A-3: ForwardPassExtractor [Complexity: 12]

```python
FORWARD_EXTRACTOR_CONFIG = {
    'device': 'cpu',
    'input_shape': (1, 3, 224, 224),
    'num_forward_passes': 1,
    'clear_cache_after': True,
    'pretrained': True,
    'baseline_subset': BASELINE_SUBSET  # 5 models
}
```

### A-4: TimingBenchmark [Complexity: 15]

```python
TIMING_BENCHMARK_CONFIG = {
    'warmup_runs': 1,
    'timer_function': 'perf_counter',
    'exclude_download_time': True,
    'per_model_logging': True,
    'percentiles': [50, 90, 95],
    'primary_metric': 'total_time',
    'secondary_metrics': ['avg_time', 'median_time', 'p90_time']
}
```

### A-5: GPUMonitor [Complexity: 11]

```python
GPU_MONITOR_SETUP = {
    'poll_interval': 0.1,
    'monitoring_method': 'torch.cuda.memory_allocated',
    'background_thread': True,
    'verify_cpu_only': True,
    'log_to_csv': True
}
```

### A-6: FeatureValidator [Complexity: 10]

```python
FEATURE_VALIDATOR_CONFIG = {
    'cached_features_path': '../h-e1/code/data/train_features.csv',
    'similarity_metric': 'cosine',
    'exact_match_threshold': 1.0,
    'log_mismatches': True,
    'per_model_validation': True
}
```

### A-7: ScalabilityAnalyzer [Complexity: 9]

```python
SCALABILITY_ANALYZER_CONFIG = {
    'target_sizes': [100, 200, 500],
    'time_complexity': 'linear',
    'extrapolation_method': 'linear_fit',
    'bottleneck_detection': True,
    'phase_breakdown': ['load', 'parse', 'extract']
}
```

### A-8: GateEvaluator [Complexity: 8]

```python
GATE_EVALUATOR_CONFIG = {
    'primary_criteria': ['P1', 'P2'],
    'secondary_criteria': ['S1', 'S2'],
    'thresholds': {
        'P1_total_time_seconds': 600,
        'P2_gpu_memory_mb': 0,
        'S1_feature_equivalence': 1.0,
        'S2_speedup_factor': 3.0
    }
}
```

---

## Subtask Budget Allocation

Total Budget: 8 subtasks

| Task ID | Task Name | Complexity | Subtasks Allocated |
|---------|-----------|------------|-------------------|
| A-1 | Project Setup | 6 | 1 (within budget) |
| A-2 | CheckpointOnlyExtractor | 14 | 2 (high complexity) |
| A-3 | ForwardPassExtractor | 12 | 1 (medium-high complexity) |
| A-4 | TimingBenchmark | 15 | 2 (very high complexity) |
| A-5 | GPUMonitor | 11 | 1 (medium complexity) |
| A-6 | FeatureValidator | 10 | 1 (medium complexity) |
| **Total** | **6 tasks** | **68** | **8/8 used** |

**Note:** Remaining tasks (A-7 through A-12) allocated to separate implementation phases.

---

## MECHANISM Compliance Check

- [x] Reuses h-m2 configurations (MODEL_FAMILIES, FEATURE_NAMES, NORM_PATTERNS, HEAD_KEYWORDS)
- [x] Fixed gate thresholds (no tuning)
- [x] Same random seed (42) as h-m2/h-e1
- [x] Single configuration (no hyperparameter grid)
- [x] Timing/monitoring-specific configs only (no model architecture changes)
- [x] MUST_WORK gate criteria clearly defined (P1, P2)
- [x] Total subtasks: 8 (exact budget)

---

## Critical Configuration Notes

### 1. Field Name Verification (h-m2 Compatibility)

**All field names match h-m2 actual code:**
- `bn_count`, `ln_count`, `gn_count`, `no_norm_flag`, `param_mass_ratio`: Match FEATURE_NAMES in h-m2/code/config.py
- `extract_features()`: Returns dict with 5 features (verified from h-m2/code/src/feature_extractor.py)

### 2. Model Counts

**Actual counts from h-m2 config:**
- CNN: 24 models
- Transformer: 22 models
- Hybrid: 11 models
- **Total unique: 50 models**

### 3. Timing Configuration

**High-precision timing:**
- `time.perf_counter()`: Nanosecond resolution (not `time.time()`)
- Warmup run: Exclude 1 model from timing stats
- Report cached-run timing (exclude first-time checkpoint download)

### 4. GPU Monitoring

**CPU-only verification:**
- Background thread polling every 0.1 seconds
- `torch.cuda.memory_allocated()` primary method
- `nvidia-smi` fallback verification
- Assert max GPU memory = 0 MB (CRITICAL gate criterion)

### 5. Checkpoint Security

**PyTorch 2.0+ security:**
- `weights_only=True`: Prevent arbitrary code execution
- `map_location='cpu'`: Force CPU device mapping
- No custom unpickling (only tensor data)

### 6. Baseline Subset

**5-model forward-pass baseline:**
- resnet50 (CNN)
- vit_base_patch16_224 (Transformer)
- efficientnet_b0 (Efficient CNN)
- deit_small_patch16_224 (Small Transformer)
- swin_tiny_patch4_window7_224 (Hierarchical Transformer)

---

## Next Phase Handoff

**For Phase 4 (Coder):**

Copy-paste ready configuration in `code/config_h_m3.py`. Import h-m2 feature extractor via relative import or copy.

**Key Import Pattern:**
```python
# Option 1: Import h-m2 feature extractor
import sys
sys.path.append('../h-m2/code')
from src.feature_extractor import StatisticalFeatureExtractor

# Option 2: Copy feature extractor to h-m3/code/src/
from src.feature_extractor import StatisticalFeatureExtractor

# Import h-m3 configs
from config_h_m3 import (
    MODEL_FAMILIES,
    GATE_CRITERIA,
    TIMING_CONFIG,
    GPU_MONITOR_CONFIG,
    CHECKPOINT_CONFIG,
    BASELINE_SUBSET,
    OUTPUT_CONFIG
)
```

**Critical Values:**
- Random seed: 42 (same as h-m2/h-e1)
- P1: Total extraction time <600 seconds (MUST_WORK gate)
- P2: GPU memory = 0 MB (MUST_WORK gate)
- S1: Feature equivalence = 1.0 (correctness validation)
- S2: Speedup >3x vs forward-pass (practical advantage)

**No Configuration Variations:**
This is MECHANISM validation - fixed thresholds, no hyperparameter tuning, reuses h-m2 feature extraction logic.

---

**End of Configuration Document**
