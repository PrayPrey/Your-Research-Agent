# h-m2/code/config.py
import torch

# Architecture configs
RESNET_CONFIG = {
    'model': 'resnet50',
    'lr': 0.001,
    'batch_size': 128,  # Reduced for PoC
    'weight_decay': 1e-4,
    'lr_schedule': 'cosine'
}

VIT_CONFIG = {
    'model': 'vit_base_patch16_224',
    'lr': 0.0003,
    'batch_size': 128,  # Reduced for PoC
    'weight_decay': 0.05,
    'lr_schedule': 'cosine'
}

# Dataset config
DATASET_CONFIG = {
    'primary': 'waterbirds',
    'image_size': 224,
    'num_workers': 4
}

WATERBIRDS_CONFIG = {
    'source': 'wilds',
    'download': True,
    'splits': ['train', 'val', 'test'],
    'augmentation': {
        'random_flip': 0.5
    }
}

# Inherited from h-e1
CONVERGENCE_CONFIG = {
    'target_accuracy': 0.90
}

OPTIMIZER_CONFIG = {
    'type': 'sgd',
    'momentum': 0.9
}

IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]

# Experiment execution (PoC)
EXPERIMENT_CONFIG = {
    'num_seeds': 1,  # PoC: 1 seed
    'seed_start': 42,
    'epochs': 30,  # PoC: reduced epochs
    'device': 'cuda' if torch.cuda.is_available() else 'cpu',
    'mixed_precision': False
}

REPRODUCIBILITY_CONFIG = {
    'torch_deterministic': True,
    'cudnn_benchmark': False,
    'cudnn_deterministic': True
}

# Gate criterion (relaxed for PoC)
GATE_CONFIG = {
    'statistical_test': 'independent_ttest',
    'alpha': 0.05,
    'min_delta_diff': 2,  # Δ_ResNet - Δ_ViT ≥ 2 epochs
    'alternative': 'greater'
}

# Output paths
OUTPUT_CONFIG = {
    'results_dir': './h-m2/results',
    'figures_dir': './h-m2/figures',
    'convergence_csv': 'architecture_convergence.csv',
    'comparison_plot': 'resnet_vs_vit_comparison.png',
    'stats_json': 'stats_summary.json'
}

PLOT_CONFIG = {
    'backend': 'Agg',
    'dpi': 150,
    'figsize': (10, 6),
    'color_resnet': '#E74C3C',
    'color_vit': '#3498DB'
}
