"""
Configuration for H-C1: Edge Case Robustness Validation
CONDITION hypothesis - tests edge case architectures with fallback heuristics
"""

import os

# Edge case model families (20 models across 4 families)
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

MIN_MODELS_PER_FAMILY = 3

# Gate criteria (SHOULD_WORK)
GATE_CRITERIA = {
    'P1_overall_accuracy_min': 0.70,
    'P2_passing_families_min': 3,
    'degradation_max': 0.15
}

# Accuracy thresholds
ACCURACY_THRESHOLDS = {
    'per_family_min': 0.70,
    'baseline_expected': 0.85,
    'edge_case_target': 0.70,
    'ci_method': 'wilson',
    'confidence_level': 0.95
}

# Feature names (from h-m3)
FEATURE_NAMES = ['bn_count', 'ln_count', 'gn_count', 'no_norm_flag', 'param_mass_ratio']

# File paths
PATHS = {
    'h_m3_extractor_dir': '../../h-m3/code/src',
    'h_e1_classifier': '../../h-e1/code/models/classifier.pkl',
    'h_e1_scaler': '../../h-e1/code/models/scaler.pkl',
    'h_e1_features': '../../h-e1/code/data/train_features.csv',
    'cache_dir': '.cache/checkpoints',
    'output_dir': 'results/',
    'plots_dir': 'results/plots/',
    'logs_dir': 'results/logs/'
}

# Output files
OUTPUT_FILES = {
    'edge_features_csv': 'results/edge_case_features.csv',
    'predictions_csv': 'results/edge_case_predictions.csv',
    'accuracy_by_family_json': 'results/accuracy_by_family.json',
    'confusion_matrix_png': 'results/plots/confusion_matrix.png',
    'feature_distributions_png': 'results/plots/feature_distributions.png',
    'failure_analysis_md': 'results/failure_analysis.md',
    'validation_report_md': 'results/04_validation.md',
    'experiment_log': 'results/logs/h_c1_experiment.log'
}

# Logging
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '[%(asctime)s] [%(levelname)s] %(message)s',
    'datefmt': '%Y-%m-%d %H:%M:%S'
}
