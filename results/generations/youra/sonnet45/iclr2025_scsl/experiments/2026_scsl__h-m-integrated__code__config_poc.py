"""Proof-of-Concept Configuration for h-m-integrated: Reduced Scale for Testing."""

import sys
from pathlib import Path

# Add h-e1 to path for imports
h_e1_path = Path(__file__).parent.parent.parent / 'h-e1' / 'code'
sys.path.insert(0, str(h_e1_path))

# LA-SSL Sampler (M-1)
LASSL_SAMPLER_CONFIG = {
    'alpha': 0.5,
    'window_size': 5,  # Reduced from 10
}

# SimCLR Baseline (M-3) - PROOF OF CONCEPT SCALE
SIMCLR_CONFIG = {
    # Model
    'encoder_name': 'resnet50',
    'projection_dim': 128,
    'pretrained': False,

    # Training - REDUCED FOR POC
    'lr': 0.3,
    'weight_decay': 1e-6,
    'temperature': 0.5,
    'momentum': 0.9,

    # Schedule - REDUCED FOR POC
    'epochs': 20,  # Reduced from 100
    'batch_size': 64,  # Reduced from 128 for stability
    'checkpoint_freq': 10,  # Save at epoch 10 and 20
    'seeds': [0],  # Single seed instead of 3
}

# LA-SSL Training (M-2, M-4) - PROOF OF CONCEPT SCALE
LASSL_CONFIG = {
    **SIMCLR_CONFIG,
    'sampler_alpha': 0.5,
    'sampler_window': 5,  # Reduced from 10
}

# Clustering (M-5)
CLUSTERING_CONFIG = {
    'n_clusters': 4,
    'random_state': 42,
    'n_init': 10,
}

# Linear Probe (M-6)
LINEAR_PROBE_CONFIG = {
    'lr_grid': [0.01, 0.001],  # Reduced grid search
    'wd_grid': [1e-4, 1e-5],  # Reduced grid search
    'seeds': [0, 1, 2],  # Reduced from 5 seeds
    'epochs': 10,  # Reduced from 20
    'batch_size': 32,
}

# Mechanism Validation (M-7)
VALIDATION_CONFIG = {
    # M1
    'ami_threshold': 0.4,
    'silhouette_threshold': 0.3,

    # M2
    'correlation_pvalue': 0.05,
    'delta_wga_threshold': 2.0,

    # M3
    'ami_reduction_threshold': 0.3,
    'auc_delta_threshold': 0.05,
}

# Visualization (M-8)
VISUALIZATION_CONFIG = {
    'tsne_perplexity': 30,
    'tsne_random_state': 42,
    'figure_dpi': 300,
    'figure_format': 'png',
}

# Data
DATA_CONFIG = {
    'root_dir': '/home/anonymous/YouRA_results_new_4_sonnet45/TEST_scsl/docs/youra_research/20260318_scsl/.data_cache/datasets/waterbird_complete95_forest2water2',
    'num_workers': 2,  # Reduced from 4 for stability
    'image_size': 224,
}

# Environment
ENVIRONMENT_CONFIG = {
    'device': 'cuda',
    'seed': 42,
    'output_dir': './results',
    'checkpoint_dir': './checkpoints',
    'figure_dir': './figures',
}
