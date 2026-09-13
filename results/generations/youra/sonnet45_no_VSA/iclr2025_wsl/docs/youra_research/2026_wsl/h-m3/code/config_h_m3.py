"""
Configuration for H-M3: Checkpoint Extraction Feasibility
MECHANISM hypothesis - extends h-m2 with timing benchmark and GPU monitoring configs
"""

import os

# ============================================================================
# INHERITED FROM H-M2 (Actual Base Code)
# ============================================================================

# Model families - reuse from h-m2
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
# H-M3 SPECIFIC: BASELINE SUBSET
# ============================================================================

BASELINE_SUBSET = [
    'resnet50',                             # CNN representative
    'vit_base_patch16_224',                 # Transformer representative
    'efficientnet_b0',                      # Efficient CNN
    'deit_small_patch16_224',               # Small Transformer
    'swin_tiny_patch4_window7_224'          # Hierarchical Transformer
]

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

# ============================================================================
# PATHS (Computed)
# ============================================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
H_E1_DATA_DIR = os.path.join(BASE_DIR, '../../h-e1/code/data')
H_M2_CODE_DIR = os.path.join(BASE_DIR, '../../h-m2/code')
RESULTS_DIR = os.path.join(BASE_DIR, 'results')
CACHE_DIR = os.path.join(BASE_DIR, CHECKPOINT_CONFIG['cache_dir'])

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
    'code_reuse_rate': 0.28,
    'random_seed': 42,
    'cpu_only': True,
    'weights_only_flag': True
}
